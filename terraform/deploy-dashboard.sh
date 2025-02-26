#!/bin/bash

set -e

ENV=${1:-stage}
ACTION=${2:-plan}

if [[ ! "$ENV" =~ ^(stage|prod)$ ]]; then
    echo "Error: Invalid environment. Must be either stage or prod"
    echo "Usage: $0 [stage|prod] [plan|apply|destroy]"
    exit 1
fi

if [[ ! "$ACTION" =~ ^(plan|apply|destroy)$ ]]; then
    echo "Error: Invalid action. Must be either plan, apply, or destroy"
    echo "Usage: $0 [stage|prod] [plan|apply|destroy]"
    exit 1
fi

# Determine env file suffix based on AWS_PROFILE
ENV_SUFFIX=""
if [ ! -z "$AWS_PROFILE" ]; then
    ENV_SUFFIX="-${AWS_PROFILE}"
fi

ENV_FILE="./deployments/env-${ENV}${ENV_SUFFIX}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: ${ENV_FILE} file not found!"
    echo "Please copy deployments/env.template to ${ENV_FILE} and fill in the required values:"
    echo "cp deployments/env.template ${ENV_FILE}"
    exit 1
fi

source "$ENV_FILE"

required_vars=(
    "TF_VAR_deptype"
    "TF_VAR_public_key"
    "TF_VAR_additional_public_key"
    "vite_api_base_url"
    "postgres_password"
    "jwt_secret_key"
    "edge_server_ip"
    "edge_server_port"
    "user_1_email"
    "user_1_password"
    "git_ref"
    "frp_auth_token"
    "letsencrypt_admin_email"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in ${ENV_FILE}"
        exit 1
    fi
done

if [ "$TF_VAR_deptype" != "$ENV" ]; then
    echo "Error: TF_VAR_deptype in ${ENV_FILE} does not match the selected environment"
    echo "Expected: $ENV"
    echo "Found: $TF_VAR_deptype"
    exit 1
fi

# Note: git_ref is now only used for application deployment, not for Terraform

cd deployments

# Determine backend config file based on AWS_PROFILE
BACKEND_SUFFIX=""
if [ ! -z "$AWS_PROFILE" ]; then
    BACKEND_SUFFIX="-${AWS_PROFILE}"
fi

echo "Initializing Terraform for ${ENV}${ENV_SUFFIX} environment..."
tofu init -reconfigure -backend-config="backend-${ENV}${BACKEND_SUFFIX}.hcl"

# Add this function for checking instance readiness
wait_for_instance() {
    local instance_dns=$1
    local max_attempts=30
    local attempt=1

    echo "Waiting for instance to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=accept-new "ubuntu@$instance_dns" "exit" 2>/dev/null; then
            echo "Instance is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: Instance not ready yet, waiting..."
        sleep 10
        attempt=$((attempt + 1))
    done

    echo "Error: Instance failed to become ready after 5 minutes"
    return 1
}

# Handle application deployment
deploy_application() {
    local instance_dns=$1
    local max_retries=3
    local retry_count=0

    echo "Deploying to dashboard server ($ENV environment): $instance_dns"

    # Wait for basic setup to complete (first time deployments)
    echo "Checking if instance setup is complete..."
    while [ $retry_count -lt $max_retries ]; do
        if ssh -o ConnectTimeout=10 "ubuntu@$instance_dns" "test -f /home/ubuntu/.setup_complete && echo 'Setup complete'" 2>/dev/null; then
            echo "Basic setup is complete, proceeding with application deployment"
            break
        fi
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            echo "Setup not yet complete. Waiting 30 seconds... (Attempt $retry_count of $max_retries)"
            sleep 30
        else
            echo "Error: Setup did not complete after $max_retries attempts"
            echo "This might be a new instance that's still initializing. Try again in a few minutes."
            return 1
        fi
    done

    retry_count=0

    # Run the full deployment process via SSH
    while [ $retry_count -lt $max_retries ]; do
        echo "Deploying application..."
        if ssh -o ConnectTimeout=30 "ubuntu@$instance_dns" bash -s << ENDSSH; then
            set -e
            echo "Starting application deployment..."

            # Check if repository exists, if not clone it
            if [ ! -d "chronos2" ]; then
                echo "Cloning repository..."
                git clone https://github.com/leej3/chronos2.git
            fi

            # Enter repository directory
            cd chronos2

            # Fetch latest changes and checkout the specific ref (tag or commit)
            echo "Updating repository..."
            git fetch --all --tags
            # Use git checkout with --detach to avoid being on a branch
            git checkout --detach ${git_ref}
            echo "Successfully checked out ${git_ref}"

            # Configure git to use HTTPS instead of SSH for submodules
            git config --global url."https://github.com/".insteadOf git@github.com:

            # Initialize git submodules
            git submodule update --init --recursive

            # Run setup script to create initial .env files if they don't exist
            if [ ! -f "dashboard_frontend/.env.docker" ] || [ ! -f "dashboard_backend/.env.docker" ]; then
                echo "Setting up initial .env files..."
                bash setup-dotenv.sh
            fi

            # Extract base URL without /api suffix for Traefik configuration
            BASE_URL=\$(echo "${vite_api_base_url}" | sed "s|/api\$||")
            DOMAIN=\$(echo "\$BASE_URL" | sed "s|^https://||")

            # Frontend environment updates
            sed -i "s|VITE_API_BASE_URL=.*|VITE_API_BASE_URL=${vite_api_base_url}|" dashboard_frontend/.env.docker

            # Apply background color if provided
            if [ ! -z "${background_color}" ]; then
                if grep -q "VITE_BACKGROUND_COLOR" dashboard_frontend/.env.docker; then
                    sed -i "s|VITE_BACKGROUND_COLOR=.*|VITE_BACKGROUND_COLOR=${background_color}|" dashboard_frontend/.env.docker
                else
                    echo "VITE_BACKGROUND_COLOR=${background_color}" >> dashboard_frontend/.env.docker
                fi
                echo "Background color set to: ${background_color}"
            fi

            # Backend environment updates
            sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${postgres_password}|" dashboard_backend/.env.docker
            sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${jwt_secret_key}|" dashboard_backend/.env.docker
            sed -i "s|EDGE_SERVER_IP=.*|EDGE_SERVER_IP=${edge_server_ip}|" dashboard_backend/.env.docker
            sed -i "s|EDGE_SERVER_PORT=.*|EDGE_SERVER_PORT=${edge_server_port}|" dashboard_backend/.env.docker
            sed -i "s|USER_1_EMAIL=.*|USER_1_EMAIL=${user_1_email}|" dashboard_backend/.env.docker
            sed -i "s|USER_1_PASSWORD=.*|USER_1_PASSWORD=${user_1_password}|" dashboard_backend/.env.docker
            sed -i "s|LETSENCRYPT_ADMIN_EMAIL=.*|LETSENCRYPT_ADMIN_EMAIL=${letsencrypt_admin_email}|" dashboard_backend/.env.docker

            # Create deployment .env.deployment file
            cat > .env.deployment << EOF
DEPLOYMENT_URI=\$DOMAIN
LETSENCRYPT_ADMIN_EMAIL=${letsencrypt_admin_email}
EOF

            # Setup FRP configuration
            mkdir -p frp_config
            if [ -f "frp_config/frps.template.toml" ]; then
                cp frp_config/frps.template.toml frp_config/frps.toml
                sed -i "s|auth.token = \"12345678\"|auth.token = \"${frp_auth_token}\"|" frp_config/frps.toml
            fi

            echo "Configuration complete, running installation script..."

            # Run the installation script with root privileges
            sudo bash install.sh
ENDSSH
            echo "Deployment successful!"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                echo "Deployment failed. Retrying in 30 seconds... (Attempt $retry_count of $max_retries)"
                sleep 30
            else
                echo "Error: Deployment failed after $max_retries attempts"
                return 1
            fi
        fi
    done
    return 1
}

case "$ACTION" in
    "plan")
        echo "Running Terraform plan for ${ENV} environment..."
        tofu plan
        ;;
    "apply")
        echo "Running Terraform apply for ${ENV} environment..."
        # Capture the plan output to check for changes
        set +e  # Temporarily disable exit on error since we want to capture the exit code
        tofu plan -detailed-exitcode > plan_output.txt 2>&1
        plan_exit_code=$?
        set -e  # Re-enable exit on error

        # Extract hostname from API URL using bash string substitution
        instance_dns=${vite_api_base_url#*//}
        instance_dns=${instance_dns%%:*}
        instance_dns=${instance_dns%/api}

        # Exit code 0 means no changes, 1 means error, 2 means changes present
        if [ $plan_exit_code -eq 0 ]; then
            echo "No infrastructure changes detected. Applying configuration updates only..."
            # Always run the full deployment to ensure configuration is updated
            deploy_application "$instance_dns"
        elif [ $plan_exit_code -eq 2 ]; then
            # Apply infrastructure changes
            echo "Infrastructure changes detected."
            echo "Running Terraform apply to update infrastructure..."
            cat plan_output.txt  # Show the plan output
            tofu apply -auto-approve

            echo "Waiting for instance to be ready..."
            if ! wait_for_instance "$instance_dns"; then
                echo "Error: Instance failed to become ready"
                exit 1
            fi

            # Give some time for setup to complete
            echo "Waiting 30 seconds for basic setup to complete..."
            sleep 30

            # Now deploy the application
            deploy_application "$instance_dns"
        else
            echo "Error during Terraform plan:"
            cat plan_output.txt
            rm plan_output.txt
            exit 1
        fi
        rm -f plan_output.txt  # Clean up the temporary file
        ;;
    "destroy")
        echo "WARNING: You are about to destroy the ${ENV} environment!"
        echo "This action cannot be undone. Please type 'yes' to confirm:"
        read -r confirmation
        if [ "$confirmation" != "yes" ]; then
            echo "Destroy cancelled."
            exit 1
        fi
        echo "Running Terraform destroy for ${ENV} environment..."
        tofu destroy -auto-approve
        ;;
esac
