"""Phase 3.3 / 4.2: strong-model harness (OpenAI API).

Deliberately mirrors LlamaHarness's interface -- `translate_story`,
`translate`, `_generate` with the same signatures and return shapes -- so
that vanilla_pipeline.py, self_refine.py and self_refine_pipeline.py run
against a proprietary model with NO changes. The comparison is only
meaningful if both arms go through identical prompt construction, identical
output parsing and identical grounding, and reusing the code is the only way
to guarantee that rather than assert it.

The prompts are IMPORTED from llama_harness, not copied. A copy would drift.

No GPU is involved, so unlike Phases 1-4 this runs locally: FOLIO loader,
OpenAI API, and the WSL Prover9 grounder are all available on the dev
machine. Kaggle is not needed.

API key handling: read from the OPENAI_API_KEY environment variable only.
The key is never logged, never written to a results file, and never printed
-- experiment logs in this project are committed to git, so anything this
module writes must be safe to publish.

Determinism caveat, to be stated in the paper: `temperature=0` plus a fixed
`seed` makes OpenAI models *near*-deterministic, not deterministic. OpenAI
documents seed as best-effort and exposes `system_fingerprint` to signal
backend changes. That fingerprint is logged with every call so a
non-reproducible result can at least be attributed. The Llama arm, running
greedy decoding locally, is genuinely deterministic. This asymmetry is a
real limitation of the comparison, not something to paper over.
"""

import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from crest.inference.confidence import _confidence_stats
from crest.inference.llama_harness import (
    PROMPT_TEMPLATE,
    PROMPT_VERSION,
    STORY_PROMPT_TEMPLATE,
    STORY_PROMPT_VERSION,
    FEWSHOT_PROMPT_TEMPLATE,
    FEWSHOT_PROMPT_VERSION,
    StoryFormatError,
    parse_story_output,
)

DEFAULT_MODEL = "gpt-4o"
SEED = 42

# Approximate USD per 1M tokens, used only for a running cost estimate so a
# run can be stopped before it burns credit unexpectedly. NOT authoritative
# -- verify against OpenAI's current pricing page before quoting any cost
# figure in the thesis.
PRICING_PER_1M = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


@dataclass
class TranslationRecord:
    timestamp: str
    model: str            # the alias requested, e.g. "gpt-4o"
    resolved_model: str   # the dated snapshot that actually answered
    prompt_version: str
    seed: int
    temperature: float
    premise: str
    raw_output: str
    fol: object
    system_fingerprint: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


class OpenAIHarness:
    """Drop-in replacement for LlamaHarness backed by the OpenAI API."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        log_path: str = "experiments/logs/openai_harness_calls.jsonl",
        seed: int = SEED,
        max_retries: int = 5,
    ):
        from openai import OpenAI  # imported here so the module loads without the dep

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set.\n"
                "  PowerShell (this session):  $env:OPENAI_API_KEY = \"sk-...\"\n"
                "  PowerShell (persistent):    [Environment]::SetEnvironmentVariable("
                "\"OPENAI_API_KEY\", \"sk-...\", \"User\")   then open a new terminal\n"
                "Do not place the key in a file inside this repo."
            )

        self.client = OpenAI(api_key=api_key)
        self.model_name = model
        self.seed = seed
        self.max_retries = max_retries
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Running totals so a run's cost is visible while it happens.
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.n_calls = 0
        # Confidence of the most recent generation; the pipeline reads this
        # after translate_story to log the story translation's confidence.
        self.last_confidence = None

    # ---- cost ------------------------------------------------------------
    @property
    def estimated_cost_usd(self) -> float:
        p = PRICING_PER_1M.get(self.model_name)
        if not p:
            return float("nan")
        return (self.prompt_tokens / 1e6) * p["input"] + (self.completion_tokens / 1e6) * p["output"]

    def cost_report(self) -> str:
        return (f"{self.n_calls} calls | {self.prompt_tokens:,} in + "
                f"{self.completion_tokens:,} out tokens | "
                f"~${self.estimated_cost_usd:.2f} (estimate, verify pricing)")

    # ---- generation ------------------------------------------------------
    def _generate(self, prompt: str, max_new_tokens: int) -> Tuple[str, bool]:
        """Returns (text, hit_token_cap), matching LlamaHarness._generate.

        hit_cap is taken from finish_reason == "length", which is the API's
        own signal that output was cut off -- the same distinction the local
        harness draws so a budget problem is never scored as a model error.
        """
        last_err = None
        for attempt in range(self.max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    seed=self.seed,
                    max_tokens=max_new_tokens,
                    # Token-level confidence, free with the same call. This is
                    # the "internal reasoning" signal: does the model's own
                    # uncertainty over the FOL it produced predict whether that
                    # FOL will silently fail? Captured here for every call so
                    # the detection analysis needs no re-run.
                    logprobs=True,
                )
                break
            except Exception as e:  # rate limits, transient 5xx
                last_err = e
                name = type(e).__name__
                if attempt == self.max_retries - 1:
                    raise
                wait = 2 ** attempt
                # Deliberately does not print the exception body: API errors
                # can echo request metadata, and these logs get committed.
                print(f"    [{name}] retry {attempt + 1}/{self.max_retries} in {wait}s")
                time.sleep(wait)

        choice = resp.choices[0]
        text = (choice.message.content or "").strip()
        hit_cap = choice.finish_reason == "length"

        self.n_calls += 1
        self.prompt_tokens += resp.usage.prompt_tokens
        self.completion_tokens += resp.usage.completion_tokens
        self.last_confidence = _confidence_stats(
            [t.logprob for t in choice.logprobs.content] if choice.logprobs and choice.logprobs.content else []
        )
        self._last_meta = {
            # The RESOLVED snapshot, not the alias we asked for. "gpt-4o" is a
            # moving pointer: today it resolves to one dated snapshot, in six
            # months to another, and a paper that reports "gpt-4o" without this
            # cannot be reproduced or even identified. Three distinct
            # system_fingerprints already appear across our own runs, so the
            # backend demonstrably changed mid-study.
            "resolved_model": getattr(resp, "model", None),
            "system_fingerprint": getattr(resp, "system_fingerprint", None),
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
            "finish_reason": choice.finish_reason,
        }
        return text, hit_cap

    # ---- same API as LlamaHarness ---------------------------------------
    def translate(self, premise: str, max_new_tokens: int = 200) -> str:
        raw, _ = self._generate(PROMPT_TEMPLATE.format(premise=premise), max_new_tokens)
        fol = raw.strip()
        self._log(PROMPT_VERSION, premise, raw, fol)
        return fol

    def translate_story(
        self,
        premises: List[str],
        conclusion: str,
        max_new_tokens: int = None,
        few_shot: bool = True,
    ) -> Tuple[List[str], str]:
        numbered = "\n".join(
            [f"P{i + 1}: {p}" for i, p in enumerate(premises)] + [f"C: {conclusion}"]
        )
        template = FEWSHOT_PROMPT_TEMPLATE if few_shot else STORY_PROMPT_TEMPLATE
        version = FEWSHOT_PROMPT_VERSION if few_shot else STORY_PROMPT_VERSION
        prompt = template.format(numbered_statements=numbered)

        if max_new_tokens is None:
            max_new_tokens = 180 * (len(premises) + 1) + 200

        raw, hit_cap = self._generate(prompt, max_new_tokens)
        try:
            premises_fol, conclusion_fol = parse_story_output(raw, len(premises))
        except StoryFormatError as e:
            self._log(version, numbered, raw, fol=None)
            if hit_cap:
                raise StoryFormatError(
                    f"output truncated at max_tokens={max_new_tokens} "
                    f"(harness budget, not a model error): {e}",
                    truncated=True,
                ) from e
            raise

        self._log(version, numbered, raw, fol="\n".join(premises_fol + [conclusion_fol]))
        return premises_fol, conclusion_fol

    def _log(self, prompt_version: str, premise: str, raw_output: str, fol) -> None:
        meta = getattr(self, "_last_meta", {})
        record = TranslationRecord(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            model=self.model_name,
            resolved_model=meta.get("resolved_model"),
            prompt_version=prompt_version,
            seed=self.seed,
            temperature=0.0,
            premise=premise,
            raw_output=raw_output,
            fol=fol,
            system_fingerprint=meta.get("system_fingerprint"),
            prompt_tokens=meta.get("prompt_tokens", 0),
            completion_tokens=meta.get("completion_tokens", 0),
            finish_reason=meta.get("finish_reason", ""),
        )
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
