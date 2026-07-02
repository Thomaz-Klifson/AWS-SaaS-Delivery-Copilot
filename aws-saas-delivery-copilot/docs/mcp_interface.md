# MCP-Style Tool Interface

## What MCP Means Here

Model Context Protocol, or MCP, is a standard way for AI applications to discover and call external tools and resources through explicit contracts. In simple terms, it lets an agent ask: what tools exist, what inputs do they accept, and how do I call them?

This project implements an MCP-style interface to demonstrate tool discovery, JSON schemas and standardized tool execution for AWS/SaaS consulting workflows.

## MCP-Style, Not A Full Official MCP Server

This is not a certified or complete MCP server implementation and does not use the official MCP SDK. It is a didactic compatibility layer over the existing FastAPI and deterministic agent toolkit.

The goal is to show:

- tool contracts;
- JSON-RPC style calls;
- tool discovery;
- structured execution results;
- a path toward a real MCP server later.

## Supported Methods

### initialize

Request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "serverInfo": {
      "name": "aws-saas-delivery-copilot",
      "version": "0.1.0"
    },
    "capabilities": {
      "tools": {
        "listChanged": false
      }
    }
  },
  "error": null
}
```

### tools/list

Returns the available MCP-style tool catalog with names, titles, descriptions and JSON input schemas.

Request:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### tools/call

Calls a registered tool. The handler extracts `tenant_id` from arguments and defaults to `tenant_acme` when omitted.

Request:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "knowledge_search",
    "arguments": {
      "tenant_id": "tenant_acme",
      "question": "Does the platform expose APIs for integrations?",
      "top_k": 3
    }
  }
}
```

Response content is returned as a text array. Objects and lists are serialized as indented JSON inside the `text` field:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"answer\": \"...\"\n}"
      }
    ]
  },
  "error": null
}
```

## Exposed Tools

- `knowledge_search`
- `security_questionnaire`
- `feedback_analysis`
- `status_report`
- `cost_estimate`
- `well_architected_assessment`

Each tool maps to a deterministic `task_type` in the existing agent orchestrator.

## FastAPI Endpoints

- `POST /mcp/rpc`: main MCP-style JSON-RPC endpoint.
- `GET /mcp/tools`: demo endpoint for listing the tool catalog.
- `POST /mcp/tools/{tool_name}/call`: demo endpoint for calling one tool with simple JSON arguments.

## Why This Matters For AI Agents

Agents need clear tool contracts. A tool registry with JSON schemas makes it easier for a model or orchestrator to choose tools, validate inputs and inspect outputs. This project uses the pattern without adding a heavy protocol dependency yet.

## AWS/SaaS Consulting Relevance

The tools map to realistic consulting workflows:

- source-backed knowledge search over tenant documentation;
- security questionnaire acceleration;
- customer feedback analysis;
- delivery status reporting;
- LLM cost estimation;
- AWS Well-Architected style assessment.

This is the kind of interface that could later connect a Bedrock agent, internal copilot or delivery automation layer to controlled business tools.

## Next Steps

- Replace this educational layer with the official MCP SDK.
- Add `resources/list` and `resources/read`.
- Add tenant authentication and authorization.
- Add structured logs and tracing for each tool call.
- Add policy controls for which tenants and users can call each tool.
- Add request IDs and audit events for consulting/client-facing governance.
