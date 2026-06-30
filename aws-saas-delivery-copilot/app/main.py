from fastapi import FastAPI

from app.core.config import settings
from app.core.tenant_loader import get_tenant_summary
from app.models.schemas import (
    HealthResponse,
    RagAskRequest,
    RagAskResponse,
    RagIngestResponse,
    TenantSummary,
)
from app.rag.service import ask_tenant_question, ingest_tenant_documents


app = FastAPI(
    title=settings.app_name,
    description="Agentic GenAI platform for SaaS delivery, RAG, feedback intelligence and AWS consulting workflows.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AWS SaaS Delivery Copilot",
        "status": "running",
        "stage": "foundation",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="aws-saas-delivery-copilot",
        stage="foundation",
    )


@app.get("/tenants/{tenant_id}/summary", response_model=TenantSummary)
def tenant_summary(tenant_id: str) -> TenantSummary:
    return get_tenant_summary(tenant_id)


@app.post("/tenants/{tenant_id}/rag/ingest", response_model=RagIngestResponse)
def rag_ingest(tenant_id: str) -> RagIngestResponse:
    return ingest_tenant_documents(tenant_id)


@app.post("/tenants/{tenant_id}/rag/ask", response_model=RagAskResponse)
def rag_ask(tenant_id: str, request: RagAskRequest) -> RagAskResponse:
    return ask_tenant_question(
        tenant_id=tenant_id,
        question=request.question,
        top_k=request.top_k,
    )
