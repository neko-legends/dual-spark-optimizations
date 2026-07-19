#!/usr/bin/env python3
"""Verify that every shard referenced by a Hugging Face safetensor index exists."""

import json
import hashlib
import argparse
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(16 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model_dir", type=Path)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--check-manifest", type=Path)
    args = parser.parse_args()
    model = args.model_dir
    index = json.loads((model / "model.safetensors.index.json").read_text())
    needed = sorted(set(index["weight_map"].values()))
    missing = [name for name in needed if not (model / name).is_file()]
    size = sum((model / name).stat().st_size for name in needed if (model / name).is_file())
    print(f"model={model}")
    print(f"safetensor_shards={len(needed)}")
    print(f"shard_bytes={size}")
    print(f"missing_shards={len(missing)}")
    if missing:
        print("\n".join(missing[:20]))
        raise SystemExit(1)

    if args.write_manifest:
        lines = [f"{sha256(model / name)}  {name}" for name in needed]
        args.write_manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote_manifest={args.write_manifest}")

    if args.check_manifest:
        failures = []
        for line in args.check_manifest.read_text(encoding="utf-8").splitlines():
            expected, name = line.split("  ", 1)
            actual = sha256(model / name)
            if actual != expected:
                failures.append(name)
        print(f"manifest_failures={len(failures)}")
        if failures:
            print("\n".join(failures))
            raise SystemExit(1)


if __name__ == "__main__":
    main()
