import uvicorn
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.dependencies import exception_handler
from src.api.routers import auth_router, dashboard_router
from src.core.common.exceptions import GenericError

app = FastAPI()


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
