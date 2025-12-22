from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from ai_guard.report.markdown import to_markdown
from ai_guard.rules import DEFAULT_RULES
from ai_guard.scanner import scan_paths


def _finding_to_dict(f) -> dict:
    """
    Robust serializer that works whether Finding is a dataclass or a simple object.
    We avoid assuming exact field names.
    """
    try:
        data = dict(vars(f))
    except TypeError:
        data = {}

    # Normalize common fields if present (helps downstream tools)
    normalized = {}
    for key in ("code", "rule_id", "id"):
        if key in data:
            normalized["code"] = data[key]
            break
    for key in ("severity", "level"):
        if key in data:
            normalized["severity"] = data[key]
            break
    for key in ("message", "msg", "description"):
        if key in data:
            normalized["message"] = data[key]
            break
    for key in ("path", "file", "filename"):
        if key in data:
            normalized["path"] = data[key]
            break
    for key in ("line", "line_no", "lineno"):
        if key in data:
            normalized["line"] = data[key]
            break

    # include all original keys too (so nothing is lost)
    merged = {**data, **normalized}
    return merged


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ai-guard",
        description="AI Guard — lightweight code review gatekeeper for security & quality checks.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan paths and print a report.")
    scan.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Paths to scan (files or directories). Default: current directory.",
    )
    scan.add_argument(
        "--format",
        choices=["md", "json"],
        default="md",
        help="Output format. Default: md",
    )
    scan.add_argument(
        "--include-self",
        action="store_true",
        help="Include ai_guard internal sources in scan (off by default).",
    )
    scan.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit with code 1 if any findings are found.",
    )

    return p


def cmd_scan(paths: Iterable[str], fmt: str, include_self: bool, fail_on_findings: bool) -> int:
    findings = scan_paths(paths, DEFAULT_RULES, include_self=include_self)

    if fmt == "md":
        print(to_markdown(findings))
    else:
        payload = {
            "findings_count": len(findings),
            "findings": [_finding_to_dict(f) for f in findings],
        }
        print(json.dumps(payload, indent=2))

    if fail_on_findings and len(findings) > 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        code = cmd_scan(
            paths=args.paths,
            fmt=args.format,
            include_self=args.include_self,
            fail_on_findings=args.fail_on_findings,
        )
        raise SystemExit(code)

    raise SystemExit(2)
