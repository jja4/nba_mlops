import sys
import os
import pandas as pd
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from joblib import load, dump
from sklearn.preprocessing import StandardScaler

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from config.config import Config  # Import Config class from config package

def train_model(file_path):
    """
    Train a logistic regression model on the provided dataset.

    Parameters:
    file_path (str): Path to the joblib file containing the train and test datasets.

    Returns:
    model: Trained logistic regression model.
    """
    # Load train and test datasets from joblib file
    X_train, X_test, y_train, y_test = load(file_path)

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

    # Initialize logistic regression model with 'liblinear' solver
    model = linear_model.LogisticRegression(solver='liblinear', C=1, max_iter=1000)

    # Fit the model to the training data
    model.fit(X_train, y_train)
    
    # Predict the target variable for the test set
    predictions = model.predict(X_test)

    # Calculate accuracy of the model
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model Accuracy: {accuracy}")
    
    return model

def main():
    """
    Main function to train the model and save it.
    """
    # Path to the joblib file containing train and test datasets
    file_path = '../../' + Config.OUTPUT_TRAIN_TEST_JOBLIB_FILE

    # Train the logistic regression model
    model = train_model(file_path)
    
    # Save the trained model to a file
    dump(model, '../../' + Config.OUTPUT_TRAINED_MODEL_FILE_LR)

if __name__ == "__main__":
    main()
