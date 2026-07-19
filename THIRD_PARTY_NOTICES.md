# Third-party notices

This project combines and adapts public work; it does not claim the upstream
benchmark results as its own.

## Runtime overlay and fast profile

The files under `recipe/overlay/`, `recipe/Dockerfile.dspark-runtime-overlay`,
and the overlay verification approach are derived from Tony Deangelo's
[`tonyd2wild/DeepSeek-v4-Flash-DSpark-60-tok-s-900K-ctx-2x-DGX-Spark`](https://github.com/tonyd2wild/DeepSeek-v4-Flash-DSpark-60-tok-s-900K-ctx-2x-DGX-Spark),
which is MIT licensed. Its license is preserved at
`third_party/LICENSE-tonyd2wild`. The vendored vLLM source files retain their
upstream Apache-2.0 notices where present.

Tony's recipe credits:

- Rafael Caricio's DSpark vLLM integration and deployment work:
  [`rafaelcaricio/vllm#1`](https://github.com/rafaelcaricio/vllm/pull/1) and
  [`rafaelcaricio/spark_vllm_docker#1`](https://github.com/rafaelcaricio/spark_vllm_docker/pull/1)
- MiaAI-Lab's two-node packaging and worker-first launch pattern:
  [`MiaAI-Lab/DeepSeek-v4-Flash-DSpark-2x-DGX-Spark`](https://github.com/MiaAI-Lab/DeepSeek-v4-Flash-DSpark-2x-DGX-Spark)

## v1.1 model and reference profile

The model selection, stage-c runtime profile, `nvfp4_ds_mla` configuration,
and v1.1 operational guidance come from drowzeys / keys:

- [`drowzeys/DeepSeek-V4-Flash-DSpark-Abliterated-Uncensored-1M-57toks`](https://github.com/drowzeys/DeepSeek-V4-Flash-DSpark-Abliterated-Uncensored-1M-57toks)
- [`drowzeys/DeepSeek-V4-Flash-DSpark-Abliterated-Uncensored-v1.1-alpha-Mida-Brikie`](https://huggingface.co/drowzeys/DeepSeek-V4-Flash-DSpark-Abliterated-Uncensored-v1.1-alpha-Mida-Brikie)

Their software license is preserved at `third_party/LICENSE-drowzeys`. The
weights are a separate gated artifact and retain the original model terms.

## Hardware networking and remote access

The fabric and Tailscale setup scripts follow NVIDIA's DGX Spark playbooks:

- [Connect Two Sparks](https://github.com/NVIDIA/dgx-spark-playbooks/tree/main/nvidia/connect-two-sparks)
- [Set up Tailscale on Your Spark](https://build.nvidia.com/spark/tailscale)
