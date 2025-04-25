from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

def test_register_duplicate_email():
    # First registration
    client.post(
        "/auth/register",
        json={
            "username": "testuser1",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    # Second registration with same email
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser2",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400

def test_login_success():
    # Register user first
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    # Login
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    # Register user first
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    # Login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

def test_get_current_user():
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    login_response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser" 