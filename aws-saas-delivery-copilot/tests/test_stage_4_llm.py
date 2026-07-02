from fastapi.testclient import TestClient

from app.llm.factory import get_llm_provider
from app.llm.mock_provider import MockLLMProvider
from app.main import app
from app.rag.service import ingest_tenant_documents


client = TestClient(app)


def test_mock_llm_provider_generates_deterministic_response():
    provider = MockLLMProvider()

    response = provider.generate(
        system_prompt="Answer from sources.",
        user_prompt=(
            "Question:\nIs data encrypted?\n\n"
            "Context:\n"
            "Source: security_policy.md\n"
            "All customer data must be encrypted at rest and in transit."
        ),
    )

    assert response.provider == "mock"
    assert response.model_id == "mock-deterministic-local"
    assert "security_policy.md" in response.text
    assert response.total_tokens >= response.input_tokens


def test_factory_returns_mock_provider_by_default():
    provider = get_llm_provider()

    assert isinstance(provider, MockLLMProvider)


def test_llm_test_endpoint_uses_mock_provider():
    response = client.post(
        "/llm/test",
        json={"prompt": "Say hello in one sentence."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "mock"
    assert data["text"]
    assert data["total_tokens"] >= 1


def test_rag_ask_uses_mock_provider_and_keeps_sources():
    ingest_tenant_documents("tenant_acme")

    response = client.post(
        "/tenants/tenant_acme/rag/ask",
        json={
            "question": "Is customer data encrypted at rest and in transit?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert "security_policy.md" in data["answer"]
    assert data["sources"][0]["source_file"] == "security_policy.md"
