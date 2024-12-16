terraform {
  required_version = ">= 1.0.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_ipv4_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = "${var.vpc_name}-${var.environment}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.internet_gateway_name}-${var.environment}"
  }
}

# Route Table
resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = var.route_table_ipv4_cidr_block
    gateway_id = aws_internet_gateway.main.id
  }
  route {
    ipv6_cidr_block = var.route_table_ipv6_cidr_block
    gateway_id      = aws_internet_gateway.main.id
  }
  tags = {
    Name = "${var.route_table_name}-${var.environment}"
  }
}

# Network ACL
resource "aws_network_acl" "allow_all" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "allow_all_acl"
  }
}

resource "aws_network_acl_rule" "allow_all_inbound" {
  network_acl_id = aws_network_acl.allow_all.id
  rule_number    = 100
  protocol       = "-1" # -1 means all protocols
  rule_action    = "allow"
  egress         = false
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 65535
}

resource "aws_network_acl_rule" "allow_all_outbound" {
  network_acl_id = aws_network_acl.allow_all.id
  rule_number    = 200
  protocol       = "-1" # -1 means all protocols
  rule_action    = "allow"
  egress         = true
  cidr_block     = "0.0.0.0/0"
  from_port      = 0
  to_port        = 65535
}

resource "aws_security_group" "allow_all" {
  name        = "allow_all_security_group"
  description = "Security group that allows all inbound and outbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "6"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "6"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "17"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "17"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_all_security_group"
  }
}

resource "aws_vpc_dhcp_options" "main" {
  domain_name         = var.vpc_domain_name
  domain_name_servers = var.vpc_domain_name_servers

  tags = {
    Name = "${var.vpc_dhcp_options_name}-${var.environment}"
  }
}

resource "aws_vpc_dhcp_options_association" "main" {
  vpc_id          = aws_vpc.main.id
  dhcp_options_id = aws_vpc_dhcp_options.main.id
}

# main Subnet
resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.subnet_ipv4_cidr_block
  availability_zone       = "${var.region}${var.availability_zone_letter_identifier}"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.subnet_name}-${var.environment}"
  }
}

# Route Table Association for main
resource "aws_route_table_association" "main" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.main.id
}

# Associate the Network ACL with the Subnet
resource "aws_network_acl_association" "main" {
  subnet_id      = aws_subnet.main.id
  network_acl_id = aws_network_acl.allow_all.id
}
