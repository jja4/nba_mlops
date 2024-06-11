from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import pandas as pd
import os
from joblib import load

# Get the path to the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', '..'))

# Construct the path to the 'trained_models' directory
trained_models_dir = os.path.join(project_root, 'trained_models')

# Specify the filename of the trained model
joblib_filename = 'model_best_lr.joblib'

# Construct the full path to the joblib file
joblib_file_path = os.path.join(trained_models_dir, joblib_filename)

# Load the joblib file
model = load(joblib_file_path)


# Constants
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI app
app = FastAPI()


# User model
class User(BaseModel):
    username: str
    password: str


# Token data model
class TokenData(BaseModel):
    username: Optional[str] = None


# Fake database
users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password":
        "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    if username in users_db:
        user_data = users_db[username]
        return User(**user_data)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the NBA prediction API!"}

# Signup endpoint
@app.post("/signup")
async def signup(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(user.password)
    users_db[user.username] = {
        "username": user.username,
        "hashed_password": hashed_password,
        "disabled": False,
    }
    return {"message": "User created successfully"}

# Login endpoint
@app.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Prediction endpoint
@app.post("/predict")
async def predict(data: dict, current_user: User = Depends(get_current_user)):
    # Perform prediction using the machine learning model
    prediction = predict_with_model(data)
    return {"prediction": prediction}


# Dummy prediction function
def predict_with_model(data):
    # Replace with actual machine learning model
    return "This is a dummy prediction"


class ScoringItem(BaseModel):
    Period: int
    Minutes_Remaining: int
    Seconds_Remaining: int
    Shot_Distance: int
    X_Location: int
    Y_Location: int
    #Shot_Made_Flag: int
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


@app.post('/free_predict')
async def scoring_endpoint(item: ScoringItem):
    # Create a DataFrame with the data of the request object
    df = pd.DataFrame([item.dict()])
    # Rename the columns to match the expected names
    df = df.rename(columns={
        "Minutes_Remaining": "Minutes Remaining",
        "Seconds_Remaining": "Seconds Remaining",
        "Shot_Distance": "Shot Distance",
        "X_Location": "X Location",
        "Y_Location": "Y Location",
        #"Shot_Made_Flag": "Shot Made Flag",
        "Action_Type_Frequency": "Action Type Frequency",
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
    return {"prediction": int(yhat)}
