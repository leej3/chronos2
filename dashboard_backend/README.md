# Dashboard Backend README - Chronos Project

## Overview

This backend provides the API.

### Environment Variables/Configuration

Configuration is typically done in the .env.docker file (see .env.sample).

- **Database Configuration**:

  - `POSTGRES_PASSWORD`: PostgreSQL password (e.g., `yourpassword`)
  - `POSTGRES_HOST`: Hostname for PostgreSQL
  - `POSTGRES_PORT`: Port for PostgreSQL

- **Authentication**:

  - `JWT_SECRET_KEY`: Secret key for JWT (e.g., `abcd`)
  - `JWT_ALGORITHM`: Algorithm for JWT (e.g., `HS256`)

- **Edge Server Configuration**:

  - `EDGE_SERVER_IP`: IP address or hostname of the Edge Server (e.g., `http://edge_server` when developing with docker and `http://localhost` if accessing a port forwarded from another host)
  - `EDGE_SERVER_PORT`: Port for the Edge Server (e.g., `5171`)

- **Admin User Credentials**:

  - `USER_1_EMAIL`: Email for the first admin user
  - `USER_1_PASSWORD`: Password for the first admin user

