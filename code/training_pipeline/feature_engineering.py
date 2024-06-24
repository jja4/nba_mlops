import sys
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from joblib import dump
import logging

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from config.config import Config  # Import Config class from config package

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

def create_features(data):
    """
    Function to create new features from the existing dataset.
    Currently, it only includes transforming the date attribute.
    
    Args:
    data (pd.DataFrame): The input dataframe containing the data.
    
    Returns:
    pd.DataFrame: The dataframe with new features added.
    """
    data = transform_date_attribute(data)
    return data

def transform_date_attribute(data):
    """
    Function to transform the 'Game Date' attribute into multiple datetime components.
    
    Args:
    data (pd.DataFrame): The input dataframe containing the 'Game Date' column.
    
    Returns:
    pd.DataFrame: The dataframe with 'Game Date' transformed into year, month, day, and day of the week.
    """
    # Tranform the date into a datetime format
    data['Game Date'] = pd.to_datetime(data['Game Date'], format='%Y%m%d')

    # Extract components
    data['Year'] = data['Game Date'].dt.year
    data['Month'] = data['Game Date'].dt.month
    data['Day'] = data['Game Date'].dt.day
    data['Day_of_Week'] = data['Game Date'].dt.dayofweek  # Monday = 0, Sunday = 6

    # Remove 'Game Date' column.
    data.drop('Game Date', axis=1, inplace=True)

    return data

def split_train_and_test_parts(data):
    """
    Function to split the dataset into training and testing parts,
    and save them as a joblib file.
    
    Args:
    data (pd.DataFrame): The input dataframe with features and target variable.
    """
    # Separate features and target variable
    features = data.drop('Shot Made Flag', axis=1)
    target = data['Shot Made Flag']

    # Split the data into training and testing sets with 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=66)
    
    # Standardization
    scaler = StandardScaler()

    # Columns to be standardized
    columns_to_scale = ['Period',
                        'Minutes Remaining',
                        'Seconds Remaining', 
                        'Shot Distance', 
                        'X Location', 
                        'Y Location']

    # Scale the features for train set and replace the original columns with the scaled features
    X_train[columns_to_scale] = scaler.fit_transform(X_train[columns_to_scale])

    # Scale the features for test set and replace the original columns with the scaled features
    X_test[columns_to_scale] = scaler.transform(X_test[columns_to_scale])
    
    # Save the train and test sets in a joblib file
    output_file_path = '../../' + Config.OUTPUT_TRAIN_TEST_JOBLIB_FILE
    dump((X_train, X_test, y_train, y_test), output_file_path)
    logging.info("New joblib file generated successfully.")
    logging.info(output_file_path)

def main():
    """
    Main function to load the data, create features, and save the processed train and test sets.
    """
    logging.info("(3) Starting the feature engineering process.")

    # Load the processed data from CSV file
    input_file_path = '../../' + Config.OUTPUT_PREPROCESSED_FILE
    logging.info(f"Loading data from {input_file_path}.")
    data = pd.read_csv(input_file_path)
    
    # Create features
    data = create_features(data)
    
    # Split and save the train and test sets
    split_train_and_test_parts(data)

    logging.info("Data processing completed.")
    logging.info("-----------------------------------")

if __name__ == "__main__":
    main()
