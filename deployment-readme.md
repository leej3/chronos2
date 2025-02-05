# Deployment Guide

## Dashboard Deployment

1. Configure environment:
```bash
cp terraform/staging/env.template terraform/staging/env
# Edit env file with your values:
# - TF_VAR_public_key: Your SSH public key
# - TF_VAR_additional_public_key: Additional SSH key if needed
# - TF_VAR_vite_api_base_url: API URL (e.g., https://your-domain.com/api)
# - TF_VAR_postgres_password: Database password
# - TF_VAR_jwt_secret_key: JWT secret for authentication
# - TF_VAR_edge_server_ip: Edge server IP address
# - TF_VAR_edge_server_port: Edge server port
# - TF_VAR_user_1_email: Admin user email
# - TF_VAR_user_1_password: Admin user password
```

2. Deploy:
```bash
./deploy-dashboard.sh
```

## Edge Server Deployment

Prerequisites:
- Direct access to the edge server for initial FRP client setup
- Git installed on the edge server

1. Configure environment:
```bash
cp edge_server/env.template edge_server/env
# Edit env file with your values:
# - EDGE_SERVER_HOST: SSH host (e.g., user@edge-server)
# - GIT_REF: Git reference to deploy (e.g., main)
# - CHRONOS_EDGE_PORT: Port for the edge server
```

2. Deploy:
```bash
./deploy-edge.sh
```

The deployment scripts will:
- Clone/update the repository
- Install dependencies
- Configure systemd services
- Start the services

To view logs:
- Dashboard: Connect to the EC2 instance and check docker logs
- Edge Server: `journalctl -u chronos -f`
