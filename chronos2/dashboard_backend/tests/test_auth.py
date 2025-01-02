import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app  
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def refresh_token(client):
    login_data = {
        "email": "admin@gmail.com",
        "password": "Aa123456@",
    }

    response = client.post("/api/auth/login", json=login_data)
    tokens = response.json().get('tokens', {})  

    assert response.status_code == 200
    json_data = response.json()
    assert 'tokens' in json_data  
    assert 'access' in tokens 
    assert 'refresh' in tokens 
    refresh_token = tokens.get('refresh')
    return refresh_token

def test_refresh_token_endpoint(client, refresh_token):
    refresh_token_data = {
        "refresh_token": refresh_token,
    }

    response = client.post("/api/auth/token/refresh", json=refresh_token_data)

    assert response.status_code == 200
    json_data = response.json()
    assert "tokens" in json_data
    assert "access" in json_data["tokens"]  
    assert "refresh" in json_data["tokens"] 
