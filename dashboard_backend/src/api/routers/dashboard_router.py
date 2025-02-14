from typing import Annotated

from fastapi import APIRouter, Request, Security
from fastapi.responses import JSONResponse, StreamingResponse
from src.api.dependencies import get_current_user
from src.api.dto.dashboard import SwitchSeason, UpdateDeviceState, UpdateSettings
from src.core.services.chronos import Chronos
from src.core.services.edge_server import EdgeServer
from src.features.auth.jwt_handler import UserToken
from src.features.dashboard.dashboard_service import DashboardService

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
    # Update for winter
    data = dashboard_service.update_settings(data)
    return JSONResponse(content=data)


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


@router.get("/boiler_errors")
async def boiler_errors(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = edge_server.get_boiler_errors()
    return JSONResponse(content=data)


@router.get("/boiler_info")
async def boiler_info(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = edge_server.get_boiler_info()
    return JSONResponse(content=data)


@router.post("/switch-season")
async def switch_season(
    data: SwitchSeason,
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    try:
        result = dashboard_service.switch_season_mode(data.season_value)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"message": str(e), "status": "error"}, status_code=400
        )
