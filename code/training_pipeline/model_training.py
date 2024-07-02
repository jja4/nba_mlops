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

def train_model(file_path):
    """
    Train a logistic regression model on the provided dataset and log metrics with MLFlow.

    Parameters:
    file_path (str): Path to the joblib file containing the train and test datasets.

    Returns:
    model: Trained logistic regression model.
    """
    # Generate versioned filename for the model
    versioned_model_path = generate_versioned_filename('../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR, 1)

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
    
    # Initialize MLFlow tracking
    mlflow.set_tracking_uri("http://localhost:6001")  # MLFlow tracking server URI
    mlflow.set_experiment("nba_shot_prediction")  # Experiment name

    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("solver", "liblinear")
        mlflow.log_param("C", 1)
        mlflow.log_param("max_iter", 1000)

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)

        # Log the trained model
        mlflow.sklearn.log_model(model, "model")

        # Ensure the directory exists for saving the model
        os.makedirs(os.path.dirname(versioned_model_path), exist_ok=True)

        # Save the model locally
        dump(model, versioned_model_path)
        logger.info(f"Model saved locally: {versioned_model_path}")

    return model, accuracy

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

    # Train the logistic regression model
    model, new_accuracy = train_model(file_path)
    
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

    if new_accuracy > best_accuracy:
        base_output_file_path = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR
        version = 1
        while True:
            output_file_path = generate_versioned_filename(base_output_file_path, version)
            if not os.path.exists(output_file_path):
                break
            version += 1
        dump(model, output_file_path)
        logger.info("Model file data saved successfully.")
        logger.info(output_file_path)

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
