# Long-context prompt fixtures

These deterministic fixtures are copied from
[`neko-legends/nvidia-local-llm-profiles`](https://github.com/neko-legends/nvidia-local-llm-profiles/tree/main/benchmarks/prompts)
so results remain comparable with the owner's other local-model work.

| file | target prompt tokens | characters | SHA-256 |
| --- | ---: | ---: | --- |
| `book-context-10k.txt` | 10,000 | 42,940 | `785c5b31d1ce77612431b1289c0a097ed51ab1a6d4a07bccfb7a70f59df55f94` |
| `book-context-200k.txt` | 200,000 | 840,403 | `a794ca243983eb3387bec6728db4b0c72a99ee2a98cfee7223269708e4ae228c` |
| `book-context-300k.txt` | 300,000 | 1,260,986 | `5e3a5f9c15da85d938993ef0c80153d26ba405a13689447fd7082d23355ca4ba` |

The target is based on the fixture generator's estimate. Always report the
server-returned `usage.prompt_tokens`, because tokenization differs by model.
