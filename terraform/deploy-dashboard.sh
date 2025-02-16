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

case "$ACTION" in
    "plan")
        echo "Running Terraform plan for ${ENV} environment..."
        tofu plan
        ;;
    "apply")
        echo "Running Terraform apply for ${ENV} environment..."
        # Capture the plan output to check for changes
        plan_output=$(tofu plan -detailed-exitcode 2>&1)
        plan_exit_code=$?

        # Exit code 0 means no changes, 1 means error, 2 means changes present
        if [ $plan_exit_code -eq 0 ]; then
            echo "No infrastructure changes detected. Proceeding with application deployment..."
            # Extract hostname from API URL using bash string substitution
            instance_dns=${TF_VAR_vite_api_base_url#*//}
            instance_dns=${instance_dns%%:*}
            instance_dns=${instance_dns%/api}

            echo "Deploying to dashboard server ($ENV environment): $instance_dns"
            ssh "ubuntu@$instance_dns" bash -s << ENDSSH
set -e
echo "Starting deployment on remote host..."

# Check if repository exists, if not clone it
if [ ! -d "chronos2" ]; then
    echo "Cloning repository..."
    git clone https://github.com/leej3/chronos2.git
fi

# Enter repository directory
cd chronos2

# Fetch latest changes and checkout specified ref
echo "Updating repository..."
git fetch origin
git checkout \${TF_VAR_git_ref:-main}
git pull origin \${TF_VAR_git_ref:-main}

# Run the dashboard installation/update script
echo "Running dashboard update..."
sudo bash install.sh
ENDSSH
        elif [ $plan_exit_code -eq 2 ]; then
            echo "Infrastructure changes detected. Running Terraform apply..."
            tofu apply -auto-approve
        else
            echo "Error during Terraform plan:"
            echo "$plan_output"
            exit 1
        fi
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
