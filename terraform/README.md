# Resource Deployment

## Architecture Overview

The deployment architecture uses a combination of local deployment scripts and EC2 instance setup scripts. Here's how the components interact:

**```mermaid
graph TD
    A[Local Machine] -->|deploy.sh| B[OpenTofu Apply]
    B -->|User Data| C[EC2 Instance]
    D[env file] -->|TF_VAR_*| B
    B -->|Variables| E[ec2-setup.sh]
    E -->|Clone & Setup| F[chronos2 repo]
    E -->|Environment Updates| G[.env files]
    G -->|Variables| H[Docker Compose]
    
    subgraph "Local Environment"
        A
        B
        D
    end
    
    subgraph "AWS Environment"
        C
        E
        F
        G
        H
    end
```**

## Variable Flow

1. **Local Environment Variables**
   - Variables are set in `staging/env` or `production/env` files
   - Format: `TF_VAR_variable_name="value"`
   - Example variables:
     - `TF_VAR_public_key`: SSH key for EC2 access
     - `TF_VAR_vite_api_base_url`: Base URL for the frontend
     - `TF_VAR_frp_auth_token`: Authentication token for FRP

2. **OpenTofu to EC2**
   - Variables are passed to the EC2 instance via user data script
   - The `ec2-setup.sh` script receives these variables as shell variables
   - Used for initial instance configuration and application setup

3. **Application Configuration**
   - Environment variables are injected into various `.env` files:
     - `dashboard_frontend/.env.docker`
     - `dashboard_backend/.env.docker`
     - `edge_server/.env.docker`
     - `frp_config/frps.toml`
     - `.env` (root level)

## Deployment Process

### Local Deployment (staging/production)

1. Copy `env.template` to `env` and fill in required values:
```bash
cp env.template env
nano env  # Edit variables as needed
```

2. Run the deployment script:
```bash
./deploy.sh
```

### EC2 Instance Setup

The `ec2-setup.sh` script performs the following:

1. Installs Docker and required packages
2. Sets up SSH keys for the ubuntu user
3. Clones the repository and initializes submodules
4. Creates and updates environment files
5. Configures FRP
6. Runs the installation script

## Environment Files

- `env.template`: Template for local deployment variables
- `.env.docker`: Container-specific environment variables
- `.env`: Application-level environment variables

## Domain Configuration

The domain name is managed through environment variables rather than hardcoded values:
- Base URL is extracted from `TF_VAR_vite_api_base_url`
- Used in frontend configuration and deployment URI
- Docker Compose uses `DEPLOYMENT_URI` from environment

## Infrastructure Requirements

- [OpenTofu](https://opentofu.org/) version >=1.8.0
- AWS account with appropriate permissions
- SSH key pair for EC2 access

## State Management

The deployment uses S3 for state storage and DynamoDB for state locking. These resources should be created once before the first deployment:

```bash
cd ~/path-to-repo/terraform/state/
tofu init
tofu apply
```

This creates:
- S3 buckets for state storage
- DynamoDB tables for state locking
- Required IAM roles and policies

> **_NOTE:_** State resources are protected against accidental destruction. Manual intervention in the AWS Console is required for removal.

## Manual Deployment Steps

### 0. Bootstrap Step: Deploy State Resources

> **_Note:_** This step should be run manually on the developer's/infrastructure engineer's local machine.

> **_Note:_** This step should only be run once for the lifetime of the deployment.

It is recommended that you use the default variable values, as defined in `modules/state/variables.tf`. If you want to change the **values** from the defaults, you can add your desired values in `state/main.tf`. You will then need to change the corresponding values in the `variables_state.tf` files of the resources (i.e. `shared`, `staging`, and `production`) to match what you set in `state/main.tf`. This can be done in an automated way by running

```bash
$ cd ~/path-to-repo/terraform/
$ # Change DynamoDB state lock table names
$ find . -name "*.tf" -exec sed -i '' "s/terraform-state-locks/chronos-state-locks/g" {} +
$ # Change names of S3 buckets that store OpenTofu state
$ find .  -name "*.tf" -exec sed -i '' "s/chronos-terraform-state-storage/chronos-state-storage-test/g" {} +
$ # Change AWS region where state resources reside
$ find . -name "*.tf" -exec sed -i '' "s/us-east-1/us-east-1/g" {} +
```

Once you have configured the variables (or preferably will be using the defaults), you can deploy the state management resources with

```bash
$ cd ~/path-to-repo/terraform/state/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

> **_NOTE:_** In order to prevent accidental destruction, the `state` modules are configured to [prevent destruction](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle#prevent_destroy) ([more info on `prevent_destroy`](https://developer.hashicorp.com/terraform/tutorials/state/resource-lifecycle#prevent-resource-deletion)) using OpenTofu. To destroy state resources, you must do so manually in the AWS Management Console.

### 1. Deploy Shared Resources

You can deploy the shared resources with:

```bash
$ cd ~/path-to-repo/terraform/shared/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

### 2. Deploy Staging Resources

You can deploy the staging resources with:

```bash
$ cd ~/path-to-repo/terraform/staging/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

### 3. Deploy Production Resources

You can deploy the production resources with:

```bash
$ cd ~/path-to-repo/terraform/production/
$ tofu init
$ tofu plan # This is not required, but gives a nice preview
$ tofu apply
```

## Development/Deployment Workflow

[Previous workflow content remains the same...]
