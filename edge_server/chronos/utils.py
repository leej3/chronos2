import time
from functools import wraps
from typing import Callable

from chronos.config import cfg
from chronos.logging import root_logger as logger
from fastapi import HTTPException


# Circuit breaker states and configuration
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self.is_open = False

    def record_failure(self):
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("Circuit breaker opened due to multiple failures")

    def record_success(self):
        """Record a success and reset failure count."""
        self.failure_count = 0
        self.is_open = False

    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if not self.is_open:
            return True

        # Check if enough time has passed to try again
        if time.time() - self.last_failure_time >= self.reset_timeout:
            logger.info("Circuit breaker reset timeout reached, allowing retry")
            self.is_open = False
            self.failure_count = 0
            return True

        return False


# Rate limiter for temperature changes
class RateLimiter:
    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self.last_change_times = {}  # Store last change time for each relay

    def can_change(self, relay_id) -> bool:
        """Check if enough time has passed since last change for a specific relay."""
        current_time = time.time()
        last_change_time = self.last_change_times.get(relay_id, 0)

        if current_time - last_change_time >= self.min_interval:
            self.last_change_times[relay_id] = current_time
            return True
        return False


# Decorator for circuit breaker pattern
def with_circuit_breaker(cb):
    """Decorator that applies circuit breaker pattern to a function.

    Args:
        cb: A CircuitBreaker instance to use for this function.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cb.can_execute():
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable due to multiple failures. Please try again later.",
                )

            try:
                result = await func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception:
                cb.record_failure()
                raise

        return wrapper

    return decorator


# Decorator for rate limiting
def with_rate_limit(rl):
    """Decorator that applies rate limiting to a function.

    Args:
        rl: A RateLimiter instance to use for this function.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            data = kwargs.get("data") if "data" in kwargs else args[0] if args else None

            # Check if it's a season switch
            if getattr(data, "is_season_switch", False):
                return await func(*args, **kwargs)

            # Extract relay_id and ensure it's provided
            relay_id = getattr(data, "id", None)
            if relay_id is None:
                raise ValueError("Relay ID must be provided for rate limiting.")

            # Apply rate limiting for the specific relay
            if not rl.can_change(relay_id):
                relay_name = cfg.relay_names.__dict__.get(str(relay_id), "unknown")
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many changes for relay {relay_name}. Please wait before trying again.",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
