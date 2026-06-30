# Agent Tools

Stage 3 introduces a deterministic agent toolkit. The orchestrator does not plan autonomously and does not call external LLMs. It maps a known `task_type` to one local tool so the workflow is easy to test and explain.

## search_knowledge_base_tool

Objective: answer a tenant question using the local RAG service and return sources.

Input:

- `tenant_id`
- `question`
- `top_k`

Output:

- `answer`
- `sources`
- `retrieved_chunks`

AWS/SaaS consulting fit: supports consultant Q&A over approved client documentation.

Future evolution: replace local embeddings with Bedrock embeddings, store source documents in S3, use a managed vector store, and generate final grounded answers with Bedrock.

## security_questionnaire_tool

Objective: draft answers for every question in the tenant security questionnaire.

Input:

- `tenant_id`

Output:

- `question`
- `draft_answer`
- `sources`
- `confidence_hint`

AWS/SaaS consulting fit: accelerates security and vendor questionnaire responses while keeping source evidence visible.

Future evolution: use Bedrock for answer drafting, add human approval, connect MCP tools to ticketing/document systems, and use LangGraph for review state.

## feedback_analysis_tool

Objective: summarize customer feedback with deterministic keyword rules.

Input:

- `tenant_id`

Output:

- `total_feedbacks`
- `top_themes`
- `positive_signals`
- `pain_points`
- `opportunities`
- `executive_summary`

AWS/SaaS consulting fit: supports discovery, stakeholder readouts and prioritization conversations.

Future evolution: use Bedrock for richer clustering and summarization, store feedback in S3/RDS, and schedule batch processing through AWS-native pipelines.

## status_report_tool

Objective: create a Markdown project status report.

Input:

- `project_name`
- `progress`
- `blockers`
- `next_steps`
- `risks`

Output:

- Markdown report with Project, Status, Progress, Blockers, Next Steps, Risks and Executive Summary.

AWS/SaaS consulting fit: mirrors weekly delivery communication with client stakeholders.

Future evolution: use Bedrock for tone refinement, MCP for publishing to docs or email, and LangGraph for approval workflows.

## llm_cost_estimator_tool

Objective: estimate LLM token usage cost from configurable example prices.

Input:

- `input_tokens`
- `output_tokens`
- `input_price_per_1k`
- `output_price_per_1k`

Output:

- `input_cost`
- `output_cost`
- `total_cost`
- note explaining that prices are examples, not official provider prices.

AWS/SaaS consulting fit: helps communicate early GenAI usage assumptions and budget sensitivity.

Future evolution: load current model pricing from configuration, integrate AWS cost allocation tags, and compare Bedrock model options.

## well_architected_assessment_tool

Objective: produce a simplified six-pillar AWS Well-Architected style assessment.

Input:

- `tenant_id`

Output:

- `pillar`
- `finding`
- `risk_level`
- `recommendation`

AWS/SaaS consulting fit: starts architecture review conversations across Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization and Sustainability.

Future evolution: use Bedrock to generate more detailed findings, connect MCP tools to AWS account evidence, and use LangGraph for multi-step assessment workflows.
