from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from src.core.chronos import Chronos
from src.core.chronos.constant import TO_SUMMER, TO_WINTER
from src.features.dashboard.dashboard_service import DashboardService

router = APIRouter(tags=["Dashboard"])
dashboard_service = DashboardService()
chronos = Chronos()


@router.route("/season_templates")
async def get_rendered_season_templates():
    data = await dashboard_service.get_data()
    return data


@router.get("/download_log")
def dump_log():
    resp = StreamingResponse(dashboard_service.log_generator(), media_type="text/csv")
    resp.headers["Content-Disposition"] = "attachment; filename=exported-data.csv"
    return resp


@router.post("/update_settings")
def update_settings(request: Request):
    for key, value in request.form.items():
        if value:
            setattr(chronos, key, float(value))
    return JSONResponse(content={"data": request.form})


@router.post("/switch_mode")
def switch_mode(request: Request):
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
def index(request: Request):
    data = dashboard_service.get_data()
    mode = int(data["results"]["mode"])
    return JSONResponse(content={"data": data, "mode": mode})


@router.post("/update_state")
def update_state(request: Request):
    device_number = int(request.form["device"])
    manual_override_value = int(request.form["manual_override"])
    chronos.devices[device_number].manual_override = manual_override_value
    return JSONResponse(content={"message": "Updated state successfully"})


@router.get("/winter")
async def winter():
    data = await dashboard_service.get_data()
    return JSONResponse(content={"data": data})


@router.get("/summer")
async def summer():
    data = await dashboard_service.get_data()
    return JSONResponse(content={"data": data})


@router.get("/chart_data")
def chart_data():
    data = dashboard_service.get_chart_data()
    return JSONResponse(content={"data": data})
