variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., staging, production)"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "ec2_key_name" {
  description = "Name of the EC2 key pair"
  type        = string
  default     = "deployer-key"
}

variable "ec2_root_block_device_size" {
  description = "Size of the root block device in GB"
  type        = number
  default     = 30
}

variable "ec2_root_block_device_type" {
  description = "Type of the root block device"
  type        = string
  default     = "gp3"
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
  description = "Public SSH key for EC2 access"
  type        = string
}

variable "additional_public_key" {
  description = "Additional public SSH key for EC2 access"
  type        = string
}

variable "eip_allocation_id" {
  description = "Allocation ID of the Elastic IP to associate with the instance"
  type        = string
}
