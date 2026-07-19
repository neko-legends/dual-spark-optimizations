#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_config
require_config WORKER_SSH

output_dir="${1:?usage: $0 OUTPUT_DIR}"
mkdir -p "$output_dir"

capture='set -u
echo "## identity"
hostname
cat /etc/dgx-release 2>/dev/null || true
echo "## time"
date --iso-8601=seconds
timedatectl show -p NTPSynchronized -p Timezone
echo "## gpu"
nvidia-smi
echo "## fabric"
ibdev2netdev
ip -br addr
ip route
show_gids
echo "## docker"
docker version
docker compose version
docker ps --no-trunc
echo "## storage-memory"
df -h / /home
free -h
echo "## tailscale"
tailscale status 2>&1 || true'

bash -c "$capture" >"$output_dir/head-state.txt" 2>&1
ssh "$WORKER_SSH" bash -c "$(printf '%q' "$capture")" >"$output_dir/worker-state.txt" 2>&1

echo "Captured head and worker state in $output_dir"
