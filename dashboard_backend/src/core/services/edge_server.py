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
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            msg = f"Failure when get data in Edge server. Detail error: {e}"
            if response.status_code == 422:
                logger.error(
                    f"Validation error response from edge server: {response.text}"
                )
            raise EdgeServerError(message=msg)
        except Exception:
            raise ErrorReadDataEdgeServer()

    @catch_connection_error
    def get_data(self):
        response = requests.get(f"{self.url}/get_data")
        return self._handle_response(response)

    @catch_connection_error
    def device_state(self, device):
        response = requests.get(f"{self.url}/device_state", params={"device": device})
        return self._handle_response(response)

    @catch_connection_error
    def update_device_state(self, id: int, state: bool):
        data = {"id": id, "state": state}
        response = requests.post(f"{self.url}/device_state", data=json.dumps(data))
        return self._handle_response(response)

    @catch_connection_error
    def download_log(self):
        response = requests.get(f"{self.url}/download_log")
        return self._handle_response(response)

    @catch_connection_error
    def get_data_boiler_stats(self):
        response = requests.get(f"{self.url}/boiler_stats")
        return self._handle_response(response)

    @catch_connection_error
    def get_boiler_status(self):
        response = requests.get(f"{self.url}/boiler_status")
        return self._handle_response(response)

    @catch_connection_error
    def boiler_set_setpoint(self, temperature):
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
