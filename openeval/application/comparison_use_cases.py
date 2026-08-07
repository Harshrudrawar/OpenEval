from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComparisonResult:
    left_name: str
    right_name: str
    left_accuracy: float
    right_accuracy: float

    @property
    def winner(self) -> str:
        if self.left_accuracy > self.right_accuracy:
            return self.left_name
        if self.right_accuracy > self.left_accuracy:
            return self.right_name
        return "tie"

    @property
    def margin(self) -> float:
        return abs(self.left_accuracy - self.right_accuracy)


@dataclass
class CompareScoresUseCase:
    def execute(
        self,
        *,
        left_name: str,
        right_name: str,
        left_accuracy: float,
        right_accuracy: float,
    ) -> ComparisonResult:
        return ComparisonResult(
            left_name=left_name,
            right_name=right_name,
            left_accuracy=left_accuracy,
            right_accuracy=right_accuracy,
        )
