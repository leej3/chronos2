from datetime import datetime

from sqlalchemy import INTEGER, Column, DateTime, String, func

from .base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(INTEGER, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, default=datetime.now, nullable=True)
