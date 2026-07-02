from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"))

    app_name: str = "AWS SaaS Delivery Copilot"
    app_env: str = "local"
    default_tenant_id: str = "tenant_acme"

    llm_provider: str = "mock"

    aws_region: str = "us-east-1"
    s3_bucket_name: str | None = None
    bedrock_model_id: str | None = None

    vector_store_path: str = ".local/chroma"


settings = Settings()
