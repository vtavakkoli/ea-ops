from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import subprocess

import yaml

from .archimate_matrix import RelationshipMatrixError, load_relationship_matrix


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
    if not folder.exists():
        return result
    for path in sorted(list(folder.rglob("*.yaml")) + list(folder.rglob("*.yml"))):
        data = _load_yaml(path)
        if not data:
            continue
        if isinstance(data, list):
            result.extend((path, item) for item in data if isinstance(item, dict))
        elif isinstance(data, dict):
            result.append((path, data))
    return result


def load_repository(root: str | Path) -> RepositoryModel:
    root = Path(root).resolve()
    config_path = root / "eaops.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"EA-Ops configuration not found: {config_path}")
    config = _load_yaml(config_path) or {}
    repo = RepositoryModel(root=root, config=config)
    paths = config.get("paths", {})
    for path, item in _documents(root / paths.get("model", "model")):
        item = dict(item)
        item["_source"] = str(path.relative_to(root))
        oid = item.get("id")
        if oid:
            if oid in repo.objects:
                item["_duplicate"] = True
            repo.objects[oid] = item
    for path, item in _documents(root / paths.get("relationships", "relationships")):
        item = dict(item)
        item["_source"] = str(path.relative_to(root))
        rid = item.get("id")
        if rid:
            if rid in repo.relationships:
                item["_duplicate"] = True
            repo.relationships[rid] = item
    for path, item in _documents(root / paths.get("views", "views")):
        item = dict(item)
        item["_source"] = str(path.relative_to(root))
        vid = item.get("id")
        if vid:
            repo.views[vid] = item
    for _, item in _documents(root / paths.get("rules", "rules")):
        repo.rules.extend(item["rules"] if "rules" in item and isinstance(item["rules"], list) else [item])
    mm_cfg = config.get("metamodel", {})
    mm_ref = mm_cfg.get("path")
    mm_path = (root / mm_ref).resolve() if mm_ref else Path(__file__).parent / "data" / f"{mm_cfg.get('builtin', 'archimate-3.2')}.yaml"
    if mm_path.exists():
        repo.metamodel = _load_yaml(mm_path) or {}
    return repo


def _endpoint_type(repo: RepositoryModel, endpoint_id: str | None) -> str | None:
    if not endpoint_id:
        return None
    if endpoint_id in repo.objects:
        return repo.objects[endpoint_id].get("type")
    if endpoint_id in repo.relationships:
        return "Relationship"
    return None


def _endpoint_exists(repo: RepositoryModel, endpoint_id: str | None) -> bool:
    return bool(endpoint_id and (endpoint_id in repo.objects or endpoint_id in repo.relationships))


def _relationship_matrix(repo: RepositoryModel) -> tuple[dict[tuple[str, str], frozenset[str]] | None, str | None]:
    spec = repo.metamodel.get("relationshipMatrix") or {}
    if not spec:
        return None, None
    try:
        _, matrix = load_relationship_matrix(spec)
        return matrix, None
    except RelationshipMatrixError as exc:
        return None, str(exc)


def valid_relationship_types(
    repo: RepositoryModel,
    source_type: str,
    target_type: str,
    matrix: dict[tuple[str, str], frozenset[str]] | None = None,
) -> tuple[str, ...]:
    if matrix is None:
        matrix, _ = _relationship_matrix(repo)
    if matrix is not None:
        return tuple(sorted(matrix.get((source_type, target_type), frozenset())))
    allowed = []
    for rel_type, spec in (repo.metamodel.get("relationshipTypes") or {}).items():
        source_types = spec.get("sourceTypes", ["*"])
        target_types = spec.get("targetTypes", ["*"])
        if ("*" in source_types or source_type in source_types) and ("*" in target_types or target_type in target_types):
            allowed.append(rel_type)
    return tuple(sorted(allowed))


def _allowed_relation(
    repo: RepositoryModel,
    rel: dict[str, Any],
    matrix: dict[tuple[str, str], frozenset[str]] | None = None,
) -> bool:
    rel_type = rel.get("type")
    spec = (repo.metamodel.get("relationshipTypes") or {}).get(rel_type)
    if not spec:
        return False
    source_type = _endpoint_type(repo, rel.get("source"))
    target_type = _endpoint_type(repo, rel.get("target"))
    if not source_type or not target_type:
        return False
    if matrix is not None:
        return rel_type in matrix.get((source_type, target_type), frozenset())
    source_types = spec.get("sourceTypes", ["*"])
    target_types = spec.get("targetTypes", ["*"])
    return ("*" in source_types or source_type in source_types) and ("*" in target_types or target_type in target_types)


def _matching_objects(repo: RepositoryModel, rule: dict[str, Any]) -> list[dict[str, Any]]:
    target_type = rule.get("target", {}).get("type")
    items = list(repo.objects.values())
    if target_type:
        allowed = {target_type} if isinstance(target_type, str) else set(target_type)
        items = [obj for obj in items if obj.get("type") in allowed]
    props = rule.get("when", {}).get("properties", {})
    if props:
        items = [obj for obj in items if all((obj.get("properties") or {}).get(k) == v for k, v in props.items())]
    return items


def _as_type_set(value: Any) -> set[str]:
    if not value:
        return set()
    return {value} if isinstance(value, str) else set(value)


def _related_relationships(repo: RepositoryModel, oid: str, requirement: dict[str, Any]) -> list[dict[str, Any]]:
    direction = requirement.get("direction", "incoming")
    rtype = requirement.get("type")
    source_types = _as_type_set(requirement.get("sourceType") or requirement.get("sourceTypes"))
    target_types = _as_type_set(requirement.get("targetType") or requirement.get("targetTypes"))
    matches = []
    for rel in repo.relationships.values():
        if direction == "incoming":
            direction_match = rel.get("target") == oid
        elif direction == "outgoing":
            direction_match = rel.get("source") == oid
        else:
            direction_match = rel.get("source") == oid or rel.get("target") == oid
        if not direction_match or (rtype and rel.get("type") != rtype):
            continue
        if source_types and _endpoint_type(repo, rel.get("source")) not in source_types:
            continue
        if target_types and _endpoint_type(repo, rel.get("target")) not in target_types:
            continue
        matches.append(rel)
    return matches


def _validate_junctions(repo: RepositoryModel) -> list[Issue]:
    issues = []
    for oid, obj in repo.objects.items():
        if obj.get("type") != "Junction":
            continue
        junction_type = str((obj.get("properties") or {}).get("junctionType", "and")).lower()
        if junction_type not in {"and", "or"}:
            issues.append(Issue("error", "JUNCTION_KIND", "Junction property 'junctionType' must be 'and' or 'or'", oid))
        incident = [r for r in repo.relationships.values() if r.get("source") == oid or r.get("target") == oid]
        rel_types = {r.get("type") for r in incident if r.get("type")}
        if len(rel_types) > 1:
            issues.append(
                Issue(
                    "error",
                    "JUNCTION_RELATIONSHIP_MIXED",
                    "An ArchiMate junction may only connect relationships of the same type; found " + ", ".join(sorted(rel_types)),
                    oid,
                )
            )
    return issues


def validate(repo: RepositoryModel) -> list[Issue]:
    issues = []
    element_types = repo.metamodel.get("elementTypes") or {}
    relationship_types = repo.metamodel.get("relationshipTypes") or {}
    matrix, matrix_error = _relationship_matrix(repo)
    matrix_spec = repo.metamodel.get("relationshipMatrix") or {}
    if matrix_spec and matrix_error:
        severity = "error" if matrix_spec.get("required", True) else "warning"
        issues.append(Issue(severity, "RELATIONSHIP_MATRIX_UNAVAILABLE", matrix_error))

    cross_ids = set(repo.objects).intersection(repo.relationships)
    for duplicate_id in sorted(cross_ids):
        issues.append(Issue("error", "DUPLICATE_GLOBAL_ID", "ID is used by both an architecture object and a relationship", duplicate_id))

    for oid, obj in repo.objects.items():
        for field_name in ("id", "type", "name"):
            if not obj.get(field_name):
                issues.append(Issue("error", "OBJECT_REQUIRED", f"Missing required field '{field_name}'", oid))
        if obj.get("_duplicate"):
            issues.append(Issue("error", "DUPLICATE_ID", "Duplicate object id", oid))
        if obj.get("type") and element_types and obj.get("type") not in element_types:
            issues.append(Issue("error", "UNKNOWN_ELEMENT_TYPE", f"Unsupported element type '{obj.get('type')}'", oid))

    for rid, rel in repo.relationships.items():
        for field_name in ("id", "type", "source", "target"):
            if not rel.get(field_name):
                issues.append(Issue("error", "REL_REQUIRED", f"Missing relationship field '{field_name}'", rid))
        if rel.get("_duplicate"):
            issues.append(Issue("error", "DUPLICATE_ID", "Duplicate relationship id", rid))
        if rel.get("type") and relationship_types and rel.get("type") not in relationship_types:
            issues.append(Issue("error", "UNKNOWN_RELATIONSHIP_TYPE", f"Unsupported relationship type '{rel.get('type')}'", rid))
        if not _endpoint_exists(repo, rel.get("source")):
            issues.append(Issue("error", "MISSING_SOURCE", f"Unknown source '{rel.get('source')}'", rid))
        if not _endpoint_exists(repo, rel.get("target")):
            issues.append(Issue("error", "MISSING_TARGET", f"Unknown target '{rel.get('target')}'", rid))
        if _endpoint_exists(repo, rel.get("source")) and _endpoint_exists(repo, rel.get("target")) and not _allowed_relation(repo, rel, matrix):
            source_type = _endpoint_type(repo, rel.get("source")) or "?"
            target_type = _endpoint_type(repo, rel.get("target")) or "?"
            allowed = valid_relationship_types(repo, source_type, target_type, matrix)
            suffix = f" Allowed: {', '.join(allowed)}." if allowed else " No relationship is permitted for this source/target pair."
            standard = repo.metamodel.get("standard") or repo.metamodel.get("name") or "configured metamodel"
            issues.append(
                Issue(
                    "error",
                    "INVALID_RELATIONSHIP",
                    f"{standard} does not permit '{rel.get('type')}' from {source_type} to {target_type}.{suffix}",
                    rid,
                )
            )

    issues.extend(_validate_junctions(repo))

    for rule in repo.rules:
        rule_id = rule.get("id", "custom-rule")
        severity = rule.get("severity", "error")
        for obj in _matching_objects(repo, rule):
            oid = obj.get("id")
            req = rule.get("require", {})
            for prop in req.get("properties", []):
                if not (obj.get("properties") or {}).get(prop):
                    issues.append(Issue(severity, rule_id, rule.get("message") or f"Required property '{prop}' is missing", oid))
            rel_req = req.get("relationship")
            if rel_req:
                min_count = int(rel_req.get("min", 1))
                max_count = rel_req.get("max")
                related = _related_relationships(repo, oid, rel_req)
                if len(related) < min_count:
                    relation_name = rel_req.get("type") or "matching"
                    issues.append(Issue(severity, rule_id, rule.get("message") or f"Requires at least {min_count} {relation_name} relationship(s)", oid))
                if max_count is not None and len(related) > int(max_count):
                    relation_name = rel_req.get("type") or "matching"
                    issues.append(Issue(severity, rule_id, rule.get("message") or f"Allows at most {max_count} {relation_name} relationship(s)", oid))
    return issues


def metrics(repo: RepositoryModel, issues: list[Issue] | None = None) -> dict[str, Any]:
    issues = issues if issues is not None else validate(repo)
    objects = list(repo.objects.values())
    owned = [o for o in objects if (o.get("properties") or {}).get("owner")]
    described = [o for o in objects if o.get("description")]
    errors = len([i for i in issues if i.severity == "error"])
    warnings = len([i for i in issues if i.severity == "warning"])
    score = 100
    score -= min(50, errors * 12)
    score -= min(20, warnings * 3)
    if objects:
        score -= round((1 - len(owned) / len(objects)) * 15)
        score -= round((1 - len(described) / len(objects)) * 15)
    return {
        "objects": len(repo.objects),
        "relationships": len(repo.relationships),
        "views": len(repo.views),
        "rules": len(repo.rules),
        "errors": errors,
        "warnings": warnings,
        "ownershipCoverage": round(len(owned) / len(objects) * 100, 1) if objects else 100.0,
        "descriptionCoverage": round(len(described) / len(objects) * 100, 1) if objects else 100.0,
        "qualityScore": max(0, score),
        "relationshipConformance": "strict" if repo.metamodel.get("relationshipMatrix") else "profile",
    }


def impact(repo: RepositoryModel, changed_ids: set[str]) -> dict[str, Any]:
    impacted = set(changed_ids)
    frontier = set(changed_ids)
    while frontier:
        nxt = set()
        for rel in repo.relationships.values():
            s, t = rel.get("source"), rel.get("target")
            if s in frontier and t not in impacted:
                nxt.add(t)
            if t in frontier and s not in impacted:
                nxt.add(s)
        impacted |= nxt
        frontier = nxt
    by_type = {}
    for oid in impacted:
        if oid in repo.objects:
            typ = repo.objects[oid].get("type", "Unknown")
            by_type[typ] = by_type.get(typ, 0) + 1
    return {"changed": sorted(changed_ids), "impacted": sorted(impacted), "byType": dict(sorted(by_type.items()))}


def changed_object_ids(repo: RepositoryModel, base: str = "HEAD~1") -> set[str]:
    try:
        proc = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=repo.root, capture_output=True, text=True, check=True)
    except Exception:
        return set()
    files = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    ids = set()
    for oid, obj in repo.objects.items():
        if obj.get("_source") in files:
            ids.add(oid)
    for rel in repo.relationships.values():
        if rel.get("_source") in files:
            ids.update([rel.get("source"), rel.get("target")])
    return {x for x in ids if x}


def json_summary(repo: RepositoryModel) -> str:
    issues = validate(repo)
    return json.dumps({"metrics": metrics(repo, issues), "issues": [i.as_dict() for i in issues]}, indent=2)
