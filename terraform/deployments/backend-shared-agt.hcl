bucket         = "agt-chronos-terraform-state-storage"
key            = "environments/shared/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "agt-chronos-terraform-state-locks"
encrypt        = true
