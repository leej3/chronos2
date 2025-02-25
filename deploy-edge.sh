#!/bin/bash

# Exit on error
set -e

ENV=${1:-stage}

if [[ ! "$ENV" =~ ^(stage|prod)$ ]]; then
    echo "Error: Invalid environment. Must be either stage or prod"
    echo "Usage: $0 [stage|prod]"
    exit 1
fi

# Check if env file exists
if [ ! -f "./edge_server/env-${ENV}" ]; then
    echo "Error: env-${ENV} file not found!"
    echo "Please copy edge_server/env.template to edge_server/env-${ENV} and fill in the required values:"
    echo "cp edge_server/env.template edge_server/env-${ENV}"
    exit 1
fi

# Source environment variables
source "./edge_server/env-${ENV}"

# Validate required variables
required_vars=(
    "EDGE_SERVER_HOST"
    "GIT_REF"
    "PI_USER"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in env-${ENV} file"
        exit 1
    fi
done

# Execute the remote commands
echo "Deploying to edge server ($ENV environment): $EDGE_SERVER_HOST"
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

# Fetch latest changes and checkout the specific ref (tag or commit)
echo "Updating repository..."
git fetch --all --tags
# Use git checkout with --detach to avoid being on a branch
git checkout --detach ${GIT_REF}
echo "Successfully checked out ${GIT_REF}"

# Run the installation script
echo "Running installation script..."
cd edge_server
sudo PI_USER=${PI_USER} READ_ONLY_MODE=${READ_ONLY_MODE} bash install.sh
ENDSSH

echo "Deployment complete!"
