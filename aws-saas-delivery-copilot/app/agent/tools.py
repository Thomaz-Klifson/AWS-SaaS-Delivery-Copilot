from collections import Counter
from typing import Any

from app.core.tenant_loader import read_feedback_items, read_security_questions
from app.models.schemas import (
    CostEstimateResponse,
    FeedbackAnalysisResponse,
    RagAskResponse,
    SecurityQuestionnaireItem,
    WellArchitectedFinding,
)
from app.rag.service import ask_tenant_question


def search_knowledge_base_tool(tenant_id: str, question: str, top_k: int = 3) -> dict[str, Any]:
    """Search the tenant knowledge base using the local RAG service."""
    response = ask_tenant_question(tenant_id=tenant_id, question=question, top_k=top_k)
    return {
        "answer": response.answer,
        "sources": [source.model_dump() for source in response.sources],
        "retrieved_chunks": [chunk.model_dump() for chunk in response.retrieved_chunks],
    }


def security_questionnaire_tool(tenant_id: str) -> list[dict[str, Any]]:
    """Draft answers for every tenant security question using local RAG."""
    items = []
    for security_question in read_security_questions(tenant_id):
        rag_response = ask_tenant_question(
            tenant_id=tenant_id,
            question=security_question.question,
            top_k=3,
        )
        items.append(
            SecurityQuestionnaireItem(
                question=security_question.question,
                draft_answer=rag_response.answer,
                sources=rag_response.sources,
                confidence_hint=_confidence_hint(rag_response),
            ).model_dump()
        )
    return items


def feedback_analysis_tool(tenant_id: str) -> dict[str, Any]:
    """Analyze tenant feedback with deterministic keyword rules."""
    feedback_items = read_feedback_items(tenant_id)
    feedback_texts = [item.feedback for item in feedback_items]
    combined = " ".join(feedback_texts).lower()

    theme_keywords = {
        "onboarding": ["onboarding"],
        "cost visibility": ["cost", "visibility"],
        "documentation": ["documentation", "docs"],
        "support": ["support", "incident"],
        "ai productivity": ["ai", "summary", "saves time"],
        "integrations": ["api", "integration", "integrations"],
    }
    theme_counts = Counter()
    for theme, keywords in theme_keywords.items():
        theme_counts[theme] = sum(combined.count(keyword) for keyword in keywords)

    top_themes = [theme for theme, count in theme_counts.most_common() if count > 0][:5]
    positive_signals = _filter_feedback(feedback_texts, ["powerful", "fast", "saves time", "useful"])
    pain_points = _filter_feedback(feedback_texts, ["too long", "need", "should be clearer", "better"])
    opportunities = _build_opportunities(top_themes, pain_points)

    executive_summary = (
        f"Analyzed {len(feedback_items)} feedback items. "
        f"Main themes are {', '.join(top_themes) if top_themes else 'not clear yet'}. "
        f"The strongest opportunities are {', '.join(opportunities[:2]) if opportunities else 'to collect more feedback'}."
    )

    return FeedbackAnalysisResponse(
        total_feedbacks=len(feedback_items),
        top_themes=top_themes,
        positive_signals=positive_signals,
        pain_points=pain_points,
        opportunities=opportunities,
        executive_summary=executive_summary,
    ).model_dump()


def status_report_tool(
    project_name: str,
    progress: list[str],
    blockers: list[str],
    next_steps: list[str],
    risks: list[str],
) -> str:
    """Build a Markdown status report for a consulting delivery workflow."""
    status = "Blocked" if blockers else "On Track"
    summary = (
        f"{project_name} is {status.lower()}. "
        f"{len(progress)} progress items completed, {len(blockers)} blockers identified, "
        f"and {len(next_steps)} next steps planned."
    )

    return "\n".join(
        [
            f"# Status Report: {project_name}",
            "",
            f"## Project\n{project_name}",
            "",
            f"## Status\n{status}",
            "",
            "## Progress",
            _markdown_list(progress),
            "",
            "## Blockers",
            _markdown_list(blockers),
            "",
            "## Next Steps",
            _markdown_list(next_steps),
            "",
            "## Risks",
            _markdown_list(risks),
            "",
            f"## Executive Summary\n{summary}",
        ]
    )


def llm_cost_estimator_tool(
    input_tokens: int,
    output_tokens: int,
    input_price_per_1k: float = 0.00025,
    output_price_per_1k: float = 0.00125,
) -> dict[str, Any]:
    """Estimate LLM usage cost from configurable example token prices."""
    input_cost = (input_tokens / 1000) * input_price_per_1k
    output_cost = (output_tokens / 1000) * output_price_per_1k

    return CostEstimateResponse(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_price_per_1k=input_price_per_1k,
        output_price_per_1k=output_price_per_1k,
        input_cost=round(input_cost, 8),
        output_cost=round(output_cost, 8),
        total_cost=round(input_cost + output_cost, 8),
        note="Example configurable prices for local estimation only; these are not official provider prices.",
    ).model_dump()


def well_architected_assessment_tool(tenant_id: str) -> list[dict[str, Any]]:
    """Create a simplified six-pillar AWS Well-Architected style assessment."""
    pillar_questions = {
        "Operational Excellence": "What operational support or incident response practices are documented?",
        "Security": "Is customer data encrypted at rest and in transit?",
        "Reliability": "What incident response or resilience practices are documented?",
        "Performance Efficiency": "Does the platform use managed services or efficient cloud services?",
        "Cost Optimization": "Is cost visibility or cost optimization mentioned?",
        "Sustainability": "Does the platform use managed services or efficient resource usage?",
    }

    findings = []
    for pillar, question in pillar_questions.items():
        rag_response = ask_tenant_question(tenant_id=tenant_id, question=question, top_k=2)
        best_source = rag_response.sources[0] if rag_response.sources else None
        risk_level = _risk_level(best_source.score if best_source else 0)
        source_name = best_source.source_file if best_source else "no source"
        findings.append(
            WellArchitectedFinding(
                pillar=pillar,
                finding=f"Local evidence retrieved from {source_name}.",
                risk_level=risk_level,
                recommendation=_pillar_recommendation(pillar, risk_level),
            ).model_dump()
        )

    return findings


def _confidence_hint(response: RagAskResponse) -> str:
    if not response.sources:
        return "low"
    score = response.sources[0].score
    if score >= 0.35:
        return "high"
    if score >= 0.15:
        return "medium"
    return "low"


def _filter_feedback(feedback_texts: list[str], keywords: list[str]) -> list[str]:
    matches = []
    for text in feedback_texts:
        normalized = text.lower()
        if any(keyword in normalized for keyword in keywords):
            matches.append(text)
    return matches


def _build_opportunities(top_themes: list[str], pain_points: list[str]) -> list[str]:
    opportunities = []
    if "onboarding" in top_themes:
        opportunities.append("Streamline onboarding and reduce time-to-value.")
    if "cost visibility" in top_themes:
        opportunities.append("Improve dashboard cost visibility and reporting.")
    if "documentation" in top_themes:
        opportunities.append("Expand API and integration documentation.")
    if pain_points and not opportunities:
        opportunities.append("Prioritize recurring customer pain points in the delivery backlog.")
    return opportunities


def _markdown_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def _risk_level(score: float) -> str:
    if score >= 0.35:
        return "low"
    if score >= 0.15:
        return "medium"
    return "high"


def _pillar_recommendation(pillar: str, risk_level: str) -> str:
    recommendations = {
        "Operational Excellence": "Document operational runbooks, ownership and post-incident review routines.",
        "Security": "Keep encryption, access control and evidence sources explicit for customer security reviews.",
        "Reliability": "Define resilience targets, incident response paths and recovery validation.",
        "Performance Efficiency": "Review managed service choices and performance assumptions as usage grows.",
        "Cost Optimization": "Add cost dashboards, budgets and tenant-level cost attribution.",
        "Sustainability": "Prefer managed services and right-sized resources, then track utilization signals.",
    }
    prefix = "Validate and improve:" if risk_level != "low" else "Maintain evidence:"
    return f"{prefix} {recommendations[pillar]}"
