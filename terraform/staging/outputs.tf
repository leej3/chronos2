output "instance_id" {
  description = "The ID of the staging EC2 instance"
  value       = module.ec2.instance_id
}

output "public_ip" {
  description = "The public IP address of the staging EC2 instance"
  value       = module.ec2.public_ip
}

output "instance_public_dns" {
  description = "The public DNS name of the staging EC2 instance"
  value       = module.ec2.instance_public_dns
}
