variable "region" {
  description = "AWS region"
  default     = "us-east-1"
  type        = string
}

variable "availability_zone_letter_identifier" {
  description = "The letter identifier for the AWS Availablity Zone. Usually `a` or `b`."
  default     = "a"
  type        = string
}

# tflint-ignore: terraform_unused_declarations
variable "ssh_port" {
  description = "Non-standard port for SSH"
  default     = 22
  type        = number
}

variable "environment" {
  description = "The name of the environment. Usually `shared`, `stage`, or `prod`."
  type        = string
}

variable "vpc_name" {
  description = "The name used to tag the VPC."
  default     = "chronos2-vpc"
  type        = string
}

variable "vpc_ipv4_cidr_block" {
  description = "The IPv4 CIDR block for the VPC. CIDR can be explicitly set or it can be derived from IPAM using `ipv4_netmask_length`"
  default     = "10.0.0.0/16"
  type        = string
}

variable "internet_gateway_name" {
  description = "The name of the internet gateway"
  default     = "chronos2-internet-gateway"
  type        = string
}

variable "route_table_name" {
  description = "The name used to tag the route table."
  default     = "chronos2-route-table"
  type        = string
}

variable "route_table_ipv4_cidr_block" {
  description = "The IPv4 CIDR block of the route table"
  default     = "0.0.0.0/0"
  type        = string
}

variable "route_table_ipv6_cidr_block" {
  description = "The IPv6 CIDR block of the route table"
  default     = "::/0"
  type        = string
}

variable "vpc_domain_name" {
  description = "The suffix domain name to use by default when resolving non Fully Qualified Domain Names. In other words, this is what ends up being the `search` value in the `/etc/resolv.conf` file."
  default     = "compute-1.amazonaws.com"
  type        = string
}

variable "vpc_domain_name_servers" {
  description = "List of name servers to configure in `/etc/resolv.conf`. If you want to use the default AWS nameservers you should set this to `AmazonProvidedDNS`."
  default     = ["AmazonProvidedDNS"]
  type        = list(string)
}

variable "vpc_dhcp_options_name" {
  description = "The name used to tag the VPC DHCP options"
  default     = "chronos2-dhcp-options"
  type        = string
}

variable "subnet_name" {
  description = "The name used to tag the AWS subnet"
  default     = "main-subnet"
  type        = string
}

variable "subnet_ipv4_cidr_block" {
  description = "The IPv4 CIDR block for the subnet."
  default     = "10.0.1.0/24"
  type        = string
}
