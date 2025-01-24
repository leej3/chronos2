from sqlalchemy import INTEGER, REAL, Column

from .base import Base


class SetpointLookup(Base):
    __tablename__ = "setpoint_lookup"

    id = Column(INTEGER, primary_key=True)
    wind_chill = Column(INTEGER)
    setpoint = Column(REAL)
    avg_wind_chill = Column(INTEGER)
    setpoint_offset = Column(INTEGER)
