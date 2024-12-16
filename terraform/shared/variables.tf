variable "environment" {
  description = "The name of the environment. Usually `shared`, `stage`, or `prod`."
  default     = "shared"
  type        = string
}

variable "AWS_ACCOUNT_ID" {
  # All caps variable name because this is read in as an environment variable
  description = "The ID of your AWS account. This should be set as an environment variable `TF_VAR_AWS_ACCOUNT_ID`."
  type        = string
}
