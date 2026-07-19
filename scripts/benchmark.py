#!/usr/bin/env python3
"""Streaming long-context benchmark for an OpenAI-compatible chat endpoint."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import statistics
import time
import urllib.request
from pathlib import Path
from typing import Any


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def stream_request(url: str, model: str, prompt: str, max_tokens: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    first_token_at: float | None = None
    last_token_at: float | None = None
    usage: dict[str, int] = {}
    text_fragments = 0

    with urllib.request.urlopen(request, timeout=3600) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            if chunk.get("usage"):
                usage = chunk["usage"]
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            fragment = delta.get("content") or delta.get("reasoning_content") or ""
            if fragment:
                now = time.perf_counter()
                first_token_at = first_token_at or now
                last_token_at = now
                text_fragments += 1

    finished = time.perf_counter()
    prompt_tokens = int(usage.get("prompt_tokens", 0))
    completion_tokens = int(usage.get("completion_tokens", 0))
    ttft = (first_token_at - started) if first_token_at is not None else finished - started
    decode_seconds = (
        last_token_at - first_token_at
        if first_token_at is not None and last_token_at is not None
        else 0.0
    )
    decode_tokens = max(completion_tokens - 1, 0)
    return {
        "wall_seconds": finished - started,
        "ttft_seconds": ttft,
        "decode_seconds": decode_seconds,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "decode_tokens_per_second": decode_tokens / decode_seconds if decode_seconds else 0.0,
        "end_to_end_tokens_per_second": completion_tokens / (finished - started),
        "stream_fragments": text_fragments,
    }


def run_group(args: argparse.Namespace, prompt: str, group: int) -> dict[str, Any]:
    group_started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(stream_request, args.url, args.model, prompt, args.max_tokens)
            for _ in range(args.concurrency)
        ]
        requests = [future.result() for future in futures]
    group_seconds = time.perf_counter() - group_started
    completion_total = sum(row["completion_tokens"] for row in requests)
    return {
        "group": group,
        "concurrency": args.concurrency,
        "group_wall_seconds": group_seconds,
        "aggregate_completion_tokens": completion_total,
        "aggregate_completion_tokens_per_second": completion_total / group_seconds,
        "requests": requests,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8888/v1/chat/completions")
    parser.add_argument("--model", default="deepseek-v4-flash-dspark-v1.1-abliterated")
    parser.add_argument("--model-revision", default="unknown")
    parser.add_argument("--profile", default="adaptive")
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=1, help="sequential groups")
    parser.add_argument("--concurrency", type=int, default=1, help="requests per group")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.runs < 1 or args.concurrency < 1 or args.max_tokens < 1:
        parser.error("runs, concurrency, and max-tokens must be positive")

    prompt_bytes = args.prompt_file.read_bytes()
    prompt = prompt_bytes.decode("utf-8")
    groups = []
    for group_number in range(1, args.runs + 1):
        result = run_group(args, prompt, group_number)
        groups.append(result)
        print(json.dumps(result), flush=True)

    requests = [request for group in groups for request in group["requests"]]
    report = {
        "schema_version": 1,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": args.url,
        "model": args.model,
        "model_revision": args.model_revision,
        "profile": args.profile,
        "prompt": {
            "path": str(args.prompt_file),
            "bytes": len(prompt_bytes),
            "characters": len(prompt),
            "sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        },
        "configuration": {
            "runs": args.runs,
            "concurrency": args.concurrency,
            "max_tokens": args.max_tokens,
            "temperature": 0.0,
            "stream": True,
        },
        "summary": {
            "request_count": len(requests),
            "mean_prompt_tokens": statistics.mean(row["prompt_tokens"] for row in requests),
            "mean_ttft_seconds": statistics.mean(row["ttft_seconds"] for row in requests),
            "p50_ttft_seconds": percentile([row["ttft_seconds"] for row in requests], 0.50),
            "p95_ttft_seconds": percentile([row["ttft_seconds"] for row in requests], 0.95),
            "mean_decode_tokens_per_second": statistics.mean(
                row["decode_tokens_per_second"] for row in requests
            ),
            "mean_group_aggregate_tokens_per_second": statistics.mean(
                group["aggregate_completion_tokens_per_second"] for group in groups
            ),
        },
        "groups": groups,
    }
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
