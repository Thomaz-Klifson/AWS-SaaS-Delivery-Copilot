from typing import Any, Protocol

from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    text: str
    provider: str
    model_id: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    raw_metadata: dict[str, Any] | None = None


class LLMProvider(Protocol):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> LLMResponse:
        """Generate a response from system and user prompts."""
