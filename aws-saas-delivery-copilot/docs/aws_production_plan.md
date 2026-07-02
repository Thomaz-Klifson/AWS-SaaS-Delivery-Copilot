# AWS Production Plan

## Documents And Tenant Data

Store tenant documents in S3 with tenant-scoped prefixes, for example `s3://bucket/tenants/{tenant_id}/documents/`. Use bucket policies, encryption and IAM conditions to enforce access boundaries.

## LLM Runtime

Use Amazon Bedrock for chat and embedding models. Keep model IDs configurable by environment and tenant use case. Add request logging, retry/backoff and quota monitoring.

## API Runtime

Deploy the FastAPI app on ECS Fargate for long-running service control, or Lambda for lighter API workloads. Use Application Load Balancer or API Gateway depending on auth and traffic requirements.

## Metadata

Use DynamoDB for simple tenant/document metadata and job state, or RDS/PostgreSQL when relational queries and reporting matter more.

## Vector Search

Use OpenSearch Serverless for managed vector retrieval or Aurora PostgreSQL with pgvector when the team wants SQL-native metadata joins and operational familiarity.

## Batch Jobs

Use SQS for ingestion and feedback-analysis jobs. Workers can run on Lambda, ECS tasks or EventBridge-triggered jobs depending on throughput.

## Observability

Use CloudWatch for application logs, metrics and alarms. Track latency, retrieval quality signals, token usage, provider errors and per-tenant request volume.

## Secrets

Use Secrets Manager or SSM Parameter Store for API keys, provider configuration and sensitive runtime settings. Never commit secrets to the repository.

## IAM

Apply least privilege for S3, Bedrock, OpenSearch, DynamoDB/RDS, SQS and CloudWatch. Separate roles for API runtime, ingestion workers and admin operations.

## Infrastructure As Code

Use Terraform or Pulumi to define networking, compute, IAM, storage, queues, monitoring and deployment configuration. Keep environment-specific values outside code.

## Edge And API Entry

Use API Gateway and/or CloudFront when public access, custom domains, throttling, WAF or edge caching are required.

## Suggested Migration Order

1. Add authentication and tenant authorization.
2. Move documents to S3.
3. Replace local vector store with OpenSearch or pgvector.
4. Enable Bedrock provider in a controlled environment.
5. Add ingestion workers with SQS.
6. Add CloudWatch metrics, dashboards and alarms.
7. Codify infrastructure with Terraform/Pulumi.
