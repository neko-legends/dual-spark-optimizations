# Pinned upstream versions

Verified on 2026-07-19. Update deliberately and rerun the full validation and
benchmark matrix whenever one of these revisions changes.

| Component | Revision |
| --- | --- |
| Tony Deangelo fast recipe | `51261f419a4a35a02966405ea9774b41735ec412` |
| drowzeys / keys recipe and docs | `1a86aa2bc7af0b8afa5615921f06f18fb71ce75e` |
| drowzeys v1.1 Hugging Face snapshot | `14c06b6db367b20a8cbe13f28b1f767b1e983307` |
| NVIDIA DGX Spark playbooks | `eda75a64a4fb9d909a59ce34ac94bb365864bce4` |

At this verification point, `recipe/` and
`scripts/verify-overlay-sources.sh` are byte-for-byte matches for Tony's
pinned commit. Runtime container digests must be recorded after the first
successful pull/build because tags are mutable.
