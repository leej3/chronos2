from sqlalchemy import BOOLEAN, INTEGER, REAL, Column, DateTime

from .base import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(INTEGER, primary_key=True)
    setpoint_min = Column(REAL, default=0, nullable=False)
    setpoint_max = Column(REAL, default=0, nullable=False)
    setpoint_offset_summer = Column(REAL, default=0, nullable=False)
    setpoint_offset_winter = Column(REAL, default=0, nullable=False)
    tolerance = Column(REAL, default=0, nullable=False)
    mode_change_delta_temp = Column(INTEGER, default=0, nullable=False)
    cascade_time = Column(INTEGER, default=0, nullable=False)
    mode = Column(INTEGER, default=0, nullable=False)
    mode_switch_timestamp = Column(DateTime, nullable=True)
    mode_switch_lockout_time = Column(INTEGER, default=2, nullable=False)
    is_auto_switch_season = Column(BOOLEAN, default=False, nullable=False)
