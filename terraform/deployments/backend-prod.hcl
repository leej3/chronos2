bucket         = "chronos2-terraform-state-storage-prod"
key            = "terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "terraform-state-locks-prod"
encrypt        = true
