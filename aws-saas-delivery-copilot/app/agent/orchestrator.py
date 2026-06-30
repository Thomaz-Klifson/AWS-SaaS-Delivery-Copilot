from typing import Any

from app.agent.tools import (
    feedback_analysis_tool,
    llm_cost_estimator_tool,
    search_knowledge_base_tool,
    security_questionnaire_tool,
    status_report_tool,
    well_architected_assessment_tool,
)
from app.models.schemas import AgentTaskResponse, ToolResult


def run_agent_task(tenant_id: str, task_type: str, payload: dict) -> AgentTaskResponse:
    if task_type == "knowledge_search":
        result = search_knowledge_base_tool(
            tenant_id=tenant_id,
            question=_required(payload, "question"),
            top_k=payload.get("top_k", 3),
        )
        tool_name = "search_knowledge_base_tool"
    elif task_type == "security_questionnaire":
        result = security_questionnaire_tool(tenant_id)
        tool_name = "security_questionnaire_tool"
    elif task_type == "feedback_analysis":
        result = feedback_analysis_tool(tenant_id)
        tool_name = "feedback_analysis_tool"
    elif task_type == "status_report":
        result = status_report_tool(
            project_name=_required(payload, "project_name"),
            progress=payload.get("progress", []),
            blockers=payload.get("blockers", []),
            next_steps=payload.get("next_steps", []),
            risks=payload.get("risks", []),
        )
        tool_name = "status_report_tool"
    elif task_type == "cost_estimate":
        result = llm_cost_estimator_tool(
            input_tokens=payload.get("input_tokens", 0),
            output_tokens=payload.get("output_tokens", 0),
            input_price_per_1k=payload.get("input_price_per_1k", 0.00025),
            output_price_per_1k=payload.get("output_price_per_1k", 0.00125),
        )
        tool_name = "llm_cost_estimator_tool"
    elif task_type == "well_architected_assessment":
        result = well_architected_assessment_tool(tenant_id)
        tool_name = "well_architected_assessment_tool"
    else:
        raise ValueError(f"Unsupported task_type: {task_type}")

    return AgentTaskResponse(
        tenant_id=tenant_id,
        task_type=task_type,
        tool_result=ToolResult(tool_name=tool_name, result=result),
    )


def _required(payload: dict[str, Any], key: str) -> Any:
    value = payload.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing required payload field: {key}")
    return value
