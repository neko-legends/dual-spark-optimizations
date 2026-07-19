import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "metrics-delta.py"
SPEC = importlib.util.spec_from_file_location("metrics_delta", MODULE_PATH)
metrics_delta = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(metrics_delta)


class MetricsDeltaTests(unittest.TestCase):
    def test_parse_and_total(self):
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary) / "metrics.txt"
            snapshot.write_text(
                '\n'.join(
                    [
                        'vllm:spec_decode_num_drafts_total{engine="0"} 10',
                        'vllm:spec_decode_num_draft_tokens_total{engine="0"} 50',
                        'vllm:spec_decode_num_accepted_tokens_total{engine="0"} 35',
                        'vllm:spec_decode_num_drafts_created{engine="0"} 1234',
                    ]
                ),
                encoding="utf-8",
            )
            parsed = metrics_delta.parse(snapshot)
            self.assertEqual(
                metrics_delta.total(parsed, "vllm:spec_decode_num_drafts_total"),
                10,
            )
            self.assertNotIn('vllm:spec_decode_num_drafts_created{engine="0"}', parsed)


if __name__ == "__main__":
    unittest.main()
