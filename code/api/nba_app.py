from datetime import datetime, timedelta, timezone
from typing import Union, Optional, Dict

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from typing_extensions import Annotated
from pydantic import BaseModel, Field
import pandas as pd
import os
import random
from joblib import load
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from psycopg2 import OperationalError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database connection details
DB_HOST = os.getenv("DB_HOST", "localhost")  # Default to 'db' for Docker Compose
DB_NAME = os.getenv("DB_NAME", "nba_db")
DB_USER = os.getenv("DB_USER", "ubuntu")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mlops")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password):
    return pwd_context.hash(password)


username = "johndoe"
password = "secret"
hashed_password = get_password_hash(password)
disabled = False


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    return conn


@app.on_event("startup")
async def startup_event():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if the username already exists
                check_query = "SELECT COUNT(*) FROM users WHERE username = %s"
                cur.execute(check_query, (username,))
                count = cur.fetchone()['count']

                if count == 0:
                    # Username doesn't exist, insert the new user
                    insert_query = """
                    INSERT INTO users (username, hashed_password, disabled)
                    VALUES (%s, %s, %s)
                    """
                    cur.execute(insert_query, (username, hashed_password, disabled))
                    print(f"User '{username}' inserted successfully.")
                else:
                    print(f"User '{username}' already exists.")

            conn.commit()
    except Exception as e:
        print(f"Error during application startup: {e}")
        raise


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str = Field(default="testuser")
    password: str = Field(default="testpassword")
    disabled: Union[bool, None] = None


class UserOut(BaseModel):
    username: str
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


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

# Configure CORS so we can communicate with the React frontend app
origins = [
    "http://localhost:3000",  # origin for the React app
]


def get_user(username: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, hashed_password, disabled FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return UserInDB(**user)
    else:
        return None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def authorize_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Root endpoint
@app.get("/")
async def root():
    """
    Welcome endpoint of the NBA prediction API.

    Returns:
        dict: A message indicating the welcome message.
    """
    return {"message": "Welcome to the NBA prediction API!"}

@app.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
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
    return Token(access_token=access_token, token_type="bearer")



# Signup endpoint
@app.post("/signup")
async def signup(user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        hashed_password = get_password_hash(user.password)
        cur.execute("INSERT INTO users (username, hashed_password, disabled) VALUES (%s, %s, %s)",
                    (user.username, hashed_password, user.disabled))
        conn.commit()
        return {"message": f"User {user.username} created successfully"}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        cur.close()
        conn.close()

@app.get("/user", response_model=UserOut)
async def read_current_user(
    current_user: Annotated[User, Depends(authorize_user)],
):
    return UserOut(username=current_user.username, disabled=current_user.disabled)


@app.post("/predict")
async def secure_predict(
    current_user: Annotated[User, Depends(authorize_user)],
):
    # Perform prediction using the machine learning model
    prediction = random.randint(0, 1)
    return {"prediction": prediction}

    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoringItem(BaseModel):
    """
    Model representing scoring parameters for prediction.
    """
    Period: int
    Minutes_Remaining: int
    Seconds_Remaining: int
    Shot_Distance: int
    X_Location: int
    Y_Location: int
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

@app.post('/unsecure_predict')
async def unsecure_predict(item: ScoringItem):
    """
    Endpoint for unsecure_prediction based on scoring parameters.

    Args:
        item (ScoringItem): Input parameters for prediction.

    Returns:
        dict: Prediction result, can be 1 or 0 indicating shot made or missed.
    """
    # Create a DataFrame with the data of the request object
    df = pd.DataFrame([item.model_dump()])
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
    return {"prediction": int(yhat.item())}  # Use item() to extract a single element


class SimplePredictInput(BaseModel):
    X_Location: float
    Y_Location: float
    Player_Index: int
# endpoint with a description of Simple Predict for Frontend
@app.post('/simple_predict', response_model=Dict[str, int], name="Simple prediction based on X_Location, Y_Location, and Player_Index.")
def simple_predict(input_data: SimplePredictInput):
    """
    Simple endpoint for prediction based on X_Location, Y_Location, and
    Player_Index.

    Args:
        input_data (SimplePredictInput): Input data containing X_Location,
        Y_Location, and Player_Index.

    Returns:
        dict: A dictionary containing a random prediction (0 or 1).
    """
    # Extract input data
    X_Location = input_data.X_Location
    Y_Location = input_data.Y_Location
    Player_Index = input_data.Player_Index

    # Dummy prediction function
    def simple_predict_no_model(X_Location, Y_Location, Player_Index):
        # Replace with actual machine learning model
        return random.randint(0, 1)

    # Generate a random prediction (0 or 1)
    prediction = simple_predict_no_model(X_Location, Y_Location, Player_Index)
    return {"prediction": prediction}
