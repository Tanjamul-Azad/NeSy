"""Token-level confidence summary, shared by both harnesses.

The "internal reasoning" signal for this project's detection question: given
the sequence of per-token log-probabilities the model assigned to the FOL it
generated, summarise how confident it was. The hypothesis under test is that
low generation confidence predicts a silent failure -- i.e. the model "knew"
its translation was shaky. If that holds, confidence is a gold-label-free
detector signal, which is exactly what a pre-solver risk layer needs.

Both the OpenAI logprobs API and a local Llama forward pass expose per-token
logprobs, so the same summary is computed for both arms and the comparison
stays apples-to-apples.

Summaries kept (all in natural log units):
  mean_logprob   average per-token logprob (higher = more confident)
  min_logprob    the single least-confident token (a mistranslation often
                 hinges on one wrong token, so the worst token can matter
                 more than the average)
  perplexity     exp(-mean_logprob), the standard readable confidence scale
  n_tokens       so a short high-confidence output isn't confused with a long one
"""

import math
from typing import List, Optional


def _confidence_stats(token_logprobs: List[float]) -> Optional[dict]:
    if not token_logprobs:
        return None
    mean_lp = sum(token_logprobs) / len(token_logprobs)
    return {
        "mean_logprob": mean_lp,
        "min_logprob": min(token_logprobs),
        "perplexity": math.exp(-mean_lp),
        "n_tokens": len(token_logprobs),
    }
