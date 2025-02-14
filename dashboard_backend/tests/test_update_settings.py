import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.routers.dashboard_router import router
from src.features.auth.jwt_handler import create_access_token

# Create a FastAPI app instance and include the router
app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for test requests."""
    token = create_access_token({"sub": "test@example.com"})
    return {"Authorization": f"Bearer {token}"}


# Fixture to monkeypatch the edge_server in the dashboard_router
@pytest.fixture
def dummy_edge_server(monkeypatch):
    """A dummy edge server with default behavior."""

    class DummyEdgeServer:
        def get_temperature_limits(self):
            return {
                "hard_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0},
                "soft_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0},
            }

        def set_temperature_limits(self, limits: dict):
            return {"status": "ok"}

    dummy = DummyEdgeServer()
    monkeypatch.setattr("src.api.routers.dashboard_router.edge_server", dummy)
    return dummy


def test_update_settings_success(client, dummy_edge_server, auth_headers):
    # Test a successful settings update when no temperature limits are being updated
    payload = {
        "setpoint_min": None,
        "setpoint_max": None,
        "other_setting": "some_value",
    }
    response = client.post("/update_settings", json=payload, headers=auth_headers)
    # Expect a 200 OK response with a success message
    assert response.status_code == 200
    # Note: success response returns key 'message' which is acceptable for success
    assert response.json().get("message") == "Settings updated successfully"


def test_update_settings_invalid_setpoint_min(client, dummy_edge_server, auth_headers):
    # Test where setpoint_min is below allowed limit
    payload = {"setpoint_min": 60, "setpoint_max": None}  # below min limit (70)
    response = client.post("/update_settings", json=payload, headers=auth_headers)
    assert response.status_code == 400
    # Should return error details under 'detail'
    expected = "Minimum setpoint must be between 70.0°F and 110.0°F"
    assert response.json().get("detail") == expected


def test_update_settings_invalid_setpoint_max(client, dummy_edge_server, auth_headers):
    # Test where setpoint_max is above allowed limit
    payload = {"setpoint_min": None, "setpoint_max": 120}  # above max limit (110)
    response = client.post("/update_settings", json=payload, headers=auth_headers)
    assert response.status_code == 400
    expected = "Maximum setpoint must be between 70.0°F and 110.0°F"
    assert response.json().get("detail") == expected


def test_update_settings_read_only_mode(client, monkeypatch, auth_headers):
    # Simulate read-only mode error by monkeypatching set_temperature_limits to raise an error
    from src.core.common.exceptions import EdgeServerError

    class DummyEdgeServer:
        def get_temperature_limits(self):
            return {"hard_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0}}

        def set_temperature_limits(self, limits: dict):
            raise EdgeServerError(
                "Operation not permitted: system is in read-only mode"
            )

    monkeypatch.setattr(
        "src.api.routers.dashboard_router.edge_server", DummyEdgeServer()
    )

    payload = {"setpoint_min": 75, "setpoint_max": 105}
    response = client.post("/update_settings", json=payload, headers=auth_headers)
    # Expect a 403 Forbidden response with the correct error message
    assert response.status_code == 403
    assert (
        response.json().get("detail")
        == "Operation not permitted: system is in read-only mode"
    )


def test_update_settings_generic_error(client, monkeypatch, auth_headers):
    # Simulate a generic error in updating temperature limits
    from src.core.common.exceptions import EdgeServerError

    class DummyEdgeServer:
        def get_temperature_limits(self):
            return {"hard_limits": {"min_setpoint": 70.0, "max_setpoint": 110.0}}

        def set_temperature_limits(self, limits: dict):
            raise EdgeServerError("Some other error")

    monkeypatch.setattr(
        "src.api.routers.dashboard_router.edge_server", DummyEdgeServer()
    )

    payload = {"setpoint_min": 75, "setpoint_max": 105}
    response = client.post("/update_settings", json=payload, headers=auth_headers)
    # Expect a 400 Bad Request with an error message indicating failure to update temperature limits
    assert response.status_code == 400
    detail = response.json().get("detail")
    assert "Failed to update temperature limits" in detail
    assert "Some other error" in detail
