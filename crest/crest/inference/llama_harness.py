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

# v3 (whole-story, FEW-SHOT) -- matches the literature standard. Logic-LM and
# LINC both prompt with worked demonstrations, not bare instructions.
#
# Motivation is empirical, not stylistic: the v2 zero-shot run (n=50) scored
# 37.9% accuracy among gradeable examples against a 33.3% chance level and a
# 34.0% majority-class baseline -- i.e. at chance. Reading the actual output
# showed the model didn't know FOLIO's *conventions* rather than failing at
# logic: it emitted things like `Knowledge(K) ∧ Book(B) → Contains(B, K)`
# (uppercase letters used as if variables, no quantifier at all) and
# `Reads(H, "Walden" by Henry Thoreau)` (raw English inside a term).
# Demonstrations are the standard fix for convention-mismatch of that kind.
#
# The demonstrations come from FOLIO's TRAIN split (never validation -- that
# would contaminate the test set) and every one was verified by running its
# gold FOL through our own Prover9 grounder and confirming it reproduces the
# gold label, so a demo cannot teach a broken NL->FOL mapping.
#
# Deliberately EXCLUDED: train example_id 251/252, whose gold FOL contains
# `Residentof` in one premise and `ResidentOf` in another. That case mismatch
# is precisely the predicate-inconsistency failure CREST exists to detect --
# using it as a demonstration would teach the model to commit the error we
# are trying to measure.
#
# Like v2, this prompt still does NOT instruct the model to keep predicate
# names consistent. The demonstrations model consistent naming by example,
# which is how the literature's prompts behave; an explicit instruction would
# be a separate condition (see the v2 note above).
FEWSHOT_PROMPT_VERSION = "v3-story-fewshot"

# train example_id 261 -- universal quantification, implication, conjunction,
# camelCase multi-word constants.
_DEMO_1 = (
    "P1: If a legislator is found guilty of stealing government funds, they will be suspended from office.\n"
    "P2: Tiffany T. Alston was a legislator in Maryland's House of Delegates from 2011 to 2013.\n"
    "P3: Tiffany T. Alston was found guilty of stealing government funds in 2012.\n"
    "C: Tiffany T. Alston was suspended from the Maryland House of Delegates.\n"
    "\n"
    "FOL translations:\n"
    "P1: ∀x ((Legislator(x) ∧ StealsFunds(x)) → Suspended(x))\n"
    "P2: Legislator(tiffanyTAlston)\n"
    "P3: StealsFunds(tiffanyTAlston) ∧ StealsFundsInYr(tiffanyTAlston, yr2012)\n"
    "C: Suspended(tiffanyTAlston)"
)

# train example_id 316 -- binary predicates, negation inside a quantified
# formula, constants that are not people.
_DEMO_2 = (
    "P1: Ordinary is an unincorporated community.\n"
    "P2: Located within Elliot County, Ordinary is on Kentucky Route 32.\n"
    "P3: Ordinary is located northwest of Sandy Hook.\n"
    "C: There are no unincorporated communities along Kentucky Route 32.\n"
    "\n"
    "FOL translations:\n"
    "P1: UnincorporatedCommunity(ordinary)\n"
    "P2: LocatedIn(ordinary, elliotCounty) ∧ On(ordinary, kentuckyRoute32)\n"
    "P3: LocatedNorthwestOf(ordinary, sandyHook)\n"
    "C: ∀x (On(x, kentuckyRoute32) → ¬UnincorporatedCommunity(x))"
)

# train example_id 1126 -- disjunction, negation, and FOLIO's ⊕ (XOR), which
# the model otherwise never produces and which our grounder specifically
# supports.
_DEMO_3 = (
    "P1: All people who regularly drink coffee are dependent on caffeine.\n"
    "P2: People regularly drink coffee, or they don't want to be addicted to caffeine, or both.\n"
    "P3: No one who doesn't want to be addicted to caffeine is unaware that caffeine is a drug.\n"
    "P4: Rina is either a student who is dependent on caffeine, or she is not a student and not dependent on caffeine.\n"
    "C: Rina doesn't want to be addicted to caffeine or is unaware that caffeine is a drug.\n"
    "\n"
    "FOL translations:\n"
    "P1: ∀x (DrinkRegularly(x, coffee) → IsDependentOn(x, caffeine))\n"
    "P2: ∀x (DrinkRegularly(x, coffee) ∨ ¬WantToBeAddictedTo(x, caffeine))\n"
    "P3: ∀x (¬WantToBeAddictedTo(x, caffeine) → ¬AwareThatDrug(x, caffeine))\n"
    "P4: ¬(IsDependentOn(rina, caffeine) ⊕ Student(rina))\n"
    "C: ¬WantToBeAddictedTo(rina, caffeine) ∨ ¬AwareThatDrug(rina, caffeine)"
)

FEWSHOT_PROMPT_TEMPLATE = (
    "Translate each natural language statement into a First-Order Logic "
    "(FOL) formula.\n\n"
    "Use standard FOL syntax: quantifiers (∀, ∃), connectives "
    "(∧, ∨, ¬, →, ↔, ⊕), and predicates in the form "
    "Predicate(arg1, arg2, ...). Write constants in lowerCamelCase and "
    "variables as x, y, z.\n\n"
    "Output exactly one line per statement, in the same order, each line "
    "starting with the label shown (P1, P2, ..., C). Output only these "
    "lines — no explanations, no commentary, no markdown.\n\n"
    "Here are worked examples.\n\n"
    "### Example 1\n" + _DEMO_1 + "\n\n"
    "### Example 2\n" + _DEMO_2 + "\n\n"
    "### Example 3\n" + _DEMO_3 + "\n\n"
    "### Now translate these\n"
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

    `truncated` distinguishes "the model ran out of token budget mid-output"
    from "the model produced the wrong shape". Both are unparseable, but the
    first is our own harness misconfiguration and must not be reported as a
    model translation failure -- the n=50 run had exactly 2 of these, both
    missing only the LAST premise, which is the signature of hitting the cap.
    """

    def __init__(self, message, truncated: bool = False):
        super().__init__(message)
        self.truncated = truncated


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

    def _generate(self, prompt: str, max_new_tokens: int) -> Tuple[str, bool]:
        """Returns (text, hit_token_cap). The flag matters: output that ran
        out of budget mid-formula is our misconfiguration, not a model
        translation failure, and conflating the two would put a harness bug
        into a reported prevalence number.
        """
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
        generated = output_ids[0][input_length:]
        hit_cap = len(generated) >= max_new_tokens
        text = self.tokenizer.decode(generated, skip_special_tokens=True).strip()
        return text, hit_cap

    def translate(self, premise: str, max_new_tokens: int = 200) -> str:
        """Per-premise translation (prompt v1). ABLATION ONLY -- see the note
        on PROMPT_TEMPLATE above; use translate_story() for the primary
        vanilla baseline.
        """
        raw_output, _ = self._generate(
            PROMPT_TEMPLATE.format(premise=premise), max_new_tokens
        )
        fol = raw_output.strip()
        self._log(PROMPT_VERSION, premise, raw_output, fol)
        return fol

    def translate_story(
        self,
        premises: List[str],
        conclusion: str,
        max_new_tokens: int = None,
        few_shot: bool = True,
    ) -> Tuple[List[str], str]:
        """Whole-story translation -- the primary vanilla baseline.

        All premises and the conclusion go in one prompt so the model can keep
        predicate and constant naming consistent across formulas, matching
        standard practice (Logic-LM, LINC, FOLIO).

        `few_shot=True` (default) uses prompt v3 with worked demonstrations,
        which is what the literature actually does. `few_shot=False` uses the
        zero-shot v2 prompt and is retained as an explicit ablation --
        "does the baseline's weakness come from missing demonstrations?" is a
        real question, and the zero-shot n=50 run answers it with a measured
        number rather than an assumption.

        Raises StoryFormatError if the output can't be parsed into exactly
        P1..Pn plus C. Callers should treat that as a loud failure, not
        silently retry or pad -- see parse_story_output.
        """
        numbered = "\n".join(
            [f"P{i + 1}: {p}" for i, p in enumerate(premises)] + [f"C: {conclusion}"]
        )
        template = FEWSHOT_PROMPT_TEMPLATE if few_shot else STORY_PROMPT_TEMPLATE
        version = FEWSHOT_PROMPT_VERSION if few_shot else STORY_PROMPT_VERSION
        prompt = template.format(numbered_statements=numbered)

        if max_new_tokens is None:
            # Scale with the story. The zero-shot n=50 run produced 2 format
            # failures, both missing only the LAST premise -- the signature of
            # running out of budget rather than of a malformed answer -- so
            # this is deliberately generous. hit_cap below catches the rest.
            max_new_tokens = 180 * (len(premises) + 1) + 200

        raw_output, hit_cap = self._generate(prompt, max_new_tokens)
        try:
            premises_fol, conclusion_fol = parse_story_output(raw_output, len(premises))
        except StoryFormatError as e:
            # Log the unparseable output before re-raising -- otherwise the
            # only record of what the model actually said is lost, and format
            # failures are exactly what we need the raw text for.
            self._log(version, numbered, raw_output, fol=None)
            if hit_cap:
                raise StoryFormatError(
                    f"output truncated at max_new_tokens={max_new_tokens} "
                    f"(harness budget, not a model error): {e}",
                    truncated=True,
                ) from e
            raise

        self._log(
            version,
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
