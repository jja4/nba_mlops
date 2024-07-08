# NBA MLOps
***
This project demonstrates MLOps best practices using a machine learning 
model that predicts if an NBA player will make a specific shot or not. The emphasis
is less on the machine learning model, and more on the automated data pipeline to train
the model, the deployment of the model, and the monitoring of the model.

![NBA Shot by Steph Curry](https://github.com/jja4/nba_mlops/blob/main/reports/images/Curry_perfect_shot.jfif)

## Project Organization
------------------------------------------------------------------------
    ├── .github            <- Scripts for Github configs
    │   └── workflow       <- Scripts for Github Actions
    │       ├── generate_new_data.yml   <- Generates new data on a specified time period
    |       ├── retrain_model.yml       <- Retrains a new model on a specified time period and condition
    |       └── unit_tests.yml          <- Runs on evry push on every branch
    ├── .gitignore      <- Includes files and folders that we don't want to control
    |
    ├── code               <- Source code for use in this project.
    │   ├── __init__.py    <- Makes code a Python module
    │   │
    |   ├── api                         <- Scripts for the FastAPI application
    │   │   ├── nba_app.py              <- Main gateway API
    │   │   └── prediction_service.py   <- Endpoint function which actually calculates the prediction
    |   |
    │   ├── config          
    │   │   └── config.py   <- Saves file path configurations
    │   │
    │   ├── database        
    │   │   └── init.sql    <- Initializes database and tables
    |   |
    │   ├── generate_new_data
    │   │   └── generate_new_data.py    <- Generates signal files for next running container
    │   │
    │   └── training_pipeline           <- Scripts to run training pipeline  
    │       ├── data_ingestion.py       <- Data ingestion from generated new data
    │       ├── data_processing.py      <- Preprocessing
    │       ├── feature_engineering.py  <- Feature engineering
    │       ├── model_training.py       <- Model training, pushing to MlFlow and Docker Hub if needed
    │       ├── inference.py            <- Inference a new model
    |       └── best_model_metrics.json <- Saved best accuracy for trained models
    │   
    ├── data                    <- Data for training the model
    |   ├── new_data            
    │   │   └── new_data.csv    <- New unseeen dataset for training
    |   |
    |   ├── predictions            
    │   │   └── predictions.csv <- Saves inference prediction results
    |   |
    │   ├── processed           <- The final, canonical data sets for modeling
    │   │   └── NBA Shot Locations 1997 - 2020-processed.csv        <- Processed new dataset. Ready for feature engineering
    │   │   └── NBA Shot Locations 1997 - 2020-train-test.joblib    <- Feature enginnered train and test sets. Ready for training
    |   |
    │   └── raw                 <- The original, immutable data dump
    │       └── NBA Shot Locations 1997 - 2020-original.csv         <- Big dataset, which is used for generating a new small dataset
    │       └── NBA Shot Locations 1997 - 2020.csv                  <- Dataset for for starting the training pipeline
    |
    ├── docker                              <- Holds all docker related files
    |   ├── docker_notes.sh                 <- Provides commands to reset Docker and to check specific tables in a PostgreSQL
    |   ├── docker-compose.api.yml          <- Connects the API, database, frontend, and monitoring
    |   ├── docker-compose.yml              <- Rans in a sequential order training pipeline containers
    |   ├── Dockerfile.api                  <- API container
    |   ├── Dockerfile.db                   <- Database container
    |   ├── Dockerfile.prediction_service   <- Prediction service container
    |   ├── Dockerfile.data_ingestion       <- Data ingestion container
    |   ├── Dockerfile.data_processing      <- Data preprocessing container
    |   ├── Dockerfile.feature_engineering  <- Fetaure engineering contrainer
    |   ├── Dockerfile.model_training       <- Model training container
    |   ├── Dockerfile.inference            <- Inference container
    |   └── entrypoint.sh                   <- Generates signal files for next running containers
    |
    ├── trained_models      <- Trained models with their version numbers and the date that they were created
    │   ├── model_best_lr-v1-20240628.joblib    <- Trained model example
    |   └── discarded       <- Keeps discarded (not improved) model versions
    |        └── model_best_lr-v1-20240705.joblib   <- Discarded file example
    |
    ├── grafana_setup                   <- Monitoring api requests
    |   ├── dashboards
    │   |    └── nba_dashboard.json     <- Grafana dashboard data
    │   │
    │   └── datasources
    │        └── datasources.yaml       <- Defines configuration settings for Grafana 
    │
    ├── prometheus_setup       
    │   └── alerting_rules.yml      <- Alerting rules when server goes down
    │   └── prometheus.yml          <- Prometheus configuration file specifying global settings
    │
    ├── logs            <- Keep all logs
    │   └── logs.log    <- Logs processes to logs.log
    |
    ├── pytest.ini      <- To suppress warnings during pytest runs
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports                     <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── NBA-MLOps-Report.pdf    <- Specification describing project context
    │
    ├── requirements.txt   <- The required libraries to deploy this project.
    │                         Generated with `pip freeze > requirements.txt`
    |
    ├── .flake8     <- Includes Flake8 standard configs
    ├── LICENSE     <- The MIT License (MIT)
    └── README.md   <- The top-level README for developers using this project.

***
## Project Introduction
![NBA MLOps Architecture Diagram](https://github.com/jja4/nba_mlops/blob/main/reports/figures/Intro.png)

***
## Architecture Diagram

![NBA MLOps Architecture Diagram](https://github.com/jja4/nba_mlops/blob/main/reports/figures/architecture_v2.png)

***

## Getting Started

### Building and Connecting to the App
#### Including FastApi, PostreSQL, Prometheus, Grafana, React

1. Make sure you have docker installed on your machine

2. Navigate to the nba_mlops directory (cd path/to/nba_mlops) and execute:

```bash
docker-compose -f docker/docker-compose.api.yml up
```

3. To check if the users table exists, first let's find the name of the database container:
```bash
docker container ls
```
4. Then use the `nba_mlops_db_1`, or similar, container name in the following:
```bash
docker exec -it nba_mlops_db_1 psql -U ubuntu -d nba_db
# enter the password 'mlops' if requested
SELECT * FROM users;
```
4. To see the previous predictions and their user verification

```bash
SELECT id, prediction, user_verification FROM predictions;
```
***

## Using the App

![FastApi GUI](https://github.com/jja4/nba_mlops/blob/main/reports/images/FastAPI_screenshot.png)

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

## Using Grafana to Monitor the App

![Grafana GUI](https://github.com/jja4/nba_mlops/blob/main/reports/images/Grafana_screenshot.png)

1. Open http://localhost:3000

2. Navigate to hamburger menu on the top left (three horizontal lines)

3. Click "Dashboards", then click on "nba_dashboard" from the list

4. The top row monitors HTTP requests, Inference Time, and the Status of the Gateway API

5. The bottom row monitors the PostgreQSL database: the number of users, number of predictions, and number of verified predictions.

## Using React to Interact with the ML model

![React GUI](https://github.com/jja4/nba_mlops/blob/main/reports/images/React_screenshot.png)

1. Open http://localhost:3001

2. Click on the basketball court to input a position for the NBA player to shoot from

3. View the prediction from the ML model if the player will make or miss the shot

***

## Configure and Test Alerts when the API shuts down

### Configure
1. In the codebase, open `nba_mlops/alertmanager/alertmanager.yml`

2. In the "global" header, replace `slack_api_url: 'URL/to/slack/hooks'` with a functional webhook for slack. Set one up here for you slack channel (https://api.slack.com/messaging/webhooks)

3. In the "receivers" header, update `- channel: '#may24_bmlops_int_nba'` with your channel name as well.

4. For email notifications, in the "receivers" header, replace `- to: 'fake@gmail.com'` with your email.

### Test
1. Make sure docker-compose already up and running 
```bash
docker-compose -f docker/docker-compose.api.yml up
``` 
2. Find the name of your API container with:
```bash
docker container ls
``` 
3. We are going to shut down your API container with:
```bash
docker container stop docker-api-1
``` 
4. You should receive a Slack message and an email after 30 seconds or so. You can resolve the alert with:
```bash
docker container start docker-api-1
``` 
***
## Deploying to AWS EC2

The app has been delpoyed to an EC2 instance, virtual machine, on AWS. 
To utilize the Free-Tier of AWS, a t3.micro virtual machine was chosen, using 16GB of Elastic Block Storage.
These links can be followed to see the AWS hosted version of the app, at least temporarily.

FastAPI
(http://13.48.249.166:8000/docs)

Grafana Monitoring
(http://13.48.249.166:3000)
u: Admin
p: Admin

React Frontend
(http://13.48.249.166:3001)

The AWS Security Group was configured with these Inbound rules:
![AWS Security Group](https://github.com/jja4/nba_mlops/blob/main/reports/images/AWS_SecurityGroup_screenshot.png)

***

## How to Run the Model Training Pipeline
Move to the `nba_mlops` project folder and run:
```bash
docker-compose -f docker/docker-compose.yml up
```

This will initiate the execution of the `docker-compose.yml` file, which in turn launches all Docker containers for the training pipeline.

***

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

***

## Python API Tests
This document describes the process for running unit tests on our Python API using GitHub Actions. The unit tests are designed to ensure that our API functions correctly and interacts properly with the database and prediction service.

The unit_tests.yaml workflow is triggered by pushes and pull requests to any branches. It sets up the necessary environment, including a PostgreSQL database and a prediction service, and then runs the unit tests.

### Triggering the Workflow
The workflow is triggered when we push any code or create a pull request on the all branches.

### Workflow Steps
1. Checkout Code: The workflow checks out the latest version of the code from the repository.
2. Set Up Python: Sets up Python 3.9 for the workflow environment.
3. Install Dependencies: Installs the necessary Python dependencies in a virtual environment.
4. Set Up Database: Configures a PostgreSQL database service with the required environment variables.
5. Wait for PostgreSQL to Be Ready: Waits for the PostgreSQL service to be ready to accept connections.
6. Set Up Database: Initializes the PostgreSQL database by running a SQL script to set up the required schema and data.
7. Start Prediction Service: Starts the prediction service using Uvicorn to host the service on the specified host and port.
8. Wait for Prediction Service to Be Ready: Waits for the prediction service to start by pausing the workflow for a specified amount of time.
9. Run Tests: Runs the unit tests using pytest to verify the functionality of the API.

### Environment Variables
The workflow uses the following environment variables:

- PYTHONPATH: Specifies the Python path to the code directory.
- DB_HOST: Hostname for the PostgreSQL database.
- DB_NAME: Name of the PostgreSQL database.
- DB_USER: Username for the PostgreSQL database.
- DB_PASSWORD: Password for the PostgreSQL database.
- PREDICTION_SERVICE_HOST: Hostname for the prediction service.
- PREDICTION_SERVICE_PORT: Port for the prediction service.

### Summary
This workflow ensures that our Python API is tested thoroughly before any changes are merged into key branches. By setting up a PostgreSQL database and a prediction service, we simulate the production environment to catch any potential issues early in the development process.

***

## Process for Retraining the Model 
Here we outline the process of retraining our model using GitHub Actions and Docker Compose, and subsequently pushing the trained model to Docker Hub. The retraining process is scheduled to run daily.

We utilize two main GitHub Actions for our retraining pipeline:

1. generate_new_data.yml: Runs every day at 4 am UTC to generate and push new data.
2. retrain_model.yml: Runs every day at 5 am UTC to retrain the model using the new data and push the updated model to Docker Hub.

### GitHub Actions Workflow
- generate_new_data.yml
This workflow generates new data from our original dataset and pushes a small CSV file to a dedicated path in our repository.

- retrain_model.yml
This workflow retrains the model using the new data generated by the previous action and pushes the trained model to Docker Hub. Below is a detailed explanation of the retrain_model.yml workflow.

### Docker Compose Configuration
Our Docker Compose file defines the services for data ingestion, data processing, feature engineering, model training, and inference. Each service builds from a specific Dockerfile and uses shared volumes for data transfer.

### entrypoint.sh
The entrypoint script coordinates the execution order of services based on signal files.

By following this process, we ensure that our model is retrained daily with the latest data and that the updated model is deployed to Docker Hub for further use.

***

### Condition for Model Update Based on Accuracy Improvement
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

***

## DagsHub Integration
This project utilizes DagsHub for collaborative machine learning and version control. DagsHub helps us manage our data, models, and experiments effectively.

### DagsHub Setup
To use DagsHub with this project, follow these steps:

First, clone the repository from DagsHub to your local machine:
```bash
git clone https://dagshub.com/joelaftreth/nba_mlops.git
cd nba_mlops
```

Ensure you have the DagsHub CLI installed. If not, install it using:
```bash
pip install dagshub
```

Initialize DagsHub in your project if you want to run it via python script `python3 model_training.py`:
```bash
import dagshub
dagshub.init("nba_mlops", "joelaftreth", mlflow=True)
```

Add your DagsHub credentials to your environment variables in `docker-compose.yml` file:
- MLFLOW_TRACKING_USERNAME=mihrandovlatyan
- MLFLOW_TRACKING_PASSWORD=generated_token

This project uses MLFlow for experiment tracking, which is integrated with DagsHub. Make sure the tracking URI is set correctly in your `model_training.py` script:

`mlflow.set_tracking_uri("https://dagshub.com/joelaftreth/nba_mlops.mlflow")`

You can run the MLOps pipeline using Docker Compose:
```bash
docker compose up --build
```

## Logging and Visualization
DagsHub provides a comprehensive interface for visualizing your model training progress, metrics, and versioned artifacts. Navigate to your repository on DagsHub to explore these features.

***

## MLFlow Integration for Local Model Tracking
This project integrates MLFlow for local model tracking, enabling you to log model metrics and artifacts for better experiment management. The MLFlow tracking server runs locally and is demonstrated only on the localhost due to the lack of an external server URL.

### Prerequisites
Ensure that MLFlow is installed on your local machine. You can install it using pip:
```bash
pip install mlflow
```

### Running the MLFlow Tracking Server
To run the MLFlow tracking server locally, use the following command:
```bash
mlflow server --host 0.0.0.0 --port 6001
```
This command starts an MLFlow server on port 6001.

### MLFlow Configuration in the Project
The 'model_training.py' script has been updated to log model parameters, metrics, and the trained model itself to the MLFlow tracking server. The relevant changes include:

1. Set Tracking URI: The MLFlow tracking server URI is set to http://localhost:6001.
2. Set Experiment Name: The experiment name is set to nba_shot_prediction.
3. Start a Run: A new MLFlow run is started with a unique name based on the versioned filename.
4. Log Parameters: Model parameters like model_type, solver, C, and max_iter are logged.
5. Log Metrics: The accuracy of the model is logged as a metric.
6. Log Model: The trained model is logged using mlflow.sklearn.log_model.

### Running the Model Training Script
To execute the model_training.py script and track your machine learning experiments locally, navigate to the code/training_pipeline folder and run the script using:
```bash
python3 model_training.py
```

### Accessing the MLFlow UI
To visualize the experiments and logged data, open your web browser and navigate to:
```bash
http://localhost:6001
```
Here, you can explore the logged experiments, runs, parameters, metrics, and artifacts.

By following these steps and understanding the MLFlow integration, you can effectively manage and track your machine learning experiments locally.

***
## Recap & next steps

![NBA MLOps Next Steps Diagram](https://github.com/jja4/nba_mlops/blob/main/reports/figures/Recap_v2.png)

