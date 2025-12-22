from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ai_guard.rules.base import Finding, Rule

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}


def scan_paths(paths: Iterable[str], rules: list[Rule], include_self: bool = False) -> list[Finding]:
    findings: list[Finding] = []

    for p in paths:
        path = Path(p)

        if path.is_dir():
            for file in path.rglob("*"):
                if file.is_file() and not _should_skip(file, include_self=include_self):
                    findings.extend(_scan_file(file, rules))
        elif path.is_file():
            if not _should_skip(path, include_self=include_self):
                findings.extend(_scan_file(path, rules))

    return findings


def _should_skip(file: Path, include_self: bool) -> bool:
    parts = set(file.parts)

    # skip common junk dirs
    if parts & DEFAULT_EXCLUDE_DIRS:
        return True

    # avoid scanning this tool's own code by default (prevents self-matching)
    if not include_self:
        # matches .../src/ai_guard/...
        if "src" in parts and "ai_guard" in parts:
            return True

    return False


def _scan_file(file: Path, rules: list[Rule]) -> list[Finding]:
    # skip binaries / very large files quickly
    try:
        content = file.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    results: list[Finding] = []
    for rule in rules:
        results.extend(rule.run(str(file), content))
    return results
