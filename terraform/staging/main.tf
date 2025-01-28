terraform {
  required_version = ">= 1.8.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "chronos2-terraform-state-storage-stage"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks-stage"
    encrypt        = true
  }
}

module "ec2" {
  source        = "../modules/ec2/"
  environment   = var.environment
  instance_type = var.instance_type
  public_key    = var.public_key
  additional_public_key = var.additional_public_key
}
