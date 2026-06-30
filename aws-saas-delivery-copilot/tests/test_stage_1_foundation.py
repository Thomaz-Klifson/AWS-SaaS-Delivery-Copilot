from fastapi.testclient import TestClient

from app.core.tenant_loader import (
    read_documents,
    read_feedback_items,
    read_security_questions,
)
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "aws-saas-delivery-copilot",
        "stage": "foundation",
    }


def test_tenant_summary_endpoint_for_acme():
    response = client.get("/tenants/tenant_acme/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant_acme"
    assert data["document_count"] == 2
    assert data["feedback_count"] == 5
    assert data["security_question_count"] == 3
    assert data["files"] == [
        "product_faq.md",
        "security_policy.md",
        "sample_feedback.csv",
        "security_questions.json",
    ]


def test_local_sample_files_are_read():
    assert len(read_documents("tenant_acme")) == 2
    assert len(read_feedback_items("tenant_acme")) == 5
    assert len(read_security_questions("tenant_acme")) == 3
