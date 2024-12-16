variable "bucket_name" {
  description = "The name of the S3 bucket to store Terraform state. Must be globally unique."
  type        = string
  default     = "chronos2-terraform-state-storage"
}

variable "table_name" {
  description = "The name of the DynamoDB table. Must be unique in this AWS account."
  type        = string
  default     = "terraform-state-locks"
}

variable "aws_region" {
  description = "The AWS region used by the deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "The name of the development environment. Usually `stage` or `prod`."
  type        = string
}
