# crest

Reproduction steps: env setup, seeds, and run commands go here.

## Setup

Virtual env lives at `D:\FYDP\.venv` (not under `crest/`), created with the system
Python so packages don't land on C: drive. pip's cache is already configured to
`D:\pip-cache` (see `pip config list`).

```bash
# from D:\FYDP
python -m venv .venv
.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
.venv\Scripts\python.exe -m pip install -r crest/requirements.txt
```

The `cu130` index matches an RTX 4060 with a recent driver (`nvidia-smi` reports
CUDA 13.3 support). If you're on a different driver/CUDA version, check
`https://download.pytorch.org/whl/<tag>/torch/` for the right tag before installing —
don't assume cu130 is still current later.

Verify the environment (Phase 0):

```bash
nvidia-smi
.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
.venv\Scripts\python.exe -c "import z3; print(z3.get_version_string())"
.venv\Scripts\python.exe -c "from huggingface_hub import whoami; print(whoami())"
```

`whoami()` requires being logged in first — run `huggingface-cli login` (or
`hf auth login`) interactively and paste your token there; don't put HF tokens in
any file in this repo.

## Structure

- `configs/` — model and dataset configs
- `data/loaders/` — dataset loaders (FOLIO, ProofWriter, ProntoQA)
- `crest/` — main package (inference, grounding, detection, correction, baselines, evaluation)
- `annotation/` — annotation guidelines and annotated samples
- `experiments/logs/` — run logs
- `scripts/` — pipeline entry-point scripts
- `results/` — tables and figures
- `notebooks/` — exploratory analysis only
