import sys
import os
import unittest
import pandas as pd

# Adjust sys.path to include the 'project' directory
# This allows the script to find and import the Config module
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_dir)

from training_pipeline.data_processing import clean_data, transform_data, frequency_encode_column, transform_attributes_with_high_cardinality, transform_quantitative_attributes_with_unique_ids, one_hot_encoding

class TestDataPreprocessing(unittest.TestCase):

    def setUp(self):
        # Create sample data for testing
        self.data = pd.DataFrame({
            'Game ID': [1, 2, 3, 3, 4],
            'Game Event ID': [101, 102, 103, 103, 104],
            'Player ID': [201, 202, 203, 203, 204],
            'Shot Type': ['Jump Shot', 'Layup', 'Dunk', 'Dunk', 'Jump Shot'],
            'Shot Zone Basic': ['Mid-Range', 'Restricted Area', 'Paint', 'Paint', 'Mid-Range'],
            'Shot Zone Area': ['Right Side(R)', 'Center(C)', 'Center(C)', 'Center(C)', 'Right Side(R)'],
            'Shot Zone Range': ['8-16 ft.', 'Less Than 8 ft.', 'Less Than 8 ft.', 'Less Than 8 ft.', '8-16 ft.'],
            'Season Type': ['Regular Season', 'Playoffs', 'Regular Season', 'Regular Season', 'Regular Season'],
            'Action Type': ['Jump Shot', 'Layup', 'Dunk', 'Dunk', 'Jump Shot'],
            'Team Name': ['Team A', 'Team B', 'Team C', 'Team C', 'Team A'],
            'Home Team': ['Team A', 'Team A', 'Team B', 'Team B', 'Team C'],
            'Away Team': ['Team B', 'Team B', 'Team A', 'Team A', 'Team B']
        })

    def test_clean_data(self):
        cleaned_data = clean_data(self.data)
        self.assertEqual(len(cleaned_data), 4)  # Check if duplicates are removed

    def test_frequency_encode_column(self):
        frequency_encoded_data = frequency_encode_column(self.data, 'Game ID')
        self.assertIn('Game ID_Frequency', frequency_encoded_data.columns)  # Check if frequency encoding is applied

    def test_transform_quantitative_attributes_with_unique_ids(self):
        transformed_data = transform_quantitative_attributes_with_unique_ids(self.data)
        self.assertNotIn('Game ID', transformed_data.columns)  # Check if columns are dropped

    def test_transform_attributes_with_high_cardinality(self):
        transformed_data = transform_attributes_with_high_cardinality(self.data)
        self.assertNotIn('Action Type', transformed_data.columns)  # Check if columns are dropped

    def test_transform_data(self):
        transformed_data = transform_data(self.data)
        self.assertNotIn('Player Name', transformed_data.columns)  # Check if columns are dropped

    def test_one_hot_encoding(self):
        transformed_data = one_hot_encoding(self.data)
        self.assertNotIn('Shot Type', transformed_data.columns)  # Check if columns are dropped
        self.assertTrue(transformed_data.columns.str.startswith('ShotType').any())  # Check for one-hot encoded columns

if __name__ == '__main__':
    unittest.main()
