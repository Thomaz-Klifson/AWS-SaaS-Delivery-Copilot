from app.mcp_server.schemas import McpToolDefinition


TOOL_DEFINITIONS = [
    McpToolDefinition(
        name="knowledge_search",
        title="Knowledge Search",
        description="Search tenant-approved knowledge base documents with local RAG and return source-backed results.",
        task_type="knowledge_search",
        inputSchema={
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "default": "tenant_acme"},
                "question": {"type": "string", "description": "Question to answer from tenant sources."},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 10, "default": 3},
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    ),
    McpToolDefinition(
        name="security_questionnaire",
        title="Security Questionnaire",
        description="Draft source-backed answers for the tenant security questionnaire.",
        task_type="security_questionnaire",
        inputSchema={
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "default": "tenant_acme"},
            },
            "additionalProperties": False,
        },
    ),
    McpToolDefinition(
        name="feedback_analysis",
        title="Feedback Analysis",
        description="Analyze tenant feedback with deterministic themes, positive signals, pain points and opportunities.",
        task_type="feedback_analysis",
        inputSchema={
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "default": "tenant_acme"},
            },
            "additionalProperties": False,
        },
    ),
    McpToolDefinition(
        name="status_report",
        title="Status Report",
        description="Generate a Markdown delivery status report for an AWS/SaaS consulting project.",
        task_type="status_report",
        inputSchema={
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "default": "tenant_acme"},
                "project_name": {"type": "string"},
                "progress": {"type": "array", "items": {"type": "string"}, "default": []},
                "blockers": {"type": "array", "items": {"type": "string"}, "default": []},
                "next_steps": {"type": "array", "items": {"type": "string"}, "default": []},
                "risks": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["project_name"],
            "additionalProperties": False,
        },
    ),
    McpToolDefinition(
        name="cost_estimate",
        title="LLM Cost Estimate",
        description="Estimate LLM token usage cost from configurable example prices.",
        task_type="cost_estimate",
        inputSchema={
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "default": "tenant_acme"},
                "input_tokens": {"type": "integer", "minimum": 0, "default": 0},
                "output_tokens": {"type": "integer", "minimum": 0, "default": 0},
                "input_price_per_1k": {"type": "number", "minimum": 0, "default": 0.00025},
                "output_price_per_1k": {"type": "number", "minimum": 0, "default": 0.00125},
            },
            "additionalProperties": False,
        },
    ),
    McpToolDefinition(
        name="well_architected_assessment",
        title="Well-Architected Assessment",
        description="Create a simplified six-pillar AWS Well-Architected style assessment from tenant evidence.",
        task_type="well_architected_assessment",
        inputSchema={
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "default": "tenant_acme"},
            },
            "additionalProperties": False,
        },
    ),
]


def list_tools() -> list[McpToolDefinition]:
    return TOOL_DEFINITIONS


def get_tool(name: str) -> McpToolDefinition | None:
    for tool in TOOL_DEFINITIONS:
        if tool.name == name:
            return tool
    return None
