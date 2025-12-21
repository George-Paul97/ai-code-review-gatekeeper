from __future__ import annotations
from pathlib import Path
from typing import Iterable

from ai_guard.rules.base import Finding, Rule


def scan_paths(paths: Iterable[str], rules: list[Rule]) -> list[Finding]:
    findings: list[Finding] = []

    for p in paths:
        path = Path(p)
        if path.is_dir():
            for file in path.rglob("*"):
                if file.is_file():
                    findings.extend(_scan_file(file, rules))
        elif path.is_file():
            findings.extend(_scan_file(path, rules))

    return findings


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
