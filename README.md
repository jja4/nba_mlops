NBA MLOps
==============================
This project demonstrates MLOps best practices using a machine learning model that predicts if an NBA player will make a specific shot or not.

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
    │   ├── retrieve_data  <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── develop_models <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
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


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>



------------
Additional information
How to Use the `@app.post('/free_predict')` Endpoint
To reach the `/free_predict` endpoint and make a prediction, follow these steps:

1. Start the API
First, navigate to the `/code/api` directory and start the API using the following command in your terminal:

```bash
uvicorn nba_app:app
```
This command will start the FastAPI application and make it accessible at http://localhost:8000.

2. Make a POST Request
You can use Postman to make a POST request to the /free_predict endpoint. Here’s how:

2.1 Open Postman and create a new POST request.
2.2 Set the request URL to http://localhost:8000/free_predict.
2.3 In the Body tab, select raw and JSON.
2.4 Provide the following JSON object with values for the features used to train the model:
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
2.5 Send the request
2.6 Get the prediction (0 or 1)
