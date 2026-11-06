"""Semantic snapshot differences and conservative before/after review scope."""
from __future__ import annotations

from .core import RepositoryModel, impact


def _public(item):
    return {key: value for key, value in item.items() if not key.startswith("_")}


def _diff(before, after):
    return {
        "added": sorted(after.keys() - before.keys()),
        "removed": sorted(before.keys() - after.keys()),
        "modified": sorted(oid for oid in before.keys() & after.keys() if _public(before[oid]) != _public(after[oid])),
    }


def compare_repositories(baseline: RepositoryModel, target: RepositoryModel) -> dict:
    """Diff facts, not files. This is an inventory gap, not TOGAF compliance."""
    return {"objects": _diff(baseline.objects, target.objects),
            "relationships": _diff(baseline.relationships, target.relationships),
            "views": _diff(baseline.views, target.views),
            "rulesChanged": baseline.rules != target.rules,
            "configChanged": baseline.config != target.config,
            "metamodelChanged": baseline.metamodel != target.metamodel}


def _metadata_only(before, after):
    old, new = _public(before), _public(after)
    for item in (old, new):
        for key in ("name", "description"):
            item.pop(key, None)
        item["properties"] = {k: v for k, v in (item.get("properties") or {}).items() if k != "owner"}
    return old == new


def change_impact(baseline: RepositoryModel, target: RepositoryModel, *, max_depth: int | None = None) -> dict:
    delta = compare_repositories(baseline, target)
    obj_delta, rel_delta = delta["objects"], delta["relationships"]
    local = {oid for oid in obj_delta["modified"] if _metadata_only(baseline.objects[oid], target.objects[oid])}
    seeds = set(obj_delta["added"] + obj_delta["removed"] + obj_delta["modified"]) - local
    for group in rel_delta.values():
        for rid in group:
            for repo in (baseline, target):
                rel = repo.relationships.get(rid, {})
                seeds.update(x for x in (rel.get("source"), rel.get("target")) if x)
    # Walk each snapshot separately. Unioning edges first could create a path that
    # never existed in either state. Preserve deleted dependency paths explicitly.
    before = impact(baseline, seeds, profile="dependency", max_depth=max_depth, explain=True)
    after = impact(target, seeds, profile="dependency", max_depth=max_depth, explain=True)
    affected = set(before["impacted"]) | set(after["impacted"]) | local
    return {"delta": delta, "metadataOnly": sorted(local), "dependencySeeds": sorted(seeds),
            "impacted": sorted(affected), "before": before, "after": after,
            "policyReviewRequired": delta["rulesChanged"] or delta["metamodelChanged"] or delta["configChanged"],
            "scope": "structural review candidates; not observed business consequences"}
