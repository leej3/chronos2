# Chronos Project

## Overview

The Chronos project has been structured into three distinct components: frontend, backend, and edge server. These components operate independently, enabling better scalability and maintainability. Docker Compose is used to integrate and manage these services for seamless deployment. Detailed information about each component is available in their respective README files:

- [Frontend README](./dashboard_frontend/README.md)
- [Backend README](./dashboard_backend/README.md)
- [Edge Server README](./edge_server/README.md)

## Installation with Docker

Follow the steps below to build and start the Chronos project using Docker Compose:

### Build and Start Services

Run the following commands to build and start all services in detached mode:

```bash
bash setup-env.sh
docker-compose up -d
```

### Stop and Remove Services

To stop and remove all running containers, use:

```bash
docker-compose down
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

For further details, please refer to the respective README files linked above and the docker compose files in this directory.
