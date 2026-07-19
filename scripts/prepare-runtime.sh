#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_config
require_config DSPARK_VLLM_IMAGE WORKER_SSH
require_command docker
require_command ssh

case "$PROFILE" in
  fast)
    "$SCRIPT_DIR/verify-overlay-sources.sh"
    docker build \
      -f "$ROOT_DIR/recipe/Dockerfile.dspark-runtime-overlay" \
      -t "$DSPARK_VLLM_IMAGE" \
      "$ROOT_DIR/recipe/overlay"
    ;;
  agent)
    require_config UPSTREAM_RUNTIME_IMAGE
    docker pull "$UPSTREAM_RUNTIME_IMAGE"
    docker tag "$UPSTREAM_RUNTIME_IMAGE" "$DSPARK_VLLM_IMAGE"
    ;;
  *)
    die "unsupported profile: $PROFILE"
    ;;
esac

echo "Streaming runtime image once from Forge to Anvil over the direct fabric..."
docker save "$DSPARK_VLLM_IMAGE" | ssh "$WORKER_SSH" docker load

docker run --rm --entrypoint /opt/env/bin/python "$DSPARK_VLLM_IMAGE" \
  -c "import vllm.v1.spec_decode.dspark; print('Forge runtime imports OK')"
ssh "$WORKER_SSH" docker run --rm --entrypoint /opt/env/bin/python "$DSPARK_VLLM_IMAGE" \
  -c "import vllm.v1.spec_decode.dspark; print('Anvil runtime imports OK')"

echo "Runtime profile '$PROFILE' is present on both nodes."
