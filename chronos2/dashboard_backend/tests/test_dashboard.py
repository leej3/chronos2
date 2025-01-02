import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app  
from unittest.mock import MagicMock
from src.features.dashboard.dashboard_service import DashboardService
from src.core.services.edge_server import EdgeServer
from src.core.chronos import Chronos
from src.features.auth.jwt_handler import UserToken
from src.api.dependencies import get_current_user


@pytest.fixture
def mock_dashboard_service():
    mock = MagicMock(DashboardService)
    mock.get_data.return_value = {"key": "value"}
    mock.get_chart_data.return_value = {"chart_key": "chart_value"}
    mock.log_generator.return_value = iter(["log_line_1", "log_line_2"])
    return mock

@pytest.fixture
def mock_edge_server():
    mock = MagicMock(EdgeServer)
    mock.update_device_state.return_value = None
    return mock

@pytest.fixture
def mock_chronos():
    mock = MagicMock(Chronos)
    mock.some_setting = "test"
    return mock

@pytest.fixture
def mock_current_user():
    return UserToken(sub="test_user", email="admin@gmail.com")

@pytest.fixture
def client(mock_dashboard_service, mock_edge_server, mock_chronos):
    app.dependency_overrides[DashboardService] = lambda: mock_dashboard_service
    app.dependency_overrides[EdgeServer] = lambda: mock_edge_server
    app.dependency_overrides[Chronos] = lambda: mock_chronos
    app.dependency_overrides[get_current_user] = lambda: mock_current_user

    return TestClient(app)


def test_dashboard_data(client):
    response = client.get("api/")
    data = response.json()
    assert response.status_code == 200
    assert 'sensors' in data
    assert 'devices' in data
    assert 'results' in data
    assert 'efficiency' in data

    assert 'return_temp' in data['sensors']
    assert 'water_out_temp' in data['sensors']

    assert isinstance(data['devices'], list)
    assert all('id' in device and 'state' in device for device in data['devices'])

    assert 'outside_temp' in data['results']
    assert 'baseline_setpoint' in data['results']
    assert 'setpoint_min' in data['results']
    assert 'setpoint_max' in data['results']

    assert 'average_temperature_difference' in data['efficiency']
    assert 'chillers_efficiency' in data['efficiency']
    assert 'hours' in data['efficiency']

    assert isinstance(data['sensors']['return_temp'], (int, float))
    assert isinstance(data['sensors']['water_out_temp'], (int, float))
    assert isinstance(data['results']['outside_temp'], (int, float))
    assert isinstance(data['efficiency']['average_temperature_difference'], (int, float))
    assert isinstance(data['efficiency']['hours'], int)


def test_update_device_state(client):
    update_data = {"id": 1, "state": "on"}
    response = client.post("/api/update_device_state", json=update_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Updated state successfully"}


def test_download_log(client):
    response = client.get("/api/download_log")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=exported-data.csv"
    content = list(response.iter_lines())    
    assert len(content) > 1




def test_chart_data(client):
    response = client.get("/api/chart_data")
    assert response.status_code == 200
    chart_data = response.json()
    assert isinstance(chart_data, list) 
    assert all(isinstance(item, dict) and len(item) == 3 for item in chart_data)
    assert all('column-1' in item and 'column-2' in item and 'date' in item for item in chart_data)



def test_update_settings(client):
    settings_data = {
        "tolerance": 0,
        "setpoint_min": 0,
        "setpoint_max": 0,
        "setpoint_offset_summer": 0,
        "setpoint_offset_winter": 0,
        "mode_change_delta_temp": 0,
        "mode_switch_lockout_time": 0,
        "cascade_time": 0
    }
    
    response = client.post("/api/update_settings", json=settings_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Updated settings successfully"}

