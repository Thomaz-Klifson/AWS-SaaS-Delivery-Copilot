# 3-Minute Demo Script

## 0:00-0:30 Problem Context

Open with the consulting scenario: a SaaS customer needs help answering security questions, analyzing customer feedback, preparing delivery updates and making architecture decisions with AWS/GenAI.

Position the project: AWS SaaS Delivery Copilot is a portfolio-grade GenAI platform that simulates a real AWS consulting delivery for a SaaS customer.

## 0:30-1:00 Architecture

Show the README architecture summary or `docs/architecture_diagram.md`.

Explain the main flow:

- FastAPI exposes the application API.
- Tenant Loader reads local tenant data.
- RAG Service retrieves source-backed context.
- Agent Orchestrator routes deterministic consulting tasks.
- MCP-style Interface exposes tool discovery and standardized tool calls.
- LLM Provider supports mock by default and Bedrock manually.

## 1:00-1:45 RAG With Sources

Run or describe:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/tenants/tenant_acme/rag/ask" `
  -ContentType "application/json" `
  -Body '{"question":"Is customer data encrypted at rest and in transit?","top_k":3}'
```

Point out:

- The answer is grounded in retrieved chunks.
- The response returns `sources`.
- `security_policy.md` should appear for encryption/security questions.
- This reduces hallucination by keeping evidence visible.

## 1:45-2:20 Agent Tools

Run or describe:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/tenants/tenant_acme/agent/run" `
  -ContentType "application/json" `
  -Body '{"task_type":"security_questionnaire","payload":{}}'
```

Mention the available tools:

- knowledge search;
- security questionnaire;
- feedback analysis;
- status report;
- cost estimate;
- Well-Architected assessment.

Explain that the agent is deterministic on purpose so the project is reliable, testable and easy to review.

## 2:20-2:45 MCP-Style Interface

Run or describe:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/mcp/rpc" `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

Explain:

- This is MCP-style, not a full official MCP server.
- It demonstrates tool contracts, JSON schemas and standard execution.
- This is how agents can discover and call tools safely.

## 2:45-3:00 Bedrock-Ready And Next Steps

Close with:

- Mock mode is default to avoid cost and external dependency.
- Bedrock Converse provider is implemented for manual testing.
- Production path: S3, Bedrock, OpenSearch/pgvector, ECS/Lambda, CloudWatch, IAM, Secrets Manager and IaC.
- Next engineering steps: evaluation, observability, tenant auth and official MCP SDK.
