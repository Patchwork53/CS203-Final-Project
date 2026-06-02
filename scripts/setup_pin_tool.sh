#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <PIN_ROOT>"
  echo "Example: $0 ~/pin-3.22-98547-g7a303a835-gcc-linux"
  exit 1
fi

PIN_ROOT="$1"
PIN_ROOT="${PIN_ROOT/#\~/$HOME}"
MANUAL_DIR="$PIN_ROOT/source/tools/ManualExamples"

if [[ ! -d "$MANUAL_DIR" ]]; then
  echo "Error: ManualExamples not found at $MANUAL_DIR"
  exit 1
fi

cp pin-tools/loadvaltrace.cpp "$MANUAL_DIR/loadvaltrace.cpp"

pushd "$MANUAL_DIR" >/dev/null
# Bootstrap Pin's expected build output directories.
make all TARGET=intel64
make obj-intel64/loadvaltrace.so TARGET=intel64
popd >/dev/null

echo "Built: $MANUAL_DIR/obj-intel64/loadvaltrace.so"
