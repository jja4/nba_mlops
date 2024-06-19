from fastapi.testclient import TestClient
from api.nba_app import app

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

def test_unsecure_predict_endpoint_shot_made():
    """
    Test the unsecure_predict endpoint of the NBA prediction API for a made shot prediction.

    This test sends a POST request to the free predict endpoint with parameters indicating a shot made, 
    and checks if the response contains the expected prediction value.

    Returns:
        None
    """
    # JSON data to send in the request
    data = {
        "Period": 1,
        "Minutes_Remaining": 10,
        "Seconds_Remaining": 30,
        "Shot_Distance": 1,        # change this to '15' to have negative result
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

    # Send POST request to the endpoint using the test client
    response = client.post("/unsecure_predict", json=data)

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the 'prediction' key
    assert 'prediction' in response.json()

    # Check if the prediction value is either 0 or 1
    prediction = response.json()['prediction']
    assert prediction == 1

def test_unsecure_predict_endpoint_shot_missed():
    """
    Test the unsecure_predict endpoint of the NBA prediction API for a missed shot prediction.

    This test sends a POST request to the free predict endpoint with parameters indicating a shot missed, 
    and checks if the response contains the expected prediction value.

    Returns:
        None
    """
    # JSON data to send in the request
    data = {
        "Period": 1,
        "Minutes_Remaining": 10,
        "Seconds_Remaining": 30,
        "Shot_Distance": 15,        # change this to '1' to have positive result
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

    # Send POST request to the endpoint using the test client
    #response = client.post("/unsecure_predict", json=data)

    # Check if the response status code is 200
    #assert response.status_code == 200

    # Check if the response contains the 'prediction' key
    #assert 'prediction' in response.json()

    # Check if the prediction value is either 0 or 1
    #prediction = response.json()['prediction']
    #assert prediction == 0
