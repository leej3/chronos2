import logging
from typing import Annotated

from fastapi import APIRouter, Request, Security
from fastapi.responses import JSONResponse, StreamingResponse
from src.api.dependencies import get_current_user
from src.api.dto.dashboard import UpdateDeviceState, UpdateSettings
from src.core.services.chronos import Chronos
from src.core.services.edge_server import EdgeServer
from src.features.auth.jwt_handler import UserToken
from src.features.dashboard.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Dashboard"])
dashboard_service = DashboardService()
edge_server = EdgeServer()
chronos = Chronos()


@router.get("/")
def dashboard_data(
    request: Request,
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = dashboard_service.get_data()
    return JSONResponse(content=data)


@router.post("/update_device_state")
def update_state(
    data: UpdateDeviceState,
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    edge_server.update_device_state(id=data.id, state=data.state)
    return JSONResponse(content={"message": "Updated state successfully"})


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
):
    try:
        logger.info(f"Received settings update request: {data.dict()}")

        # Handle winter setpoint offset if provided
        if data.setpoint_offset_winter is not None:
            logger.info(
                f"Processing winter setpoint offset: {data.setpoint_offset_winter}"
            )

            # Get current boiler status to get base setpoint
            boiler_status = edge_server.get_boiler_status()
            current_setpoint = boiler_status.get(
                "current_setpoint", 150.0
            )  # Default to 150°F if not found

            # Calculate new setpoint with offset
            new_setpoint = current_setpoint + data.setpoint_offset_winter

            # First ensure within user-configured range if provided
            if data.setpoint_min is not None:
                new_setpoint = max(data.setpoint_min, new_setpoint)
            if data.setpoint_max is not None:
                new_setpoint = min(data.setpoint_max, new_setpoint)

            # Validate against hardware limits before proceeding
            if new_setpoint < 120.0 or new_setpoint > 180.0:
                error_msg = f"Calculated setpoint {new_setpoint}°F is outside valid range (120°F-180°F). Please adjust your settings."
                logger.error(error_msg)
                return JSONResponse(content={"message": error_msg}, status_code=400)

            logger.info(
                f"Calculated new setpoint: {new_setpoint}°F (base: {current_setpoint}°F + offset: {data.setpoint_offset_winter}°F, "
                f"user limits: {data.setpoint_min}°F - {data.setpoint_max}°F)"
            )

            # Update boiler setpoint
            response = edge_server.boiler_set_setpoint(new_setpoint)
            logger.info(f"Edge server response: {response}")

        # Update other settings
        for key, value in data.dict().items():
            if value is not None:
                setattr(chronos, key, value)

        return JSONResponse(
            content={"message": "Settings updated successfully"}, status_code=200
        )
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"message": f"Error updating settings: {str(e)}"}, status_code=400
        )


@router.get("/boiler_stats")
async def boiler_stats(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = edge_server.get_data_boiler_stats()
    return JSONResponse(content=data)


@router.get("/boiler_status")
async def boiler_status(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = edge_server.get_boiler_status()
    return JSONResponse(content=data)
