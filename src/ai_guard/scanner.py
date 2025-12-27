from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ai_guard.rules.base import Finding, Rule


def _normalize_pattern(p: str) -> str:
    # normalize Windows paths to forward slashes + strip leading ./ and trailing /
    p = p.replace("\\", "/").strip()
    if p.startswith("./"):
        p = p[2:]
    return p.rstrip("/")


def _is_excluded(file: Path, exclude: list[str]) -> bool:
    if not exclude:
        return False

    posix = file.as_posix()
    for raw in exclude:
        pat = _normalize_pattern(raw)
        if not pat:
            continue

        # Match as a directory segment or prefix anywhere in path.
        # Examples:
        #  - ".venv/" excludes ".../.venv/Lib/site-packages/..."
        #  - "dist/" excludes ".../dist/app.js"
        if posix.startswith(pat) or f"/{pat}/" in posix or posix.endswith(f"/{pat}"):
            return True

    return False


def scan_paths(
    paths: Iterable[str],
    rules: list[Rule],
    *,
    include_self: bool = False,
    exclude: list[str] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    exclude = exclude or []

    for p in paths:
        path = Path(p)

        if path.is_dir():
            for file in path.rglob("*"):
                if not file.is_file():
                    continue

                if not include_self and "src/ai_guard" in file.as_posix().replace("\\", "/"):
                    # skip scanning our own package by default
                    continue

                if _is_excluded(file, exclude):
                    continue

                findings.extend(_scan_file(file, rules))

        elif path.is_file():
            if not include_self and "src/ai_guard" in path.as_posix().replace("\\", "/"):
                continue
            if _is_excluded(path, exclude):
                continue
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
