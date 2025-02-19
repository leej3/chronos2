#!/bin/bash

# Validate git_ref is set
if [ -z "${git_ref}" ]; then
    echo "Error: git_ref must be provided in your environment configuration."
    exit 1
fi

# Install Docker
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

# Clone repository and setup environment
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/leej3/chronos2.git
cd chronos2

# Checkout the specified git reference
sudo -u ubuntu git checkout "${git_ref}"

# Configure git to use HTTPS instead of SSH for submodules
sudo -u ubuntu git config --global url."https://github.com/".insteadOf git@github.com:

# Initialize git submodules
sudo -u ubuntu git submodule update --init --recursive

# Run setup script to create initial .env files
sudo -u ubuntu bash setup-dotenv.sh

# Update environment variables for staging
sudo -u ubuntu bash -c '
# Extract base URL without /api suffix for Traefik configuration
BASE_URL=$(echo "${vite_api_base_url}" | sed "s|/api$||")
DOMAIN=$(echo "$BASE_URL" | sed "s|^https://||")

# Frontend environment updates
sed -i "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=${vite_api_base_url}|" dashboard_frontend/.env.docker

# Backend environment updates
sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${postgres_password}|" dashboard_backend/.env.docker
sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${jwt_secret_key}|" dashboard_backend/.env.docker
sed -i "s|EDGE_SERVER_IP=.*|EDGE_SERVER_IP=${edge_server_ip}|" dashboard_backend/.env.docker
sed -i "s|EDGE_SERVER_PORT=.*|EDGE_SERVER_PORT=${edge_server_port}|" dashboard_backend/.env.docker
sed -i "s|USER_1_EMAIL=.*|USER_1_EMAIL=${user_1_email}|" dashboard_backend/.env.docker
sed -i "s|USER_1_PASSWORD=.*|USER_1_PASSWORD=${user_1_password}|" dashboard_backend/.env.docker
sed -i "s|LETSENCRYPT_ADMIN_EMAIL=.*|LETSENCRYPT_ADMIN_EMAIL=${letsencrypt_admin_email}|" dashboard_backend/.env.docker

# Create deployment .env.deployment file for only systemd/compose stack required variables
cat > .env.deployment << EOF
DEPLOYMENT_URI=$DOMAIN
LETSENCRYPT_ADMIN_EMAIL=${letsencrypt_admin_email}
EOF
'

# Setup FRP configuration
sudo -u ubuntu bash -c '
mkdir -p frp_config
cp frp_config/frps.template.toml frp_config/frps.toml
sed -i "s|auth.token = \"12345678\"|auth.token = \"${frp_auth_token}\"|" frp_config/frps.toml
'

# Run the installation script with root privileges
cd /home/ubuntu/chronos2
bash install.sh
