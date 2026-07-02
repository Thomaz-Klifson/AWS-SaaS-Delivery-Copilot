import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def force_mock_llm_provider():
    original_provider = settings.llm_provider
    settings.llm_provider = "mock"
    try:
        yield
    finally:
        settings.llm_provider = original_provider
