from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QALens API"
    app_version: str = "0.1.0"
    environment: str = "development"

    jira_base_url: str | None = None
    jira_client_id: str | None = None
    jira_client_secret: str | None = None
    jira_redirect_uri: str | None = None

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
