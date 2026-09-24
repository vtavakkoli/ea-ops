from __future__ import annotations

import argparse
import json
from pathlib import Path

from eaops.core import load_repository, validate
from benchmarks.common import write_csv


def evaluate(root: str | Path) -> tuple[list[dict], dict[str, float | int]]:
    root = Path(root)
    truth_files = sorted(root.rglob("ground_truth.json"))
    if not truth_files:
        raise FileNotFoundError(f"No ground_truth.json files found below {root}")

    rows = []
    total_tp = total_fp = total_fn = 0
    for truth_path in truth_files:
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        expected = {(x["code"], x.get("object_id")) for x in truth.get("expected_errors", [])}
        issues = validate(load_repository(truth_path.parent))
        actual = {(i.code, i.object_id) for i in issues if i.severity == "error"}
        tp = len(expected & actual)
        fp = len(actual - expected)
        fn = len(expected - actual)
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append(
            {
                "fault_type": truth.get("fault_type", "unknown"),
                "trial": truth_path.parent.name,
                "injected": len(expected),
                "detected": tp,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": f"{precision:.6f}",
                "recall": f"{recall:.6f}",
                "f1": f"{f1:.6f}",
                "actual_error_count": len(actual),
            }
        )
        total_tp += tp
        total_fp += fp
        total_fn += fn

    precision = total_tp / (total_tp + total_fp) if total_tp + total_fp else 1.0
    recall = total_tp / (total_tp + total_fn) if total_tp + total_fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return rows, {"tp": total_tp, "fp": total_fp, "fn": total_fn, "precision": precision, "recall": recall, "f1": f1}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate EA-Ops fault-detection precision, recall and F1.")
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--minimum-f1", type=float, default=0.99)
    args = parser.parse_args()
    rows, totals = evaluate(args.root)
    write_csv(args.output, rows)
    print(json.dumps(totals, indent=2))
    if float(totals["f1"]) < args.minimum_f1:
        raise SystemExit(f"F1 {totals['f1']:.6f} is below minimum {args.minimum_f1:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
