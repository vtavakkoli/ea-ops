from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
from pathlib import Path

from benchmarks.common import summary, write_csv, write_json


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _numbers(rows: list[dict], key: str) -> list[float]:
    return [float(row[key]) for row in rows if row.get(key) not in (None, "")]


def aggregate_accuracy(input_dir: Path, output_dir: Path) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(input_dir.glob("accuracy-*.csv")):
        for row in _read_csv(path):
            grouped[row["fault_type"]].append(row)
    table = []
    for fault, rows in sorted(grouped.items()):
        tp = sum(int(r["tp"]) for r in rows)
        fp = sum(int(r["fp"]) for r in rows)
        fn = sum(int(r["fn"]) for r in rows)
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        table.append(
            {
                "fault_type": fault,
                "trials": len(rows),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": f"{precision:.6f}",
                "recall": f"{recall:.6f}",
                "f1": f"{f1:.6f}",
            }
        )
    write_csv(output_dir / "summary" / "Table-1-validation-accuracy.csv", table)
    return table


def aggregate_performance(input_dir: Path, output_dir: Path) -> tuple[list[dict], list[dict]]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for path in sorted(input_dir.glob("performance-*.csv")):
        for row in _read_csv(path):
            grouped[int(row["objects"])].append(row)

    scalability, impact_table = [], []
    for objects, rows in sorted(grouped.items()):
        validation = summary(_numbers(rows, "validation_seconds"))
        throughput = summary(_numbers(rows, "objects_per_second"))
        memory = _numbers(rows, "peak_rss_mb")
        report = summary(_numbers(rows, "report_seconds"))
        portal = summary(_numbers(rows, "portal_seconds"))
        impact_s = summary(_numbers(rows, "impact_seconds"))
        impact_size = summary(_numbers(rows, "impact_size"))
        relationships = int(rows[0]["relationships"])
        scalability.append(
            {
                "objects": objects,
                "relationships": relationships,
                "repetitions": validation["n"],
                "validation_median_s": f"{validation['median']:.6f}",
                "validation_mean_s": f"{validation['mean']:.6f}",
                "validation_p95_s": f"{validation['p95']:.6f}",
                "validation_ci95_s": f"{validation['ci95']:.6f}",
                "objects_per_second_median": f"{throughput['median']:.2f}",
                "peak_rss_mb_max": f"{max(memory):.2f}",
                "report_median_s": f"{report['median']:.6f}",
                "portal_median_s": f"{portal['median']:.6f}",
            }
        )
        impact_table.append(
            {
                "objects": objects,
                "relationships": relationships,
                "impact_median_ms": f"{impact_s['median'] * 1000:.6f}",
                "impact_p95_ms": f"{impact_s['p95'] * 1000:.6f}",
                "impact_ci95_ms": f"{impact_s['ci95'] * 1000:.6f}",
                "impacted_objects_median": f"{impact_size['median']:.1f}",
            }
        )
    write_csv(output_dir / "summary" / "Table-2-scalability.csv", scalability)
    write_csv(output_dir / "summary" / "Table-3-impact.csv", impact_table)
    return scalability, impact_table


def figures(scalability: list[dict], impact_table: list[dict], output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    xs = [int(r["objects"]) for r in scalability]

    fig, ax = plt.subplots()
    ax.plot(xs, [float(r["validation_median_s"]) for r in scalability], marker="o")
    ax.set_xscale("log")
    ax.set_xlabel("Architecture objects")
    ax.set_ylabel("Median validation time (s)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(figure_dir / "Figure-validation-runtime.pdf")
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.plot(xs, [float(r["peak_rss_mb_max"]) for r in scalability], marker="o")
    ax.set_xscale("log")
    ax.set_xlabel("Architecture objects")
    ax.set_ylabel("Peak RSS (MB)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(figure_dir / "Figure-memory.pdf")
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.plot(xs, [float(r["impact_median_ms"]) for r in impact_table], marker="o")
    ax.set_xscale("log")
    ax.set_xlabel("Architecture objects")
    ax.set_ylabel("Median impact-analysis time (ms)")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(figure_dir / "Figure-impact-runtime.pdf")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate raw EA-Ops research CSVs into paper tables and figures.")
    parser.add_argument("--input", default="results/raw")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    input_dir, output_dir = Path(args.input), Path(args.output)
    accuracy = aggregate_accuracy(input_dir, output_dir)
    scalability, impact_table = aggregate_performance(input_dir, output_dir)
    figures(scalability, impact_table, output_dir)
    write_json(
        output_dir / "summary" / "summary.json",
        {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "accuracy_fault_classes": len(accuracy),
            "scalability_sizes": len(scalability),
            "note": "Raw measurements remain in results/raw; tables are deterministic aggregations.",
        },
    )
    print(json.dumps({"accuracy_rows": len(accuracy), "scalability_rows": len(scalability)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
