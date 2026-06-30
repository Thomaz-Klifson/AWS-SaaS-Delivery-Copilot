from fastapi.testclient import TestClient

from app.agent.orchestrator import run_agent_task
from app.agent.tools import (
    feedback_analysis_tool,
    llm_cost_estimator_tool,
    search_knowledge_base_tool,
    security_questionnaire_tool,
    status_report_tool,
    well_architected_assessment_tool,
)
from app.main import app
from app.rag.service import ingest_tenant_documents


client = TestClient(app)


def test_search_knowledge_base_tool_returns_sources():
    ingest_tenant_documents("tenant_acme")

    result = search_knowledge_base_tool(
        "tenant_acme",
        "Is customer data encrypted at rest and in transit?",
    )

    assert result["answer"]
    assert result["sources"][0]["source_file"] == "security_policy.md"
    assert result["retrieved_chunks"]


def test_security_questionnaire_tool_answers_all_questions():
    ingest_tenant_documents("tenant_acme")

    result = security_questionnaire_tool("tenant_acme")

    assert len(result) == 3
    assert {"question", "draft_answer", "sources", "confidence_hint"} <= set(result[0])
    assert result[0]["confidence_hint"] in {"high", "medium", "low"}


def test_feedback_analysis_tool_returns_deterministic_analysis():
    result = feedback_analysis_tool("tenant_acme")

    assert result["total_feedbacks"] == 5
    assert "cost visibility" in result["top_themes"]
    assert result["pain_points"]
    assert result["executive_summary"]


def test_status_report_tool_returns_markdown():
    result = status_report_tool(
        project_name="ACME SaaS Delivery Copilot",
        progress=["RAG implemented"],
        blockers=["Bedrock pending"],
        next_steps=["Add provider abstraction"],
        risks=["Scope creep"],
    )

    assert "# Status Report: ACME SaaS Delivery Copilot" in result
    assert "## Status\nBlocked" in result
    assert "- RAG implemented" in result


def test_llm_cost_estimator_tool_returns_costs():
    result = llm_cost_estimator_tool(input_tokens=1000, output_tokens=500)

    assert result["input_cost"] == 0.00025
    assert result["output_cost"] == 0.000625
    assert result["total_cost"] == 0.000875
    assert "not official" in result["note"]


def test_well_architected_assessment_tool_returns_six_pillars():
    ingest_tenant_documents("tenant_acme")

    result = well_architected_assessment_tool("tenant_acme")

    assert len(result) == 6
    assert {item["pillar"] for item in result} == {
        "Operational Excellence",
        "Security",
        "Reliability",
        "Performance Efficiency",
        "Cost Optimization",
        "Sustainability",
    }


def test_orchestrator_supports_all_task_types():
    ingest_tenant_documents("tenant_acme")

    tasks = [
        ("knowledge_search", {"question": "Does the platform expose APIs for integrations?"}),
        ("security_questionnaire", {}),
        ("feedback_analysis", {}),
        (
            "status_report",
            {
                "project_name": "ACME SaaS Delivery Copilot",
                "progress": ["Tenant summary endpoint implemented"],
                "blockers": [],
                "next_steps": ["Add Bedrock provider"],
                "risks": ["Scope creep before interview"],
            },
        ),
        ("cost_estimate", {"input_tokens": 1200, "output_tokens": 300}),
        ("well_architected_assessment", {}),
    ]

    for task_type, payload in tasks:
        response = run_agent_task("tenant_acme", task_type, payload)
        assert response.tenant_id == "tenant_acme"
        assert response.task_type == task_type
        assert response.tool_result.result


def test_agent_run_endpoint_security_questionnaire():
    response = client.post(
        "/tenants/tenant_acme/agent/run",
        json={"task_type": "security_questionnaire", "payload": {}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "security_questionnaire"
    assert data["tool_result"]["tool_name"] == "security_questionnaire_tool"
    assert len(data["tool_result"]["result"]) == 3


def test_agent_run_endpoint_status_report():
    response = client.post(
        "/tenants/tenant_acme/agent/run",
        json={
            "task_type": "status_report",
            "payload": {
                "project_name": "ACME SaaS Delivery Copilot",
                "progress": ["RAG ingestion implemented"],
                "blockers": ["Bedrock integration pending"],
                "next_steps": ["Add Bedrock provider"],
                "risks": ["Scope creep before interview"],
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tool_result"]["tool_name"] == "status_report_tool"
    assert "Status Report" in data["tool_result"]["result"]
