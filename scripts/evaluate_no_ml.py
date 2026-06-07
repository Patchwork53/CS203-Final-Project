#!/usr/bin/env python3
"""Evaluate the non-ML value predictor on a trace file."""

from __future__ import annotations

import argparse
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lvp.trace_parser import iter_trace
from lvp.value_predictor_no_ml import HybridLastValuePredictor


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the final non-ML load value predictor on a trace"
    )
    parser.add_argument("trace", help="Path to trace file")
    parser.add_argument(
        "--pair-threshold",
        type=int,
        default=1,
        help="Confidence threshold for the PC/address pair table",
    )
    parser.add_argument(
        "--disable-stride",
        action="store_true",
        help="Disable stable stride predictions and use only last-value prediction",
    )
    parser.add_argument(
        "--stride-threshold",
        type=int,
        default=2,
        help="Confidence threshold for stride prediction",
    )
    args = parser.parse_args()

    predictor = HybridLastValuePredictor(
        pair_threshold=args.pair_threshold,
        enable_stride=not args.disable_stride,
        stride_threshold=args.stride_threshold,
    )
    stats = predictor.evaluate_trace(iter_trace(args.trace))

    if stats.total_loads == 0:
        print("No parsable load events were found. Check trace format.")
        return

    print("== Non-ML Value Predictor Results ==")
    print("Strategy:             pc-address/address/pc hybrid")
    print(f"Pair threshold:       {args.pair_threshold}")
    stride_enabled = not args.disable_stride
    print(f"Stride enabled:       {stride_enabled}")
    if stride_enabled:
        print(f"Stride threshold:     {args.stride_threshold}")
    print(f"Trace events:         {stats.total_loads}")
    print(f"Predictions used:     {stats.predictions_made}")
    print(f"Correct predictions:  {stats.correct_predictions}")
    print(f"Coverage:             {stats.coverage:.4f}")
    print(f"Accuracy (used only): {stats.accuracy:.4f}")
    print(f"Accuracy (overall):   {stats.effective_accuracy:.4f}")


if __name__ == "__main__":
    main()
