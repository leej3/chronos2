from fastapi import FastAPI
from loguru import logger
from api.endpoints import router
from core.config import settings

app = FastAPI(
    title="HVAC Edge Server",
    description="Minimal HVAC control interface",
    version="1.0.0"
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )