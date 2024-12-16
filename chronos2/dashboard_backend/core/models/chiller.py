from datetime import datetime
from sqlalchemy import Column, INTEGER, BOOLEAN, DateTime
from .base import Base

class Chiller1(Base):

    __tablename__ = "chiller1"

    id = Column(INTEGER, primary_key=True)
    backup = Column(BOOLEAN, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    switched_timestamp = Column(DateTime, nullable=False)
    status = Column(INTEGER, default=0, nullable=False)
    manual_override = Column(INTEGER, default=0, nullable=False)


class Chiller2(Base):

    __tablename__ = "chiller2"

    id = Column(INTEGER, primary_key=True)
    backup = Column(BOOLEAN, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    switched_timestamp = Column(DateTime, nullable=False)
    status = Column(INTEGER, default=0, nullable=False)
    manual_override = Column(INTEGER, default=0, nullable=False)


class Chiller3(Base):

    __tablename__ = "chiller3"

    id = Column(INTEGER, primary_key=True)
    backup = Column(BOOLEAN, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    switched_timestamp = Column(DateTime, nullable=False)
    status = Column(INTEGER, default=0, nullable=False)
    manual_override = Column(INTEGER, default=0, nullable=False)


class Chiller4(Base):

    __tablename__ = "chiller4"

    id = Column(INTEGER, primary_key=True)
    backup = Column(BOOLEAN, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    switched_timestamp = Column(DateTime, nullable=False)
    status = Column(INTEGER, default=0, nullable=False)
    manual_override = Column(INTEGER, default=0, nullable=False)
