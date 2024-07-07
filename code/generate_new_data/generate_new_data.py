import sys
import os
import pandas as pd
import numpy as np

# Adjust sys.path to include the 'project' directory
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

from config.config import Config

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_dir)

from logs.logger import logger

logger.info("Generating a new data is starting.")

# For demonstration, assume we have a large dataset 'NBA Shot Locations 1997 - 2020-original.csv'
# Replace this with actual data loading logic
big_data = pd.read_csv(Config.ORIGINAL_BIG_DATA_FILE)

# Shuffle and select a small portion to simulate new data
small_data = big_data.sample(frac=0.1)  # Adjust frac as needed
print(f"Size of new data set is: {small_data.shape}")

# Save this small portion as new_data.csv
print(f"Saving CSV to: {Config.NEW_DATA_FILE}")
small_data.to_csv(Config.NEW_DATA_FILE, index=False)

logger.info("Generating a new data was finished.")
logger.info("---------------------------------")
