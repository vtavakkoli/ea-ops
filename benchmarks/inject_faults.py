from __future__ import annotations

import argparse
from pathlib import Path
import shutil

import yaml

try:
    from benchmarks.common import write_json
except ModuleNotFoundError:  # direct script execution: python benchmarks/inject_faults.py
    from common import write_json


FAULTS = (
    "dangling_source",
    "dangling_target",
    "invalid_archimate_relationship",
    "missing_owner",
    "missing_criticality",
    "duplicate_id",
    "invalid_lifecycle",
    "governance_violation",
)


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _find(items: list[dict], oid: str) -> dict:
    return next(item for item in items if item.get("id") == oid)


def inject_fault(clean: str | Path, output: str | Path, fault: str) -> Path:
    if fault not in FAULTS:
        raise ValueError(f"Unsupported fault: {fault}")
    clean = Path(clean)
    root = Path(output)
    if root.exists():
        shutil.rmtree(root)
    shutil.copytree(clean, root)

    model_path = root / "model" / "model.yaml"
    rel_path = root / "relationships" / "relationships.yaml"
    model = _load(model_path)
    rels = _load(rel_path)
    expected: list[dict[str, str]] = []

    if fault == "dangling_source":
        rel = next(r for r in rels if str(r.get("id", "")).startswith("rel.association."))
        rel["source"] = "app.missing-source"
        expected.append({"code": "MISSING_SOURCE", "object_id": rel["id"]})
    elif fault == "dangling_target":
        rel = next(r for r in rels if str(r.get("id", "")).startswith("rel.association."))
        rel["target"] = "app.missing-target"
        expected.append({"code": "MISSING_TARGET", "object_id": rel["id"]})
    elif fault == "invalid_archimate_relationship":
        rel = next(r for r in rels if str(r.get("id", "")).startswith("rel.association."))
        rel["type"] = "Access"
        expected.append({"code": "INVALID_RELATIONSHIP", "object_id": rel["id"]})
    elif fault == "missing_owner":
        _find(model, "app.000000")["properties"].pop("owner", None)
        expected.append({"code": "BENCH-APP-REQUIRED", "object_id": "app.000000"})
    elif fault == "missing_criticality":
        _find(model, "process.benchmark")["properties"].pop("criticality", None)
        expected.append({"code": "BENCH-PROC-REQUIRED", "object_id": "process.benchmark"})
    elif fault == "duplicate_id":
        duplicate = dict(_find(model, "app.000000"))
        duplicate["name"] = "Intentional duplicate"
        _save(root / "model" / "zz-duplicate.yaml", [duplicate])
        expected.append({"code": "DUPLICATE_ID", "object_id": "app.000000"})
    elif fault == "invalid_lifecycle":
        _find(model, "app.000000")["properties"]["lifecycle"] = "invalid-lifecycle"
        expected.append({"code": "BENCH-LIFECYCLE", "object_id": "app.000000"})
    elif fault == "governance_violation":
        _find(model, "data.benchmark")["properties"].pop("classification", None)
        expected.append({"code": "BENCH-DATA-REQUIRED", "object_id": "data.benchmark"})

    _save(model_path, model)
    _save(rel_path, rels)
    write_json(
        root / "ground_truth.json",
        {
            "fault_type": fault,
            "oracle": "independent mutation manifest; no EA-Ops validator imports",
            "expected_errors": expected,
        },
    )
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject one controlled fault and write independent ground truth.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--fault", required=True, choices=FAULTS)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(inject_fault(args.model, args.output, args.fault))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
