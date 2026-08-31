"""Validator for the Rule Version Marker Invariant.

`.gzkit/rules/skill-surface-sync.md` § Non-negotiable rules #2 declares the
body-level ``<!-- rule-version: X.Y.Z -->`` marker binding on every canonical
rule, alongside a visible ``> **Rule version:** `X.Y.Z`` block quote carrying a
rationale. Nothing enforced it: four rules shipped with no marker at all, and
three of those four (``adr-audit.md``, ``cli.md``, ``pythonic.md``) were among
the worst-drifted files found by the Pass A conflict-matrix re-run of
2026-07-16. A declared invariant with no mechanical arm is the failure class
that audit named throughout — prose asserting a discipline nothing checks.

Two violations are detected:

``missing-marker``
    No ``<!-- rule-version: X.Y.Z -->`` comment in the body.
``marker-blockquote-drift``
    The HTML marker and the visible block quote name different versions. Both
    are required by the same clause, and `skill-surface-sync.md`
    § Conflict resolution keys on version equality — a bump applied to one and
    not the other reintroduces the ambiguity the marker exists to remove.

Read-only by contract — never writes files, never invokes shell=True, never
calls an LLM, never reads outside ``.gzkit/rules/*.md``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

from gzkit.rules import NESTED_SURFACE_NAMES

if TYPE_CHECKING:
    from gzkit.core.validation_rules import ValidationError

# The package-internal agent contract is a generated concatenation, not an
# authored rule; skill-surface-sync excludes it from rule scaffolding.
#: Generated per-subtree surfaces are not rules and carry no rule-version
#: marker. Sourced from ``gzkit.rules`` so this scanner and the rule loader
#: cannot disagree about what counts as a rule file (GHI #923).
_EXEMPT_FILENAMES = NESTED_SURFACE_NAMES

_MARKER_RE = re.compile(r"<!--\s*rule-version:\s*(\d+\.\d+\.\d+)\s*-->")
_BLOCKQUOTE_RE = re.compile(r">\s*\*\*Rule version:\*\*\s*`(\d+\.\d+\.\d+)`")


class MarkerViolation(BaseModel):
    """A canonical rule that failed the version-marker invariant."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file: str
    reason: Literal["missing-marker", "marker-blockquote-drift"]
    marker_version: str | None = None
    blockquote_version: str | None = None


class RuleVersionMarkersResult(BaseModel):
    """Aggregate result of one `--rule-version-markers` scope run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scope: str = "rule-version-markers"
    result: Literal["pass", "fail"]
    violations: list[MarkerViolation]
    canonical_root: str
    files_checked: int
    exit_code: int


def rule_version_of(body: str) -> str | None:
    """Return the ``<!-- rule-version: X.Y.Z -->`` version in *body*, if any.

    The single reader of the marker grammar. Other scopes that key on a rule's
    version (``advisory_scorecard``'s Coverage Ledger, GHI #754) call this
    rather than restating the regex — a second copy is how two readers of one
    convention drift apart.
    """
    match = _MARKER_RE.search(body)
    return match.group(1) if match else None


def canonical_rule_files(rules_root: Path) -> list[Path]:
    """Return the authored rule files under ``rules_root``, sorted."""
    if not rules_root.is_dir():
        return []
    return sorted(p for p in rules_root.glob("*.md") if p.name not in _EXEMPT_FILENAMES)


def audit_rule_version_markers(project_root: Path) -> list[MarkerViolation]:
    """Return every canonical rule violating the version-marker invariant."""
    rules_root = project_root / ".gzkit" / "rules"
    violations: list[MarkerViolation] = []
    for path in canonical_rule_files(rules_root):
        body = path.read_text(encoding="utf-8", errors="replace")
        marker = _MARKER_RE.search(body)
        if marker is None:
            violations.append(MarkerViolation(file=path.name, reason="missing-marker"))
            continue
        quote = _BLOCKQUOTE_RE.search(body)
        if quote is None:
            violations.append(
                MarkerViolation(
                    file=path.name,
                    reason="marker-blockquote-drift",
                    marker_version=marker.group(1),
                    blockquote_version=None,
                )
            )
            continue
        if marker.group(1) != quote.group(1):
            violations.append(
                MarkerViolation(
                    file=path.name,
                    reason="marker-blockquote-drift",
                    marker_version=marker.group(1),
                    blockquote_version=quote.group(1),
                )
            )
    return violations


def run_rule_version_markers(project_root: Path) -> RuleVersionMarkersResult:
    """Run the scope and return its structured result."""
    rules_root = project_root / ".gzkit" / "rules"
    files = canonical_rule_files(rules_root)
    violations = audit_rule_version_markers(project_root)
    return RuleVersionMarkersResult(
        result="fail" if violations else "pass",
        violations=violations,
        canonical_root=rules_root.as_posix(),
        files_checked=len(files),
        exit_code=3 if violations else 0,
    )


def audit_rule_version_markers_errors(project_root: Path) -> list[ValidationError]:
    """Registry-shaped adapter: return violations as ``ValidationError``.

    ``VALIDATOR_REGISTRY`` entries answer to
    ``Callable[[Path, str | None], list[ValidationError]]``; the structured
    ``MarkerViolation`` model above stays the validator's own vocabulary.
    """
    from gzkit.core.validation_rules import ValidationError  # noqa: PLC0415

    return [
        ValidationError(
            type="surface",
            artifact=f".gzkit/rules/{v.file}",
            message=format_violation(v),
            field="rule-version",
        )
        for v in audit_rule_version_markers(project_root)
    ]


def format_violation(violation: MarkerViolation) -> str:
    """Return a one-line operator-facing message for ``violation``."""
    if violation.reason == "missing-marker":
        return (
            f".gzkit/rules/{violation.file}: no `<!-- rule-version: X.Y.Z -->` marker "
            "(skill-surface-sync.md § Non-negotiable rules #2)"
        )
    if violation.blockquote_version is None:
        return (
            f".gzkit/rules/{violation.file}: marker={violation.marker_version} but no visible "
            "`> **Rule version:**` block quote"
        )
    return (
        f".gzkit/rules/{violation.file}: marker={violation.marker_version} disagrees with "
        f"block quote={violation.blockquote_version}"
    )
