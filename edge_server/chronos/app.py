import logging
import os
import time
from collections import namedtuple
from functools import wraps
from typing import Callable

from chronos.config import cfg
from chronos.data_models import (
    BoilerStats,
    DeviceModel,
    ErrorHistory,
    ModelInfo,
    OperatingStatus,
    SetpointLimitsUpdate,
    SetpointUpdate,
    SystemStatus,
)
from chronos.devices import (
    ModbusException,
    SerialDevice,
    create_modbus_connection,
    safe_read_temperature,
)
from chronos.mock_devices.mock_data import (
    history_none,
    mock_boiler_stats,
    mock_devices_data,
    mock_error_history,
    mock_error_history_none,
    mock_model_info,
    mock_operating_status,
    mock_point_update,
    mock_sensors,
)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# Circuit breaker states and configuration
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self.is_open = False

    def record_failure(self):
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("Circuit breaker opened due to multiple failures")

    def record_success(self):
        """Record a success and reset failure count."""
        self.failure_count = 0
        self.is_open = False

    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if not self.is_open:
            return True

        # Check if enough time has passed to try again
        if time.time() - self.last_failure_time >= self.reset_timeout:
            logger.info("Circuit breaker reset timeout reached, allowing retry")
            self.is_open = False
            self.failure_count = 0
            return True

        return False


# Rate limiter for temperature changes
class RateLimiter:
    def __init__(self, min_interval: float = 5.0):
        self.min_interval = min_interval
        self.last_change_time = 0

    def can_change(self) -> bool:
        """Check if enough time has passed since last change."""
        current_time = time.time()
        if current_time - self.last_change_time >= self.min_interval:
            self.last_change_time = current_time
            return True
        return False


# Create instances
circuit_breaker = CircuitBreaker()
rate_limiter = RateLimiter()


# Decorator for circuit breaker pattern
def with_circuit_breaker(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not circuit_breaker.can_execute():
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable due to multiple failures. Please try again later.",
            )

        try:
            result = await func(*args, **kwargs)
            circuit_breaker.record_success()
            return result
        except Exception:
            circuit_breaker.record_failure()
            raise

    return wrapper


# Decorator for rate limiting
def with_rate_limit(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not rate_limiter.can_change():
            raise HTTPException(
                status_code=429,
                detail="Too many temperature changes. Please wait before trying again.",
            )
        return await func(*args, **kwargs)

    return wrapper


def check_read_only(func: Callable):
    """Decorator to prevent write operations in read-only mode."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        if cfg.READ_ONLY_MODE:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted: system is in read-only mode",
            )
        return await func(*args, **kwargs)

    return wrapper


DeviceTuple = namedtuple(
    "DeviceTuple", ["boiler", "chiller1", "chiller2", "chiller3", "chiller4"]
)

# Initialize devices
DEVICES = DeviceTuple(
    *[
        SerialDevice(id=i, portname=cfg.serial.portname, baudrate=cfg.serial.baudr)
        for i in range(5)
    ]
)
MOCK_DEVICES = cfg.MOCK_DEVICES
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Legacy endpoints
def get_chronos_status():
    chronos_status = True
    try:
        with open("/var/run/chronos.pid") as pid_file:
            pid = int(pid_file.readline())
    except IOError:
        chronos_status = False
    else:
        chronos_status = os.path.exists("/proc/{}".format(pid))
    return chronos_status


@app.get("/get_data", response_model=SystemStatus)
@with_circuit_breaker
async def get_data():
    """Legacy endpoint for system status."""
    if MOCK_DEVICES:
        try:
            sensors = mock_sensors()
            devices = {device["id"]: device["state"] for device in mock_devices_data()}
            status = True
            return SystemStatus(
                sensors=sensors,
                devices=devices,
                status=status,
                mock_devices=MOCK_DEVICES,
                read_only_mode=cfg.READ_ONLY_MODE,
            )
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            return SystemStatus(
                sensors={},
                devices={},
                status=False,
                mock_devices=True,
                read_only_mode=cfg.READ_ONLY_MODE,
            )

    try:
        sensors = {
            "return_temp": safe_read_temperature(cfg.sensors.in_id),
            "water_out_temp": safe_read_temperature(cfg.sensors.out_id),
        }
        status = get_chronos_status()
        devices = {i: DEVICES[i].state for i in range(len(DEVICES))}
        return SystemStatus(
            sensors=sensors,
            devices=devices,
            status=status,
            mock_devices=MOCK_DEVICES,
            read_only_mode=cfg.READ_ONLY_MODE,
        )
    except Exception as e:
        logger.error(f"Error reading data: {e}")
        return SystemStatus(
            sensors={},
            devices={},
            status=False,
            mock_devices=False,
            read_only_mode=cfg.READ_ONLY_MODE,
        )


@app.get("/device_state", response_model=DeviceModel)
@with_circuit_breaker
async def get_device_state(
    device: int = Query(..., ge=0, lt=5, description="The device ID (0-4)"),
):
    """Legacy endpoint for device state."""
    if MOCK_DEVICES:
        return DeviceModel(id=device, state=True)
    return DeviceModel(id=device, state=DEVICES[device].state)


@app.post("/device_state")
@with_circuit_breaker
@with_rate_limit
@check_read_only
async def update_device_state(data: DeviceModel):
    if MOCK_DEVICES:
        return DeviceModel(id=data.id, state=data.state)
    """Legacy endpoint for updating device state."""
    device_obj = DEVICES[data.id]
    device_obj.state = data.state
    return DeviceModel(id=device_obj.id, state=device_obj.state)


# New boiler endpoints
@app.get("/boiler_stats", response_model=BoilerStats)
@with_circuit_breaker
async def get_boiler_stats():
    """Get current boiler statistics."""
    if MOCK_DEVICES:
        try:
            return BoilerStats(**mock_boiler_stats())
        except ModbusException as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to read boiler data: {str(e)}"
            )
    try:
        with create_modbus_connection() as device:
            stats = device.read_boiler_data()
            if not stats:
                raise HTTPException(
                    status_code=500, detail="Failed to read boiler data"
                )
            return BoilerStats(**stats)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read boiler data: {str(e)}"
        )


@app.get("/boiler_status", response_model=OperatingStatus)
@with_circuit_breaker
async def get_boiler_status():
    """Get current boiler operating status."""
    if MOCK_DEVICES:
        return OperatingStatus(**mock_operating_status())
    try:
        with create_modbus_connection() as device:
            status = device.read_operating_status()
            if not status:
                raise HTTPException(
                    status_code=500, detail="Failed to read operating status"
                )
            return OperatingStatus(**status)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read operating status: {str(e)}"
        )


@app.get("/boiler_errors", response_model=ErrorHistory)
@with_circuit_breaker
async def get_boiler_errors():
    """Get boiler error history."""
    if MOCK_DEVICES:
        try:
            history = history_none()
            if history:
                return ErrorHistory(**mock_error_history_none())
            return ErrorHistory(**mock_error_history())
        except ModbusException as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to read error history: {str(e)}"
            )
    try:
        with create_modbus_connection() as device:
            history = device.read_error_history()
            if not history:
                history = {
                    "last_lockout_code": None,
                    "last_lockout_str": None,
                    "last_blockout_code": None,
                    "last_blockout_str": None,
                }
            return ErrorHistory(**history)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read error history: {str(e)}"
        )


@app.get("/boiler_info", response_model=ModelInfo)
@with_circuit_breaker
async def get_boiler_info():
    """Get boiler model information."""
    if MOCK_DEVICES:
        try:
            return ModelInfo(**mock_model_info())
        except ModbusException as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to read model info: {str(e)}"
            )
    try:
        with create_modbus_connection() as device:
            info = device.read_model_info()
            if not info:
                raise HTTPException(status_code=500, detail="Failed to read model info")
            return ModelInfo(**info)
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read model info: {str(e)}"
        )


@app.post("/boiler_set_setpoint")
@with_circuit_breaker
@with_rate_limit
@check_read_only
async def set_setpoint(data: SetpointUpdate):
    if MOCK_DEVICES:
        try:
            mock_point_update()
            return {"message": f"Temperature setpoint set to {data.temperature}°F"}
        except ModbusException as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to set temperature: {str(e)}"
            )
    """Update boiler temperature setpoint."""
    try:
        with create_modbus_connection() as device:
            success = device.set_boiler_setpoint(data.temperature)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to set temperature")
            return {"message": f"Temperature setpoint set to {data.temperature}°F"}
    except ModbusException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to set temperature: {str(e)}"
        )


@app.get("/download_log", response_class=FileResponse)
@with_circuit_breaker
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
    if MOCK_DEVICES:
        return {
            "hard_limits": {
                "min_setpoint": cfg.temperature.min_setpoint,
                "max_setpoint": cfg.temperature.max_setpoint,
            },
            "soft_limits": {
                "min_setpoint": cfg.temperature.min_setpoint,
                "max_setpoint": cfg.temperature.max_setpoint,
            },
        }

    try:
        with create_modbus_connection() as device:
            soft_limits = device.get_temperature_limits()
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


@app.post("/temperature_limits")
@check_read_only
async def set_temperature_limits(limits: SetpointLimitsUpdate):
    """Set soft temperature limits for the boiler."""
    try:
        # Validate that min < max
        limits.validate_range()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if MOCK_DEVICES:
        return {"message": "Temperature limits updated successfully"}

    # Set limits in modbus device
    try:
        with create_modbus_connection() as device:
            success = device.set_temperature_limits(
                limits.min_setpoint, limits.max_setpoint
            )
            if not success:
                raise HTTPException(
                    status_code=500, detail="Failed to set temperature limits"
                )
    except ModbusException as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"message": "Temperature limits updated successfully"}
