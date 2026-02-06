# Must have prerequisite 

1. Create IAM User: linkmonitor-automation
2. Attach these permissions to linkmonitor-automation user:
```
AmazonEC2FullAccess
AmazonSSMReadOnlyAccess
AmazonVPCReadOnlyAccess
```
4. Create Access Keys: choose linkmonitor-automation user -> **Security credentials** Tab -> **Create access key**
5. CLI option
6. Copy the ```Secret access key```, as you are prompted ```This is the only time that the secret access key can be viewed or downloaded. You cannot recover it later. However, you can create a new access key any time```:

![img_1.png](../docs-pictures/aws%20access%20key.png)

7. Create ```credentials``` **file** in ~/.aws with the following content:
```
[default]
aws_access_key_id = Access key (found in the key name)
aws_secret_access_key = Secret access key you just copied 
```

8. Create ```config``` **file** in ~/.aws with the following lines:
```
[default]
region = eu-central-1
output = json
```
9. Install AWS CLI locally:
```shell
./aws/shell_scripts/01_install_aws_locally.sh
```


# ❗ AWS EIP (Elastic IP) consideration:
- Some target websites restrict or block traffic originating from known cloud provider IP ranges (such as AWS), which can affect scraping reliability
- During testing, certain Elastic IPs were blocked at the application level by target sites, despite being fully reachable at the network level 
- To keep the setup flexible and allow easy IP rotation if needed, the **Elastic IP is currently managed outside of Terraform**
- This avoids unnecessary infrastructure changes when dealing with external IP-based restrictions
- For that reason, I decided to not include the EIP inside the terraform scripts
```shell
curl -v https://example.com # can fail if IP is blocked
```

# Prepare Infrastructure
- If you've decided to stick to an Elastic IP, consider changing the ```environment.properties``` inside shell_scripts

## Run terraform to access the EC2 Instance:
```shell
./aws/shell_scripts/02_run_terraform.sh
```

## Copy local python files:
```shell
./aws/shell_scripts/03_copy_files_to_aws.sh
```

## Prepare python installation and scripts:
```shell
./aws/shell_scripts/04_aws_python_setup.sh
```
