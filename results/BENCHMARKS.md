# Measured benchmarks

These are local measurements from this repository's harness, not upstream claims.
Each case uses a 256-token output cap. C1 contains three sequential requests;
C4 contains three groups of four simultaneous requests (12 total). Repeated
identical prompts can benefit from the runtime's observed prefix caching, so
TTFT combines the first full prefill with subsequent cache-assisted requests.
Decode tok/s is the per-request mean; aggregate tok/s is the group throughput.

| Profile | Prompt | C | Requests | Decode tok/s | Aggregate tok/s | Mean TTFT (s) | Model revision | Source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `fast` | 10K | 1 | 3 | 36.79 | 30.86 | 2.26 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast/20260719T172757Z/book-context-10k-c1.json`](raw/fast/20260719T172757Z/book-context-10k-c1.json) |
| `fast` | 200K | 1 | 3 | 49.88 | 24.52 | 35.50 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast/20260719T172757Z/book-context-200k-c1.json`](raw/fast/20260719T172757Z/book-context-200k-c1.json) |
| `fast` | 300K | 1 | 3 | 57.29 | 31.07 | 22.26 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast/20260719T172757Z/book-context-300k-c1.json`](raw/fast/20260719T172757Z/book-context-300k-c1.json) |
| `agent` | 10K | 1 | 3 | 35.30 | 33.78 | 0.34 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`agent/20260719T174232Z/book-context-10k-c1.json`](raw/agent/20260719T174232Z/book-context-10k-c1.json) |
| `agent` | 200K | 1 | 3 | 36.94 | 22.94 | 34.06 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`agent/20260719T174232Z/book-context-200k-c1.json`](raw/agent/20260719T174232Z/book-context-200k-c1.json) |
| `agent` | 300K | 1 | 3 | 53.77 | 31.50 | 22.00 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`agent/20260719T174232Z/book-context-300k-c1.json`](raw/agent/20260719T174232Z/book-context-300k-c1.json) |
| `agent` | 10K | 4 | 12 | 19.39 | 60.10 | 3.87 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`agent/20260719T174232Z/book-context-10k-c4.json`](raw/agent/20260719T174232Z/book-context-10k-c4.json) |
| `agent` | 200K | 4 | 12 | 22.46 | 64.70 | 2.83 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`agent/20260719T174232Z/book-context-200k-c4.json`](raw/agent/20260719T174232Z/book-context-200k-c4.json) |
| `agent` | 300K | 4 | 12 | 34.57 | 82.37 | 3.67 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`agent/20260719T174232Z/book-context-300k-c4.json`](raw/agent/20260719T174232Z/book-context-300k-c4.json) |

Generated: 2026-07-19T17:54:58+00:00
