from src.chronos.lib.db import History
from src.core.configs.database import get_db
from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from src.features.dashboard.dashboard_service import DashboardService
from src.chronos.lib import Chronos, WINTER, SUMMER, TO_WINTER, TO_SUMMER
from src.chronos.lib import db_queries

router = APIRouter(tags=["Dashboard"])
dashboard_service = DashboardService()
chronos = Chronos()


@router.route("/season_templates")
async def get_rendered_season_templates():
    data = await dashboard_service.get_data()
    return data


@router.get("/download_log")
def dump_log():
    resp = StreamingResponse(db_queries.log_generator(), media_type="text/csv")
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
async def index(request: Request):
    data = await dashboard_service.get_data()
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
    data = db_queries.get_chart_data()
    resp = Response(
        response=data,
        status=200,
        mimetype="application/json"
    )
    return resp
