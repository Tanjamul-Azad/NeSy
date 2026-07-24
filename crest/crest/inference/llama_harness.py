"""Local Llama-3.1-8B-Instruct wrapper for NL -> FOL translation.

Phase 1.1: reproducibility is itself a claim in the paper. Every call is
logged (prompt version, exact input, exact output, generation config, seed)
so a "training-free, deterministic detector" claim is actually falsifiable,
not asserted.

Model source (2026-07-16): meta-llama/Llama-3.1-8B-Instruct itself is gated
and pending Meta's manual approval. Using NousResearch's ungated reupload
instead -- verified byte-identical safetensors shard sizes against the
official repo across all 4 shards before trusting it. Same model, same
weights, just an unblocked host. Swap MODEL_NAME back to the official repo
once/if Meta's approval clears, purely for citation-path cleanliness; no
functional difference either way.
"""

import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_NAME = "NousResearch/Meta-Llama-3.1-8B-Instruct"
SEED = 42

# Frozen prompt templates — do not edit in place once experiments have started.
# Bump the version string and log the change instead, so past runs stay
# attributable to a specific, known prompt.
#
# v1 (per-premise) translates each premise in ISOLATION. Keep it, but do not
# use it as the primary vanilla baseline: with no shared context the model
# cannot know which predicate names it used for earlier premises, so
# predicate/constant naming inconsistency is structurally guaranteed -- which
# is precisely the failure class CREST claims to detect. Reporting prevalence
# from that setup would be measuring an artefact of our own design, and the
# standard in this literature (Logic-LM, LINC, FOLIO's own baselines) is to
# translate the whole problem at once. v1's real value is as an ABLATION:
# "inconsistency with vs. without shared context" is a genuine measurement.
PROMPT_VERSION = "v1"
PROMPT_TEMPLATE = (
    "Translate the following natural language premise into a single "
    "First-Order Logic (FOL) formula. Use standard FOL syntax with "
    "quantifiers (∀, ∃), connectives (∧, ∨, ¬, →, ↔), "
    "and predicates in the form Predicate(arg1, arg2, ...). "
    "Output only the FOL formula, nothing else.\n\n"
    "Premise: {premise}\n"
    "FOL:"
)

# v2 (whole-story) is the PRIMARY vanilla baseline: all premises plus the
# conclusion in one prompt, matching standard practice.
#
# Deliberate design choice: this prompt does NOT contain an explicit "use
# consistent predicate names" instruction. Adding one would hand-hold the
# model past the exact phenomenon under study and make the measurement
# circular. Consistency here is whatever emerges naturally from seeing the
# full context. A third variant that DOES nag about consistency is worth
# running as a separate condition (it directly answers the reviewer question
# "why not just prompt it better?", the same class of objection Phase 3.3
# addresses for model capability) -- add it as STORY_PROMPT_TEMPLATE_V3
# rather than by editing this one.
STORY_PROMPT_VERSION = "v2-story"
STORY_PROMPT_TEMPLATE = (
    "Translate each of the following natural language statements into a "
    "First-Order Logic (FOL) formula.\n\n"
    "Use standard FOL syntax: quantifiers (∀, ∃), connectives "
    "(∧, ∨, ¬, →, ↔, ⊕), and predicates in the form "
    "Predicate(arg1, arg2, ...).\n\n"
    "Output exactly one line per statement, in the same order, each line "
    "starting with the same label shown below (P1, P2, ..., C). "
    "Output only these lines — no explanations, no commentary, no blank "
    "lines, no markdown.\n\n"
    "{numbered_statements}\n\n"
    "FOL translations:\n"
)


class StoryFormatError(ValueError):
    """The model's whole-story output couldn't be parsed into exactly the
    expected set of labelled formulas (P1..Pn plus C).

    Subclasses ValueError deliberately: the grounder/evaluation layer already
    treats ValueError as a "loud" malformed-input failure, and a translation
    the pipeline cannot even parse is loud by definition -- it visibly breaks
    rather than silently producing a confident wrong answer.
    """


def _strip_markdown_fences(text: str) -> str:
    lines = [ln for ln in text.split("\n") if not ln.strip().startswith("```")]
    return "\n".join(lines)


# Accepts "P1:", "P1.", "P1)", "p1 -", "C:", etc. The model is told to use
# "P1:" but small models drift on punctuation, and rejecting a correct
# formula over a stray period would inflate the loud-failure rate with
# something that isn't a translation error at all.
_LABEL_RE = re.compile(r"^\s*([PpCc])\s*(\d*)\s*[:.)\-]\s*(.+?)\s*$")

# Markdown bold ("**P1:** ...") survives the label regex and would otherwise
# leave a stray "**" glued to the front of the formula, which then fails to
# parse as FOL and gets miscounted as a translation error rather than the
# formatting noise it is. FOL notation never contains "**", so stripping it
# line-wide is safe.
_BOLD_RE = re.compile(r"\*\*")


def parse_story_output(raw_output: str, n_premises: int) -> Tuple[List[str], str]:
    """Parse a whole-story translation into (premises_fol, conclusion_fol).

    Strict about completeness, lenient about surface formatting -- see
    _LABEL_RE. Raises StoryFormatError if any expected label is missing,
    duplicated, or extra, rather than silently padding/truncating: a
    length mismatch between premises and their formulas would misalign every
    downstream comparison, which is exactly the kind of silent corruption
    this project exists to study.
    """
    text = _strip_markdown_fences(raw_output)

    premises: dict = {}
    conclusion = None
    for line in text.split("\n"):
        m = _LABEL_RE.match(_BOLD_RE.sub("", line))
        if not m:
            continue
        kind, num, formula = m.group(1).upper(), m.group(2), m.group(3).strip()
        if not formula:
            continue
        if kind == "P":
            if not num:
                continue
            idx = int(num)
            if idx in premises:
                raise StoryFormatError(
                    f"duplicate label P{idx} in model output"
                )
            premises[idx] = formula
        else:
            if conclusion is not None:
                raise StoryFormatError("duplicate label C in model output")
            conclusion = formula

    expected = set(range(1, n_premises + 1))
    got = set(premises)
    if got != expected:
        missing = sorted(expected - got)
        extra = sorted(got - expected)
        raise StoryFormatError(
            f"expected P1..P{n_premises}, missing={missing}, extra={extra}"
        )
    if conclusion is None:
        raise StoryFormatError("no conclusion (C) line in model output")

    return [premises[i] for i in range(1, n_premises + 1)], conclusion


@dataclass
class TranslationRecord:
    timestamp: str
    model: str
    prompt_version: str
    seed: int
    temperature: float
    premise: str
    raw_output: str
    fol: object  # str, or None when the output couldn't be parsed at all


class LlamaHarness:
    """NL premise in -> FOL string out. Every call logged to `log_path`."""

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        log_path: str = "experiments/logs/llama_harness_calls.jsonl",
        seed: int = SEED,
    ):
        self.model_name = model_name
        self.seed = seed
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        torch.manual_seed(seed)

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quant_config,
            device_map="auto",
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16,
        )
        self.model.eval()

    def _generate(self, prompt: str, max_new_tokens: int) -> str:
        torch.manual_seed(self.seed)

        messages = [{"role": "user", "content": prompt}]
        # return_dict=True: newer transformers versions return a BatchEncoding
        # (dict-like, no .shape) from apply_chat_template unless explicitly
        # told to, so unpack it into generate() rather than pass positionally.
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
        ).to(self.model.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,  # temperature=0 / greedy: determinism is the point
                num_beams=1,
            )

        input_length = inputs["input_ids"].shape[-1]
        return self.tokenizer.decode(
            output_ids[0][input_length:], skip_special_tokens=True
        ).strip()

    def translate(self, premise: str, max_new_tokens: int = 200) -> str:
        """Per-premise translation (prompt v1). ABLATION ONLY -- see the note
        on PROMPT_TEMPLATE above; use translate_story() for the primary
        vanilla baseline.
        """
        raw_output = self._generate(PROMPT_TEMPLATE.format(premise=premise), max_new_tokens)
        fol = raw_output.strip()
        self._log(PROMPT_VERSION, premise, raw_output, fol)
        return fol

    def translate_story(
        self,
        premises: List[str],
        conclusion: str,
        max_new_tokens: int = None,
    ) -> Tuple[List[str], str]:
        """Whole-story translation (prompt v2) -- the primary vanilla baseline.

        All premises and the conclusion go in one prompt so the model can keep
        predicate and constant naming consistent across formulas, matching
        standard practice (Logic-LM, LINC, FOLIO).

        Raises StoryFormatError if the output can't be parsed into exactly
        P1..Pn plus C. Callers should treat that as a loud failure, not
        silently retry or pad -- see parse_story_output.
        """
        numbered = "\n".join(
            [f"P{i + 1}: {p}" for i, p in enumerate(premises)] + [f"C: {conclusion}"]
        )
        prompt = STORY_PROMPT_TEMPLATE.format(numbered_statements=numbered)

        if max_new_tokens is None:
            # Scale with the story: one formula per statement, and a fixed
            # budget silently truncates longer FOLIO stories mid-output, which
            # would show up as a bogus "missing P7" format failure rather than
            # the token-budget problem it actually is.
            max_new_tokens = 120 * (len(premises) + 1) + 100

        raw_output = self._generate(prompt, max_new_tokens)
        try:
            premises_fol, conclusion_fol = parse_story_output(raw_output, len(premises))
        except StoryFormatError:
            # Log the unparseable output before re-raising -- otherwise the
            # only record of what the model actually said is lost, and format
            # failures are exactly what we need the raw text for.
            self._log(STORY_PROMPT_VERSION, numbered, raw_output, fol=None)
            raise

        self._log(
            STORY_PROMPT_VERSION,
            numbered,
            raw_output,
            fol="\n".join(premises_fol + [conclusion_fol]),
        )
        return premises_fol, conclusion_fol

    def _log(self, prompt_version: str, premise: str, raw_output: str, fol) -> None:
        record = TranslationRecord(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            model=self.model_name,
            prompt_version=prompt_version,
            seed=self.seed,
            temperature=0.0,
            premise=premise,
            raw_output=raw_output,
            fol=fol,
        )
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
