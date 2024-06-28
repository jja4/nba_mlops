from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from joblib import load


# Get the path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Construct the path to the 'trained_models' directory
trained_models_dir = os.path.join(project_root, 'trained_models')

# Specify the filename of the trained model
joblib_filename = 'model_best_lr.joblib'

# Construct the full path to the joblib file
joblib_file_path = os.path.join(trained_models_dir, joblib_filename)

# Load the joblib file
model = load(joblib_file_path)

app = FastAPI()


class ScoringItem(BaseModel):
    """
    Model representing scoring parameters for prediction.
    """
    Period: float
    Minutes_Remaining: float
    Seconds_Remaining: float
    Shot_Distance: float
    X_Location: float
    Y_Location: float
    Action_Type_Frequency: float
    Team_Name_Frequency: float
    Home_Team_Frequency: float
    Away_Team_Frequency: float
    ShotType_2PT_Field_Goal: int
    ShotType_3PT_Field_Goal: int
    ShotZoneBasic_Above_the_Break_3: int
    ShotZoneBasic_Backcourt: int
    ShotZoneBasic_In_The_Paint_Non_RA: int
    ShotZoneBasic_Left_Corner_3: int
    ShotZoneBasic_Mid_Range: int
    ShotZoneBasic_Restricted_Area: int
    ShotZoneBasic_Right_Corner_3: int
    ShotZoneArea_Back_Court_BC: int
    ShotZoneArea_Center_C: int
    ShotZoneArea_Left_Side_Center_LC: int
    ShotZoneArea_Left_Side_L: int
    ShotZoneArea_Right_Side_Center_RC: int
    ShotZoneArea_Right_Side_R: int
    ShotZoneRange_16_24_ft: int
    ShotZoneRange_24_ft: int
    ShotZoneRange_8_16_ft: int
    ShotZoneRange_Back_Court_Shot: int
    ShotZoneRange_Less_Than_8_ft: int
    SeasonType_Playoffs: int
    SeasonType_Regular_Season: int
    Game_ID_Frequency: float
    Game_Event_ID_Frequency: float
    Player_ID_Frequency: float
    Year: int
    Month: int
    Day: int
    Day_of_Week: int

@app.post('/predict')
async def predict(input_data: ScoringItem):
    """
    Endpoint for secure prediction based on scoring parameters.

    Args:
        item (ScoringItem): Input parameters for prediction.

    Returns:
        dict: Prediction result, can be 1 or 0 indicating shot made or missed.
    """
    # Create a DataFrame with the data of the request object
    df = pd.DataFrame([input_data.model_dump()])
    # Rename the columns to match the expected names
    df = df.rename(columns={
        "Minutes_Remaining": "Minutes Remaining",
        "Seconds_Remaining": "Seconds Remaining",
        "Shot_Distance": "Shot Distance",
        "X_Location": "X Location",
        "Y_Location": "Y Location",
        #"Shot_Made_Flag": "Shot Made Flag",
        "Action_Type_Frequency": "Action Type_Frequency",
        "Team_Name_Frequency": "Team Name_Frequency",
        "Home_Team_Frequency": "Home Team_Frequency",
        "Away_Team_Frequency": "Away Team_Frequency",
        "ShotType_2PT_Field_Goal": "ShotType_2PT Field Goal",
        "ShotType_3PT_Field_Goal": "ShotType_3PT Field Goal",
        "ShotZoneBasic_Above_the_Break_3": "ShotZoneBasic_Above the Break 3",
        "ShotZoneBasic_Backcourt": "ShotZoneBasic_Backcourt",
        "ShotZoneBasic_In_The_Paint_Non_RA": "ShotZoneBasic_In The Paint (Non-RA)",
        "ShotZoneBasic_Left_Corner_3": "ShotZoneBasic_Left Corner 3",
        "ShotZoneBasic_Mid_Range": "ShotZoneBasic_Mid-Range",
        "ShotZoneBasic_Restricted_Area": "ShotZoneBasic_Restricted Area",
        "ShotZoneBasic_Right_Corner_3": "ShotZoneBasic_Right Corner 3",
        "ShotZoneArea_Back_Court_BC": "ShotZoneArea_Back Court(BC)",
        "ShotZoneArea_Center_C": "ShotZoneArea_Center(C)",
        "ShotZoneArea_Left_Side_Center_LC": "ShotZoneArea_Left Side Center(LC)",
        "ShotZoneArea_Left_Side_L": "ShotZoneArea_Left Side(L)",
        "ShotZoneArea_Right_Side_Center_RC": "ShotZoneArea_Right Side Center(RC)",
        "ShotZoneArea_Right_Side_R": "ShotZoneArea_Right Side(R)",
        "ShotZoneRange_16_24_ft": "ShotZoneRange_16-24 ft.",
        "ShotZoneRange_24_ft": "ShotZoneRange_24+ ft.",
        "ShotZoneRange_8_16_ft": "ShotZoneRange_8-16 ft.",
        "ShotZoneRange_Back_Court_Shot": "ShotZoneRange_Back Court Shot",
        "ShotZoneRange_Less_Than_8_ft": "ShotZoneRange_Less Than 8 ft.",
        "SeasonType_Playoffs": "SeasonType_Playoffs",
        "SeasonType_Regular_Season": "SeasonType_Regular Season",
        "Game_ID_Frequency": "Game ID_Frequency",
        "Game_Event_ID_Frequency": "Game Event ID_Frequency",
        "Player_ID_Frequency": "Player ID_Frequency",
        "Year": "Year",
        "Month": "Month",
        "Day": "Day",
        "Day_of_Week": "Day_of_Week"
    })
    # Make a prediction with the loaded model
    yhat = model.predict(df)
    # Return the prediction as an answer
    return {"prediction": int(yhat.item())}

