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
- [ ] Record the resolved base-image digest after the first runtime pull.
- [ ] Decide whether to pin runtime images by digest in addition to tag.
- [ ] Commit the initial implementation with a provenance-focused message.
- [ ] Push the initial branch to `neko-legends/dual-spark-optimizations`.
- [ ] Enable an appropriate branch protection policy if desired.
- [ ] Add a release tag only after both profiles are measured.

## 2. Machine identity and base state

- [x] Keep distinct hostnames: Forge and Anvil.
- [x] Confirm the same Linux username (`jun`) on both nodes.
- [x] Regenerate Anvil's duplicated factory SSH host key.
- [x] Confirm Forge and Anvil now have different ED25519 host fingerprints.
- [x] Verify Ubuntu 24.04.4 on both nodes.
- [x] Verify NVIDIA driver 580.159.03 on both nodes.
- [x] Verify Docker and Docker Compose on both nodes.
- [ ] Add `jun` to the Docker group on both nodes and reconnect/reboot.
- [ ] Install benchmark/bootstrap packages on both nodes.
- [x] Verify roughly 3.5 TiB free storage per node.
- [x] Install Forge's public SSH key on Anvil.
- [x] Verify Forge-to-Anvil key authentication over the LAN IP.
- [x] Record both `/etc/machine-id` values; discovery: factory IDs are duplicated.
- [ ] Back up and regenerate Anvil's duplicated `/etc/machine-id`.
- [ ] Reboot Anvil and confirm Forge/Anvil machine IDs differ.
- [x] Record DGX OS/Spark software versions (7.2.3 base, 7.5.0 OTA).
- [ ] Record firmware versions relevant to CX-7 and GB10.
- [x] Confirm both clocks report NTP synchronization and America/Los_Angeles.
- [x] Capture an initial idle thermal/power sample on each node.

## 3. Direct 200GbE fabric

- [x] Detect Forge's active port: `enp1s0f0np0` / `rocep1s0f0`.
- [x] Detect Anvil's active port: `enp1s0f1np1` / `rocep1s0f1`.
- [x] Add node-specific NIC/HCA settings; do not assume matching port names.
- [ ] Run Forge fabric setup with sudo (`10.100.10.1/24`).
- [ ] Run Anvil fabric setup with sudo (`10.100.10.2/24`).
- [ ] Confirm `/etc/netplan/40-dual-spark.yaml` permissions are `600`.
- [ ] Confirm normal LAN interfaces and default routes remain unchanged.
- [ ] Confirm bidirectional ICMP over `10.100.10.1` / `10.100.10.2`.
- [ ] Confirm RoCE v2 GID index `3` appears after IPv4 assignment on Forge.
- [ ] Confirm RoCE v2 GID index `3` appears after IPv4 assignment on Anvil.
- [ ] Verify passwordless Forge-to-Anvil SSH over `10.100.10.2`.
- [ ] Benchmark TCP bandwidth with `iperf3` in both directions.
- [ ] Benchmark multiple streams and record CPU utilization.
- [ ] Validate RDMA with `ib_write_bw` or an equivalent perftest.
- [ ] Record negotiated link speed, MTU, and active port state.
- [ ] Decide whether jumbo MTU improves measured throughput before enabling it.
- [ ] Run an NCCL all-reduce sanity/performance test over the selected HCA.
- [ ] Capture `NCCL_DEBUG=INFO` evidence that traffic uses CX-7, not LAN/Tailscale.
- [ ] Document netplan rollback and test it without applying it permanently.

## 4. Tailscale management plane

- [ ] Install Tailscale on Forge from the official Noble repository.
- [ ] Install Tailscale on Anvil from the official Noble repository.
- [ ] Authenticate Forge into the existing tailnet.
- [ ] Authenticate Anvil into the existing tailnet.
- [ ] Confirm MagicDNS names are unique and stable.
- [ ] Confirm Windows can `tailscale ping` both Sparks.
- [ ] Confirm SSH key authentication works over each Tailscale address.
- [ ] Keep NCCL and model transfer off Tailscale.
- [ ] Review tailnet ACLs so the vLLM API is not unintentionally exposed.
- [ ] Record Tailscale IPs without committing reusable auth keys.

## 5. Gated model acquisition and replication

- [x] Confirm the v1.1 repository is gated (`gated=auto`).
- [x] Confirm the snapshot contains 48 safetensor shards.
- [x] Estimate the complete snapshot at about 155.44 GiB.
- [x] Configure Forge as the only Hugging Face download node.
- [x] Add shard-index verification before and after transfer.
- [x] Add resumable `rsync --partial` transfer over the direct fabric.
- [ ] Accept the model's Hugging Face gate with the intended account.
- [ ] Authenticate the Forge-only HF CLI environment.
- [x] Pin the resolved model commit SHA in `.env.example`.
- [ ] Download the complete v1.1 snapshot on Forge.
- [ ] Verify all 48 shards and record total bytes on Forge.
- [ ] Transfer the snapshot once from Forge to Anvil via `10.100.10.2`.
- [ ] Verify all 48 shards and total bytes on Anvil.
- [x] Add a deterministic SHA-256 manifest check across both model copies.
- [ ] Run the SHA-256 manifest check successfully on the downloaded copies.
- [ ] Confirm no full model download occurred independently on Anvil.
- [ ] Record transfer elapsed time and effective GiB/s.
- [ ] Confirm at least 500 GiB free space remains on both nodes.

## 6. Runtime preparation

- [x] Vendor and verify Tony-derived overlay sources.
- [x] Add a `fast` profile using `fp8`, C1, and 900K context.
- [x] Add an `agent` profile using stage-c, `nvfp4_ds_mla`, C4, and 1M context.
- [x] Keep unsupported KV-cache modes out of the Tony-derived image.
- [x] Build/pull the runtime only on Forge and stream it to Anvil.
- [x] Validate Compose rendering for both profiles on Forge.
- [ ] Build the `fast` image on Forge.
- [ ] Record the fast image ID, digest, and base-image digest.
- [ ] Stream and load the fast image on Anvil.
- [ ] Verify DSpark imports inside the fast image on both nodes.
- [ ] Pull/tag the drowzeys stage-c image on Forge.
- [ ] Record the agent image ID and digest.
- [ ] Stream and load the agent image on Anvil.
- [ ] Verify DSpark imports inside the agent image on both nodes.
- [ ] Confirm both nodes report identical image IDs for each profile.

## 7. Cluster launch validation

- [x] Implement worker-first launch.
- [x] Implement head-first shutdown.
- [x] Keep the API loopback-only by default.
- [x] Mount local verified weights read-only at `/model`.
- [x] Add node-specific HCA, interface, GID, and host-IP injection.
- [ ] Run `scripts/preflight.sh` successfully.
- [ ] Confirm no stale vLLM/DSpark containers or GPU processes.
- [ ] Launch Anvil rank 1 and verify it waits cleanly.
- [ ] Launch Forge rank 0 and wait for model initialization.
- [ ] Confirm `/v1/models` returns the configured served model.
- [ ] Run a minimal deterministic chat completion.
- [ ] Verify tool parser and reasoning parser startup flags.
- [ ] Confirm thinking defaults to false for agent-oriented use.
- [ ] Inspect logs for TCP fallback, GID, memory, CUDA graph, and NCCL warnings.
- [ ] Confirm the endpoint remains bound to `127.0.0.1:8888`.
- [ ] Test a Windows SSH tunnel to the loopback API.
- [ ] Perform a clean stop/start cycle for each profile.
- [ ] Verify restart does not redownload weights or images.

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
- [ ] Add a fixed warmup policy that does not pollute measured runs.
- [ ] Decide output length (256 versus 1,024) and document the rationale.
- [ ] Ensure benchmark prompts/results contain no private data.

## 9. Fast-profile benchmark matrix

- [ ] Fast C1: 10K prompt, three stable runs.
- [ ] Fast C1: 200K prompt, three stable runs.
- [ ] Fast C1: 300K prompt, three stable runs.
- [ ] Record TTFT, prompt throughput, decode tok/s, acceptance, and wall time.
- [ ] Confirm the 900K configured context accepts all three fixtures.
- [ ] Test 512-token and 1,024-token output lengths if thermally stable.
- [ ] Compare MTP speculative token counts 3, 4, 5, and 6.
- [ ] Compare GPU memory utilization 0.80 and 0.82 without unsafe pressure.
- [ ] Measure cold start and warm restart separately.
- [ ] Run a sustained thermal-soak benchmark.

## 10. Agent-profile benchmark matrix

- [ ] Agent C1: 10K prompt, three stable runs.
- [ ] Agent C1: 200K prompt, three stable runs.
- [ ] Agent C1: 300K prompt, three stable runs.
- [ ] Agent C4: 10K prompt, three groups.
- [ ] Agent C4: 200K prompt, three groups.
- [ ] Agent C4: 300K prompt only after confirming KV capacity and stability.
- [ ] Record per-request TTFT distribution and aggregate tok/s.
- [ ] Confirm the 1M configured context accepts all three fixtures.
- [ ] Exercise Hermes/tool calling without publishing unsafe prompt content.
- [ ] Check for skill-catalog spill and protocol leakage.
- [ ] Validate `max_tokens=8192` operational guidance separately from speed tests.

## 11. Comparison and optimization decisions

- [x] Add a deterministic Markdown/SVG benchmark report generator.
- [ ] Render the final chart from measured fast and agent results.
- [ ] Compare fast versus agent at identical C1 prompts and output lengths.
- [ ] Separate prefill, decode, and end-to-end conclusions.
- [ ] Compare draft acceptance and accepted tokens per draft step.
- [ ] Confirm any tok/s gain is repeatable and outside run-to-run variance.
- [ ] Reject configurations that silently reduce usable context.
- [ ] Reject configurations that route traffic over LAN instead of CX-7.
- [ ] Reject configurations that corrupt tool calling or produce garble.
- [ ] Pick a default profile based on measured workload goals.
- [ ] Keep the non-default profile documented and reproducible.
- [ ] Document which techniques transferred cleanly and which did not.

## 12. Documentation and release

- [x] Explain that hostnames do not need to match.
- [x] Explain that only the username must match.
- [x] Explain one-download model replication.
- [x] Explain Tailscale versus CX-7 responsibilities.
- [x] Warn that upstream performance is not a local measurement.
- [ ] Add actual fabric validation output to docs.
- [x] Add a tracked benchmark-table and chart location with an honest pending state.
- [ ] Replace the pending table/chart with measured data and reviewed raw-result provenance.
- [ ] Add tested image/model revision matrix.
- [ ] Add troubleshooting for gated HF access.
- [ ] Add troubleshooting for GID-index and NCCL fallback failures.
- [ ] Add troubleshooting for model OOM and KV-pool sizing.
- [ ] Add recovery instructions for interrupted model/image transfers.
- [ ] Add security guidance for remote API consumers.
- [ ] Run a fresh-agent dry run using only README and `AGENTS.md`.
- [ ] Review all claims against raw artifacts.
- [ ] Push and create the first measured release after local results are reviewed.
