import os
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://vetadmin:vet%402026secure@mq3-database:5432/vetclinica"
)

def create_engine_with_retry(url: str, retries: int = 10, delay: int = 3):
    for attempt in range(retries):
        try:
            engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10)
            with engine.connect() as conn:
                logger.info("Conexão com o banco estabelecida com sucesso!")
            return engine
        except OperationalError as e:
            logger.warning(f"Tentativa {attempt + 1}/{retries} falhou: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    raise Exception("Não foi possível conectar ao banco de dados após várias tentativas")

engine = create_engine_with_retry(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
