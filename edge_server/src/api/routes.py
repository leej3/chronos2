from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional
from loguru import logger
from core.hvac_controller import HVACController
from core.constants import MODES, TEMP_LIMITS

router = APIRouter()
controller = HVACController()

class ModeUpdate(BaseModel):
    mode: str = Field(..., description="System mode: COOLING, HEATING, or OFF")

    @validator('mode')
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

@router.get("/state")
async def get_state():
    """Get current system state"""
    try:
        return controller.get_state()
    except Exception as e:
        logger.error(f"Error getting state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mode")
async def get_mode():
    """Get current system mode"""
    try:
        state = controller.get_state()
        mode_value = state['system_mode']
        mode_name = next(
            (name for name, value in MODES.items() if value == mode_value),
            'UNKNOWN'
        )
        return {"mode": mode_name}
    except Exception as e:
        logger.error(f"Error getting mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mode")
async def set_mode(mode_update: ModeUpdate):
    """Set system mode"""
    try:
        controller.set_mode(mode_update.mode)
        return {"status": "success", "mode": mode_update.mode}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/temperature")
async def get_temperature():
    """Get current temperature readings"""
    try:
        state = controller.get_state()
        return {
            "temperature_1": state['temperature_1'],
            "temperature_2": state['temperature_2']
        }
    except Exception as e:
        logger.error(f"Error getting temperature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/temperature")
async def set_temperature(temp_update: TemperatureUpdate):
    """Set target temperature"""
    try:
        controller.set_temperature(temp_update.temperature)
        return {"status": "success", "temperature": temp_update.temperature}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting temperature: {e}")
        raise HTTPException(status_code=500, detail=str(e))