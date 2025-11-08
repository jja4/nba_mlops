import unittest
import pandas as pd
from sklearn import linear_model
from training_pipeline.inference import make_predictions


class TestMakePredictions(unittest.TestCase):
    def setUp(self):
        # Define a mock model (replace with your actual mock model)
        self.mock_model = linear_model.LogisticRegression()

        # Mock the predict method to avoid NotFittedError
        self.mock_model.predict = unittest.mock.Mock(return_value=[0, 1, 0, 1, 0])

        # Prepare mock data for predictions
        self.mock_data = pd.DataFrame({
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

    def test_make_predictions(self):
        # Test the make_predictions function with the mock model and mock data
        predictions = make_predictions(self.mock_model, self.mock_data)

        # Assertions based on the expected behavior of your make_predictions function
        self.assertEqual(predictions, [0, 1, 0, 1, 0])


if __name__ == '__main__':
    unittest.main()
