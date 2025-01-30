# Chronos Project

## Overview

The Chronos project has been structured into three distinct components: frontend, backend, and edge server. These components operate independently, enabling better scalability and maintainability. Docker Compose is used to integrate and manage these services for seamless deployment. Detailed information about each component is available in their respective README files:

- [Frontend README](./dashboard_frontend/README.md)
- [Backend README](./dashboard_backend/README.md)
- [Edge Server README](./edge_server/README.md)

## Development with Docker

Follow the steps below to build and start the Chronos project using Docker Compose:

### Build and Start Services

Run the following commands to build and start all services in detached mode:

```bash
bash setup-dotenv.sh
docker compose up --build
```

### Stop and Remove Services

To stop and remove all running containers, use:

```bash
docker compose down
```

Sometimes the postgres container has been initialized with a different user than the one specified in the .env.docker file. To fix this, remove the postgres volume run the following command:

```bash
docker compose down -v
```

## Docker Services

The Chronos project consists of the following services managed by Docker Compose. During development the docker-compose.override.yml file is used automatically and the services are exposed on the local host machine for debugging purposes. The services themselves in the containers are configured to look for each other via the docker network. During deployment the edge server is run on the edge host and connects to the stack using a fast reverse proxy.

### Frontend

- **Service Name:** `dashboard_frontend`
- **Port:** `5173`
- **Access URL:** [http://localhost:5173](http://localhost:5173)

### Backend

- **Service Name:** `dashboard_backend`
- **Port:** `5172`
- **Access URL:** [http://localhost:5172/api](http://localhost:5172/api)
- **API Documentation:** [http://localhost:5172/docs](http://localhost:5172/docs)

### Edge Server

- **Service Name:** `edge_server`
- **Port:** `5171`
- **API Documentation:** [http://localhost:5171/docs](http://localhost:5171/docs)
- **Access URL:** Configured via `.env` files in the backend and frontend components.

For further details, please refer to the respective README files linked above and the docker compose files in this directory. Note, other services are run depending on the deployment configuration.

## Environment Configuration

The project uses several environment files for different purposes. `setup-dotenv.sh` is used to create these files from their templates.

### Environment Files Overview

#### Docker Service Configuration
These files configure the individual services in the Docker Compose stack:

- `dashboard_frontend/.env.docker` (from `.env.sample`)
  - Frontend configuration
  - API endpoints
  - Feature flags

- `dashboard_backend/.env.docker` (from `.env.sample`)
  - Database credentials
  - API configuration
  - Edge server connection details

#### Local Development
These files are used for local development and testing:

- `dashboard_frontend/.env` (from `.env.sample.local`)
  - Local development settings
  - Local API endpoints

- `dashboard_backend/.env` (from `.env.sample.local`)
  - Local database connection
  - Development configuration

#### Deployment Configuration
- `.env` (from `.env.sample.install`)
  - `DEPLOYMENT_URI`: Your domain (e.g., chronos.yourdomain.com)
  - `LETSENCRYPT_ADMIN_EMAIL`: Email for SSL certificates

## Deployment

### Prerequisites
Before deploying, you must set up and configure the environment:

1. Create environment files from templates:
   ```bash
   ./setup-dotenv.sh
   ```

2. Configure the Docker services by editing:
   - `dashboard_frontend/.env.docker`
   - `dashboard_backend/.env.docker`
   These files configure the core functionality of each service.


3. Configure the deployment environment in .env

4. Run the installation script:
   ```bash
   sudo bash install.sh
   ```

The installation script will:
- Verify Docker is installed
- Create the installation directory at `/opt/chronos`
- Copy all files and configurations to the installation directory
- Set up and start the systemd service

### Managing the Service

Once installed as a systemd service, you can manage it with standard commands:
```bash
# View service status
sudo systemctl status chronos

# View systemd logs
sudo journalctl -u chronos -f

# View docker logs
sudo docker compose -f docker-compose.yml -f docker-compose.deployment.yml logs -f

# Stop the service
sudo systemctl stop chronos

# Start the service
sudo systemctl start chronos

# Restart the service
sudo systemctl restart chronos
```

The systemd service will:
- Start automatically on boot
- Restart on failure
- Handle docker compose up/down operations
- Use the configured environment variables
