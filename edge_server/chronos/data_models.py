from typing import Optional

from pydantic import BaseModel, Field


class SystemStatus(BaseModel):
    sensors: dict
    devices: dict
    status: bool
    mock_devices: bool = False
    read_only_mode: bool = False


class DeviceModel(BaseModel):
    id: int = Field(..., ge=0, lt=7, description="Device ID (0-4)")
    state: bool


# New models for boiler data
class BoilerStats(BaseModel):
    """Statistics from the boiler including temperatures and performance metrics."""

    system_supply_temp: Optional[float] = Field(
        None, description="System supply temperature in °F"
    )
    outlet_temp: float = Field(..., description="Outlet temperature in °F")
    inlet_temp: float = Field(..., description="Inlet temperature in °F")
    flue_temp: float = Field(..., description="Flue temperature in °F")
    cascade_current_power: float = Field(
        ..., description="Current cascade power percentage"
    )
    lead_firing_rate: float = Field(
        ..., description="Lead boiler firing rate percentage"
    )
    water_flow_rate: float = Field(..., description="Water flow rate in GPM")
    pump_status: bool = Field(..., description="Pump running status")
    flame_status: bool = Field(..., description="Flame detection status")


class OperatingStatus(BaseModel):
    """Current operating status of the boiler."""

    operating_mode: int = Field(..., description="Current operating mode number")
    operating_mode_str: str = Field(..., description="Operating mode description")
    cascade_mode: int = Field(..., description="Current cascade mode number")
    cascade_mode_str: str = Field(..., description="Cascade mode description")
    current_setpoint: float = Field(
        ..., description="Current temperature setpoint in °F"
    )
    status: bool = Field(default=True, description="Current boiler status")
    setpoint_temperature: float = Field(
        ..., description="Target temperature setpoint in °F"
    )
    current_temperature: float = Field(
        ..., description="Current measured temperature in °F"
    )
    pressure: float = Field(default=0.0, description="Current system pressure")
    error_code: int = Field(default=0, description="Current error code, 0 if no error")


class SetpointUpdate(BaseModel):
    """Temperature setpoint update request."""

    temperature: float = Field(
        ..., description="Temperature setpoint in °F", ge=120, le=180
    )
