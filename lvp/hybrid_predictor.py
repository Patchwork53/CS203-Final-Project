"""Table-based non-ML load value predictor.

This module implements an online table predictor for the project:
exact PC/address context first, then address context, then PC context.
"""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from typing import Iterable, Protocol, TypeVar


MAX_CONFIDENCE = 7
TableKey = TypeVar("TableKey", bound=Hashable)


@dataclass(frozen=True)
class Prediction:
    predicted_value: int
    use_prediction: bool


@dataclass
class TableEntry:
    last_value: int
    confidence: int = 0
    stride: int = 0
    stride_confidence: int = 0


@dataclass(frozen=True)
class PredictionStats:
    total_loads: int
    predictions_made: int
    correct_predictions: int

    @property
    def coverage(self) -> float:
        if self.total_loads == 0:
            return 0.0
        return self.predictions_made / self.total_loads

    @property
    def accuracy(self) -> float:
        if self.predictions_made == 0:
            return 0.0
        return self.correct_predictions / self.predictions_made

    @property
    def effective_accuracy(self) -> float:
        if self.total_loads == 0:
            return 0.0
        return self.correct_predictions / self.total_loads


class TracePredictor(Protocol):
    def predict(self, pc: int, address: int) -> Prediction: ...

    def update(self, pc: int, address: int, actual_value: int) -> None: ...


def evaluate_trace(predictor: TracePredictor, events: Iterable) -> PredictionStats:
    total_loads = 0
    predictions_made = 0
    correct_predictions = 0

    for event in events:
        total_loads += 1
        prediction = predictor.predict(event.pc, event.address)
        if prediction.use_prediction:
            predictions_made += 1
            if prediction.predicted_value == event.value:
                correct_predictions += 1
        predictor.update(event.pc, event.address, event.value)

    return PredictionStats(
        total_loads=total_loads,
        predictions_made=predictions_made,
        correct_predictions=correct_predictions,
    )


class HybridLastValuePredictor:
    """Hybrid value predictor that prefers the most specific matching context.

    Prediction order:
    1. Repeated stride for exact `(PC, address)` or PC context, when enabled.
    2. Exact `(PC, address)` pair after it has shown a stable repeat.
    3. Load address, once seen.
    4. Load PC, once seen.
    """

    def __init__(
        self,
        pair_threshold: int = 1,
        *,
        enable_stride: bool = True,
        stride_threshold: int = 2,
    ) -> None:
        if pair_threshold < 0:
            raise ValueError("pair_threshold must be non-negative")
        if stride_threshold < 0:
            raise ValueError("stride_threshold must be non-negative")

        self.pair_threshold = pair_threshold
        self.enable_stride = enable_stride
        self.stride_threshold = stride_threshold
        self._pc_address_table: dict[tuple[int, int], TableEntry] = {}
        self._pc_table: dict[int, TableEntry] = {}
        self._address_table: dict[int, TableEntry] = {}

    def predict(self, pc: int, address: int) -> Prediction:
        pc_address_entry = self._pc_address_table.get((pc, address))
        if pc_address_entry is not None and self._has_stable_stride(pc_address_entry):
            return Prediction(predicted_value=pc_address_entry.last_value + pc_address_entry.stride, use_prediction=True)
        if pc_address_entry is not None and pc_address_entry.confidence >= self.pair_threshold:
            return Prediction(predicted_value=pc_address_entry.last_value, use_prediction=True)

        address_entry = self._address_table.get(address)
        if address_entry is not None:
            return Prediction(predicted_value=address_entry.last_value, use_prediction=True)

        pc_entry = self._pc_table.get(pc)
        if pc_entry is not None and self._has_stable_stride(pc_entry):
            return Prediction(predicted_value=pc_entry.last_value + pc_entry.stride, use_prediction=True)
        if pc_entry is not None:
            return Prediction(predicted_value=pc_entry.last_value, use_prediction=True)

        return Prediction(predicted_value=0, use_prediction=False)

    def _has_stable_stride(self, entry: TableEntry) -> bool:
        return (
            self.enable_stride
            and entry.stride != 0
            and entry.stride_confidence >= self.stride_threshold
        )

    def update(self, pc: int, address: int, actual_value: int) -> None:
        self._update_table(self._pc_address_table, (pc, address), actual_value)
        self._update_table(self._address_table, address, actual_value)
        self._update_table(self._pc_table, pc, actual_value)

    def _update_table(self, table: dict[TableKey, TableEntry], key: TableKey, actual_value: int) -> None:
        entry = table.get(key)
        if entry is None:
            table[key] = TableEntry(last_value=actual_value)
            return

        next_stride = actual_value - entry.last_value

        if entry.last_value == actual_value:
            entry.confidence = min(entry.confidence + 1, MAX_CONFIDENCE)
        else:
            entry.confidence = max(entry.confidence - 1, 0)

        if next_stride == entry.stride:
            entry.stride_confidence = min(entry.stride_confidence + 1, MAX_CONFIDENCE)
        else:
            entry.stride_confidence = max(entry.stride_confidence - 1, 0)

        entry.stride = next_stride
        entry.last_value = actual_value

    def evaluate_trace(self, events: Iterable) -> PredictionStats:
        return evaluate_trace(self, events)
