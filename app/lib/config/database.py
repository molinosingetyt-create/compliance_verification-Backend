import boto3
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.lib.config.config import settings

# Token IAM expira en ~900 s; reciclar conexiones antes para no reutilizar tokens vencidos.
_IAM_POOL_RECYCLE = 600
_PASSWORD_POOL_RECYCLE = 3600


def _iam_connection():
    client = boto3.client("rds", region_name=settings.aws_region_resolved)
    token = client.generate_db_auth_token(
        DBHostname=settings.DB_HOST,
        Port=int(settings.DB_PORT or 5432),
        DBUsername=settings.DB_USER or "",
        Region=settings.aws_region_resolved,
    )
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT or 5432),
        dbname=settings.DATABASE,
        user=settings.DB_USER,
        password=token,
        sslmode=(settings.DB_SSLMODE or "require").strip(),
    )


def _build_engine():
    common = dict(
        pool_size=50,
        max_overflow=150,
        pool_timeout=30,
        pool_pre_ping=True,
    )

    if settings.DB_USE_IAM_AUTH:
        return create_engine(
            "postgresql+psycopg2://",
            creator=_iam_connection,
            pool_recycle=_IAM_POOL_RECYCLE,
            **common,
        )

    return create_engine(
        settings.database_url,
        pool_recycle=_PASSWORD_POOL_RECYCLE,
        **common,
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
