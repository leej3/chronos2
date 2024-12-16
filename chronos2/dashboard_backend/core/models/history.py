from datetime import datetime
from sqlalchemy import Column, INTEGER, REAL, DateTime
from .base import Base

class History(Base):

    __tablename__ = "history"

    id = Column(INTEGER, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    outside_temp = Column(REAL, default=0, nullable=False)
    effective_setpoint = Column(REAL, default=0, nullable=False)
    water_out_temp = Column(REAL, default=0, nullable=False)
    return_temp = Column(REAL, default=0, nullable=False)
    boiler_status = Column(INTEGER, default=0, nullable=False)
    cascade_fire_rate = Column(REAL, default=0, nullable=False)
    lead_fire_rate = Column(REAL, default=0, nullable=False)
    chiller1_status = Column(INTEGER, default=0, nullable=False)
    chiller2_status = Column(INTEGER, default=0, nullable=False)
    chiller3_status = Column(INTEGER, default=0, nullable=False)
    chiller4_status = Column(INTEGER, default=0, nullable=False)
    tha_setpoint = Column(REAL, default=0, nullable=False)
    setpoint_offset_winter = Column(REAL, default=0, nullable=False)
    setpoint_offset_summer = Column(REAL, default=0, nullable=False)
    tolerance = Column(REAL, default=0, nullable=False)
    boiler_manual_override = Column(INTEGER, default=0, nullable=False)
    chiller1_manual_override = Column(INTEGER, default=0, nullable=False)
    chiller2_manual_override = Column(INTEGER, default=0, nullable=False)
    chiller3_manual_override = Column(INTEGER, default=0, nullable=False)
    chiller4_manual_override = Column(INTEGER, default=0, nullable=False)
    mode = Column(INTEGER, default=1, nullable=False)
    cascade_time = Column(INTEGER, default=0, nullable=False)
    wind_speed = Column(REAL, default=0, nullable=False)
    avg_outside_temp = Column(REAL, default=0, nullable=False)
    avg_cascade_fire_rate = Column(REAL, default=0, nullable=False)
    delta = Column(INTEGER, default=0, nullable=False)

