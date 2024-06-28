import sys
import os
import pandas as pd
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from joblib import load, dump
from sklearn.preprocessing import StandardScaler
import logging
import datetime

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Set up logging
log_file = os.path.join(project_dir, 'log.txt')

# Set up logging to file with timestamp and append mode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a'),  # Add a FileHandler for log.txt in append mode
        logging.StreamHandler()  # Add a StreamHandler for the console output
    ]
)

from config.config import Config  # Import Config class from config package

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
    
    return model

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
    model = train_model(file_path)
    
    # Determine the output file path with versioning
    base_output_file_path = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR
    version = 1
    while True:
        output_file_path = generate_versioned_filename(base_output_file_path, version)
        if not os.path.exists(output_file_path):
            break
        version += 1

    # Save the trained model to a file
    output_file_path = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR
    dump(model, output_file_path)

    logging.info("Model file data saved successfully.")
    logging.info(output_file_path)

    # Each service script creates its signal file at the end
    open('signal_model_training_done', 'w').close()

    logging.info("Model training completed.")
    logging.info("-----------------------------------")

if __name__ == "__main__":
    main()
