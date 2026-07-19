#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_config
require_config SERVED_MODEL_NAME MODEL_REVISION DSPARK_VLLM_IMAGE WORKER_SSH

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output_dir="${OUTPUT_DIR:-$ROOT_DIR/benchmark-results/$PROFILE/$timestamp}"
runs="${BENCHMARK_RUNS:-1}"
max_tokens="${BENCHMARK_MAX_TOKENS:-256}"
mkdir -p "$output_dir"

git -C "$ROOT_DIR" rev-parse HEAD >"$output_dir/git-revision.txt" 2>/dev/null || echo uncommitted >"$output_dir/git-revision.txt"
docker image inspect "$DSPARK_VLLM_IMAGE" >"$output_dir/runtime-image-inspect.json"
grep -Eiv '(^|_)(token|secret|password|key)=' "$ENV_FILE" >"$output_dir/config.env"
cp "$ROOT_DIR/profiles/$PROFILE.env" "$output_dir/profile.env"
"$SCRIPT_DIR/capture-cluster-state.sh" "$output_dir/before"

telemetry_query='timestamp,temperature.gpu,power.draw,clocks.current.sm,clocks.current.memory,utilization.gpu,memory.used'
nvidia-smi --query-gpu="$telemetry_query" --format=csv -l 1 >"$output_dir/head-telemetry.csv" &
head_telemetry_pid=$!
ssh "$WORKER_SSH" nvidia-smi --query-gpu="$telemetry_query" --format=csv -l 1 >"$output_dir/worker-telemetry.csv" &
worker_telemetry_pid=$!

stop_telemetry() {
  kill "$head_telemetry_pid" "$worker_telemetry_pid" 2>/dev/null || true
  wait "$head_telemetry_pid" "$worker_telemetry_pid" 2>/dev/null || true
}
trap stop_telemetry EXIT INT TERM

run_case() {
  local prompt="$1"
  local concurrency="$2"
  local name
  name="$(basename "$prompt" .txt)-c$concurrency"
  curl -fsS http://127.0.0.1:8888/metrics >"$output_dir/$name.metrics.before.txt" || true
  python3 "$SCRIPT_DIR/benchmark.py" \
    --prompt-file "$prompt" \
    --model "$SERVED_MODEL_NAME" \
    --model-revision "$MODEL_REVISION" \
    --profile "$PROFILE" \
    --runs "$runs" \
    --concurrency "$concurrency" \
    --max-tokens "$max_tokens" \
    --output "$output_dir/$name.json" \
    | tee "$output_dir/$name.stdout.txt"
  curl -fsS http://127.0.0.1:8888/metrics >"$output_dir/$name.metrics.after.txt" || true
  if [ -s "$output_dir/$name.metrics.before.txt" ] && [ -s "$output_dir/$name.metrics.after.txt" ]; then
    python3 "$SCRIPT_DIR/metrics-delta.py" \
      "$output_dir/$name.metrics.before.txt" \
      "$output_dir/$name.metrics.after.txt" \
      --output "$output_dir/$name.speculative-delta.json"
  fi
}

for prompt in "$ROOT_DIR"/benchmarks/prompts/book-context-{10k,200k,300k}.txt; do
  run_case "$prompt" 1
done

if [ "${FULL_CONCURRENCY:-0}" = 1 ]; then
  for prompt in "$ROOT_DIR"/benchmarks/prompts/book-context-{10k,200k,300k}.txt; do
    run_case "$prompt" 4
  done
fi

stop_telemetry
trap - EXIT INT TERM
"$SCRIPT_DIR/capture-cluster-state.sh" "$output_dir/after"
echo "Benchmark suite complete: $output_dir"
