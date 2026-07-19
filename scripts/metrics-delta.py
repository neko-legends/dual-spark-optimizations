#!/usr/bin/env python3
"""Compute speculative-decoding counter deltas from two Prometheus snapshots."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


METRIC = re.compile(r"^(?P<series>vllm:spec_decode_[^ ]+)(?:\s+)(?P<value>[-+0-9.eE]+)$")


def parse(path: Path) -> dict[str, float]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = METRIC.match(line)
        if match and "_created{" not in match.group("series"):
            values[match.group("series")] = float(match.group("value"))
    return values


def total(deltas: dict[str, float], metric: str) -> float:
    return sum(value for series, value in deltas.items() if series.startswith(metric + "{"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    before = parse(args.before)
    after = parse(args.after)
    deltas = {
        series: value - before.get(series, 0.0)
        for series, value in after.items()
        if value - before.get(series, 0.0) != 0
    }
    drafts = total(deltas, "vllm:spec_decode_num_drafts_total")
    draft_tokens = total(deltas, "vllm:spec_decode_num_draft_tokens_total")
    accepted = total(deltas, "vllm:spec_decode_num_accepted_tokens_total")
    report = {
        "drafts": drafts,
        "draft_tokens": draft_tokens,
        "accepted_tokens": accepted,
        "acceptance_rate": accepted / draft_tokens if draft_tokens else 0.0,
        "accepted_tokens_per_draft": accepted / drafts if drafts else 0.0,
        "series_deltas": deltas,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
