# use the generated key pair
resource "aws_key_pair" "login" {
  key_name   = var.key_pair_name
  public_key = file("${path.module}/../aws/login-key.pub")
}