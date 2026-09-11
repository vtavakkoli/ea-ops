from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import subprocess

import yaml


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    object_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {"severity": self.severity, "code": self.code, "message": self.message, "object_id": self.object_id}


@dataclass
class RepositoryModel:
    root: Path
    config: dict[str, Any]
    objects: dict[str, dict[str, Any]] = field(default_factory=dict)
    relationships: dict[str, dict[str, Any]] = field(default_factory=dict)
    views: dict[str, dict[str, Any]] = field(default_factory=dict)
    rules: list[dict[str, Any]] = field(default_factory=list)
    metamodel: dict[str, Any] = field(default_factory=dict)


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _documents(folder: Path) -> list[tuple[Path, dict[str, Any]]]:
    result = []
    if not folder.exists(): return result
    for path in sorted(list(folder.rglob("*.yaml")) + list(folder.rglob("*.yml"))):
        data = _load_yaml(path)
        if not data: continue
        if isinstance(data, list):
            result.extend((path, item) for item in data if isinstance(item, dict))
        elif isinstance(data, dict):
            result.append((path, data))
    return result


def load_repository(root: str | Path) -> RepositoryModel:
    root = Path(root).resolve()
    config_path = root / "eaops.yaml"
    if not config_path.exists(): raise FileNotFoundError(f"EA-Ops configuration not found: {config_path}")
    config = _load_yaml(config_path) or {}
    repo = RepositoryModel(root=root, config=config)
    paths = config.get("paths", {})
    for path, item in _documents(root / paths.get("model", "model")):
        item = dict(item); item["_source"] = str(path.relative_to(root)); oid = item.get("id")
        if oid:
            if oid in repo.objects: item["_duplicate"] = True
            repo.objects[oid] = item
    for path, item in _documents(root / paths.get("relationships", "relationships")):
        item = dict(item); item["_source"] = str(path.relative_to(root)); rid = item.get("id")
        if rid:
            if rid in repo.relationships: item["_duplicate"] = True
            repo.relationships[rid] = item
    for path, item in _documents(root / paths.get("views", "views")):
        item = dict(item); item["_source"] = str(path.relative_to(root)); vid = item.get("id")
        if vid: repo.views[vid] = item
    for _, item in _documents(root / paths.get("rules", "rules")):
        repo.rules.extend(item["rules"] if "rules" in item and isinstance(item["rules"], list) else [item])
    mm_cfg = config.get("metamodel", {})
    mm_ref = mm_cfg.get("path")
    mm_path = (root / mm_ref).resolve() if mm_ref else Path(__file__).parent / "data" / f"{mm_cfg.get('builtin','archimate-3.2')}.yaml"
    if mm_path.exists(): repo.metamodel = _load_yaml(mm_path) or {}
    return repo


def _allowed_relation(repo: RepositoryModel, rel: dict[str, Any]) -> bool:
    spec = (repo.metamodel.get("relationshipTypes") or {}).get(rel.get("type"))
    if not spec: return False
    source = repo.objects.get(rel.get("source"), {}); target = repo.objects.get(rel.get("target"), {})
    source_types = spec.get("sourceTypes", ["*"]); target_types = spec.get("targetTypes", ["*"])
    return ("*" in source_types or source.get("type") in source_types) and ("*" in target_types or target.get("type") in target_types)


def _matching_objects(repo: RepositoryModel, rule: dict[str, Any]) -> list[dict[str, Any]]:
    target_type = rule.get("target", {}).get("type"); items = list(repo.objects.values())
    if target_type:
        allowed = {target_type} if isinstance(target_type, str) else set(target_type)
        items = [obj for obj in items if obj.get("type") in allowed]
    props = rule.get("when", {}).get("properties", {})
    if props: items = [obj for obj in items if all((obj.get("properties") or {}).get(k) == v for k, v in props.items())]
    return items


def validate(repo: RepositoryModel) -> list[Issue]:
    issues = []; element_types = repo.metamodel.get("elementTypes") or {}
    for oid, obj in repo.objects.items():
        for field_name in ("id", "type", "name"):
            if not obj.get(field_name): issues.append(Issue("error", "OBJECT_REQUIRED", f"Missing required field '{field_name}'", oid))
        if obj.get("_duplicate"): issues.append(Issue("error", "DUPLICATE_ID", "Duplicate object id", oid))
        if obj.get("type") and element_types and obj.get("type") not in element_types:
            issues.append(Issue("error", "UNKNOWN_ELEMENT_TYPE", f"Unsupported element type '{obj.get('type')}'", oid))
    for rid, rel in repo.relationships.items():
        for field_name in ("id", "type", "source", "target"):
            if not rel.get(field_name): issues.append(Issue("error", "REL_REQUIRED", f"Missing relationship field '{field_name}'", rid))
        if rel.get("_duplicate"): issues.append(Issue("error", "DUPLICATE_ID", "Duplicate relationship id", rid))
        if rel.get("source") not in repo.objects: issues.append(Issue("error", "MISSING_SOURCE", f"Unknown source '{rel.get('source')}'", rid))
        if rel.get("target") not in repo.objects: issues.append(Issue("error", "MISSING_TARGET", f"Unknown target '{rel.get('target')}'", rid))
        if rel.get("source") in repo.objects and rel.get("target") in repo.objects and not _allowed_relation(repo, rel):
            issues.append(Issue("error", "INVALID_RELATIONSHIP", f"Relationship '{rel.get('type')}' is not allowed for this source/target pair", rid))
    for rule in repo.rules:
        rule_id = rule.get("id", "custom-rule"); severity = rule.get("severity", "error")
        for obj in _matching_objects(repo, rule):
            oid = obj.get("id"); req = rule.get("require", {})
            for prop in req.get("properties", []):
                if not (obj.get("properties") or {}).get(prop): issues.append(Issue(severity, rule_id, rule.get("message") or f"Required property '{prop}' is missing", oid))
            rel_req = req.get("relationship")
            if rel_req:
                direction = rel_req.get("direction", "incoming"); rtype = rel_req.get("type"); min_count = int(rel_req.get("min", 1)); related = []
                for rel in repo.relationships.values():
                    match_direction = rel.get("target") == oid if direction == "incoming" else rel.get("source") == oid
                    if match_direction and (not rtype or rel.get("type") == rtype): related.append(rel)
                if len(related) < min_count: issues.append(Issue(severity, rule_id, rule.get("message") or f"Requires at least {min_count} {rtype} relationship(s)", oid))
    return issues


def metrics(repo: RepositoryModel, issues: list[Issue] | None = None) -> dict[str, Any]:
    issues = issues if issues is not None else validate(repo); objects = list(repo.objects.values())
    owned = [o for o in objects if (o.get("properties") or {}).get("owner")]; described = [o for o in objects if o.get("description")]
    errors = len([i for i in issues if i.severity == "error"]); warnings = len([i for i in issues if i.severity == "warning"]); score = 100
    score -= min(50, errors * 12); score -= min(20, warnings * 3)
    if objects:
        score -= round((1 - len(owned) / len(objects)) * 15); score -= round((1 - len(described) / len(objects)) * 15)
    return {"objects": len(repo.objects), "relationships": len(repo.relationships), "views": len(repo.views), "rules": len(repo.rules), "errors": errors, "warnings": warnings, "ownershipCoverage": round(len(owned) / len(objects) * 100, 1) if objects else 100.0, "descriptionCoverage": round(len(described) / len(objects) * 100, 1) if objects else 100.0, "qualityScore": max(0, score)}


def impact(repo: RepositoryModel, changed_ids: set[str]) -> dict[str, Any]:
    impacted = set(changed_ids); frontier = set(changed_ids)
    while frontier:
        nxt = set()
        for rel in repo.relationships.values():
            s, t = rel.get("source"), rel.get("target")
            if s in frontier and t not in impacted: nxt.add(t)
            if t in frontier and s not in impacted: nxt.add(s)
        impacted |= nxt; frontier = nxt
    by_type = {}
    for oid in impacted:
        if oid in repo.objects:
            typ = repo.objects[oid].get("type", "Unknown"); by_type[typ] = by_type.get(typ, 0) + 1
    return {"changed": sorted(changed_ids), "impacted": sorted(impacted), "byType": dict(sorted(by_type.items()))}


def changed_object_ids(repo: RepositoryModel, base: str = "HEAD~1") -> set[str]:
    try:
        proc = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=repo.root, capture_output=True, text=True, check=True)
    except Exception: return set()
    files = {line.strip() for line in proc.stdout.splitlines() if line.strip()}; ids = set()
    for oid, obj in repo.objects.items():
        if obj.get("_source") in files: ids.add(oid)
    for rel in repo.relationships.values():
        if rel.get("_source") in files: ids.update([rel.get("source"), rel.get("target")])
    return {x for x in ids if x}


def json_summary(repo: RepositoryModel) -> str:
    issues = validate(repo)
    return json.dumps({"metrics": metrics(repo, issues), "issues": [i.as_dict() for i in issues]}, indent=2)
