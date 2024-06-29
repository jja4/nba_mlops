import sys
import os
import pandas as pd
from sklearn import linear_model
from sklearn.metrics import accuracy_score
from joblib import load, dump
import logging
import datetime
import json

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

log_file = os.path.join(project_dir, 'log.txt')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a'),
        logging.StreamHandler()
    ]
)

from config.config import Config

def train_model(file_path):
    """
    Train a logistic regression model on the provided dataset.

    Parameters:
    file_path (str): Path to the joblib file containing the train and test datasets.

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
    logging.info("(4) Starting the model training process.")

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

    if new_accuracy > best_accuracy:
        base_output_file_path = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR
        version = 1
        while True:
            output_file_path = generate_versioned_filename(base_output_file_path, version)
            if not os.path.exists(output_file_path):
                break
            version += 1
        dump(model, output_file_path)
        logging.info("Model file data saved successfully.")
        logging.info(output_file_path)

        new_metrics = {'accuracy': new_accuracy}
        with open(metrics_file, 'w') as f:
            json.dump(new_metrics, f)

        # Create the signal file indicating a new model version
        open('../../signal_new_model_version', 'w').close()
    
    # Always create this signal file at the end of model training
    open('signal_model_training_done', 'w').close()
    
    logging.info("Model training completed.")
    logging.info("-----------------------------------")

if __name__ == "__main__":
    main()
