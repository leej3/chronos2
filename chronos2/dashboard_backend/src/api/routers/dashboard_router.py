from typing import Annotated

from fastapi import APIRouter, Request, Security
from fastapi.responses import JSONResponse, StreamingResponse
from src.api.dependencies import get_current_user
from src.api.dto.dashboard import UpdateDeviceState, UpdateSettings
from src.core.chronos import Chronos
from src.core.chronos.constant import TO_SUMMER, TO_WINTER
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
    # Call to edge server update setting
    # edge_server.update_settings(data.dict())
    # Update settings in DB
    for key, value in data.dict().items():
        if value:
            setattr(chronos, key, value)
    return JSONResponse(content={"message": "Updated settings successfully"})
