import sys
import os
import pandas as pd
from joblib import load
from sklearn.model_selection import train_test_split
import logging
import glob

# Adjust sys.path to include the 'project' directory
# This allows the script to find and import the Config module
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_dir)

from logger import logger

code_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, code_dir)

from config.config import Config

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

def find_latest_versioned_model(base_filename):
    """
    Find the latest versioned model file based on base_filename.
    Returns the path to the latest versioned model file.
    """
    search_pattern = f"{base_filename}-v*-*.joblib"
    files = glob.glob(search_pattern)
    
    if not files:
        raise FileNotFoundError(f"No model files found with pattern '{search_pattern}'")
    
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def main():
    """
    Main function to load datasets, load the model, make predictions, and save the predictions.
    """
    logger.info("(5) Starting the model prediction process.")

    # Check if a new model version signal file exists
    new_model_signal_file = '../../signal_new_model_version'
    if not os.path.exists(new_model_signal_file):
        logger.info("No new model version found. Skipping inference.")
        logger.info("-----------------------------------")
        return

    try:
        # Path to the joblib file containing train and test datasets
        file_path = '../../' + Config.OUTPUT_TRAIN_TEST_JOBLIB_FILE

        # Load the train and test datasets
        X_train, X_test, y_train, y_test = load(file_path)

        # Path to the base filename of the model
        base_model_filename = '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR

        # Find the latest versioned model file
        latest_model_file = find_latest_versioned_model(base_model_filename)
        
        print('Last version model path:')
        print(latest_model_file)

        # Load the model
        model = load(latest_model_file)
        
        # Make predictions using the model
        predictions = make_predictions(model, X_test)
        print(f"Predictions: {predictions}")
        
        # Save predictions to a CSV file
        output_file_path = '../../' + Config.OUTPUT_PREDICTIONS_RESULTS_FILE
        pd.DataFrame(predictions, columns=['Prediction']).to_csv(output_file_path, index=False)
        logger.info("Prediction file data saved successfully.")
        logger.info(output_file_path)

        # Each service script creates its signal file at the end
        open('signal_inference_done', 'w').close()

        logger.info("Model inference completed.")
        logger.info("-----------------------------------")
    
    finally:
        # Remove the signal_new_model_version file regardless of success or failure
        if os.path.exists(new_model_signal_file):
            os.remove(new_model_signal_file)
            logger.info("Removed signal_new_model_version file.")
            print("Removed signal_new_model_version file.")

if __name__ == "__main__":
    main()
