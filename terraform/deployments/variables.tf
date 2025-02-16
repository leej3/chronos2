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

variable "vite_api_base_url" {
  description = "Base URL for the Vite frontend API"
  type        = string
}

variable "postgres_password" {
  description = "Password for PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "Secret key for JWT authentication"
  type        = string
  sensitive   = true
}

variable "edge_server_ip" {
  description = "IP address of the edge server"
  type        = string
}

variable "edge_server_port" {
  description = "Port number for the edge server"
  type        = string
}

variable "user_1_email" {
  description = "Email for the first user"
  type        = string
}

variable "user_1_password" {
  description = "Password for the first user"
  type        = string
  sensitive   = true
}

variable "frp_auth_token" {
  description = "Authentication token for FRP"
  type        = string
  sensitive   = true
}

variable "bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  type        = string
}

variable "table_name" {
  description = "Name of the DynamoDB table for state locking"
  type        = string
}
