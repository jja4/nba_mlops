#!/bin/bash

echo "Starting entrypoint.sh..."
echo "WAIT_FOR_FILE: $WAIT_FOR_FILE"
echo "WAIT_FOR_PREV_FILE: $WAIT_FOR_PREV_FILE"

# Remove the old signal file if it exists
if [ "$WAIT_FOR_FILE" ]; then
  if [ -f $WAIT_FOR_FILE ]; then
    echo "Removing old signal file $WAIT_FOR_FILE..."
    rm -f $WAIT_FOR_FILE
  fi
fi

# Wait for the presence of the previous step's signal file
if [ "$WAIT_FOR_PREV_FILE" ]; then
  echo "Waiting for file $WAIT_FOR_PREV_FILE..."
  while [ ! -f $WAIT_FOR_PREV_FILE ]; do
    sleep 2  # Pause for 2 seconds before checking again
  done
  echo "File $WAIT_FOR_PREV_FILE found, proceeding..."
fi

# Run the main command
"$@"

# After the main command finishes, remove the previous step's signal file
#if [ "$WAIT_FOR_PREV_FILE" ]; then
  #echo "Removing previous step's signal file $WAIT_FOR_PREV_FILE..."
  #rm -f $WAIT_FOR_PREV_FILE
#fi

# Create the signal file for the next step
if [ "$WAIT_FOR_FILE" ]; then
  echo "Creating signal file $WAIT_FOR_FILE..."
  touch $WAIT_FOR_FILE
fi

echo "Entrypoint script finished."
