# Structural review policies

EA-Ops returns candidates for review. A reached ID is not a measured business consequence, and an excluded ID is not proven unaffected.

The default remains undirected reachability over all relationship kinds, including seed IDs which may be missing/deleted. The adjacency implementation preserves that output. It often returns an entire connected component.

```bash
eaops impact . --id service.identity
eaops impact . --id service.identity --profile dependency --explain
eaops impact . --id app.payment --direction incoming --relationship-type Serving --max-depth 2
eaops diff snapshots/baseline snapshots/target
eaops impact snapshots/target --baseline snapshots/baseline --max-depth 3
```

| Dependency-policy relationship | Propagation |
| --- | --- |
| Serving, Realization, Assignment, Triggering, Flow | Source to target |
| Composition, Aggregation | Part (target) to whole (source) |
| Access: read | Data (target) to reader (source) |
| Access: write | Writer (source) to data (target) |
| Access: read-write or unspecified `access` | Both directions |
| Association, Influence, Specialization, other intent links | Excluded from this policy |

These directions are explicit review heuristics, not ArchiMate derivation rules. Organizations must assess the policy against their dependency conventions. `--profile dependency` defines direction itself; raw `--direction` is available with the structural profile. Type filters restrict either profile. A depth of zero returns seeds only. Explanations give a shortest-path predecessor and relationship ID, not all possible paths.

Before/after comparison ignores serialization-source fields. Owner/name/description-only edits stay local. Other object changes propagate; changed relationships seed both old and new endpoints. Each state is traversed separately and the results are combined, preserving deleted paths. An object changed only in metadata can still propagate if it is also a changed-relationship endpoint. Rule, configuration, and metamodel changes set `policyReviewRequired`; they do not silently certify any object.

Ownership edits can have organizational effects beyond this local heuristic. Hop limits can hide distant consequences; missing relationships can hide any consequence. Evaluate review usefulness with architects before adopting the policy as a gate. Matrix validation checks explicit relationship compatibility; it does not compute derived relationships or provide full ArchiMate certification.

The `diff` command is an inventory gap, not TOGAF target-state compliance. See the companion repository's `research/run_roadmap.py` for three reproducible snapshots with Plateau/Gap concepts.
