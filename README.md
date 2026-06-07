# CS203 Final Project - Pin Setup + Last-Value Baseline

This repository now includes:

- A Pin pintool to generate load-value traces in the format needed by the project.
- A baseline last-value predictor (PC-indexed) for quick evaluation.
- A table-based non-ML predictor using PC/address, address, and PC last-value tables.

## Repository Layout

- `pin-tools/loadvaltrace.cpp`: Custom Pin tool that logs load PC, load address, and loaded value.
- `scripts/setup_pin_tool.sh`: Copies/builds the pintool inside your Pin `ManualExamples` directory.
- `scripts/collect_trace.sh`: Runs the built pintool on any target binary.
- `scripts/evaluate_baseline.py`: Evaluates the last-value predictor on a trace.
- `scripts/evaluate_no_ml.py`: Evaluates the configurable non-ML predictor on a trace.
- `scripts/generate_sample_trace.py`: Creates a tiny synthetic trace for sanity checks.
- `lvp/baseline_last_value.py`: Baseline predictor implementation.
- `lvp/trace_parser.py`: Trace parsing utilities.
- `lvp/value_predictor_no_ml.py`: Table-based predictor implementation.

## 1) Prerequisites

You need Intel Pin downloaded and extracted locally.

Example expected root path:

`~/pin-3.22-98547-g7a303a835-gcc-linux`

## 2) Build the custom Pin tool

From repo root:

```bash
./scripts/setup_pin_tool.sh ~/pin-3.22-98547-g7a303a835-gcc-linux
```

This builds:

`~/pin-3.22-98547-g7a303a835-gcc-linux/source/tools/ManualExamples/obj-intel64/loadvaltrace.so`

## 3) Collect a load-value trace

Example on `/bin/ls`:

```bash
./scripts/collect_trace.sh \
	~/pin-3.22-98547-g7a303a835-gcc-linux \
	traces/ls_trace.out \
	/bin/ls -la
```

Trace line format:

`0xPC: R 0xADDRESS, 0xVALUE`

Only load reads are logged.

## 4) Run the baseline predictor

```bash
python3 scripts/evaluate_baseline.py traces/ls_trace.out
```

Reported metrics:

- `Coverage`: fraction of events where a prediction was used.
- `Accuracy (used only)`: accuracy on events where confidence/use is Yes.
- `Accuracy (overall)`: correct predictions over all events.

## 4b) Run the non-ML predictor

```bash
python3 scripts/evaluate_no_ml.py traces/ls_trace.out
```

The predictor checks tables in this order:

- Repeated stride for exact `(PC, address)` or PC context.
- Exact `(PC, address)` pair after one stable repeat.
- Load address, once seen.
- Load PC, once seen.

Useful options:

- `--pair-threshold N`: number of stable repeats required before using the `(PC, address)` table. The default is `1`.
- `--disable-stride`: turn off stride prediction and use only the last-value table order.
- `--stride-threshold N`: number of repeated strides required before stride prediction. The default is `2`.

## 5) Quick sanity check (no Pin required)

```bash
python3 scripts/generate_sample_trace.py
python3 scripts/evaluate_baseline.py sample_trace.out
```

## Baseline behavior

The included baseline is the required simple **last-value predictor**:

- Index by load PC.
- Predict the most recently seen value for that PC.
- Confidence/use is `No` for a PC before first observation, otherwise `Yes`.

This gives you a clean reference point before implementing your own predictor design.
