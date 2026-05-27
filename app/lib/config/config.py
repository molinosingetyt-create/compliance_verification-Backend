from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
from typing import Optional


class Settings(BaseSettings):
    # Si se define, se usa tal cual (permite URL completa con parámetros como sslmode).
    # Con DB_USE_IAM_AUTH=true la app ignora DATABASE_URL y arma la conexión con token IAM.
    DATABASE_URL: Optional[str] = None
    # Autenticación IAM a RDS/Aurora (token ~15 min); requiere boto3 y rol/profila con rds-db:connect
    DB_USE_IAM_AUTH: bool = False
    AWS_REGION: Optional[str] = None
    DB_SSLMODE: Optional[str] = "require"
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
    def aws_region_resolved(self) -> str:
        return (self.AWS_REGION or "us-east-1").strip()

    @property
    def database_url(self) -> str:
        # Con IAM no se usa esta URL para crear el engine (ver database.py).
        if self.DB_USE_IAM_AUTH:
            raise RuntimeError(
                "Con DB_USE_IAM_AUTH=true usa el engine con creator IAM; no hay database_url estable."
            )

        # Preferir URL explícita desde env si existe
        if self.DATABASE_URL:
            return self.DATABASE_URL

        base = (
            f"postgresql+psycopg2://{self.DB_USER}:{quote_plus(self.DB_PASS or '')}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DATABASE}"
        )
        # RDS a menudo requiere TLS; por defecto pedimos sslmode=require
        sslmode = (self.DB_SSLMODE or "require").strip()
        if sslmode and "sslmode=" not in base:
            sep = "&" if "?" in base else "?"
            base = f"{base}{sep}sslmode={sslmode}"
        return base


settings = Settings()
