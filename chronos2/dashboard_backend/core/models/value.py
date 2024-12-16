from sqlalchemy import Column, INTEGER, BOOLEAN
from .base import Base

class SummerValve(Base):

    __tablename__ = "summer_valve"

    id = Column(INTEGER, primary_key=True)
    backup = Column(BOOLEAN, default=False, nullable=False)
    status = Column(INTEGER, default=0, nullable=False)


class WinterValve(Base):

    __tablename__ = "winter_valve"

    id = Column(INTEGER, primary_key=True)
    backup = Column(BOOLEAN, default=False, nullable=False)
    status = Column(INTEGER, default=0, nullable=False)
