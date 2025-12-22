from __future__ import annotations

from collections import defaultdict

from ai_guard.rules.base import Finding


def to_markdown(findings: list[Finding]) -> str:
    if not findings:
        return "# AI Guard Report\n\n✅ No findings.\n"

    by_file: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        by_file[f.file_path].append(f)

    lines: list[str] = []
    lines.append("# AI Guard Report")
    lines.append("")
    lines.append(f"Findings: **{len(findings)}**")
    lines.append("")

    for file_path in sorted(by_file.keys()):
        lines.append(f"## {file_path}")
        lines.append("")
        for f in sorted(by_file[file_path], key=lambda x: (x.severity.value, x.line or 0)):
            loc = f"line {f.line}" if f.line else "line ?"
            lines.append(f"- **[{f.severity.value.upper()}] {f.rule_id}** ({loc}) — {f.message}")
        lines.append("")

    return "\n".join(lines)
