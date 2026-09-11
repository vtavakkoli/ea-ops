from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .core import changed_object_ids, impact, json_summary, load_repository, metrics, validate
from .portal_git import render_portal
from .render import render_report


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
    args = p.parse_args(argv)
    repo = load_repository(args.root)
    if args.cmd == "validate": return _print_validation(repo)
    if args.cmd == "summary":
        print(json_summary(repo)); return 0
    if args.cmd == "report":
        print(render_report(repo, args.output)); return 0
    if args.cmd == "build":
        print(render_portal(repo, args.output)); return 0
    if args.cmd == "impact":
        changed = set(args.id) or changed_object_ids(repo, args.base)
        print(json.dumps(impact(repo, changed), indent=2)); return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
