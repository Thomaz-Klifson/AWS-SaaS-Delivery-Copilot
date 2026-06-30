
Architecture
Goal

Build a portfolio-grade Agentic RAG platform that looks like a realistic AWS consulting delivery for a SaaS client.

High-level flow

User / Client System
↓
FastAPI Backend
↓
Agent Orchestrator
↓
Tools:

Knowledge Base Search
Security Questionnaire Drafting
Feedback Summarization
Status Report Generation
Cost Estimation
Well-Architected Assessment
↓
LLM Provider:
Mock mode locally
Amazon Bedrock-ready
↓
Response with sources, metadata, latency and cost estimate
AWS target architecture
Amazon Bedrock for LLMs
Amazon S3 for documents and feedback files
PostgreSQL + pgvector or Chroma locally for vector search
Amazon SQS for async batch jobs
DynamoDB for tenant/job metadata
CloudWatch for logs
Secrets Manager for secrets
Terraform/Pulumi for IaC
