import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from joblib import dump
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

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
    
    # Save the train and test sets in a joblib file
    dump((X_train, X_test, y_train, y_test), '../../data/processed/NBA Shot Locations 1997 - 2020-train-test.joblib')
    logging.info("New joblib file generated successfully.")

def main():
    """
    Main function to load the data, create features, and save the processed train and test sets.
    """
    # Load the processed data from CSV file
    data = pd.read_csv('../../data/processed/NBA Shot Locations 1997 - 2020-processed.csv')
    
    # Create features
    data = create_features(data)
    
    # Split and save the train and test sets
    split_train_and_test_parts(data)

if __name__ == "__main__":
    main()
