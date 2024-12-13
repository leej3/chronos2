variable "environment" {
  description = "The name of the environment. Usually `shared`, `stage`, or `prod`."
  type        = string
}

variable "region" {
  description = "AWS region"
  default     = "us-east-1"
  type        = string
}

variable "instance_profile_name" {
  description = "The name of the instance profile"
  default     = "chronos2-instance-profile"
  type        = string
}

variable "instance_profile_role_name" {
  description = "The name of the instance profile"
  default     = "chronos2-instance-profile-role"
  type        = string
}

variable "cd_iam_policy_name" {
  description = "The name of the IAM policy for continuous deployment to ECR"
  default     = "GitHubActions-ECR"
  type        = string
}

variable "cd_iam_role_policy_name" {
  description = "The name of the IAM role policy for continuous deployment to ECR"
  default     = "github-actions-role"
  type        = string
}

variable "AWS_ACCOUNT_ID" {
  # All caps variable name because this is read in as an environment variable
  description = "The ID of your AWS account. This should be set as an environment variable `TF_VAR_AWS_ACCOUNT_ID`."
  type        = string
}
