data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-${var.ubuntu_ami_release}-amd64-server-*"]
  }
}

data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket         = "${var.state_bucket_name}-shared"
    key            = var.state_backend_key
    dynamodb_table = "${var.state_table_name}-shared"
    region         = var.state_storage_region
  }
}
