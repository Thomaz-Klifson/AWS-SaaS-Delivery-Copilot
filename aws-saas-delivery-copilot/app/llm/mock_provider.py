import re

from app.llm.provider import LLMResponse


class MockLLMProvider:
    provider_name = "mock"
    model_id = "mock-deterministic-local"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> LLMResponse:
        """Return deterministic local text and approximate token usage."""
        input_tokens = _estimate_tokens(system_prompt) + _estimate_tokens(user_prompt)
        answer = _build_mock_answer(user_prompt)
        output_tokens = min(_estimate_tokens(answer), max_tokens)

        return LLMResponse(
            text=answer,
            provider=self.provider_name,
            model_id=self.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            raw_metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "mode": "deterministic_mock",
            },
        )


def _estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"\S+", text)))


def _build_mock_answer(user_prompt: str) -> str:
    question = _extract_section(user_prompt, "Question")
    context = _extract_section(user_prompt, "Context")
    sources = sorted(set(re.findall(r"Source: ([^\n]+)", context)))
    first_context_line = _first_context_line(context)

    if not context.strip():
        return "There is not enough information in the provided sources to answer."

    source_text = ", ".join(sources) if sources else "provided sources"
    if first_context_line:
        return (
            f"Based on {source_text}, the answer to '{question}' is: "
            f"{first_context_line}"
        )
    return f"Based on {source_text}, the provided context should be reviewed for this question."


def _extract_section(prompt: str, section_name: str) -> str:
    pattern = rf"{section_name}:\n(.*?)(?:\n\n[A-Z][A-Za-z ]+:\n|\Z)"
    match = re.search(pattern, prompt, flags=re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()


def _first_context_line(context: str) -> str:
    for line in context.splitlines():
        clean_line = line.strip()
        if clean_line and not clean_line.startswith(("Source:", "Chunk:", "Score:")):
            return clean_line
    return ""
