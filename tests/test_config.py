from __future__ import annotations

from pathlib import Path

from ai_guard.cli import load_config


def test_load_config_missing_file_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.toml"
    cfg = load_config(str(missing))
    assert cfg == {}


def test_load_config_none_returns_empty() -> None:
    cfg = load_config(None)
    assert cfg == {}


def test_load_config_parses_scan_exclude_and_output_default_format(tmp_path: Path) -> None:
    p = tmp_path / "ai-guard.toml"
    p.write_text(
        """
[scan]
exclude = [
  ".venv/",
  "tests/fixtures/**",
]

[output]
default_format = "json"
""".strip(),
        encoding="utf-8",
    )

    cfg = load_config(str(p))

    assert isinstance(cfg, dict)
    assert cfg["scan"]["exclude"] == [".venv/", "tests/fixtures/**"]
    assert cfg["output"]["default_format"] == "json"
