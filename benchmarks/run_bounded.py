"""Linux research supervisor: keep elapsed time and observed process RSS on timeout.

Use a deadline shorter than the CI job timeout so artifacts can still be uploaded.
Peak RSS is sampled for the benchmark child only; polling can miss short peaks.
The benchmark also records its OS high-water mark at each phase boundary.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deadline-seconds", type=float, default=9000)
    parser.add_argument("--telemetry", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or args.deadline_seconds <= 0:
        parser.error("a command and positive deadline are required")
    if not sys.platform.startswith("linux"):
        parser.error("RSS sampling requires Linux /proc")
    output = Path(args.telemetry)
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    child = subprocess.Popen(command)
    observed_peak = 0.0
    def record(status):
        output.write_text(json.dumps({"status": status, "elapsed_seconds": time.perf_counter() - started,
            "observed_child_peak_rss_mb": observed_peak, "sampling_interval_seconds": 0.5,
            "pid": child.pid, "command": command, "returncode": child.poll(),
            "workflow_run_id": os.environ.get("GITHUB_RUN_ID"),
            "memory_scope": "benchmark child only; Linux VmHWM sampled every 0.5 s"}, indent=2) + "\n")
    timed_out = False
    try:
        while child.poll() is None:
            try:
                for line in Path(f"/proc/{child.pid}/status").read_text().splitlines():
                    if line.startswith("VmHWM:"):
                        observed_peak = max(observed_peak, float(line.split()[1]) / 1024)
            except (FileNotFoundError, ProcessLookupError):
                pass
            if time.perf_counter() - started >= args.deadline_seconds:
                timed_out = True
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                break
            record("running")
            time.sleep(0.5)
    finally:
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        record("timeout" if timed_out else "completed" if child.returncode == 0 else "failed")
    return 124 if timed_out else child.returncode


if __name__ == "__main__":
    raise SystemExit(main())
