from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ComparisonResult:
    left_name: str
    right_name: str
    left_score: float
    right_score: float

    @property
    def winner(self) -> str:
        if self.left_score > self.right_score:
            return self.left_name
        if self.right_score > self.left_score:
            return self.right_name
        return "tie"


@dataclass
class CompareScoresUseCase:
    def execute(
        self,
        *,
        left_name: str,
        right_name: str,
        left_scores: list[float],
        right_scores: list[float],
    ) -> ComparisonResult:
        left_avg = sum(left_scores) / len(left_scores) if left_scores else 0.0
        right_avg = sum(right_scores) / len(right_scores) if right_scores else 0.0

        return ComparisonResult(
            left_name=left_name,
            right_name=right_name,
            left_score=left_avg,
            right_score=right_avg,
        )
