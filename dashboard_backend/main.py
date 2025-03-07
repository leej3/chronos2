import asyncio
import signal
import sys

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.dependencies import exception_handler
from src.api.routers import auth_router, dashboard_router
from src.core.common.exceptions import GenericError
from src.core.services.chronos import Chronos
from src.features.auth.auth_service import AuthService

chronos = Chronos()
is_auto_switch_season = chronos.is_auto_switch_season


def destructor(signum=None, frame=None, status=0):
    chronos.scheduler.shutdown(wait=False)
    chronos._turn_off_all_devices()
    sys.exit(status)


signal.signal(signal.SIGTERM, destructor)

auth_service = AuthService()
app = FastAPI()
scheduler = AsyncIOScheduler()


async def auto_switch_season():
    try:
        while True:
            if is_auto_switch_season:
                await chronos._switch_season_auto()
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(1)
    except Exception:
        asyncio.create_task(auto_switch_season())


@app.on_event("startup")
async def startup():
    auth_service.create_or_update_user()
    scheduler.add_job(chronos.create_update_history, "cron", minute="*")
    scheduler.add_job(chronos.get_data_from_web, "cron", minute="*")
    scheduler.start()

    asyncio.create_task(auto_switch_season())


@app.exception_handler(GenericError)
async def generic_exception_handler(
    request: Request, exc: GenericError
) -> JSONResponse:
    return await exception_handler(request, exc)


api_router = APIRouter(prefix="/api")
api_router.include_router(dashboard_router.router)
api_router.include_router(auth_router.router)

app.include_router(api_router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5172, reload=True)
