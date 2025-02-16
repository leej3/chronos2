terraform {
  required_version = ">= 1.8.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {}
}

module "networking" {
  source      = "../modules/networking/"
  environment = var.environment
}

module "iam_role_and_policy" {
  source         = "../modules/iam/"
  environment    = var.environment
  AWS_ACCOUNT_ID = var.AWS_ACCOUNT_ID
}

# Elastic IPs for environments
resource "aws_eip" "chronos_production" {
  domain = "vpc"
  tags = {
    Name = "chronos-production-eip"
    Environment = "production"
    ManagedBy = "terraform"
    Persistent = "true"
  }
}

resource "aws_eip" "chronos_staging" {
  domain = "vpc"
  tags = {
    Name = "chronos-staging-eip"
    Environment = "staging"
    ManagedBy = "terraform"
    Persistent = "true"
  }
}
