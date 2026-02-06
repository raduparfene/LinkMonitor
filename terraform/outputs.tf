# terraform outputs those values:

output "instance_id" {
  value = aws_instance.tf_ec2_instance_link_monitor.id
}

output "public_ip" {
  value = data.aws_eip.static_ip.public_ip
}

output "state" {
  value = aws_instance.tf_ec2_instance_link_monitor.instance_state
}
