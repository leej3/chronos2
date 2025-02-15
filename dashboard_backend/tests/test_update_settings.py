import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.dependencies import get_current_user
from src.api.routers.dashboard_router import router
from src.core.common.exceptions import EdgeServerError
from src.core.services.chronos import Chronos
from src.core.services.edge_server import EdgeServer
from src.features.auth.jwt_handler import UserToken, create_access_token

# Create a FastAPI app instance and include the router
app = FastAPI()
app.include_router(router, prefix="/api")


@pytest.fixture(autouse=True)
def setup_env():
    """Set up test environment variables."""
    os.environ["READ_ONLY_MODE"] = "false"
    yield
    # Clean up
    if "READ_ONLY_MODE" in os.environ:
        del os.environ["READ_ONLY_MODE"]


@pytest.fixture
def mock_chronos():
    mock = Chronos()
    return mock


@pytest.fixture
def mock_current_user():
    return UserToken(user_id="test_user", sub="test_user", email="admin@gmail.com")


@pytest.fixture
def client(dummy_edge_server, mock_chronos, mock_current_user):
    app.dependency_overrides[EdgeServer] = lambda: dummy_edge_server
    app.dependency_overrides[Chronos] = lambda: mock_chronos
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for test requests."""
    token = create_access_token(
        UserToken(user_id="test_user", sub="test@example.com", email="test@example.com")
    )
    return {"Authorization": f"Bearer {token}"}


# Fixture to monkeypatch the edge_server in the dashboard_router
@pytest.fixture
def dummy_edge_server(monkeypatch):
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

    dummy = DummyEdgeServer()
    monkeypatch.setattr("src.api.routers.dashboard_router.EdgeServer", lambda: dummy)
    return dummy


def test_update_settings(client, dummy_edge_server):
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
    def raise_read_only_error(limits):
        raise EdgeServerError("Operation not permitted: system is in read-only mode")

    dummy_edge_server.set_temperature_limits = raise_read_only_error
    response = client.post("/api/update_settings", json=settings_data)
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Operation not permitted: system is in read-only mode"
    )


def test_update_settings_invalid_setpoint_min(client, dummy_edge_server, auth_headers):
    # Test where setpoint_min is below allowed limit
    payload = {
        "setpoint_min": 60,  # below min limit (70)
        "setpoint_max": None,
        "tolerance": 1.0,
        "setpoint_offset_summer": 140.0,
        "setpoint_offset_winter": 130.0,
        "mode_change_delta_temp": 3.0,
        "mode_switch_lockout_time": 30,
        "cascade_time": 5,
    }
    response = client.post("/api/update_settings", json=payload, headers=auth_headers)
    assert response.status_code == 400
    # Should return error details under 'detail'
    expected = "Minimum setpoint must be between 70.0°F and 110.0°F"
    assert response.json().get("detail") == expected


def test_update_settings_invalid_setpoint_max(client, dummy_edge_server, auth_headers):
    # Test where setpoint_max is above allowed limit
    payload = {
        "setpoint_min": None,
        "setpoint_max": 120,  # above max limit (110)
        "tolerance": 1.0,
        "setpoint_offset_summer": 140.0,
        "setpoint_offset_winter": 130.0,
        "mode_change_delta_temp": 3.0,
        "mode_switch_lockout_time": 30,
        "cascade_time": 5,
    }
    response = client.post("/api/update_settings", json=payload, headers=auth_headers)
    assert response.status_code == 400
    expected = "Maximum setpoint must be between 70.0°F and 110.0°F"
    assert response.json().get("detail") == expected


def test_update_settings_read_only_mode(client, dummy_edge_server, auth_headers):
    # Simulate read-only mode error by modifying the dummy_edge_server
    def raise_read_only_error(*args, **kwargs):
        raise EdgeServerError("Operation not permitted: system is in read-only mode")

    dummy_edge_server.set_temperature_limits = raise_read_only_error

    payload = {
        "setpoint_min": 75,
        "setpoint_max": 105,
        "tolerance": 1.0,
        "setpoint_offset_summer": 140.0,
        "setpoint_offset_winter": 130.0,
        "mode_change_delta_temp": 3.0,
        "mode_switch_lockout_time": 30,
        "cascade_time": 5,
    }
    response = client.post("/api/update_settings", json=payload, headers=auth_headers)
    # Expect a 403 Forbidden response with the correct error message
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Operation not permitted: system is in read-only mode"
    }


def test_update_settings_generic_error(client, dummy_edge_server, auth_headers):
    # Simulate a generic error in updating temperature limits
    def raise_generic_error(*args, **kwargs):
        raise EdgeServerError("Some other error")

    dummy_edge_server.set_temperature_limits = raise_generic_error

    payload = {
        "setpoint_min": 75,
        "setpoint_max": 105,
        "tolerance": 1.0,
        "setpoint_offset_summer": 140.0,
        "setpoint_offset_winter": 130.0,
        "mode_change_delta_temp": 3.0,
        "mode_switch_lockout_time": 30,
        "cascade_time": 5,
    }
    response = client.post("/api/update_settings", json=payload, headers=auth_headers)
    # Expect a 400 Bad Request with an error message indicating failure to update temperature limits
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Failed to update temperature limits: Some other error"
    }
