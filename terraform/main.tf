provider "aws" {
  region = var.region
}

##############################
#  EXISTING STATIC IP (EIP)  #
#  NOTE: created manually    #
##############################
data "aws_eip" "static_ip" {
  id = var.eip_allocation_id
}

resource "aws_eip_association" "tf_eip_aws_eip_association_link_monitor" {
  instance_id   = aws_instance.tf_ec2_instance_link_monitor.id
  allocation_id = data.aws_eip.static_ip.id
}

resource "aws_security_group" "tf_security_group_link_monitor" {
  name        = "lm-security-group"
  description = "Allow SSH only from anywhere (you can restrict later)"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


