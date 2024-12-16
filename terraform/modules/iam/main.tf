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

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "profile" {
  name               = "${var.instance_profile_role_name}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "profile" {
  role       = aws_iam_role.profile.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "profile" {
  name = "${var.instance_profile_name}-${var.environment}"
  role = aws_iam_role.profile.name
}

resource "aws_iam_policy" "cd" {
  name   = "${var.cd_iam_policy_name}-${var.environment}"
  policy = file("${path.module}/policies/gha-policy.json")
}

resource "aws_iam_role" "cd" {
  name = "${var.cd_iam_role_policy_name}-${var.environment}"
  assume_role_policy = templatefile("${path.module}/policies/assume-role.json.tftpl",
    {
      AWS_ACCOUNT_ID = var.AWS_ACCOUNT_ID
    },
  )
}

resource "aws_iam_role_policy_attachment" "cd" {
  role       = aws_iam_role.cd.name
  policy_arn = aws_iam_policy.cd.arn
}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]
  thumbprint_list = ["1b511abead59c6ce207077c0bf0e0043b1382612"]
}
