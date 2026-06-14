import json
import urllib.error
import urllib.request

from django.conf import settings

from .base import ScoringResult


class OpenAIScoringProvider:
    def score(self, job_description: str, resume_text: str) -> ScoringResult:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")

        prompt = (
            "Score this resume against the job description from 0-100 and provide a brief summary. "
            'Respond with JSON: {"score": number, "summary": string}.\n\n'
            f"Job:\n{job_description}\n\nResume:\n{resume_text}"
        )
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc

        content = body["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return ScoringResult(score=float(parsed["score"]), summary=str(parsed["summary"]))
