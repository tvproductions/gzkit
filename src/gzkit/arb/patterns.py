"""Extract anti-patterns from ARB receipts for operator guidance tables.

Aggregates recurring lint failures and maps them to actionable agent guidance.
The output is formatted as Markdown table rows suitable for guidance
documents.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.arb.paths import receipts_root
from gzkit.arb.ruff_reporter import SCHEMA_ID as LINT_SCHEMA_ID

# Map ruff rules to agent-actionable guidance.
# Key: rule code (or prefix), Value: (anti-pattern description, correct approach)
RULE_GUIDANCE: dict[str, tuple[str, str]] = {
    "BLE001": (
        "Catching blind `Exception`",
        "Catch specific exceptions (e.g., `ValueError`, `OSError`)",
    ),
    "D417": (
        "Missing argument descriptions in docstrings",
        "Document all Args in PEP 257 style: `arg_name: Description.`",
    ),
    "D301": (
        "Backslashes in docstrings without raw string",
        'Use `r"""` for docstrings containing backslashes',
    ),
    "E402": (
        "Module-level import not at top of file",
        "Move imports to top; use `if TYPE_CHECKING:` for type-only imports",
    ),
    "F821": (
        "Undefined name (variable not defined)",
        "Define variables before use; check spelling and scope",
    ),
    "F841": (
        "Local variable assigned but never used",
        "Remove unused variables or prefix with `_` if intentionally unused",
    ),
    "I001": (
        "Import order incorrect",
        "Run `ruff check --fix` or use isort; stdlib -> third-party -> local",
    ),
    "UP": (
        "Using outdated Python syntax",
        "Use modern syntax (f-strings, `|` for unions, etc.)",
    ),
    "SIM": (
        "Overly complex expression",
        "Simplify: use ternary, walrus operator, or early returns",
    ),
    "PERF": (
        "Performance anti-pattern",
        "Use generators, avoid repeated lookups, prefer comprehensions",
    ),
    "COM812": (
        "Missing trailing comma in multi-line",
        "Add trailing commas in multi-line lists/dicts/args",
    ),
    "invalid-syntax": (
        "Produced unparseable Python code",
        "Validate syntax before committing; smaller incremental changes",
    ),
    "E501": (
        "Line too long",
        "Break long lines; use parentheses for implicit continuation",
    ),
    "F401": (
        "Unused import",
        "Remove unused imports or use `if TYPE_CHECKING:` for type-only",
    ),
}


class PatternCandidate(BaseModel):
    """A candidate anti-pattern derived from ARB findings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule: str = Field(..., description="Ruff rule code")
    count: int = Field(..., description="Number of occurrences across receipts")
    anti_pattern: str = Field(..., description="Human-readable anti-pattern label")
    correct_approach: str = Field(..., description="Recommended correct approach")
    sample_paths: list[str] = Field(
        default_factory=list, description="Sample file paths where the rule triggered"
    )


class PatternReport(BaseModel):
    """Aggregated pattern candidates from ARB receipts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scanned_receipts: int = Field(..., description="Receipts inspected")
    total_findings: int = Field(..., description="Total lint findings aggregated")
    candidates: list[PatternCandidate] = Field(default_factory=list)


def _iter_receipt_paths(root: Path, *, limit: int) -> list[Path]:
    paths = sorted(root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if limit < 0:
        return paths
    return paths[:limit]


def _get_guidance(rule: str) -> tuple[str, str]:
    """Return guidance for a rule, preferring exact match then prefix."""
    if rule in RULE_GUIDANCE:
        return RULE_GUIDANCE[rule]
    for prefix in ("UP", "SIM", "PERF", "COM"):
        if rule.startswith(prefix) and prefix in RULE_GUIDANCE:
            return RULE_GUIDANCE[prefix]
    return (f"Ruff rule {rule} violation", "See ruff documentation for guidance")


def collect_patterns(
    *,
    limit: int = 500,
    root: Path | None = None,
) -> PatternReport:
    """Collect anti-patterns from ARB lint receipts."""
    receipts_dir = root or receipts_root()
    rule_counts: Counter[str] = Counter()
    rule_paths: dict[str, list[str]] = {}
    scanned = 0
    total_findings = 0

    for receipt_path in _iter_receipt_paths(receipts_dir, limit=limit):
        try:
            payload: Any = json.loads(receipt_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("schema") != LINT_SCHEMA_ID:
            continue
        scanned += 1

        findings = payload.get("findings")
        if not isinstance(findings, list):
            continue

        for item in findings:
            if not isinstance(item, dict):
                continue
            rule = item.get("rule")
            path = item.get("path")
            if isinstance(rule, str) and rule:
                rule_counts[rule] += 1
                total_findings += 1
                if isinstance(path, str) and path:
                    samples = rule_paths.setdefault(rule, [])
                    if len(samples) < 3 and path not in samples:
                        samples.append(path)

    candidates: list[PatternCandidate] = []
    for rule, count in rule_counts.most_common(20):
        if count < 2:
            continue
        anti_pattern, correct = _get_guidance(rule)
        candidates.append(
            PatternCandidate(
                rule=rule,
                count=count,
                anti_pattern=anti_pattern,
                correct_approach=correct,
                sample_paths=rule_paths.get(rule, []),
            )
        )

    return PatternReport(
        scanned_receipts=scanned,
        total_findings=total_findings,
        candidates=candidates,
    )


def render_patterns_markdown(report: PatternReport) -> str:
    """Render a pattern report as Markdown for guidance documents."""
    lines: list[str] = []
    lines.append("# ARB Pattern Extraction Report")
    lines.append("")
    lines.append(f"**Receipts scanned:** {report.scanned_receipts}")
    lines.append(f"**Total findings:** {report.total_findings}")
    lines.append("")

    if not report.candidates:
        lines.append("No recurring patterns found (all rules had <2 occurrences).")
        return "\n".join(lines) + "\n"

    lines.append("## Candidate Anti-Patterns")
    lines.append("")
    lines.append("| Anti-pattern | Correct approach | Occurrences |")
    lines.append("|--------------|------------------|-------------|")
    for c in report.candidates:
        lines.append(f"| {c.anti_pattern} | {c.correct_approach} | {c.count} |")

    lines.append("")
    lines.append("## Sample Paths by Rule")
    lines.append("")
    for c in report.candidates:
        if c.sample_paths:
            lines.append(f"### {c.rule} ({c.count}x)")
            for p in c.sample_paths:
                lines.append(f"- `{p}`")
            lines.append("")

    return "\n".join(lines) + "\n"


def render_patterns_compact(report: PatternReport) -> str:
    """Render a compact single-line summary for quick review."""
    if not report.candidates:
        return (
            f"arb patterns: scanned={report.scanned_receipts} "
            f"findings={report.total_findings} candidates=0\n"
        )

    top3 = ", ".join(f"{c.rule}({c.count})" for c in report.candidates[:3])
    return (
        f"arb patterns: scanned={report.scanned_receipts} findings={report.total_findings} "
        f"candidates={len(report.candidates)} top=[{top3}]\n"
    )


__all__ = [
    "PatternCandidate",
    "PatternReport",
    "RULE_GUIDANCE",
    "collect_patterns",
    "render_patterns_compact",
    "render_patterns_markdown",
]
