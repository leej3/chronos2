#!/bin/bash
set -e

# This script only handles essential EC2 instance setup
# Application configuration and git repository setup are handled separately via SSH after deployment

# Install Docker and essential dependencies
apt-get update
apt-get install -y ca-certificates curl git rsync
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
usermod -aG docker ubuntu

# Setup SSH keys for the ubuntu user
mkdir -p /home/ubuntu/.ssh
echo "${public_key}" >> /home/ubuntu/.ssh/authorized_keys
echo "${additional_public_key}" >> /home/ubuntu/.ssh/authorized_keys
chmod 700 /home/ubuntu/.ssh
chmod 600 /home/ubuntu/.ssh/authorized_keys
chown -R ubuntu:ubuntu /home/ubuntu/.ssh

# Create a marker file that indicates setup is complete
touch /home/ubuntu/.setup_complete

echo "Basic system setup complete. Repository and configuration will be applied via SSH."
