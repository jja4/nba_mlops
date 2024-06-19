import os
import sys
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from joblib import load

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from training_pipeline.model_training import train_model

def test_train_model():

    # Generate synthetic data
    file_path = '../../data/processed/NBA Shot Locations 1997 - 2020-train-test.joblib'  # Update with actual path
    print(f"Loading data from: {file_path}")

    X_train, X_test, y_train, y_test = load(file_path)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")
    
    # Train the model
    model = train_model(file_path)  # Assuming train_model takes file_path
    
    # Predict on the test set
    predictions = model.predict(X_test)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, predictions)
    
    # Assert that accuracy is reasonable (e.g., above a certain threshold)
    assert accuracy >= 0.6, f"Accuracy too low: {accuracy}"

if __name__ == "__main__":
    test_train_model()
