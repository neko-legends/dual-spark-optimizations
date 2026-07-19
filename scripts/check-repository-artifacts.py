#!/usr/bin/env python3
"""Fail when tracked files look like model weights, secrets, or large artifacts."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_TRACKED_BYTES = 25 * 1024 * 1024
BLOCKED_SUFFIXES = {".safetensors", ".gguf", ".ckpt", ".onnx", ".pt", ".pth"}
SECRET_PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----"),
    "Hugging Face token": re.compile(rb"\bhf_[A-Za-z0-9]{20,}\b"),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT, stderr=subprocess.DEVNULL
    )
    return [ROOT / item.decode("utf-8") for item in output.split(b"\0") if item]


def violations(paths: list[Path]) -> list[str]:
    problems: list[str] = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        lower_name = path.name.lower()
        if path.suffix.lower() in BLOCKED_SUFFIXES or lower_name.endswith(
            ".safetensors.index.json"
        ):
            problems.append(f"model artifact: {relative}")
            continue
        if not path.exists():
            continue
        size = path.stat().st_size
        if size > MAX_TRACKED_BYTES:
            problems.append(f"oversized tracked file ({size} bytes): {relative}")
            continue
        if size <= 5 * 1024 * 1024:
            content = path.read_bytes()
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(content):
                    problems.append(f"possible {label}: {relative}")
    return problems


def main() -> int:
    problems = violations(tracked_files())
    if problems:
        print("Repository artifact guard failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print("Repository artifact guard passed: no weights, secrets, or oversized files tracked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
