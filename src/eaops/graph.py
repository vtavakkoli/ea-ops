"""Indexed structural impact; dependency propagation is an explicit review policy.

This is not an ArchiMate derivation engine or a prediction of business consequence.
The legacy undirected default is retained for reproducibility.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import RepositoryModel


def propagation_arcs(rel: dict[str, Any], profile: str, direction: str):
    source, target = rel.get("source"), rel.get("target")
    if not source or not target:
        return []
    if profile == "structural":
        arcs = [(source, target), (target, source)]
    else:
        kind = rel.get("type")
        if kind in {"Serving", "Realization", "Assignment", "Triggering", "Flow"}:
            arcs = [(source, target)]
        elif kind in {"Composition", "Aggregation"}:
            arcs = [(target, source)]  # changed part -> containing whole
        elif kind == "Access":
            access = (rel.get("properties") or {}).get("accessType", "access")
            arcs = []
            if access in {"read", "read-write", "access"}:
                arcs.append((target, source))  # changed data -> reader
            if access in {"write", "read-write", "access"}:
                arcs.append((source, target))  # changed writer -> data
        else:
            arcs = []  # Association and intent links are not dependency evidence.
        return arcs
    if direction == "outgoing":
        return [(source, target)]
    if direction == "incoming":
        return [(target, source)]
    return arcs


def indexed_impact(
    repo: RepositoryModel,
    changed_ids: set[str],
    *,
    profile: str = "structural",
    direction: str = "both",
    relationship_types: set[str] | None = None,
    max_depth: int | None = None,
    explain: bool = False,
) -> dict[str, Any]:
    if profile not in {"structural", "dependency"}:
        raise ValueError("profile must be structural or dependency")
    if direction not in {"both", "incoming", "outgoing"}:
        raise ValueError("direction must be both, incoming or outgoing")
    if profile == "dependency" and direction != "both":
        raise ValueError("dependency profile defines its own relationship directions")
    if max_depth is not None and (isinstance(max_depth, bool) or not isinstance(max_depth, int) or max_depth < 0):
        raise ValueError("max_depth must be a nonnegative integer")
    adjacency = defaultdict(list)
    for rid, rel in repo.relationships.items():
        if relationship_types is not None and rel.get("type") not in relationship_types:
            continue
        for source, target in propagation_arcs(rel, profile, direction):
            adjacency[source].append((target, rid))
    distance = {oid: 0 for oid in sorted(changed_ids)}
    reasons = {oid: {"depth": 0, "via": None, "relationship": None} for oid in distance}
    queue = deque(distance)
    while queue:
        current = queue.popleft()
        if max_depth is not None and distance[current] >= max_depth:
            continue
        for neighbor, rid in adjacency.get(current, ()):
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                reasons[neighbor] = {"depth": distance[neighbor], "via": current, "relationship": rid}
                queue.append(neighbor)
    by_type: dict[str, int] = {}
    for oid in distance:
        if oid in repo.objects:
            kind = repo.objects[oid].get("type", "Unknown")
            by_type[kind] = by_type.get(kind, 0) + 1
    result = {"changed": sorted(changed_ids), "impacted": sorted(distance), "byType": dict(sorted(by_type.items()))}
    if explain:
        result.update(profile=profile, direction=direction, maxDepth=max_depth,
                      relationshipTypes=sorted(relationship_types) if relationship_types is not None else None,
                      reasons={oid: reasons[oid] for oid in sorted(reasons)})
    return result
