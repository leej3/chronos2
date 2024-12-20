import requests
from src.core.common.exceptions import EdgeServerError, ErrorReadDataEdgeServer
from src.core.configs.config import settings


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
            raise EdgeServerError()
        except Exception as e:
            raise ErrorReadDataEdgeServer()

    def get_data(self):
        response = requests.get(f"{self.url}/")
        return self._handle_response(response)

    def device_state(self, device):
        response = requests.get(f"{self.url}/device_state", params={"device": device})
        return self._handle_response(response)

    def update_device_state(self, device, state):
        response = requests.post(
            f"{self.url}/device_state", data={"id": device, state: state}
        )
        return self._handle_response(response)

    def download_log(self):
        response = requests.get(f"{self.url}/download_log")
        return self._handle_response(response)
