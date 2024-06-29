from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from joblib import load
import glob
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Get the path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Construct the path to the 'trained_models' directory
trained_models_dir = os.path.join(project_root, 'trained_models')

def find_latest_versioned_model(base_filename):
    """
    Find the latest versioned model file based on base_filename.
    Returns the path to the latest versioned model file.
    """
    search_pattern = f"{base_filename}-v*-*.joblib"
    files = glob.glob(os.path.join(trained_models_dir, search_pattern))
    
    if not files:
        raise FileNotFoundError(f"No model files found with pattern '{search_pattern}'")
    
    latest_file = max(files, key=os.path.getctime)
    return latest_file

# Specify the base filename of the trained model
base_joblib_filename = 'model_best_lr'

# Load the latest versioned model file
try:
    joblib_file_path = find_latest_versioned_model(base_joblib_filename)
    model = load(joblib_file_path)
    print(f"Loaded model from {joblib_file_path}")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

app = FastAPI()

class ScoringItem(BaseModel):
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
    try:
        # Create a DataFrame with the data of the request object
        df = pd.DataFrame([input_data.model_dump()])
        
        # Rename the columns to match the expected names
        df = df.rename(columns={
            "Minutes_Remaining": "Minutes Remaining",
            "Seconds_Remaining": "Seconds Remaining",
            "Shot_Distance": "Shot Distance",
            "X_Location": "X Location",
            "Y_Location": "Y Location",
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

        # Perform model evaluation (Optional: This is just an example)
        try:
            validation_data = pd.read_csv('path_to_validation_data.csv')  # Load your validation dataset
            X_val = validation_data.drop(columns=['target_column'])
            y_val = validation_data['target_column']
            
            # Make predictions on the validation set
            val_predictions = model.predict(X_val)
            
            # Calculate evaluation metrics
            accuracy = accuracy_score(y_val, val_predictions)
            precision = precision_score(y_val, val_predictions)
            recall = recall_score(y_val, val_predictions)
            
            evaluation_metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall
            }
            print("Model evaluation metrics:", evaluation_metrics)  # Or use a logging system
        except Exception as eval_error:
            evaluation_metrics = {
                'error': str(eval_error)
            }
            print(f"Error during model evaluation: {str(eval_error)}")
        
        # Make a prediction with the loaded model
        yhat = model.predict(df)
        
        # Return the prediction as an answer
        return {"prediction": int(yhat.item()), "evaluation_metrics": evaluation_metrics}

    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

