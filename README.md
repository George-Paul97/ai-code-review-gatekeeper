# AI Code Review Gatekeeper (ai-guard)

A lightweight, dependency-free code scanning tool that acts as a CI “gatekeeper” for pull requests.
It flags common risky patterns (security + hygiene) and can fail the build when findings are present.

- ✅ Fast: scans only relevant files in PRs (configurable)
- ✅ Simple: no external services required
- ✅ CI-friendly: non-zero exit code on findings (`--fail-on-findings`)
- ✅ Cross-platform: works on Windows and Linux

## What it does

`ai-guard` performs a rule-based scan over source files and reports findings with:
- rule id
- severity (LOW/MEDIUM/HIGH)
- file path + line number
- short message

It’s designed to complement (not replace) human review:
you run it on PR diffs to catch obvious issues early, especially in AI-assisted code generation workflows.

## Install

Requires Python 3.11+.

### Local (editable)
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .
```

## Dev tooling (tests + lint)
```bash
python -m pip install -e ".[dev]"
```
## Usage

### Scan a directory (Markdown report)
```bash
ai-guard scan src
```

### Scan and fail if findings exist (CI mode)
```bash
ai-guard scan src --fail-on-findings
```

### JSON output (for bots / tooling)
```bash
ai-guard scan src --format json
```

### Run via Python module

#### Useful if the console script isn’t on PATH:
```bash
python -m ai_guard scan src
```

## Configuration (`ai-guard.toml`)

#### By default, `ai-guard` looks for `ai-guard.toml` in the current working directory.
#### You can also pass a custom path:
```bash
ai-guard scan . --config path/to/ai-guard.toml
```

### Example config:
```bash
# ai-guard.toml
[scan]
exclude = [
  ".venv/",
  "node_modules/",
  "dist/",
  "build/",
  ".git/",
  "tests/fixtures/**",
]

[output]
default_format = "md"
```

## Notes:

- `exclude` supports glob patterns, including `**`

- Path matching is normalized to be Windows/POSIX separator-safe

## Exit codes

- `0` — no findings (or scan completed successfully)

- `1` — findings exist and `--fail-on-findings` was used

- `2` — invalid arguments / command usage errors

This makes it suitable for CI gating.

## GitHub Actions (PR gate)

#### This repo includes a workflow that runs on pull requests:
- computes changed files in the PR diff
- runs `ai-guard scan` on those files
- posts a Markdown report in the job summary
- fails the PR when findings exist

#### If the PR doesn’t change any relevant file types, the scan is skipped.

## Development
#### Run lint + tests:
```bash
ruff check .
pytest -q
```

## Scope & limitations

#### This is intentionally a small, rule-based gatekeeper:

- It does not attempt deep static analysis

- It does not train models or run LLMs

- It aims to catch obvious “red flags” cheaply, early, and consistently