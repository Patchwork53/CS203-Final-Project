"""Last-value baseline predictor for load value prediction."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Prediction:
    predicted_value: int
    use_prediction: bool


class LastValuePredictor:
    """Baseline: track last observed value per load PC and always use when known."""

    def __init__(self) -> None:
        self._table: dict[int, int] = {}

    def predict(self, pc: int, address: int) -> Prediction:
        # Address is intentionally unused in this baseline; this is PC-indexed.
        _ = address
        if pc not in self._table:
            return Prediction(predicted_value=0, use_prediction=False)
        return Prediction(predicted_value=self._table[pc], use_prediction=True)

    def update(self, pc: int, address: int, actual_value: int) -> None:
        _ = address
        self._table[pc] = actual_value
