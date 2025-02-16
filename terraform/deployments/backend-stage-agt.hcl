bucket         = "agt-chronos-terraform-state-storage"
key            = "environments/stage/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "agt-chronos-terraform-state-locks"
encrypt        = true
