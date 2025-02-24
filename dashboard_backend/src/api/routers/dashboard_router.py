import logging
from typing import Annotated

from fastapi import APIRouter, Request, Security
from fastapi.responses import JSONResponse, StreamingResponse
from src.api.dependencies import get_current_user
from src.api.dto.dashboard import (
    SetpointUpdate,
    SwitchSeason,
    UpdateDeviceState,
    UpdateSettings,
)
from src.core.common.exceptions import EdgeServerError
from src.core.services.chronos import Chronos
from src.core.services.edge_server import EdgeServer
from src.features.auth.jwt_handler import UserToken
from src.features.dashboard.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dashboard"])
dashboard_service = DashboardService()
chronos = Chronos()


def get_edge_server():
    return EdgeServer()


def get_dashboard_service():
    return DashboardService()


@router.get("/")
def dashboard_data(
    request: Request,
    current_user: Annotated[UserToken, Security(get_current_user)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
    dashboard_service: Annotated[DashboardService, Security(get_dashboard_service)],
):
    data = dashboard_service.get_data()
    return JSONResponse(content=data)


@router.post("/update_device_state")
def update_state(
    data: UpdateDeviceState,
    current_user: Annotated[UserToken, Security(get_current_user)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
    dashboard_service: Annotated[DashboardService, Security(get_dashboard_service)],
):
    data = dashboard_service.update_device_state(data)
    return JSONResponse(content=data)


@router.get("/download_log")
def download_log(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    resp = StreamingResponse(dashboard_service.log_generator(), media_type="text/csv")
    resp.headers["Content-Disposition"] = "attachment; filename=exported-data.csv"
    return resp


@router.get("/chart_data")
def chart_data(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = dashboard_service.get_chart_data()
    return JSONResponse(content=data)


@router.post("/update_settings")
async def update_settings(
    data: UpdateSettings,
    current_user: Annotated[UserToken, Security(get_current_user)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
):
    try:
        logger.info(f"Received settings update request: {data.dict()}")

        # Get temperature limits from edge server
        limits = edge_server.get_temperature_limits()
        hard_limits = limits["hard_limits"]

        # Validate setpoint limits against hardware limits
        if data.setpoint_min is not None:
            if (
                data.setpoint_min < hard_limits["min_setpoint"]
                or data.setpoint_min > hard_limits["max_setpoint"]
            ):
                error_msg = f"Minimum setpoint must be between {hard_limits['min_setpoint']}°F and {hard_limits['max_setpoint']}°F"
                return JSONResponse(content={"detail": error_msg}, status_code=400)

        if data.setpoint_max is not None:
            if (
                data.setpoint_max < hard_limits["min_setpoint"]
                or data.setpoint_max > hard_limits["max_setpoint"]
            ):
                error_msg = f"Maximum setpoint must be between {hard_limits['min_setpoint']}°F and {hard_limits['max_setpoint']}°F"
                return JSONResponse(content={"detail": error_msg}, status_code=400)

        # Update temperature limits in edge server if they changed
        if data.setpoint_min is not None or data.setpoint_max is not None:
            soft_limits = {
                "min_setpoint": (
                    data.setpoint_min
                    if data.setpoint_min is not None
                    else hard_limits["min_setpoint"]
                ),
                "max_setpoint": (
                    data.setpoint_max
                    if data.setpoint_max is not None
                    else hard_limits["max_setpoint"]
                ),
            }
            edge_server.set_temperature_limits(limits=soft_limits)

        # Update settings
        for key, value in data.dict().items():
            if value is not None:
                setattr(chronos, key, value)

        return JSONResponse(content={"message": "Settings updated successfully"})
    except EdgeServerError as e:
        logger.error(f"Error updating settings: {str(e)}", exc_info=True)
        error_msg = str(e)
        if "read-only mode" in error_msg.lower():
            return JSONResponse(
                content={
                    "detail": "Operation not permitted: system is in read-only mode"
                },
                status_code=403,
            )
        return JSONResponse(
            content={"detail": f"Failed to update temperature limits: {error_msg}"},
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"detail": f"Error updating settings: {str(e)}"},
            status_code=400,
        )
    # Update for winter
    # data = dashboard_service.update_settings(data)
    # return JSONResponse(content=data)


@router.get("/boiler_stats")
async def boiler_stats(
    current_user: Annotated[UserToken, Security(get_current_user)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
):
    data = edge_server.get_data_boiler_stats()
    return JSONResponse(content=data)


@router.get("/boiler_status")
async def boiler_status(
    current_user: Annotated[UserToken, Security(get_current_user)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
):
    data = edge_server.get_boiler_status()
    return JSONResponse(content=data)


@router.get("/temperature_limits")
async def temperature_limits(
    current_user: Annotated[UserToken, Security(get_current_user)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
):
    """Get the valid temperature range for the boiler from the edge server."""
    data = edge_server.get_temperature_limits()
    return JSONResponse(content=data)


@router.post("/boiler_set_setpoint")
async def boiler_set_setpoint(
    data: SetpointUpdate,
    current_user: Annotated[UserToken, Security(get_current_user)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
):
    data = dashboard_service.boiler_set_setpoint(data.temperature)
    return JSONResponse(content=data)


@router.post("/switch-season")
async def switch_season(
    data: SwitchSeason,
    current_user: Annotated[UserToken, Security(get_current_user)],
    dashboard_service: Annotated[DashboardService, Security(get_dashboard_service)],
    edge_server: Annotated[EdgeServer, Security(get_edge_server)],
):
    result = dashboard_service.switch_season_mode(data.season_value)
    return JSONResponse(content=result, status_code=200)
