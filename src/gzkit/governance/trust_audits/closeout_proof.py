"""Derived closeout-proof view (ADR-0.0.69 / OBPI-0.0.69-03).

Recomputes per-REQ proof for in-closeout ADRs over the three REQ-kind channels
on every run. Never reads proof from a stored artifact (Boundary Invariant 2).

Exit contract (communicated via return value to validate_cmd):
    []          → all proven  → exit 0
    non-empty   → any unproven → exit 3
An I/O error reading a ceremony/brief never propagates: on the gate path
(explicit ``adr_id``) it is converted to a fail-close ValidationError (exit 3);
on the ``gz check`` sweep path one unreadable sibling is tolerated (return []).
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError as PydanticValidationError

from gzkit.core.validation_rules import ValidationError

if TYPE_CHECKING:
    from collections.abc import Callable

_REQ_LINE_RE = re.compile(
    r"^\s*-\s*\[[ xX]\]\s*(REQ-[\d]+\.[\d]+\.[\d]+-[\d]+-[\d]+)",
    re.IGNORECASE,
)
_KIND_TAG_RE = re.compile(r"\[(BEHAVIOR|SUPPORT|STRUCTURAL[_-]FENCE)\]", re.IGNORECASE)
_RERUN_CMD_RE = re.compile(r"(?:uv\s+run\s+)?(gz\s+validate\s+--\S+)")
_AC_HEADING_RE = re.compile(r"^##\s+Acceptance\s+Criteria\s*$", re.IGNORECASE | re.MULTILINE)
_COVERS_RE = re.compile(r'@covers\s*\(\s*["\']([^"\']+)["\']\s*\)', re.IGNORECASE)

# A ceremony swept by the gz-check path must have been touched within this window
# to count as an *active* closeout. Parked ceremonies (e.g. a step-6 state left
# untouched for days) are excluded from gz-check failure — the explicit-adr_id
# ceremony-gate path always enforces regardless of freshness, so the actual
# EXECUTE->ATTESTATION advance is never weakened (operator ruling 2026-06-10).
_ACTIVE_CLOSEOUT_WINDOW_HOURS = 24


def _parse_reqs_from_brief(body: str) -> list[tuple[str, str | None, str]]:
    """Return (req_id, kind, full_line) tuples from the Acceptance Criteria section."""
    m = _AC_HEADING_RE.search(body)
    if not m:
        return []
    section = body[m.end() :]
    next_h2 = re.search(r"^##\s", section, re.MULTILINE)
    if next_h2:
        section = section[: next_h2.start()]

    results = []
    for line in section.splitlines():
        req_match = _REQ_LINE_RE.match(line)
        if not req_match:
            continue
        req_id = req_match.group(1)
        kind_match = _KIND_TAG_RE.search(line)
        kind = kind_match.group(1).upper().replace("-", "_") if kind_match else None
        results.append((req_id, kind, line))
    return results


def _find_covers_in_tests(project_root: Path, req_id: str) -> bool:
    """Return True if any test file under project_root/tests declares @covers(req_id)."""
    tests_root = project_root / "tests"
    if not tests_root.is_dir():
        return False
    for py_file in tests_root.rglob("*.py"):
        try:
            text = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for found_id in _COVERS_RE.findall(text):
            if found_id.strip() == req_id:
                return True
    return False


def _extract_rerun_command(line: str) -> str | None:
    """Extract the first `gz validate --<scope>` from a REQ line, normalized to `uv run`."""
    m = _RERUN_CMD_RE.search(line)
    if not m:
        return None
    cmd = m.group(1)
    if not cmd.startswith("uv run "):
        cmd = f"uv run {cmd}"
    return cmd


def _find_obpi_briefs(project_root: Path, adr_id: str) -> list[Path]:
    """Locate OBPI brief files for the given ADR ID."""
    pattern = f"docs/design/adr/**/{adr_id}/obpis/*.md"
    return list(project_root.glob(pattern))


def _is_in_closeout(ceremony: dict) -> bool:
    """Return True when a ceremony state indicates closeout is in progress."""
    return ceremony.get("completed_at") is None


def _parse_ts(value: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp (accepting a trailing ``Z``) to aware UTC."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _is_active_closeout(ceremony: dict, now: datetime) -> bool:
    """Return True when an in-progress ceremony was touched within the active window.

    Used only by the gz-check sweep (no explicit ``adr_id``): a parked ceremony
    left untouched longer than ``_ACTIVE_CLOSEOUT_WINDOW_HOURS`` is not treated as
    an active closeout and is excluded from gz-check failure. The explicit-adr_id
    ceremony-gate path bypasses this and always enforces.
    """
    if not _is_in_closeout(ceremony):
        return False
    touched = _parse_ts(ceremony.get("updated_at")) or _parse_ts(ceremony.get("started_at"))
    if touched is None:
        # No timestamp to age against — treat as active (fail-safe toward enforcement).
        return True
    age_hours = (now - touched).total_seconds() / 3600
    return age_hours <= _ACTIVE_CLOSEOUT_WINDOW_HOURS


def _err(artifact: str, message: str) -> ValidationError:
    """Build a ``closeout_proof`` ValidationError."""
    return ValidationError(type="closeout_proof", artifact=artifact, message=message)


def _enforcement_floor_green(project_root: Path) -> bool:
    """Return True when the OBPI-19 enforcement floor passes (no FACADE/TEST_BUG).

    A meta-property structural-fence proves via this floor at ADR closeout
    (``req_kind.is_meta_property_enforcement_fence``), so its closeout deferral is
    gated on this returning True. Mirrors ``quality.run_enforcement_floor_audit``
    success (every discovered claim PASSes) and adds a ``verified_count > 0``
    guard so an empty registry never reads as a false green. READ-ONLY
    (``root=None`` → no ledger mutation). ``project_root`` is accepted for a
    uniform helper signature and future per-project scoping.
    """
    from gzkit.enforcement import run_meta_validator  # noqa: PLC0415

    result = run_meta_validator(root=None)
    return result.verified_count > 0 and result.facade_count == 0 and result.test_bug_count == 0


def _withdrawn_obpi_ids(project_root: Path) -> set[str]:
    """Return OBPI ids carrying an ``obpi_withdrawn`` event in the ledger.

    A withdrawn OBPI (e.g. one superseded by a sibling ADR) was never built;
    demanding @covers proof for its REQs at the parent ADR's closeout is a
    false positive. The withdrawn signal is read directly from the event
    stream so it holds even when the OBPI has no ``obpi_created`` ancestor in
    the graph (the explicit withdrawal IS the disposition).
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.is_file():
        return set()
    withdrawn: set[str] = set()
    try:
        for raw in ledger_path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if ev.get("event") == "obpi_withdrawn" and isinstance(ev.get("id"), str):
                withdrawn.add(ev["id"])
    except OSError:
        return set()
    return withdrawn


def _waived_req_ids(project_root: Path) -> set[str]:
    """Return REQ ids waived in ``data/behave_coverage_waivers.json``.

    The waiver registry is the canonical operator-attested record of REQs that
    are legitimately uncovered — most importantly REQs whose covering test was
    *removed* by a superseding OBPI (e.g. a staging behavior replaced by a
    fail-closed one). Such REQs have no @covers test by design; the closeout
    proof must honor the waiver rather than re-demand the deleted test.
    """
    waiver_path = project_root / "data" / "behave_coverage_waivers.json"
    if not waiver_path.is_file():
        return set()
    try:
        payload = json.loads(waiver_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    waived: set[str] = set()
    waivers = payload.get("waivers", {})
    if isinstance(waivers, dict):
        for entry in waivers.values():
            if isinstance(entry, dict) and isinstance(entry.get("waived_reqs"), list):
                waived.update(r for r in entry["waived_reqs"] if isinstance(r, str))
    return waived


def _check_req(
    project_root: Path,
    artifact: str,
    req_id: str,
    kind: str | None,
    line: str,
    waived_reqs: set[str],
    floor_green: Callable[[], bool],
) -> ValidationError | None:
    """Recompute one REQ's proof over its channel; return an error if unproven."""
    from gzkit.req_kind_fence import (
        is_meta_property_enforcement_fence,
        resolve_fence_proof,
    )
    from gzkit.req_kind_support import resolve_support_proof

    if req_id in waived_reqs:
        return None
    if kind is None:
        return _err(
            artifact,
            f"{req_id}: no inline [kind] tag — explicit tags required at closeout "
            f"(ruling 6.2-A). Tag as [BEHAVIOR], [SUPPORT], or [STRUCTURAL-FENCE].",
        )
    if kind == "BEHAVIOR":
        if _find_covers_in_tests(project_root, req_id):
            return None
        return _err(
            artifact,
            f'{req_id} [BEHAVIOR]: no @covers("{req_id}") found in tests/. '
            f"Add a @covers decorator to the covering test.",
        )
    if kind == "SUPPORT":
        req_text = line.split(":", 1)[-1].strip() if ":" in line else line
        try:
            proof_status = resolve_support_proof(req_text, project_root, req_id=req_id)
        except PydanticValidationError as exc:
            return _err(
                artifact,
                f"{req_id} [SUPPORT]: data/support_proof_grandfather.json is "
                f"malformed ({exc}) — GHI #660 fail-closes this instead of "
                f"silently tolerating an empty grandfather set. Fix the JSON "
                f"file, then re-run: uv run gz validate --closeout-proof",
            )
        # "grandfathered-support" (GHI #647) is a tolerated pre-cutover hollow
        # proof — non-failing, like "pass", until repaired off the snapshot.
        if proof_status in ("pass", "grandfathered-support"):
            return None
        if proof_status == "undeclared-support":
            return _err(
                artifact,
                f"{req_id} [SUPPORT]: undeclared-support — the REQ declares no "
                f"unambiguous witness clause, so no proof channel was resolved "
                f"(GHI #888). Append exactly one clause of the form: Witnessed by "
                f"`<event_type>` [citing `<path>`] + `gz validate --<scope>`. "
                f"Re-run: uv run gz validate --closeout-proof",
            )
        rerun = _extract_rerun_command(line)
        suffix = f" Re-run: {rerun}" if rerun else ""
        return _err(artifact, f"{req_id} [SUPPORT]: {proof_status}.{suffix}")
    if kind == "STRUCTURAL_FENCE":
        # Pass req_text so resolve_fence_proof can apply the OBPI-0.0.74-18
        # enforcement-asserting upgrade (BI#10): a fence whose text asserts
        # enforcement resolves "pass" only when its named @enforces claim is
        # registered, not merely when the ADR carries a ## Boundary Invariants
        # heading. Dropping req_text bypassed that upgrade at the binding
        # closeout gate (GHI #649) — it must mirror the gz covers call site
        # (req_kind.py) and the SUPPORT branch above.
        req_text = line.split(":", 1)[-1].strip() if ":" in line else line
        proof_status = resolve_fence_proof(req_id, project_root, req_text)
        if proof_status == "pass":
            return None
        # A meta-property enforcement fence names no single bindable claim (e.g.
        # "the registry has no _NEGATIVE_CONTROL_DEBT escape"). It is not per-claim
        # provable here; it proves via the OBPI-19 enforcement floor at ADR closeout
        # (req_kind.is_meta_property_enforcement_fence contract). Defer it to the
        # floor: proven iff the floor is green. A single-claim fence skips this and
        # keeps the OBPI-18 teeth below.
        if is_meta_property_enforcement_fence(req_text):
            if floor_green():
                return None
            return _err(
                artifact,
                f"{req_id} [STRUCTURAL-FENCE]: meta-property fence — the OBPI-19 "
                f"enforcement floor that proves it is RED. Run "
                f"`uv run gz validate --qc-binding` and fix the FACADE/TEST_BUG so "
                f"the floor proves it.",
            )
        return _err(
            artifact,
            f"{req_id} [STRUCTURAL-FENCE]: {proof_status}. "
            f"For a state-property fence, add a parent-ADR '## Boundary "
            f"Invariants' anchor; for an enforcement-asserting fence "
            f"(text says X is enforced/fail-closes/has a live NC), register "
            f"its named @enforces claim with a passing un-forced NC.",
        )
    return None


def _check_brief(
    project_root: Path,
    adr_id: str,
    brief_path: Path,
    waived_reqs: set[str],
    floor_green: Callable[[], bool],
    *,
    fail_close: bool,
) -> list[ValidationError]:
    """Recompute proof for every REQ in one OBPI brief.

    ``fail_close`` is set on the explicit-adr_id gate path: an unreadable brief
    there is a fail-close error (a corrupt/missing target must block the gate),
    never silently treated as proven. On the sweep path (``fail_close=False``)
    an unreadable sibling brief is tolerated so one bad file does not break the
    whole ``gz check`` run.
    """
    artifact = f"{adr_id}/{brief_path.stem}"
    try:
        body = brief_path.read_text(encoding="utf-8")
    except OSError as exc:
        if fail_close:
            return [_err(artifact, f"brief could not be read (fail-close): {exc}")]
        return []
    results = (
        _check_req(project_root, artifact, req_id, kind, line, waived_reqs, floor_green)
        for req_id, kind, line in _parse_reqs_from_brief(body)
    )
    return [e for e in results if e is not None]


def _resolve_ceremony_files(ceremonies_dir: Path, adr_id: str | None) -> list[Path]:
    """Resolve the ceremony files to sweep: one for an explicit adr_id, else all."""
    if adr_id is not None:
        target = ceremonies_dir / f"{adr_id}.ceremony.json"
        return [target] if target.exists() else []
    return list(ceremonies_dir.glob("*.ceremony.json"))


def validate_closeout_proof(
    project_root: Path,
    *,
    adr_id: str | None = None,
) -> list[ValidationError]:
    """Recompute per-REQ proof for in-closeout ADRs over three channels.

    Returns an empty list when all REQs are proven (exit 0).
    Returns ValidationError entries when any REQ is unproven (exit 3).
    Never reads from a stored proof artifact (Boundary Invariant 2).
    """
    ceremonies_dir = project_root / ".gzkit" / "ceremonies"
    if not ceremonies_dir.is_dir():
        return []

    # Explicit adr_id (ceremony gate) → enforce on that ADR unconditionally.
    # No adr_id (gz-check sweep) → only enforce on freshly-active ceremonies.
    scan_all = adr_id is None
    now = datetime.now(UTC)
    errors: list[ValidationError] = []
    withdrawn_obpis = _withdrawn_obpi_ids(project_root)
    waived_reqs = _waived_req_ids(project_root)

    # Memoize the floor result: a meta-property structural-fence defers to the
    # OBPI-19 enforcement floor, but the floor (the meta-validator) is run at most
    # once per call and only when a meta-property fence actually needs it.
    _floor_cache: list[bool] = []

    def floor_green() -> bool:
        if not _floor_cache:
            _floor_cache.append(_enforcement_floor_green(project_root))
        return _floor_cache[0]

    for ceremony_path in _resolve_ceremony_files(ceremonies_dir, adr_id):
        try:
            ceremony = json.loads(ceremony_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            # Gate path (explicit adr_id) → a corrupt/unreadable ceremony for the
            # gated ADR must fail-close. Sweep path → tolerate one bad sibling so
            # a stray corruption does not break the whole gz-check run.
            if not scan_all:
                errors.append(
                    _err(
                        ceremony_path.stem.replace(".ceremony", ""),
                        f"ceremony file could not be read (fail-close): {exc}",
                    )
                )
            continue

        active = _is_active_closeout(ceremony, now) if scan_all else _is_in_closeout(ceremony)
        if not active:
            continue

        this_adr_id = ceremony.get("adr_id", ceremony_path.stem.replace(".ceremony", ""))
        for brief_path in _find_obpi_briefs(project_root, this_adr_id):
            if brief_path.stem in withdrawn_obpis:
                continue  # withdrawn OBPI never built — not a coverage gap
            errors.extend(
                _check_brief(
                    project_root,
                    this_adr_id,
                    brief_path,
                    waived_reqs,
                    floor_green,
                    fail_close=not scan_all,
                )
            )

    return errors
