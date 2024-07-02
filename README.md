NBA MLOps
===========================================================================================
This project demonstrates MLOps best practices using a machine learning 
model that predicts if an NBA player will make a specific shot or not.

![NBA Shot by Steph Curry](https://github.com/jja4/nba_mlops/blob/main/reports/images/Curry_perfect_shot.jfif)

Project Organization
------------
    ├── .github            <- Scripts for Github configs
    │   └── workflow       <- Scripts for Github Actions
    │       └── nba_app.yml
    |
    ├── code               <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── database  <- Scripts to download or generate data
    │   │   └── setup_database.py
    │   │
    │   ├── training_pipeline <- Scripts to run training pipeline
    │   │   │                 
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── api            <- Scripts for the FastAPI application
    │   │   └── nba_app.py <- Main application file for the API
    │   │
    |   ├── tests          <- Scripts to run unit tests
    │   │   └── test_example.py
    |   |
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   │   └── visualize.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py
    |
    ├── data
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    |
    ├── trained_models     <- Trained and serialized models, model predictions, or model summaries
    |
    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── requirements.txt   <- The required libraries to deploy this project.

***

===========================================================================================

## Getting Started

## Building and Connecting to the App, including the PostgreSQL database

1. Make sure you have docker installed on your machine

2. Navigate to the nba_mlops directory (cd path/to/nba_mlops) and execute:

```bash
docker-compose -f docker-compose.api.yml up
```

3. To check if the users table exists, run the following code
```bash
docker exec -it nba_mlops_db_1 psql -U ubuntu -d nba_db
# enter the password 'mlops' if requested
SELECT * FROM users;
```
4. To see the previous predictions and their user verification

```bash
SELECT id, prediction, user_verification FROM predictions;
```

===========================================================================================

## Running the app
How to Use the `@app.post('/predict')` Endpoint
To reach the `/predict` endpoint and make a prediction, follow these steps:

We have two options to do that:

A. Running the API in Python virtual environment (RECOMMENDED)
    
1. Start the API

First, navigate to the main directory and start the API using the following command in your terminal:
```bash
uvicorn code.api.nba_app:app --reload
```
This command will start the FastAPI application and make it accessible at http://localhost:8000.
    
2. Run unit tests in another console
```bash
python -m venv venv
```
This command creates a Python virtual environment named "venv" in the current directory. A virtual environment is a self-contained 
directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages.
    
```bash
source venv/bin/activate
```
This command activates the virtual environment. When you activate a virtual environment, it changes your shell's PATH environment variable to point to the Python interpreter and other scripts specific to the virtual environment. This ensures that when you run Python commands, you're using the version of Python and packages installed in the virtual environment, rather than the system-wide Python installation.
    
```bash
pip install -r requirements.txt
```
This command installs Python packages listed in the requirements.txt file into the activated virtual environment using pip, the Python package installer. The -r flag tells pip to install all the packages listed in the requirements file.
    
```bash
export PYTHONPATH=./code
```
This command sets the PYTHONPATH environment variable to include the ./code directory. PYTHONPATH is a list of directories where Python looks for modules when you import them. By adding ./code to PYTHONPATH, you're telling Python to also search for modules in the code directory when you run your tests.
    
```bash
pytest -v code/tests
```
This command runs your unit tests using pytest, a testing framework for Python. The -v flag makes pytest run in verbose mode, which provides more detailed output about the tests being run. code/tests specifies the directory containing your test files.


B. Running the API locally
    
1. Start the API

First, navigate to the `/code/api` directory and start the API using the following command in your terminal:
    
```bash
uvicorn nba_app:app
```
This command will start the FastAPI application and make it accessible at http://localhost:8000.

===========================================================================================

## Using the App

1. Open http://localhost:8000/docs.

2. Navigate to "POST /signup"

3. Click "Try it Out"

4. Enter your username and password to register with the database
```bash{
  "username": "newuser",
  "password": "newpassword",
  "disabled": false
}
```
5. Click "Execute", in the Response body, you should see a "message": "User {your new username} created successfully"

6. In the FastAPI GUI, navigate to the "Authorize" button at the top.

7. Enter your username and password (you can leave all other fields empty) and click "Authorize"

8. Navigate to "POST /predict"

9. Click "Try it Out"

10. Use the Default values in the Request Body or provide the following JSON object with values for the features used to train the model:
```bash
{
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
```
11. Click "Execute" and view the prediction (0 or 1) in the Response body

===========================================================================================

## Verifying previous predictions

1. Once logged in as an authenticated user, navigate to "GET /verify_random_prediction"

2. Click "Try it Out"

3. Inspect the input parameters

4. Navigate to "POST /verify_random_prediction"

5. Click "Try it Out"

6. Enter the corresponding prediction_id and the true_value (0 for miss, 1 for make) of the NBA shot
```bash
{
  "prediction_id": 13,
  "true_value": 0
}
```
7. Click "Execute", in the Response body, you should see a "message": "Prediction_id:13 verified successfully"

## How to Use the `docker compose up`
Move to `nba_mlops` project main folder and run:
```bash
docker compose up
```

This will initiate the execution of the `docker-compose.yml` file, which in turn launches all Docker containers for the respective scripts.

===========================================================================================

## Why and how we use logging
In our project, we have implemented logging across various stages of our data pipeline. Each stage logs important events and statuses to ensure we have a clear and detailed record of the process. Here's a breakdown of how logging is implemented in our project:
1. Data Ingestion:
    - The process starts with logging the initiation of the data ingestion process.
    - It logs the source of the data and confirms successful reading of the data.
    - Validation of the data is logged, along with the outcome of the validation.
    - The ingestion of new data and its appending to the existing dataset is logged.
    - Finally, the successful saving of the data and the completion of the ingestion process are logged.
2. Data Processing:
    - The start of the data processing stage is logged.
    - The source of the data being processed is logged.
    - Successful saving of the processed data is logged.
    - Completion of the data processing pipeline is logged.
3. Feature Engineering:
    - The initiation of the feature engineering process is logged.
    - Loading of data for feature engineering is logged.
    - Generation of the joblib file containing the training and test datasets is logged.
    - Completion of the feature engineering process is logged.
4. Model Training:
    - Logging starts with the model training process.
    - Successful saving of the trained model is logged.
    - The completion of the model training process is logged.
5. Model Prediction:
    - The start of the model prediction process is logged.
    - Successful saving of the prediction results is logged.
    - Completion of the model prediction process is logged.

Logging is a critical part of our data pipeline for several reasons:
- Monitoring and Debugging: Logging helps us keep track of what our application is doing, making it easier to identify where things might be going wrong.
- Accountability and Traceability: Logs provide a historical record of events that have taken place in our application.
- Performance Analysis: By logging timestamps, we can measure the duration of different processes and identify bottlenecks in our data pipeline.
- Communication: Logs serve as a means of communication among team members. They provide insights into the execution flow and status of different components, which is essential for collaborative development and troubleshooting. 

===========================================================================================

## Getting new data and retrain the model
We simulate retrieving new data by running a GitHub action (generate_new_data.yml) every Sunday at 9 am UTC. This action generates a small CSV file from our original big data and pushes it to a dedicated path in our repository. On Monday at 9 am UTC, another GitHub action (retrain_model.yml) triggers retraining. This action runs only after receiving a notification of the push action for the new data file. The retraining process involves running Docker Compose and pushing the trained model to Docker Hub.

===========================================================================================

## Condition for Model Update Based on Accuracy Improvement
In the context of this project, the model training process involves evaluating the accuracy of the newly trained model against the current best model. Here's the condition that determines whether the new accuracy should trigger a model update and a Docker Hub push:

1. Current Best Model Metrics:

The accuracy of the current best model is stored in best_model_metrics.json.

2. New Model Training:

During the model training process, a new accuracy metric (new_accuracy) is calculated based on the latest training data.

3. Improvement Condition:

The decision to update the model and trigger a Docker Hub push depends on whether the new_accuracy is greater than the best_accuracy recorded in best_model_metrics.json. Specifically:
- If new_accuracy > best_accuracy, the newly trained model is considered better, and it replaces the current best model.
- Otherwise, if new_accuracy <= best_accuracy, the new model is not considered an improvement, and the current best model remains unchanged.

4. Action on Improvement:

When the new model shows improved accuracy (new_accuracy > best_accuracy):
- The new model is saved, and the metrics in best_model_metrics.json are updated to reflect the new accuracy value.
- A signal file (signal_new_model_version) is generated to indicate that a new model version has been created and should be used for subsequent tasks such as deployment or further evaluation.
- Docker images associated with various services (like data ingestion, processing, feature engineering, model training, and inference) are built, tagged with a version identifier, and pushed to Docker Hub.

5. Notification:

Users are informed through logs and messages that the model has been updated due to improved accuracy, and Docker images have been pushed to Docker Hub accordingly.

This evaluation ensures that the model continuously improves based on the latest data, and significant accuracy improvements trigger updates to the production model as well as Docker Hub for deployment.

===========================================================================================

## MLFlow Integration for Local Model Tracking
This project integrates MLFlow for local model tracking, enabling you to log model metrics and artifacts for better experiment management. The MLFlow tracking server runs locally and is demonstrated only on the localhost due to the lack of an external server URL.

# Prerequisites
Ensure that MLFlow is installed on your local machine. You can install it using pip:
```bash
pip install mlflow
```

# Running the MLFlow Tracking Server
To run the MLFlow tracking server locally, use the following command:
```bash
mlflow server --host 0.0.0.0 --port 6001
```
This command starts an MLFlow server on port 6001.

# Accessing the MLFlow UI
To visualize the experiments and logged data, open your web browser and navigate to:
```bash
http://localhost:6001
```
Here, you can explore the logged experiments, runs, parameters, metrics, and artifacts.

# MLFlow Configuration in the Project
The 'model_training.py' script has been updated to log model parameters, metrics, and the trained model itself to the MLFlow tracking server. The relevant changes include:

1. Set Tracking URI: The MLFlow tracking server URI is set to http://localhost:6001.
2. Set Experiment Name: The experiment name is set to nba_shot_prediction.
3. Start a Run: A new MLFlow run is started with a unique name based on the versioned filename.
4. Log Parameters: Model parameters like model_type, solver, C, and max_iter are logged.
5. Log Metrics: The accuracy of the model is logged as a metric.
6. Log Model: The trained model is logged using mlflow.sklearn.log_model.

By following these steps and understanding the MLFlow integration, you can effectively manage and track your machine learning experiments locally.

===========================================================================================

