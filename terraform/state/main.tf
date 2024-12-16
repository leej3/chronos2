terraform {
  required_version = ">= 1.0.0, < 2.0.0"
}

module "stage_state" {
  source      = "../modules/state/"
  environment = "stage"
}

module "prod_state" {
  source      = "../modules/state/"
  environment = "prod"
}

module "shared_state" {
  source      = "../modules/state/"
  environment = "shared"
}
