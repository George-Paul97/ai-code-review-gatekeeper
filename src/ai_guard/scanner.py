from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path, PurePosixPath

from ai_guard.rules.base import Finding, Rule


def _norm_posix(path_str: str) -> str:
    s = path_str.replace("\\", "/")
    if s.startswith("./"):
        s = s[2:]
    return s


def _is_excluded(rel_posix: str, exclude: list[str]) -> bool:
    rp = _norm_posix(rel_posix)
    p = PurePosixPath(rp)

    for pat in exclude:
        pat_n = _norm_posix(pat)

        # Treat trailing "/" as "prefix folder"
        if pat_n.endswith("/"):
            if rp.startswith(pat_n):
                return True
            continue

        # PurePosixPath.match supports ** globs
        if p.match(pat_n):
            return True

    return False


def scan_paths(
    paths: Iterable[str],
    rules: list[Rule],
    *,
    include_self: bool = False,
    exclude: list[str] | None = None,
) -> list[Finding]:
    exclude = exclude or []
    findings: list[Finding] = []
    cwd = Path.cwd()

    for p in paths:
        path = Path(p)

        if path.is_dir():
            for file in path.rglob("*"):
                if not file.is_file():
                    continue

                # make a stable relative path for matching
                try:
                    rel = file.resolve().relative_to(cwd.resolve()).as_posix()
                except Exception:
                    rel = file.as_posix()
                rel = _norm_posix(rel)

                if _is_excluded(rel, exclude):
                    continue

                if not include_self and rel.startswith("src/ai_guard/"):
                    continue

                findings.extend(_scan_file(file, rules))

        elif path.is_file():
            try:
                rel = path.resolve().relative_to(cwd.resolve()).as_posix()
            except Exception:
                rel = path.as_posix()
            rel = _norm_posix(rel)

            if _is_excluded(rel, exclude):
                continue

            if not include_self and rel.startswith("src/ai_guard/"):
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
