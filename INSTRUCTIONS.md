# CS203 Final Project Instructions

## Prerequisites

This project uses Python 3 and Intel Pin 3.22.

Expected Pin root path used in the examples:

```bash
~/pin-3.22-98547-g7a303a835-gcc-linux
```

If your Pin directory is somewhere else, replace that path in the commands below.

## Repository Layout

- `pin-tools/loadvaltrace.cpp`: custom Pin pintool for load-value traces.
- `scripts/setup_pin_tool.sh`: copies and builds the pintool inside Pin's `ManualExamples` directory.
- `scripts/collect_trace.sh`: runs the pintool on a target program.
- `scripts/evaluate_baseline.py`: evaluates the required PC-indexed last-value baseline.
- `scripts/evaluate_no_ml.py`: evaluates the final hybrid stride predictor.
- `lvp/baseline_last_value.py`: baseline predictor source.
- `lvp/value_predictor_no_ml.py`: final predictor source.
- `lvp/trace_parser.py`: trace parser.
- `traces/ls_trace.out`: sample trace used for evaluation.
- `sample_trace.out`: tiny sanity-check trace.

## Build the Pin Tool

From the repository root:

```bash
./scripts/setup_pin_tool.sh ~/pin-3.22-98547-g7a303a835-gcc-linux
```

This builds:

```text
~/pin-3.22-98547-g7a303a835-gcc-linux/source/tools/ManualExamples/obj-intel64/loadvaltrace.so
```

## Generate a Load-Value Trace

Example command used to collect a trace for `/bin/ls`:

```bash
mkdir -p traces
./scripts/collect_trace.sh \
  ~/pin-3.22-98547-g7a303a835-gcc-linux \
  traces/ls_trace.out \
  /bin/ls -la
```

The output trace format is:

```text
0xPC: R 0xADDRESS, 0xVALUE
```

The included parser expects this exact format.

## Run a Syntax Check

```bash
python3 -m py_compile \
  lvp/trace_parser.py \
  lvp/baseline_last_value.py \
  lvp/value_predictor_no_ml.py \
  scripts/evaluate_baseline.py \
  scripts/evaluate_no_ml.py
```

## Evaluate the Baseline

Exact command:

```bash
python3 scripts/evaluate_baseline.py traces/ls_trace.out
```

Expected result on the included `traces/ls_trace.out`:

```text
Trace events:         212930
Predictions used:     206300
Correct predictions:  105068
Coverage:             0.9689
Accuracy (used only): 0.5093
Accuracy (overall):   0.4934
```

## Evaluate the Final Predictor

Exact command:

```bash
python3 scripts/evaluate_no_ml.py traces/ls_trace.out
```

Expected result on the included `traces/ls_trace.out`:

```text
Trace events:         212930
Predictions used:     211050
Correct predictions:  164570
Coverage:             0.9912
Accuracy (used only): 0.7798
Accuracy (overall):   0.7729
```

## Evaluate the Final Predictor Without Stride

This command is useful for isolating the benefit of stride prediction:

```bash
python3 scripts/evaluate_no_ml.py traces/ls_trace.out --disable-stride
```

Expected result on the included `traces/ls_trace.out`:

```text
Trace events:         212930
Predictions used:     211050
Correct predictions:  161747
Coverage:             0.9912
Accuracy (used only): 0.7664
Accuracy (overall):   0.7596
```

## Tune Predictor Options

The final evaluator supports:

```bash
python3 scripts/evaluate_no_ml.py traces/ls_trace.out --pair-threshold 1 --stride-threshold 2
```

Options:

- `--pair-threshold N`: confidence threshold before using exact `(PC, address)` last-value predictions. Default: `1`.
- `--stride-threshold N`: confidence threshold before using stride predictions. Default: `2`.
- `--disable-stride`: disables stride prediction.

## Run the Tiny Sanity Trace

Generate and evaluate a small sample trace:

```bash
python3 scripts/generate_sample_trace.py
python3 scripts/evaluate_baseline.py sample_trace.out
python3 scripts/evaluate_no_ml.py sample_trace.out
```

This is only a sanity check; the main reported results use `traces/ls_trace.out`.
