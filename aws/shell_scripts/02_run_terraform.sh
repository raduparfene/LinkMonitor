#!/usr/bin/env bash
set -euo pipefail

set -a
source ./aws/shell_scripts/environment.properties
set +a

: "${ELIP:?ELIP is missing/empty in environment.properties}"
ELIP="$ELIP"

# create a key pair and use it for terraform to access the EC2 Instance
test -f aws/login-key || (ssh-keygen -t ed25519 -f aws/login-key -N "" && chmod 600 aws/login-key)

terraform -chdir=terraform destroy -auto-approve
terraform -chdir=terraform init
terraform -chdir=terraform plan
terraform -chdir=terraform apply -auto-approve

ssh-keygen -R $ELIP 2>/dev/null || true # delete previous blueprint from local machine