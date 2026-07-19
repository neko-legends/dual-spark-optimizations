#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_config
require_config WORKER_SSH HEAD_ROCE_IP WORKER_ROCE_IP \
  HEAD_NCCL_SOCKET_IFNAME HEAD_NCCL_IB_HCA HEAD_NCCL_IB_GID_INDEX \
  WORKER_NCCL_SOCKET_IFNAME WORKER_NCCL_IB_HCA WORKER_NCCL_IB_GID_INDEX \
  MODEL_DIR WORKER_MODEL_DIR

require_command docker
require_command ssh
require_command rsync

minimum_kb=$((95 * 1024 * 1024))
head_available_kb="$(awk '/MemAvailable/ { print $2 }' /proc/meminfo)"
[ "$head_available_kb" -ge "$minimum_kb" ] || \
  die "Forge has less than 95 GiB available memory"

echo "Head: $(hostname) ($(whoami))"
[ "$(whoami)" = "jun" ] || echo "warning: expected user jun on the head"
ip -4 addr show dev "$HEAD_NCCL_SOCKET_IFNAME" | grep -F "$HEAD_ROCE_IP/" >/dev/null || \
  die "$HEAD_ROCE_IP is not configured on $HEAD_NCCL_SOCKET_IFNAME"
ibdev2netdev | grep -F "$HEAD_NCCL_IB_HCA" | grep -F '(Up)' >/dev/null || \
  die "$HEAD_NCCL_IB_HCA is not active"
show_gids | awk -v hca="$HEAD_NCCL_IB_HCA" -v idx="$HEAD_NCCL_IB_GID_INDEX" \
  '$1 == hca && $3 == idx { found=1 } END { exit !found }' || \
  die "head GID index $HEAD_NCCL_IB_GID_INDEX not found on $HEAD_NCCL_IB_HCA"

ping -c 2 -W 2 "$WORKER_ROCE_IP" >/dev/null || die "cannot reach worker RoCE IP $WORKER_ROCE_IP"
ssh -o BatchMode=yes -o ConnectTimeout=5 "$WORKER_SSH" true || \
  die "passwordless SSH from head to $WORKER_SSH is not ready"

ssh "$WORKER_SSH" "
  set -eu
  [ \"\$(whoami)\" = jun ]
  ip -4 addr show dev '$WORKER_NCCL_SOCKET_IFNAME' | grep -F '$WORKER_ROCE_IP/' >/dev/null
  ibdev2netdev | grep -F '$WORKER_NCCL_IB_HCA' | grep -F '(Up)' >/dev/null
  show_gids | awk -v hca='$WORKER_NCCL_IB_HCA' -v idx='$WORKER_NCCL_IB_GID_INDEX' \
    '\$1 == hca && \$3 == idx { found=1 } END { exit !found }'
  docker info >/dev/null
  available_kb=\$(awk '/MemAvailable/ { print \$2 }' /proc/meminfo)
  [ \"\$available_kb\" -ge '$((95 * 1024 * 1024))' ]
  mkdir -p '$WORKER_MODEL_DIR'
"

docker info >/dev/null
mkdir -p "$MODEL_DIR"
echo "Preflight passed for profile=$PROFILE: Forge head -> Anvil worker over $HEAD_ROCE_IP/$WORKER_ROCE_IP"
