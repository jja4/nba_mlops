import sys
import os
import unittest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock

# Adjust sys.path to include the 'project' directory
# This allows the script to find and import the Config module
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Mock the config module
class Config:
    NEW_DATA_FILE = 'new_data.csv'
    OUTPUT_RAW_FILE = 'output_data.csv'

# Import functions to be tested
from training_pipeline.data_ingestion import fetch_data_from_csv, validate_data, append_data, save_data

class TestDataIngestion(unittest.TestCase):

    @patch('training_pipeline.data_ingestion.pd.read_csv')
    def test_fetch_data_from_csv(self, mock_read_csv):
        # Test reading a valid CSV file
        mock_read_csv.return_value = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        result = fetch_data_from_csv('valid.csv')
        pd.testing.assert_frame_equal(result, pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}))
        
        # Test handling a FileNotFoundError
        mock_read_csv.side_effect = FileNotFoundError
        result = fetch_data_from_csv('invalid.csv')
        self.assertTrue(result.empty)

    def test_validate_data(self):
        # Test with valid data
        data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        result = validate_data(data)
        pd.testing.assert_frame_equal(result, data)
        
        # Test with empty data
        data = pd.DataFrame()
        result = validate_data(data)
        self.assertTrue(result.empty)

    def test_append_data(self):
        # Test appending non-empty DataFrames
        existing_data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        new_data = pd.DataFrame({'col1': [5, 6], 'col2': [7, 8]})
        result = append_data(existing_data, new_data)
        expected_data = pd.DataFrame({'col1': [1, 2, 5, 6], 'col2': [3, 4, 7, 8]})
        pd.testing.assert_frame_equal(result, expected_data)
        
        # Test appending an empty DataFrame
        empty_data = pd.DataFrame()
        result = append_data(existing_data, empty_data)
        pd.testing.assert_frame_equal(result, existing_data)

        # Test appending to an empty DataFrame
        result = append_data(empty_data, new_data)
        pd.testing.assert_frame_equal(result, new_data)

    @patch('training_pipeline.data_ingestion.pd.DataFrame.to_csv')
    @patch('training_pipeline.data_ingestion.os.makedirs')
    def test_save_data(self, mock_makedirs, mock_to_csv):
        # Test saving data to a CSV file
        data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        save_data(data, 'output.csv')
        
        # Ensure directories are created if they don't exist
        mock_makedirs.assert_called_once_with(os.path.dirname('output.csv'), exist_ok=True)
        # Ensure data is saved to CSV
        mock_to_csv.assert_called_once_with('output.csv', index=False)

if __name__ == '__main__':
    unittest.main()
