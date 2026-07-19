# Pinned upstream versions

Verified on 2026-07-19. Update deliberately and rerun the full validation and
benchmark matrix whenever one of these revisions changes.

| Component | Revision |
| --- | --- |
| Tony Deangelo fast recipe | `51261f419a4a35a02966405ea9774b41735ec412` |
| drowzeys / keys recipe and docs | `1a86aa2bc7af0b8afa5615921f06f18fb71ce75e` |
| drowzeys v1.1 Hugging Face snapshot | `14c06b6db367b20a8cbe13f28b1f767b1e983307` |
| NVIDIA DGX Spark playbooks | `eda75a64a4fb9d909a59ce34ac94bb365864bce4` |
| Tony fast base image resolved digest | `ghcr.io/bjk110/vllm-spark@sha256:d8492e7677cf1b9aaa3344e0e6865efc468454013eee5ebabac85be90af027be` |
| drowzeys stage-c image digest | `ghcr.io/drowzeys/vllm-dspark-nvfp4-stage-c@sha256:f3b0577bfec41ac2cece2cbe0c4a9be934d9d4f18c50bbcdd602848da2499fb8` |

At this verification point, the overlay is based on Tony's pinned commit. Three
files also carry the ragged-batch/stable-KV-slot concurrency changes from the
pinned drowzeys stage-c image; see `THIRD_PARTY_NOTICES.md`. The original
measured fast image ID was
`sha256:131a0df01260cdeb2292edbe2b1836e5f459b36bfe237197ddff64a9d5758947`;
the measured Tony+C4 image ID was
`sha256:830c4f7c30f57ac8692676a502087c8589ef4228580b195be76656141470f799`;
the final C1-preserving combined overlay image ID was
`sha256:e8df377b28db3bde399d0829ff35cb59ffee6071a953d8ab3b425da65546c4f5`;
the measured live-batch adaptive overlay image ID was
`sha256:1e7f77755b53dd713b192dcacb9d60df680bbcbf68932c1e82bc3d35d6295ffb`;
the measured stage-c image ID was
`sha256:76532c4cc261afe7a7cad1d9731cd5123d0e14219c9a1d35a0ef6163fe67c5d4`.
The resolved registry digests above make the mutable tags auditable.
