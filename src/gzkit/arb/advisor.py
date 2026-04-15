"""Summarize ARB receipts into actionable recommendations.

ARB's long-term value is reducing the *rate* of agent-authored defects
(first-pass failures), not generating workflow noise. This module reads recent
receipt JSON files and produces a compact report suitable for a
human-in-the-loop guardrail tuning loop.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.arb.paths import receipts_root
from gzkit.arb.ruff_reporter import SCHEMA_ID as LINT_SCHEMA_ID


class ArbAdvice(BaseModel):
    """Aggregated ARB findings and guardrail recommendations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scanned_receipts: int = Field(..., description="Total receipts inspected")
    failed_receipts: int = Field(..., description="Receipts with non-zero exit_status")
    findings_total: int = Field(..., description="Total findings across all receipts")
    top_rules: list[tuple[str, int]] = Field(default_factory=list)
    top_paths: list[tuple[str, int]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


def _iter_receipt_paths(root: Path, *, limit: int) -> list[Path]:
    paths = sorted(root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if limit < 0:
        return paths
    return paths[:limit]


def _rule_category(rule: str) -> str:
    if not rule:
        return "unknown"
    if rule.startswith(("F", "B")):
        return "correctness"
    if rule.startswith(("E", "W", "I", "UP", "COM")):
        return "style"
    if rule.startswith(("PERF", "SIM")):
        return "quality"
    return "unknown"


def _recommendations_for_counts(rule_counts: Counter[str]) -> list[str]:
    if not rule_counts:
        return ["No findings in recent receipts."]

    style = 0
    correctness = 0
    quality = 0
    for rule, count in rule_counts.items():
        cat = _rule_category(rule)
        if cat == "style":
            style += count
        elif cat == "correctness":
            correctness += count
        elif cat == "quality":
            quality += count

    total = style + correctness + quality
    if total == 0:
        return ["Findings present, but rule categories are unknown."]

    recs: list[str] = []

    if style / total >= 0.6:
        recs.append(
            "Style-dominant failures: tighten the agent loop to run "
            "`uv run ruff check . --fix && uv run ruff format .` early and often."
        )
    if correctness > 0:
        recs.append(
            "Correctness-class rules present (e.g., F*/B*): bias toward smaller diffs "
            "and add/extend unit tests around touched code paths."
        )
    if quality > 0 and style / total < 0.6:
        recs.append(
            "Quality rules present (e.g., SIM*/PERF*): consider codifying a short "
            "refactor pattern in agent instructions for recurring hotspots."
        )

    recs.append(
        "To keep ARB cheap, periodically run "
        "`uv run gz arb tidy --keep-last 200 --apply` (dry-run without `--apply`)."
    )
    return recs


def collect_arb_advice(
    *,
    limit: int = 50,
    root: Path | None = None,
) -> ArbAdvice:
    """Collect and summarize recent ARB receipts."""
    receipts_dir = root or receipts_root()
    rule_counts: Counter[str] = Counter()
    path_counts: Counter[str] = Counter()
    scanned = 0
    failed = 0
    findings_total = 0

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
        exit_status = int(payload.get("exit_status") or 0)
        if exit_status != 0:
            failed += 1

        total = payload.get("findings_total")
        if isinstance(total, int) and total >= 0:
            findings_total += total
        else:
            findings = payload.get("findings")
            if isinstance(findings, list):
                findings_total += len(findings)

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
            if isinstance(path, str) and path:
                path_counts[path] += 1

    return ArbAdvice(
        scanned_receipts=scanned,
        failed_receipts=failed,
        findings_total=findings_total,
        top_rules=rule_counts.most_common(10),
        top_paths=path_counts.most_common(10),
        recommendations=_recommendations_for_counts(rule_counts),
    )


def render_arb_advice_text(advice: ArbAdvice) -> str:
    """Render advice as a compact text report."""
    lines: list[str] = []
    lines.append("ARB Advice")
    lines.append(f"Receipts scanned: {advice.scanned_receipts}")
    lines.append(f"Failures: {advice.failed_receipts}")
    lines.append(f"Findings total (incl. truncated): {advice.findings_total}")

    if advice.top_rules:
        lines.append("")
        lines.append("Top rules:")
        for rule, count in advice.top_rules:
            lines.append(f"  - {rule}: {count}")

    if advice.top_paths:
        lines.append("")
        lines.append("Top paths:")
        for path, count in advice.top_paths:
            lines.append(f"  - {path}: {count}")

    lines.append("")
    lines.append("Recommendations:")
    for rec in advice.recommendations:
        lines.append(f"  - {rec}")

    return "\n".join(lines) + "\n"


__all__ = ["ArbAdvice", "collect_arb_advice", "render_arb_advice_text"]
