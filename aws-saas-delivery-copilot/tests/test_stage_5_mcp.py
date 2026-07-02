import json

from fastapi.testclient import TestClient

from app.main import app
from app.mcp_server.registry import get_tool, list_tools
from app.mcp_server.schemas import JsonRpcRequest
from app.mcp_server.server import handle_mcp_request
from app.rag.service import ingest_tenant_documents


client = TestClient(app)


def test_mcp_registry_exposes_expected_tools():
    tools = list_tools()
    tool_names = {tool.name for tool in tools}

    assert tool_names == {
        "knowledge_search",
        "security_questionnaire",
        "feedback_analysis",
        "status_report",
        "cost_estimate",
        "well_architected_assessment",
    }
    assert get_tool("knowledge_search").inputSchema["required"] == ["question"]


def test_mcp_initialize():
    response = handle_mcp_request(
        JsonRpcRequest(id=1, method="initialize", params={})
    )

    assert response.error is None
    assert response.result["protocolVersion"] == "2025-06-18"
    assert response.result["serverInfo"]["name"] == "aws-saas-delivery-copilot"
    assert response.result["capabilities"]["tools"]["listChanged"] is False


def test_mcp_tools_list():
    response = handle_mcp_request(
        JsonRpcRequest(id=2, method="tools/list", params={})
    )

    assert response.error is None
    assert len(response.result["tools"]) == 6
    assert response.result["tools"][0]["inputSchema"]["type"] == "object"


def test_mcp_tools_call_knowledge_search():
    ingest_tenant_documents("tenant_acme")

    response = handle_mcp_request(
        JsonRpcRequest(
            id=3,
            method="tools/call",
            params={
                "name": "knowledge_search",
                "arguments": {
                    "tenant_id": "tenant_acme",
                    "question": "Does the platform expose APIs for integrations?",
                    "top_k": 3,
                },
            },
        )
    )

    assert response.error is None
    content = response.result["content"]
    assert content[0]["type"] == "text"
    parsed = json.loads(content[0]["text"])
    assert parsed["sources"][0]["source_file"] == "product_faq.md"


def test_mcp_tools_call_cost_estimate():
    response = handle_mcp_request(
        JsonRpcRequest(
            id=4,
            method="tools/call",
            params={
                "name": "cost_estimate",
                "arguments": {
                    "tenant_id": "tenant_acme",
                    "input_tokens": 1000,
                    "output_tokens": 500,
                },
            },
        )
    )

    assert response.error is None
    parsed = json.loads(response.result["content"][0]["text"])
    assert parsed["total_cost"] == 0.000875


def test_mcp_tools_call_unknown_tool_returns_json_rpc_error():
    response = handle_mcp_request(
        JsonRpcRequest(
            id=5,
            method="tools/call",
            params={"name": "missing_tool", "arguments": {}},
        )
    )

    assert response.result is None
    assert response.error.code == -32602
    assert "Unknown tool" in response.error.message


def test_mcp_rpc_endpoint_initialize():
    response = client.post(
        "/mcp/rpc",
        json={"jsonrpc": "2.0", "id": "init-1", "method": "initialize", "params": {}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "init-1"
    assert data["result"]["protocolVersion"] == "2025-06-18"


def test_mcp_rpc_endpoint_tools_call():
    response = client.post(
        "/mcp/rpc",
        json={
            "jsonrpc": "2.0",
            "id": "call-1",
            "method": "tools/call",
            "params": {
                "name": "cost_estimate",
                "arguments": {"input_tokens": 1000, "output_tokens": 500},
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    parsed = json.loads(data["result"]["content"][0]["text"])
    assert parsed["input_tokens"] == 1000


def test_mcp_tools_demo_endpoints():
    list_response = client.get("/mcp/tools")
    assert list_response.status_code == 200
    assert len(list_response.json()["tools"]) == 6

    call_response = client.post(
        "/mcp/tools/cost_estimate/call",
        json={"input_tokens": 1000, "output_tokens": 500},
    )
    assert call_response.status_code == 200
    parsed = json.loads(call_response.json()["content"][0]["text"])
    assert parsed["output_tokens"] == 500
