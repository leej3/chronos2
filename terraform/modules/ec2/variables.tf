variable "region" {
  description = "The AWS region used by the deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "The name of the development environment. Usually `stage` or `prod`."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.large"
  type        = string
}

variable "ec2_key_name" {
  description = "Key name of the Key Pair to use for the instance; which can be managed using the `aws_key_pair` resource."
  default     = "pi4_2024"
  type        = string
}

variable "ec2_root_block_device_size" {
  description = "Size of the volume in gibibytes (GiB)."
  default     = 30
  type        = number
}

variable "ec2_root_block_device_type" {
  description = "Type of volume. Valid values include standard, gp2, gp3, io1, io2, sc1, or st1."
  default     = "gp2"
  type        = string
}

variable "eip_domain" {
  description = "Indicates if this EIP is for use in VPC"
  default     = "vpc"
  type        = string
}

variable "ubuntu_ami_release" {
  description = "The release of Ubuntu to use for the EC2 AMI. E.g. 20.04, 22.04, 24.04"
  default     = "20.04"
  type        = string
}

variable "public_key" {
  description = "The public key used to deploy to the EC2 instance via ssh"
  type        = string
}

variable "additional_public_key" {
  description = "An additional SSH public key to be added to the EC2 instance authorized_keys"
  type        = string
}
