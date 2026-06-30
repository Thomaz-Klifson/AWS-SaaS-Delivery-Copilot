# AWS SaaS Delivery Copilot

Portfolio project for an AI Engineer Jr/Pleno interview context, inspired by AWS consulting engagements for SaaS clients.

The goal is to simulate a GenAI delivery copilot for a consulting team: a multi-tenant platform that combines RAG with sources, AI agents with tools, feedback analysis, security questionnaire support, status reports, cost estimates, evaluation and an AWS-ready architecture.

## Current Stage: Stage 2 Local Multi-Tenant RAG

This repository is currently in Stage 2. The implementation includes a local RAG foundation, but it intentionally does not include LangGraph agents, MCP, Bedrock calls or AWS deployment yet.

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

## Why Mock/Extractive Mode

The current answer generation does not call an LLM. It builds a draft answer from the most relevant retrieved chunks. This keeps the project easy to run locally and makes retrieval quality visible before adding a generative model.

In a later AWS-ready stage, this layer can be replaced with:

- Amazon Bedrock embeddings instead of local hashing embeddings.
- S3 as the source document store instead of local tenant folders.
- OpenSearch Serverless, Aurora pgvector or another managed vector store instead of local JSON.
- Bedrock chat/inference models for grounded final answers.

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

## Tests

```bash
python -m pytest
```

## Roadmap

1. Stage 1: foundation with FastAPI, schemas, local tenant data loading and tests.
2. Stage 2: local multi-tenant RAG with chunking, embeddings, vector store and extractive answers.
3. Stage 3: stronger retrieval evaluation, prompt templates and Bedrock-ready model interfaces.
4. Stage 4: feedback analysis pipeline and customer-facing insights.
5. Stage 5: security questionnaire assistant.
6. Stage 6: agent orchestration for reports, estimates and delivery workflows.
7. Stage 7: evaluation, observability and cost tracking.
8. Stage 8: AWS architecture and deployment blueprint.
