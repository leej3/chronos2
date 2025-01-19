import unittest
import requests
import sys
import os
import time
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.common.exceptions import (
    ConnectToEdgeServerError,
    EdgeServerError,
    ErrorReadDataEdgeServer,
)
from src.core.services.edge_server import EdgeServer
from unittest.mock import patch

class TestEdgeServer(unittest.TestCase):
    def setUp(self):
        self.edge_server = EdgeServer()

    # @patch("src.core.services.edge_server.requests.get")
    def test_get_data_success(self):
        # mock_data = {
        #     "sensors": {
        #         "return_temp": 32.2,
        #         "water_out_temp": 32.2
        #     },
        #     "devices": [
        #         {"id": 0, "state": True},
        #         {"id": 1, "state": True},
        #         {"id": 2, "state": False},
        #         {"id": 3, "state": False},
        #         {"id": 4, "state": False}
        #     ]
        # }
        # mock_response = MagicMock()
        # mock_response.raise_for_status.return_value = None
        # mock_response.json.return_value = None
        # mock_get.return_value = mock_response
        response = self.edge_server.get_data()
        assert len(response["devices"]) == 5
        assert len(response["sensors"]) == 2
        

    @patch("src.core.services.edge_server.requests.get")
    def test_get_data_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(ConnectToEdgeServerError):
            self.edge_server.get_data()

    @patch("src.core.services.edge_server.requests.get")
    def test_get_data_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Error!")
        mock_get.return_value = mock_response

        with self.assertRaises(EdgeServerError):
            self.edge_server.get_data()

    # @patch("src.core.services.edge_server.requests.get")
    def test_device_state_success(self):
        # mock_response = MagicMock()
        # mock_response.raise_for_status.return_value = None
        # mock_response.json.return_value = {"device": "on"}
        # mock_get.return_value = mock_response
        id = 1 
        response = self.edge_server.device_state(id)
        assert response["id"] == id
        assert response["state"] in [True, False]  
        # self.assertEqual(response, {"device": "on"})
        # mock_get.assert_called_once_with(f"{self.edge_server.url}/device_state", params={"device": "heater"})

    # @patch("src.core.services.edge_server.requests.post")
    def test_update_device_state_success(self):
        
        device = {"id": 1, "state": True}
        time.sleep(5)
        response = self.edge_server.update_device_state(device["id"], device["state"])
        assert response["id"] == device["id"]
        assert response["state"] == device["state"]


    @patch("src.core.services.edge_server.requests.get")
    def test_download_log_success(self,mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"log": "data"}
        mock_get.return_value = mock_response

        response = self.edge_server.download_log()

        self.assertEqual(response, {"log": "data"})
        mock_get.assert_called_once_with(f"{self.edge_server.url}/download_log")

    @patch("src.core.services.edge_server.requests.get")
    def test_download_log_general_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Unexpected error!")
        mock_get.return_value = mock_response

        with self.assertRaises(ErrorReadDataEdgeServer):
            self.edge_server.download_log()

if __name__ == "__main__":
    unittest.main()
