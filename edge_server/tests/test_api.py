import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.constants import MODES, TEMP_LIMITS, COMPONENTS, COMPONENT_GROUPS

client = TestClient(app)

def test_get_state():
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert "temperatures" in data
    assert "mode" in data
    assert len(data["components"]) == len(COMPONENTS)

def test_get_mode():
    response = client.get("/api/mode")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert data["mode"] in MODES

def test_set_mode_valid():
    response = client.post("/api/mode", json={"mode": "COOLING"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["mode"] == "COOLING"

def test_set_mode_invalid():
    response = client.post("/api/mode", json={"mode": "INVALID"})
    assert response.status_code == 400

def test_get_components():
    response = client.get("/api/components")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    components = data["components"]
    assert len(components) == len(COMPONENTS)
    for component in components:
        assert "id" in component
        assert "type" in component
        assert "status" in component

def test_get_component_groups():
    response = client.get("/api/components/groups")
    assert response.status_code == 200
    data = response.json()
    assert "groups" in data
    assert set(data["groups"]) == set(COMPONENT_GROUPS.keys())

@pytest.mark.parametrize("group_id", COMPONENT_GROUPS.keys())
def test_update_component_group_valid(group_id):
    response = client.post(f"/api/components/group/{group_id}", json=True)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["group"] == group_id
    assert len(data["components"]) == len(COMPONENT_GROUPS[group_id])

def test_update_component_group_invalid():
    response = client.post("/api/components/group/invalid", json=True)
    assert response.status_code == 400

@pytest.mark.parametrize("component_id", [comp['id'] for comp in COMPONENTS.values()])
def test_update_component_valid(component_id):
    response = client.post(f"/api/components/{component_id}", json={"status": True})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["component_id"] == component_id
    assert data["active"] is True

def test_update_component_invalid():
    response = client.post("/api/components/invalid_id", json={"status": True})
    assert response.status_code == 400

def test_get_temperature():
    response = client.get("/api/temperature")
    assert response.status_code == 200
    data = response.json()
    assert "temperatures" in data
    temps = data["temperatures"]
    assert "temp_1" in temps
    assert "temp_2" in temps

def test_set_temperature_valid():
    temp = (TEMP_LIMITS["MIN"] + TEMP_LIMITS["MAX"]) / 2
    response = client.post("/api/temperature", json={"temperature": temp})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["temperature"] == temp

def test_set_temperature_invalid():
    temp = TEMP_LIMITS["MIN"] - 1
    response = client.post("/api/temperature", json={"temperature": temp})
    assert response.status_code == 400

def test_get_logs():
    response = client.get("/api/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)