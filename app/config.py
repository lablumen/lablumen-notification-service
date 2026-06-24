from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    aws_region: str = "us-east-1"
    notifications_queue_url: str = ""
    ses_sender_email: str = "no-reply@lablumen.local"

    poll_wait_seconds: int = 20  # SQS long-poll
    max_messages: int = 10
    error_backoff_seconds: int = 5


settings = Settings()
