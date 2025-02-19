#!/bin/bash
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (with sudo)"
    exit 1
fi

INSTALL_DIR="/opt/chronos"
SERVICE_NAME="chronos"

echo "Installing Chronos main stack..."

# Check for docker
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed"
    echo "Please install docker first: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check for rsync
if ! command -v rsync &> /dev/null; then
    echo "Error: rsync is not installed"
    echo "Please install rsync first"
    exit 1
fi

# Verify .env.docker files exist and are configured
if ! find . -name "*.env.docker" | grep -q .; then
    echo "Error: .env.docker files not found"
    echo "Please complete the environment setup before installation:"
    echo "1. Run ./setup-dotenv.sh"
    echo "2. Configure the .env.docker files in dashboard_frontend/ and dashboard_backend/"
    exit 1
fi

# Create or update installation directory
echo "Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
rsync -av --delete . "$INSTALL_DIR/"


# Verify deployment environment variables
if [ ! -f "$INSTALL_DIR/.env.deployment" ]; then
    echo "No .env.deployment file detected..."
    exit 1
fi
if ! grep -q "DEPLOYMENT_URI=" "$INSTALL_DIR/.env.deployment" || ! grep -q "LETSENCRYPT_ADMIN_EMAIL=" "$INSTALL_DIR/.env.deployment"; then
    echo "Error: Deployment environment not configured"
    echo "The .env.deployment file must contain:"
    echo "- DEPLOYMENT_URI"
    echo "- LETSENCRYPT_ADMIN_EMAIL"
    exit 1
fi

# Install and configure systemd service
echo "Configuring systemd service..."
cp chronos.service /etc/systemd/system/
systemctl daemon-reload

# Enable and start service
echo "Enabling and starting service..."
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "Installation complete! Service status:"
echo Deployment successful $(date) >> deployment.log
systemctl status "$SERVICE_NAME"
echo
echo "To view logs, run: journalctl -u $SERVICE_NAME -f"
echo "To view docker logs, run: docker compose -f docker-compose.yml -f docker-compose.deployment.yml logs -f"
