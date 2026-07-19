# Hybrid design rationale

## What can be combined

The v1.1 checkpoint has the same DeepSeek V4 Flash DSpark architecture as the
stock checkpoint used by Tony's recipe. Weight choice and most serving/runtime
choices are therefore orthogonal. The measured `fast` profile combines:

- drowzeys v1.1 main-model edits with stock MTP heads;
- Tony's vendored DSpark/vLLM overlay;
- DSpark speculative decoding with five draft tokens;
- B12X MoE and WO-projection paths;
- one request owning the fp8 KV pool;
- worker-first TP=2 launch over direct RoCE.

The tracked speculative-decoding metrics and throughput results confirm that
the v1.1 checkpoint runs with this combined DSpark path.

## What must remain separate

Tony's pinned overlay advertises `fp8` / `fp8_ds_mla`; it does not advertise
`nvfp4_ds_mla`. Drowzeys' stage-c image supplies the latter. Consequently:

- `fast` uses the Tony-derived image, `fp8`, C1, and 900K;
- `adaptive` adds drowzeys' ragged-batch and stable-KV-slot concurrency changes
  while preserving Tony's original row-zero path whenever the live batch is a
  single request; `fast-c4` is a compatibility alias;
- `long-c4` is drowzeys stage-c with `nvfp4_ds_mla`, C4, and 1M context.

Putting `nvfp4_ds_mla` into the Tony-derived image without a source audit would
be configuration theater, not an optimization. The repository prevents that
by keeping image and KV-cache choices together in profile files.

## Why one download and two local copies

Tensor parallel ranks need low-latency access to their local weight shards.
Serving a 155 GiB model over a network filesystem introduces an avoidable
runtime dependency. The head therefore downloads the pinned gated snapshot once,
verifies it, and copies it to the worker over the 200GbE link. Both ranks then mount
their local verified tree read-only.

The runtime image follows the same principle: build or pull once on the head,
then stream `docker save` into `docker load` on the worker.

## Network separation

- CX-7 (`10.100.10.0/24`): NCCL, Gloo/TP sockets, model and image transfer.
- LAN: initial bootstrap and fallback management.
- Tailscale: encrypted remote management only.

Explicit per-node interface/HCA fields are necessary because active port names
can differ between systems. Discover them locally and keep them in `.env`.

## Benchmark decision rule

No single number decides the default. Compare at identical prompt/output
shapes and record:

- prompt tokens and time to first token;
- decode and end-to-end tok/s;
- draft acceptance and accepted tokens per draft;
- aggregate throughput and per-request latency at C4;
- thermal/power stability;
- usable context, protocol/tool behavior, and output quality.

The measurements select `adaptive` as the general-purpose default: it remained
within 1.6–8.8% of `fast` at C1 and produced the highest C4 aggregate throughput
at 10K, 200K, and 300K. `fast` remains the single-request specialist, while
`long-c4` remains for the full 1M stage-c configuration. Tool/agent behavior is
shared; the profiles change runtime, cache, concurrency, and context capacity.
