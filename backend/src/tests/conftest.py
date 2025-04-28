import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture
def client():
    """
    Test client fixture that can be used in tests
    """
    return TestClient(app) 