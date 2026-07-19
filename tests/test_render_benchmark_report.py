import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "render-benchmark-report.py"
SPEC = importlib.util.spec_from_file_location("render_benchmark_report", MODULE_PATH)
reporter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = reporter
SPEC.loader.exec_module(reporter)


class RenderBenchmarkReportTests(unittest.TestCase):
    def test_load_and_render(self):
        payload = {
            "schema_version": 1,
            "profile": "fast",
            "model_revision": "abc123",
            "prompt": {"path": "/tmp/book-context-10k.txt"},
            "configuration": {"concurrency": 1},
            "summary": {
                "request_count": 3,
                "mean_decode_tokens_per_second": 61.25,
                "mean_group_aggregate_tokens_per_second": 60.5,
                "mean_ttft_seconds": 2.75,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "fast" / "run" / "book-context-10k-c1.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(payload), encoding="utf-8")
            results = reporter.load_results(root)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].prompt, "10K")
        self.assertEqual(results[0].model_revision, "abc123")
        svg = reporter.render_svg(results)
        markdown = reporter.render_markdown(results, "2026-07-19T00:00:00+00:00")
        self.assertIn("61.2", svg)
        self.assertIn("61.25", markdown)
        self.assertIn("abc123", markdown)
        stage_c_result = reporter.Result(
            profile="long-c4",
            prompt="10K",
            concurrency=4,
            decode_tps=20.0,
            aggregate_tps=80.0,
            ttft=3.0,
            requests=12,
            model_revision="abc123",
            source="long-c4/result.json",
        )
        self.assertIn(
            "Adaptive vs specialist profiles",
            reporter.render_concurrency_svg([stage_c_result]),
        )
        adaptive_rows = []
        for prompt, fast_c1, adaptive_c1, prior_c4, adaptive_c4 in (
            ("10K", 35.64, 34.54, 69.40, 75.44),
            ("200K", 52.47, 47.87, 64.70, 83.24),
            ("300K", 56.21, 55.32, 82.37, 87.10),
        ):
            for profile, concurrency, decode, aggregate in (
                ("fast", 1, fast_c1, fast_c1),
                ("adaptive", 1, adaptive_c1, adaptive_c1),
                ("fast-c4", 4, prior_c4 / 4, prior_c4),
                ("adaptive", 4, adaptive_c4 / 4, adaptive_c4),
            ):
                adaptive_rows.append(
                    reporter.Result(
                        profile=profile,
                        prompt=prompt,
                        concurrency=concurrency,
                        decode_tps=decode,
                        aggregate_tps=aggregate,
                        ttft=1.0,
                        requests=3 if concurrency == 1 else 12,
                        model_revision="abc123",
                        source=f"{profile}/{prompt}-c{concurrency}.json",
                    )
                )
        adaptive_svg = reporter.render_adaptive_svg(adaptive_rows)
        self.assertIn("One runtime. Fast alone. Faster together.", adaptive_svg)
        self.assertIn("adaptive  87.10", adaptive_svg)
        self.assertIn("No agent skill", adaptive_svg)

    def test_placeholder_is_honest(self):
        self.assertIn("Benchmarks pending", reporter.render_svg([]))
        self.assertIn("Benchmarks pending", reporter.render_concurrency_svg([]))
        self.assertIn("Benchmarks pending", reporter.render_adaptive_svg([]))
        self.assertIn("No local benchmark results", reporter.render_markdown([], "now"))


if __name__ == "__main__":
    unittest.main()
