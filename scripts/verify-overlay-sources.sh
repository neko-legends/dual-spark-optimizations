#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKERFILE="${1:-$REPO_DIR/recipe/Dockerfile.dspark-runtime-overlay}"
CONTEXT_DIR="${2:-$REPO_DIR/recipe/overlay}"

missing=0

while IFS= read -r source; do
  [ -z "$source" ] && continue
  if [ ! -e "$CONTEXT_DIR/$source" ]; then
    echo "Missing overlay source referenced by $(basename "$DOCKERFILE"): $source" >&2
    missing=1
  fi
done < <(awk '$1 == "COPY" { print $2 }' "$DOCKERFILE")

if [ "$missing" -ne 0 ]; then
  exit 1
fi

grep -Fq '_store_main_kv_ragged' \
  "$CONTEXT_DIR/vllm/models/deepseek_v4/nvidia/dspark.py" || {
  echo "Missing DSpark ragged-KV concurrency support" >&2
  exit 1
}
grep -Fq 'req_ids: list[str]' \
  "$CONTEXT_DIR/vllm/v1/spec_decode/dspark_proposer.py" || {
  echo "Missing DSpark stable request-slot support" >&2
  exit 1
}
grep -Fq 'dspark_propose_kwargs' \
  "$CONTEXT_DIR/vllm/v1/worker/gpu_model_runner.py" || {
  echo "Missing DSpark request-ID forwarding" >&2
  exit 1
}

echo "Overlay source check passed for $DOCKERFILE"
