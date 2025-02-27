# State management backend configuration
variable "state_bucket_name" {
  description = "S3 bucket for Terraform state"
  type        = string
}

variable "state_backend_key" {
  description = "Path to the shared state file"
  type        = string
}

variable "state_table_name" {
  description = "DynamoDB table name for state locking"
  type        = string
}

variable "state_storage_region" {
  description = "Region for state storage"
  type        = string
  default     = "us-east-1"
}
