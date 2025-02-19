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
  key_name                    = "deployer-key-${var.environment}"
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

  user_data                   = templatefile("${path.module}/scripts/ec2-setup.sh", {
    additional_public_key = var.additional_public_key
    public_key            = var.public_key
    vite_api_base_url    = var.vite_api_base_url
    postgres_password    = var.postgres_password
    jwt_secret_key       = var.jwt_secret_key
    edge_server_ip       = var.edge_server_ip
    edge_server_port     = var.edge_server_port
    user_1_email        = var.user_1_email
    user_1_password     = var.user_1_password
    frp_auth_token      = var.frp_auth_token
    git_ref             = var.git_ref
    letsencrypt_admin_email = var.letsencrypt_admin_email
  })
  user_data_replace_on_change = true
}

resource "aws_eip_association" "deployment" {
  instance_id   = aws_instance.deployment.id
  allocation_id = var.eip_allocation_id
}

resource "aws_key_pair" "deployer" {
  key_name   = "deployer-key-${var.environment}"
  public_key = var.public_key
}
