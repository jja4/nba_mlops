from fastapi.testclient import TestClient
from api.nba_app import app
import requests

client = TestClient(app)

def test_root_endpoint():
    """
    Test the root endpoint of the NBA prediction API.

    This test checks if the root endpoint returns the expected message.

    Returns:
        None
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the NBA prediction API!"}



