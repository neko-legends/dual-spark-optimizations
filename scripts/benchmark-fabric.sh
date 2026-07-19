#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"
load_config
require_config WORKER_SSH HEAD_ROCE_IP WORKER_ROCE_IP \
  HEAD_NCCL_IB_HCA HEAD_NCCL_IB_GID_INDEX \
  WORKER_NCCL_IB_HCA WORKER_NCCL_IB_GID_INDEX
require_command iperf3
require_command ib_write_bw
require_command ssh

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
output_dir="${OUTPUT_DIR:-$ROOT_DIR/fabric-results/$timestamp}"
parallel_streams="${IPERF_STREAMS:-4}"
duration="${IPERF_SECONDS:-15}"
mkdir -p "$output_dir"

ping -c 3 -W 2 "$WORKER_ROCE_IP" | tee "$output_dir/ping.txt"

run_iperf() {
  local direction="$1"
  local reverse_flag=()
  [ "$direction" = reverse ] && reverse_flag=(-R)
  ssh "$WORKER_SSH" "iperf3 -s -1 -D -B '$WORKER_ROCE_IP'"
  sleep 1
  iperf3 -c "$WORKER_ROCE_IP" -B "$HEAD_ROCE_IP" \
    -P "$parallel_streams" -t "$duration" -J "${reverse_flag[@]}" \
    >"$output_dir/iperf3-$direction.json"
}

run_iperf forward
run_iperf reverse

worker_log="/tmp/dual-spark-ib-write-bw-$timestamp.txt"
worker_pid="$(ssh "$WORKER_SSH" "nohup ib_write_bw -d '$WORKER_NCCL_IB_HCA' -x '$WORKER_NCCL_IB_GID_INDEX' -F --report_gbits -s 8388608 -n 1000 >'$worker_log' 2>&1 & echo \$!")"
cleanup_rdma() {
  ssh "$WORKER_SSH" "kill '$worker_pid' 2>/dev/null || true" || true
}
trap cleanup_rdma EXIT INT TERM
sleep 2
timeout 180 ib_write_bw -d "$HEAD_NCCL_IB_HCA" -x "$HEAD_NCCL_IB_GID_INDEX" \
  -F --report_gbits -s 8388608 -n 1000 "$WORKER_ROCE_IP" \
  | tee "$output_dir/ib-write-bw-client.txt"
ssh "$WORKER_SSH" "cat '$worker_log'" >"$output_dir/ib-write-bw-server.txt"
cleanup_rdma
trap - EXIT INT TERM

echo "Fabric benchmarks complete: $output_dir"
