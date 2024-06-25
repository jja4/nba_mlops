class Config:
    DATA_DIR = 'data/'
    NEW_DATA_DIR = 'data/new_data/'             # Place for saving fresh new data, which can be used for retraining
    RAW_DATA_DIR = 'data/raw/'                  # Place for saving validated dats in the early stage of training pipeline
    PROCESSED_DATA_DIR = 'data/processed/'      # Place for saving preprocessed and feature engineered data
    TRAINED_MODEL_DIR = 'trained_models/'       # Place for saving trained models
    PREDICTIONS_DATA_DIR = 'data/predictions/'  # Place for saving prediction results

    NEW_DATA_FILE = 'data/new_data/new_data.csv'    # contains fresh new data
    ORIGINAL_BIG_DATA_FILE = 'data/raw/NBA Shot Locations 1997 - 2020-original.csv'  # original big data
    OUTPUT_RAW_FILE = 'data/raw/NBA Shot Locations 1997 - 2020.csv' # validated data
    OUTPUT_PREPROCESSED_FILE = 'data/processed/NBA Shot Locations 1997 - 2020-processed.csv'    # preprocessed data
    OUTPUT_TRAIN_TEST_JOBLIB_FILE = 'data/processed/NBA Shot Locations 1997 - 2020-train-test.joblib'   # Splitted data for training and testing
    OUTPUT_TRAINED_MODEL_FILE_LR = 'trained_models/model_best_lr.joblib'    # Trained Logistic Regression model file
    OUTPUT_PREDICTIONS_RESULTS_FILE = 'data/predictions/predictions.csv'  # Prediction results
    
