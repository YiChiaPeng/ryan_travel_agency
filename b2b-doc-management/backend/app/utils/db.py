from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import time
import logging

logger = logging.getLogger(__name__)

# Use SQLite for development when DATABASE_URL is not set or points to MariaDB
DATABASE_URL = os.getenv("DATABASE_URL")

def wait_for_db(database_url, max_retries=30, retry_interval=2):
    """
    等待數據庫變為可用
    """
    retries = 0
    
    while retries < max_retries:
        try:
            # 創建臨時引擎進行連接測試
            test_engine = create_engine(database_url)
            
            # 嘗試建立連接並執行簡單查詢
            with test_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("數據庫連接成功!")
                return True
                
        except OperationalError as e:
            retries += 1
            logger.warning(f"數據庫連接失敗 (嘗試 {retries}/{max_retries}): {e}")
            
            if retries < max_retries:
                logger.info(f"等待 {retry_interval} 秒後重試...")
                time.sleep(retry_interval)
            else:
                logger.error("達到最大重試次數，數據庫連接失敗")
                raise
                
        except Exception as e:
            logger.error(f"連接數據庫時發生未預期的錯誤: {e}")
            raise
    
    return False

# 等待數據庫可用
wait_for_db(DATABASE_URL)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
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