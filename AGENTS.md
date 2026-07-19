# Instructions for AI agents

## Mission

Maintain a reproducible two-DGX-Spark deployment that combines drowzeys v1.1
weights with two explicitly separate runtime profiles. Never claim that the
hybrid reaches an upstream tok/s figure until it has been measured here.

## Fixed deployment facts

- Forge is rank 0, download node, and API head: `10.100.10.1` on
  `enp1s0f0np0` / `rocep1s0f0`.
- Anvil is rank 1: `10.100.10.2` on `enp1s0f1np1` / `rocep1s0f1`.
- Both Linux accounts are `jun`. Hostnames must remain distinct.
- Download gated weights only on Forge. Replicate to Anvil with `rsync` over
  the direct fabric. Never download the full model independently on both nodes.
- Tailscale is management-only. NCCL and bulk transfer use the CX-7 addresses.

## Safety and secrets

- Never commit `.env`, HF tokens, private SSH keys, model weights, or generated
  benchmark data containing prompts.
- Commit only reviewed benchmark summaries and generated charts. Keep raw
  captures under the ignored `benchmark-results/` tree.
- Keep the API bound to `127.0.0.1` by default. Document authentication and
  firewalling before changing it to `0.0.0.0`.
- Do not delete or overwrite netplan files. `setup-fabric.sh` may only manage
  `/etc/netplan/40-dual-spark.yaml` and must back it up first.
- Do not mix v1.0 and v1.1 model shards. Verify the safetensor index after every
  transfer.
- Preserve upstream license headers and `THIRD_PARTY_NOTICES.md` when updating
  vendored overlay files.

## Change workflow

1. Read `.env.example`, both profile files, and the relevant upstream source.
2. Run `scripts/preflight.sh` before cluster operations.
3. Validate shell with `bash -n scripts/*.sh` and ShellCheck when available.
4. Validate Compose for both profiles before launch.
5. Start rank 1 before rank 0; stop rank 0 before rank 1.
6. Benchmark a runtime/configuration change against the unchanged profile and
   record image digest, model revision, prompt/output lengths, context, and
   concurrency.
7. Distinguish measured local results from upstream reference results in docs.
8. After completing a benchmark matrix, run
   `python3 scripts/render-benchmark-report.py`, review the generated table and
   SVG, and update README claims from those artifacts only.
9. Run `python3 scripts/check-repository-artifacts.py` before every commit.
10. Treat `TODO.md` as the resumable execution ledger and update checkboxes only
   when supporting evidence exists.

## Profile boundaries

- `fast` uses the Tony-derived overlay and `fp8`, one sequence, 900K context.
- `agent` uses drowzeys stage-c and `nvfp4_ds_mla`, four sequences, 1M context.
- Do not set `nvfp4_ds_mla` on the Tony-derived image unless a source audit and
  runtime test prove support.
