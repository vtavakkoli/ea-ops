from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import sys

from benchmarks.common import write_json


def _cpu() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def _memory_mb() -> int | None:
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) // 1024
    return None


def collect() -> dict:
    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": os.environ.get("GITHUB_SHA"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "runner_name": os.environ.get("RUNNER_NAME"),
        "image_os": os.environ.get("ImageOS"),
        "platform": platform.platform(),
        "python": sys.version,
        "cpu": _cpu(),
        "memory_mb": _memory_mb(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(write_json(args.output, collect()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
