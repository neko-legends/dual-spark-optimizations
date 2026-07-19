#!/usr/bin/env bash
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "run this script with sudo" >&2; exit 1; }
target_user="${SUDO_USER:?run this script with sudo from the deployment account}"
id "$target_user" >/dev/null 2>&1 || { echo "user not found: $target_user" >&2; exit 1; }

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv rsync iperf3 perftest shellcheck

if ! id -nG "$target_user" | tr ' ' '\n' | grep -qx docker; then
  usermod -aG docker "$target_user"
  echo "Added $target_user to the docker group. Reconnect or reboot before using Docker."
fi

systemctl enable --now docker
echo "Host bootstrap complete on $(hostname) for user $target_user."
