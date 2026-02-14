# Install Terraform
```shell
sudo apt update && sudo apt install -y gnupg software-properties-common curl
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update
terraform -v
```

# Inside project root directory, execute these, to create the infrastructure:
```shell
terraform -chdir=terraform destroy -auto-approve 
terraform -chdir=terraform init
terraform -chdir=terraform plan
terraform -chdir=terraform apply -auto-approve
```
