#!/bin/bash
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (with sudo)"
    exit 1
fi

INSTALL_DIR="/opt/chronos"
SERVICE_NAME="chronos"
SERVICE_USER="pi"
SERVICE_GROUP="dialout"

echo "Installing Chronos edge server..."

# Create or update installation directory
echo "Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
rsync -av --delete --exclude='.venv' . "$INSTALL_DIR/"

# Set correct ownership
echo "Setting correct ownership..."
chown -R $SERVICE_USER:$SERVICE_USER "$INSTALL_DIR"

# Ensure service user is in dialout group
echo "Ensuring $SERVICE_USER has access to serial ports..."
usermod -a -G dialout $SERVICE_USER

# Install uv for the service user if not already installed
echo "Installing uv package manager..."
sudo -u $SERVICE_USER mkdir -p /home/$SERVICE_USER/.local/bin
sudo -u $SERVICE_USER bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'

# Install dependencies as the service user
echo "Installing dependencies..."
cd "$INSTALL_DIR/edge_server"
sudo -u $SERVICE_USER bash -c "
    export PATH=/home/$SERVICE_USER/.local/bin:\$PATH
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    uv sync"

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
echo
echo "NOTE: You may need to log out and back in for the dialout group changes to take effect."
