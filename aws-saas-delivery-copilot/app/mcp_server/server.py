import json
from typing import Any

from pydantic import ValidationError

from app.agent.orchestrator import run_agent_task
from app.mcp_server.registry import get_tool, list_tools
from app.mcp_server.schemas import (
    JsonRpcRequest,
    JsonRpcResponse,
    McpToolCallParams,
    McpToolResultContent,
)


PROTOCOL_VERSION = "2025-06-18"
DEFAULT_TENANT_ID = "tenant_acme"


def handle_mcp_request(request: JsonRpcRequest) -> JsonRpcResponse:
    if request.method == "initialize":
        return _success(request.id, _initialize_result())
    if request.method == "tools/list":
        return _success(request.id, {"tools": [_tool_dump(tool) for tool in list_tools()]})
    if request.method == "tools/call":
        return _handle_tools_call(request)

    return _error(request.id, -32601, f"Method not found: {request.method}")


def call_tool_by_name(tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    tool = get_tool(tool_name)
    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    safe_arguments = dict(arguments or {})
    tenant_id = safe_arguments.pop("tenant_id", DEFAULT_TENANT_ID)
    response = run_agent_task(
        tenant_id=tenant_id,
        task_type=tool.task_type,
        payload=safe_arguments,
    )
    content = McpToolResultContent(text=_stringify_result(response.tool_result.result))
    return {"content": [content.model_dump()]}


def _handle_tools_call(request: JsonRpcRequest) -> JsonRpcResponse:
    try:
        params = McpToolCallParams(**(request.params or {}))
        result = call_tool_by_name(params.name, params.arguments)
        return _success(request.id, result)
    except ValidationError as error:
        return _error(request.id, -32602, "Invalid tools/call params.", error.errors())
    except ValueError as error:
        return _error(request.id, -32602, str(error))


def _initialize_result() -> dict[str, Any]:
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "serverInfo": {
            "name": "aws-saas-delivery-copilot",
            "version": "0.1.0",
        },
        "capabilities": {
            "tools": {
                "listChanged": False,
            }
        },
    }


def _tool_dump(tool) -> dict[str, Any]:
    return tool.model_dump(by_alias=True)


def _stringify_result(result: dict | list | str) -> str:
    if isinstance(result, str):
        return result
    return json.dumps(result, indent=2, ensure_ascii=False)


def _success(request_id, result: Any) -> JsonRpcResponse:
    return JsonRpcResponse(id=request_id, result=result)


def _error(request_id, code: int, message: str, data: Any | None = None) -> JsonRpcResponse:
    return JsonRpcResponse(
        id=request_id,
        error={
            "code": code,
            "message": message,
            "data": data,
        },
    )
