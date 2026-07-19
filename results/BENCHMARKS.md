# Measured benchmarks

These are local measurements from this repository's harness, not upstream claims.
Each case uses a 256-token output cap. C1 contains three sequential requests;
C4 contains three groups of four simultaneous requests (12 total). Repeated
identical prompts can benefit from the runtime's observed prefix caching, so
TTFT combines the first full prefill with subsequent cache-assisted requests.
Decode tok/s is the per-request mean; aggregate tok/s is the group throughput.

| Profile | Prompt | C | Requests | Decode tok/s | Aggregate tok/s | Mean TTFT (s) | Model revision | Source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `adaptive` | 10K | 1 | 3 | 34.54 | 33.30 | 0.30 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`adaptive/20260719T193858Z/book-context-10k-c1.json`](raw/adaptive/20260719T193858Z/book-context-10k-c1.json) |
| `adaptive` | 200K | 1 | 3 | 47.87 | 30.09 | 33.92 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`adaptive/20260719T193858Z/book-context-200k-c1.json`](raw/adaptive/20260719T193858Z/book-context-200k-c1.json) |
| `adaptive` | 300K | 1 | 3 | 55.32 | 32.60 | 22.17 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`adaptive/20260719T193858Z/book-context-300k-c1.json`](raw/adaptive/20260719T193858Z/book-context-300k-c1.json) |
| `adaptive` | 10K | 4 | 12 | 21.26 | 75.44 | 0.54 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`adaptive/20260719T193858Z/book-context-10k-c4.json`](raw/adaptive/20260719T193858Z/book-context-10k-c4.json) |
| `adaptive` | 200K | 4 | 12 | 31.10 | 83.24 | 3.76 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`adaptive/20260719T193858Z/book-context-200k-c4.json`](raw/adaptive/20260719T193858Z/book-context-200k-c4.json) |
| `adaptive` | 300K | 4 | 12 | 34.04 | 87.10 | 3.11 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`adaptive/20260719T193858Z/book-context-300k-c4.json`](raw/adaptive/20260719T193858Z/book-context-300k-c4.json) |
| `fast` | 10K | 1 | 3 | 35.64 | 29.76 | 2.03 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast/20260719T190448Z/book-context-10k-c1.json`](raw/fast/20260719T190448Z/book-context-10k-c1.json) |
| `fast` | 200K | 1 | 3 | 52.47 | 33.93 | 33.13 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast/20260719T190448Z/book-context-200k-c1.json`](raw/fast/20260719T190448Z/book-context-200k-c1.json) |
| `fast` | 300K | 1 | 3 | 56.21 | 33.14 | 21.84 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast/20260719T190448Z/book-context-300k-c1.json`](raw/fast/20260719T190448Z/book-context-300k-c1.json) |
| `fast-c4` | 10K | 1 | 3 | 35.20 | 33.75 | 0.34 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast-c4/20260719T184424Z/book-context-10k-c1.json`](raw/fast-c4/20260719T184424Z/book-context-10k-c1.json) |
| `fast-c4` | 200K | 1 | 3 | 36.20 | 22.45 | 33.51 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast-c4/20260719T184424Z/book-context-200k-c1.json`](raw/fast-c4/20260719T184424Z/book-context-200k-c1.json) |
| `fast-c4` | 300K | 1 | 3 | 51.59 | 30.70 | 22.02 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast-c4/20260719T184424Z/book-context-300k-c1.json`](raw/fast-c4/20260719T184424Z/book-context-300k-c1.json) |
| `fast-c4` | 10K | 4 | 12 | 20.10 | 69.40 | 1.43 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast-c4/20260719T184424Z/book-context-10k-c4.json`](raw/fast-c4/20260719T184424Z/book-context-10k-c4.json) |
| `fast-c4` | 200K | 4 | 12 | 19.64 | 63.31 | 2.47 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast-c4/20260719T184424Z/book-context-200k-c4.json`](raw/fast-c4/20260719T184424Z/book-context-200k-c4.json) |
| `fast-c4` | 300K | 4 | 12 | 32.59 | 79.67 | 3.58 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`fast-c4/20260719T184424Z/book-context-300k-c4.json`](raw/fast-c4/20260719T184424Z/book-context-300k-c4.json) |
| `long-c4` | 10K | 1 | 3 | 35.30 | 33.78 | 0.34 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`long-c4/20260719T174232Z/book-context-10k-c1.json`](raw/long-c4/20260719T174232Z/book-context-10k-c1.json) |
| `long-c4` | 200K | 1 | 3 | 36.94 | 22.94 | 34.06 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`long-c4/20260719T174232Z/book-context-200k-c1.json`](raw/long-c4/20260719T174232Z/book-context-200k-c1.json) |
| `long-c4` | 300K | 1 | 3 | 53.77 | 31.50 | 22.00 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`long-c4/20260719T174232Z/book-context-300k-c1.json`](raw/long-c4/20260719T174232Z/book-context-300k-c1.json) |
| `long-c4` | 10K | 4 | 12 | 19.39 | 60.10 | 3.87 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`long-c4/20260719T174232Z/book-context-10k-c4.json`](raw/long-c4/20260719T174232Z/book-context-10k-c4.json) |
| `long-c4` | 200K | 4 | 12 | 22.46 | 64.70 | 2.83 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`long-c4/20260719T174232Z/book-context-200k-c4.json`](raw/long-c4/20260719T174232Z/book-context-200k-c4.json) |
| `long-c4` | 300K | 4 | 12 | 34.57 | 82.37 | 3.67 | `14c06b6db367b20a8cbe13f28b1f767b1e983307` | [`long-c4/20260719T174232Z/book-context-300k-c4.json`](raw/long-c4/20260719T174232Z/book-context-300k-c4.json) |

Generated: 2026-07-19T19:51:43+00:00
