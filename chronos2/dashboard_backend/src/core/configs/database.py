import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from src.core.configs.root_logger import root_logger as logger

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

# Replace with your own PostgreSQL instance
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    "Provide a transactional scope around a series of operations."
    Session = scoped_session(SessionLocal)
    Session()
    try:
        yield Session
        Session.commit()
    except Exception as e:
        logger.exception("Failed during interaction with the db: {}".format(e))
        Session.rollback()
    finally:
        Session.remove()
