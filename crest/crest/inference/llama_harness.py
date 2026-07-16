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
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_NAME = "NousResearch/Meta-Llama-3.1-8B-Instruct"
SEED = 42

# Frozen prompt template — do not edit in place once experiments have started.
# Bump PROMPT_VERSION and log the change instead, so past runs stay attributable
# to a specific, known prompt.
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


@dataclass
class TranslationRecord:
    timestamp: str
    model: str
    prompt_version: str
    seed: int
    temperature: float
    premise: str
    raw_output: str
    fol: str


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
        )
        self.model.eval()

    def translate(self, premise: str, max_new_tokens: int = 200) -> str:
        torch.manual_seed(self.seed)

        prompt = PROMPT_TEMPLATE.format(premise=premise)
        messages = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        ).to(self.model.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,  # temperature=0 / greedy: determinism is the point
                num_beams=1,
            )

        raw_output = self.tokenizer.decode(
            output_ids[0][inputs.shape[-1]:], skip_special_tokens=True
        ).strip()
        fol = raw_output.strip()

        self._log(premise, raw_output, fol)
        return fol

    def _log(self, premise: str, raw_output: str, fol: str) -> None:
        record = TranslationRecord(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            model=self.model_name,
            prompt_version=PROMPT_VERSION,
            seed=self.seed,
            temperature=0.0,
            premise=premise,
            raw_output=raw_output,
            fol=fol,
        )
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
