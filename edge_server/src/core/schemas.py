from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from .constants import MODES, TEMP_LIMITS

class SensorConfig(BaseModel):
    id: str
    type: str
    pin: int

class ActuatorConfig(BaseModel):
    id: str
    type: str
    pin: int

class ComponentStatus(BaseModel):
    id: str
    type: str  # "chiller" or "boiler"
    status: bool
    pin: int

class SystemState(BaseModel):
    components: List[ComponentStatus]
    temperatures: Dict[str, float]
    humidity: Optional[float]
    mode: str

class ComponentUpdate(BaseModel):
    id: str
    status: bool

class ModeUpdate(BaseModel):
    mode: str = Field(..., description="System mode: COOLING, HEATING, or OFF")

    def validate_mode(cls, v):
        if v.upper() not in MODES:
            raise ValueError(f"Invalid mode. Must be one of: {list(MODES.keys())}")
        return v.upper()

class TemperatureUpdate(BaseModel):
    temperature: float = Field(
        ..., 
        description="Target temperature in Celsius",
        ge=TEMP_LIMITS['MIN'],
        le=TEMP_LIMITS['MAX']
    )