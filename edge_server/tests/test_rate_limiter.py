import asyncio
import time
from dataclasses import dataclass
from typing import Optional

import pytest
from chronos.app import RateLimiter, with_rate_limit
from fastapi import HTTPException


@pytest.fixture
def rate_limiter():
    """Fixture to provide a fresh rate limiter instance for each test"""
    return RateLimiter(min_interval=1.0)


@dataclass
class MockRequest:
    """Mock request object to simulate FastAPI request data"""

    is_season_switch: bool = False
    temperature: Optional[float] = None


class TestRateLimiter:
    """Test suite for RateLimiter class"""

    def test_initialization_default_values(self):
        """Test RateLimiter initializes with correct default values"""
        limiter = RateLimiter()
        assert limiter.min_interval == 1.0
        assert limiter.last_change_time == 0

    def test_initialization_custom_values(self):
        """Test RateLimiter initializes with custom values"""
        custom_interval = 10.0
        limiter = RateLimiter(min_interval=custom_interval)
        assert limiter.min_interval == custom_interval
        assert limiter.last_change_time == 0

    def test_can_change_basic_flow(self, rate_limiter):
        """Test the basic flow of can_change method"""
        # First call should succeed
        assert rate_limiter.can_change() is True
        initial_time = rate_limiter.last_change_time
        assert initial_time > 0

        # Immediate second call should fail
        assert rate_limiter.can_change() is False
        # Verify last_change_time wasn't updated
        assert rate_limiter.last_change_time == initial_time

    def test_can_change_after_interval(self, rate_limiter):
        """Test can_change allows changes after interval"""
        assert rate_limiter.can_change() is True
        time.sleep(1.1)  # Sleep slightly longer than min_interval
        assert rate_limiter.can_change() is True


async def rate_limited_test_function(data=None):
    """Function to be tested with rate limiting"""
    return "success"


class TestRateLimitDecorator:
    """Test suite for with_rate_limit decorator"""

    def test_basic_rate_limiting(self):
        """Test basic rate limiting functionality"""

        # Apply the decorator to the function
        decorated_function = with_rate_limit(rate_limited_test_function)

        # Run the coroutine in an event loop
        loop = asyncio.get_event_loop()

        # First call should succeed
        assert loop.run_until_complete(decorated_function()) == "success"

        # Immediate second call should fail
        with pytest.raises(HTTPException) as exc_info:
            loop.run_until_complete(decorated_function())
        assert exc_info.value.status_code == 429
        assert "Too many temperature changes" in exc_info.value.detail

    def test_season_switch_bypass(self):
        """Test that season switch requests bypass rate limiting"""

        # Apply the decorator to the function
        decorated_function = with_rate_limit(rate_limited_test_function)

        # Regular request should be rate limited
        regular_request = MockRequest(is_season_switch=False)
        season_switch_request = MockRequest(is_season_switch=True)

        # Run the coroutine in an event loop
        loop = asyncio.get_event_loop()

        # First regular request succeeds
        assert loop.run_until_complete(decorated_function(regular_request)) == "success"

        # Second regular request fails
        with pytest.raises(HTTPException):
            loop.run_until_complete(decorated_function(regular_request))

        # Season switch request should bypass rate limiting
        assert (
            loop.run_until_complete(decorated_function(season_switch_request))
            == "success"
        )
        assert (
            loop.run_until_complete(decorated_function(season_switch_request))
            == "success"
        )

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""

        # Apply the decorator to the function
        decorated_function = with_rate_limit(rate_limited_test_function)

        # Simulate multiple concurrent calls
        task_count = 5
        results = []

        # Run the coroutine in an event loop
        loop = asyncio.get_event_loop()

        for _ in range(task_count):
            try:
                results.append(loop.run_until_complete(decorated_function()))
            except HTTPException as e:
                results.append(e)

        # Verify exactly one success and rest failures
        success_count = sum(1 for r in results if r == "success")
        error_count = sum(
            1 for r in results if isinstance(r, HTTPException) and r.status_code == 429
        )

        assert success_count == 1
        assert error_count == task_count - 1

    def test_error_handling(self):
        """Test that decorator properly handles errors from wrapped function"""

        async def failing_function():
            raise ValueError("Test error")

        # Apply the decorator to the function
        decorated_function = with_rate_limit(failing_function)

        # Run the coroutine in an event loop
        loop = asyncio.get_event_loop()

        # First call should raise the original error
        with pytest.raises(ValueError) as exc_info:
            loop.run_until_complete(decorated_function())
        assert str(exc_info.value) == "Test error"

        # Second call should still be rate limited
        with pytest.raises(HTTPException) as exc_info:
            loop.run_until_complete(decorated_function())
        assert exc_info.value.status_code == 429
