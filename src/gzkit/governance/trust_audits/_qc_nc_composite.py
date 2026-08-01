"""Per-invariant fixtures decomposing the three composite enforcement claims.

Three claims each fan out to several independent invariants, but carried ONE
negative control apiece — so every invariant the single fixture did not happen to
violate could be deleted outright and the control stayed green (GHI #699
generator #4):

* ``surface-fidelity`` fans out to four sub-validators
  (``trust_audits/__init__.py``); its fixture exercised pointer-integrity only.
* ``task-envelope-coherence`` checks four signatures
  (``commands/validate_task_envelope.py``); its fixture exercised signature (a).
* ``waiver-ratchet`` enforces three mechanisms
  (``trust_audits/waiver_ratchet.py``); its fixture exercised shrink-ratchet
  growth.

Each fixture below plants exactly one invariant's violation against the SAME
production entrypoint, and each claim pins an ``expect`` naming that invariant's
finding. Deleting any one sub-validator now reddens its own claim rather than
hiding behind a sibling.

The parent claim ids are deliberately retained — ``_STEP_CLASSIFICATION`` in
``qc_binding.py`` maps the "Surface fidelity" / "Task envelope coherence" /
"Waiver ratchet" gz-check steps onto exactly those ids, and dropping one would
make ``audit_qc_binding`` report the step as green-by-emptiness. The siblings are
additive.

Split into its own module for the same reason ``_qc_nc_entrypoints`` was
(``.claude/rules/pythonic.md`` module-size discipline).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

# Every ledger timestamp here must post-date the task-envelope enforcement epoch
# (2026-05-30T14:44:00+00:00) and, for obpi_id divergence, the canonical cutover
# (2026-07-10T10:14:00+00:00) — before those the validator grandfathers the shape.
_AFTER_EPOCH = "2026-06-01T00:00:00+00:00"
_AFTER_CUTOVER = "2026-07-15T00:00:00+00:00"

# An unused semver: keeps the in-process @advances registry from contaminating the
# layer-drift channel comparison with real TASK ids.
_UNUSED_OBPI = "OBPI-9.9.9-01"


def _root(slug: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"gzkit-qc-nc-{slug}-"))


def _put(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _put_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    _put(path, "\n".join(json.dumps(r) for r in records) + "\n")


# ---------------------------------------------------------------------------
# surface-fidelity siblings
# ---------------------------------------------------------------------------


def build_bullet_retention() -> Path:
    """Build an invariant-tier scorecard bullet absent from the per-turn surface.

    Only the scorecard exists, so the other three sub-validators return no
    findings and this claim isolates bullet-retention.
    """
    root = _root("bullet-retention")
    _put(
        root / "docs" / "governance" / "advisory-rules-audit.md",
        "| 1 | Never fabricate evidence | **Mechanical** | n |\n",
    )
    return root


def build_surface_weight() -> Path:
    """Build a per-turn surface in the fail-closed red band against a zero floor."""
    root = _root("surface-weight")
    _put(root / "data" / "surface_weight_floor.json", json.dumps({"lines": 0}) + "\n")
    _put(root / "AGENTS.md", "x\n" * 3001)
    return root


# ---------------------------------------------------------------------------
# task-envelope-coherence siblings
# ---------------------------------------------------------------------------


def build_task_envelope_subdivision() -> Path:
    """Signature (b): an OBPI closed with only seq=01 TASKs and no exemption.

    No brief on disk, so no ``req_atomic`` exemption applies. ``obpi_receipt_emitted``
    is outside the worklog set, so signature (a) does not also fire.
    """
    root = _root("task-envelope-subdivision")
    _put_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "task_started",
                "ts": _AFTER_EPOCH,
                "obpi_id": _UNUSED_OBPI,
                "task_id": "TASK-9.9.9-01-01-01",
            },
            {
                "event": "obpi_receipt_emitted",
                "receipt_event": "completed",
                "id": _UNUSED_OBPI,
                "ts": "2026-06-01T00:00:02+00:00",
            },
        ],
    )
    return root


def build_task_envelope_layer_drift() -> Path:
    """Signature (c): the ledger and frontmatter channels name different TASKs."""
    root = _root("task-envelope-layer-drift")
    _put_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "task_started",
                "ts": _AFTER_EPOCH,
                "obpi_id": _UNUSED_OBPI,
                "task_id": "TASK-9.9.9-01-01-01",
            }
        ],
    )
    _put(
        root / "docs" / "design" / "adr" / "foundation" / "ADR-9.9.9" / "OBPI-9.9.9-01.md",
        f"---\nid: {_UNUSED_OBPI}\ntasks:\n  - TASK-9.9.9-01-01-02\n---\n\n# brief\n",
    )
    return root


def build_task_envelope_obpi_divergence() -> Path:
    """Signature (d): one task_id carrying two obpi_id spellings.

    The two spellings name different lineages (``-01`` vs ``-02``), so the
    same-lineage grandfather cannot apply regardless of the run date — a
    date-sensitive fixture would silently stop violating later.
    """
    root = _root("task-envelope-obpi-divergence")
    _put_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "task_started",
                "ts": _AFTER_CUTOVER,
                "obpi_id": _UNUSED_OBPI,
                "task_id": "TASK-9.9.9-01-01-01",
            },
            {
                "event": "task_completed",
                "ts": "2026-07-15T00:00:01+00:00",
                "obpi_id": "OBPI-9.9.9-02-demo",
                "task_id": "TASK-9.9.9-01-01-01",
            },
        ],
    )
    return root


# ---------------------------------------------------------------------------
# waiver-ratchet siblings
# ---------------------------------------------------------------------------


def _registry(root: Path, surfaces: list[dict[str, object]]) -> None:
    _put(
        root / "data" / "waiver_ratchet_registry.json",
        json.dumps({"surfaces": surfaces}, indent=2) + "\n",
    )


def build_waiver_closed_set_lock() -> Path:
    """Build a closed-set-lock surface whose entry carries no lock field."""
    root = _root("waiver-closed-set-lock")
    _registry(
        root,
        [
            {
                "data_file": "data/a_waivers.json",
                "mechanism": "closed-set-lock",
                "entries_path": "waivers",
            }
        ],
    )
    _put(root / "data" / "a_waivers.json", json.dumps({"waivers": [{"note": "x"}]}) + "\n")
    return root


def build_waiver_dated_cutover() -> Path:
    """Build a dated-cutover surface whose cutover has not closed.

    2099 keeps the violation in the future for the lifetime of the codebase; a
    near date would quietly stop violating once it passed.
    """
    root = _root("waiver-dated-cutover")
    _registry(
        root,
        [
            {
                "data_file": "data/c_waivers.json",
                "mechanism": "dated-cutover",
                # Read from the REGISTRY surface, not the data file.
                "cutover_date": "2099-01-01",
            }
        ],
    )
    _put(root / "data" / "c_waivers.json", "{}\n")
    return root


def build_waiver_silent_bypass() -> Path:
    """Build a waiver data file on disk that no registry surface declares."""
    root = _root("waiver-silent-bypass")
    _registry(root, [])
    _put(root / "data" / "rogue_waivers.json", "{}\n")
    return root


def build_handoff_populated_sections() -> Path:
    """Build a post-cutover handoff with every required section PRESENT but one empty.

    Isolates the ``validate_sections_populated`` invariant (GHI #698). The parent
    ``handoff-documents`` fixture omits six of the seven headings, so its findings
    are all *missing-section* — delete the populated check and it stays red for
    the same missing-section reason, so the control never notices. This fixture
    plants the *present-but-empty* violation the parent never reached: all seven
    headings present, six carrying session-specific body text, one heading with an
    empty body, so the ONLY blocking finding the production audit can raise is
    "Empty required section". Delete ``validate_sections_populated`` and this
    document validates clean — which reddens the control.

    Frontmatter mirrors the parent fixture (proven to satisfy HandoffFrontmatter
    — the parent fails only on missing sections) and the timestamp is post-cutover
    so ``run_handoff_document_audit`` does not grandfather it.
    """
    root = _root("handoff-populated-sections")
    sections = (
        "Current State Summary",
        "Important Context",
        "Decisions Made",
        "Immediate Next Steps",
        "Pending Work / Open Loops",
        "Verification Checklist",
        "Evidence / Artifacts",
    )
    empty_section = "Verification Checklist"
    lines = [
        "---",
        "mode: CREATE",
        "adr_id: ADR-0.0.72",
        "branch: main",
        "timestamp: '2026-07-16T00:00:00+00:00'",
        "agent: agent:test",
        "---",
        "",
    ]
    for section in sections:
        lines.append(f"## {section}")
        lines.append("")
        if section != empty_section:
            lines.append(f"Session-specific content for the {section} section.")
            lines.append("")
    _put(root / ".gzkit" / "handoffs" / "populated.md", "\n".join(lines) + "\n")
    return root
