import sys
import os
import pandas as pd

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from config.config import Config  # Import Config class from config package

def clean_data(data):
    """
    Clean the data by removing missing values and duplicates.

    Parameters:
    data (DataFrame): The input DataFrame to be cleaned.

    Returns:
    DataFrame: The cleaned DataFrame.
    """
    data = data.dropna()  # Drop missing values
    data = data.drop_duplicates()  # Drop duplicate rows
    return data

def transform_data(data):
    """
    Transform the data by encoding categorical and quantitative attributes.

    Parameters:
    data (DataFrame): The input DataFrame to be transformed.

    Returns:
    DataFrame: The transformed DataFrame.
    """
    data = transform_attributes_with_high_cardinality(data)
    data = one_hot_encoding(data)
    data = transform_quantitative_attributes_with_unique_ids(data)
    
    if 'Player Name' in data.columns:
        data.drop(['Player Name'], axis=1, inplace=True)  # Remove 'Player Name' column if exists
    if 'Team ID' in data.columns:
        data.drop(['Team ID'], axis=1, inplace=True)  # Remove 'Team ID' column if exists
        
    return data

def transform_quantitative_attributes_with_unique_ids(data):
    """
    Transform quantitative attributes with unique IDs by applying frequency encoding.

    Parameters:
    data (DataFrame): The input DataFrame.

    Returns:
    DataFrame: The DataFrame with frequency-encoded quantitative attributes.
    """
    frequency_encode_column(data, 'Game ID')
    frequency_encode_column(data, 'Game Event ID')
    frequency_encode_column(data, 'Player ID')
    data.drop(['Game ID', 'Game Event ID', 'Player ID'], axis=1, inplace=True)
    return data

def one_hot_encoding(data):
    """
    Perform one-hot encoding for each categorical column.

    Parameters:
    data (DataFrame): The input DataFrame.

    Returns:
    DataFrame: The DataFrame with one-hot encoded categorical attributes.
    """
    shot_type_encoded = pd.get_dummies(data['Shot Type'], prefix='ShotType', dtype=int)
    shot_zone_basic_encoded = pd.get_dummies(data['Shot Zone Basic'], prefix='ShotZoneBasic', dtype=int)
    shot_zone_area_encoded = pd.get_dummies(data['Shot Zone Area'], prefix='ShotZoneArea', dtype=int)
    shot_zone_range_encoded = pd.get_dummies(data['Shot Zone Range'], prefix='ShotZoneRange', dtype=int)
    season_type_encoded = pd.get_dummies(data['Season Type'], prefix='SeasonType', dtype=int)
    
    data = pd.concat([data, shot_type_encoded, shot_zone_basic_encoded, shot_zone_area_encoded, shot_zone_range_encoded, season_type_encoded], axis=1)
    data.drop(['Shot Type', 'Shot Zone Basic', 'Shot Zone Area', 'Shot Zone Range', 'Season Type'], axis=1, inplace=True)
    return data

def transform_attributes_with_high_cardinality(data):
    """
    Transform attributes with high cardinality by applying frequency encoding.

    Parameters:
    data (DataFrame): The input DataFrame.

    Returns:
    DataFrame: The DataFrame with frequency-encoded high cardinality attributes.
    """
    frequency_encode_column(data, 'Action Type')
    frequency_encode_column(data, 'Team Name')
    frequency_encode_column(data, 'Home Team')
    frequency_encode_column(data, 'Away Team')
    data.drop(['Action Type', 'Team Name', 'Home Team', 'Away Team'], axis=1, inplace=True)
    return data

def frequency_encode_column(data, column_name):
    """
    Perform frequency encoding on a specified column.

    Parameters:
    data (DataFrame): The input DataFrame.
    column_name (str): The name of the column to be frequency encoded.

    Returns:
    DataFrame: The DataFrame with the frequency-encoded column.
    """
    frequency = data[column_name].value_counts(normalize=True)
    data[column_name + '_Frequency'] = data[column_name].map(frequency)
    return data

def main():
    """
    Main function to load, clean, transform, and save the dataset.
    """
    input_file_path = '../../' + Config.OUTPUT_RAW_FILE
    output_file_path = '../../' + Config.OUTPUT_PREPROCESSED_FILE

    data = pd.read_csv(input_file_path)
    data = clean_data(data)
    data = transform_data(data)
    data.to_csv(output_file_path, index=False)

if __name__ == "__main__":
    main()
