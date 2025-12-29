from __future__ import annotations

from pathlib import Path

from ai_guard.rules import DEFAULT_RULES
from ai_guard.scanner import scan_paths

PAYLOAD = "e" + "val" + "('1+1')\n"

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_exclude_globs_skips_fixtures_cross_platform(tmp_path: Path) -> None:
    # Build a small tree:
    # repo/
    #   src/app.py              (clean)
    #   tests/fixtures/bad.py   (has eval -> should be ignored by exclude)
    root = tmp_path

    _write(root / "src" / "app.py", "print('ok')\n")
    _write(root / "tests" / "fixtures" / "bad.py", PAYLOAD)

    findings = scan_paths(
        [str(root)],
        DEFAULT_RULES,
        include_self=False,
        exclude=["tests/fixtures/**"],
    )

    # If exclude works, we should see zero findings
    assert findings == []


def test_exclude_globs_does_not_skip_other_tests(tmp_path: Path) -> None:
    root = tmp_path

    _write(root / "src" / "app.py", "print('ok')\n")
    _write(root / "tests" / "not_fixtures.py", PAYLOAD)

    findings = scan_paths(
        [str(root)],
        DEFAULT_RULES,
        include_self=False,
        exclude=["tests/fixtures/**"],
    )

    # This one should still be reported (not under tests/fixtures)
    assert len(findings) >= 1
