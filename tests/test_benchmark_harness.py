from pathlib import Path
import json
import tempfile
import unittest
import subprocess
import sys

import yaml

from benchmarks.generate_model import generate_repository
from benchmarks.inject_faults import inject_fault


class BenchmarkHarnessTests(unittest.TestCase):
    def test_generator_has_exact_object_count_and_fault_ground_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = generate_repository(Path(tmp) / "clean", objects=20, relationships=40, seed=7)
            model = yaml.safe_load((root / "model" / "model.yaml").read_text(encoding="utf-8"))
            relationships = yaml.safe_load((root / "relationships" / "relationships.yaml").read_text(encoding="utf-8"))
            self.assertEqual(20, len(model))
            self.assertEqual(40, len(relationships))

            faulty = inject_fault(root, Path(tmp) / "faulty", "missing_owner")
            truth = json.loads((faulty / "ground_truth.json").read_text(encoding="utf-8"))
            self.assertEqual("missing_owner", truth["fault_type"])
            self.assertEqual("BENCH-APP-REQUIRED", truth["expected_errors"][0]["code"])

    def test_research_scripts_support_direct_execution(self):
        repo_root = Path(__file__).resolve().parents[1]
        for script in (
            "benchmarks/inject_faults.py",
            "benchmarks/evaluate_accuracy.py",
            "benchmarks/environment.py",
            "benchmarks/aggregate.py",
        ):
            proc = subprocess.run(
                [sys.executable, script, "--help"],
                cwd=repo_root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, proc.returncode, msg=f"{script}: {proc.stderr}")


if __name__ == "__main__":
    unittest.main()
