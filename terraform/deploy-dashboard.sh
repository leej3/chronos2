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
    "TF_VAR_vite_api_base_url"
    "TF_VAR_postgres_password"
    "TF_VAR_jwt_secret_key"
    "TF_VAR_edge_server_ip"
    "TF_VAR_edge_server_port"
    "TF_VAR_user_1_email"
    "TF_VAR_user_1_password"
    "TF_VAR_git_ref"
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

# Add this function near the start of the file, after the environment validation
deploy_application() {
    local instance_dns=$1
    local max_retries=3
    local retry_count=0

    echo "Deploying to dashboard server ($ENV environment): $instance_dns"

    while [ $retry_count -lt $max_retries ]; do
        if ssh -o ConnectTimeout=10 "ubuntu@$instance_dns" bash -s << ENDSSH; then
            set -e
            echo "Starting deployment on remote host..."

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
            git checkout --detach ${TF_VAR_git_ref}
            echo "Successfully checked out ${TF_VAR_git_ref}"

            # Update submodules
            git submodule update --init --recursive

            # Run the dashboard installation/update script
            echo "Running dashboard update..."
            sudo bash install.sh
ENDSSH
            echo "Deployment successful!"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                echo "Deployment failed. Retrying in 10 seconds... (Attempt $retry_count of $max_retries)"
                sleep 10
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
        instance_dns=${TF_VAR_vite_api_base_url#*//}
        instance_dns=${instance_dns%%:*}
        instance_dns=${instance_dns%/api}

        # Exit code 0 means no changes, 1 means error, 2 means changes present
        if [ $plan_exit_code -eq 0 ]; then
            echo "No infrastructure changes detected. Proceeding with application deployment..."
            deploy_application "$instance_dns"
        elif [ $plan_exit_code -eq 2 ]; then
            echo "Infrastructure changes detected. Running Terraform apply..."
            cat plan_output.txt  # Show the plan output
            tofu apply -auto-approve

            echo "Waiting for instance to be ready..."
            if ! wait_for_instance "$instance_dns"; then
                echo "Error: Instance failed to become ready"
                exit 1
            fi

            echo "Infrastructure changes applied successfully."
            echo "Note: The EC2 instance is handling the deployment through user data script."
            echo "You can check the instance's system log for deployment progress."
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
