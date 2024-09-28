#!/bin/bash

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null
then
    echo "pipenv is not installed. Installing pipenv..."
    pip install --user pipenv
    
    if ! command -v pipenv &> /dev/null
    then
        echo "Failed to install pipenv. Please install it manually."
        exit 1
    fi
else
    echo "pipenv is already installed."
fi

# Install project dependencies using Pipfile
echo "Installing project dependencies..."
pipenv install

# Check if the installation was successful
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Please check the Pipfile."
    exit 1
fi

# Add the remanufacturing lab root path in the .env file
KEY="PROJECT_ROOT_PATH"
PROJECT_ROOT=$(git rev-parse --show-toplevel)
if grep -q "^$KEY=" ".env"; then
    echo "$KEY found in $ENV_FILE. Updating its value."
    sed -i "s|^$KEY=.*|$KEY=$PROJECT_ROOT|" ".env"
else
    echo "$KEY not found in .env. Adding it."
    # Append the key-value pair to the .env file
    echo "$KEY=$PROJECT_ROOT" >> ".env"
fi

# Run the Python app in pipenv shell
echo "Running the app..."
pipenv run python app/app.py

# Check if the script ran successfully
if [ $? -ne 0 ]; then
    echo "Failed to run the app."
    exit 1
fi