# Engineering Trade-Offs

## Mock vs Bedrock

Mock mode is default because it makes the project deterministic, free to run and easy to test without credentials. Bedrock is implemented as an optional provider to prove the integration path. In production, Bedrock would be used with model access, quotas, logging and cost controls.

## Deterministic Tools vs Autonomous Agent

The current agent routes known `task_type` values to explicit tools. This avoids unpredictable behavior and makes tests straightforward. A more autonomous agent could plan multi-step workflows, but would require stronger guardrails, tracing, evaluation and retry logic.

## MCP-Style vs Official MCP Server

The project implements JSON-RPC style discovery and tool calls to demonstrate MCP concepts without taking on SDK complexity. A production version should use the official MCP SDK, support resources, authentication and richer protocol compatibility.

## Local Vector Store vs Managed Vector Database

The local JSON vector store is simple and visible for demos. It is not built for scale, concurrency or high recall. Production options include OpenSearch Serverless, Aurora PostgreSQL with pgvector or another managed vector database.

## Extractive/Grounded Answers vs Free Generation

Grounded answers reduce hallucination because responses are tied to retrieved chunks and source files. Free generation can sound more polished, but it increases risk unless prompts, evaluation and citation checks are in place.

## No Deploy Yet vs AWS-Ready Architecture

No deployment keeps the portfolio project fast to inspect and run locally. The architecture is still AWS-ready: documents can move to S3, models to Bedrock, metadata to DynamoDB/RDS, vector search to OpenSearch/pgvector and runtime to ECS or Lambda.

## Python/FastAPI Choice

FastAPI is a pragmatic choice for AI service APIs: it is lightweight, typed, test-friendly and familiar in ML/GenAI stacks. The trade-off is that production hardening still needs authentication, observability, rate limits and deployment automation.

## Simplified Tenant Isolation

Tenant isolation is currently path-based and explicit through `tenant_id`. This is enough for a local demo. Production isolation would require auth claims, authorization checks, tenant-scoped storage, audit logs and encryption boundaries.
