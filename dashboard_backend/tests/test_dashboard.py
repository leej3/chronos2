import os
import sys
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from unittest.mock import MagicMock

from main import app
from src.api.dependencies import get_current_user
from src.core.common.exceptions import EdgeServerError
from src.core.services.chronos import Chronos
from src.core.services.edge_server import EdgeServer
from src.features.auth.jwt_handler import UserToken
from src.features.dashboard.dashboard_service import DashboardService


@pytest.fixture(autouse=True)
def setup_env():
    """Set up test environment variables."""
    os.environ["READ_ONLY_MODE"] = "false"
    yield
    # Clean up
    if "READ_ONLY_MODE" in os.environ:
        del os.environ["READ_ONLY_MODE"]


@pytest.fixture
def mock_dashboard_service():
    mock = MagicMock(DashboardService)
    mock.get_data.return_value = {"key": "value"}
    mock.get_chart_data.return_value = {"chart_key": "chart_value"}
    mock.log_generator.return_value = iter(["log_line_1", "log_line_2"])
    return mock


@pytest.fixture
def mock_edge_server(monkeypatch):
    """Create a dummy edge server for testing."""

    class DummyEdgeServer:
        def get_temperature_limits(self):
            return {
                "hard_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0},
                "soft_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0},
            }

        def set_temperature_limits(self, limits: dict):
            # This will be overridden in specific tests
            return {"status": "ok"}

        def update_device_state(self, *args, **kwargs):
            return None

    dummy = DummyEdgeServer()
    monkeypatch.setattr("src.api.routers.dashboard_router.EdgeServer", lambda: dummy)
    return dummy


@pytest.fixture
def mock_chronos():
    mock = MagicMock(Chronos)
    mock.some_setting = "test"
    return mock


@pytest.fixture
def mock_current_user():
    return UserToken(user_id="test_user", sub="test_user", email="admin@gmail.com")


@pytest.fixture
def client(mock_dashboard_service, mock_edge_server, mock_chronos, mock_current_user):
    app.dependency_overrides[DashboardService] = lambda: mock_dashboard_service
    app.dependency_overrides[EdgeServer] = lambda: mock_edge_server
    app.dependency_overrides[Chronos] = lambda: mock_chronos
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    return TestClient(app)


@pytest.fixture
def mock_switch_season_response():
    current_time = datetime.now()
    unlock_time = current_time + timedelta(minutes=2)
    return {
        "message": "Switched to Winter mode successfully",
        "status": "success",
        "mode": 0,
        "mode_switch_timestamp": current_time.isoformat(),
        "mode_switch_lockout_time": 2,
        "unlock_time": unlock_time.isoformat(),
    }


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


def test_update_settings(client, mock_edge_server):
    settings_data = {
        "tolerance": 1,
        "setpoint_min": 75,  # Within valid range
        "setpoint_max": 105,  # Within valid range
        "setpoint_offset_summer": 140,
        "setpoint_offset_winter": 130.0,
        "mode_change_delta_temp": 3,
        "mode_switch_lockout_time": 30,
        "cascade_time": 5,
    }

    # Test successful update
    response = client.post("/api/update_settings", json=settings_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Settings updated successfully"}

    # Test read-only mode error
    def raise_read_only_error(*args, **kwargs):
        raise EdgeServerError("Operation not permitted: system is in read-only mode")

    mock_edge_server.set_temperature_limits = raise_read_only_error
    response = client.post("/api/update_settings", json=settings_data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Operation not permitted: system is in read-only mode"
    }


# def test_switch_season(client, mock_dashboard_service, mock_switch_season_response):
#     # Setup mock
#     mock_dashboard_service.switch_season_mode.return_value = mock_switch_season_response

#     # Test switching to Winter mode
#     response = client.post("/api/switch-season", json={"season_value": 0})
#     assert response.status_code == 200
#     assert response.json()["status"] == "success"
#     assert response.json()["mode"] == 0
#     assert "unlock_time" in response.json()
#     assert "mode_switch_lockout_time" in response.json()

#     # Test invalid season value
#     response = client.post("/api/switch-season", json={"season_value": 3})
#     assert response.status_code == 400
#     assert "error" in response.json()["status"]


def test_get_data_with_lockout(client, mock_dashboard_service):
    current_time = datetime.now()
    mock_response = {
        "results": {
            "mode": 0,
            "lockout_info": {
                "mode_switch_timestamp": current_time.isoformat(),
                "mode_switch_lockout_time": 2,
                "unlock_time": (current_time + timedelta(minutes=2)).isoformat(),
            },
        }
    }
    mock_dashboard_service.get_data.return_value = mock_response

    response = client.get("/api/")
    assert response.status_code == 200
    assert "lockout_info" in response.json()["results"]
