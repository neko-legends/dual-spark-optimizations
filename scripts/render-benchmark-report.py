#!/usr/bin/env python3
"""Render benchmark JSON reports as a Markdown table and standalone SVG chart."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROMPT_ORDER = {"10K": 0, "200K": 1, "300K": 2}
PROFILE_ORDER = {"adaptive": 0, "fast": 1, "fast-c4": 2, "long-c4": 3}
PROFILE_COLORS = {
    "adaptive": "#22d3ee",
    "fast": "#65d6ad",
    "fast-c4": "#f59e0b",
    "long-c4": "#7aa2f7",
}
PROFILE_LABELS = {
    "adaptive": "Adaptive",
    "fast": "Tony C1",
    "fast-c4": "Pre-adaptive C4",
    "long-c4": "stage-c long C4",
}


@dataclass(frozen=True)
class Result:
    profile: str
    prompt: str
    concurrency: int
    decode_tps: float
    aggregate_tps: float
    ttft: float
    requests: int
    model_revision: str
    source: str


def prompt_label(path: str) -> str:
    name = Path(path).stem.lower()
    for label in ("10K", "200K", "300K"):
        if f"-{label.lower()}" in name:
            return label
    return Path(path).stem


def load_results(input_dir: Path) -> list[Result]:
    results: list[Result] = []
    for path in sorted(input_dir.rglob("book-context-*-c*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or "summary" not in payload:
            continue
        configuration = payload["configuration"]
        summary = payload["summary"]
        profile = payload.get("profile")
        if profile not in PROFILE_ORDER:
            profile = next((part for part in path.parts if part in PROFILE_ORDER), "unknown")
        results.append(
            Result(
                profile=profile,
                prompt=prompt_label(payload["prompt"]["path"]),
                concurrency=int(configuration["concurrency"]),
                decode_tps=float(summary["mean_decode_tokens_per_second"]),
                aggregate_tps=float(summary["mean_group_aggregate_tokens_per_second"]),
                ttft=float(summary["mean_ttft_seconds"]),
                requests=int(summary["request_count"]),
                model_revision=str(payload.get("model_revision", "unknown")),
                source=path.relative_to(input_dir).as_posix(),
            )
        )
    return sorted(
        results,
        key=lambda row: (
            PROFILE_ORDER.get(row.profile, 99),
            row.concurrency,
            PROMPT_ORDER.get(row.prompt, 99),
            row.source,
        ),
    )


def _svg_text(x: float, y: float, value: str, **attrs: object) -> str:
    rendered = " ".join(f'{key.replace("_", "-")}="{html.escape(str(val))}"' for key, val in attrs.items())
    return f'<text x="{x:.1f}" y="{y:.1f}" {rendered}>{html.escape(value)}</text>'


def render_svg(results: Iterable[Result]) -> str:
    rows = [row for row in results if row.concurrency == 1]
    width, height = 1120, 650
    if not rows:
        return "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="360" viewBox="0 0 {width} 360">',
                '<rect width="100%" height="100%" rx="18" fill="#111827"/>',
                _svg_text(560, 145, "Dual-Spark benchmark comparison", fill="#f8fafc", font_size=30, text_anchor="middle", font_family="system-ui, sans-serif", font_weight="700"),
                _svg_text(560, 195, "Benchmarks pending", fill="#fbbf24", font_size=25, text_anchor="middle", font_family="system-ui, sans-serif"),
                _svg_text(560, 238, "Run the profiles, then render benchmark-results to replace this chart.", fill="#a7b0c0", font_size=16, text_anchor="middle", font_family="system-ui, sans-serif"),
                "</svg>",
            ]
        ) + "\n"

    panels = [
        ("Mean decode throughput (C1)", "tokens/s", lambda row: row.decode_tps),
        ("Mean time to first token (C1)", "seconds", lambda row: row.ttft),
    ]
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" rx="18" fill="#111827"/>',
        _svg_text(55, 55, "Dual-Spark measured benchmark comparison", fill="#f8fafc", font_size=27, font_family="system-ui, sans-serif", font_weight="700"),
        _svg_text(55, 82, "Same v1.1 weights · TTFT includes first full prefill plus cache-assisted repeats", fill="#a7b0c0", font_size=14, font_family="system-ui, sans-serif"),
    ]
    for index, (title, unit, getter) in enumerate(panels):
        panel_x = 55 + index * 535
        panel_y, chart_w, chart_h = 130, 475, 390
        values = [getter(row) for row in rows]
        maximum = max(values) * 1.15 if max(values) else 1.0
        output.append(_svg_text(panel_x, 115, title, fill="#f8fafc", font_size=18, font_family="system-ui, sans-serif", font_weight="600"))
        for tick in range(5):
            value = maximum * tick / 4
            y = panel_y + chart_h - chart_h * tick / 4
            output.append(f'<line x1="{panel_x}" y1="{y:.1f}" x2="{panel_x + chart_w}" y2="{y:.1f}" stroke="#2b3548"/>')
            output.append(_svg_text(panel_x - 8, y + 5, f"{value:.1f}", fill="#8993a4", font_size=12, text_anchor="end", font_family="system-ui, sans-serif"))
        prompts = sorted({row.prompt for row in rows}, key=lambda item: PROMPT_ORDER.get(item, 99))
        profiles = sorted({row.profile for row in rows}, key=lambda item: PROFILE_ORDER.get(item, 99))
        group_w = chart_w / max(len(prompts), 1)
        bar_w = min(48, group_w / (len(profiles) + 1))
        for prompt_index, prompt in enumerate(prompts):
            center = panel_x + group_w * (prompt_index + 0.5)
            output.append(_svg_text(center, panel_y + chart_h + 27, prompt, fill="#d8dee9", font_size=13, text_anchor="middle", font_family="system-ui, sans-serif"))
            for profile_index, profile in enumerate(profiles):
                matches = [row for row in rows if row.prompt == prompt and row.profile == profile]
                if not matches:
                    continue
                value = getter(matches[-1])
                x = center + (profile_index - (len(profiles) - 1) / 2) * (bar_w + 6) - bar_w / 2
                bar_h = chart_h * value / maximum
                y = panel_y + chart_h - bar_h
                color = PROFILE_COLORS.get(profile, "#c084fc")
                output.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="5" fill="{color}"/>')
                output.append(_svg_text(x + bar_w / 2, y - 7, f"{value:.1f}", fill="#f8fafc", font_size=11, text_anchor="middle", font_family="system-ui, sans-serif"))
        output.append(_svg_text(panel_x, panel_y + chart_h + 55, unit, fill="#8993a4", font_size=12, font_family="system-ui, sans-serif"))
    legend_x = 55
    for profile in sorted({row.profile for row in rows}, key=lambda item: PROFILE_ORDER.get(item, 99)):
        color = PROFILE_COLORS.get(profile, "#c084fc")
        output.append(f'<rect x="{legend_x}" y="605" width="16" height="16" rx="3" fill="{color}"/>')
        output.append(_svg_text(legend_x + 24, 618, PROFILE_LABELS.get(profile, profile), fill="#d8dee9", font_size=13, font_family="system-ui, sans-serif"))
        legend_x += 190
    output.append("</svg>")
    return "\n".join(output) + "\n"


def render_concurrency_svg(results: Iterable[Result]) -> str:
    rows = [
        row for row in results
        if row.profile in ("adaptive", "fast", "long-c4")
        and row.concurrency in (1, 4)
    ]
    width, height = 1120, 470
    if not rows:
        return render_svg([]).replace('height="360"', 'height="470"').replace(
            'viewBox="0 0 1120 360"', 'viewBox="0 0 1120 470"'
        )
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" rx="18" fill="#111827"/>',
        _svg_text(55, 55, "Adaptive vs specialist profiles", fill="#f8fafc", font_size=27, font_family="system-ui, sans-serif", font_weight="700"),
        _svg_text(55, 82, "Mean aggregate completion throughput · matched uncensored v1.1 weights", fill="#a7b0c0", font_size=14, font_family="system-ui, sans-serif"),
    ]
    chart_x, chart_y, chart_w, chart_h = 80, 115, 980, 265
    maximum = max(row.aggregate_tps for row in rows) * 1.15
    for tick in range(5):
        value = maximum * tick / 4
        y = chart_y + chart_h - chart_h * tick / 4
        output.append(f'<line x1="{chart_x}" y1="{y:.1f}" x2="{chart_x + chart_w}" y2="{y:.1f}" stroke="#2b3548"/>')
        output.append(_svg_text(chart_x - 10, y + 5, f"{value:.1f}", fill="#8993a4", font_size=12, text_anchor="end", font_family="system-ui, sans-serif"))
    prompts = sorted({row.prompt for row in rows}, key=lambda item: PROMPT_ORDER.get(item, 99))
    series = [("fast", 1), ("adaptive", 1), ("adaptive", 4), ("long-c4", 4)]
    colors = {
        ("fast", 1): "#65d6ad",
        ("adaptive", 1): "#22d3ee",
        ("adaptive", 4): "#f59e0b",
        ("long-c4", 4): "#c084fc",
    }
    group_w, bar_w = chart_w / len(prompts), 52
    for prompt_index, prompt in enumerate(prompts):
        center = chart_x + group_w * (prompt_index + 0.5)
        output.append(_svg_text(center, chart_y + chart_h + 27, prompt, fill="#d8dee9", font_size=14, text_anchor="middle", font_family="system-ui, sans-serif"))
        for series_index, (profile, concurrency) in enumerate(series):
            matches = [row for row in rows if row.prompt == prompt and row.profile == profile and row.concurrency == concurrency]
            if not matches:
                continue
            value = matches[-1].aggregate_tps
            x = center + (series_index - (len(series) - 1) / 2) * (bar_w + 7) - bar_w / 2
            bar_h = chart_h * value / maximum
            y = chart_y + chart_h - bar_h
            output.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" rx="6" fill="{colors[(profile, concurrency)]}"/>')
            output.append(_svg_text(x + bar_w / 2, y - 7, f"{value:.1f}", fill="#f8fafc", font_size=12, text_anchor="middle", font_family="system-ui, sans-serif"))
    legend_x = 80
    for profile, concurrency in series:
        output.append(f'<rect x="{legend_x}" y="430" width="16" height="16" rx="3" fill="{colors[(profile, concurrency)]}"/>')
        output.append(_svg_text(legend_x + 24, 443, f"{PROFILE_LABELS[profile]} C{concurrency}", fill="#d8dee9", font_size=13, font_family="system-ui, sans-serif"))
        legend_x += 245
    output.append("</svg>")
    return "\n".join(output) + "\n"


def render_adaptive_svg(results: Iterable[Result]) -> str:
    """Render one explanatory, mobile-friendly adaptive-vs-specialist figure."""
    rows = list(results)
    prompts = ("10K", "200K", "300K")

    def one(profile: str, prompt: str, concurrency: int) -> Result | None:
        matches = [
            row
            for row in rows
            if row.profile == profile
            and row.prompt == prompt
            and row.concurrency == concurrency
        ]
        return matches[-1] if matches else None

    c1: list[tuple[str, float, float]] = []
    c4: list[tuple[str, float, float]] = []
    for prompt in prompts:
        adaptive_c1 = one("adaptive", prompt, 1)
        fast_c1 = one("fast", prompt, 1)
        adaptive_c4 = one("adaptive", prompt, 4)
        prior_c4 = [
            result
            for profile in ("fast-c4", "long-c4")
            if (result := one(profile, prompt, 4)) is not None
        ]
        if adaptive_c1 is not None and fast_c1 is not None:
            c1.append((prompt, fast_c1.decode_tps, adaptive_c1.decode_tps))
        if adaptive_c4 is not None and prior_c4:
            c4.append(
                (
                    prompt,
                    max(result.aggregate_tps for result in prior_c4),
                    adaptive_c4.aggregate_tps,
                )
            )

    if len(c1) != 3 or len(c4) != 3:
        return render_svg([]).replace(
            "Dual-Spark benchmark comparison", "Adaptive benchmark comparison"
        )

    width, height = 640, 910
    bg = "#08111f"
    card = "#111c2e"
    grid = "#2a3a52"
    text_color = "#f8fafc"
    muted = "#9fb0c6"
    adaptive = "#22d3ee"
    specialist = "#64748b"
    positive = "#4ade80"
    tradeoff = "#fbbf24"
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="adaptive-title adaptive-desc">',
        '<title id="adaptive-title">Adaptive DSpark performance versus specialist profiles</title>',
        '<desc id="adaptive-desc">At 10K, 200K, and 300K prompts, adaptive retains 91 to 98 percent of dedicated single-request decode speed and exceeds the best previously measured four-request aggregate throughput.</desc>',
        f'<rect width="100%" height="100%" rx="22" fill="{bg}"/>',
        _svg_text(32, 45, "One runtime. Fast alone. Faster together.", fill=text_color, font_size=28, font_family="system-ui, sans-serif", font_weight="750"),
        _svg_text(32, 73, "Uncensored v1.1 · two DGX Sparks · matched 256-token tests", fill=muted, font_size=15, font_family="system-ui, sans-serif"),
        f'<rect x="32" y="94" width="576" height="58" rx="13" fill="#0e7490"/>',
        _svg_text(52, 119, "AUTOMATIC LIVE-BATCH ROUTING", fill="#cffafe", font_size=14, font_family="system-ui, sans-serif", font_weight="750", letter_spacing="0.8"),
        _svg_text(52, 141, "No agent skill, request flag, or model reload required", fill="#ecfeff", font_size=16, font_family="system-ui, sans-serif"),
    ]

    def panel(
        y: int,
        title: str,
        subtitle: str,
        data: list[tuple[str, float, float]],
        maximum: float,
        delta_mode: str,
    ) -> None:
        output.append(f'<rect x="32" y="{y}" width="576" height="282" rx="16" fill="{card}"/>')
        output.append(_svg_text(52, y + 37, title, fill=text_color, font_size=20, font_family="system-ui, sans-serif", font_weight="700"))
        output.append(_svg_text(52, y + 61, subtitle, fill=muted, font_size=14, font_family="system-ui, sans-serif"))
        plot_x, plot_w = 152, 410
        for tick in (0.0, 0.5, 1.0):
            x = plot_x + plot_w * tick
            output.append(f'<line x1="{x:.1f}" y1="{y + 82}" x2="{x:.1f}" y2="{y + 255}" stroke="{grid}" stroke-width="0.75" shape-rendering="crispEdges"/>')
            output.append(_svg_text(x, y + 78, f"{maximum * tick:.0f}", fill=muted, font_size=12, text_anchor="middle", font_family="system-ui, sans-serif"))
        output.append(_svg_text(582, y + 61, "tok/s", fill=muted, font_size=12, text_anchor="end", font_family="system-ui, sans-serif"))
        for index, (prompt, baseline, current) in enumerate(data):
            row_y = y + 108 + index * 55
            if delta_mode == "loss":
                delta = (current / baseline - 1.0) * 100
                delta_text = f"{delta:.1f}%"
                delta_color = tradeoff
            else:
                delta = (current / baseline - 1.0) * 100
                delta_text = f"+{delta:.1f}%"
                delta_color = positive
            output.append(_svg_text(52, row_y + 20, prompt, fill=text_color, font_size=17, font_family="system-ui, sans-serif", font_weight="700"))
            output.append(_svg_text(125, row_y + 20, delta_text, fill=delta_color, font_size=14, text_anchor="middle", font_family="system-ui, sans-serif", font_weight="750"))
            baseline_w = plot_w * baseline / maximum
            current_w = plot_w * current / maximum
            output.append(f'<rect x="{plot_x}" y="{row_y}" width="{baseline_w:.1f}" height="20" rx="5" fill="{specialist}"/>')
            output.append(_svg_text(plot_x + 8, row_y + 15, f"specialist  {baseline:.2f}", fill="#f1f5f9", font_size=13, font_family="system-ui, sans-serif", font_weight="650"))
            output.append(f'<rect x="{plot_x}" y="{row_y + 25}" width="{current_w:.1f}" height="20" rx="5" fill="{adaptive}"/>')
            output.append(_svg_text(plot_x + 8, row_y + 40, f"adaptive  {current:.2f}", fill="#082f49", font_size=13, font_family="system-ui, sans-serif", font_weight="750"))

    panel(
        174,
        "C1 · Single-request decode speed",
        "Adaptive stays close to the dedicated fast profile",
        c1,
        60.0,
        "loss",
    )
    panel(
        474,
        "C4 · Four-request aggregate throughput",
        "Adaptive beats the best prior concurrent result",
        c4,
        90.0,
        "gain",
    )
    output.extend(
        [
            f'<rect x="32" y="774" width="576" height="88" rx="16" fill="#0f2f2b" stroke="#166534" stroke-width="1"/>',
            _svg_text(52, 805, "THE BALANCED DEFAULT", fill=positive, font_size=14, font_family="system-ui, sans-serif", font_weight="800", letter_spacing="0.8"),
            _svg_text(52, 832, "Keeps 91–98% of C1 speed", fill=text_color, font_size=19, font_family="system-ui, sans-serif", font_weight="700"),
            '<line x1="332" y1="813" x2="332" y2="840" stroke="#3f625e" stroke-width="1" shape-rendering="crispEdges"/>',
            _svg_text(351, 832, "raises C4 by 5.7–28.7%", fill=text_color, font_size=19, font_family="system-ui, sans-serif", font_weight="700"),
            _svg_text(32, 892, "Three runs per case; repeated identical prompts may benefit from prefix caching. Full raw JSON is tracked in results/raw.", fill=muted, font_size=11, font_family="system-ui, sans-serif"),
            "</svg>",
        ]
    )
    return "\n".join(output) + "\n"


def render_markdown(results: list[Result], generated_at: str) -> str:
    if not results:
        return f"""# Measured benchmarks

No local benchmark results are available yet. This is intentional: upstream
numbers are not substituted for measurements from a private deployment.

After running the profiles, generate this report and its charts from the head:

```bash
python3 scripts/render-benchmark-report.py
```

Generated: {generated_at}
"""
    lines = [
        "# Measured benchmarks",
        "",
        "These are local measurements from this repository's harness, not upstream claims.",
        "Each case uses a 256-token output cap. C1 contains three sequential requests;",
        "C4 contains three groups of four simultaneous requests (12 total). Repeated",
        "identical prompts can benefit from the runtime's observed prefix caching, so",
        "TTFT combines the first full prefill with subsequent cache-assisted requests.",
        "Decode tok/s is the per-request mean; aggregate tok/s is the group throughput.",
        "",
        "| Profile | Prompt | C | Requests | Decode tok/s | Aggregate tok/s | Mean TTFT (s) | Model revision | Source |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in results:
        lines.append(
            f"| `{row.profile}` | {row.prompt} | {row.concurrency} | {row.requests} | "
            f"{row.decode_tps:.2f} | {row.aggregate_tps:.2f} | {row.ttft:.2f} | "
            f"`{row.model_revision}` | [`{row.source}`](raw/{row.source}) |"
        )
    lines.extend(["", f"Generated: {generated_at}", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("benchmark-results"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--placeholder", action="store_true")
    args = parser.parse_args()
    results = [] if args.placeholder else load_results(args.input)
    if not results and not args.placeholder:
        parser.error(f"no benchmark JSON reports found under {args.input}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    (args.output_dir / "benchmark-comparison.svg").write_text(
        render_svg(results), encoding="utf-8"
    )
    (args.output_dir / "concurrency-comparison.svg").write_text(
        render_concurrency_svg(results), encoding="utf-8"
    )
    (args.output_dir / "adaptive-performance.svg").write_text(
        render_adaptive_svg(results), encoding="utf-8"
    )
    (args.output_dir / "BENCHMARKS.md").write_text(
        render_markdown(results, generated_at), encoding="utf-8"
    )
    print(f"Rendered {len(results)} benchmark report(s) into {args.output_dir}")


if __name__ == "__main__":
    main()
