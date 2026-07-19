#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_config
require_config WORKER_SSH WORKER_CHECKOUT MODEL_DIR WORKER_MODEL_DIR \
  HEAD_ROCE_IP WORKER_ROCE_IP HEAD_NCCL_SOCKET_IFNAME HEAD_NCCL_IB_HCA \
  HEAD_NCCL_IB_GID_INDEX WORKER_NCCL_SOCKET_IFNAME WORKER_NCCL_IB_HCA \
  WORKER_NCCL_IB_GID_INDEX DSPARK_VLLM_IMAGE MASTER_PORT

require_command docker
require_command rsync
require_command ssh

[ -f "$MODEL_DIR/model.safetensors.index.json" ] || die "model is missing on Forge: $MODEL_DIR"
ssh "$WORKER_SSH" test -f "$WORKER_MODEL_DIR/model.safetensors.index.json" || \
  die "model is missing on Anvil: $WORKER_MODEL_DIR"

echo "Syncing deployment files to Anvil (model weights are not included)..."
ssh "$WORKER_SSH" "mkdir -p '$WORKER_CHECKOUT'"
rsync -az \
  --exclude .git/ --exclude .env --exclude .venv-hf/ --exclude benchmark-results/ \
  "$ROOT_DIR/" "$WORKER_SSH:$WORKER_CHECKOUT/"
scp "$ENV_FILE" "$WORKER_SSH:$WORKER_CHECKOUT/.env"

echo "Starting Anvil rank 1 first..."
ssh "$WORKER_SSH" "
  cd '$WORKER_CHECKOUT'
  set -a
  source .env
  source 'profiles/$PROFILE.env'
  set +a
  COMPOSE_PROJECT_NAME=dual-spark \
  MODEL_DIR='$WORKER_MODEL_DIR' \
  NODE_RANK=1 HEADLESS=1 \
  MASTER_ADDR='$HEAD_ROCE_IP' MASTER_PORT='$MASTER_PORT' \
  VLLM_HOST_IP='$WORKER_ROCE_IP' \
  NCCL_SOCKET_IFNAME='$WORKER_NCCL_SOCKET_IFNAME' \
  NCCL_IB_HCA='$WORKER_NCCL_IB_HCA' \
  NCCL_IB_GID_INDEX='$WORKER_NCCL_IB_GID_INDEX' \
  docker compose --env-file .env -f docker-compose.dspark.yml up -d
"

echo "Starting Forge rank 0..."
COMPOSE_PROJECT_NAME=dual-spark \
MODEL_DIR="$MODEL_DIR" \
NODE_RANK=0 HEADLESS='' \
MASTER_ADDR="$HEAD_ROCE_IP" MASTER_PORT="$MASTER_PORT" \
VLLM_HOST_IP="$HEAD_ROCE_IP" \
NCCL_SOCKET_IFNAME="$HEAD_NCCL_SOCKET_IFNAME" \
NCCL_IB_HCA="$HEAD_NCCL_IB_HCA" \
NCCL_IB_GID_INDEX="$HEAD_NCCL_IB_GID_INDEX" \
docker compose --env-file "$ENV_FILE" -f "$ROOT_DIR/docker-compose.dspark.yml" up -d

api="http://${VLLM_HOST:-127.0.0.1}:${VLLM_PORT:-8888}/v1/models"
attempts="${WAIT_ATTEMPTS:-100}"
delay="${WAIT_SECONDS:-15}"
echo "Waiting for $api (model initialization can take several minutes)..."
for _ in $(seq 1 "$attempts"); do
  if curl -fsS --max-time 5 "$api" >/dev/null; then
    echo "Dual-Spark API is ready: $api"
    docker compose --env-file "$ENV_FILE" -f "$ROOT_DIR/docker-compose.dspark.yml" ps
    ssh "$WORKER_SSH" "cd '$WORKER_CHECKOUT' && docker compose --env-file .env -f docker-compose.dspark.yml ps"
    exit 0
  fi
  sleep "$delay"
done

echo "Timed out waiting for the API. Recent Forge logs:" >&2
docker compose --env-file "$ENV_FILE" -f "$ROOT_DIR/docker-compose.dspark.yml" logs --tail=150 >&2 || true
echo "Recent Anvil logs:" >&2
ssh "$WORKER_SSH" "cd '$WORKER_CHECKOUT' && docker compose --env-file .env -f docker-compose.dspark.yml logs --tail=150" >&2 || true
exit 1
