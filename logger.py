import logging
import os
import time

# Set timezone to UTC
os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
nba_logs_dir = os.path.join(project_dir, "logs")

# Set the path for the logs directory
if not os.path.exists(nba_logs_dir):
    os.makedirs(nba_logs_dir)

# Create logs.log file if it doesn't exist in the NBA logs directory
log_file = os.path.join(nba_logs_dir, "logs.log")
if not os.path.exists(log_file):
    open(log_file, 'a').close()

# Create logs directory if it doesn't exist
# logs_dir = "logs"
# if not os.path.exists(logs_dir):
#    os.makedirs(logs_dir)

# Create logs.log file if it doesn't exist
# log_file = os.path.join(logs_dir, "logs.log")
# if not os.path.exists(log_file):
#    open(log_file, 'a').close()

# Configure logging without specifying filename in basicConfig
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a'),  # Add a FileHandler for log.txt in append mode
        logging.StreamHandler()  # Add a StreamHandler for the console output
    ]
)

# Get a logger instance and expose it as part of the module
logger = logging.getLogger(__name__)

# Example usage within the module (optional)
logger.info("Custom logger module initialized.")
logger.info("---------------------------------")

