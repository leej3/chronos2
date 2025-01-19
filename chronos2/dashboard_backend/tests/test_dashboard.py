import os
import sys
import time

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock

from main import app
from src.api.dependencies import get_current_user
from src.core.chronos import Chronos
from src.core.services.edge_server import EdgeServer
from src.features.auth.jwt_handler import UserToken
from src.features.dashboard.dashboard_service import DashboardService


@pytest.fixture
def mock_dashboard_service():
    mock = MagicMock(DashboardService)
    mock.get_data.return_value = {"key": "value"}
    mock.get_chart_data.return_value = {"chart_key": "chart_value"}
    mock.log_generator.return_value = iter(["log_line_1", "log_line_2"])
    return mock


@pytest.fixture
def mock_edge_server():
    mock = MagicMock(EdgeServer)
    mock.update_device_state.return_value = None
    return mock


@pytest.fixture
def mock_chronos():
    mock = MagicMock(Chronos)
    mock.some_setting = "test"
    return mock


@pytest.fixture
def mock_current_user():
    return UserToken(sub="test_user", email="admin@gmail.com")


@pytest.fixture
def client(mock_dashboard_service, mock_edge_server, mock_chronos):
    app.dependency_overrides[DashboardService] = lambda: mock_dashboard_service
    app.dependency_overrides[EdgeServer] = lambda: mock_edge_server
    app.dependency_overrides[Chronos] = lambda: mock_chronos
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    return TestClient(app)


def test_dashboard_data(client):
    response = client.get("api/")
    data = response.json()
    devices = {"0": True, "1": False, "2": False, "3": False, "4": False}

    assert response.status_code == 200
    assert "sensors" in data
    assert "devices" in data
    assert "results" in data
    assert "efficiency" in data

    assert "return_temp" in data["sensors"]
    assert "water_out_temp" in data["sensors"]

    assert devices == data["devices"]

    assert "outside_temp" in data["results"]
    assert "baseline_setpoint" in data["results"]
    assert "setpoint_min" in data["results"]
    assert "setpoint_max" in data["results"]

    assert "average_temperature_difference" in data["efficiency"]
    assert "chillers_efficiency" in data["efficiency"]
    assert "hours" in data["efficiency"]


def test_update_device_state(client):
    update_data = {"id": 1, "state": "on"}
    response = client.post("/api/update_device_state", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Updated state successfully"}


def test_download_log(client):
    response = client.get("/api/download_log")
    assert response.status_code == 200
    content = list(response.iter_lines())
    assert len(content) >= 1


def test_chart_data(client):
    response = client.get("/api/chart_data")
    assert response.status_code == 200
    chart_data = response.json()
    assert isinstance(chart_data, list)
    assert all(isinstance(item, dict) and len(item) == 3 for item in chart_data)
    assert all(
        "column-1" in item and "column-2" in item and "date" in item
        for item in chart_data
    )


def test_update_settings(client):
    settings_data = {
        "tolerance": 1,
        "setpoint_min": 1,
        "setpoint_max": 10,
        "setpoint_offset_summer": 140,
        "setpoint_offset_winter": 130.0,
        "mode_change_delta_temp": 3,
        "mode_switch_lockout_time": 30,
        "cascade_time": 5,
    }
    time.sleep(5)
    response = client.post("/api/update_settings", json=settings_data)
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Temperature setpoint set to {settings_data['setpoint_offset_winter']}°F"
    }
