from __future__ import annotations

import argparse
import csv
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


def run(model: str | Path, repetitions: int, warmups: int, build_repetitions: int) -> list[dict]:
    model = Path(model)
    for _ in range(warmups):
        repo, _, _ = _validate_once(model)
        impact(repo, {"app.000000"})

    rows = []
    for repetition in range(1, repetitions + 1):
        repo, validation_wall, validation_cpu = _validate_once(model)

        impact0 = time.perf_counter()
        impact_result = impact(repo, {"app.000000"})
        impact_wall = time.perf_counter() - impact0

        report_wall = ""
        portal_wall = ""
        if repetition <= build_repetitions:
            with tempfile.TemporaryDirectory() as tmp:
                report0 = time.perf_counter()
                render_report(repo, Path(tmp) / "architecture-report.md")
                report_wall = time.perf_counter() - report0
                portal0 = time.perf_counter()
                render_portal(repo, Path(tmp) / "site")
                portal_wall = time.perf_counter() - portal0

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
                "report_seconds": f"{report_wall:.9f}" if report_wall != "" else "",
                "portal_seconds": f"{portal_wall:.9f}" if portal_wall != "" else "",
                "peak_rss_mb": f"{_rss_mb():.3f}",
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark EA-Ops validation, impact analysis and publication.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--repetitions", type=int, default=30)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--build-repetitions", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = run(args.model, args.repetitions, args.warmups, args.build_repetitions)
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
