bucket         = "chronos2-terraform-state-storage-stage"
key            = "terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "terraform-state-locks-stage"
encrypt        = true
