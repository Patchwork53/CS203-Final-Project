# CS203 Final Project Report: Load Value Prediction

## Overview

This project implements Option 1, a practical non-ML load value predictor. The predictor operates online over a memory load trace. For each load, it receives:

- the load instruction PC,
- the memory address read by the load,
- and, after prediction, the actual loaded value.

The predictor outputs:

- a predicted value,
- and a binary decision for whether to use that prediction.

The required baseline is also implemented: a simple PC-indexed last-value predictor that predicts the most recent value loaded by the same PC.

## Approach

We started with the required PC-indexed last-value baseline because it is simple, online, and directly matches the project requirement. That baseline captures temporal value locality at the load-instruction level, but it misses two useful patterns:

- A load address may repeatedly contain the same value even when accessed by different PCs.
- A specific `(PC, address)` pair may be more predictable than either the PC or address alone.
- Some values change by a repeated stride rather than remaining constant.

The final predictor converged toward a hybrid design that uses increasingly general contexts. It first tries the most specific context, exact `(PC, address)`, then falls back to address and PC contexts. We then added stride prediction only for the contexts where it improved results: exact `(PC, address)` and PC. Address-only stride was not used in the final design because it was noisier in testing.

## Predictor Design

The final predictor is implemented in `lvp/value_predictor_no_ml.py`.

It maintains three tables:

- `PC-address table`: keyed by `(load PC, load address)`.
- `Address table`: keyed by load address.
- `PC table`: keyed by load PC.

Each table entry stores:

- `last_value`: the most recent value observed for that context.
- `confidence`: a saturating counter for repeated last values.
- `stride`: the most recent delta between consecutive observed values.
- `stride_confidence`: a saturating counter for repeated strides.

The prediction order is:

1. If stride prediction is enabled and the exact `(PC, address)` entry has a stable nonzero stride, predict `last_value + stride`.
2. If stride prediction is enabled and the PC entry has a stable nonzero stride, predict `last_value + stride`.
3. If the exact `(PC, address)` entry has enough last-value confidence, predict its `last_value`.
4. If the address entry exists, predict its `last_value`.
5. If the PC entry exists, predict its `last_value`.
6. Otherwise, do not use a prediction.

The default thresholds are:

- `pair_threshold = 1`
- `stride_threshold = 2`
- `MAX_CONFIDENCE = 7`

The predictor learns online. It predicts before seeing the current actual value, then updates all three tables after the actual value is known.

## Baseline

The baseline is implemented in `lvp/baseline_last_value.py`.

It uses one table keyed only by load PC:

1. If the PC has been seen before, predict the last value observed for that PC.
2. If the PC has not been seen before, do not use a prediction.
3. After the actual load value is known, update the PC table.

This is the required comparison point from the project instructions.

## Experimental Setup

Traces use the format:

```text
0xPC: R 0xADDRESS, 0xVALUE
```

The trace generator is a custom Intel Pin pintool in `pin-tools/loadvaltrace.cpp`. It follows the modified `pinatrace` approach described in the project instructions:

- instrument memory reads,
- ignore stores,
- use `PIN_SafeCopy` to read the loaded value,
- print PC, load address, and loaded value.

The primary evaluation trace used here is:

- `traces/ls_trace.out`
- 212,930 load events

A tiny sanity trace is also included:

- `sample_trace.out`
- 7 load events

The metrics reported by the evaluation scripts are:

- `Coverage`: predictions used / total load events.
- `Accuracy (used only)`: correct predictions / predictions used.
- `Accuracy (overall)`: correct predictions / total load events.

We use `Accuracy (overall)` as the main comparison metric because it includes both correctness and the decision to use or not use a prediction.

## Results

Results on `traces/ls_trace.out`:

| Predictor | Predictions Used | Correct | Coverage | Used Accuracy | Overall Accuracy |
|---|---:|---:|---:|---:|---:|
| PC last-value baseline | 206,300 | 105,068 | 0.9689 | 0.5093 | 0.4934 |
| Hybrid without stride | 211,050 | 161,747 | 0.9912 | 0.7664 | 0.7596 |
| Hybrid with stride | 211,050 | 164,570 | 0.9912 | 0.7798 | 0.7729 |

The final hybrid stride predictor improves overall accuracy from `0.4934` to `0.7729` on the main trace.

Compared to the baseline, the final predictor gets:

- 59,502 more correct predictions,
- higher coverage,
- and substantially higher used-only accuracy.

## Analysis

The baseline performs poorly because PC-only last-value prediction merges all behavior for one load instruction. If a load PC accesses changing data, its last value may not be reliable.

The hybrid predictor improves accuracy for two reasons:

- The exact `(PC, address)` table captures highly specific local behavior. This avoids mixing unrelated values that share only a PC or only an address.
- The address and PC fallback tables preserve coverage when the exact pair has not become confident yet.

Stride prediction provides an additional improvement because some loads do not repeat the same value, but change by a stable delta. We only use stride for exact `(PC, address)` and PC contexts because address-only stride was less reliable in testing.

The final design remains practical and hardware-like: it uses small table entries, saturating counters, online updates, and no offline training.

## Source Code

Important source files:

- `pin-tools/loadvaltrace.cpp`: custom Pin trace generator.
- `lvp/trace_parser.py`: parser for trace lines.
- `lvp/baseline_last_value.py`: required PC-indexed last-value baseline.
- `lvp/value_predictor_no_ml.py`: final hybrid stride predictor.
- `scripts/evaluate_baseline.py`: baseline evaluator.
- `scripts/evaluate_no_ml.py`: final predictor evaluator.
- `scripts/setup_pin_tool.sh`: builds the custom Pin tool.
- `scripts/collect_trace.sh`: collects a trace using Pin.

## Reproducibility

The exact commands used to build, collect traces, and evaluate predictors are listed in `INSTRUCTIONS.md`.
