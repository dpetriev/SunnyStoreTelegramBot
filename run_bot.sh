#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Set Python path to include the current directory
export PYTHONPATH="${PYTHONPATH}:/workspace"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt || handle_error "Failed to install dependencies"

# Run the bot
echo "Starting the bot..."
python3 -m bot