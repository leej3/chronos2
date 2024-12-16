from datetime import datetime
from sqlalchemy import Column, INTEGER, REAL, BOOLEAN, DateTime
from .base import Base


class Boiler(Base):

    __tablename__ = "boiler"

    id = Column(INTEGER, primary_key=True)
    backup = Column(BOOLEAN, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    switched_timestamp = Column(DateTime, nullable=False)
    status = Column(INTEGER, default=0, nullable=False)
    manual_override = Column(INTEGER, default=0, nullable=False)
    system_supply_temp = Column(REAL, default=0, nullable=False)
    outlet_temp = Column(REAL, default=0, nullable=False)
    inlet_temp = Column(REAL, default=0, nullable=False)
    flue_temp = Column(REAL, default=0, nullable=False)
    cascade_current_power = Column(REAL, default=0, nullable=False)
    lead_firing_rate = Column(REAL, default=0, nullable=False)