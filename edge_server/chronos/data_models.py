from typing import Optional

from pydantic import BaseModel, Field

from .config import cfg


class SystemStatus(BaseModel):
    sensors: dict
    mock_devices: bool = False
    read_only_mode: bool = False


class SwitchStateRequest(BaseModel):
    command: str
    relay_only: bool = False
    is_season_switch: bool = False


class RelayModel(BaseModel):
    id: int = Field(..., ge=0, lt=8, description="Device ID (0-7)")
    state: bool
    is_season_switch: bool = False


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


class SetpointUpdate(BaseModel):
    """Temperature setpoint update."""

    temperature: float = Field(
        ...,
        description="Desired temperature setpoint in °F",
        ge=cfg.temperature.min_setpoint,
        le=cfg.temperature.max_setpoint,
        error_messages={
            "type_error": "Temperature must be a number",
            "ge": f"Temperature must be at least {cfg.temperature.min_setpoint}°F for safe operation",
            "le": f"Temperature must not exceed {cfg.temperature.max_setpoint}°F for safe operation",
        },
    )


class SetpointLimitsUpdate(BaseModel):
    """Update for user-defined soft temperature limits."""

    min_setpoint: float = Field(
        ...,
        description="Minimum allowed setpoint in °F",
        ge=cfg.temperature.min_setpoint,
        le=cfg.temperature.max_setpoint,
    )
    max_setpoint: float = Field(
        ...,
        description="Maximum allowed setpoint in °F",
        ge=cfg.temperature.min_setpoint,
        le=cfg.temperature.max_setpoint,
    )

    def validate_range(self):
        """Ensure min is less than max."""
        if self.min_setpoint >= self.max_setpoint:
            raise ValueError("Minimum setpoint must be less than maximum setpoint")
        return self
