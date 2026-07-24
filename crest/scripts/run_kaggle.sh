#!/usr/bin/env bash
set -euo pipefail

# Push the CREST notebook to Kaggle and start a run.
#
# ---------------------------------------------------------------------------
# ALWAYS pass --accelerator NvidiaTeslaT4. This is not optional.
# ---------------------------------------------------------------------------
# kernel-metadata.json can only say `enable_gpu: true`, which lets Kaggle pick
# whichever GPU is free. When it picks a Tesla P100 the run dies:
#
#     Found GPU0 Tesla P100-PCIE-16GB which is of cuda capability 6.0.
#     Minimum ... supported by this version of PyTorch is (7.0) - (12.0)
#     Error named symbol not found at line 62 in file /src/csrc/ops.cu
#     Kernel died
#
# The P100 is Pascal (sm_60), too old for both Kaggle's current PyTorch build
# and bitsandbytes' precompiled 4-bit kernels. Confirmed twice now (2026-07-18
# and again 2026-07-24) -- pin T4 and it works. Valid values for this flag are
# NvidiaTeslaT4, NvidiaTeslaP100, Tpu1VmV38.
#
# NOTE: the notebook `git clone`s the repo from GitHub, so push your code to
# GitHub BEFORE running this or Kaggle will run the previous commit.
#
# Usage: ./scripts/run_kaggle.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

kaggle kernels push -p "${REPO_ROOT}/scripts/kaggle_kernel" --accelerator NvidiaTeslaT4

echo
echo "Pushed. Poll with:"
echo "  kaggle kernels status tanjamulazad/crest-llama-harness"
echo "Fetch logs when it finishes with:"
echo "  kaggle kernels output tanjamulazad/crest-llama-harness -p ./kaggle_out"
