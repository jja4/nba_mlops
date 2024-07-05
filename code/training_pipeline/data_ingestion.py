import sys
import os
import pandas as pd
import logging

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_dir)

from logger import logger

code_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, code_dir)

from config.config import Config

def fetch_data_from_csv(file_path):
    """
    Reads data from a CSV file.

    Parameters:
    file_path (str): The path to the CSV file to read.

    Returns:
    DataFrame: A pandas DataFrame containing the data from the CSV file.
    """
    try:
        logger.info(f"Reading data from CSV file: {file_path}")
        data = pd.read_csv(file_path)
        logger.info("Data read successfully from CSV file.")
        return data
    except FileNotFoundError as e:
        logging.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

def validate_data(data):
    """
    Validates the data.

    Parameters:
    data (DataFrame): The pandas DataFrame to validate.

    Returns:
    DataFrame: The validated DataFrame.
    """
    logger.info("Validating data.")
    if data.empty:
        logging.warning("Data is empty.")
    else:
        logger.info("Data validation passed.")
    return data

def append_data(existing_data, new_data):
    """
    Appends new data to existing data.

    Parameters:
    existing_data (DataFrame): The existing data.
    new_data (DataFrame): The new data to append.

    Returns:
    DataFrame: A pandas DataFrame containing the combined data.
    """
    logger.info("Appending new data to existing data.")
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    logger.info("Data appended successfully.")
    return combined_data

def save_data(data, file_path):
    """
    Saves data to a CSV file.

    Parameters:
    data (DataFrame): The data to save.
    file_path (str): The path to the CSV file to save.
    """
    # Create parent directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    logger.info(f"Saving data to CSV file: {file_path}")
    data.to_csv(file_path, index=False)
    logger.info("Data saved successfully.")

def main():
    """
    Main function to execute the data processing workflow:
    - Fetches new data from a CSV file.
    - Validates the new data.
    - Appends the new data to existing data if it exists.
    - Saves the combined data to a CSV file.
    """
    logger.info("(1) Starting the data ingestion process.")

    input_file_path = '../../' + Config.NEW_DATA_FILE
    output_file_path = '../../' + Config.OUTPUT_RAW_FILE
    
    # Fetch new data
    new_data = fetch_data_from_csv(input_file_path)
    
    # Validate new data
    validated_new_data = validate_data(new_data)
    
    # Check if raw data file already exists and read it
    if os.path.exists(output_file_path):
        existing_data = fetch_data_from_csv(output_file_path)
    else:
        existing_data = pd.DataFrame()
    
    # Append new data to existing data
    combined_data = append_data(existing_data, validated_new_data)
    
    # Save combined data
    save_data(combined_data, output_file_path)

    # Each service script creates its signal file at the end
    open('signal_data_ingestion_done', 'w').close()

    logger.info("Data ingestion process completed.")
    logger.info("---------------------------------")

if __name__ == "__main__":
    main()
