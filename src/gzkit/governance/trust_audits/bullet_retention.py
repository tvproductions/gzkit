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

**Classification reader** (ADR-0.35.0 § Decision item 9, OBPI-0.35.0-10). In a
project with section-ownership enrollment every scorecard row names its source in
the Notes column as ``source=<path>[#<section-id>] [entry=<entry-id>]`` inside one
code span. A row attributed to a corpus-owned section resolves its classification
from that ``CorpusEntry.classification``; every other row resolves from the
scorecard. Exactly one surface answers for a bullet, a broken owned mapping fails
closed instead of falling back, and a corpus/scorecard disagreement is reported
while the corpus value binds. A row attributed to a ``SKILL.md`` or an ADR file is
retention-checked against that file, not the per-turn surface (GHI #939). A
project with no enrollment and no attribution keeps the legacy audit unchanged.

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
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, NamedTuple

from pydantic import BaseModel, ConfigDict

from gzkit.advisory import emit_advisory
from gzkit.arb.paths import receipts_root
from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.models.corpus import CorpusEntry, effective_corpus
from gzkit.content.ownership import declaration_path, load_declaration
from gzkit.content.parse import section_id
from gzkit.core.validation_rules import ValidationError
from gzkit.ledger import Ledger

_SCORECARD_PATH = Path("docs") / "governance" / "advisory-rules-audit.md"
_DECISION = "ADR-0.35.0 § Decision item 9"
_RERUN = "re-run `uv run gz validate --bullet-retention`"
_OWNED = "corpus-owned"
# The value `gz content remember` wrote when no review had classified the entry.
_CAPTURE_DEFAULT = "Ambiguous"
_SECTION_HEADING = "### "
# One code span in the Notes column: `source=<path>[#<section-id>] [entry=<entry-id>]`.
_ATTRIBUTION_RE = re.compile(
    r"`source=(?P<path>[^`#\s]+)(?:#(?P<section>[^`\s]+))?(?:\s+entry=(?P<entry>[^`\s]+))?`"
)
# Sources whose own text is the retention target (GHI #939): a skill or an ADR file.
_DECLARED_SOURCE_RE = re.compile(r"^(\.gzkit/skills/[^/]+/SKILL\.md|docs/design/adr/.+\.md)$")
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
    r"^\|\s*(?P<num>[^|]+?)\s*\|\s*(?P<rule>[^|]+?)\s*\|\s*\*\*(?P<cls>[^*]+)\*\*\s*\|"
    r"(?P<notes>.*)$"
)


class AuditedBullet(BaseModel):
    """One scorecard row as the audit resolved it: who classified it, and from where.

    A read result, never a second classification store: ``classification`` is the
    value that binds, ``authority`` names the one surface it was read from, and
    ``scorecard_classification`` keeps the scorecard's own cell visible so a
    disagreement on an owned bullet can be seen rather than discarded.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    section_id: str | None
    row_number: str
    rule: str
    source: str | None
    scorecard_classification: str
    classification: str
    authority: Literal["corpus", "scorecard"]
    entry_id: str | None = None


class _Row(NamedTuple):
    """One parsed scorecard row; identity is ``(section_id, number)``."""

    section_id: str | None
    number: str
    rule: str
    classification: str
    source: str | None
    source_section: str | None
    entry_id: str | None


class _Resolved(NamedTuple):
    """A row with its binding corpus entry, or ``None`` when the scorecard answers."""

    row: _Row
    entry: CorpusEntry | None


class _Ownership(NamedTuple):
    """An enrolled surface's declared sections and its effective entries by id."""

    sections: Mapping[str, str]
    entries: Mapping[str, CorpusEntry]


def validate_bullet_retention(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for enforced bullets whose tier-scoped retention fails."""
    scorecard = project_root / _SCORECARD_PATH
    if not scorecard.exists():
        return []

    rows = _parse_scorecard(scorecard)
    if not rows:
        return []

    resolved, errors = _resolve_population(project_root, rows)
    for item in resolved:
        if item.entry is not None and _disagrees(item.entry, item.row):
            emit_advisory(_disagreement_message(item.row, item.entry))
    errors.extend(_retention_errors(project_root, resolved))
    return errors


def audited_population(project_root: Path) -> list[AuditedBullet]:
    """Return every scorecard row the audit resolved, with its classification authority."""
    scorecard = project_root / _SCORECARD_PATH
    if not scorecard.exists():
        return []
    resolved, _ = _resolve_population(project_root, _parse_scorecard(scorecard))
    return [
        AuditedBullet(
            section_id=row.section_id,
            row_number=row.number,
            rule=row.rule,
            source=row.source,
            scorecard_classification=row.classification,
            classification=entry.classification if entry is not None else row.classification,
            authority="corpus" if entry is not None else "scorecard",
            entry_id=entry.id if entry is not None else None,
        )
        for row, entry in resolved
    ]


def _resolve_population(
    project_root: Path, rows: list[_Row]
) -> tuple[list[_Resolved], list[ValidationError]]:
    """Decide which single surface classifies each row; fail closed on a broken mapping.

    With no ownership declaration and no attributed row the project is not
    enrolled: every row is answered by the scorecard, as before this reader.
    """
    surfaces = _enrolled_surfaces(project_root)
    if not surfaces and not any(row.source for row in rows):
        return [_Resolved(row, None) for row in rows], []

    errors = _identity_errors(rows)
    ownership = {surface: _load_ownership(project_root, surface) for surface in surfaces}
    errors.extend(o for o in ownership.values() if isinstance(o, ValidationError))
    errors.extend(_capture_default_errors(ownership))
    resolved: list[_Resolved] = []
    for row in rows:
        outcome = _resolve_row(project_root, row, ownership)
        if isinstance(outcome, ValidationError):
            errors.append(outcome)
        elif outcome is not None:
            resolved.append(outcome)
    return resolved, errors


def _enrolled_surfaces(project_root: Path) -> list[str]:
    """Return the surfaces that carry a section-ownership declaration."""
    directory = declaration_path(project_root, "surface").parent
    return sorted(path.name[: -len(".json")] for path in directory.glob("*.json"))


def _load_ownership(project_root: Path, surface: str) -> _Ownership | ValidationError:
    """Load *surface*'s witnessed declaration and effective corpus, or the reason it failed."""
    try:
        surface_text = (project_root / surface).read_text(encoding="utf-8")
        declaration = load_declaration(
            declaration_path(project_root, surface), surface_text, project_root
        )
        corpus = effective_corpus(load_corpus(project_root, surface))
    except (OSError, ValueError) as exc:
        return _error(
            f"Bullet-retention ownership violation: the ownership declaration or corpus "
            f"of enrolled surface {surface!r} could not be loaded.\n"
            f"  Detail: {exc}\n"
            f"  Why: {_DECISION} — an enrolled surface whose ownership cannot be read is "
            f"never answered by the scorecard instead.\n"
            f"  Fix: repair the surface as the detail directs, then {_RERUN}."
        )
    return _Ownership(declaration.sections, {entry.id: entry for entry in corpus.entries})


def _capture_default_errors(
    ownership: Mapping[str, _Ownership | ValidationError],
) -> list[ValidationError]:
    """Refuse every corpus-owned section whose live entries still carry the capture default."""
    errors: list[ValidationError] = []
    for surface, owned in ownership.items():
        if isinstance(owned, ValidationError):
            continue
        unreviewed: dict[str, list[str]] = {}
        for entry in owned.entries.values():
            if entry.classification == _CAPTURE_DEFAULT and (
                owned.sections.get(entry.section) == _OWNED
            ):
                unreviewed.setdefault(entry.section, []).append(entry.id)
        for section, entry_ids in sorted(unreviewed.items()):
            errors.append(
                _error(
                    f"Bullet-retention classification violation: corpus-owned section "
                    f"{section!r} of {surface!r} carries the capture default "
                    f"{_CAPTURE_DEFAULT!r} on: {', '.join(entry_ids)}.\n"
                    f"  Why: {_DECISION} — owning a section makes its entries' "
                    f"classification binding, so an unreviewed capture default may not "
                    f"author a gate verdict.\n"
                    f"  Fix: for each entry run `uv run gz content retire {surface} --entry "
                    f'<id> --reason "<why>"`, capture the reviewed class with `uv run gz '
                    f'content remember {surface} --section {section} --text "<text>" '
                    f"--classification <Mechanical|Promotable|Judgment>`, publish with "
                    f"`uv run gz content land {surface}`, then {_RERUN}."
                )
            )
    return errors


def _identity_errors(rows: list[_Row]) -> list[ValidationError]:
    """Name every row whose ``(section id, row number)`` identity is missing or duplicated."""
    errors = [
        _mapping_error(row, "sits outside any `###` scorecard section, so it has no identity")
        for row in rows
        if row.section_id is None
    ]
    sectioned = [row for row in rows if row.section_id is not None]
    counts = Counter(_identity(row) for row in sectioned)
    reported: set[str] = set()
    for row in sectioned:
        key = _identity(row)
        if counts[key] > 1 and key not in reported:
            reported.add(key)
            errors.append(_mapping_error(row, f"shares its identity with {counts[key] - 1} other"))
    return errors


def _resolve_row(
    project_root: Path, row: _Row, ownership: Mapping[str, _Ownership | ValidationError]
) -> _Resolved | ValidationError | None:
    """Resolve one attributed row; ``None`` when its surface's load failure is already named."""
    if row.source is None:
        return _mapping_error(row, "carries no `source=` attribution in its Notes column")
    owned = ownership.get(row.source)
    if owned is None:
        if row.entry_id is not None:
            return _mapping_error(
                row,
                f"cites corpus entry {row.entry_id!r} but surface {row.source!r} has no "
                f"ownership declaration",
            )
        if not (project_root / row.source).is_file():
            return _missing_source_error(row)
        return _Resolved(row, None)
    if isinstance(owned, ValidationError):
        return None
    return _resolve_enrolled_row(row, owned)


def _resolve_enrolled_row(row: _Row, owned: _Ownership) -> _Resolved | ValidationError:
    """Bind a row on an enrolled surface to its corpus entry when its section is owned."""
    state = owned.sections.get(row.source_section or "")
    if state is None:
        return _mapping_error(
            row,
            f"names section {row.source_section!r}, which the ownership declaration of "
            f"{row.source!r} does not declare",
        )
    if state != _OWNED:
        return _Resolved(row, None)
    if row.entry_id is None:
        return _mapping_error(
            row, f"sits in corpus-owned section {row.source_section!r} but cites no entry id"
        )
    entry = owned.entries.get(row.entry_id)
    if entry is None:
        return _mapping_error(
            row,
            f"cites entry {row.entry_id!r}, which is not live in the effective corpus "
            f"(retired, superseded or never captured)",
        )
    if entry.section != row.source_section:
        return _mapping_error(
            row,
            f"cites entry {row.entry_id!r}, which belongs to section {entry.section!r}, "
            f"not {row.source_section!r}",
        )
    return _Resolved(row, entry)


def _retention_errors(project_root: Path, resolved: list[_Resolved]) -> list[ValidationError]:
    """Return the retention violation of every enforced bullet, by its binding class."""
    surface_text = _normalize(_collect_surface_corpus(project_root))
    entries = _load_corpus_entries(project_root)
    errors: list[ValidationError] = []
    for row, entry in resolved:
        classification = entry.classification if entry is not None else row.classification
        normalized_rule = _normalize(row.rule)
        if not _is_enforced(classification) or not normalized_rule:
            continue
        if row.source is not None and _DECLARED_SOURCE_RE.match(row.source):
            retained = normalized_rule in _normalize(_read_source(project_root, row.source))
            error = None if retained else _source_absent_error(row)
        else:
            error = _surface_retention_error(
                project_root, _Resolved(row, entry), surface_text, entries
            )
        if error is not None:
            errors.append(error)
    return errors


def _surface_retention_error(
    project_root: Path, item: _Resolved, surface_text: str, entries: list[CorpusEntry]
) -> ValidationError | None:
    """Apply the tier-scoped per-turn-surface contract to one enforced bullet."""
    row, entry = item
    normalized_rule = _normalize(row.rule)
    if entry is not None:
        classification, origin = entry.classification, _corpus_origin(entry)
        tier, surface = entry.tier, entry.surface
    else:
        classification, origin = row.classification, ""
        tier, surface = _resolve_tier(normalized_rule, entries)
    if tier == "compressible":
        if _retention_witnessed(project_root, surface):
            return None
        return _compressible_unwitnessed_error(row.rule, classification, surface, origin)
    # Invariant tier (and the conservative unknown-tier fallback): verbatim.
    if normalized_rule in surface_text:
        return None
    return _invariant_absent_error(row.rule, classification, origin)


def _read_source(project_root: Path, source: str) -> str:
    """Return an attributed source file's text, or empty text when it cannot be read."""
    try:
        return (project_root / source).read_text(encoding="utf-8")
    except OSError:
        return ""


def _disagrees(entry: CorpusEntry, row: _Row) -> bool:
    """Return True when a reviewed corpus class differs from the scorecard cell.

    An entry still on the capture default binds nothing: the fence names it, so
    there is no binding disagreement to report.
    """
    if entry.classification == _CAPTURE_DEFAULT:
        return False
    return entry.classification.lower() != row.classification.strip().lower()


def _identity(row: _Row) -> str:
    """Render a row's ``(scorecard section id, row number)`` identity."""
    return f"{row.section_id} #{row.number}"


def _corpus_origin(entry: CorpusEntry) -> str:
    """Name the corpus entry a bound classification was read from."""
    return (
        f"  Classification source: corpus entry {entry.id!r} "
        f"(section {entry.section!r} of {entry.surface} is corpus-owned; {_DECISION}).\n"
    )


def _disagreement_message(row: _Row, entry: CorpusEntry) -> str:
    """Report a corpus/scorecard disagreement on an owned bullet; the corpus value binds."""
    return (
        f"bullet-retention: scorecard row {_identity(row)} scores {row.classification!r} but "
        f"corpus entry {entry.id!r} classifies it {entry.classification!r}; the corpus value "
        f"binds ({_DECISION}). Reconcile the row's Score in {_SCORECARD_PATH.as_posix()} or "
        f"the entry in {corpus_path(Path(), entry.surface).as_posix()} so the two agree."
    )


def _error(message: str) -> ValidationError:
    """Build a bullet-retention finding against the scorecard."""
    return ValidationError(
        type="bullet_retention",
        artifact=_SCORECARD_PATH.as_posix(),
        message=f"{message}\n  Source: {_SCORECARD_PATH.as_posix()}",
    )


def _mapping_error(row: _Row, problem: str) -> ValidationError:
    """Build the fail-closed error for a row whose identity or source mapping is broken."""
    return _error(
        f"Bullet-retention mapping violation: scorecard row {_identity(row)} {problem}.\n"
        f"  Bullet: {row.rule!r}\n"
        f"  Why: {_DECISION} — every row names the one surface that classifies it, and a "
        f"row whose mapping is broken is never answered by the scorecard instead.\n"
        f"  Fix: record `source=<path>#<section-id> entry=<entry-id>` in the row's Notes "
        f"column (live entry ids are in .gzkit/corpus/<surface>.jsonl), then {_RERUN}."
    )


def _missing_source_error(row: _Row) -> ValidationError:
    """Build the fail-closed error for a row whose attributed source file does not exist."""
    return _error(
        f"Bullet-retention violation: scorecard row {_identity(row)} is attributed to "
        f"source {row.source!r}, which does not exist.\n"
        f"  Bullet: {row.rule!r}\n"
        f"  Why: ADR-0.0.33 Invariant 1, source-aware per OBPI-0.35.0-10 (GHI #939) — a "
        f"row is retained against the source that declares it and is never exempt.\n"
        f"  Fix: restore {row.source}, or correct the row's `source=` attribution, "
        f"then {_RERUN}."
    )


def _source_absent_error(row: _Row) -> ValidationError:
    """Build the fail-closed error for an enforced row absent from its attributed source."""
    return _error(
        f"Bullet-retention violation: {row.classification!r} scorecard row {_identity(row)} "
        f"is not found verbatim in its attributed source {row.source!r}.\n"
        f"  Bullet: {row.rule!r}\n"
        f"  Why: ADR-0.0.33 Invariant 1, source-aware per OBPI-0.35.0-10 (GHI #939) — a "
        f"skill- or ADR-sourced discipline is retained against that source's own text "
        f"and is never exempt.\n"
        f"  Fix: restore the bullet text verbatim to {row.source}, or correct the row's "
        f"`source=` attribution, then {_RERUN}."
    )


def _invariant_absent_error(
    rule_text: str, classification: str, origin: str = ""
) -> ValidationError:
    """Build the fail-closed error for an invariant-tier bullet absent from the surface."""
    return ValidationError(
        type="bullet_retention",
        artifact=_SCORECARD_PATH.as_posix(),
        message=(
            f"Bullet-retention violation: invariant-tier {classification!r} bullet "
            f"not found verbatim in per-turn surface.\n"
            f"  Bullet: {rule_text!r}\n"
            f"{origin}"
            f"  Why: ADR-0.0.33 Invariant 1 requires invariant-tier content to render "
            f"verbatim at every setpoint (tier-scoped amendment 2026-06-03).\n"
            f"  Fix: restore the bullet text verbatim to AGENTS.md/CLAUDE.md/.claude/rules, "
            f"or re-classify it compressible in the corpus and record an advisor-QC verdict.\n"
            f"  Source: {_SCORECARD_PATH.as_posix()}"
        ),
    )


def _compressible_unwitnessed_error(
    rule_text: str, classification: str, surface: str | None, origin: str = ""
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
            f"{origin}"
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


def _parse_scorecard(path: Path) -> list[_Row]:
    """Parse advisory-rules-audit.md into rows keyed by ``(section id, row number)``."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []

    results: list[_Row] = []
    section: str | None = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(_SECTION_HEADING):
            section = section_id(stripped[len(_SECTION_HEADING) :])
            continue
        m = _TABLE_ROW_RE.match(stripped)
        if m is None:
            continue
        rule_text = m.group("rule").strip()
        # Skip header rows (rule text is literally "Rule" or similar)
        if rule_text.lower() in {"rule", "#", "score", "notes"}:
            continue
        attribution = _ATTRIBUTION_RE.search(m.group("notes"))
        results.append(
            _Row(
                section_id=section,
                number=m.group("num").strip(),
                rule=rule_text,
                classification=m.group("cls").strip(),
                source=attribution.group("path") if attribution else None,
                source_section=attribution.group("section") if attribution else None,
                entry_id=attribution.group("entry") if attribution else None,
            )
        )
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
    # Drop inline-link targets, keep link text: a target is relative to the file
    # carrying it, so a quote in docs/ must repoint what the rule links (GHI #803).
    text = re.sub(r"\]\([^)\s]*\)", "]", text)
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
