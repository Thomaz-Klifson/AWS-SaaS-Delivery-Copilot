from fastapi.testclient import TestClient

from app.main import app
from app.rag.chunking import chunk_text
from app.rag.service import ask_tenant_question, ingest_tenant_documents


client = TestClient(app)


def test_chunking_preserves_metadata_and_overlap():
    chunks = chunk_text(
        text="alpha beta gamma delta epsilon zeta eta theta",
        tenant_id="tenant_test",
        source_file="example.md",
        chunk_size=24,
        overlap=6,
    )

    assert len(chunks) > 1
    assert chunks[0].tenant_id == "tenant_test"
    assert chunks[0].source_file == "example.md"
    assert chunks[0].chunk_id == "example.md:0"
    assert chunks[0].text


def test_ingest_tenant_acme_documents():
    response = ingest_tenant_documents("tenant_acme")

    assert response.tenant_id == "tenant_acme"
    assert response.document_count == 2
    assert response.chunk_count >= 2
    assert response.indexed_files == ["product_faq.md", "security_policy.md"]


def test_security_question_retrieves_security_policy():
    ingest_tenant_documents("tenant_acme")

    response = ask_tenant_question(
        "tenant_acme",
        "Is customer data encrypted at rest and in transit?",
    )

    assert response.sources
    assert response.sources[0].source_file == "security_policy.md"
    assert "security_policy.md" in {source.source_file for source in response.sources}


def test_integrations_question_retrieves_product_faq():
    ingest_tenant_documents("tenant_acme")

    response = ask_tenant_question(
        "tenant_acme",
        "Does the platform expose APIs for integrations?",
    )

    assert response.sources
    assert response.sources[0].source_file == "product_faq.md"
    assert "product_faq.md" in {source.source_file for source in response.sources}


def test_rag_ingest_endpoint():
    response = client.post("/tenants/tenant_acme/rag/ingest")

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant_acme"
    assert data["document_count"] == 2
    assert data["chunk_count"] >= 2


def test_rag_ask_endpoint():
    client.post("/tenants/tenant_acme/rag/ingest")

    response = client.post(
        "/tenants/tenant_acme/rag/ask",
        json={
            "question": "Does the platform expose APIs for integrations?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant_acme"
    assert data["question"] == "Does the platform expose APIs for integrations?"
    assert data["sources"][0]["source_file"] == "product_faq.md"
    assert data["retrieved_chunks"]
