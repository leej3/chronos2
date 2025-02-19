import json
import logging
from functools import wraps

import requests
from src.core.common.exceptions import (
    ConnectToEdgeServerError,
    EdgeServerError,
    ErrorReadDataEdgeServer,
)
from src.core.configs.config import settings

logger = logging.getLogger(__name__)


def catch_connection_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            raise ConnectToEdgeServerError()

    return wrapper


class EdgeServer:
    def __init__(self):
        self.ip_address = settings.EDGE_SERVER_IP
        self.port = settings.EDGE_SERVER_PORT
        self.url = f"{self.ip_address}:{self.port}"

    def _handle_response(self, response):
        """Handle response from edge server."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if (
                response.status_code == 403
                and "read-only mode" in response.text.lower()
            ):
                msg = "Operation not permitted: system is in read-only mode"
            elif response.status_code == 422:
                logger.error(
                    f"Validation error response from edge server: {response.text}"
                )
                msg = response.json().get("detail", str(e))
            else:
                msg = response.json().get("detail", str(e))
            raise EdgeServerError(message=msg)
        except Exception:
            raise ErrorReadDataEdgeServer()

    @catch_connection_error
    def get_data(self):
        """Get data from edge server."""
        response = requests.get(f"{self.url}/get_data")
        return self._handle_response(response)

    @catch_connection_error
    def device_state(self, device):
        response = requests.get(f"{self.url}/device_state", params={"device": device})
        return self._handle_response(response)

    @catch_connection_error
    def update_device_state(self, id: int, state: bool):
        """Update device state."""
        data = {"id": id, "state": state}
        response = requests.post(f"{self.url}/device_state", data=json.dumps(data))
        return self._handle_response(response)

    @catch_connection_error
    def download_log(self):
        response = requests.get(f"{self.url}/download_log")
        return self._handle_response(response)

    @catch_connection_error
    def get_data_boiler_stats(self):
        """Get boiler statistics."""
        response = requests.get(f"{self.url}/boiler_stats")
        return self._handle_response(response)

    @catch_connection_error
    def get_boiler_status(self):
        """Get boiler status."""
        response = requests.get(f"{self.url}/boiler_status")
        return self._handle_response(response)

    @catch_connection_error
    def get_boiler_errors(self):
        """Get boiler errors."""
        response = requests.get(f"{self.url}/boiler_errors")
        return self._handle_response(response)

    @catch_connection_error
    def get_boiler_info(self):
        """Get boiler information."""
        response = requests.get(f"{self.url}/boiler_info")
        return self._handle_response(response)

    @catch_connection_error
    def get_temperature_limits(self):
        """Get temperature limits."""
        response = requests.get(f"{self.url}/temperature_limits")
        return self._handle_response(response)

    @catch_connection_error
    def set_temperature_limits(self, limits: dict):
        """Set temperature limits."""
        response = requests.post(f"{self.url}/temperature_limits", json=limits)
        return self._handle_response(response)

    @catch_connection_error
    def boiler_set_setpoint(self, temperature: float) -> bool:
        """Set boiler temperature setpoint."""
        logger.info(f"Sending temperature setpoint to edge server: {temperature}")
        data = {"temperature": temperature}
        logger.info(f"Request payload: {data}")
        response = requests.post(
            f"{self.url}/boiler_set_setpoint",
            json=data,  # Use json parameter instead of manually serializing
        )
        logger.info(f"Edge server response status: {response.status_code}")
        logger.info(f"Edge server response body: {response.text}")
        return self._handle_response(response)

    @catch_connection_error
    def _switch_state(self, command, relay_only=False):
        response = requests.post(
            f"{self.url}/switch_state",
            json={
                "command": command,
                "relay_only": relay_only,
                "is_season_switch": command == "switch-season",
            },
        )
        return self._handle_response(response)
