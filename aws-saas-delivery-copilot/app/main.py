from fastapi import FastAPI, HTTPException

from app.agent.orchestrator import run_agent_task
from app.core.config import settings
from app.core.tenant_loader import get_tenant_summary
from app.llm.factory import get_llm_provider
from app.llm.provider import LLMResponse
from app.mcp_server.registry import list_tools
from app.mcp_server.schemas import JsonRpcRequest, JsonRpcResponse
from app.mcp_server.server import call_tool_by_name, handle_mcp_request
from app.models.schemas import (
    AgentTaskRequest,
    AgentTaskResponse,
    HealthResponse,
    LLMTestRequest,
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


@app.post("/tenants/{tenant_id}/agent/run", response_model=AgentTaskResponse)
def agent_run(tenant_id: str, request: AgentTaskRequest) -> AgentTaskResponse:
    try:
        return run_agent_task(
            tenant_id=tenant_id,
            task_type=request.task_type,
            payload=request.payload,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/llm/test", response_model=LLMResponse)
def llm_test(request: LLMTestRequest) -> LLMResponse:
    try:
        provider = get_llm_provider()
        return provider.generate(
            system_prompt="You are a concise assistant for local provider testing.",
            user_prompt=f"Question:\n{request.prompt}\n\nContext:\nManual provider test.",
            temperature=0.2,
            max_tokens=120,
        )
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/mcp/rpc", response_model=JsonRpcResponse)
def mcp_rpc(request: JsonRpcRequest) -> JsonRpcResponse:
    return handle_mcp_request(request)


@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": [tool.model_dump(by_alias=True) for tool in list_tools()]}


@app.post("/mcp/tools/{tool_name}/call")
def mcp_tool_call(tool_name: str, arguments: dict):
    try:
        return call_tool_by_name(tool_name, arguments)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
