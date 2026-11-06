from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import resource
import sys
import tempfile
import time

from eaops.core import impact, load_repository, validate
from eaops.render import render_report
from eaops.repository_portal import render_portal


def _rss_mb() -> float:
    value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value / (1024 * 1024) if sys.platform == "darwin" else value / 1024


def _validate_once(model: Path):
    wall0 = time.perf_counter()
    cpu0 = time.process_time()
    repo = load_repository(model)
    issues = validate(repo)
    wall = time.perf_counter() - wall0
    cpu = time.process_time() - cpu0
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        sample = "; ".join(f"{i.code}:{i.object_id}" for i in errors[:5])
        raise RuntimeError(f"Generated clean benchmark is invalid ({len(errors)} errors): {sample}")
    return repo, wall, cpu


def run(model: str | Path, repetitions: int, warmups: int, build_repetitions: int,
        output: Path | None = None, progress: Path | None = None) -> list[dict]:
    if repetitions < 1 or warmups < 0 or not 0 <= build_repetitions <= repetitions:
        raise ValueError("require repetitions >= 1, warmups >= 0 and 0 <= build_repetitions <= repetitions")
    model = Path(model)
    started = time.perf_counter()
    def event(stage, repetition=0):
        if progress is not None:
            progress.parent.mkdir(parents=True, exist_ok=True)
            with progress.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"stage": stage, "repetition": repetition,
                                         "elapsed_seconds": time.perf_counter() - started,
                                         "process_peak_rss_mb": _rss_mb()}) + "\n")
    def checkpoint():
        if output is not None and rows:
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_suffix(output.suffix + ".tmp")
            with temporary.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            temporary.replace(output)
    for _ in range(warmups):
        event("warmup")
        repo, _, _ = _validate_once(model)
        impact(repo, {"app.000000"})
        del repo

    rows = []
    for repetition in range(1, repetitions + 1):
        event("validation", repetition)
        repo, validation_wall, validation_cpu = _validate_once(model)

        impact0 = time.perf_counter()
        impact_result = impact(repo, {"app.000000"})
        impact_wall = time.perf_counter() - impact0
        rows.append(
            {
                "repetition": repetition,
                "objects": len(repo.objects),
                "relationships": len(repo.relationships),
                "validation_seconds": f"{validation_wall:.9f}",
                "validation_cpu_seconds": f"{validation_cpu:.9f}",
                "objects_per_second": f"{len(repo.objects) / validation_wall:.3f}",
                "relationships_per_second": f"{len(repo.relationships) / validation_wall:.3f}",
                "impact_seconds": f"{impact_wall:.9f}",
                "impact_size": len(impact_result["impacted"]),
                "report_seconds": "",
                "portal_seconds": "",
                "peak_rss_mb": f"{_rss_mb():.3f}",
            }
        )
        checkpoint()  # Preserve completed phases even if publication is terminated.
        if repetition <= build_repetitions:
            with tempfile.TemporaryDirectory() as tmp:
                event("report", repetition)
                report0 = time.perf_counter()
                render_report(repo, Path(tmp) / "architecture-report.md")
                rows[-1]["report_seconds"] = f"{time.perf_counter() - report0:.9f}"
                rows[-1]["peak_rss_mb"] = f"{_rss_mb():.3f}"
                checkpoint()
                event("portal", repetition)
                portal0 = time.perf_counter()
                render_portal(repo, Path(tmp) / "site")
                rows[-1]["portal_seconds"] = f"{time.perf_counter() - portal0:.9f}"
        rows[-1]["peak_rss_mb"] = f"{_rss_mb():.3f}"
        checkpoint()
        event("repetition_complete", repetition)
        del repo  # Do not count simultaneous old/new repositories on the next load.
    event("complete", repetitions)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark EA-Ops validation, impact analysis and publication.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--build-repetitions", type=int, default=3)
    parser.add_argument("--output", required=True)
    parser.add_argument("--progress", help="Append per-phase progress telemetry as JSONL")
    args = parser.parse_args()
    rows = run(args.model, args.repetitions, args.warmups, args.build_repetitions,
               output=Path(args.output), progress=Path(args.progress) if args.progress else None)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
