from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
from typing import Optional


class Settings(BaseSettings):
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DATABASE: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    SECRET_KEY_REFRESH: Optional[str] = None
    ALGORITHM: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[str] = None
    ENCRYPT_KEY: Optional[str] = None
    CORS_ORIGINS: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{settings.DB_USER}:{quote_plus(settings.DB_PASS)}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DATABASE}"


settings = Settings()
