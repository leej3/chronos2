variable "environment" {
  description = "The name of the environment. Usually `stage`."
  default     = "stage"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.large"
  type        = string
}

variable "PUBLIC_KEY" {
  description = "The public key used to deploy to the EC2 instance via ssh. All caps because this should be set via an environment variable."
  type        = string
}

variable "additional_public_key" {
  description = "An additional SSH public key to be added to the EC2 instance authorized_keys"
  type        = string
}
