import sys
import os
import pandas as pd
import logging

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Set up logging
logging.basicConfig(level=logging.INFO)

from config.config import Config  # Import Config class from config package

def fetch_data_from_csv(file_path):
    """
    Reads data from a CSV file.

    Parameters:
    file_path (str): The path to the CSV file to read.

    Returns:
    DataFrame: A pandas DataFrame containing the data from the CSV file.
    """
    try:
        logging.info(f"Reading data from CSV file: {file_path}")
        data = pd.read_csv(file_path)
        logging.info("Data read successfully from CSV file.")
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
    logging.info("Validating data.")
    if data.empty:
        logging.warning("Data is empty.")
    else:
        logging.info("Data validation passed.")
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
    logging.info("Appending new data to existing data.")
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)
    logging.info("Data appended successfully.")
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
    
    logging.info(f"Saving data to CSV file: {file_path}")
    data.to_csv(file_path, index=False)
    logging.info("Data saved successfully.")

def main():
    """
    Main function to execute the data processing workflow:
    - Fetches new data from a CSV file.
    - Validates the new data.
    - Appends the new data to existing data if it exists.
    - Saves the combined data to a CSV file.
    """
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

if __name__ == "__main__":
    main()
