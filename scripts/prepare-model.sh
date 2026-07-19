#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_config
require_config MODEL_ID MODEL_REVISION MODEL_DIR WORKER_MODEL_DIR WORKER_SSH
require_command python3
require_command rsync
require_command ssh

HF_VENV="${HF_VENV:-$ROOT_DIR/.venv-hf}"
if [ ! -x "$HF_VENV/bin/hf" ]; then
  python3 -m venv "$HF_VENV"
  "$HF_VENV/bin/python" -m pip install --upgrade pip
  "$HF_VENV/bin/python" -m pip install 'huggingface_hub>=0.34,<2'
fi

if [ -z "${HF_TOKEN:-}" ]; then
  HF_HUB_OFFLINE=0 "$HF_VENV/bin/hf" auth whoami >/dev/null 2>&1 || {
    echo "The head node is not authenticated to Hugging Face." >&2
    echo "Accept the gated model terms, then run: $HF_VENV/bin/hf auth login" >&2
    exit 1
  }
fi

mkdir -p "$MODEL_DIR"
echo "Downloading the gated model on the head node only: $MODEL_ID"
HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 "$HF_VENV/bin/hf" download "$MODEL_ID" \
  --revision "$MODEL_REVISION" \
  --local-dir "$MODEL_DIR" \
  --max-workers "${HF_DOWNLOAD_WORKERS:-4}"

manifest="$MODEL_DIR/.dual-spark-shards.sha256"
echo "Hashing the 48 shards on the head node to create a transfer manifest..."
python3 "$SCRIPT_DIR/verify-model.py" "$MODEL_DIR" --write-manifest "$manifest"

echo "Transferring the verified model once over the direct fabric to $WORKER_SSH:$WORKER_MODEL_DIR"
ssh "$WORKER_SSH" "mkdir -p '$WORKER_MODEL_DIR'"
transfer_started="$(date +%s)"
transfer_bytes="$(du -sb "$MODEL_DIR" | awk '{print $1}')"
rsync -aH --partial --info=progress2 "$MODEL_DIR/" "$WORKER_SSH:$WORKER_MODEL_DIR/"
transfer_seconds="$(( $(date +%s) - transfer_started ))"
scp "$SCRIPT_DIR/verify-model.py" "$WORKER_SSH:/tmp/dual-spark-verify-model.py"
ssh "$WORKER_SSH" python3 /tmp/dual-spark-verify-model.py "$WORKER_MODEL_DIR" \
  --check-manifest "$WORKER_MODEL_DIR/.dual-spark-shards.sha256"

echo "transfer_seconds=$transfer_seconds"
awk -v bytes="$transfer_bytes" -v seconds="$transfer_seconds" \
  'BEGIN { if (seconds > 0) printf "transfer_GiB_per_second=%.3f\n", bytes / 1073741824 / seconds }'
echo "Model download and direct-fabric replication complete."
