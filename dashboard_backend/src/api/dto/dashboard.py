from typing import Optional

from pydantic import BaseModel, Field, validator


class SetpointUpdate(BaseModel):
    temperature: float


class SwitchSeason(BaseModel):
    season_value: int


class UpdateDeviceState(BaseModel):
    id: int
    state: bool


class RelayModel(BaseModel):
    id: int = Field(..., ge=0, lt=7, description="Device ID (0-4)")
    state: bool


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
    setpoint_min: Optional[float] = Field(None)  # Validation will be done in the router
    setpoint_max: Optional[float] = Field(None)  # Validation will be done in the router
    setpoint_offset_summer: Optional[float]
    setpoint_offset_winter: Optional[float]
    mode_change_delta_temp: Optional[float]
    mode_switch_lockout_time: Optional[int]
    cascade_time: Optional[int]

    @validator("setpoint_max")
    def max_greater_than_min(cls, v, values):
        if v is not None and values.get("setpoint_min") is not None:
            if v < values["setpoint_min"]:
                raise ValueError(
                    "Maximum setpoint must be greater than minimum setpoint"
                )
        return v
