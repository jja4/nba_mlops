import os
import sys
from fastapi.testclient import TestClient
from api.nba_app import app, lifespan
import pytest
import asyncio
from unittest.mock import Mock, patch
import requests_mock

test_client = TestClient(app)

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Create a new event loop for running async functions
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Run the lifespan event before tests
@pytest.fixture(scope="module", autouse=True)
async def run_lifespan():
    async with lifespan(app):
        yield

# Create a test client
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def get_token(client: TestClient) -> str:
    login_data = {
        "grant_type": "",
        "username": "johndoe",
        "password": "secret",
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "accept": "application/json"
    }
    response = client.post("/login", data=login_data, headers=headers)
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the NBA prediction API!"}

def test_predict_endpoint_shot_made(client: TestClient):
    data = {
        "Period": -0.4,
        "Minutes_Remaining": 1.4,
        "Seconds_Remaining": -1.3,
        "Shot_Distance": 0.3,
        "X_Location": 0.6,
        "Y_Location": 0.8,
        "Action_Type_Frequency": 0.5,
        "Team_Name_Frequency": 0.5,
        "Home_Team_Frequency": 0.4,
        "Away_Team_Frequency": 0.6,
        "ShotType_2PT_Field_Goal": 1,
        "ShotType_3PT_Field_Goal": 0,
        "ShotZoneBasic_Above_the_Break_3": 0,
        "ShotZoneBasic_Backcourt": 0,
        "ShotZoneBasic_In_The_Paint_Non_RA": 0,
        "ShotZoneBasic_Left_Corner_3": 0,
        "ShotZoneBasic_Mid_Range": 0,
        "ShotZoneBasic_Restricted_Area": 1,
        "ShotZoneBasic_Right_Corner_3": 0,
        "ShotZoneArea_Back_Court_BC": 1,
        "ShotZoneArea_Center_C": 0,
        "ShotZoneArea_Left_Side_Center_LC": 0,
        "ShotZoneArea_Left_Side_L": 0,
        "ShotZoneArea_Right_Side_Center_RC": 1,
        "ShotZoneArea_Right_Side_R": 0,
        "ShotZoneRange_16_24_ft": 0,
        "ShotZoneRange_24_ft": 1,
        "ShotZoneRange_8_16_ft": 0,
        "ShotZoneRange_Back_Court_Shot": 1,
        "ShotZoneRange_Less_Than_8_ft": 0,
        "SeasonType_Playoffs": 1,
        "SeasonType_Regular_Season": 0,
        "Game_ID_Frequency": 0.8,
        "Game_Event_ID_Frequency": 0.7,
        "Player_ID_Frequency": 0.9,
        "Year": 2022,
        "Month": 6,
        "Day": 11,
        "Day_of_Week": 5
    }
    
    token = get_token(client)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = client.post("/predict", json=data, headers=headers)
    assert response.status_code == 200
    assert 'prediction' in response.json()
    assert response.json()['prediction'] == 1  # Ensure this matches the mock return value
