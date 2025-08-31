from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "mariadb://user:password@db:3306/b2b_documents")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    """Return a raw DB-API connection from the SQLAlchemy engine for simple scripts.
    The caller should call .cursor() and manage commits if needed.
    """
    return engine.raw_connection()

def init_db():
    """Initialize database schema from SQLAlchemy models (Base)."""
    Base.metadata.create_all(bind=engine)