# Interview Q&A

## What is RAG?

Retrieval-Augmented Generation retrieves relevant source context before generating an answer. It helps the system answer from approved knowledge instead of relying only on model memory.

## How does this project reduce hallucination?

It retrieves tenant documents, returns sources and instructs the provider to answer only from context. The mock provider and extractive fallback keep behavior deterministic for local testing.

## How does the MCP-style interface work?

It exposes JSON-RPC methods for `initialize`, `tools/list` and `tools/call`. Tools have names, descriptions and JSON input schemas, then calls are routed to the existing agent orchestrator.

## Why use mock mode?

Mock mode avoids cost, quota, credentials and network dependency. It makes tests reliable while preserving the same provider interface used by Bedrock.

## How would you plug in Bedrock?

Set `LLM_PROVIDER=bedrock`, configure `AWS_REGION`, set `BEDROCK_MODEL_ID`, ensure AWS credentials and model access, then use the existing Bedrock Converse provider.

## How would you take this to production on AWS?

Move documents to S3, metadata to DynamoDB/RDS, vector search to OpenSearch or pgvector, runtime to ECS Fargate or Lambda, secrets to Secrets Manager, logs to CloudWatch and infrastructure to Terraform/Pulumi.

## How would you monitor cost?

Track token usage per request, tenant and model. Add budgets, dashboards, alerts and cost allocation tags. Use the cost estimator as an early local approximation.

## How would you protect tenant data?

Use authenticated tenant claims, authorization checks, tenant-scoped storage paths, encryption, least-privilege IAM, audit logs and tests that verify cross-tenant access is blocked.

## What would change with LangGraph?

LangGraph would help model multi-step workflows with state, retries, branching and human review. I would add it after tool contracts, tracing and evaluation are stable.

## What would change with the official MCP SDK?

The MCP-style layer would become a protocol-compliant server with official transports, resources and richer client compatibility. The existing registry and tool schemas are a foundation for that migration.

## How does this relate to Well-Architected?

The project includes a simplified six-pillar assessment tool and a production plan that maps to operational excellence, security, reliability, performance efficiency, cost optimization and sustainability.

## What are the current limitations?

The vector store is local, auth is not implemented, tenant isolation is simplified, the agent is deterministic, MCP is style-compatible only and Bedrock is optional/manual due to quota and credential dependencies.
