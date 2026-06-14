from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ScoringResult:
    score: float
    summary: str


class ScoringProvider(Protocol):
    def score(self, job_description: str, resume_text: str) -> ScoringResult: ...
