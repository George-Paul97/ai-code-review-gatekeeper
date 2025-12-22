from __future__ import annotations

import re

from ai_guard.rules.base import Finding, Severity


class PythonSecurityRule:
    rule_id = "PYSEC001"
    title = "Potentially unsafe Python patterns"

    _PATTERNS = [
        (re.compile(r"\beval\s*\("), "Use of eval() can lead to code injection."),
        (re.compile(r"\bexec\s*\("), "Use of exec() can lead to code injection."),
        (
            re.compile(r"subprocess\.(run|Popen)\s*\(.*shell\s*=\s*True", re.DOTALL),
            "subprocess with shell=True may allow command injection.",
        ),
        (re.compile(r"\bpickle\.loads\s*\("), "pickle.loads() on untrusted data is unsafe."),
    ]

    def run(self, file_path: str, content: str) -> list[Finding]:
        # Only run on .py files (keep it simple)
        if not file_path.lower().endswith(".py"):
            return []

        findings: list[Finding] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            for pattern, msg in self._PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            rule_id=self.rule_id,
                            title=self.title,
                            message=msg,
                            severity=Severity.HIGH,
                            file_path=file_path,
                            line=idx,
                        )
                    )
        return findings
