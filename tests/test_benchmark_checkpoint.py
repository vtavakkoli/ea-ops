import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from benchmarks.benchmark import run
from benchmarks.generate_model import generate_repository


class CheckpointTests(unittest.TestCase):
    def test_completed_phases_survive_portal_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = generate_repository(root / "model", objects=20)
            output, progress = root / "raw.csv", root / "progress.jsonl"
            with patch("benchmarks.benchmark.render_portal", side_effect=RuntimeError("publication interrupted")):
                with self.assertRaises(RuntimeError):
                    run(model, 1, 0, 1, output=output, progress=progress)
            with output.open() as handle:
                records = list(csv.DictReader(handle))
            self.assertEqual(1, len(records))
            self.assertGreater(float(records[0]["validation_seconds"]), 0)
            self.assertGreater(float(records[0]["report_seconds"]), 0)
            self.assertEqual("", records[0]["portal_seconds"])
            self.assertEqual("portal", json.loads(progress.read_text().splitlines()[-1])["stage"])

    @unittest.skipUnless(sys.platform.startswith("linux"), "supervisor samples Linux /proc")
    def test_deadline_keeps_elapsed_and_memory_telemetry(self):
        script = Path(__file__).resolve().parents[1] / "benchmarks" / "run_bounded.py"
        with tempfile.TemporaryDirectory() as tmp:
            telemetry = Path(tmp) / "resource.json"
            result = subprocess.run([sys.executable, str(script), "--deadline-seconds", "0.1",
                "--telemetry", str(telemetry), "--", sys.executable, "-c", "import time; time.sleep(10)"], capture_output=True)
            self.assertEqual(124, result.returncode, result.stderr)
            data = json.loads(telemetry.read_text())
            self.assertEqual("timeout", data["status"])
            self.assertGreaterEqual(data["elapsed_seconds"], 0.1)
            self.assertGreater(data["observed_child_peak_rss_mb"], 0)
