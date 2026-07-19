# Dual-Spark release checklist

This is the resumable source of truth for humans and AI agents. Check an item
only after recording evidence in the repository or the final deployment notes.

## 1. Repository and provenance

- [x] Attach `D:\forPublic\dual-spark-optimizations` to the empty GitHub repository.
- [x] Audit drowzeys v1.0 versus v1.1 model differences.
- [x] Audit Tony's runtime, overlay, launch order, and published benchmark scope.
- [x] Audit NVIDIA's Connect Two Sparks and Tailscale playbooks.
- [x] Preserve Tony's MIT license.
- [x] Preserve drowzeys / keys' MIT license.
- [x] Credit Rafael Caricio and MiaAI-Lab transitively and directly.
- [x] Separate software licensing from gated model-weight licensing.
- [x] Add `AGENTS.md` and Copilot instructions.
- [x] Add LF normalization and executable script modes.
- [x] Add CI for ShellCheck, unit tests, overlay inputs, fixture hashes, and Compose rendering.
- [x] Review every vendored overlay file against Tony's pinned current commit.
- [x] Record the exact Tony, drowzeys, NVIDIA, and model revisions.
- [x] Record the resolved base-image digest after the first runtime pull.
- [x] Record resolved runtime digests alongside readable tags.
- [x] Commit the initial implementation with a provenance-focused message.
- [x] Push the initial branch to `neko-legends/dual-spark-optimizations`.
- [ ] Enable an appropriate branch protection policy if desired.
- [ ] Add a release tag only after all recommended profiles are measured.

## 2. Machine identity and base state

- [x] Keep distinct hostnames on the two nodes.
- [x] Confirm the same Linux username on both nodes.
- [x] Regenerate the affected node's duplicated factory SSH host key.
- [x] Confirm the two nodes have different ED25519 host fingerprints.
- [x] Verify Ubuntu 24.04.4 on both nodes.
- [x] Verify NVIDIA driver 580.159.03 on both nodes.
- [x] Verify Docker and Docker Compose on both nodes.
- [x] Add the deployment user to the Docker group on both nodes and reconnect/reboot.
- [x] Install benchmark/bootstrap packages on both nodes.
- [x] Verify roughly 3.5 TiB free storage per node.
- [x] Install the head node's public SSH key on the worker.
- [x] Verify head-to-worker key authentication over the LAN IP.
- [x] Record both `/etc/machine-id` values; discovery: factory IDs are duplicated.
- [x] Back up and regenerate the duplicated `/etc/machine-id`.
- [x] Reboot the affected node and confirm the machine IDs differ.
- [x] Record DGX OS/Spark software versions (7.2.3 base, 7.5.0 OTA).
- [x] Record CX-7 firmware `28.45.4028` and NVIDIA kernel/driver evidence.
- [x] Confirm both clocks report NTP synchronization and America/Los_Angeles.
- [x] Capture an initial idle thermal/power sample on each node.

## 3. Direct 200GbE fabric

- [x] Detect the head node's active CX-7 interface and HCA.
- [x] Detect the worker node's active CX-7 interface and HCA.
- [x] Add node-specific NIC/HCA settings; do not assume matching port names.
- [x] Run head fabric setup with sudo (`10.100.10.1/24`).
- [x] Run worker fabric setup with sudo (`10.100.10.2/24`).
- [x] Confirm `/etc/netplan/40-dual-spark.yaml` permissions are `600`.
- [x] Confirm normal LAN interfaces and default routes remain unchanged.
- [x] Confirm bidirectional ICMP over `10.100.10.1` / `10.100.10.2`.
- [x] Confirm RoCE v2 GID index `3` appears after IPv4 assignment on both nodes.
- [x] Verify passwordless head-to-worker SSH over `10.100.10.2`.
- [x] Benchmark TCP bandwidth with `iperf3` in both directions.
- [x] Benchmark four streams and record iperf3 CPU utilization.
- [x] Validate RDMA with `ib_write_bw` or an equivalent perftest.
- [x] Record 200,000 Mb/s full-duplex link, MTU 1500, and active port state.
- [ ] Decide whether jumbo MTU improves measured throughput before enabling it.
- [ ] Run an NCCL all-reduce sanity/performance test over the selected HCA.
- [ ] Capture `NCCL_DEBUG=INFO` evidence that traffic uses CX-7, not LAN/Tailscale.
- [ ] Document netplan rollback and test it without applying it permanently.

## 4. Tailscale management plane

- [x] Install Tailscale on both nodes from the official Noble repository.
- [x] Authenticate both nodes into the existing tailnet.
- [x] Confirm their MagicDNS names are unique.
- [ ] Confirm Windows can `tailscale ping` both Sparks.
- [ ] Confirm SSH key authentication works over each Tailscale address.
- [x] Keep NCCL and model transfer off Tailscale.
- [ ] Review tailnet ACLs so the vLLM API is not unintentionally exposed.
- [ ] Record Tailscale IPs without committing reusable auth keys.

## 5. Gated model acquisition and replication

- [x] Confirm the v1.1 repository is gated (`gated=auto`).
- [x] Confirm the snapshot contains 48 safetensor shards.
- [x] Estimate the complete snapshot at about 155.44 GiB.
- [x] Configure the head as the only Hugging Face download node.
- [x] Add shard-index verification before and after transfer.
- [x] Add resumable `rsync --partial` transfer over the direct fabric.
- [x] Accept the model's Hugging Face gate with the intended account.
- [x] Authenticate the head-only HF CLI environment.
- [x] Pin the resolved model commit SHA in `.env.example`.
- [x] Download the complete v1.1 snapshot on the head.
- [x] Verify all 48 shards and record total bytes on the head.
- [x] Transfer the snapshot once from head to worker via `10.100.10.2`.
- [x] Verify all 48 shards and total bytes on the worker.
- [x] Add a deterministic SHA-256 manifest check across both model copies.
- [x] Run the SHA-256 manifest check successfully on the downloaded copies.
- [x] Confirm no full model download occurred independently on the worker.
- [x] Record transfer: 173,766,905,451 bytes in 536 s at 0.302 GiB/s.
- [x] Confirm at least 500 GiB free space remains on both nodes.

## 6. Runtime preparation

- [x] Vendor and verify Tony-derived overlay sources.
- [x] Add a `fast` profile using `fp8`, C1, and 900K context.
- [x] Add a `long-c4` profile using stage-c, `nvfp4_ds_mla`, C4, and 1M context.
- [x] Add a `fast-c4` profile with the Tony runtime and four live sequences.
- [x] Port drowzeys' ragged-batch/stable-slot C4 support into the fast overlay.
- [x] Keep unsupported KV-cache modes out of the Tony-derived image.
- [x] Build/pull the runtime only on the head and stream it to the worker.
- [x] Validate Compose rendering for all profiles on the head.
- [x] Build the `fast` image on the head.
- [x] Record the fast image ID and resolved base-image digest.
- [x] Stream and load the fast image on the worker.
- [x] Verify DSpark imports inside the fast image on both nodes.
- [x] Pull/tag the drowzeys stage-c image on the head.
- [x] Record the stage-c image ID and registry digest.
- [x] Stream and load the stage-c image on the worker.
- [x] Verify DSpark imports inside the stage-c image on both nodes.
- [x] Confirm both nodes report identical image IDs for each profile.

## 7. Cluster launch validation

- [x] Implement worker-first launch.
- [x] Implement head-first shutdown.
- [x] Keep the API loopback-only by default.
- [x] Mount local verified weights read-only at `/model`.
- [x] Add node-specific HCA, interface, GID, and host-IP injection.
- [x] Run `scripts/preflight.sh` successfully.
- [ ] Confirm no stale vLLM/DSpark containers or GPU processes.
- [x] Launch worker rank 1 and verify it waits cleanly.
- [x] Launch head rank 0 and wait for model initialization.
- [x] Confirm `/v1/models` returns the configured served model.
- [x] Run minimal deterministic warmup chat completions on all runtimes.
- [x] Verify tool parser and reasoning parser startup flags.
- [x] Confirm thinking defaults to false for agent-oriented use.
- [x] Inspect logs for TCP fallback, GID, memory, CUDA graph, and NCCL warnings.
- [x] Confirm the endpoint remains bound to `127.0.0.1:8888`.
- [ ] Test a Windows SSH tunnel to the loopback API.
- [x] Perform a clean stop/start cycle while switching profiles.
- [x] Verify restart does not redownload weights or images.

## 8. Benchmark fixtures and methodology

- [x] Import the deterministic 10K prompt fixture.
- [x] Import the deterministic 200K prompt fixture.
- [x] Import the deterministic 300K prompt fixture.
- [x] Preserve and document SHA-256 for every fixture.
- [x] Report server-returned prompt tokens rather than filename estimates.
- [x] Add streaming TTFT measurement.
- [x] Add decode tok/s and end-to-end tok/s measurement.
- [x] Add concurrency and sequential-run controls.
- [x] Capture before/after Prometheus metrics.
- [x] Compute draft acceptance and accepted-tokens-per-draft from metric deltas.
- [x] Capture runtime image metadata and effective profile configuration.
- [x] Add exact model revision and profile to every benchmark report.
- [x] Add per-second GPU clocks, temperatures, power, utilization, and memory telemetry.
- [ ] Add NCCL counters or logs sufficient to prove fabric selection.
- [x] Run one discarded 10K/32-token warmup before each measured profile.
- [x] Use a 256-token output cap for the initial matrix to bound thermal/runtime cost.
- [x] Review published benchmark artifacts for prompt text and private data.

## 9. Fast-profile benchmark matrix

- [x] Fast C1: 10K prompt, three measured runs.
- [x] Fast C1: 200K prompt, three measured runs.
- [x] Fast C1: 300K prompt, three measured runs.
- [x] Record TTFT, prompt tokens, decode tok/s, acceptance, and wall time.
- [x] Confirm the 900K configured context accepts all three fixtures.
- [ ] Test 512-token and 1,024-token output lengths if thermally stable.
- [ ] Compare MTP speculative token counts 3, 4, 5, and 6.
- [ ] Compare GPU memory utilization 0.80 and 0.82 without unsafe pressure.
- [ ] Measure cold start and warm restart separately.
- [ ] Run a sustained thermal-soak benchmark.

## 10. C4 benchmark matrix

- [x] Stage-c C1: 10K, 200K, and 300K prompts, three measured runs each.
- [x] Stage-c C4: 10K, 200K, and 300K prompts, three groups each.
- [x] Combined fast C1: 10K, 200K, and 300K prompts, three runs each.
- [x] Combined fast C4: 10K, 200K, and 300K prompts, three groups each.
- [x] Record per-request TTFT distribution and aggregate tok/s.
- [x] Confirm the 1M configured context accepts all three fixtures.
- [ ] Exercise Hermes/tool calling without publishing unsafe prompt content.
- [ ] Check for skill-catalog spill and protocol leakage.
- [ ] Validate `max_tokens=8192` operational guidance separately from speed tests.

## 11. Comparison and optimization decisions

- [x] Add a deterministic Markdown/SVG benchmark report generator.
- [x] Render charts from measured fast, combined-C4, and stage-c results.
- [x] Compare all runtimes at identical prompts, outputs, and concurrency.
- [x] Separate TTFT, decode, and aggregate-throughput conclusions.
- [x] Publish draft acceptance and accepted-token metric deltas with each case.
- [ ] Confirm any tok/s gain is repeatable and outside run-to-run variance.
- [x] Confirm configured 900K/1M contexts accept the 300K fixture.
- [x] Confirm model transfer routes over CX-7, not LAN or Tailscale.
- [ ] Reject configurations that corrupt tool calling or produce garble.
- [x] Add live-batch adaptive dispatch between Tony's C1 hot path and stable-slot C4.
- [x] Benchmark `adaptive` at matched C1/C4 10K, 200K, and 300K cases.
- [x] Make `adaptive` the default based on its measured C1/C4 balance.
- [x] Keep `fast` as the dedicated C1 specialist.
- [x] Keep `long-c4` for full-context stage-c operation.
- [x] Document the measured profile boundary and avoid combining unsupported KV modes.

## 12. Documentation and release

- [x] Explain that hostnames do not need to match.
- [x] Explain that only the username must match.
- [x] Explain one-download model replication.
- [x] Explain Tailscale versus CX-7 responsibilities.
- [x] Warn that upstream performance is not a local measurement.
- [x] Add actual TCP, RDMA, route, link, and transfer validation to docs/results.
- [x] Add a tracked benchmark-table and chart location with an honest pending state.
- [x] Replace the pending table/chart with measured data and reviewed raw-result provenance.
- [x] Add tested image/model revision evidence.
- [ ] Add troubleshooting for gated HF access.
- [ ] Add troubleshooting for GID-index and NCCL fallback failures.
- [ ] Add troubleshooting for model OOM and KV-pool sizing.
- [ ] Add recovery instructions for interrupted model/image transfers.
- [ ] Add security guidance for remote API consumers.
- [ ] Run a fresh-agent dry run using only README and `AGENTS.md`.
- [x] Review published performance and fabric claims against raw artifacts.
- [x] Commit and push the measured results after final validation.
