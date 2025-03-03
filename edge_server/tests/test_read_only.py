import pytest
from chronos.app import app
from chronos.config import cfg
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def set_read_only_mode(monkeypatch):
    # Force read-only mode for testing
    monkeypatch.setenv("READ_ONLY_MODE", "true")
    cfg.READ_ONLY_MODE = True
    yield
    cfg.READ_ONLY_MODE = False


def test_update_device_state_blocked():
    # Attempt to update device state, which should be blocked
    payload = {"id": 0, "state": True}
    response = client.post("/device_state", json=payload)
    assert response.status_code == 403
    assert "Operation not permitted" in response.json().get("detail", "")


def test_set_setpoint_blocked(client):
    """Test that setting setpoint is blocked in read-only mode."""
    cfg.READ_ONLY_MODE = True
    cfg.MOCK_DEVICES = True
    try:
        # Attempt to update boiler setpoint, which should be blocked
        payload = {"temperature": 75.0}  # Valid temperature between 70.0°F and 110.0°F
        response = client.post("/boiler_set_setpoint", json=payload)
        assert response.status_code == 403
        assert (
            "Operation not permitted: system is in read-only mode"
            in response.json()["detail"]
        )
    finally:
        cfg.READ_ONLY_MODE = False
        cfg.MOCK_DEVICES = False


def test_temperature_limits_blocked():
    # Attempt to update temperature limits, which should be blocked
    payload = {"min_setpoint": 70.0, "max_setpoint": 90.0}
    response = client.post("/temperature_limits", json=payload)
    assert response.status_code == 403
    assert "Operation not permitted" in response.json().get("detail", "")


def test_write_operations_blocked(client):
    """Test that all write operations are blocked in read-only mode."""
    cfg.READ_ONLY_MODE = True
    cfg.MOCK_DEVICES = True
    try:
        # Test setting temperature limits
        response = client.post(
            "/temperature_limits",
            json={"min_setpoint": 75.0, "max_setpoint": 105.0},
        )
        assert response.status_code == 403
        assert (
            "Operation not permitted: system is in read-only mode"
            in response.json()["detail"]
        )

        # Test setting device state
        response = client.post("/device_state", json={"id": 0, "state": True})
        assert response.status_code == 403
        assert (
            "Operation not permitted: system is in read-only mode"
            in response.json()["detail"]
        )
    finally:
        cfg.READ_ONLY_MODE = False
        cfg.MOCK_DEVICES = False
