import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "verify-model.py"


class VerifyModelTests(unittest.TestCase):
    def test_manifest_round_trip_and_corruption_detection(self):
        with tempfile.TemporaryDirectory() as temporary:
            model = Path(temporary)
            shards = ["model-00001.safetensors", "model-00002.safetensors"]
            (model / shards[0]).write_bytes(b"first shard")
            (model / shards[1]).write_bytes(b"second shard")
            (model / "model.safetensors.index.json").write_text(
                json.dumps({"weight_map": {"a": shards[0], "b": shards[1]}}),
                encoding="utf-8",
            )
            manifest = model / ".dual-spark-shards.sha256"

            subprocess.run(
                [sys.executable, SCRIPT, model, "--write-manifest", manifest],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [sys.executable, SCRIPT, model, "--check-manifest", manifest],
                check=True,
                capture_output=True,
                text=True,
            )

            (model / shards[1]).write_bytes(b"corrupted")
            failed = subprocess.run(
                [sys.executable, SCRIPT, model, "--check-manifest", manifest],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn(shards[1], failed.stdout)


if __name__ == "__main__":
    unittest.main()
