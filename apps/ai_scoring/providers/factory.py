from django.conf import settings

from .base import ScoringProvider
from .mock import MockScoringProvider


def get_scoring_provider() -> ScoringProvider:
    provider = settings.AI_PROVIDER.lower()

    if provider == "mock":
        return MockScoringProvider()

    if provider == "openai":
        from .openai import OpenAIScoringProvider

        return OpenAIScoringProvider()

    if provider == "anthropic":
        from .anthropic import AnthropicScoringProvider

        return AnthropicScoringProvider()

    raise ValueError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")
