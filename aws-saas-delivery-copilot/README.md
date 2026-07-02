# AWS SaaS Delivery Copilot

Portfolio project for an AI Engineer Jr/Pleno interview context, inspired by AWS consulting engagements for SaaS clients.

The goal is to simulate a GenAI delivery copilot for a consulting team: a multi-tenant platform that combines RAG with sources, AI agents with tools, feedback analysis, security questionnaire support, status reports, cost estimates, evaluation and an AWS-ready architecture.

## Current Stage: Stage 5 MCP-Style Tool Interface

This repository is currently in Stage 5. The implementation includes a local RAG foundation, a deterministic agent toolkit, an LLM provider layer with mock mode by default plus optional Amazon Bedrock Converse support, and an MCP-style tool interface. It intentionally does not include LangGraph agents or AWS deployment yet.

Stage 1 delivered:

- A FastAPI backend with health and tenant summary endpoints.
- Basic Pydantic schemas for tenants, documents, feedback, security questions and health checks.
- Local file readers for tenant documents, feedback CSV and security questionnaire JSON.
- A sample tenant, `tenant_acme`, under `data/tenants`.
- Basic pytest coverage for API endpoints and sample data loading.

Stage 2 adds:

- Tenant document chunking with overlap and metadata.
- Local hashing-based embeddings with no API key required.
- Local JSON vector store persisted under `.local/vector_store`.
- RAG ingestion and question-answering service.
- FastAPI endpoints for ingestion and asking questions.
- Mock/extractive answer generation with retrieved sources.

Stage 3 adds:

- A simple agent orchestrator for deterministic task routing.
- Agent tools for knowledge search, security questionnaire drafting, feedback analysis, status reports, cost estimates and Well-Architected style assessment.
- A FastAPI endpoint for running agent tasks.
- Documentation for how each tool maps to AWS/SaaS consulting workflows.

Stage 4 adds:

- `app/llm` provider abstraction.
- `MockLLMProvider` for deterministic local execution and automated tests.
- `BedrockConverseProvider` using `boto3` and the Bedrock Runtime Converse API.
- `/llm/test` endpoint for manual provider checks.
- RAG answer generation through the configured provider, with extractive fallback.
- Manual Bedrock smoke script under `scripts/test_bedrock.py`.

Stage 5 adds:

- An MCP-style JSON-RPC endpoint for tool discovery and execution.
- Tool definitions with JSON input schemas.
- Demo endpoints for listing and calling tools.
- Documentation explaining that this is MCP-compatible in style, not a full official MCP SDK server.

## Why Local Deterministic Mode

The default `LLM_PROVIDER=mock` does not call external services. It produces deterministic local responses from the retrieved context and simulates token usage. The agent also does not use autonomous planning yet; it routes known task types to explicit tools. The MCP-style layer exposes those tools with JSON schemas and JSON-RPC shaped calls, but it is not a full official MCP server. This keeps the project easy to run locally, testable and demo-friendly before adding production Bedrock workflows, official MCP SDK support or LangGraph.

In a later AWS-ready stage, this layer can be replaced with:

- Amazon Bedrock embeddings instead of local hashing embeddings.
- S3 as the source document store instead of local tenant folders.
- OpenSearch Serverless, Aurora pgvector or another managed vector store instead of local JSON.
- Bedrock chat/inference models for grounded final answers. Stage 4 already includes an optional Bedrock Converse provider for manual testing.
- LangGraph for multi-step planning and stateful workflows.
- Official MCP tools/resources for external systems such as ticketing, CRM, documents or cloud APIs.

## Planned Architecture

The planned production-style architecture is:

1. FastAPI backend as the application API.
2. Tenant-aware ingestion for documents, feedback and questionnaires.
3. RAG pipeline with source-grounded answers.
4. Agent orchestration for delivery workflows and report generation.
5. Feedback intelligence batch pipeline for summaries and insights.
6. Security questionnaire copilot using approved tenant knowledge.
7. Evaluation layer for answer quality and grounding.
8. Observability for traces, latency, cost and quality metrics.
9. AWS-ready deployment using services such as Amazon Bedrock, S3, SQS, DynamoDB/RDS and IaC.

## Project Structure

```text
app/
  core/              # settings and tenant data loading
  models/            # Pydantic schemas
  agent/             # deterministic tools and task orchestrator
  mcp_server/        # MCP-style JSON-RPC tool interface
  rag/               # chunking, embeddings, vector store and RAG service
  main.py            # FastAPI application
data/
  tenants/
    tenant_acme/     # sample tenant data
docs/                # architecture notes and delivery examples
infra/               # future IaC placeholders
tests/               # pytest tests
```

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Basic service information. |
| GET | `/health` | Health check for local/runtime validation. |
| GET | `/tenants/{tenant_id}/summary` | Counts local tenant documents, feedback items and security questions. |
| POST | `/tenants/{tenant_id}/rag/ingest` | Chunks and indexes tenant documents into the local vector store. |
| POST | `/tenants/{tenant_id}/rag/ask` | Retrieves relevant chunks and returns an extractive answer with sources. |
| POST | `/tenants/{tenant_id}/agent/run` | Runs one deterministic agent task for the tenant. |
| POST | `/llm/test` | Tests the configured LLM provider. |
| POST | `/mcp/rpc` | MCP-style JSON-RPC endpoint for initialize, tools/list and tools/call. |
| GET | `/mcp/tools` | Demo endpoint for listing the MCP-style tool catalog. |
| POST | `/mcp/tools/{tool_name}/call` | Demo endpoint for calling one MCP-style tool. |

## LLM Provider Configuration

Default local mode:

```env
LLM_PROVIDER=mock
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=
S3_BUCKET_NAME=
```

Optional Bedrock mode:

```env
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

Mock mode is the default to avoid external cost, credentials and network dependency. Bedrock is optional and should be enabled only for manual testing or later AWS-ready runs. No AWS credentials are stored in this project. Use standard AWS configuration methods such as `AWS_PROFILE`, SSO, environment credentials or an attached role.

List available foundation models with AWS CLI:

```bash
aws bedrock list-foundation-models --region us-east-1
```

For inference, also confirm model access in the Amazon Bedrock console for the selected region and model.

Test the current provider:

```bash
curl -X POST http://127.0.0.1:8000/llm/test ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"Say hello in one sentence.\"}"
```

Automated tests force `LLM_PROVIDER=mock` to avoid AWS cost, credentials and network dependencies.

Manual Bedrock smoke test:

```bash
set LLM_PROVIDER=bedrock
set AWS_REGION=us-east-1
set BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
python scripts\test_bedrock.py
```

The manual Bedrock test can still fail even when the code is correct. Common causes are missing model access, account quota, daily token limits or model-level throttling. `ThrottlingException` specifically means the selected account/model/region is currently limited or throttled; it is not necessarily a bug in the provider implementation.

Common Bedrock issues:

- Missing credentials: run `aws sts get-caller-identity` and confirm your profile/session.
- Model access denied: enable the model in the Bedrock console for the same region.
- `ThrottlingException`: wait for daily quota reset, reduce prompt/max tokens, try a smaller/different model or request a quota increase.
- Wrong region: confirm `AWS_REGION` supports the selected model.
- Invalid model id: compare `BEDROCK_MODEL_ID` with `aws bedrock list-foundation-models`.

## RAG Usage

Run ingestion for the sample tenant:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/rag/ingest
```

Example response:

```json
{
  "tenant_id": "tenant_acme",
  "document_count": 2,
  "chunk_count": 2,
  "indexed_files": ["product_faq.md", "security_policy.md"]
}
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/rag/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Is customer data encrypted at rest and in transit?\",\"top_k\":3}"
```

Example response shape:

```json
{
  "answer": "Extractive draft answer based only on retrieved local sources...",
  "tenant_id": "tenant_acme",
  "question": "Is customer data encrypted at rest and in transit?",
  "sources": [
    {
      "source_file": "security_policy.md",
      "chunk_id": "security_policy.md:0",
      "score": 0.4315
    }
  ],
  "retrieved_chunks": [
    {
      "source_file": "security_policy.md",
      "chunk_id": "security_policy.md:0",
      "text": "ACME SaaS Security Policy...",
      "score": 0.4315
    }
  ],
  "top_k": 3
}
```

Another expected retrieval:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/rag/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Does the platform expose APIs for integrations?\",\"top_k\":3}"
```

This should return `product_faq.md` as the top source.

## Agent Toolkit Usage

Supported `task_type` values:

- `knowledge_search`
- `security_questionnaire`
- `feedback_analysis`
- `status_report`
- `cost_estimate`
- `well_architected_assessment`

Security questionnaire:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/agent/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task_type\":\"security_questionnaire\",\"payload\":{}}"
```

Knowledge search:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/agent/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task_type\":\"knowledge_search\",\"payload\":{\"question\":\"Does the platform expose APIs for integrations?\",\"top_k\":3}}"
```

Status report:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/agent/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task_type\":\"status_report\",\"payload\":{\"project_name\":\"ACME SaaS Delivery Copilot\",\"progress\":[\"RAG ingestion implemented\",\"Tenant summary endpoint implemented\"],\"blockers\":[\"Bedrock integration pending\"],\"next_steps\":[\"Add Bedrock provider\",\"Add MCP server\"],\"risks\":[\"Scope creep before interview\"]}}"
```

Cost estimate:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/agent/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task_type\":\"cost_estimate\",\"payload\":{\"input_tokens\":1200,\"output_tokens\":300}}"
```

Feedback analysis:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/agent/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task_type\":\"feedback_analysis\",\"payload\":{}}"
```

Well-Architected assessment:

```bash
curl -X POST http://127.0.0.1:8000/tenants/tenant_acme/agent/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task_type\":\"well_architected_assessment\",\"payload\":{}}"
```

## MCP-Style Tool Interface

The project includes an MCP-style interface for tool discovery and execution. It is intentionally lightweight and didactic: it follows JSON-RPC and MCP tool concepts, but it is not a complete certified MCP server and does not use the official MCP SDK yet.

Main endpoint:

```text
POST /mcp/rpc
```

Supported methods:

- `initialize`
- `tools/list`
- `tools/call`

Demo endpoints:

```text
GET /mcp/tools
POST /mcp/tools/{tool_name}/call
```

PowerShell examples:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/mcp/rpc" `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/mcp/rpc" `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/mcp/rpc" `
  -ContentType "application/json" `
  -Body '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"knowledge_search","arguments":{"tenant_id":"tenant_acme","question":"Does the platform expose APIs for integrations?","top_k":3}}}'
```

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/mcp/tools/cost_estimate/call" `
  -ContentType "application/json" `
  -Body '{"input_tokens":1000,"output_tokens":500}'
```

This is relevant for AI engineering roles because production agents need controlled tool contracts, input schemas, structured outputs, tenant boundaries and predictable execution paths. It demonstrates the architecture needed before plugging in a full MCP server, LangGraph workflow or Bedrock agent.

More detail: see `docs/mcp_interface.md`.

## How This Maps To AWS Consulting Workflows

- Knowledge search maps to consultant Q&A over client-approved project documentation.
- Security questionnaire drafting maps to vendor/security review acceleration with source-backed answers.
- Feedback analysis maps to customer discovery, product insights and executive readouts.
- Status reports map to weekly client delivery communication.
- Cost estimates map to early GenAI usage planning and stakeholder expectation setting.
- Well-Architected assessment maps to architecture review conversations across the six AWS pillars.

## Tests

```bash
python -m pytest
```

## Roadmap

1. Stage 1: foundation with FastAPI, schemas, local tenant data loading and tests.
2. Stage 2: local multi-tenant RAG with chunking, embeddings, vector store and extractive answers.
3. Stage 3: deterministic agent toolkit for consulting workflows.
4. Stage 4: LLM provider layer with mock mode and optional Bedrock Converse.
5. Stage 5: MCP-style tool interface with JSON-RPC, discovery and tool execution.
6. Stage 6: stronger retrieval evaluation and prompt templates.
7. Stage 7: feedback analysis pipeline and security questionnaire improvements.
8. Stage 8: evaluation, observability, AWS architecture and deployment blueprint.
