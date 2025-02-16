#!/bin/bash
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (with sudo)"
    exit 1
fi

# Verify we're in the edge_server directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "$(basename "$SCRIPT_DIR")" != "edge_server" ]; then
    echo "Error: This script must be run from the edge_server directory"
    exit 1
fi

# Verify we're in the project root structure
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
if [ ! -f "$PROJECT_ROOT/deploy-edge.sh" ] || [ ! -d "$PROJECT_ROOT/edge_server" ]; then
    echo "Error: Script must be run from within the project structure"
    echo "Please cd to the edge_server directory in the project root"
    exit 1
fi

INSTALL_DIR="/opt/chronos"
SERVICE_NAME="chronos-edge"
PI_USER="${PI_USER:-pi}"
SERVICE_GROUP="dialout"
READ_ONLY_MODE="${READ_ONLY_MODE:-false}"

echo "Installing Chronos edge server..."
echo "Read-only mode: ${READ_ONLY_MODE}"

# Create or update installation directory
echo "Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$PROJECT_ROOT"
rsync -av --delete \
    --exclude='.venv' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    ./ "$INSTALL_DIR/"

# Set correct ownership
echo "Setting correct ownership..."
chown -R $PI_USER:$PI_USER "$INSTALL_DIR"

# Process service template
echo "Processing service template..."
if ! sed -e "s/__USER__/$PI_USER/g" \
        -e "s/__READ_ONLY_MODE__/$READ_ONLY_MODE/g" \
        "$INSTALL_DIR/edge_server/chronos-edge.service.template" > "$INSTALL_DIR/edge_server/chronos-edge.service"; then
    echo "Error: Failed to process service template"
    exit 1
fi

# Check if UV is already installed
echo "Checking UV installation..."
if ! sudo -u $PI_USER bash -c "export PATH=/home/$PI_USER/.local/bin:\$PATH && command -v uv >/dev/null 2>&1"; then
    echo "Installing UV package manager..."
    sudo -u $PI_USER mkdir -p /home/$PI_USER/.local/bin
    sudo -u $PI_USER bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
else
    echo "UV is already installed, skipping installation"
fi

# Install dependencies as the service user
echo "Installing dependencies..."
cd "$INSTALL_DIR/edge_server"
sudo -u $PI_USER bash -c "
    set -x
    export PATH=/home/$PI_USER/.local/bin:\$PATH
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    uv sync"

# Install and configure systemd service
echo "Configuring systemd service..."
if ! cp "$INSTALL_DIR/edge_server/chronos-edge.service" /etc/systemd/system/; then
    echo "Error: Failed to copy service file to systemd directory"
    exit 1
fi

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
