import logging
import os

from chronos.config import cfg
from chronos.data_models import (
    BoilerStats,
    OperatingStatus,
    RelayModel,
    SeasonSwitch,
    SetpointLimitsUpdate,
    SetpointUpdate,
    SystemStatus,
)
from chronos.devices import get_device_manager
from chronos.utils import (
    CircuitBreaker,
    RateLimiter,
    with_circuit_breaker,
    with_rate_limit,
)
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize the device manager
device_manager = get_device_manager()

# Create instances of CircuitBreaker and RateLimiter
circuit_breaker = CircuitBreaker()

rate_limiter = RateLimiter(min_interval=5)
rate_limiter_season_switch = RateLimiter(min_interval=120)

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ensure_not_read_only():
    if cfg.READ_ONLY_MODE:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted: system is in read-only mode",
        )
    return True


@app.get("/get_data", response_model=SystemStatus)
@with_circuit_breaker(circuit_breaker)
async def get_data():
    return SystemStatus(
        sensors=device_manager.get_sensor_data(),
        mock_devices=device_manager.is_mock_mode(),
        read_only_mode=cfg.READ_ONLY_MODE,
        season_mode=device_manager.season_mode,
        is_switching_season=device_manager.is_switching_season,
    )


@app.get("/get_state_of_all_relays", response_model=list[RelayModel])
@with_circuit_breaker(circuit_breaker)
async def get_state_of_all_relays():
    return device_manager.get_state_of_all_relays()


@app.get("/device_state", response_model=RelayModel)
@with_circuit_breaker(circuit_breaker)
async def get_relay_state(
    device: int = Query(..., ge=0, lt=8, description="The device ID (0-7)"),
):
    return device_manager.get_relay_state(device)


@app.post("/device_state", dependencies=[Depends(ensure_not_read_only)])
@with_circuit_breaker(circuit_breaker)
@with_rate_limit(rate_limiter)
async def update_device_state(data: RelayModel):
    return device_manager.set_device_state(data.id, data.state)


# New boiler endpoints
@app.get("/boiler_stats", response_model=BoilerStats)
@with_circuit_breaker(circuit_breaker)
async def get_boiler_stats():
    """Get current boiler statistics."""
    try:
        stats = device_manager.get_boiler_stats()
        if not stats:
            raise HTTPException(status_code=500, detail="Failed to read boiler data")
        return BoilerStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read boiler data: {str(e)}"
        )


@app.get("/boiler_status", response_model=OperatingStatus)
@with_circuit_breaker(circuit_breaker)
async def get_boiler_status():
    """Get current boiler operating status."""
    try:
        status = device_manager.get_operating_status()
        if not status:
            raise HTTPException(
                status_code=500, detail="Failed to read operating status"
            )
        return OperatingStatus(**status)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read operating status: {str(e)}"
        )


@app.post("/boiler_set_setpoint", dependencies=[Depends(ensure_not_read_only)])
@with_circuit_breaker(circuit_breaker)
@with_rate_limit(rate_limiter)
async def set_setpoint(data: SetpointUpdate):
    try:
        success = device_manager.set_boiler_setpoint(data.temperature)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set temperature")
        return {"message": f"Temperature setpoint set to {data.temperature}°F"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download_log", response_class=FileResponse)
@with_circuit_breaker(circuit_breaker)
async def download_log():
    """Endpoint for downloading log file"""
    log_path = cfg.files.log_path
    try:
        if not os.path.exists(log_path):
            raise FileNotFoundError(f"File at path {log_path} does not exist.")
        return FileResponse(
            log_path, media_type="text/plain; charset=utf-8", filename="chronos_log.txt"
        )
    except (FileNotFoundError, RuntimeError) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read log file: {str(e)}"
        )


@app.get("/temperature_limits")
def get_temperature_limits():
    """Get both hard and soft temperature limits for the boiler."""
    try:
        soft_limits = device_manager.get_temperature_limits()
        if not soft_limits:
            soft_limits = {
                "min_setpoint": cfg.temperature.min_setpoint,
                "max_setpoint": cfg.temperature.max_setpoint,
            }

        return {
            "hard_limits": {
                "min_setpoint": cfg.temperature.min_setpoint,
                "max_setpoint": cfg.temperature.max_setpoint,
            },
            "soft_limits": soft_limits,
        }
    except Exception as e:
        logger.error(f"Failed to get temperature limits: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get temperature limits")


@app.post("/temperature_limits", dependencies=[Depends(ensure_not_read_only)])
async def set_temperature_limits(limits: SetpointLimitsUpdate):
    try:
        limits.validate_range()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        success = device_manager.set_temperature_limits(
            limits.min_setpoint, limits.max_setpoint
        )
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to set temperature limits"
            )
        return {"message": "Temperature limits updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/season_switch", dependencies=[Depends(ensure_not_read_only)])
@with_circuit_breaker(circuit_breaker)
@with_rate_limit(rate_limiter_season_switch)
async def season_switch(data: SeasonSwitch):
    try:
        device_manager.season_switch(data.season_mode, data.mode_switch_lockout_time)
        return {"message": "Season switch updated successfully"}
    except Exception as e:
        logger.error(f"Failed to set season switch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
