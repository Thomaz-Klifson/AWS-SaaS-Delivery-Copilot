from typing import Any

from pydantic import BaseModel, Field


JsonRpcId = str | int | None


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: JsonRpcId = None
    method: str
    params: dict[str, Any] | None = None


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: JsonRpcId = None
    result: Any | None = None
    error: JsonRpcError | None = None


class McpToolDefinition(BaseModel):
    name: str
    title: str
    description: str
    inputSchema: dict[str, Any] = Field(alias="inputSchema")
    task_type: str


class McpToolCallParams(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class McpToolResultContent(BaseModel):
    type: str = "text"
    text: str
