from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .core import changed_object_ids, impact, json_summary, load_repository, metrics, validate
from .repository_portal import render_portal
from .render import render_report
from .compare import change_impact, compare_repositories


def _print_validation(repo) -> int:
    issues = validate(repo)
    m = metrics(repo, issues)
    print("EA-Ops Validation")
    print(f"Objects: {m['objects']}  Relationships: {m['relationships']}  Views: {m['views']}  Rules: {m['rules']}")
    print(f"Quality: {m['qualityScore']}/100  Ownership: {m['ownershipCoverage']}%")
    for issue in issues:
        print(f"{issue.severity.upper():7} {issue.code:28} {issue.object_id or '-'} — {issue.message}")
    if not issues:
        print("PASS    MODEL_VALID                  - — No validation findings")
    return 1 if any(i.severity == "error" for i in issues) else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="eaops", description="Git-native Enterprise Architecture Operations")
    p.add_argument("--version", action="version", version=f"eaops {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("validate", "summary"):
        s = sub.add_parser(name)
        s.add_argument("root", nargs="?", default=".")
    report = sub.add_parser("report")
    report.add_argument("root", nargs="?", default=".")
    report.add_argument("--output", "-o", default="reports/architecture-report.md")
    build = sub.add_parser("build")
    build.add_argument("root", nargs="?", default=".")
    build.add_argument("--output", "-o", default="site")
    imp = sub.add_parser("impact")
    imp.add_argument("root", nargs="?", default=".")
    imp.add_argument("--base", default="HEAD~1")
    imp.add_argument("--id", action="append", default=[])
    imp.add_argument("--profile", choices=("structural", "dependency"), default="structural")
    imp.add_argument("--direction", choices=("both", "incoming", "outgoing"), default="both")
    imp.add_argument("--relationship-type", action="append", default=None)
    imp.add_argument("--max-depth", type=int)
    imp.add_argument("--explain", action="store_true")
    imp.add_argument("--baseline", help="Compare two snapshot directories with change-aware dependency scope")
    diff = sub.add_parser("diff", help="Semantic baseline-to-target inventory gap")
    diff.add_argument("baseline")
    diff.add_argument("target")
    args = p.parse_args(argv)
    if args.cmd == "diff":
        print(json.dumps(compare_repositories(load_repository(args.baseline), load_repository(args.target)), indent=2))
        return 0
    repo = load_repository(args.root)
    if args.cmd == "validate": return _print_validation(repo)
    if args.cmd == "summary":
        print(json_summary(repo)); return 0
    if args.cmd == "report":
        print(render_report(repo, args.output)); return 0
    if args.cmd == "build":
        print(render_portal(repo, args.output)); return 0
    if args.cmd == "impact":
        if args.max_depth is not None and args.max_depth < 0:
            p.error("--max-depth must be nonnegative")
        if args.baseline:
            if args.id or args.profile != "structural" or args.direction != "both" or args.relationship_type is not None:
                p.error("--baseline selects change-aware dependency policy; use only --max-depth with it")
            print(json.dumps(change_impact(load_repository(args.baseline), repo, max_depth=args.max_depth), indent=2))
            return 0
        if args.profile == "dependency" and args.direction != "both":
            p.error("--profile dependency defines its own traversal direction")
        changed = set(args.id) or changed_object_ids(repo, args.base)
        print(json.dumps(impact(repo, changed, profile=args.profile, direction=args.direction,
                                relationship_types=set(args.relationship_type) if args.relationship_type is not None else None,
                                max_depth=args.max_depth, explain=args.explain), indent=2)); return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
