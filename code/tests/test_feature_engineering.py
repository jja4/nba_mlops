import sys
import os
import unittest
import pandas as pd

# Adjust sys.path to include the 'project' directory
# This allows the script to find and import the Config module
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from training_pipeline.feature_engineering import transform_date_attribute

class TestTransformDateAttribute(unittest.TestCase):
    
    def test_transform_date_attribute(self):
        # Create a sample DataFrame with 'Game Date' column
        data = pd.DataFrame({'Game Date': ['20230101', '20230215']})
        
        # Call the function
        transformed_data = transform_date_attribute(data.copy())
        
        # Check if columns 'Year', 'Month', 'Day', 'Day_of_Week' are created
        self.assertTrue('Year' in transformed_data.columns)
        self.assertTrue('Month' in transformed_data.columns)
        self.assertTrue('Day' in transformed_data.columns)
        self.assertTrue('Day_of_Week' in transformed_data.columns)
        
        # Check specific values (example)
        self.assertEqual(transformed_data['Year'].iloc[0], 2023)
        self.assertEqual(transformed_data['Month'].iloc[1], 2)
        self.assertIn(transformed_data['Day_of_Week'].iloc[0], [0, 1, 2, 3, 4, 5, 6])  # Ensure valid day of week
        
if __name__ == '__main__':
    unittest.main()
