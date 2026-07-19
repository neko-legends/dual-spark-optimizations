import importlib.util
import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "benchmark.py"
SPEC = importlib.util.spec_from_file_location("dual_spark_benchmark", MODULE_PATH)
benchmark = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(benchmark)


class StreamingHandler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 - BaseHTTPRequestHandler API
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))
        assert payload["stream"] is True
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        chunks = [
            {"choices": [{"delta": {"reasoning_content": "think"}}]},
            {"choices": [{"delta": {"content": "answer"}}]},
            {
                "choices": [],
                "usage": {"prompt_tokens": 123, "completion_tokens": 9},
            },
        ]
        for chunk in chunks:
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.flush()
            time.sleep(0.01)
        self.wfile.write(b"data: [DONE]\n\n")

    def log_message(self, _format, *args):
        pass


class BenchmarkTests(unittest.TestCase):
    def test_percentile(self):
        self.assertEqual(benchmark.percentile([1.0, 2.0, 3.0], 0.5), 2.0)
        self.assertEqual(benchmark.percentile([], 0.95), 0.0)

    def test_stream_request_parses_usage_and_timings(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), StreamingHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = benchmark.stream_request(
                f"http://127.0.0.1:{server.server_port}/v1/chat/completions",
                "test-model",
                "test prompt",
                9,
            )
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

        self.assertEqual(result["prompt_tokens"], 123)
        self.assertEqual(result["completion_tokens"], 9)
        self.assertEqual(result["stream_fragments"], 2)
        self.assertGreater(result["wall_seconds"], 0)
        self.assertGreater(result["ttft_seconds"], 0)
        self.assertGreater(result["decode_tokens_per_second"], 0)


if __name__ == "__main__":
    unittest.main()
