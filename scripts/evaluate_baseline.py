#!/usr/bin/env python3
"""Evaluate the last-value load predictor on a trace file."""

from __future__ import annotations

import argparse
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lvp.baseline_last_value import LastValuePredictor
from lvp.trace_parser import iter_trace


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate PC-indexed last-value predictor on a load trace"
    )
    parser.add_argument("trace", help="Path to trace file")
    args = parser.parse_args()

    predictor = LastValuePredictor()

    total_events = 0
    used_predictions = 0
    correct_predictions = 0

    for event in iter_trace(args.trace):
        total_events += 1

        pred = predictor.predict(event.pc, event.address)
        if pred.use_prediction:
            used_predictions += 1
            if pred.predicted_value == event.value:
                correct_predictions += 1

        predictor.update(event.pc, event.address, event.value)

    if total_events == 0:
        print("No parsable load events were found. Check trace format.")
        return

    coverage = used_predictions / total_events
    used_accuracy = (correct_predictions / used_predictions) if used_predictions else 0.0
    overall_accuracy = correct_predictions / total_events

    print("== Last-Value Baseline Results ==")
    print(f"Trace events:         {total_events}")
    print(f"Predictions used:     {used_predictions}")
    print(f"Correct predictions:  {correct_predictions}")
    print(f"Coverage:             {coverage:.4f}")
    print(f"Accuracy (used only): {used_accuracy:.4f}")
    print(f"Accuracy (overall):   {overall_accuracy:.4f}")


if __name__ == "__main__":
    main()
