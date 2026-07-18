# crest

Reproduction steps: env setup, seeds, and run commands go here.

## GPU-heavy work runs on Kaggle, not locally

Decision (2026-07-18): loading Llama-3.1-8B-Instruct in 4-bit via bitsandbytes
segfaulted reproducibly on this local Windows machine — crashed at the exact
same tensor every time, across two CUDA versions (cu130, cu124) and multiple
`device_map` configs. That pattern (identical crash point regardless of
config) points to a Windows-specific bitsandbytes bug, not a config or
hardware problem here. Also, local hardware is genuinely tight for this work:
8GB VRAM and only ~16GB system RAM (often <5GB free with normal apps open).

**Model loading, inference, and training now run on Kaggle** (free T4x2/P100,
16GB VRAM, Linux — sidesteps the Windows bitsandbytes issue and gives more
headroom). Use `crest/scripts/crest_kaggle.ipynb`: it clones this repo fresh
into the Kaggle session, installs the non-torch dependencies (Kaggle's base
image already has torch+CUDA configured — don't reinstall it), and runs the
harness. GitHub stays the single source of truth; the notebook can push
results back to it directly (see its last cell) using a Kaggle Secret, not
this repo, for the token.

The local venv (below) still exists for the parts that don't need heavy
GPU/RAM work: the FOLIO loader, the Prover9 grounder, code editing, and any
CPU-only debugging.

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
.venv\Scripts\hf.exe auth whoami
```

`hf auth login` requires being logged in first — run it interactively (it opens
a browser device-code flow, or accepts a pasted token) and complete it there;
don't put HF tokens in any file in this repo or paste them into any chat/AI tool.

Llama-3.1-8B-Instruct is gated (`gated: manual`) — request access at
https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct and wait for approval
(can take hours, not instant) before the harness can download weights.

### Model/dataset cache location

Default HF cache is under `C:\Users\<you>\.cache\huggingface`, which may not have
room for a ~16GB model. Point just the *cache* (not the token/login, which should
stay at its default location) at a drive with space:

```
setx HF_HUB_CACHE "D:\huggingface_cache\hub"
```

This is a **persistent per-user env var** — set once, applies to all new
terminals/processes afterward, doesn't need repeating per session.

### Grounder: Prover9, not Z3

Phase 1.3 found that Logic-LM's own grounding code doesn't transfer — its Z3
module targets a different custom DSL, and its FOLIO-specific code is a single
hardcoded Prover9 example, not a reusable parser. See
`crest/crest/grounding/fol_to_prover9.py` for the full reasoning and the actual
grounder (NLTK for parsing, Prover9 for proving — matches how FOLIO's own gold
labels were verified, and how Logic-LM evaluates FOLIO).

The vendored Prover9 binary (`crest/vendor/prover9/bin/`) is a Linux ELF
executable, so **this requires WSL (Ubuntu) enabled on Windows** — the grounder
shells out via `wsl -d Ubuntu -- ...`. Every teammate running this on Windows
needs WSL set up, not just this machine. If a binary loses its executable bit
after a Windows-side file copy, fix it from inside WSL: `chmod +x
/mnt/d/FYDP/crest/vendor/prover9/bin/*`.

## Structure

- `configs/` — model and dataset configs
- `data/loaders/` — dataset loaders (FOLIO, ProofWriter, ProntoQA)
- `crest/` — main package (inference, grounding, detection, correction, baselines, evaluation)
- `annotation/` — annotation guidelines and annotated samples
- `experiments/logs/` — run logs
- `scripts/` — pipeline entry-point scripts
- `results/` — tables and figures
- `notebooks/` — exploratory analysis only
