from datetime import datetime, timedelta, timezone
from typing import Union, Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from typing_extensions import Annotated
from pydantic import BaseModel, Field
import os
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import httpx
import json
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Summary


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database connection details
DB_HOST = os.getenv("DB_HOST", "localhost")  # Uses'db' for Docker Compose
DB_NAME = os.getenv("DB_NAME", "nba_db")
DB_USER = os.getenv("DB_USER", "ubuntu")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mlops")
PREDICTION_SERVICE_HOST = os.getenv('PREDICTION_SERVICE_HOST', 'localhost')
PREDICTION_SERVICE_PORT = os.getenv('PREDICTION_SERVICE_PORT', '8001')


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
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

                # Check if the predictions table exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'predictions'
                );
                """)
                table_exists = cur.fetchone()['exists']
                if not table_exists:
                    print("Table 'predictions' does not exist yet.")
                else:
                    print("Table 'predictions' already exists.")

            conn.commit()
    except Exception as e:
        print(f"Error during application startup: {e}")
        raise

    yield  # This is where the application runs

    # Shutdown event (if needed)
    # can add any cleanup code here if necessary

app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

# Configure CORS so we can communicate with the React frontend app
origins = [
    "http://localhost:3000",  # origin for the React app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str = Field(default="testuser")
    password: str = Field(default="testpassword")
    disabled: Union[bool, None] = False


class UserInDB(User):
    hashed_password: str


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


inference_time_summary = Summary('inference_time_seconds', 'Time taken for inference')


@app.post('/predict', name="Secure prediction based on scoring parameters.")
async def predict(
    current_user: Annotated[User, Depends(authorize_user)],
    item: ScoringItem
):
    with inference_time_summary.time():
        url = f"http://{PREDICTION_SERVICE_HOST}:{PREDICTION_SERVICE_PORT}/predict"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=item.dict())
            result = response.json()

        # Save prediction and input parameters to database
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            insert_query = """
            INSERT INTO predictions (prediction, input_parameters)
            VALUES (%s, %s)
            """
            cur.execute(insert_query, (result["prediction"], json.dumps(item.dict())))
            conn.commit()
        except Exception as e:
            print(f"Error saving prediction: {e}")
            raise HTTPException(status_code=500, detail="Error saving prediction")
        finally:
            cur.close()
            conn.close()
            
            return response.json()


class VerificationInput(BaseModel):
    prediction_id: Optional[int] = None
    true_value: int

@app.get("/verify_random_prediction")
async def get_random_prediction(
    current_user: Annotated[User, Depends(authorize_user)],
):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT id, prediction, input_parameters, timestamp
            FROM predictions 
            WHERE user_verification IS NULL
            ORDER BY RANDOM()
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """)
        prediction = cur.fetchone()
        
        if not prediction:
            return {"message": "No unverified predictions available"}
            
        response = {
            "prediction_id": prediction['id'],
            "model_prediction": prediction['prediction'],
            "date_time": prediction['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            "input_parameters": json.loads(prediction['input_parameters'])
            if isinstance(prediction['input_parameters'], str) else prediction['input_parameters']
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/verify_random_prediction")
async def verify_prediction(
    current_user: Annotated[User, Depends(authorize_user)],
    verification: VerificationInput
):
    # add check to make sure prediction id is available
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM predictions WHERE id = %s", (verification.prediction_id,))
        prediction = cur.fetchone()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        cur.execute(
            "UPDATE predictions SET user_verification = %s WHERE id = %s",
            (verification.true_value, verification.prediction_id)
        )
        conn.commit()
        
        return {"message": f"Prediction_id:{verification.prediction_id} verified successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()