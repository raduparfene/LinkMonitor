# ec2 instance
resource "aws_instance" "tf_ec2_instance_link_monitor" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id
  key_name      = aws_key_pair.login.key_name

  vpc_security_group_ids = [
    aws_security_group.tf_security_group_link_monitor.id
  ]

  root_block_device {
    volume_size = 8
    volume_type = "gp3"
  }

  tags = {
    Name = "LinkMonitorServer"
  }
}