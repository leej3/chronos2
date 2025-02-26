variable "deptype" {
  description = "The deployment type (stage or prod)"
  type        = string
  validation {
    condition     = contains(["stage", "prod"], var.deptype)
    error_message = "deptype must be either 'stage' or 'prod'"
  }
}

variable "pi_user" {
  description = "The value of pi, can be overridden but defaults to 'pi'"
  type        = string
  default     = "pi"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.small"
  type        = string
}

variable "public_key" {
  description = "SSH public key for EC2 instance access"
  type        = string
}

variable "additional_public_key" {
  description = "Additional SSH public key for EC2 instance access"
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  type        = string
}

variable "table_name" {
  description = "Name of the DynamoDB table for state locking"
  type        = string
}
