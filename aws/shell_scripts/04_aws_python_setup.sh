#!/usr/bin/env bash
set -euo pipefail

set -a
source environment.properties
set +a

: "${ELIP:?ELIP is missing/empty in environment.properties}"
ELIP="$ELIP"

ssh -i ~/.ssh/login-key ubuntu@$ELIP <<'EOF'
cd /home/ubuntu/LinkMonitor
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m playwright install --with-deps chromium
python link_monitor.py
EOF