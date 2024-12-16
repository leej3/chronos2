from fastapi import APIRouter
from src.features.dashboard.dashboard_service import DashboardService

router = APIRouter(tags=["Dashboard"], prefix="")

@router.get("/")
def dashboard():
    dashboard_service = DashboardService()
    return dashboard_service.get_data()

