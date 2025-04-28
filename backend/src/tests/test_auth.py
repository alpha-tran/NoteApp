from fastapi.testclient import TestClient
import pytest
import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import DataBase
from schemas.auth import RegisterData
from schemas.user import UserResponse

client = TestClient(app)

@pytest.fixture(autouse=True)
async def setup_database():
    await DataBase.connect_to_mongo()
    db = DataBase.get_mongo_db()
    # Clear the users collection before each test
    await db["users"].delete_many({})
    yield
    # Clean up after each test
    await db["users"].delete_many({})
    await DataBase.close_mongo_connection()

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