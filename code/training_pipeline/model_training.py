import warnings
warnings.filterwarnings("ignore", category=UserWarning, message="Setuptools is replacing distutils.")

import sys
import os
import pandas as pd
from sklearn import linear_model
from sklearn.metrics import accuracy_score
from joblib import load, dump
import datetime
import json
import mlflow
import mlflow.sklearn

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from config.config import Config
from logger import logger

def train_model(file_path, output_base_filename, log_to_mlflow=True):
    """
    Train a logistic regression model on the provided dataset and log metrics with MLFlow.

    Parameters:
    file_path (str): Path to the joblib file containing the train and test datasets.
    output_base_filename (str): Base filename for saving the model.
    log_to_mlflow (bool): Whether to log metrics to MLFlow.

    Returns:
    model: Trained logistic regression model.
    """

    # Load train and test datasets from joblib file
    X_train, X_test, y_train, y_test = load(file_path)

    # Initialize logistic regression model with 'liblinear' solver
    model = linear_model.LogisticRegression(solver='liblinear', C=1, max_iter=1000)

    # Fit the model to the training data
    model.fit(X_train, y_train)
    
    # Predict the target variable for the test set
    predictions = model.predict(X_test)

    # Calculate accuracy of the model
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model Accuracy: {accuracy}")
    
    # Generate versioned filename
    version = 1
    while True:
        versioned_filename = generate_versioned_filename(output_base_filename, version)
        if not os.path.exists(versioned_filename):
            break
        version += 1

    if log_to_mlflow:
        # Extract just the filename without the path and extension for the run name
        run_name = os.path.splitext(os.path.basename(versioned_filename))[0]

        # Initialize MLFlow tracking
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:6001"))  # MLFlow tracking server URI
        mlflow.set_experiment("nba_shot_prediction")  # Experiment name

        with mlflow.start_run(run_name=run_name):
            # Log parameters
            mlflow.log_param("model_type", "LogisticRegression")
            mlflow.log_param("solver", "liblinear")
            mlflow.log_param("C", 1)
            mlflow.log_param("max_iter", 1000)

            # Log metrics
            mlflow.log_metric("accuracy", accuracy)

            # Log the trained model
            mlflow.sklearn.log_model(model, "model")

    return model, accuracy, versioned_filename

def generate_versioned_filename(base_filename, version):
    """
    Generate a versioned filename based on base_filename, version number, and current date.
    Example: If base_filename='model', version=1, it will generate 'model-v1-20240628.joblib'
    """
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    return f"{base_filename}-v{version}-{current_date}.joblib"

def main():
    """
    Main function to train the model and save it.
    """
    logger.info("(4) Starting the model training process.")

    # Path to the joblib file containing train and test datasets
    file_path = '../../' + Config.OUTPUT_TRAIN_TEST_JOBLIB_FILE

    # Base filename for the output model file
    base_output_file_path = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR

    # Train the logistic regression model
    log_to_mlflow = os.getenv("LOG_TO_MLFLOW", "true").lower() == "true"
    model, new_accuracy, versioned_filename = train_model(file_path, base_output_file_path, log_to_mlflow)
    
    metrics_file = '../../best_model_metrics.json'
    
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            best_metrics = json.load(f)
        best_accuracy = best_metrics.get('accuracy', 0)
    else:
        best_accuracy = 0

    # Print new accuracy
    print(f"New Accuracy: {new_accuracy}")
    print(f"Best current Accuracy: {best_accuracy}")

    dump(model, versioned_filename)
    logger.info("Model file data saved successfully.")
    logger.info(versioned_filename)

    if new_accuracy > best_accuracy:
        new_metrics = {'accuracy': new_accuracy}
        with open(metrics_file, 'w') as f:
            json.dump(new_metrics, f)

        # Create the signal file indicating a new model version
        open('../../signal_new_model_version', 'w').close()
        print("Creating signal file /app/signal_new_model_version...")
    
    # Always create this signal file at the end of model training
    open('signal_model_training_done', 'w').close()
    
    logger.info("Model training completed.")
    logger.info("-----------------------------------")

if __name__ == "__main__":
    main()
