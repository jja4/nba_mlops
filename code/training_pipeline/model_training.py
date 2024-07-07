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
import random
import dagshub

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
code_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)
sys.path.insert(0, code_dir)

from config.config import Config
from logger import logger

def load_best_metrics(metrics_file_path):
    """
    Load the best metrics from the specified file.
    
    Parameters:
    metrics_file_path (str): Path to the file containing the best metrics.
    
    Returns:
    dict: Dictionary containing the best metrics.
    """
    if os.path.exists(metrics_file_path):
        with open(metrics_file_path, 'r') as f:
            return json.load(f)
    else:
        return {'accuracy': 0}

def save_metrics(metrics_file_path, metrics):
    """
    Save the given metrics to the specified file.
    
    Parameters:
    metrics_file_path (str): Path to the file where the metrics will be saved.
    metrics (dict): Dictionary containing the metrics to save.
    """
    with open(metrics_file_path, 'w') as f:
        json.dump(metrics, f)

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

    # (solver='liblinear', C=1, max_iter=1000): this is the best params that we get from previous project
    # For demonstration purposes we are using a mechanism to pick up parameters randomly.
    # Define possible values for each parameter
    solvers = ['liblinear', 'saga', 'newton-cg', 'lbfgs']
    C_values = [0.01, 0.1, 1, 10, 100]
    max_iters = [100, 200, 500, 1000, 2000]

    # Randomly select a value for each parameter
    solver = random.choice(solvers)
    C = random.choice(C_values)
    max_iter = random.choice(max_iters)

    # Initialize the LogisticRegression model with the random parameters
    model = linear_model.LogisticRegression(solver=solver, C=C, max_iter=max_iter)

    # Print the selected parameters for reference
    print(f"Selected parameters: solver={solver}, C={C}, max_iter={max_iter}")

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
        # When we run it via github action, it gives an error: dagshub does not have init function.
        # This is because github action's dagshub version is different.
        # For github actions we use user-token env variables.
        dagshub.init("nba_mlops", "joelaftreth", mlflow=True)
    
    # Extract just the filename without the path and extension for the run name
    run_name = os.path.splitext(os.path.basename(versioned_filename))[0]

    # Initialize MLFlow tracking
    #mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:6001"))  # MLFlow tracking server URI
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/joelaftreth/nba_mlops.mlflow"))
    #mlflow.set_tracking_uri(https://dagshub.com/<DagsHub-user-name>/<repository-name>.mlflow)
    mlflow.set_experiment("nba_shot_prediction")  # Experiment name

    with mlflow.start_run(run_name=run_name):
        # Log parameters
        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("solver", solver)
        mlflow.log_param("C", C)
        mlflow.log_param("max_iter", max_iter)

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

def ensure_directory_exists(file_path):
    """
    Ensure the directory for the specified file path exists.
    
    Parameters:
    file_path (str): The file path for which the directory should be ensured.
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def main():
    """
    Main function to train the model and save it.
    """
    logger.info("(4) Starting the model training process.")

    # Path to the joblib file containing train and test datasets
    file_path = '../../' + Config.OUTPUT_TRAIN_TEST_JOBLIB_FILE

    # Base filename for the output model file
    base_output_file_path = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR

    # Base filename for the discarded model file
    discarded_output_file_path = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR_DISCARDED

    # Train the logistic regression model
    log_to_mlflow = os.getenv("LOG_TO_MLFLOW", "true").lower() == "true"
    model, new_accuracy, versioned_filename = train_model(file_path, base_output_file_path, log_to_mlflow)
    
    metrics_file = '../../best_model_metrics.json'
    
    # Load the best accuracy from metrics file
    best_metrics = load_best_metrics(metrics_file)
    best_accuracy = best_metrics.get('accuracy', 0)

    # Print new accuracy
    print(f"New Accuracy: {new_accuracy}")
    print(f"Best current Accuracy: {best_accuracy}")

    if new_accuracy > best_accuracy:
        # Save the model to the original path
        ensure_directory_exists(versioned_filename)
        dump(model, versioned_filename)
        logger.info("Model file data saved successfully.")
        logger.info(versioned_filename)

        # Save new metrics as the best metrics
        new_metrics = {'accuracy': new_accuracy}
        save_metrics(metrics_file, new_metrics)

        # Create the signal file indicating a new model version
        open('../../signal_new_model_version', 'w').close()
        print("Creating signal file /app/signal_new_model_version...")
    else:
        # Save the model to the discarded path
        discarded_filename = generate_versioned_filename(discarded_output_file_path, 1)
        ensure_directory_exists(discarded_filename)
        dump(model, discarded_filename)
        logger.info("Model file data saved in discarded folder.")
        logger.info(discarded_filename)
    
    # Always create this signal file at the end of model training
    open('signal_model_training_done', 'w').close()
    
    logger.info("Model training completed.")
    logger.info("-----------------------------------")

if __name__ == "__main__":
    main()
