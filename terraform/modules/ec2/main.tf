terraform {
  required_version = ">= 1.8.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# EC2 Instance
resource "aws_instance" "deployment" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = data.terraform_remote_state.shared.outputs.subnet_id
  key_name                    = var.ec2_key_name
  vpc_security_group_ids      = [data.terraform_remote_state.shared.outputs.security_group_id]
  associate_public_ip_address = true
  iam_instance_profile        = data.terraform_remote_state.shared.outputs.instance_profile_name
  root_block_device {
    volume_size = var.ec2_root_block_device_size
    volume_type = var.ec2_root_block_device_type
  }

  tags = {
    Name = var.environment
  }

  user_data                   = templatefile("${path.module}/scripts/install-docker.sh", {
    additional_public_key = var.additional_public_key
  })
  user_data_replace_on_change = true
}

resource "aws_eip" "deployment" {
  domain = var.eip_domain

  tags = {
    Name = var.environment
  }
}

resource "aws_eip_association" "deployment" {
  instance_id   = aws_instance.deployment.id
  allocation_id = aws_eip.deployment.id
}

resource "aws_key_pair" "deployer" {
  key_name   = "deployer-key-${var.environment}"
  public_key = var.public_key
}
