# Instructions for AI agents

## Mission

Maintain a reproducible two-DGX-Spark deployment that combines drowzeys'
uncensored v1.1 weights with Tony-derived runtime optimizations. Never claim
that a configuration reaches an upstream tok/s figure until measured here.

## Deployment invariants

- Rank 0 is the download/API head; rank 1 is the worker. Hostnames remain
  distinct and deployment-specific values belong only in the ignored `.env`.
- Use the same Linux account on both nodes.
- Download gated weights only on the head. Replicate to the worker with `rsync` over
  the direct fabric. Never download the full model independently on both nodes.
- Tailscale is management-only. NCCL and bulk transfer use the CX-7 addresses.

## Safety and secrets

- Never commit `.env`, HF tokens, private SSH keys, model weights, or generated
  benchmark data containing prompts.
- Commit only reviewed, privacy-scrubbed benchmark evidence and generated
  charts. Keep unsanitized captures under the ignored `benchmark-results/` tree.
- Keep the API bound to `127.0.0.1` by default. Document authentication and
  firewalling before changing it to `0.0.0.0`.
- Do not delete or overwrite netplan files. `setup-fabric.sh` may only manage
  `/etc/netplan/40-dual-spark.yaml` and must back it up first.
- Do not mix v1.0 and v1.1 model shards. Verify the safetensor index after every
  transfer.
- Preserve upstream license headers and `THIRD_PARTY_NOTICES.md` when updating
  vendored overlay files.

## Change workflow

1. Read `.env.example`, all profile files, and the relevant upstream source.
2. Run `scripts/preflight.sh` before cluster operations.
3. Validate shell with `bash -n scripts/*.sh` and ShellCheck when available.
4. Validate Compose for every profile before launch.
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

## Profile decisions

- All profiles use the same uncensored v1.1 weights, tool parser, and reasoning
  parser. A profile name does not change the model's agent behavior.
- `adaptive` is the measured general-purpose default. It selects the original
  Tony row-zero draft path for a lone live request and stable-slot/ragged-batch
  handling when requests overlap; clients need no special behavior.
- `fast` is the C1 specialist. Use it only when accepting no concurrent work is
  worth its measured 1.6–8.8% C1 advantage over `adaptive`.
- `long-c4` is drowzeys stage-c. It remains useful for the full 1M
  configuration, not as the measured default or a claim about agent ability.
- Do not set `nvfp4_ds_mla` on the Tony-derived image unless a source audit and
  runtime test prove support.
