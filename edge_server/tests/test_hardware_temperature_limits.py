import warnings

import pytest
from chronos.app import app
from chronos.config import cfg
from chronos.devices import create_modbus_connection
from fastapi.testclient import TestClient

client = TestClient(app)


def get_current_hardware_limits():
    """Try to retrieve the current hardware temperature limits directly."""
    try:
        with create_modbus_connection() as device:
            limits = device.get_temperature_limits()
            return limits
    except Exception:
        return None


@pytest.fixture(scope="module")
def hardware_state():
    # Skip the test if hardware is not available
    if get_current_hardware_limits() is None:
        pytest.skip("Modbus hardware not available - skipping hardware test")
    # Ensure that hardware tests are executed in non read-only and real device mode
    cfg.READ_ONLY_MODE = False
    cfg.MOCK_DEVICES = False

    # Get the current hardware limits via the API endpoint
    get_resp = client.get("/temperature_limits")
    if get_resp.status_code != 200:
        pytest.skip(f"Failed to GET hardware limits: {get_resp.text}")
    data = get_resp.json()
    original_limits = data.get("soft_limits")
    if not original_limits:
        pytest.skip("Could not retrieve soft_limits from endpoint")

    yield original_limits

    # Teardown: restore the original hardware state
    revert_payload = {
        "min_setpoint": original_limits["min_setpoint"],
        "max_setpoint": original_limits["max_setpoint"],
    }
    revert_resp = client.post("/temperature_limits", json=revert_payload)
    if revert_resp.status_code != 200:
        pytest.fail(f"Failed to revert hardware temperature limits: {revert_resp.text}")


def test_hardware_temperature_limits_update(hardware_state):
    """Test updating temperature limits on hardware and relying on the fixture to restore state afterward."""
    original_limits = hardware_state
    orig_min = original_limits["min_setpoint"]
    orig_max = original_limits["max_setpoint"]

    # Decide on new limits to update, ensuring there's room for change
    if orig_min + 1.0 < orig_max:
        test_min = orig_min + 1.0
        test_max = orig_max - 1.0 if (orig_max - 1.0) > (orig_min + 1.0) else orig_max
    else:
        warnings.warn(
            "Not enough range to alter temperature limits for testing", UserWarning
        )
        pytest.skip("Not enough range to alter temperature limits for testing")

    payload = {"min_setpoint": test_min, "max_setpoint": test_max}

    # Post new temperature limits
    update_resp = client.post("/temperature_limits", json=payload)
    assert update_resp.status_code == 200, f"Update failed: {update_resp.text}"
    assert "Temperature limits updated successfully" in update_resp.json().get(
        "message", ""
    ), "Update message mismatch"

    # Verify the update by fetching the limits
    get_resp_after = client.get("/temperature_limits")
    assert get_resp_after.status_code == 200, (
        f"GET after update failed: {get_resp_after.text}"
    )
    updated_limits = get_resp_after.json().get("soft_limits")
    assert abs(updated_limits["min_setpoint"] - test_min) < 0.001, (
        "min_setpoint not updated correctly"
    )
    assert abs(updated_limits["max_setpoint"] - test_max) < 0.001, (
        "max_setpoint not updated correctly"
    )
