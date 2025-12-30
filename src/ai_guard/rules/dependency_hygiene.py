from __future__ import annotations

from ai_guard.rules.base import Finding, Severity


class DependencyHygieneRule:
    rule_id = "DEPS001"
    title = "Dependency version pinning hygiene"

    def run(self, file_path: str, content: str) -> list[Finding]:
        if not file_path.lower().endswith(("requirements.txt", "requirements-dev.txt")):
            return []

        findings: list[Finding] = []
        for idx, raw in enumerate(content.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            # Very simple heuristic:
            # warn if dependency has no == or ~= or >= etc.
            if all(op not in line for op in ("==", "~=", ">=", "<=", ">", "<")):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title=self.title,
                        message=(
                            "Dependency is unpinned; consider pinning versions "
                            "for reproducible builds."
                        ),
                        severity=Severity.LOW,
                        file_path=file_path,
                        line=idx,
                    )
                )

        return findings
