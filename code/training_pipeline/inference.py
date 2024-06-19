import sys
import os
import pandas as pd
from joblib import load
from sklearn.model_selection import train_test_split
import logging

# Adjust sys.path to include the 'project' directory
# This allows the script to find and import the Config module
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Set up logging
logging.basicConfig(level=logging.INFO)

from config.config import Config  # Import Config class from config package

def load_model(model_path):
    """
    Load the machine learning model from the specified path.

    Parameters:
    model_path (str): The file path to the saved model.

    Returns:
    model: The loaded model.
    """
    model = load(model_path)
    return model

def make_predictions(model, new_data):
    """
    Make predictions using the provided model and new data.

    Parameters:
    model: The trained model used for making predictions.
    new_data (DataFrame or array-like): The data for which predictions are to be made.

    Returns:
    array: The predictions made by the model.
    """
    predictions = model.predict(new_data)
    return predictions

def main():
    """
    Main function to load datasets, load the model, make predictions, and save the predictions.
    """
    # Path to the joblib file containing train and test datasets
    file_path = '../../' + Config.OUTPUT_TRAIN_TEST_JOBLIB_FILE

    # Load the train and test datasets
    X_train, X_test, y_train, y_test = load(file_path)
    
    # Use the test dataset as new data for making predictions
    new_data = X_test

    # Load the trained model
    model = load_model('../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR)
    
    # Make predictions using the model
    predictions = make_predictions(model, new_data)
    print(f"Predictions: {predictions}")

    print(f"Predictions: {X_test.shape}")
    
    # Save predictions to a CSV file
    output_file_path = '../../' + Config.OUTPUT_PREDICTIONS_RESULTS_FILE
    pd.DataFrame(predictions, columns=['Prediction']).to_csv(output_file_path, index=False)
    logging.info("Prediction file data saved successfully.")
    logging.info(output_file_path)

if __name__ == "__main__":
    main()
