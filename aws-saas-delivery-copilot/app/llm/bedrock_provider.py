from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.core.config import settings
from app.llm.provider import LLMResponse


class BedrockConverseProvider:
    provider_name = "bedrock"

    def __init__(self, model_id: str | None = None, region_name: str | None = None):
        self.model_id = model_id or settings.bedrock_model_id
        self.region_name = region_name or settings.aws_region
        if not self.model_id:
            raise ValueError(
                "BEDROCK_MODEL_ID is required when LLM_PROVIDER=bedrock. "
                "Set it in .env after enabling model access in Amazon Bedrock."
            )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> LLMResponse:
        """Generate text with Amazon Bedrock Runtime Converse API."""
        try:
            client = self._client()
            response = client.converse(
                modelId=self.model_id,
                system=[{"text": system_prompt}],
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": user_prompt}],
                    }
                ],
                inferenceConfig={
                    "temperature": temperature,
                    "maxTokens": max_tokens,
                },
            )
        except NoCredentialsError as error:
            raise RuntimeError(
                "AWS credentials were not found. Configure AWS_PROFILE, environment "
                "credentials, or SSO before using LLM_PROVIDER=bedrock."
            ) from error
        except ClientError as error:
            raise RuntimeError(_friendly_client_error(error)) from error
        except BotoCoreError as error:
            raise RuntimeError(
                f"Bedrock request failed in region {self.region_name}. Check network, region, "
                f"credentials and model access. Original error: {error}"
            ) from error

        usage = response.get("usage", {})
        input_tokens = int(usage.get("inputTokens", 0) or 0)
        output_tokens = int(usage.get("outputTokens", 0) or 0)

        return LLMResponse(
            text=_extract_text(response),
            provider=self.provider_name,
            model_id=self.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=int(usage.get("totalTokens", input_tokens + output_tokens) or 0),
            raw_metadata={
                "stop_reason": response.get("stopReason"),
                "metrics": response.get("metrics"),
                "usage": usage,
            },
        )

    def _client(self):
        import boto3

        return boto3.client("bedrock-runtime", region_name=self.region_name)


def _extract_text(response: dict) -> str:
    content = response.get("output", {}).get("message", {}).get("content", [])
    text_parts = [item.get("text", "") for item in content if item.get("text")]
    return "\n".join(text_parts).strip()


def _friendly_client_error(error: ClientError) -> str:
    code = error.response.get("Error", {}).get("Code", "Unknown")
    message = error.response.get("Error", {}).get("Message", str(error))
    return (
        f"Bedrock Converse call failed ({code}): {message}. "
        "Check AWS credentials, AWS_REGION, BEDROCK_MODEL_ID and whether model access "
        "is enabled for this account and region."
    )
