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

data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket = "agt-chronos-terraform-state-storage"
    key    = "environments/shared/terraform.tfstate"
    region = "us-east-1"
  }
}

locals {
  environment = var.deptype == "stage" ? "stage" : "prod"
  eip_id = var.deptype == "stage" ? data.terraform_remote_state.shared.outputs.staging_eip_allocation_id : data.terraform_remote_state.shared.outputs.production_eip_allocation_id
}

module "ec2" {
  source = "../modules/ec2"

  environment     = local.environment
  public_key      = var.public_key
  additional_public_key = var.additional_public_key
  eip_allocation_id = local.eip_id

  # State Configuration
  state_bucket_name     = var.bucket_name
  state_backend_key     = "environments/shared/terraform.tfstate"
  state_table_name      = var.table_name
  state_storage_region  = "us-east-1"
}
