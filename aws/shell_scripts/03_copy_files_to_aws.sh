#!/usr/bin/env bash
set -euo pipefail

set -a
source ./aws/shell_scripts/environment.properties
set +a

: "${ELIP:?ELIP is missing/empty in environment.properties}"
ELIP="$ELIP"

ssh -i ~/.ssh/login-key -o StrictHostKeyChecking=no ubuntu@$ELIP 'mkdir -p /home/ubuntu/LinkMonitor/{links,certs}' && \
rsync -av -e "ssh -i ~/.ssh/login-key" ./links/ ubuntu@$ELIP:/home/ubuntu/LinkMonitor/links/ && \
rsync -av -e "ssh -i ~/.ssh/login-key" ./certs/ ubuntu@$ELIP:/home/ubuntu/LinkMonitor/certs/ && \
rsync -av -e "ssh -i ~/.ssh/login-key" .env link_monitor.py requirements.txt ubuntu@$ELIP:/home/ubuntu/LinkMonitor/