#!/usr/bin/env bash
set -euo pipefail

worker="${1:?usage: $0 USER@WORKER_FABRIC_IP}"
key="$HOME/.ssh/id_ed25519"

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
if [ ! -f "$key" ]; then
  ssh-keygen -t ed25519 -N "" -C "$(hostname)-to-dual-spark-worker" -f "$key"
fi

echo "Installing $(hostname)'s public key on $worker. You may be prompted once for the worker password."
ssh-copy-id -i "$key.pub" "$worker"
ssh -o BatchMode=yes -o ConnectTimeout=5 "$worker" hostname
echo "Passwordless inter-node SSH is ready."
