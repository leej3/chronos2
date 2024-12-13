output "subnet_id" {
  value = module.networking.subnet_id
}

output "security_group_id" {
  value = module.networking.security_group_id
}

output "instance_profile_name" {
  value = module.iam_role_and_policy.instance_profile_name
}
