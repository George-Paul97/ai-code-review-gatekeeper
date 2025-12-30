from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
import tomllib
from collections.abc import Iterable
from pathlib import Path

from ai_guard.report.markdown import to_markdown
from ai_guard.rules import DEFAULT_RULES
from ai_guard.scanner import scan_paths


def _finding_to_dict(f) -> dict:
    """Serialize Finding objects without assuming exact field names."""
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
    return {**data, **normalized}

def _get_version() -> str:
    try:
        return importlib.metadata.version("ai-guard")
    except Exception:
        return "dev"

def load_config(path: str | None) -> dict:
    if not path:
        return {}

    p = Path(path)
    if not p.exists() or not p.is_file():
        return {}

    try:
        data = tomllib.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ai-guard",
        description="AI Guard — lightweight code review gatekeeper for security & quality checks.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {_get_version()}")

    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan paths and print a report.")
    scan.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Paths to scan (files or directories).",
    )

    scan.add_argument("--format", choices=["md", "json"], default="md", help="Output format.")
    scan.add_argument("--include-self", action="store_true", help="Include ai_guard sources too.")
    scan.add_argument("--fail-on-findings", action="store_true", help="Exit 1 if findings exist.")
    scan.add_argument(
        "--config",
        default="ai-guard.toml",
        help="Path to ai-guard.toml config file (default: ai-guard.toml if present).",
    )

    return p


def cmd_scan(
    paths: Iterable[str],
    fmt: str,
    include_self: bool,
    fail_on_findings: bool,
    config_path: str,
) -> int:
    cfg = load_config(config_path)

    try:
        exclude = cfg.get("scan", {}).get("exclude", []) or []
    except Exception:
        exclude = []

    findings = scan_paths(paths, DEFAULT_RULES, include_self=include_self, exclude=exclude)

    if fmt == "md":
        print(to_markdown(findings))
    else:
        payload = {
            "findings_count": len(findings),
            "findings": [_finding_to_dict(f) for f in findings],
        }
        print(json.dumps(payload, indent=2))

    return 1 if (fail_on_findings and len(findings) > 0) else 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    argv_effective = argv if argv is not None else sys.argv[1:]
    user_provided_format = "--format" in argv_effective
    fmt = args.format

    if not user_provided_format:
        cfg = load_config(args.config)
        cfg_fmt = (cfg.get("output", {}) or {}).get("default_format")
        if cfg_fmt in ("md", "json"):
            fmt = cfg_fmt

    if args.command == "scan":
        return cmd_scan(
            paths=args.paths,
            fmt=fmt,
            include_self=args.include_self,
            fail_on_findings=args.fail_on_findings,
            config_path=args.config,
        )

    return 2
