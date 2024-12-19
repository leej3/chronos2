from typing import Annotated

from fastapi import APIRouter, Request, Security
from fastapi.responses import JSONResponse, StreamingResponse
from src.api.dependencies import get_current_user
from src.api.dto.dashboard import UpdateSettings, UpdateState
from src.core.chronos import Chronos
from src.core.chronos.constant import TO_SUMMER, TO_WINTER
from src.features.auth.jwt_handler import UserToken
from src.features.dashboard.dashboard_service import DashboardService

router = APIRouter(tags=["Dashboard"])
dashboard_service = DashboardService()
chronos = Chronos()


@router.route("/season_templates")
async def get_rendered_season_templates(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = await dashboard_service.get_data()
    return data


@router.get("/download_log")
def dump_log(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    resp = StreamingResponse(dashboard_service.log_generator(), media_type="text/csv")
    resp.headers["Content-Disposition"] = "attachment; filename=exported-data.csv"
    return resp


@router.post("/update_settings")
async def update_settings(
    data: UpdateSettings,
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    for key, value in data.dict().items():
        if value:
            setattr(chronos, key, value)
    return JSONResponse(content={"message": "Updated settings successfully"})


@router.post("/switch_mode")
def switch_mode(
    request: Request,
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    mode = int(request.form["mode"])
    if mode == TO_WINTER:
        error = chronos.is_time_to_switch_season_to_summer
        chronos.switch_season(TO_WINTER)
    elif mode == TO_SUMMER:
        error = chronos.is_time_to_switch_season_to_winter
        chronos.switch_season(TO_SUMMER)
    return JSONResponse(
        content={
            "error": error,
            "mode_switch_lockout_time": chronos.mode_switch_lockout_time,
        }
    )


@router.get("/")
def index(
    request: Request,
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = dashboard_service.get_data()
    return JSONResponse(content=data)


@router.post("/update_state")
def update_state(
    data: UpdateState,
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    device_number = data.device
    manual_override_value = data.manual_override
    chronos.devices[device_number].manual_override = manual_override_value
    return JSONResponse(content={"message": "Updated state successfully"})


@router.get("/winter")
def winter(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = dashboard_service.get_data()
    return JSONResponse(content=data)


@router.get("/summer")
def summer(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = dashboard_service.get_data()
    return JSONResponse(content=data)


@router.get("/chart_data")
def chart_data(
    current_user: Annotated[UserToken, Security(get_current_user)],
):
    data = dashboard_service.get_chart_data()
    return JSONResponse(content=data)
