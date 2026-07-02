import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings
from app.llm.factory import get_llm_provider


def main() -> None:
    if settings.llm_provider.lower() != "bedrock":
        print("Set LLM_PROVIDER=bedrock before running this manual script.")
        print("Automated tests intentionally use LLM_PROVIDER=mock.")
        return

    provider = get_llm_provider()
    response = provider.generate(
        system_prompt="You are a concise AWS SaaS delivery copilot.",
        user_prompt="Question:\nSay hello in one sentence.\n\nContext:\nManual Bedrock smoke test.",
        temperature=0.2,
        max_tokens=120,
    )
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
