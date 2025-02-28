import os
import sys
from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock

from fastapi import HTTPException
from src.api.dependencies import get_current_user
from src.api.routers.dashboard_router import (
    get_dashboard_service,
    get_edge_server,
    router,
)
from src.core.common.exceptions import EdgeServerError
from src.core.services.chronos import Chronos
from src.core.services.device import Device
from src.core.services.edge_server import EdgeServer
from src.features.auth.jwt_handler import UserToken
from src.features.dashboard.dashboard_service import DashboardService

app = FastAPI()
app.include_router(router, prefix="/api")

data = {
    "sensors": {"return_temp": 75.0, "water_out_temp": 85.0},
    "devices": {"0": True, "1": False, "2": False, "3": False, "4": False},
    "results": {
        "outside_temp": 65.0,
        "baseline_setpoint": 80.0,
        "setpoint_min": 70.0,
        "setpoint_max": 110.0,
    },
}

settings = {
    "tolerance": 1.0,
    "setpoint_min": 75.0,
    "setpoint_max": 105.0,
    "cascade_time": 5,
    "mode_switch_lockout_time": 30,
    "setpoint_offset_summer": 140,
    "setpoint_offset_winter": 130,
    "mode_change_delta_temp": 3,
}

settings_invalid = {
    "setpoint_min": 100,
    "setpoint_max": 90,
}

switch_season_success_response = {
    "status": "success",
    "mode": 0,
    "mode_switch_timestamp": datetime.now().isoformat(),
    "mode_switch_lockout_time": 30,
    "unlock_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
}


@pytest.fixture
def mock_current_user():
    return UserToken(user_id="test_user", sub="test_user", email="test@example.com")


@pytest.fixture
def mock_edge_server():
    mock = MagicMock(spec=EdgeServer)
    mock.get_temperature_limits.return_value = {
        "hard_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0},
        "soft_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0},
    }

    return mock


@pytest.fixture
def mock_device():
    mock = MagicMock(spec=Device)
    mock.turn_on = MagicMock(spec=Device.turn_on)
    mock.turn_off = MagicMock(spec=Device.turn_off)
    mock.edge_server = MagicMock(spec=EdgeServer)
    return mock


@pytest.fixture
def mock_chronos():
    mock = MagicMock(spec=Chronos)
    mock.mode = 1
    mock._save_devices_states = MagicMock(spec=Chronos._save_devices_states)
    mock.turn_off_devices = MagicMock(spec=Chronos.turn_off_devices)

    return mock


@pytest.fixture
def mock_dashboard_service():
    mock = MagicMock(spec=DashboardService)
    mock.switch_season_mode = MagicMock(spec=DashboardService.switch_season_mode)
    mock.chronos = MagicMock(spec=Chronos)
    return mock


@pytest.fixture
def client(mock_current_user, mock_edge_server, mock_dashboard_service):
    app.dependency_overrides = {
        get_current_user: lambda: mock_current_user,
        get_edge_server: lambda: mock_edge_server,
        get_dashboard_service: lambda: mock_dashboard_service,
    }

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_dashboard_data(client, mock_dashboard_service, mock_edge_server):
    mock_dashboard_service.get_data.return_value = data

    response = client.get("/api/")

    assert response.status_code == 200
    assert response.json() == data


def test_update_device_state(client, mock_dashboard_service):
    mock_dashboard_service.update_device_state.return_value = {
        "id": 0,
        "state": 1,
        "switched_timestamp": datetime.now().isoformat(),
    }
    response = client.post(
        "/api/update_device_state",
        json={"id": 0, "state": 1, "is_season_switch": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 0
    assert data["state"] == 1


def test_update_device_state_error(client, mock_dashboard_service):
    mock_dashboard_service.update_device_state.side_effect = HTTPException(
        status_code=500, detail="Failed to update device state"
    )
    response = client.post("/api/update_device_state", json={"id": 2, "state": 1})
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to update device state"}


def test_update_settings_success(client, mock_edge_server):
    response = client.post("/api/update_settings", json=settings)
    assert response.status_code == 200
    assert response.json() == {"message": "Settings updated successfully"}


def test_update_settings_temperature_limits_error(client, mock_edge_server):
    mock_edge_server.set_temperature_limits.side_effect = EdgeServerError("Test error")
    response = client.post("/api/update_settings", json=settings)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Failed to update temperature limits: Test error"
    }


def test_update_settings_read_only_mode(client, mock_edge_server):
    mock_edge_server.set_temperature_limits.side_effect = EdgeServerError(
        "read-only mode"
    )
    response = client.post("/api/update_settings", json=settings)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Operation not permitted: system is in read-only mode"
    }


def test_update_settings_validation(client, mock_edge_server):
    response = client.post("/api/update_settings", json=settings_invalid)
    assert response.status_code == 422


def test_switch_season_success(client, mock_edge_server, mock_dashboard_service):
    mock_dashboard_service.switch_season_mode.return_value = (
        switch_season_success_response
    )
    response = client.post("/api/switch-season", json={"season_value": 0})
    data = response.json()
    assert response.status_code == 200
    assert data == switch_season_success_response


def test_switch_season_invalid_season_value(client, mock_dashboard_service):
    mock_dashboard_service.switch_season_mode.side_effect = HTTPException(
        status_code=400, detail="Invalid season value: 6"
    )
    response = client.post("/api/switch-season", json={"season_value": 6})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid season value: 6"}
