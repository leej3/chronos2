import uvicorn
from fastapi import FastAPI, APIRouter
from src.api.routers import dashboard_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
api_router = APIRouter(prefix="/api")
api_router.include_router(dashboard_router.router)

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
