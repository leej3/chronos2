#!/bin/bash
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (with sudo)"
    exit 1
fi

INSTALL_DIR="/opt/chronos"
SERVICE_NAME="chronos"

echo "Installing Chronos edge server..."

# Create or update installation directory
echo "Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"

# Install uv if not already installed and set up PATH
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source the environment file to get uv in PATH
    if [ -f "/root/.local/bin/env" ]; then
        source "/root/.local/bin/env"
    else
        export PATH="/root/.local/bin:$PATH"
    fi
fi

# Verify uv is now available
if ! command -v uv &> /dev/null; then
    echo "Error: uv installation failed or not in PATH"
    echo "Please ensure /root/.local/bin is in your PATH"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
cd "$INSTALL_DIR"
uv sync

# Install and configure systemd service
echo "Configuring systemd service..."
cp chronos.service /etc/systemd/system/
systemctl daemon-reload

# Enable and restart service
echo "Enabling and starting service..."
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "Installation complete! Service status:"
systemctl status "$SERVICE_NAME"
echo
echo "To view logs, run: journalctl -u $SERVICE_NAME -f"
