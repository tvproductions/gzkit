"""Task-envelope-coherence validator (OBPI-0.0.64-04).

Extracted from ``validate_cmd.py`` (A3 module split). Composite of three
Heavy-fail signatures over TASK discovery channels (ledger, brief frontmatter,
commit trailers, ``@advances`` registry). ``subprocess`` and ``_sig_c_layer_drift``
are patched by ``tests/governance/test_task_envelope_coherence.py`` against this
module's namespace. Shares ``_find_obpi_briefs`` with the briefs validator module.
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path

from gzkit.commands.validate_briefs import _find_obpi_briefs
from gzkit.doc_coverage.manifest import MANPAGE_DIR
from gzkit.validate import ValidationError

# ---------------------------------------------------------------------------
# Task-envelope-coherence validator (OBPI-0.0.64-04)
# ---------------------------------------------------------------------------

# Worklog event types that carry an optional ``task_id`` field per ADR-0.0.64-01.
# Signature (a) only fires for these — non-worklog events (e.g. obpi_lock_*) are
# governance/ceremony events, not labor units.
_TASK_WORKLOG_TYPES: frozenset[str] = frozenset(
    {
        "artifact_edited",
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


def _task_envelope_event_before_epoch(ev: dict[str, object]) -> bool:
    """Return True when a ledger event predates prospective TASK-envelope enforcement."""
    raw_ts = ev.get("ts") or ev.get("timestamp")
    if not isinstance(raw_ts, str) or not raw_ts:
        return False
    try:
        observed = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
    except ValueError:
        return False
    return observed <= _TASK_ENVELOPE_ENFORCEMENT_EPOCH


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


_ADR_DECISION_DOC_RE = re.compile(r"/adr/.+/ADR-\d+\.\d+\.\d+-[^/]+\.md$")


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
        if task_id and obpi_id and obpi_id in active_tasks_by_obpi:
            active_tasks_by_obpi[obpi_id].discard(task_id)
        return True

    # Closeout ``meta-receipt-bind`` is a Gate-5 ceremony receipt-binding
    # event (it binds already-emitted attestation receipts and carries an
    # ``attestor``), not a TASK labor unit — exclude it from attribution
    # drift exactly as ``obpi_lock_*`` governance events are. The carve-out
    # is narrow: only this ``receipt_event`` is excused; bare or other
    # ``audit_receipt_emitted`` rows remain labor and still fail (GHI #563).
    if ev_type == "audit_receipt_emitted" and ev.get("receipt_event") == "meta-receipt-bind":
        return True

    # ``composition_rendered`` is validator-emitted render telemetry, not labor.
    # ``gz validate --invariant-coherence`` (in the default ``gz check`` scope)
    # emits one on every run, so any ``gz check`` during an active OBPI pipeline
    # emits an unattributed event while TASKs are live. A whole-AGENTS.md render
    # belongs to no single REQ and cannot be honestly attributed to one — the
    # whole type is excused from attribution drift (unlike the narrow
    # meta-receipt-bind discriminator above).
    if ev_type == "composition_rendered":
        return True

    if _is_active_obpi_brief_reflection_event(ev, active_tasks_by_obpi):
        return True
    if _is_adr_decision_doc_reflection_event(ev, active_tasks_by_obpi):
        return True
    if _is_support_manpage_reflection_event(ev, active_tasks_by_obpi):
        return True
    if _is_req_attributed_uncovered_accept_event(ev, active_tasks_by_obpi):
        return True
    return ev_type not in _TASK_WORKLOG_TYPES


def _sig_a_attribution_drift(project_root: Path) -> list[ValidationError]:
    """Signature (a) — worklog event emitted under an active TASK with no ``task_id``.

    Scans ``.gzkit/ledger.jsonl`` for any worklog event (per ``_TASK_WORKLOG_TYPES``)
    that lacks a ``task_id`` field while a TASK is active in scope at its emission
    time. "Active TASK in scope" is computed per OBPI: a TASK is active between its
    ``task_started`` event and its terminal (``task_completed``/``task_blocked``/
    ``task_escalated``) event for the same OBPI.

    Heavy-fail: each missing-``task_id`` worklog event yields one ValidationError.
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
        if any_active and not task_id:
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
                tasks_by_obpi.setdefault(obpi_id, set()).add(task_id)
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
        tasks = tasks_by_obpi.get(obpi_id, set())
        if not tasks:
            continue
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
    brief_fms = _collect_obpi_brief_frontmatter(project_root)
    fm_tasks = brief_fms.get(obpi_id, {}).get("tasks") or []
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
        if ev.get("event") == "task_started" and ev.get("obpi_id") == obpi_id and ev.get("task_id"):
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
    advances_map = _advances_channel_map()
    frontmatter_map = _frontmatter_channel_map(brief_fms)
    commit_trailer_map = _commit_trailer_channel_map(project_root)

    # OBPIs come from authored briefs plus any with ledger task_started events
    # even without a brief.
    obpi_ids = set(brief_fms.keys()) | ledger_obpis

    for obpi_id in sorted(obpi_ids):
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
        # Drift = at least one non-empty channel disagrees with the union.
        diverging_channels = sorted(ch for ch, tids in non_empty.items() if tids != all_tasks)
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


def _validate_task_envelope_coherence(project_root: Path) -> list[ValidationError]:
    """Validate task envelope coherence (OBPI-0.0.64-04).

    Composite of three Heavy-fail signatures:
        (a) worklog event under active TASK with no ``task_id`` (attribution drift)
        (b) OBPI default-bucket-only TASKs without ``req_atomic`` exemption
        (c) layer-drift across the four discovery channels (@advances, frontmatter
            tasks:, commit trailer, ledger task_id)

    All ValidationError instances carry ``type="task_envelope_coherence"`` and
    route to exit 3 via ``_POLICY_BREACH_ERROR_TYPES``.
    """
    errors: list[ValidationError] = []
    errors.extend(_sig_a_attribution_drift(project_root))
    errors.extend(_sig_b_subdivision_skipped(project_root))
    errors.extend(_sig_c_layer_drift(project_root))
    return errors
