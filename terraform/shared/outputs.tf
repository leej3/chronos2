output "subnet_id" {
  value = module.networking.subnet_id
}

output "security_group_id" {
  value = module.networking.security_group_id
}

output "instance_profile_name" {
  value = module.iam_role_and_policy.instance_profile_name
}

output "production_eip_allocation_id" {
  description = "The allocation ID of the Production Elastic IP"
  value       = aws_eip.chronos_production.id
}

output "production_eip_public_ip" {
  description = "The public IP address of the Production Elastic IP"
  value       = aws_eip.chronos_production.public_ip
}

output "staging_eip_allocation_id" {
  description = "The allocation ID of the Staging Elastic IP"
  value       = aws_eip.chronos_staging.id
}

output "staging_eip_public_ip" {
  description = "The public IP address of the Staging Elastic IP"
  value       = aws_eip.chronos_staging.public_ip
}
