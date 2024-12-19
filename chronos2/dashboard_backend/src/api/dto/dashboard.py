from typing import Optional

from pydantic import BaseModel


class UpdateState(BaseModel):
    device: int
    manual_override: int


class UpdateSettings(BaseModel):
    """
    tolerance: "",
    setpoint_min: "",
    setpoint_max: "",
    setpoint_offset_summer: "",
    setpoint_offset_winter: "",
    mode_change_delta_temp: "",
    mode_switch_lockout_time: "",
    cascade_time: "",
    """

    # device: int
    tolerance: Optional[float]
    setpoint_min: Optional[float]
    setpoint_max: Optional[float]
    setpoint_offset_summer: Optional[float]
    setpoint_offset_winter: Optional[float]
    mode_change_delta_temp: Optional[float]
    mode_switch_lockout_time: Optional[int]
    cascade_time: Optional[int]
