import json
import urllib.error
import urllib.request

from django.conf import settings

from .base import ScoringResult


class AnthropicScoringProvider:
    def score(self, job_description: str, resume_text: str) -> ScoringResult:
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when AI_PROVIDER=anthropic")

        prompt = (
            "Score this resume against the job description from 0-100 and provide a brief summary. "
            'Respond with JSON only: {"score": number, "summary": string}.\n\n'
            f"Job:\n{job_description}\n\nResume:\n{resume_text}"
        )
        payload = {
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Anthropic request failed: {exc}") from exc

        content = body["content"][0]["text"]
        parsed = json.loads(content)
        return ScoringResult(score=float(parsed["score"]), summary=str(parsed["summary"]))
