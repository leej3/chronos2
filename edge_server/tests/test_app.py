import logging
import os
import time
from unittest.mock import patch

import pytest
from chronos.app import app
from chronos.config import cfg
from chronos.devices.manager import MockDeviceManager
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)


mock_get_sensor_data = MockDeviceManager().get_sensor_data()
season_mode = MockDeviceManager().season_mode
is_switching_season = MockDeviceManager().is_switching_season

mock_system_status = {
    "sensors": mock_get_sensor_data,
    "mock_devices": True,
    "read_only_mode": False,
    "season_mode": "winter",
    "is_switching_season": False,
}

mock_get_state_of_all_relays = MockDeviceManager().get_state_of_all_relays()

mock_relay_state = MockDeviceManager().get_relay_state(1)

mock_boiler_stats = MockDeviceManager().get_boiler_stats()


mock_operating_status = MockDeviceManager().get_operating_status()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_device_manager():
    with patch("chronos.app.device_manager") as mock:
        yield mock


def test_get_data(client, mock_device_manager):
    mock_device_manager.get_sensor_data.return_value = mock_system_status["sensors"]
    mock_device_manager.season_mode = "winter"
    mock_device_manager.is_switching_season = False
    mock_device_manager.is_mock_mode.return_value = True

    response = client.get("/get_data")
    assert response.status_code == 200
    data = response.json()
    assert data == mock_system_status
    assert "sensors" in data
    assert isinstance(data["sensors"]["water_out_temp"], (int, float))
    assert isinstance(data["sensors"]["return_temp"], (int, float))


def test_get_state_of_all_relays(client, mock_device_manager):
    mock_device_manager.get_state_of_all_relays.return_value = (
        mock_get_state_of_all_relays
    )
    mock_device_manager.is_mock_mode.return_value = True
    response = client.get("/get_state_of_all_relays")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8
    for i in range(len(data)):
        assert data[i]["id"] == mock_get_state_of_all_relays[i]["id"]
        assert data[i]["state"] == mock_get_state_of_all_relays[i]["state"]


def test_get_relay_state(client, mock_device_manager):
    mock_device_manager.get_relay_state.return_value = mock_relay_state

    response = client.get("/device_state?device=1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_relay_state["id"]
    assert data["state"] == mock_relay_state["state"]


def test_get_relay_state_invalid_device_id(client, mock_device_manager):
    response = client.get("/device_state?device=10")
    assert response.status_code == 422


def test_update_device_state(client, mock_device_manager):
    mock_device_manager.set_device_state.return_value = True

    response = client.post(
        "/device_state", json={"id": 2, "state": True, "is_season_switch": False}
    )
    assert response.status_code == 200
    assert response.json() is True


def test_update_device_state_invalid_device_id(client, mock_device_manager):
    response = client.post(
        "/device_state", json={"id": 10, "state": True, "is_season_switch": False}
    )
    assert response.status_code == 422


def test_update_device_state_circuit_breaker(client, mock_device_manager):
    mock_device_manager.set_device_state.return_value = True
    with patch("chronos.app.circuit_breaker.can_execute", return_value=True):
        response = client.post("/device_state", json={"id": 0, "state": True})
        assert response.status_code == 200
        assert response.json() is True


def test_update_device_state_error_circuit_breaker(client, mock_device_manager):
    mock_device_manager.set_device_state.return_value = True
    with patch("chronos.app.circuit_breaker.can_execute", return_value=False):
        response = client.post("/device_state", json={"id": 0, "state": True})
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"]


def test_update_device_state_rate_limiter(client, mock_device_manager):
    mock_device_manager.set_device_state.return_value = True
    with patch("chronos.app.rate_limiter.can_change_specific_relay", return_value=True):
        response = client.post("/device_state", json={"id": 0, "state": True})
        assert response.status_code == 200
        assert response.json() is True


def test_update_device_state_rate_limiter_error(client, mock_device_manager):
    mock_device_manager.set_device_state.return_value = True
    with patch(
        "chronos.app.rate_limiter.can_change_specific_relay", return_value=False
    ):
        response = client.post("/device_state", json={"id": 0, "state": True})
        assert response.status_code == 429
        assert "Too many changes" in response.json()["detail"]


def test_update_device_state_is_season_switch_rate_limiter(client, mock_device_manager):
    time.sleep(5)
    mock_device_manager.set_device_state.return_value = True
    response = client.post("/device_state", json={"id": 1, "state": True})
    assert response.status_code == 200
    assert response.json() is True
    time.sleep(5)

    response2 = client.post("/device_state", json={"id": 2, "state": True})
    assert response2.status_code == 200
    assert response2.json() is True
    time.sleep(5)

    response3 = client.post("/device_state", json={"id": 3, "state": False})
    assert response3.status_code == 200
    assert response3.json() is True
    time.sleep(5)
    response4 = client.post("/device_state", json={"id": 4, "state": True})
    assert response4.status_code == 200
    assert response4.json() is True


def test_update_device_state_is_season_switch_rate_limiter_error(
    client, mock_device_manager
):
    mock_device_manager.set_device_state.return_value = True
    response = client.post("/device_state", json={"id": 1, "state": True})
    assert response.status_code == 200
    assert response.json() is True

    response2 = client.post("/device_state", json={"id": 1, "state": True})
    assert response2.status_code == 429
    assert "Too many changes" in response2.json()["detail"]

    response3 = client.post("/device_state", json={"id": 1, "state": False})
    assert response3.status_code == 429
    assert "Too many changes" in response3.json()["detail"]


def test_update_device_state_read_only(client, mock_device_manager):
    mock_device_manager.set_device_state.return_value = True
    cfg.READ_ONLY_MODE = True
    response = client.post(
        "/device_state", json={"id": 0, "state": True, "is_season_switch": False}
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Operation not permitted: system is in read-only mode"
    )


def test_get_boiler_stats(client, mock_device_manager):
    mock_device_manager.get_boiler_stats.return_value = mock_boiler_stats
    mock_device_manager.is_mock_mode.return_value = True
    response = client.get("/boiler_stats")
    assert response.status_code == 200
    data = response.json()
    assert data["system_supply_temp"] == mock_boiler_stats["system_supply_temp"]
    assert data["flue_temp"] == mock_boiler_stats["flue_temp"]
    assert data["cascade_current_power"] == mock_boiler_stats["cascade_current_power"]
    assert data["lead_firing_rate"] == mock_boiler_stats["lead_firing_rate"]
    assert data["pump_status"] == mock_boiler_stats["pump_status"]
    assert data["flame_status"] == mock_boiler_stats["flame_status"]


def test_get_boiler_status(client, mock_device_manager):
    mock_device_manager.get_operating_status.return_value = mock_operating_status
    mock_device_manager.is_mock_mode.return_value = True
    response = client.get("/boiler_status")
    assert response.status_code == 200
    data = response.json()
    assert data["operating_mode"] == mock_operating_status["operating_mode"]
    assert data["operating_mode_str"] == mock_operating_status["operating_mode_str"]
    assert data["cascade_mode"] == mock_operating_status["cascade_mode"]
    assert data["cascade_mode_str"] == mock_operating_status["cascade_mode_str"]
    assert data["current_setpoint"] == mock_operating_status["current_setpoint"]


def test_set_setpoint(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    mock_device_manager.set_boiler_setpoint.return_value = True
    response = client.post("/boiler_set_setpoint", json={"temperature": 80})
    assert response.status_code == 200
    assert response.json() == {"message": "Temperature setpoint set to 80.0°F"}


def test_set_setpoint_invalid_temperature(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    mock_device_manager.set_boiler_setpoint.return_value = False
    response = client.post("/boiler_set_setpoint", json={"temperature": 180})
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "Input should be less than or equal to 110"
    )


def test_set_setpoint_rate_limiter(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    mock_device_manager.set_boiler_setpoint.return_value = True
    with patch("chronos.app.rate_limiter.can_change", return_value=True):
        response = client.post("/boiler_set_setpoint", json={"temperature": 80})
        assert response.status_code == 200
        assert response.json() == {"message": "Temperature setpoint set to 80.0°F"}


def test_set_setpoint_rate_limiter_error(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    mock_device_manager.set_boiler_setpoint.return_value = True
    with patch("chronos.app.rate_limiter.can_change", return_value=False):
        response = client.post("/boiler_set_setpoint", json={"temperature": 80})
        assert response.status_code == 429
        assert "Too many changes." in response.json()["detail"]


def test_get_temperature_limits(client, mock_device_manager):
    mock_limits = {"min_setpoint": 70, "max_setpoint": 110}
    mock_device_manager.get_temperature_limits.return_value = mock_limits

    response = client.get("/temperature_limits")
    assert response.status_code == 200
    assert "hard_limits" in response.json()
    assert "soft_limits" in response.json()


def test_set_temperature_limits(client, mock_device_manager):
    mock_device_manager.set_temperature_limits.return_value = True

    response = client.post(
        "/temperature_limits", json={"min_setpoint": 70, "max_setpoint": 110}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Temperature limits updated successfully"}


def test_set_temperature_limits_invalid_temperature(client, mock_device_manager):
    mock_device_manager.set_temperature_limits.return_value = False
    response = client.post(
        "/temperature_limits", json={"min_setpoint": 120, "max_setpoint": 180}
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"][0]["msg"]
        == "Input should be less than or equal to 110"
    )


def test_set_temperature_limits_invalid_temperature_type(client, mock_device_manager):
    mock_device_manager.set_temperature_limits.return_value = False
    response = client.post(
        "/temperature_limits", json={"min_setpoint": "70", "max_setpoint": "110"}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "500: Failed to set temperature limits"


def test_set_temperature_limits_read_only(client, mock_device_manager):
    mock_device_manager.set_temperature_limits.return_value = False
    cfg.READ_ONLY_MODE = True
    response = client.post(
        "/temperature_limits", json={"min_setpoint": 70, "max_setpoint": 110}
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Operation not permitted: system is in read-only mode"
    )


def test_download_log(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    response = client.get("/download_log")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="chronos_log.txt"'
    )


def test_download_log_file_not_found(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    log_path = cfg.files.log_path
    os.unlink(log_path)
    response = client.get("/download_log")
    assert response.status_code == 500
    assert "Failed to read log file" in response.json()["detail"]


def test_season_switch(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    response = client.post(
        "/season_switch", json={"season_mode": "winter", "mode_switch_lockout_time": 10}
    )
    assert response.status_code == 200


def test_season_switch_rate_limiter(client, mock_device_manager):
    mock_device_manager.is_mock_mode.return_value = True
    response = client.post(
        "/season_switch", json={"season_mode": "winter", "mode_switch_lockout_time": 10}
    )
    assert response.status_code == 429
    assert "Too many changes" in response.json()["detail"]
