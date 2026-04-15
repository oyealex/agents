from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any, Literal

from agents.sanitize import sanitize_text

try:
    from langchain_core.tools import tool
except ModuleNotFoundError:

    def tool(func: Any) -> Any:
        return func


Severity = Literal["low", "medium", "high"]


@tool
def scenario_risk_tool(area: str, severity: Severity, evidence: str) -> str:
    """Create a normalized risk record for a test scenario."""
    priority = {"low": 1, "medium": 2, "high": 3}[severity]
    payload = {
        "area": sanitize_text(area),
        "severity": severity,
        "priority": priority,
        "evidence": sanitize_text(evidence),
        "recommended_action": _recommended_action(severity),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


@tool
def acceptance_matrix_tool(requirement: str, expected_signal: str, owner: str) -> str:
    """Create one acceptance-check row for a complex agent orchestration test."""
    payload = {
        "requirement": sanitize_text(requirement),
        "expected_signal": sanitize_text(expected_signal),
        "owner": sanitize_text(owner),
        "status": "to_verify",
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _recommended_action(severity: Severity) -> str:
    if severity == "high":
        return "block release until resolved"
    if severity == "medium":
        return "fix before broad testing"
    return "track as follow-up"


class ComplexTestToolProvider:
    """Registers custom tools for multi-subagent integration testing."""

    def __init__(self, label: str = "complex-subagent-test") -> None:
        self.label = sanitize_text(label)

    def tools_for_thread(self, thread_id: str) -> Iterable[Any]:
        return (scenario_risk_tool, acceptance_matrix_tool)
