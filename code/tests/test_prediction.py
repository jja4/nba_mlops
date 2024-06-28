from fastapi.testclient import TestClient
from api.nba_app import app, lifespan
import pytest
import asyncio
import json

test_client = TestClient(app)


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
        "Period": 1,
        "Minutes_Remaining": 10,
        "Seconds_Remaining": 30,
        "Shot_Distance": 1,
        "X_Location": 5,
        "Y_Location": 10,
        "Action_Type_Frequency": 0.2,
        "Team_Name_Frequency": 0.5,
        "Home_Team_Frequency": 0.4,
        "Away_Team_Frequency": 0.6,
        "ShotType_2PT_Field_Goal": 1,
        "ShotType_3PT_Field_Goal": 0,
        "ShotZoneBasic_Above_the_Break_3": 1,
        "ShotZoneBasic_Backcourt": 0,
        "ShotZoneBasic_In_The_Paint_Non_RA": 0,
        "ShotZoneBasic_Left_Corner_3": 0,
        "ShotZoneBasic_Mid_Range": 1,
        "ShotZoneBasic_Restricted_Area": 0,
        "ShotZoneBasic_Right_Corner_3": 0,
        "ShotZoneArea_Back_Court_BC": 0,
        "ShotZoneArea_Center_C": 1,
        "ShotZoneArea_Left_Side_Center_LC": 0,
        "ShotZoneArea_Left_Side_L": 0,
        "ShotZoneArea_Right_Side_Center_RC": 1,
        "ShotZoneArea_Right_Side_R": 0,
        "ShotZoneRange_16_24_ft": 1,
        "ShotZoneRange_24_ft": 0,
        "ShotZoneRange_8_16_ft": 0,
        "ShotZoneRange_Back_Court_Shot": 0,
        "ShotZoneRange_Less_Than_8_ft": 1,
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

    # Log the response details
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content.decode('utf-8')}")

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the 'prediction' key
    response_json = response.json()
    assert 'prediction' in response_json

    # Check if the prediction value is either 0 or 1
    prediction = response_json['prediction']
    assert prediction == 1


def test_predict_endpoint_shot_missed(client: TestClient):
    data = {
        "Period": 1,
        "Minutes_Remaining": 10,
        "Seconds_Remaining": 30,
        "Shot_Distance": 15,
        "X_Location": 5,
        "Y_Location": 10,
        "Action_Type_Frequency": 0.2,
        "Team_Name_Frequency": 0.5,
        "Home_Team_Frequency": 0.4,
        "Away_Team_Frequency": 0.6,
        "ShotType_2PT_Field_Goal": 1,
        "ShotType_3PT_Field_Goal": 0,
        "ShotZoneBasic_Above_the_Break_3": 1,
        "ShotZoneBasic_Backcourt": 0,
        "ShotZoneBasic_In_The_Paint_Non_RA": 0,
        "ShotZoneBasic_Left_Corner_3": 0,
        "ShotZoneBasic_Mid_Range": 1,
        "ShotZoneBasic_Restricted_Area": 0,
        "ShotZoneBasic_Right_Corner_3": 0,
        "ShotZoneArea_Back_Court_BC": 0,
        "ShotZoneArea_Center_C": 1,
        "ShotZoneArea_Left_Side_Center_LC": 0,
        "ShotZoneArea_Left_Side_L": 0,
        "ShotZoneArea_Right_Side_Center_RC": 1,
        "ShotZoneArea_Right_Side_R": 0,
        "ShotZoneRange_16_24_ft": 1,
        "ShotZoneRange_24_ft": 0,
        "ShotZoneRange_8_16_ft": 0,
        "ShotZoneRange_Back_Court_Shot": 0,
        "ShotZoneRange_Less_Than_8_ft": 1,
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

    # Log the response details
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content.decode('utf-8')}")

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the 'prediction' key
    response_json = response.json()
    assert 'prediction' in response_json

    # Check if the prediction value is either 0 or 1
    prediction = response_json['prediction']
    assert prediction == 0


def test_predict_endpoint_unauthorized(client: TestClient):
    data = {
        "Period": 1,
        "Minutes_Remaining": 10,
        "Seconds_Remaining": 30,
        "Shot_Distance": 15,
        "X_Location": 5,
        "Y_Location": 10,
        "Action_Type_Frequency": 0.2,
        "Team_Name_Frequency": 0.5,
        "Home_Team_Frequency": 0.4,
        "Away_Team_Frequency": 0.6,
        "ShotType_2PT_Field_Goal": 1,
        "ShotType_3PT_Field_Goal": 0,
        "ShotZoneBasic_Above_the_Break_3": 1,
        "ShotZoneBasic_Backcourt": 0,
        "ShotZoneBasic_In_The_Paint_Non_RA": 0,
        "ShotZoneBasic_Left_Corner_3": 0,
        "ShotZoneBasic_Mid_Range": 1,
        "ShotZoneBasic_Restricted_Area": 0,
        "ShotZoneBasic_Right_Corner_3": 0,
        "ShotZoneArea_Back_Court_BC": 0,
        "ShotZoneArea_Center_C": 1,
        "ShotZoneArea_Left_Side_Center_LC": 0,
        "ShotZoneArea_Left_Side_L": 0,
        "ShotZoneArea_Right_Side_Center_RC": 1,
        "ShotZoneArea_Right_Side_R": 0,
        "ShotZoneRange_16_24_ft": 1,
        "ShotZoneRange_24_ft": 0,
        "ShotZoneRange_8_16_ft": 0,
        "ShotZoneRange_Back_Court_Shot": 0,
        "ShotZoneRange_Less_Than_8_ft": 1,
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
    response = client.post("/predict", json=data)

    # Log the response details
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content.decode('utf-8')}")

    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
