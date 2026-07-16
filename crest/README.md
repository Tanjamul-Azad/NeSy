# crest

Reproduction steps: env setup, seeds, and run commands go here.

## Setup

```bash
pip install -r requirements.txt
```

## Structure

- `configs/` — model and dataset configs
- `data/loaders/` — dataset loaders (FOLIO, ProofWriter, ProntoQA)
- `crest/` — main package (inference, grounding, detection, correction, baselines, evaluation)
- `annotation/` — annotation guidelines and annotated samples
- `experiments/logs/` — run logs
- `scripts/` — pipeline entry-point scripts
- `results/` — tables and figures
- `notebooks/` — exploratory analysis only
