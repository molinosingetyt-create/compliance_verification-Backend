from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.lib.config.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.DB_USER}:{quote_plus(settings.DB_PASS)}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DATABASE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=50,
    max_overflow=150,
    pool_timeout=30,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
