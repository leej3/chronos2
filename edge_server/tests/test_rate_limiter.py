import time

import pytest
from chronos.app import RateLimiter, with_rate_limit
from chronos.data_models import SwitchStateRequest
from fastapi import HTTPException


@pytest.fixture(autouse=True)
def fake_time(monkeypatch):
    # Create a mutable time value that we can control
    current_time = [1000.0]

    def fake_time_func():
        return current_time[0]

    monkeypatch.setattr(time, "time", fake_time_func)
    return current_time


@pytest.mark.asyncio
async def test_rate_limiter_can_change(fake_time):
    rl = RateLimiter(min_interval=5.0, season_interval=2.0)
    # First call should succeed
    assert rl.can_change() == True
    # Immediate second call should fail
    assert rl.can_change() == False
    # Simulate passage of time greater than min_interval
    fake_time[0] += 5.1
    assert rl.can_change() == True


@pytest.mark.asyncio
async def test_rate_limiter_can_season_change(fake_time):
    rl = RateLimiter(min_interval=5.0, season_interval=2.0)
    # First call should succeed
    assert rl.can_season_change() == True
    # Immediate second call should fail
    assert rl.can_season_change() == False
    # Simulate passage of time greater than season_interval
    fake_time[0] += 2.1
    assert rl.can_season_change() == True


# Create a dummy async function decorated with with_rate_limit
def create_dummy_function():
    @with_rate_limit
    async def dummy(data: SwitchStateRequest):
        return data.command

    return dummy


@pytest.mark.asyncio
async def test_with_rate_limit_regular(fake_time):
    dummy = create_dummy_function()
    data = SwitchStateRequest(command="on", is_season_switch=False)
    # First call should pass
    result = await dummy(data)
    assert result == "on"
    # Immediate second call should be rate limited
    with pytest.raises(HTTPException) as excinfo:
        await dummy(data)
    assert excinfo.value.status_code == 429
    assert "Too many relay toggles" in excinfo.value.detail
    # Simulate passage of time to reset rate limiter (5 seconds)
    fake_time[0] += 5.1
    result = await dummy(data)
    assert result == "on"


@pytest.mark.asyncio
async def test_with_rate_limit_season(fake_time):
    dummy = create_dummy_function()
    season_data = SwitchStateRequest(command="switch-season", is_season_switch=True)
    # First call should pass
    result = await dummy(season_data)
    assert result == "switch-season"
    # Immediate second call should also pass (no rate limiting for season switches)
    result = await dummy(season_data)
    assert result == "switch-season"
    # Third call should also pass
    result = await dummy(season_data)
    assert result == "switch-season"


@pytest.mark.asyncio
async def test_with_rate_limit_mixed_modes(fake_time):
    dummy = create_dummy_function()
    # Test that season switch and regular changes use different rate limiters
    season_data = SwitchStateRequest(command="switch-season", is_season_switch=True)
    regular_data = SwitchStateRequest(command="on", is_season_switch=False)

    # First season switch should work
    result = await dummy(season_data)
    assert result == "switch-season"

    # Regular relay toggle should work
    result = await dummy(regular_data)
    assert result == "on"

    # Second season switch should work (no rate limiting)
    result = await dummy(season_data)
    assert result == "switch-season"

    # Second regular toggle should fail (rate limited)
    with pytest.raises(HTTPException) as excinfo:
        await dummy(regular_data)
    assert excinfo.value.status_code == 429
    assert "Too many relay toggles" in excinfo.value.detail

    # Wait for regular interval (5.1s)
    fake_time[0] += 5.1
    # Regular toggle should work again
    result = await dummy(regular_data)
    assert result == "on"
