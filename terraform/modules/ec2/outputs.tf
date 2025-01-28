output "instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.deployment.id
}

output "public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_eip.deployment.public_ip
}

output "instance_public_dns" {
  description = "The public DNS name of the EC2 instance"
  value       = aws_eip.deployment.public_dns
}
