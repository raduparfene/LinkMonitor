variable "region" {
  type        = string
  default     = "eu-central-1"
}

variable "ami_id" {
  type = string
  description = "The AMI used for LinkMonitor EC2"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID (e.g., vpc-xxxxxxxxxxxxx)"
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID (e.g., subnet-xxxxxxxxxxxxx)"
}

variable "key_pair_name" {
  type        = string
  description = "Your EC2 key pair name (e.g., login-key)"
}

variable "eip_allocation_id" {
  type      = string
  sensitive = true
}