variable "environment" {
  description = "The name of the environment. Usually `shared`, `stage`, or `prod`."
  type        = string
}

variable "region" {
  description = "AWS region"
  default     = "us-east-1"
  type        = string
}

variable "ecr_name" {
  description = "The name of the ECR repository"
  default     = "chronos2-ecr"
  type        = string
}
