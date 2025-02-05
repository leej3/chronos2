#!/bin/bash

# Exit on error
set -e

# Check if env file exists
if [ ! -f "./edge_server/env" ]; then
    echo "Error: env file not found!"
    echo "Please copy edge_server/env.template to edge_server/env and fill in the required values:"
    echo "cp edge_server/env.template edge_server/env"
    exit 1
fi

# Source environment variables
source ./edge_server/env

# Validate required variables
required_vars=(
    "EDGE_SERVER_HOST"
    "GIT_REF"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in env file"
        exit 1
    fi
done

# Execute the remote commands
echo "Deploying to edge server, $EDGE_SERVER_HOST"
ssh "$EDGE_SERVER_HOST" bash -s << ENDSSH
set -e
echo "Starting deployment on remote host..."

# Check if repository exists, if not clone it
if [ ! -d "chronos2" ]; then
    echo "Cloning repository..."
    git clone https://github.com/leej3/chronos2.git
fi

# Enter repository directory
cd chronos2

# Fetch latest changes and checkout specified ref
echo "Updating repository..."
git fetch origin
git checkout ${GIT_REF}
git pull origin ${GIT_REF}

# Run the installation script
echo "Running installation script..."
cd edge_server
sudo bash install.sh
ENDSSH

echo "Deployment complete!" 