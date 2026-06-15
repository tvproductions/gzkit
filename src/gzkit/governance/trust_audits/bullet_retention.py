"""Bullet-retention validator — ADR-0.0.33 Invariant 1 (tier-scoped).

Reads ``docs/governance/advisory-rules-audit.md``, extracts every bullet
classified **Mechanical** or **Promotable**, and enforces retention
**tier-aware** per the ADR-0.0.33 § Amendment (2026-06-03), realized by
OBPI-0.0.37-25:

* **Invariant tier** (``CorpusEntry.tier == "invariant"``, and the conservative
  fallback for any bullet that maps to no corpus entry): the Era-1 verbatim
  contract is preserved — the bullet's normalized text MUST appear as a
  substring in the per-turn surface corpus (``AGENTS.md``, ``CLAUDE.md``,
  ``.claude/rules/**``). Absence is a fail-closed ``ValidationError``.
* **Compressible tier** (``CorpusEntry.tier == "compressible"``): retention is
  satisfied not by verbatim substring but by a present, valid advisor-QC
  information-retention witness for the entry's committed rendition — the latest
  ``rendition_advisor_verdict`` ledger event for the surface, whose
  ``arb-step-judge-*`` receipt exists and carries ``exit_status == 0`` (the
  receipt the operator cites at Gate 5; ADR-0.0.39, OBPI-0.0.37-24). A reworded
  or combined compressible entry that carries the witness MUST NOT fail; one
  without a valid witness fails closed (retention is unwitnessed). The invariant
  preserved is *no binding information is lost* (witnessed by receipt +
  attestation), never *every byte identical*.

Returns a ``ValidationError(type="bullet_retention")`` for every retention
violation. An empty list means the surface is clean.

Era-2 forward compatibility: the function signature
``validate_bullet_retention(project_root: Path) -> list[ValidationError]``
matches the ``trust_audits`` package pattern established by
``validate_advisor_proof_binding`` so the Era-2 Pydantic-content-model upgrade
(per ADR-0.0.34) can replace the substring check without rewriting the
registration.
"""

from __future__ import annotations

import contextlib
import json
import re
from pathlib import Path

from gzkit.arb.paths import receipts_root
from gzkit.content.corpus_store import load_corpus
from gzkit.content.models.corpus import CorpusEntry
from gzkit.core.validation_rules import ValidationError
from gzkit.ledger import Ledger

_SCORECARD_PATH = Path("docs") / "governance" / "advisory-rules-audit.md"
_SURFACE_FILES = ("AGENTS.md", "CLAUDE.md")
_RULES_GLOB = ".claude/rules/**/*.md"
_CORPUS_DIR = Path(".gzkit") / "corpus"
_LEDGER_PATH = Path(".gzkit") / "ledger.jsonl"
_ADVISOR_VERDICT_EVENT = "rendition_advisor_verdict"
# Canonical advisor-QC receipt id prefix (``arb-step-judge-<32hex>``); the
# compressible witness only honors a receipt of this shape (ADR-0.0.39 /
# OBPI-0.0.37-24 — the step name ``judge`` binds the canonical receipt-id regex).
_JUDGE_RECEIPT_PREFIX = "arb-step-judge-"

_ENFORCED_CLASSES = frozenset({"mechanical", "promotable"})

# Match a scorecard table row: | number | rule text | **Classification** | notes |
# The classification cell is mandatory; the notes cell is optional.
_TABLE_ROW_RE = re.compile(
    r"^\|\s*[^|]+\s*\|\s*(?P<rule>[^|]+?)\s*\|\s*\*\*(?P<cls>[^*]+)\*\*\s*\|"
)


def validate_bullet_retention(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for enforced bullets whose tier-scoped retention fails."""
    scorecard = project_root / _SCORECARD_PATH
    if not scorecard.exists():
        return []

    bullets = _parse_scorecard(scorecard)
    if not bullets:
        return []

    normalized_corpus = _normalize(_collect_surface_corpus(project_root))
    entries = _load_corpus_entries(project_root)

    errors: list[ValidationError] = []
    for rule_text, classification in bullets:
        if not _is_enforced(classification):
            continue
        normalized_rule = _normalize(rule_text)
        if not normalized_rule:
            continue
        tier, surface = _resolve_tier(normalized_rule, entries)
        if tier == "compressible":
            if not _retention_witnessed(project_root, surface):
                errors.append(_compressible_unwitnessed_error(rule_text, classification, surface))
            continue
        # Invariant tier (and the conservative unknown-tier fallback): verbatim.
        if normalized_rule not in normalized_corpus:
            errors.append(_invariant_absent_error(rule_text, classification))
    return errors


def _invariant_absent_error(rule_text: str, classification: str) -> ValidationError:
    """Build the fail-closed error for an invariant-tier bullet absent from the surface."""
    return ValidationError(
        type="bullet_retention",
        artifact=_SCORECARD_PATH.as_posix(),
        message=(
            f"Bullet-retention violation: invariant-tier {classification!r} bullet "
            f"not found verbatim in per-turn surface.\n"
            f"  Bullet: {rule_text!r}\n"
            f"  Why: ADR-0.0.33 Invariant 1 requires invariant-tier content to render "
            f"verbatim at every setpoint (tier-scoped amendment 2026-06-03).\n"
            f"  Fix: restore the bullet text verbatim to AGENTS.md/CLAUDE.md/.claude/rules, "
            f"or re-classify it compressible in the corpus and record an advisor-QC verdict.\n"
            f"  Source: {_SCORECARD_PATH.as_posix()}"
        ),
    )


def _compressible_unwitnessed_error(
    rule_text: str, classification: str, surface: str | None
) -> ValidationError:
    """Build the fail-closed error for a compressible-tier bullet lacking a valid witness."""
    surface_label = surface if surface is not None else "(unknown surface)"
    return ValidationError(
        type="bullet_retention",
        artifact=_SCORECARD_PATH.as_posix(),
        message=(
            f"Bullet-retention violation: compressible-tier {classification!r} bullet "
            f"retention is unwitnessed for surface {surface_label!r}.\n"
            f"  Bullet: {rule_text!r}\n"
            f"  Why: ADR-0.0.33 Invariant 1 (tier-scoped) requires compressible-tier "
            f"retention to be witnessed by a valid advisor-QC receipt "
            f"(arb-step-judge-*, exit_status 0) + operator attestation — the compressible "
            f"tier is not an unconditional escape from retention.\n"
            f"  Fix: run `uv run gz content advise-rendition {surface_label} "
            f'--score <0.0-1.0> --explanation "<reasoning>"` to record the verdict, '
            f"then cite the receipt in the operator's Gate-5 attestation.\n"
            f"  Source: {_SCORECARD_PATH.as_posix()}"
        ),
    )


def _parse_scorecard(path: Path) -> list[tuple[str, str]]:
    """Parse advisory-rules-audit.md and return (rule_text, classification) pairs."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []

    results: list[tuple[str, str]] = []
    for line in content.splitlines():
        m = _TABLE_ROW_RE.match(line.strip())
        if m is None:
            continue
        rule_text = m.group("rule").strip()
        classification = m.group("cls").strip()
        # Skip header rows (rule text is literally "Rule" or similar)
        if rule_text.lower() in {"rule", "#", "score", "notes"}:
            continue
        results.append((rule_text, classification))
    return results


def _collect_surface_corpus(project_root: Path) -> str:
    """Concatenate AGENTS.md, CLAUDE.md, and .claude/rules/**/*.md into one string."""
    parts: list[str] = []
    for name in _SURFACE_FILES:
        path = project_root / name
        if path.exists():
            with contextlib.suppress(OSError):
                parts.append(path.read_text(encoding="utf-8"))

    rules_root = project_root / ".claude" / "rules"
    if rules_root.exists():
        for rule_path in sorted(rules_root.rglob("*.md")):
            with contextlib.suppress(OSError):
                parts.append(rule_path.read_text(encoding="utf-8"))

    return "\n".join(parts)


def _normalize(text: str) -> str:
    """Strip bullet markers and collapse whitespace for substring matching."""
    # Strip leading markdown bullet markers: -, *, digits followed by .
    text = re.sub(r"^[\s\-\*]+", "", text.strip())
    text = re.sub(r"^\d+\.\s*", "", text)
    # Collapse runs of whitespace to a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _is_enforced(classification: str) -> bool:
    """Return True when the classification is Mechanical or Promotable."""
    return classification.strip().lower() in _ENFORCED_CLASSES


def _load_corpus_entries(project_root: Path) -> list[CorpusEntry]:
    """Load every corpus entry across all per-surface stores under ``.gzkit/corpus/``.

    The surface name is the store filename stem (e.g. ``AGENTS.md.jsonl`` →
    surface ``AGENTS.md``). Returns an empty list when no corpus store exists —
    every enforced bullet then maps to the conservative invariant fallback.
    """
    corpus_root = project_root / _CORPUS_DIR
    if not corpus_root.is_dir():
        return []
    entries: list[CorpusEntry] = []
    for store_path in sorted(corpus_root.glob("*.jsonl")):
        surface = store_path.name[: -len(".jsonl")]
        with contextlib.suppress(OSError, ValueError):
            entries.extend(load_corpus(project_root, surface).entries)
    return entries


def _resolve_tier(normalized_rule: str, entries: list[CorpusEntry]) -> tuple[str, str | None]:
    """Resolve an enforced bullet's tier from the corpus store.

    A bullet maps to the first corpus entry whose normalized text contains the
    bullet's normalized text — the entry is the source-of-truth row the bullet
    was rendered from. Returns ``(entry.tier, entry.surface)``.

    When the bullet maps to no corpus entry (tier unknown), the conservative
    fallback is ``("invariant", None)`` — preserving the Era-1 verbatim contract
    so an un-classified bullet is never silently waived (booked decision,
    2026-06-14).
    """
    for entry in entries:
        if normalized_rule in _normalize(entry.text):
            return entry.tier, entry.surface
    return "invariant", None


def _retention_witnessed(project_root: Path, surface: str | None) -> bool:
    """Return True when *surface* carries a valid advisor-QC retention witness.

    The witness is the latest ``rendition_advisor_verdict`` ledger event for the
    surface (surface-level granularity, booked 2026-06-14): its ``receipt_id``
    must carry the canonical ``arb-step-judge-`` prefix AND resolve to a receipt
    that exists and carries ``exit_status == 0``. Absence of the event, a
    non-canonical receipt id, a missing receipt, or a non-zero ``exit_status``
    means retention is unwitnessed.
    """
    if surface is None:
        return False
    receipt_id = _latest_verdict_receipt_id(project_root, surface)
    if receipt_id is None or not receipt_id.startswith(_JUDGE_RECEIPT_PREFIX):
        return False
    return _receipt_exit_status_ok(project_root, receipt_id)


def _latest_verdict_receipt_id(project_root: Path, surface: str) -> str | None:
    """Return the receipt_id of the latest advisor-QC verdict for *surface*, or None."""
    ledger = Ledger(project_root / _LEDGER_PATH)
    if not ledger.exists():
        return None
    receipt_id: str | None = None
    for event in ledger.read_all():
        if event.event != _ADVISOR_VERDICT_EVENT:
            continue
        if event.extra.get("surface") != surface:
            continue
        candidate = event.extra.get("receipt_id")
        if isinstance(candidate, str) and candidate:
            receipt_id = candidate
    return receipt_id


def _receipt_exit_status_ok(project_root: Path, receipt_id: str) -> bool:
    """Return True when the named receipt file exists and carries ``exit_status == 0``."""
    receipt_file = receipts_root(project_root=project_root) / f"{receipt_id}.json"
    if not receipt_file.is_file():
        return False
    try:
        receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return receipt.get("exit_status") == 0
