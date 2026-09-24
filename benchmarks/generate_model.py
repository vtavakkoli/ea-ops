from __future__ import annotations

import argparse
from pathlib import Path
import random
import shutil

import yaml


def _write_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def generate_repository(output: str | Path, objects: int, relationships: int | None = None, seed: int = 42) -> Path:
    if objects < 10:
        raise ValueError("objects must be >= 10 so the benchmark can include governance fixtures")
    relationships = relationships if relationships is not None else objects * 2
    if relationships < 2:
        raise ValueError("relationships must be >= 2")

    root = Path(output)
    if root.exists():
        shutil.rmtree(root)
    for folder in ("model", "relationships", "views", "rules"):
        (root / folder).mkdir(parents=True, exist_ok=True)

    _write_yaml(
        root / "eaops.yaml",
        {
            "name": f"EA-Ops Benchmark {objects}",
            "version": "1.0",
            "metamodel": {"builtin": "archimate-3.2"},
            "paths": {"model": "model", "relationships": "relationships", "views": "views", "rules": "rules"},
        },
    )

    model = [
        {"id": "role.benchmark", "type": "BusinessRole", "name": "Benchmark Role", "properties": {"owner": "Research"}},
        {
            "id": "process.benchmark",
            "type": "BusinessProcess",
            "name": "Benchmark Process",
            "description": "Controlled business-process fixture for governance experiments.",
            "properties": {"owner": "Research", "lifecycle": "active", "criticality": "normal"},
        },
        {"id": "service.benchmark", "type": "ApplicationService", "name": "Benchmark Service", "properties": {"owner": "Research"}},
        {
            "id": "data.benchmark",
            "type": "DataObject",
            "name": "Benchmark Data",
            "properties": {"owner": "Research", "classification": "internal"},
        },
        {
            "id": "requirement.benchmark",
            "type": "Requirement",
            "name": "Benchmark Requirement",
            "properties": {"owner": "Research", "status": "approved"},
        },
    ]
    app_count = objects - len(model)
    app_ids = []
    for i in range(app_count):
        oid = f"app.{i:06d}"
        app_ids.append(oid)
        model.append(
            {
                "id": oid,
                "type": "ApplicationComponent",
                "name": f"Benchmark Application {i:06d}",
                "description": "Deterministically generated application component.",
                "properties": {"owner": f"Team-{i % 17:02d}", "lifecycle": "active"},
            }
        )
    _write_yaml(root / "model" / "model.yaml", model)

    rels = [
        {"id": "rel.fixture.assignment", "type": "Assignment", "source": "role.benchmark", "target": "process.benchmark"},
        {"id": "rel.fixture.serving", "type": "Serving", "source": "service.benchmark", "target": "process.benchmark"},
    ]
    rng = random.Random(seed)
    required_generated = max(0, relationships - len(rels))
    used: set[tuple[str, str]] = set()
    max_pairs = len(app_ids) * max(0, len(app_ids) - 1)
    if required_generated > max_pairs:
        raise ValueError(f"relationships={relationships} exceeds available unique directed application pairs")
    while len(used) < required_generated:
        source = app_ids[rng.randrange(len(app_ids))]
        target = app_ids[rng.randrange(len(app_ids))]
        if source == target or (source, target) in used:
            continue
        used.add((source, target))
    for i, (source, target) in enumerate(sorted(used)):
        rels.append({"id": f"rel.association.{i:07d}", "type": "Association", "source": source, "target": target})
    _write_yaml(root / "relationships" / "relationships.yaml", rels)

    _write_yaml(
        root / "rules" / "governance.yaml",
        {
            "rules": [
                {
                    "id": "BENCH-PROC-REQUIRED",
                    "target": {"type": "BusinessProcess"},
                    "require": {"properties": ["owner", "lifecycle", "criticality"]},
                    "severity": "error",
                    "message": "Benchmark processes require owner, lifecycle and criticality.",
                },
                {
                    "id": "BENCH-APP-REQUIRED",
                    "target": {"type": "ApplicationComponent"},
                    "require": {"properties": ["owner", "lifecycle"]},
                    "severity": "error",
                    "message": "Benchmark applications require owner and lifecycle.",
                },
                {
                    "id": "BENCH-DATA-REQUIRED",
                    "target": {"type": "DataObject"},
                    "require": {"properties": ["owner", "classification"]},
                    "severity": "error",
                    "message": "Benchmark data requires owner and classification.",
                },
                {
                    "id": "BENCH-REQ-REQUIRED",
                    "target": {"type": "Requirement"},
                    "require": {"properties": ["owner", "status"]},
                    "severity": "error",
                    "message": "Benchmark requirements require owner and status.",
                },
                {
                    "id": "BENCH-LIFECYCLE",
                    "target": {"type": "ApplicationComponent"},
                    "allow": {"properties": {"lifecycle": ["active", "strategic", "tolerate", "migrate", "eliminate"]}},
                    "severity": "error",
                    "message": "Application lifecycle must use the benchmark vocabulary.",
                },
            ]
        },
    )
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a deterministic EA-Ops research model.")
    parser.add_argument("--objects", type=int, required=True)
    parser.add_argument("--relationships", type=int)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(generate_repository(args.output, args.objects, args.relationships, args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
