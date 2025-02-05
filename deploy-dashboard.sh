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

if [ ! -f "./terraform/deployments/env-${ENV}" ]; then
    echo "Error: env-${ENV} file not found!"
    echo "Please copy terraform/deployments/env.template to terraform/deployments/env-${ENV} and fill in the required values:"
    echo "cp terraform/deployments/env.template terraform/deployments/env-${ENV}"
    exit 1
fi

source "./terraform/deployments/env-${ENV}"

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
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in env-${ENV} file"
        exit 1
    fi
done

if [ "$TF_VAR_deptype" != "$ENV" ]; then
    echo "Error: TF_VAR_deptype in env-${ENV} file does not match the selected environment"
    echo "Expected: $ENV"
    echo "Found: $TF_VAR_deptype"
    exit 1
fi

cd terraform/deployments

echo "Initializing Terraform for ${ENV} environment..."
tofu init -reconfigure -backend-config="backend-${ENV}.hcl"

case "$ACTION" in
    "plan")
        echo "Running Terraform plan for ${ENV} environment..."
        tofu plan
        ;;
    "apply")
        echo "Running Terraform apply for ${ENV} environment..."
        tofu apply -auto-approve
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
