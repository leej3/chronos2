# Backend README - Chronos Project

## Overview

The backend of the **Chronos** project provides the core API and server-side functionalities. It is a standalone service that can be run independently or as part of the full Chronos project setup.

## Environment Variables

The project relies on environment variables for configuration. To ensure all components run smoothly, follow these steps:

### Setting Up the Environment Variables

1. **Copy the example environment file**:

   ```bash
   cp chronos2/dashboard_backend/.env.sample chronos2/dashboard_backend/.env
   ```

2. **Modify the `.env` file**: Open the `.env` file and adjust the values based on your local or production setup. The most important variables to configure are listed below.

### Required Environment Variables

- **Database Configuration**:

  - `POSTGRES_USER`: PostgreSQL username (e.g., `postgres`)
  - `POSTGRES_PASSWORD`: PostgreSQL password (e.g., `yourpassword`)
  - `POSTGRES_DB`: Name of the database (e.g., `dev_chronos2`)
  - `DB_HOST`: Hostname for PostgreSQL (e.g., `postgres`)
  - `DB_PORT`: Port for PostgreSQL (default: `5432`)

- **Authentication**:

  - `JWT_SECRET_KEY`: Secret key for JWT (e.g., `abcd`)
  - `JWT_ALGORITHM`: Algorithm for JWT (e.g., `HS256`)

- **Edge Server Configuration**:

  - `EDGE_SERVER_IP`: IP address or hostname of the Edge Server (e.g., `http://edge_server` or `http://localhost`)
  - `EDGE_SERVER_PORT`: Port for the Edge Server (e.g., `5171`)

- **Admin User Credentials**:

  - `USER_1_EMAIL`: Email for the first admin user (e.g., `admin@gmail.com`)
  - `USER_1_PASSWORD`: Password for the first admin user (e.g., `Aa123456@`)

For more detailed instructions or troubleshooting, refer to the project’s [main README](../../README.md).
