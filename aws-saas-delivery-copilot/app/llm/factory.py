from app.core.config import settings
from app.llm.bedrock_provider import BedrockConverseProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.provider import LLMProvider


def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider.strip().lower()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "bedrock":
        return BedrockConverseProvider()
    raise ValueError(
        f"Unsupported LLM_PROVIDER={settings.llm_provider!r}. "
        "Use 'mock' or 'bedrock'."
    )
