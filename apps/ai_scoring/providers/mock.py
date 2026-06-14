import hashlib

from .base import ScoringResult


class MockScoringProvider:
    def score(self, job_description: str, resume_text: str) -> ScoringResult:
        digest = hashlib.sha256(resume_text.encode("utf-8")).hexdigest()
        score = 40 + (int(digest[:8], 16) % 56)
        summary = (
            f"Mock score {score}/100 — deterministic match for role based on resume keywords "
            f"and experience signals."
        )
        return ScoringResult(score=float(score), summary=summary)
