"""Task-envelope-coherence validator (OBPI-0.0.64-04).

Extracted from ``validate_cmd.py`` (A3 module split). Composite of four
Heavy-fail signatures: (a)/(b)/(c) over TASK discovery channels (ledger, brief
frontmatter, commit trailers, ``@advances`` registry) plus (d) ledger obpi_id
divergence integrity. ``subprocess`` and ``_sig_c_layer_drift``
are patched by ``tests/governance/test_task_envelope_coherence.py`` against this
module's namespace. Shares ``_find_obpi_briefs`` with the briefs validator module.
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path

from gzkit.commands.validate_briefs import _find_obpi_briefs
from gzkit.doc_coverage.manifest import MANPAGE_DIR
from gzkit.ledger import extract_bare_obpi_id
from gzkit.validate import ValidationError

# ---------------------------------------------------------------------------
# Task-envelope-coherence validator (OBPI-0.0.64-04)
# ---------------------------------------------------------------------------

# Worklog event types that carry an optional ``task_id`` field per ADR-0.0.64-01.
# Signature (a) only fires for these — non-worklog events (e.g. obpi_lock_*) are
# governance/ceremony events, not labor units.
#
# ``artifact_edited`` was REMOVED 2026-09-02 (GHI #947) because it never met this
# roster's own membership criterion: ``artifact_edited_event`` accepts no
# ``task_id`` parameter, so NEITHER of its producers can supply one — not the
# commit-locus backstop (GHI #847/#869) and not the tool-locus hook
# (``hooks/core.py:record_artifact_edit``). There is also no single current TASK
# to attribute to: TASKs are listed per OBPI and ``gz obpi pipeline`` auto-starts
# one per REQ. Gating a type whose producers cannot attribute makes its rows fail
# PERMANENTLY against an append-only ledger, which then blocks every later push
# including commits unrelated to the OBPI whose TASKs happened to be open
# (measured 2026-09-02 at ledger :15690, a tool-locus row with no ``commit``).
# GHI #869 fixed only the commit-locus half by keying a carve-out to ``commit``,
# on the premise that the tool locus could attribute; that premise was false, so
# the carve-out is gone and the type is out of the roster entirely.
_TASK_WORKLOG_TYPES: frozenset[str] = frozenset(
    {
        "attested",
        "gate_checked",
        "audit_receipt_emitted",
        "artifact_renamed",
        "obpi_completion_uncovered_accept",
        "intrinsic-complexity-attestation",
        "composition_rendered",
    }
)

# Return-to-health bootstrap boundary, recorded 2026-05-30. ADR-0.0.64's
# validator was promoted into `gz check` after historical TASK work had already
# emitted ledger rows without `task_id` and closed several default-bucket OBPIs.
# Do not rewrite ledger history; enforce prospectively from this epoch.
_TASK_ENVELOPE_ENFORCEMENT_EPOCH = datetime.fromisoformat("2026-05-30T14:44:00+00:00")

# GHI #653 regressed through the later ``gz task start --req`` producer, which
# continued emitting short ids after positional start was repaired. Rows emitted
# before this second producer repair are append-only history. Same-lineage short/
# full spellings before this dated cutover remain readable; every later raw
# spelling divergence still fails Signature (d).
#
# 2026-07-29: advanced from 2026-07-10T10:14 — that value dated a repair that
# never actually covered the ``--req`` path. Proof: a 2026-07-29 run of
# ``gz task start --req REQ-0.34.0-03-01 --seq next`` still emitted the short
# ``OBPI-0.34.0-03``. Root cause was NOT a missing artifact-graph key but an
# ambiguity — a phantom Layer-2 key (``OBPI-0.34.0-03-insight-harvester``, an
# ``obpi_created`` with no brief ever on disk) shared the short prefix, so
# ``_resolve_obpi_id`` saw two matches and bailed to the short form. Repaired at
# emission this date: the resolver now disambiguates by on-disk brief (Layer-1
# canon decides; two REAL briefs still refuse to guess) and ``adr_id`` is
# canonicalized via ``resolve_artifact_id``. Pinned by
# tests/test_task_obpi_id_canonicalization.py. Blast radius measured BEFORE
# advancing: exactly 2 post-cutover divergent task_ids (TASK-0.34.0-03-01-02,
# -03), both same-lineage, ZERO cross-lineage — so this tolerates only the rows
# the unrepaired producer wrote and masks nothing else. The shrink-only
# grandfather set below is untouched.
_OBPI_ID_CANONICAL_CUTOVER = datetime.fromisoformat("2026-07-29T09:45:00+00:00")
_OBPI_LINEAGE_RE = re.compile(r"^(OBPI-\d+\.\d+\.\d+-\d+)")


# Signature (d) — obpi_id divergence — grandfathers the divergent task_ids that
# predate its introduction (GHI #653). The ledger is append-only (history is
# never rewritten), and the read-side active-TASK walk was already hardened
# (commit ef976e88) so these cause no Signature (a) false positive. This set is
# SHRINK-ONLY: never add a new task_id here — fix the producer (canonicalize the
# obpi_id at emission in src/gzkit/commands/task.py) instead.
_OBPI_ID_DIVERGENCE_GRANDFATHER: frozenset[str] = frozenset(
    {"TASK-0.0.69-03-05-01", "TASK-0.0.74-20-01-01"}
)

# Signature (c) — layer-drift — grandfathers OBPIs whose channel disagreement is
# sealed in append-only history. Both completed BEFORE the channels were keyed on
# a common identity (GHI #731), so the gate never compared them: their commits
# declared one TASK while the ledger recorded 4-6, and a commit cannot gain a
# trailer retroactively without rewriting history.
#
# SHRINK-ONLY: never add an OBPI here. A new disagreement means an author
# under-declared `Task:` trailers on a commit they can still amend, or the
# pipeline minted TASKs it did not attribute — fix the attribution, not the list.
# Pinned by tests/test_task_obpi_id_canonicalization.py.
_SIG_C_DRIFT_GRANDFATHER: frozenset[str] = frozenset({"OBPI-0.0.41-03", "OBPI-0.0.63-01"})

# TASK-lifecycle event types whose obpi_id must agree across a single task_id.
_TASK_LIFECYCLE_TYPES: frozenset[str] = frozenset(
    {"task_started", "task_completed", "task_blocked", "task_escalated"}
)


def _task_envelope_event_before_epoch(ev: dict[str, object]) -> bool:
    """Return True when a ledger event predates prospective TASK-envelope enforcement."""
    observed = _ledger_event_timestamp(ev)
    return observed is not None and observed <= _TASK_ENVELOPE_ENFORCEMENT_EPOCH


def _ledger_event_timestamp(ev: dict[str, object]) -> datetime | None:
    """Parse one ledger timestamp without turning malformed history into a crash."""
    raw_ts = ev.get("ts") or ev.get("timestamp")
    if not isinstance(raw_ts, str) or not raw_ts:
        return None
    try:
        return datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _obpi_lineage_id(obpi_id: str) -> str:
    """Return the slug-independent OBPI identity encoded by TASK ids."""
    match = _OBPI_LINEAGE_RE.match(obpi_id)
    return match.group(1) if match else obpi_id


def _bucket_channel_by_lineage(channel: dict[str, set[str]]) -> dict[str, set[str]]:
    """Re-key a discovery-channel map by OBPI lineage instead of id spelling.

    Signature (c) compares TASK sets per OBPI, but its channels natively key on
    different id forms, so one OBPI split into two buckets each holding a subset
    — and a bucket with only one non-empty channel is skipped. That is why the
    gate compared 6 of 776 OBPIs (GHI #731).

    Narrow by construction: lineage is ``OBPI-<semver>-<item>``, so genuinely
    different OBPIs never merge and real cross-OBPI drift still fires.
    """
    bucketed: dict[str, set[str]] = {}
    for obpi_id, task_ids in channel.items():
        bucketed.setdefault(_obpi_lineage_id(obpi_id), set()).update(task_ids)
    return bucketed


def _sig_c_comparison_coverage(project_root: Path) -> tuple[int, int]:
    """Return ``(compared, total)`` OBPIs for Signature (c).

    Exposed so the comparison surface is measurable rather than assumed: a gate
    that silently stops comparing looks identical to a gate finding nothing.
    """
    brief_fms = _collect_obpi_brief_frontmatter(project_root)
    ledger_map, ledger_obpis = _ledger_task_channel(project_root / ".gzkit" / "ledger.jsonl")
    maps = (
        _bucket_channel_by_lineage(ledger_map),
        _bucket_channel_by_lineage(_advances_channel_map()),
        _bucket_channel_by_lineage(_frontmatter_channel_map(brief_fms)),
        _bucket_channel_by_lineage(_commit_trailer_channel_map(project_root)),
    )
    obpi_ids = {_obpi_lineage_id(o) for o in set(brief_fms.keys()) | ledger_obpis}
    compared = sum(1 for o in obpi_ids if sum(1 for m in maps if m.get(o)) >= 2)
    return compared, len(obpi_ids)


def _event_path(ev: dict[str, object]) -> str:
    raw_path = ev.get("path") or ev.get("id") or ""
    if not isinstance(raw_path, str):
        return ""
    return raw_path.replace("\\", "/")


def _is_active_obpi_brief_reflection_event(
    ev: dict[str, object],
    active_tasks_by_obpi: dict[str, set[str]],
) -> bool:
    """Return True when an ``artifact_edited`` event is an OBPI-brief ceremony edit.

    Both brief *authoring* (``gz-obpi-specify`` edits ``/obpis/<X>.md`` before the
    pipeline starts X's own TASKs) and closeout *reflection* (writing completion
    evidence back into the brief) are ceremony/proof bookkeeping on the OBPI itself,
    not implementation labor for one REQ. The earlier form additionally required the
    brief's own OBPI to already have active TASKs, which flagged pre-pipeline
    authoring emitted while a *different* OBPI's TASKs were active (GHI #563). This
    now mirrors the ADR-decision-doc carve-out: a brief edit is excused whenever any
    TASK is active (signature (a) only fires then anyway). Ordinary source/doc
    artifact edits remain worklog events and still require TASK attribution.
    """
    if ev.get("event") != "artifact_edited":
        return False
    if not any(active_tasks_by_obpi.values()):
        return False
    path = _event_path(ev)
    return "/obpis/" in path and path.endswith(".md")


# Matches both versioned ADR decision docs (``ADR-<semver>-*.md``) and pool ADRs
# (``ADR-pool.*.md``). Pool ADRs are backlog governance artifacts — the same
# SUPPORT-channel carve-out reasoning applies, and GHI #563 designed this carve-out
# precisely for a backlog edit emitted while a *different* OBPI's TASKs are active.
_ADR_DECISION_DOC_RE = re.compile(r"/adr/.+/ADR-(?:\d+\.\d+\.\d+-|pool\.)[^/]+\.md$")


def _is_adr_decision_doc_reflection_event(
    ev: dict[str, object],
    active_tasks_by_obpi: dict[str, set[str]],
) -> bool:
    """Return True for an ADR-decision-doc edit while any OBPI TASK is active.

    ADR decision documents (``docs/design/adr/**/ADR-<semver>-*.md``, excluding
    per-OBPI briefs under ``/obpis/``) are SUPPORT-channel governance artifacts:
    their edits are witnessed by the ``artifact_edited`` ledger event plus the
    document structural validators, not by per-REQ TASK labor (see the REQ Scope
    Discipline taxonomy). Editing one while an OBPI pipeline's TASKs are still
    active — a design/redesign session that amends an ADR, possibly a *different*
    ADR than the active OBPI's own parent — is governance ceremony, not OBPI-REQ
    implementation labor. This is the ADR-decision-doc-layer sibling of the
    OBPI-brief reflection carve-out above.
    """
    if ev.get("event") != "artifact_edited":
        return False
    if not any(active_tasks_by_obpi.values()):
        return False
    path = _event_path(ev)
    if "/obpis/" in path:
        return False
    return bool(_ADR_DECISION_DOC_RE.search(path))


def _is_support_manpage_reflection_event(
    ev: dict[str, object],
    active_tasks_by_obpi: dict[str, set[str]],
) -> bool:
    """Return True for a ``docs/user/manpages/`` edit while any OBPI TASK is active.

    CLI manpages are SUPPORT-channel documentation artifacts: a SUPPORT-kind REQ
    (e.g. OBPI-0.0.41-02's REQ-09) is witnessed by the ``artifact_edited`` ledger
    event plus ``gz validate --documents`` admitting the doc's shape — the manpage
    edit IS the proof, not a per-REQ TASK labor record (see the REQ Scope Discipline
    taxonomy). Editing one while an OBPI pipeline's TASKs are active is governance
    documentation ceremony, not OBPI-REQ implementation labor. This is the manpage-
    layer sibling of the ADR-decision-doc and OBPI-brief reflection carve-outs above;
    ordinary ``src/`` edits remain worklog events and still require TASK attribution.
    """
    if ev.get("event") != "artifact_edited":
        return False
    if not any(active_tasks_by_obpi.values()):
        return False
    path = _event_path(ev)
    return f"{MANPAGE_DIR.as_posix()}/" in path and path.endswith(".md")


def _is_req_attributed_uncovered_accept_event(
    ev: dict[str, object],
    active_tasks_by_obpi: dict[str, set[str]],
) -> bool:
    """Return True when an uncovered-accept event carries REQ-level attribution."""
    if ev.get("event") != "obpi_completion_uncovered_accept":
        return False
    obpi_id = ev.get("obpi_id")
    req_id = ev.get("req_id")
    if not isinstance(obpi_id, str) or not isinstance(req_id, str):
        return False
    active_tasks = active_tasks_by_obpi.get(obpi_id, set())
    if not active_tasks:
        return False
    m = re.match(r"^REQ-(\d+\.\d+\.\d+)-(\d+)-(\d+)$", req_id)
    if not m:
        return False
    task_prefix = f"TASK-{m.group(1)}-{m.group(2)}-{m.group(3)}-"
    return any(task.startswith(task_prefix) for task in active_tasks)


def _sig_a_is_not_labor_event(
    ev: dict,
    ev_type: str,
    obpi_id: str,
    task_id: str | None,
    active_tasks_by_obpi: dict[str, set[str]],
) -> bool:
    """Update per-OBPI active-TASK state for *ev* and report whether it is non-labor.

    Returns ``True`` when *ev* is not an attributable labor unit and the caller
    should skip it: TASK lifecycle transitions (which mutate the active sets here
    as a side effect), the ``meta-receipt-bind`` Gate-5 ceremony carve-out, brief
    reflection / REQ-attributed uncovered-accept events, and any non-worklog type.
    Returns ``False`` only for worklog events that must be checked for drift.
    """
    if ev_type == "task_started" and task_id and obpi_id:
        active_tasks_by_obpi.setdefault(obpi_id, set()).add(task_id)
        return True
    if ev_type in ("task_completed", "task_blocked", "task_escalated"):
        # A terminal event ends the TASK identified by ``task_id`` regardless of
        # which obpi_id spelling the start/complete pair recorded. The same TASK
        # can be started under a short obpi_id (``OBPI-0.0.74-20``) and completed
        # under the full slug (``OBPI-0.0.74-20-mx-...``); keying the discard to
        # the event's own obpi_id orphans the divergent start in the other
        # bucket, marking the TASK perpetually active. ``task_id`` is globally
        # unique to one OBPI, so clearing it from every bucket is safe.
        if task_id:
            for active in active_tasks_by_obpi.values():
                active.discard(task_id)
        return True

    # Closeout ``meta-receipt-bind`` is a Gate-5 ceremony receipt-binding
    # event (it binds already-emitted attestation receipts and carries an
    # ``attestor``), not a TASK labor unit — exclude it from attribution
    # drift exactly as ``obpi_lock_*`` governance events are. The carve-out
    # is narrow: only this ``receipt_event`` is excused; bare or other
    # ``audit_receipt_emitted`` rows remain labor and still fail (GHI #563).
    if ev_type == "audit_receipt_emitted" and ev.get("receipt_event") == "meta-receipt-bind":
        return True

    # ``composition_rendered`` is render telemetry, not labor. The validator no
    # longer emits it (removed 2026-06-23 — no consumer, and the per-run emission
    # broke the gz check / pre-push gate; ADR-0.0.37 Draft, OBPI-03 repudiated),
    # but the type stays defined and historical ledgers carry instances. A
    # whole-AGENTS.md render belongs to no single REQ and cannot be honestly
    # attributed to one — the type stays excused from attribution drift so legacy
    # events never trip the gate (unlike the narrow meta-receipt-bind
    # discriminator above).
    if ev_type == "composition_rendered":
        return True

    # NOTE (GHI #947): a ``commit``-keyed carve-out for commit-locus
    # ``artifact_edited`` rows lived here from GHI #869 until 2026-09-02. It is
    # gone because ``artifact_edited`` left ``_TASK_WORKLOG_TYPES`` entirely —
    # see that roster's comment — so the final ``ev_type not in`` test below now
    # excuses BOTH loci and this branch could never fire. The reasoning it
    # carried (attributing to an arbitrary live TASK would be FALSE attribution,
    # worse than none) is preserved there and still governs.

    if _is_active_obpi_brief_reflection_event(ev, active_tasks_by_obpi):
        return True
    if _is_adr_decision_doc_reflection_event(ev, active_tasks_by_obpi):
        return True
    if _is_support_manpage_reflection_event(ev, active_tasks_by_obpi):
        return True
    if _is_req_attributed_uncovered_accept_event(ev, active_tasks_by_obpi):
        return True
    return ev_type not in _TASK_WORKLOG_TYPES


# Signature (a) — `gz adr demote`'s `artifact_renamed` producer went unattributed
# until ADR-0.34.0 OBPI-04 repaired it (`_apply_demote(..., task_id=...)` ->
# `artifact_renamed_event(..., task_id=...)`). `artifact_renamed` is a worklog
# type, but the only prior bulk demotion — GHI #520's Day-0 pool migration,
# 2026-05-23 — predates `_TASK_ENVELOPE_ENFORCEMENT_EPOCH`, so the gap never
# surfaced until the Foundation Sunset ran the verb again inside a TASK envelope.
#
# The ledger is append-only (history is not rewritten), so the rows that
# unrepaired producer already wrote are grandfathered here. BLAST RADIUS MEASURED
# BEFORE ADDING, per the precedent of `_OBPI_ID_CANONICAL_CUTOVER` above: exactly
# 51 `reason="pool_demotion"` renames carry no `task_id` — 28 pre-epoch (already
# tolerated) and the 23 the Sunset emitted on 2026-07-30. The predicate is
# narrowed to that exact shape (event type AND reason AND missing task_id) and to
# renames emitted at or before the cutover, so it masks nothing else and expires
# by construction: a demotion run after this date must carry `task_id` or fail.
_POOL_DEMOTION_ATTRIBUTION_CUTOVER = datetime.fromisoformat("2026-07-30T09:00:00+00:00")


def _sig_a_is_grandfathered_demotion(
    ev: dict[str, object], ev_type: str, task_id: str | None
) -> bool:
    """Return True for a pre-cutover ``pool_demotion`` rename from the unrepaired producer."""
    if ev_type != "artifact_renamed" or task_id or ev.get("reason") != "pool_demotion":
        return False
    raw_ts = ev.get("ts")
    if not isinstance(raw_ts, str):
        return False
    try:
        emitted = datetime.fromisoformat(raw_ts)
    except ValueError:
        return False
    return emitted <= _POOL_DEMOTION_ATTRIBUTION_CUTOVER


def _sig_a_attribution_drift(
    project_root: Path, *, obpi_filter: str | None = None
) -> list[ValidationError]:
    """Signature (a) — worklog event emitted under an active TASK with no ``task_id``.

    Scans ``.gzkit/ledger.jsonl`` for any worklog event (per ``_TASK_WORKLOG_TYPES``)
    that lacks a ``task_id`` field while a TASK is active in scope at its emission
    time. "Active TASK in scope" is computed per OBPI: a TASK is active between its
    ``task_started`` event and its terminal (``task_completed``/``task_blocked``/
    ``task_escalated``) event for the same OBPI.

    Heavy-fail: each missing-``task_id`` worklog event yields one ValidationError.

    ``obpi_filter``: when set (the completion-chokepoint scoping, GHI #590), emit
    errors only for events whose own ``obpi_id`` matches — i.e. *that* OBPI's own
    unattributed labor. The active-TASK state walk and every carve-out is
    identical to the unfiltered (repo-wide ``gz check``) pass; only error emission
    is narrowed, so the chokepoint cannot flag another OBPI's drift.
    """
    import json as _json  # noqa: PLC0415

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []

    # Walk the ledger in order, tracking which OBPI's TASK is active at each point.
    # Multi-OBPI activity is allowed; we track per-OBPI active sets.
    active_tasks_by_obpi: dict[str, set[str]] = {}
    errors: list[ValidationError] = []

    for line_num, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            ev = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        if _task_envelope_event_before_epoch(ev):
            continue
        ev_type = ev.get("event", "")
        obpi_id = ev.get("obpi_id") or ""
        task_id = ev.get("task_id")

        if _sig_a_is_not_labor_event(ev, ev_type, obpi_id, task_id, active_tasks_by_obpi):
            continue

        any_active = any(active_tasks_by_obpi.values())
        if _sig_a_is_grandfathered_demotion(ev, ev_type, task_id):
            continue
        if any_active and not task_id and (obpi_filter is None or obpi_id == obpi_filter):
            errors.append(
                ValidationError(
                    type="task_envelope_coherence",
                    artifact=f".gzkit/ledger.jsonl:{line_num}",
                    message=(
                        f"Signature (a): worklog event {ev_type!r} emitted under "
                        f"active TASK with no task_id field "
                        f"(active TASKs: "
                        f"{sorted({t for s in active_tasks_by_obpi.values() for t in s})})."
                    ),
                )
            )
    return errors


def _collect_obpi_brief_frontmatter(
    project_root: Path,
) -> dict[str, dict[str, object]]:
    """Return a mapping of OBPI id (stem) to its parsed frontmatter."""
    import yaml  # noqa: PLC0415

    out: dict[str, dict[str, object]] = {}
    for brief_path in _find_obpi_briefs(project_root):
        text = brief_path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        if end == -1:
            continue
        try:
            fm = yaml.safe_load(text[4:end]) or {}
        except yaml.YAMLError:
            continue
        if isinstance(fm, dict):
            obpi_id = str(fm.get("id") or brief_path.stem)
            out[obpi_id] = fm
    return out


_SIG_B_TASK_ID_RE = re.compile(
    r"^TASK-(?P<semver>\d+\.\d+\.\d+)-(?P<obpi_item>\d+)-(?P<req_index>\d+)-(?P<seq>\d+)$"
)


def _scan_ledger_for_obpi_completions_and_tasks(
    ledger_path: Path,
) -> tuple[set[str], dict[str, set[str]]]:
    import json as _json  # noqa: PLC0415

    completed_obpis: set[str] = set()
    tasks_by_obpi: dict[str, set[str]] = {}
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        if _task_envelope_event_before_epoch(ev):
            continue
        ev_type = ev.get("event", "")
        if ev_type == "obpi_receipt_emitted" and ev.get("receipt_event") == "completed":
            completed_obpis.add(str(ev.get("id") or ""))
        elif ev_type == "task_started":
            obpi_id = ev.get("obpi_id") or ""
            task_id = ev.get("task_id") or ""
            if obpi_id and task_id:
                tasks_by_obpi.setdefault(str(obpi_id), set()).add(task_id)
    return completed_obpis, tasks_by_obpi


def _group_tasks_by_req(tasks: set[str]) -> dict[str, set[str]]:
    seqs_by_req: dict[str, set[str]] = {}
    for tid in tasks:
        m = _SIG_B_TASK_ID_RE.match(tid)
        if not m:
            continue
        req_id = f"REQ-{m['semver']}-{m['obpi_item']}-{m['req_index']}"
        seqs_by_req.setdefault(req_id, set()).add(m["seq"])
    return seqs_by_req


def _sig_b_error_for_obpi(
    obpi_id: str, seqs_by_req: dict[str, set[str]], req_atomic: object
) -> ValidationError | None:
    if not seqs_by_req or not all(seqs == {"01"} for seqs in seqs_by_req.values()):
        return None
    if not isinstance(req_atomic, list):
        req_atomic = []
    atomic_set = {str(r) for r in req_atomic}
    all_reqs = set(seqs_by_req.keys())
    if atomic_set >= all_reqs:
        return None
    unexempted = sorted(all_reqs - atomic_set)
    return ValidationError(
        type="task_envelope_coherence",
        artifact=obpi_id,
        message=(
            f"Signature (b): OBPI {obpi_id} closed with only seq=01 TASKs "
            f"across all REQs and no req_atomic exemption for: "
            f"{', '.join(unexempted)}. Subdivide via "
            f"`gz task start --seq next` or declare `req_atomic:` "
            f"in brief frontmatter with inline rationale."
        ),
    )


def _sig_b_subdivision_skipped(project_root: Path) -> list[ValidationError]:
    """Signature (b) — OBPI closes with only ``seq=01`` TASKs across all REQs."""
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []

    completed_obpis, tasks_by_obpi = _scan_ledger_for_obpi_completions_and_tasks(ledger_path)
    brief_fms = _collect_obpi_brief_frontmatter(project_root)
    errors: list[ValidationError] = []
    for obpi_id in sorted(completed_obpis):
        if not obpi_id:
            continue
        tasks = set(tasks_by_obpi.get(obpi_id, set()))
        if not tasks:
            continue
        lineage = _obpi_lineage_id(obpi_id)
        for event_obpi_id, event_tasks in tasks_by_obpi.items():
            if event_obpi_id != obpi_id and _obpi_lineage_id(event_obpi_id) == lineage:
                tasks.update(event_tasks)
        seqs_by_req = _group_tasks_by_req(tasks)
        err = _sig_b_error_for_obpi(
            obpi_id, seqs_by_req, brief_fms.get(obpi_id, {}).get("req_atomic") or []
        )
        if err is not None:
            errors.append(err)
    return errors


def _read_brief_frontmatter(brief_path: Path) -> dict[str, object]:
    """Parse a single brief's YAML frontmatter (single-brief mirror of the bulk collector)."""
    import yaml  # noqa: PLC0415

    text = brief_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    try:
        fm = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return {}
    return fm if isinstance(fm, dict) else {}


def pending_obpi_sig_b_error(project_root: Path, brief_path: Path) -> ValidationError | None:
    """Signature-(b) check for an OBPI *about to be completed* — the chokepoint gate (GHI #590).

    The repo-wide validator only flags OBPIs that already carry a completion
    event; this scoped variant predicts the same residue one step earlier, so
    ``gz obpi complete`` can fail closed before it ever reaches ``gz check``.
    The canonical full-slug id is read from the brief frontmatter so the ledger
    ``task_started.obpi_id`` scan and the ``req_atomic`` lookup align — guarding
    the short-vs-full obpi_id divergence (a mismatch would find zero tasks and
    silently pass). Reuses ``_sig_b_error_for_obpi`` so the rule is identical to
    ``gz validate --task-envelope-coherence`` Signature (b) — single source of truth.
    """
    fm = _read_brief_frontmatter(brief_path)
    obpi_id = str(fm.get("id") or brief_path.stem)
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    tasks = _ledger_channel_for_obpi(ledger_path, obpi_id)
    seqs_by_req = _group_tasks_by_req(tasks)
    req_atomic = fm.get("req_atomic") or []
    return _sig_b_error_for_obpi(obpi_id, seqs_by_req, req_atomic)


def pending_obpi_task_envelope_errors(
    project_root: Path, brief_path: Path
) -> list[ValidationError]:
    """All task-envelope-coherence errors (Sig a/b/c) an OBPI would carry at completion (GHI #590).

    The completion chokepoint must predict every signature ``gz check`` enforces —
    Sig (a) unattributed labor, Sig (b) seq=01-only-without-``req_atomic``, and
    Sig (c) layer-drift — scoped to the pending OBPI, so the residue can never
    reach ``main``. Each signature reuses the same rule as the repo-wide
    validator (single source of truth); only the scoping differs:
      - Sig (a): ``_sig_a_attribution_drift`` with ``obpi_filter`` (carve-outs intact),
      - Sig (b): ``pending_obpi_sig_b_error`` (already scoped, full-slug-id-derived),
      - Sig (c): ``_sig_c_layer_drift`` filtered to this OBPI's ``artifact`` errors.
    """
    obpi_id = str(_read_brief_frontmatter(brief_path).get("id") or brief_path.stem)
    errors: list[ValidationError] = []
    sig_b = pending_obpi_sig_b_error(project_root, brief_path)
    if sig_b is not None:
        errors.append(sig_b)
    errors.extend(_sig_a_attribution_drift(project_root, obpi_filter=obpi_id))
    errors.extend(e for e in _sig_c_layer_drift(project_root) if e.artifact == obpi_id)
    return errors


def _task_matches_obpi(task_id: str, obpi_id: str) -> bool:
    m = re.match(r"^TASK-(\d+\.\d+\.\d+)-(\d+)-", task_id)
    return bool(m and f"OBPI-{m.group(1)}-{m.group(2)}" == obpi_id)


def _advances_channel_for_obpi(obpi_id: str) -> set[str]:
    try:
        from gzkit.tasks import get_task_registry  # noqa: PLC0415

        return {
            rec.task_id for rec in get_task_registry() if _task_matches_obpi(rec.task_id, obpi_id)
        }
    except Exception:  # noqa: BLE001  -- defensive; registry walk is best-effort
        return set()


def _frontmatter_channel_for_obpi(project_root: Path, obpi_id: str) -> set[str]:
    """Collect the ``tasks:`` a brief declares, on either spelling of its id.

    The frontmatter map is keyed on the brief's authored ``id:`` — conventionally
    the full slug — while the other three channels resolve on the bare
    ``OBPI-<semver>-<NN>`` form, because that is the shape ``_task_matches_obpi``
    rebuilds out of a TASK id. ``_channel_declarations_for_obpi`` hands ONE id to
    all four collectors, so a caller must pick a form that is wrong for one side
    of that split; it picked bare, and this channel read empty for every
    full-slug brief in the repo (GHI #946).

    Accepting both here rather than at the caller keeps the choice off the one
    surface whose job is comparing these channels: an empty channel is dropped
    from the drift comparison (``populated``), so the failure is a quiet wrong
    verdict rather than a loud disagreement.
    """
    brief_fms = _collect_obpi_brief_frontmatter(project_root)
    fm = brief_fms.get(obpi_id)
    if fm is None:
        bare = extract_bare_obpi_id(obpi_id)
        fm = next(
            (v for k, v in brief_fms.items() if bare and extract_bare_obpi_id(k) == bare),
            None,
        )
    fm_tasks = (fm or {}).get("tasks") or []
    if not isinstance(fm_tasks, list):
        return set()
    return {str(t) for t in fm_tasks if isinstance(t, str)}


def _ledger_channel_for_obpi(ledger_path: Path, obpi_id: str) -> set[str]:
    import json as _json  # noqa: PLC0415

    result: set[str] = set()
    if not ledger_path.exists():
        return result
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        event_obpi = str(ev.get("obpi_id") or "")
        if (
            ev.get("event") == "task_started"
            and _obpi_lineage_id(event_obpi) == _obpi_lineage_id(obpi_id)
            and ev.get("task_id")
        ):
            result.add(str(ev["task_id"]))
    return result


def _commit_trailer_channel_for_obpi(project_root: Path, obpi_id: str) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--format=%B%n--EOC--"],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return set()
    if result.returncode != 0:
        return set()
    from gzkit.tasks import parse_task_trailers  # noqa: PLC0415

    found: set[str] = set()
    for chunk in result.stdout.split("--EOC--"):
        for tid in parse_task_trailers(chunk):
            tid_str = str(tid)
            if _task_matches_obpi(tid_str, obpi_id):
                found.add(tid_str)
    return found


def _channel_declarations_for_obpi(project_root: Path, obpi_id: str) -> dict[str, set[str]]:
    """Collect per-channel TASK ID declarations for the named OBPI."""
    return {
        "advances": _advances_channel_for_obpi(obpi_id),
        "frontmatter": _frontmatter_channel_for_obpi(project_root, obpi_id),
        "commit_trailer": _commit_trailer_channel_for_obpi(project_root, obpi_id),
        "ledger": _ledger_channel_for_obpi(project_root / ".gzkit" / "ledger.jsonl", obpi_id),
    }


def _obpi_id_for_task(task_id: str) -> str | None:
    """Return the OBPI id a TASK id belongs to, or ``None`` for non-formal ids.

    Inverse of ``_task_matches_obpi``: ``_task_matches_obpi(tid, obpi)`` is true
    iff ``_obpi_id_for_task(tid) == obpi``. Slug-form direct-fix ids
    (``TASK-<slug>-#<ghi>``) have no OBPI parent and return ``None``.
    """
    m = re.match(r"^TASK-(\d+\.\d+\.\d+)-(\d+)-", task_id)
    if not m:
        return None
    return f"OBPI-{m.group(1)}-{m.group(2)}"


def _advances_channel_map() -> dict[str, set[str]]:
    """Group every ``@advances``-registered TASK id by its OBPI (registry walked once)."""
    out: dict[str, set[str]] = {}
    try:
        from gzkit.tasks import get_task_registry  # noqa: PLC0415

        for rec in get_task_registry():
            obpi_id = _obpi_id_for_task(rec.task_id)
            if obpi_id:
                out.setdefault(obpi_id, set()).add(rec.task_id)
    except Exception:  # noqa: BLE001  -- defensive; registry walk is best-effort
        return {}
    return out


def _frontmatter_channel_map(
    brief_fms: dict[str, dict[str, object]],
) -> dict[str, set[str]]:
    """Group each brief's frontmatter ``tasks:`` declarations by OBPI id.

    Reuses the already-collected ``brief_fms`` mapping so the brief corpus is
    parsed once for the whole audit rather than once per OBPI.
    """
    out: dict[str, set[str]] = {}
    for obpi_id, fm in brief_fms.items():
        fm_tasks = fm.get("tasks") or []
        if not isinstance(fm_tasks, list):
            continue
        tids = {str(t) for t in fm_tasks if isinstance(t, str)}
        if tids:
            out[obpi_id] = tids
    return out


def _commit_trailer_channel_map(project_root: Path) -> dict[str, set[str]]:
    """Parse every commit's TASK trailers in ONE ``git log`` walk, grouped by OBPI.

    Bulk-audit counterpart to ``_commit_trailer_channel_for_obpi``: one
    ``git log --all`` walk for the whole audit instead of one subprocess per
    brief.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--format=%B%n--EOC--"],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=30,
        )
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return {}
    if result.returncode != 0:
        return {}
    from gzkit.tasks import parse_task_trailers  # noqa: PLC0415

    out: dict[str, set[str]] = {}
    for chunk in result.stdout.split("--EOC--"):
        for tid in parse_task_trailers(chunk):
            tid_str = str(tid)
            obpi_id = _obpi_id_for_task(tid_str)
            if obpi_id:
                out.setdefault(obpi_id, set()).add(tid_str)
    return out


def _ledger_task_channel(ledger_path: Path) -> tuple[dict[str, set[str]], set[str]]:
    """Read the ledger ONCE; return (ledger TASK channel map, all OBPI ids seen).

    The channel map groups ``task_started`` ``task_id`` values by ``obpi_id``
    (matching ``_ledger_channel_for_obpi``). The second set carries every
    ``obpi_id`` appearing on a ``task_started`` event even when the event omits
    ``task_id`` — preserving the brief-less OBPI discovery the audit previously
    did in a separate ledger pass.
    """
    import json as _json  # noqa: PLC0415

    channel: dict[str, set[str]] = {}
    seen_obpis: set[str] = set()
    if not ledger_path.exists():
        return channel, seen_obpis
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        if ev.get("event") != "task_started":
            continue
        obpi_id = ev.get("obpi_id")
        if not obpi_id:
            continue
        obpi_str = str(obpi_id)
        seen_obpis.add(obpi_str)
        task_id = ev.get("task_id")
        if task_id:
            channel.setdefault(obpi_str, set()).add(str(task_id))
    return channel, seen_obpis


def _sig_c_layer_drift(project_root: Path) -> list[ValidationError]:
    """Signature (c) — layer-drift across the four discovery channels per OBPI.

    Drift = two or more channels each declare at least one TASK ID for the
    OBPI, but the union of TASK IDs spans more than the intersection (i.e. a
    TASK ID present on one channel is missing from another non-empty channel).
    Conservative single-OBPI-and-REQ scoping: drift fires when channels
    disagree on the set of TASKs for the same OBPI.

    Each channel is materialized ONCE for the whole audit (one ``git log``
    walk, one frontmatter parse, one ledger read) and indexed per-OBPI inside
    the loop, rather than re-scanning every channel per brief.
    """
    errors: list[ValidationError] = []
    brief_fms = _collect_obpi_brief_frontmatter(project_root)

    ledger_map, ledger_obpis = _ledger_task_channel(project_root / ".gzkit" / "ledger.jsonl")
    # Key EVERY channel on OBPI lineage (GHI #731). The channels natively use
    # different id forms — the ledger groups by the raw `obpi_id` event field
    # (full slug after `gz obpi complete`) while the commit-trailer channel keys
    # off the form encoded in the TASK id (short `OBPI-<semver>-<item>`) — so one
    # OBPI landed in two buckets, each holding a subset, and `len(non_empty) < 2`
    # skipped it. Measured before this fix: the gate compared 6 of 776 OBPIs.
    # A TASK id encodes exactly one OBPI lineage, so lineage is the correct
    # comparison key and distinct OBPIs never merge.
    ledger_map = _bucket_channel_by_lineage(ledger_map)
    advances_map = _bucket_channel_by_lineage(_advances_channel_map())
    frontmatter_map = _bucket_channel_by_lineage(_frontmatter_channel_map(brief_fms))
    commit_trailer_map = _bucket_channel_by_lineage(_commit_trailer_channel_map(project_root))

    # OBPIs come from authored briefs plus any with ledger task_started events
    # even without a brief.
    obpi_ids = {_obpi_lineage_id(o) for o in set(brief_fms.keys()) | ledger_obpis}

    for obpi_id in sorted(obpi_ids):
        if obpi_id in _SIG_C_DRIFT_GRANDFATHER:
            continue
        channels = {
            "advances": advances_map.get(obpi_id, set()),
            "frontmatter": frontmatter_map.get(obpi_id, set()),
            "commit_trailer": commit_trailer_map.get(obpi_id, set()),
            "ledger": ledger_map.get(obpi_id, set()),
        }
        non_empty = {k: v for k, v in channels.items() if v}
        if len(non_empty) < 2:
            continue  # need at least two channels with declarations to compare
        all_tasks: set[str] = set()
        for tids in non_empty.values():
            all_tasks |= tids
        diverging_channels = _crossing_channels(non_empty)
        if diverging_channels:
            errors.append(
                ValidationError(
                    type="task_envelope_coherence",
                    artifact=obpi_id,
                    message=(
                        f"Signature (c): layer-drift across discovery channels "
                        f"for {obpi_id}. Union: "
                        f"{sorted(all_tasks)}; diverging channels: "
                        f"{diverging_channels}. "
                        f"Run `gz task envelope diagnose {obpi_id}` "
                        f"to see per-channel declarations side-by-side."
                    ),
                )
            )
    return errors


def _crossing_channels(non_empty: dict[str, set[str]]) -> list[str]:
    """Return the channels that CONTRADICT one another, never those merely behind.

    Two channels cross when each holds a TASK id the other lacks. Channels whose
    declarations are *nested* — one a subset of the other — do not cross: the
    smaller is simply further behind, which is the normal state of a discovery
    channel that accretes.

    This replaced ``tids != all_tasks`` on 2026-08-17 (GHI #820). Set equality
    against the union reported any channel short of the union as divergent, which
    made the gate **satisfiable only by falsifying attribution**: ``gz obpi
    pipeline`` writes every ``task_started`` event AT LAUNCH, while commit
    trailers accrete one commit at a time, so those two channels could agree only
    if every commit carried every TASK's trailer.
    ``.claude/rules/task-discovery.md`` § Layer-drift fail-close forbids precisely
    that (*"do not silently rewrite TASK IDs across channels to make the validator
    happy"*) and defines drift as one unit of labor surfacing *"with different
    TASK IDs"* — a contradiction, not a shortfall. A gate whose only passing move
    is the act its own rule prohibits is worse than no gate;
    ``_SIG_C_DRIFT_GRANDFATHER`` is where two prior instances were absorbed
    instead of diagnosed.

    The real signal is preserved: ``@advances`` naming TASK-A while the trailer
    names TASK-C still fires, because neither set contains the other.
    """
    crossing: set[str] = set()
    channels = sorted(non_empty.items())
    for index, (name_a, tasks_a) in enumerate(channels):
        for name_b, tasks_b in channels[index + 1 :]:
            if (tasks_a - tasks_b) and (tasks_b - tasks_a):
                crossing.update((name_a, name_b))
    return sorted(crossing)


def _sig_d_obpi_id_divergence(project_root: Path) -> list[ValidationError]:
    """Signature (d) — a single ``task_id`` carries divergent ``obpi_id`` across events.

    A ``task_id`` maps to exactly one OBPI, so every TASK-lifecycle event
    (``task_started``/``task_completed``/``task_blocked``/``task_escalated``)
    for it MUST carry the same canonical ``obpi_id``. Two spellings — the short
    ``OBPI-<semver>-<item>`` form versus the full slug ``gz obpi pipeline``
    records — break start/complete pairing in the active-TASK walk and were the
    producer defect behind the Signature (a) false positives (GHI #653;
    read-side hardened in commit ef976e88). The two pre-existing divergent
    task_ids are grandfathered via ``_OBPI_ID_DIVERGENCE_GRANDFATHER``
    (shrink-only); every other divergence fail-closes.

    Heavy-fail: one ValidationError per divergent ``task_id``.
    """
    import json as _json  # noqa: PLC0415

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []

    obpi_by_task: dict[str, set[str]] = {}
    latest_by_task: dict[str, datetime | None] = {}
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        if ev.get("event") not in _TASK_LIFECYCLE_TYPES:
            continue
        task_id = ev.get("task_id")
        obpi_id = ev.get("obpi_id")
        if isinstance(task_id, str) and task_id and isinstance(obpi_id, str) and obpi_id:
            obpi_by_task.setdefault(task_id, set()).add(obpi_id)
            observed = _ledger_event_timestamp(ev)
            previous = latest_by_task.get(task_id)
            if observed is not None and (previous is None or observed > previous):
                latest_by_task[task_id] = observed

    errors: list[ValidationError] = []
    for task_id in sorted(obpi_by_task):
        if task_id in _OBPI_ID_DIVERGENCE_GRANDFATHER:
            continue
        spellings = obpi_by_task[task_id]
        if len(spellings) > 1:
            lineages = {_obpi_lineage_id(obpi_id) for obpi_id in spellings}
            latest = latest_by_task.get(task_id)
            if len(lineages) == 1 and latest is not None and latest <= _OBPI_ID_CANONICAL_CUTOVER:
                continue
            errors.append(
                ValidationError(
                    type="task_envelope_coherence",
                    artifact=task_id,
                    message=(
                        f"Signature (d): TASK {task_id} carries divergent obpi_id "
                        f"across lifecycle events: {sorted(spellings)}. A task_id "
                        f"maps to exactly one OBPI — emit the canonical full slug "
                        f"on every TASK event (GHI #653)."
                    ),
                )
            )
    return errors


def _sig_e_unresolvable_task_declaration(project_root: Path) -> list[ValidationError]:
    """Signature (e) — a brief's ``tasks:`` entry names an unresolvable TASK.

    Two arms, both promised by ``.gzkit/rules/task-discovery.md`` § Convention:
    Frontmatter ``tasks:`` — *"rejecting malformed TASK IDs and unknown
    parents"* — and both deferred to OBPI-0.0.64-04, whose seven REQs never
    scoped them (GHI #753).

    This is the corpus-side half. ``BriefStructure._validate_tasks`` covers the
    model-construction path, but ``_collect_obpi_brief_frontmatter`` reads raw
    YAML and never builds the model, so a malformed id on disk would otherwise
    reach signature (c)'s channel comparison as a legitimate declaration. The
    parent-REQ arm lives here rather than on the model because resolving it
    means scanning the brief corpus off disk, which the model may not do
    (``.gzkit/rules/hexagonal-architecture.md`` rule 1).

    Parent resolution reuses the frontmatter already collected for the rest of
    the audit, so the corpus is still parsed once.
    """
    from gzkit.tasks import TaskId  # noqa: PLC0415  (module-local, as the trailer channel does)

    errors: list[ValidationError] = []
    brief_fms = _collect_obpi_brief_frontmatter(project_root)

    known_reqs: set[str] = set()
    for fm in brief_fms.values():
        declared_reqs = fm.get("reqs")
        if isinstance(declared_reqs, list):
            known_reqs |= {str(r) for r in declared_reqs}

    for obpi_id, fm in sorted(brief_fms.items()):
        declared = fm.get("tasks")
        if not isinstance(declared, list):
            continue
        for raw in declared:
            tid = str(raw)
            try:
                parsed = TaskId.parse(tid)
            except ValueError:
                errors.append(
                    ValidationError(
                        type="task_envelope_coherence",
                        artifact=obpi_id,
                        message=(
                            f"Signature (e): malformed TASK id {tid!r} in the "
                            f"`tasks:` frontmatter of {obpi_id}. Expected "
                            f"TASK-X.Y.Z-NN-MM-PP. Recovery: correct the entry, "
                            f"or let `gz task start` stamp it."
                        ),
                    )
                )
                continue
            if not known_reqs:
                # No REQs discoverable at all means the corpus was unreadable,
                # not that every declaration is unknown. Flagging here would
                # fail the whole corpus on a parse failure elsewhere.
                continue
            parent_req = f"REQ-{parsed.semver}-{parsed.obpi_item}-{parsed.req_index}"
            if parent_req not in known_reqs:
                errors.append(
                    ValidationError(
                        type="task_envelope_coherence",
                        artifact=obpi_id,
                        message=(
                            f"Signature (e): TASK {tid} declared in {obpi_id} "
                            f"derives parent {parent_req}, which is in no "
                            f"extracted brief. Recovery: correct the TASK id, or "
                            f"add the REQ to its brief's `reqs:`."
                        ),
                    )
                )
    return errors


def _validate_task_envelope_coherence(project_root: Path) -> list[ValidationError]:
    """Validate task envelope coherence (OBPI-0.0.64-04).

    Composite of five Heavy-fail signatures:
        (a) worklog event under active TASK with no ``task_id`` (attribution drift)
        (b) OBPI default-bucket-only TASKs without ``req_atomic`` exemption
        (c) layer-drift across the four discovery channels (@advances, frontmatter
            tasks:, commit trailer, ledger task_id)
        (d) a single ``task_id`` carries divergent ``obpi_id`` across its
            lifecycle events (producer canonicalization drift, GHI #653)
        (e) a brief's ``tasks:`` entry is malformed or derives a parent REQ that
            exists in no brief (GHI #753)

    All ValidationError instances carry ``type="task_envelope_coherence"`` and
    route to exit 3 via ``_POLICY_BREACH_ERROR_TYPES``.
    """
    errors: list[ValidationError] = []
    errors.extend(_sig_a_attribution_drift(project_root))
    errors.extend(_sig_b_subdivision_skipped(project_root))
    errors.extend(_sig_c_layer_drift(project_root))
    errors.extend(_sig_d_obpi_id_divergence(project_root))
    errors.extend(_sig_e_unresolvable_task_declaration(project_root))
    return errors
