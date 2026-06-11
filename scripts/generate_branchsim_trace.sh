
#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PIN_ROOT="$repo_root/tools/pin-3.22-98547-g7a303a835-gcc-linux"
BRANCHSIM="$repo_root/scripts/assignment2-branchpredictor-Patchwork53-main/branchsim"
BRANCH_TRACE="$repo_root/scripts/BranchPredictor-Traces/gcc-10K.txt"
OUTPUT_TRACE="$repo_root/traces/branchsim_trace.out"

if [[ ! -x "$BRANCHSIM" ]]; then
  echo "Error: branchsim binary not found: $BRANCHSIM"
  exit 1
fi

if [[ ! -f "$BRANCH_TRACE" ]]; then
  echo "Error: branch trace not found: $BRANCH_TRACE"
  exit 1
fi

"$repo_root/scripts/collect_trace.sh" \
  "$PIN_ROOT" \
  "$OUTPUT_TRACE" \
  "$BRANCHSIM" \
  -i "$BRANCH_TRACE" -m 0 -n 1 -a 8
