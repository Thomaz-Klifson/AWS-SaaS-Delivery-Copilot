# AWS SaaS Delivery Copilot

Portfolio project for an AI Engineer Jr/Pleno interview context, inspired by AWS consulting engagements for SaaS clients.

The goal is to simulate a GenAI delivery copilot for a consulting team: a multi-tenant platform that combines RAG with sources, AI agents with tools, feedback analysis, security questionnaire support, status reports, cost estimates, evaluation and an AWS-ready architecture.

## Current Stage: Stage 3 Deterministic Agent Toolkit

This repository is currently in Stage 3. The implementation includes a local RAG foundation and a deterministic agent toolkit for AWS/SaaS consulting workflows. It intentionally does not include LangGraph agents, MCP, Bedrock calls or AWS deployment yet.

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

## Why Local Deterministic Mode

The current RAG answer generation does not call an LLM. It builds a draft answer from the most relevant retrieved chunks. The agent also does not use autonomous planning yet; it routes known task types to explicit tools. This keeps the project easy to run locally, testable and demo-friendly before adding Bedrock, MCP or LangGraph.

In a later AWS-ready stage, this layer can be replaced with:

- Amazon Bedrock embeddings instead of local hashing embeddings.
- S3 as the source document store instead of local tenant folders.
- OpenSearch Serverless, Aurora pgvector or another managed vector store instead of local JSON.
- Bedrock chat/inference models for grounded final answers.
- LangGraph for multi-step planning and stateful workflows.
- MCP tools for external systems such as ticketing, CRM, documents or cloud APIs.

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
4. Stage 4: stronger retrieval evaluation, prompt templates and Bedrock-ready model interfaces.
5. Stage 5: feedback analysis pipeline and customer-facing insights.
6. Stage 6: security questionnaire assistant improvements.
7. Stage 7: evaluation, observability and cost tracking.
8. Stage 8: AWS architecture and deployment blueprint.
