from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Project information
    PROJECT_NAME: str = "HangSeng Sentiment Price Prediction Agent"

    # Debug mode
    DEBUG: bool = True

    # API credentials
    APIFY_API_TOKEN: str = ""
    EXA_API_KEY: str = ""

    # Database
    DATABASE_URL: str = ""

    # Read configuration from .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Create settings object
settings = Settings()