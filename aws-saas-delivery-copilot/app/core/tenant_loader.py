import csv
import json
from pathlib import Path

from app.models.schemas import DocumentMetadata, FeedbackItem, SecurityQuestion, TenantSummary


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data" / "tenants"


def get_tenant_path(tenant_id: str) -> Path:
    return DATA_ROOT / tenant_id


def read_documents(tenant_id: str) -> list[DocumentMetadata]:
    documents_path = get_tenant_path(tenant_id) / "documents"
    if not documents_path.exists():
        return []

    documents = []
    for file_path in sorted(path for path in documents_path.iterdir() if path.is_file()):
        documents.append(
            DocumentMetadata(
                file_name=file_path.name,
                path=str(file_path.relative_to(PROJECT_ROOT)),
                size_bytes=file_path.stat().st_size,
            )
        )
    return documents


def read_feedback_items(tenant_id: str) -> list[FeedbackItem]:
    feedback_path = get_tenant_path(tenant_id) / "feedback" / "sample_feedback.csv"
    if not feedback_path.exists():
        return []

    with feedback_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return [FeedbackItem(**row) for row in csv.DictReader(csv_file)]


def read_security_questions(tenant_id: str) -> list[SecurityQuestion]:
    questions_path = get_tenant_path(tenant_id) / "questionnaires" / "security_questions.json"
    if not questions_path.exists():
        return []

    with questions_path.open("r", encoding="utf-8-sig") as json_file:
        questions = json.load(json_file)

    return [SecurityQuestion(**question) for question in questions]


def get_tenant_summary(tenant_id: str) -> TenantSummary:
    documents = read_documents(tenant_id)
    feedback_items = read_feedback_items(tenant_id)
    security_questions = read_security_questions(tenant_id)

    files = [document.file_name for document in documents]
    if feedback_items:
        files.append("sample_feedback.csv")
    if security_questions:
        files.append("security_questions.json")

    return TenantSummary(
        tenant_id=tenant_id,
        document_count=len(documents),
        feedback_count=len(feedback_items),
        security_question_count=len(security_questions),
        files=files,
    )
