#!/usr/bin/env bash
set -euo pipefail

# Phase 3.1: vanilla NL -> Llama -> FOL -> Prover9 pipeline.
#
# Needs a GPU for LlamaHarness (4-bit Llama-3.1-8B via bitsandbytes) --
# run this from a Kaggle kernel shell (see crest/scripts/kaggle_kernel/
# crest_kaggle.ipynb, which runs the same module inline), not on the local
# Windows dev box. Run from the crest/ project root (the dir containing
# both crest/ and data/).
#
# Usage: ./scripts/run_vanilla_pipeline.sh [--limit 50] [--split validation]

python -m crest.evaluation.vanilla_pipeline "$@"
