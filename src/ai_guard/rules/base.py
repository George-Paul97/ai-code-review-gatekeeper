from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    message: str
    severity: Severity
    file_path: str
    line: int | None = None


class Rule(Protocol):
    rule_id: str
    title: str

    def run(self, file_path: str, content: str) -> list[Finding]:
        ...
