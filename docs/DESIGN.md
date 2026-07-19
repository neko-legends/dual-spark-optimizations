# Hybrid design rationale

## What can be combined

The v1.1 checkpoint has the same DeepSeek V4 Flash DSpark architecture as the
stock checkpoint used by Tony's recipe. Weight choice and most serving/runtime
choices are therefore orthogonal. The experimental `fast` profile combines:

- drowzeys v1.1 main-model edits with stock MTP heads;
- Tony's vendored DSpark/vLLM overlay;
- DSpark speculative decoding with five draft tokens;
- B12X MoE and WO-projection paths;
- one request owning the fp8 KV pool;
- worker-first TP=2 launch over direct RoCE.

Stock MTP heads make v1.1 a plausible fit for speculative decoding, but that is
a hypothesis until draft acceptance and tok/s are measured on the combined
system.

## What must remain separate

Tony's pinned overlay advertises `fp8` / `fp8_ds_mla`; it does not advertise
`nvfp4_ds_mla`. Drowzeys' stage-c image supplies the latter. Consequently:

- `fast` uses the Tony-derived image, `fp8`, C1, and 900K;
- `agent` uses drowzeys stage-c, `nvfp4_ds_mla`, C4, and 1M.

Putting `nvfp4_ds_mla` into the Tony-derived image without a source audit would
be configuration theater, not an optimization. The repository prevents that
by keeping image and KV-cache choices together in profile files.

## Why one download and two local copies

Tensor parallel ranks need low-latency access to their local weight shards.
Serving a 155 GiB model over a network filesystem introduces an avoidable
runtime dependency. Forge therefore downloads the pinned gated snapshot once,
verifies it, and copies it to Anvil over the 200GbE link. Both ranks then mount
their local verified tree read-only.

The runtime image follows the same principle: build or pull once on Forge,
then stream `docker save` into `docker load` on Anvil.

## Network separation

- CX-7 (`10.100.10.0/24`): NCCL, Gloo/TP sockets, model and image transfer.
- LAN: initial bootstrap and fallback management.
- Tailscale: encrypted remote management only.

Explicit per-node interface/HCA fields are necessary because the cable is in
Forge's port 0 and Anvil's port 1. Requiring identical interface names would be
both unnecessary and incorrect for this physical layout.

## Benchmark decision rule

No single number decides the default. Compare at identical prompt/output
shapes and record:

- prompt tokens and time to first token;
- decode and end-to-end tok/s;
- draft acceptance and accepted tokens per draft;
- aggregate throughput and per-request latency at C4;
- thermal/power stability;
- usable context, protocol/tool behavior, and output quality.

The fastest profile wins only for workloads where its context, concurrency,
and agent-behavior tradeoffs are acceptable.
