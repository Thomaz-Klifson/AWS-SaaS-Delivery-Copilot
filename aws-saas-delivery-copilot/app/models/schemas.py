from pydantic import BaseModel, Field


class Tenant(BaseModel):
    tenant_id: str
    name: str | None = None


class DocumentMetadata(BaseModel):
    file_name: str
    path: str
    size_bytes: int


class FeedbackItem(BaseModel):
    feedback_id: str
    customer_segment: str
    feedback: str


class SecurityQuestion(BaseModel):
    question: str
    expected_source: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    stage: str


class TenantSummary(BaseModel):
    tenant_id: str
    document_count: int = Field(ge=0)
    feedback_count: int = Field(ge=0)
    security_question_count: int = Field(ge=0)
    files: list[str]


class RagIngestResponse(BaseModel):
    tenant_id: str
    document_count: int = Field(ge=0)
    chunk_count: int = Field(ge=0)
    indexed_files: list[str]


class RagAskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class RagSource(BaseModel):
    source_file: str
    chunk_id: str
    score: float


class RetrievedChunk(BaseModel):
    source_file: str
    chunk_id: str
    text: str
    score: float


class RagAskResponse(BaseModel):
    answer: str
    tenant_id: str
    question: str
    sources: list[RagSource]
    retrieved_chunks: list[RetrievedChunk]
    top_k: int


class SecurityQuestionnaireItem(BaseModel):
    question: str
    draft_answer: str
    sources: list[RagSource]
    confidence_hint: str


class FeedbackAnalysisResponse(BaseModel):
    total_feedbacks: int
    top_themes: list[str]
    positive_signals: list[str]
    pain_points: list[str]
    opportunities: list[str]
    executive_summary: str


class CostEstimateResponse(BaseModel):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    input_price_per_1k: float = Field(ge=0)
    output_price_per_1k: float = Field(ge=0)
    input_cost: float = Field(ge=0)
    output_cost: float = Field(ge=0)
    total_cost: float = Field(ge=0)
    note: str


class WellArchitectedFinding(BaseModel):
    pillar: str
    finding: str
    risk_level: str
    recommendation: str


class ToolResult(BaseModel):
    tool_name: str
    result: dict | list | str


class AgentTaskRequest(BaseModel):
    task_type: str = Field(min_length=1)
    payload: dict = Field(default_factory=dict)


class AgentTaskResponse(BaseModel):
    tenant_id: str
    task_type: str
    tool_result: ToolResult
