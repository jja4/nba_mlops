import pandas as pd
from joblib import dump, load
import numpy as np
import sklearn

## basic script to load data examples and a pretrained model
## and use it to make predictions

# # instead of loading from csv, and preprocessing, load the data from 
# the joblib file in data directory one level up
# df = pd.read_csv('NBA Shot Locations 1997 - 2020.csv')

# load the data from the joblib file in data directory one level up
X_train_full, X_test_full, y_train_full, y_test_full = joblib.load(
    'data/processed/NBA Shot Locations 1997 - 2020-Report2-train-test.joblib')
model_rf = load('model_best_rf.joblib')

percentage = 0.01    # 1% of the full dataset, which is about 40k rows

# Take 1% of the full dataset
sample_size = int(len(X_train_full) * percentage)

# Take a random sample of the data
random_indices = np.random.choice(len(X_train_full), sample_size, replace=False)
X_train = X_train_full.iloc[random_indices]
y_train = y_train_full.iloc[random_indices]

# Similarly, take a same sample of the test set
sample_size_test = int(len(X_test_full) * percentage)
random_indices_test = np.random.choice(len(X_test_full), sample_size_test, replace=False)
X_test = X_test_full.iloc[random_indices_test]
y_test = y_test_full.iloc[random_indices_test]

y_pred = model_rf.predict(X_test)
