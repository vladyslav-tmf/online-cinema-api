from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import get_settings

settings = get_settings()

DATABASE_URL = f"sqlite:///{settings.PATH_TO_DB}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
connection = engine.connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
