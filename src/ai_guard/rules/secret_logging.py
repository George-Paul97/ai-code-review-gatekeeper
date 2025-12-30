from __future__ import annotations

from ai_guard.rules.base import Finding, Severity


class SecretLoggingRule:
    rule_id = "SECLOG001"
    title = "Potential secret leakage in logs"

    _KEYWORDS = ("password", "passwd", "token", "secret", "api_key", "apikey", "authorization")
    _LOG_FUNCS = ("print", "logger.", "console.", "log.", "logging.")

    def run(self, file_path: str, content: str) -> list[Finding]:
        # apply to common text/code files
        extensions = (".py", ".js", ".ts", ".php", ".go", ".rb")
        if not any(file_path.lower().endswith(ext) for ext in extensions):
            return []


        findings: list[Finding] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            low = line.lower()
            if any(lf in low for lf in self._LOG_FUNCS) and any(k in low for k in self._KEYWORDS):
                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title=self.title,
                        message=(
                            "Logging line appears to include secret-related keyword; "
                            "verify no sensitive data is logged."
                        ),
                        severity=Severity.MEDIUM,
                        file_path=file_path,
                        line=idx,
                    )
                )

        return findings
