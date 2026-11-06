"""Supplemental revision experiment, separate from the original hosted-run study.

Defaults: one warmup, three measured repetitions and three publication builds.
Each size runs in a fresh child process; the original safe YAML loader is retained.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from benchmarks.environment import collect
from benchmarks.generate_model import generate_repository


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[100, 1000, 10000, 50000, 100000])
    parser.add_argument("--output", default="research/revision/results")
    parser.add_argument("--generated", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    environment = collect()
    environment["protocol"] = {"warmups": 1, "repetitions": 3, "build_repetitions": 3, "seed": 42,
                               "study": "supplemental revision; not a matched-hardware speedup estimate"}
    environment["source_git_base"] = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    environment["source_was_modified"] = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    (output / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    for size in args.sizes:
        model = generate_repository(Path(args.generated) / str(size), objects=size, seed=42)
        print(f"Generated {size}; starting measured run", flush=True)
        command = [sys.executable, "benchmarks/run_bounded.py", "--deadline-seconds", "1800",
                   "--telemetry", str(output / f"resource-{size}.json"), "--", sys.executable,
                   "benchmarks/benchmark.py", "--model", str(model), "--warmups", "1",
                   "--repetitions", "3", "--build-repetitions", "3",
                   "--output", str(output / f"performance-{size}.csv"),
                   "--progress", str(output / f"progress-{size}.jsonl")]
        subprocess.run(command, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
