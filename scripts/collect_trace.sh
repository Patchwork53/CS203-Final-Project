#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <PIN_ROOT> <OUTPUT_TRACE> <target_binary> [target args ...]"
  echo "Example: $0 ~/pin-3.22-98547-g7a303a835-gcc-linux trace.out /bin/ls -la"
  exit 1
fi

PIN_ROOT="$1"
PIN_ROOT="${PIN_ROOT/#\~/$HOME}"
OUTPUT_TRACE="$2"
shift 2

TOOL_SO="$PIN_ROOT/source/tools/ManualExamples/obj-intel64/loadvaltrace.so"
PIN_BIN="$PIN_ROOT/pin"

if [[ ! -x "$PIN_BIN" ]]; then
  echo "Error: pin binary not found: $PIN_BIN"
  exit 1
fi

if [[ ! -f "$TOOL_SO" ]]; then
  echo "Error: loadvaltrace.so not found: $TOOL_SO"
  echo "Run scripts/setup_pin_tool.sh first."
  exit 1
fi

"$PIN_BIN" -t "$TOOL_SO" -o "$OUTPUT_TRACE" -- "$@"

echo "Trace written to: $OUTPUT_TRACE"
