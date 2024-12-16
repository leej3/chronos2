output "instance_id" {
  value = aws_instance.deployment.id
}

output "public_dns" {
  value = aws_eip.deployment.public_dns
}

output "public_ip" {
  value = aws_eip.deployment.public_ip
}
