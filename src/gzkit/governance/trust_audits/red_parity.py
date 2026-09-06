"""RED-parity trust audit — BEHAVIOR REQs must carry a falsifiability witness (GHI #642).

``@covers`` parity proves a BEHAVIOR REQ has a covering test. It never proves that
test can fail. A test authored after the production code, passing on its first run,
satisfies coverage identically to a genuine RED-first test — so the pipeline's
Red-Green-Refactor instruction had no mechanical witness at all.

This audit is that witness's read-path. For every BEHAVIOR REQ in a heavy-lane brief
whose completion receipt postdates the cutover, the ledger must carry a
``red_receipt_emitted`` event, and that event's ``failure_class`` may not be ``none``
— a test that passes with the production hunks withheld cannot fail, which is exactly
the ``AGENTS.md`` § DO IT RIGHT Rule 6 defect.

Per ADR-0.0.74 §5, an enforcement claim with no live negative control is a facade.
The pipeline asserts test-first discipline; this audit plus its paired NC is what
stops that claim from being one.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

from gzkit.validate import ValidationError

if TYPE_CHECKING:
    from collections.abc import Iterator

_LEDGER_REL = ".gzkit/ledger.jsonl"
_ADR_ROOT_REL = "docs/design/adr"
_ERR_TYPE = "red_parity"

# The instant `gz arb red` and this audit landed (GHI #642). Briefs whose completion
# receipt predates it are out of scope: no RED witness could have been captured, and
# synthesising one after the fact would fabricate the very evidence this gate exists
# to make un-fabricable. Registered as a `dated-cutover` honesty mechanism.
CUTOVER = dt.datetime(2026, 7, 9, 12, 0, tzinfo=dt.UTC)

_TERMINAL_STATUSES = frozenset({"Completed", "Validated"})
_LANE_RE = re.compile(r"^lane:\s*[\"']?(\w+)", re.MULTILINE)
_STATUS_RE = re.compile(r"^status:\s*[\"']?([\w-]+)", re.MULTILINE)


def _is_void_witness(event: dict) -> bool:
    """Report whether a RED event says the run could not tell, rather than what it found.

    Two shapes, and they are the same claim (GHI #839, #849):

    * ``not-applicable`` — nothing was withheld, so the experiment never ran.
    * ``error`` on a ``reconstructed`` base — the test met a tree months older than
      itself and died on an import. That is as likely to be unrelated drift as the
      missing implementation, so banking it as a weak RED would let a hollow test in
      old code clear this gate. Fail-OPEN, which is why it is excluded here rather
      than merely reported.

    An event with no ``base_provenance`` predates the reconstructed base and therefore
    ran against HEAD, where ``error`` IS a legitimate weak RED — so the field's absence
    must read as ``working-tree``, never as unknown.
    """
    failure_class = event.get("failure_class")
    if failure_class == "not-applicable":
        return True
    provenance = event.get("base_provenance", "working-tree")
    return failure_class == "error" and provenance == "reconstructed"


def _iter_ledger(project_root: Path) -> Iterator[dict]:
    """Yield each well-formed ledger event; skip unparseable lines."""
    try:
        text = (project_root / _LEDGER_REL).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            yield event


def _event_ts(event: dict) -> dt.datetime | None:
    """Return a UTC-aware timestamp, reading naive values as UTC."""
    raw = event.get("ts")
    if not isinstance(raw, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.UTC)


def _collect(project_root: Path) -> tuple[dict[str, dict], dict[str, dt.datetime]]:
    """Single ledger pass: RED witnesses by REQ, and completion instants by OBPI."""
    witnesses: dict[str, dict] = {}
    completions: dict[str, dt.datetime] = {}
    for event in _iter_ledger(project_root):
        name = event.get("event")
        if name == "red_receipt_emitted":
            req_id = event.get("req_id")
            # A run that witnessed nothing is not recorded here (GHI #839, #849).
            # Skipping rather than storing also keeps it from OVERWRITING an earlier
            # genuine witness for the same REQ — this dict keeps the last event per
            # REQ, so a void re-run after a real one would otherwise erase the finding
            # it could not reproduce.
            if isinstance(req_id, str) and not _is_void_witness(event):
                witnesses[req_id] = event
        elif name == "obpi_receipt_emitted" and event.get("receipt_event") == "completed":
            obpi_id = event.get("obpi_id") or event.get("id")
            ts = _event_ts(event)
            if isinstance(obpi_id, str) and ts is not None:
                completions[obpi_id] = ts
    return witnesses, completions


def _behavior_reqs(brief_path: Path) -> list[str]:
    """Return the brief's BEHAVIOR-kind REQs.

    An untagged REQ defaults to BEHAVIOR, matching the fail-closed default in
    ``.gzkit/rules/tests.md`` § REQ Scope Discipline. Relying on
    ``parse_brief_req_kinds`` alone would silently drop every legacy untagged REQ.
    """
    from gzkit.governance.req_coverage import parse_brief_req_kinds, parse_brief_reqs

    kinds = parse_brief_req_kinds(brief_path)
    return [req for req in parse_brief_reqs(brief_path) if kinds.get(req, "BEHAVIOR") == "BEHAVIOR"]


def _brief_is_in_scope(text: str) -> bool:
    """Heavy lane, terminal status — the same bar Gate 3 and Gate 4 answer to."""
    lane = _LANE_RE.search(text)
    status = _STATUS_RE.search(text)
    if lane is None or lane.group(1).lower() != "heavy":
        return False
    return status is not None and status.group(1) in _TERMINAL_STATUSES


def _missing_witness_error(obpi_id: str, req_id: str, brief_rel: str) -> ValidationError:
    return ValidationError(
        type=_ERR_TYPE,
        artifact=f"{brief_rel}:{req_id}",
        message=(
            f"BEHAVIOR REQ '{req_id}' in completed heavy-lane OBPI '{obpi_id}' carries no "
            "'red_receipt_emitted' witness. `@covers` parity proves the REQ has a covering "
            "test; it never proves that test can fail. Recovery: run `uv run gz arb red "
            f"--req {req_id} --obpi {obpi_id}` to run the covering test against the base "
            "tree with the production hunks withheld (GHI #642)."
        ),
    )


def _unfalsifiable_error(obpi_id: str, req_id: str, brief_rel: str) -> ValidationError:
    return ValidationError(
        type=_ERR_TYPE,
        artifact=f"{brief_rel}:{req_id}",
        message=(
            f"BEHAVIOR REQ '{req_id}' in OBPI '{obpi_id}' has a RED witness with "
            "failure_class 'none': its covering test PASSED against the base tree with "
            "the production hunks withheld. A test that passes without its implementation "
            "cannot fail when the business logic changes (AGENTS.md § DO IT RIGHT Rule 6), "
            "so it witnesses nothing. Recovery: rewrite the test to assert the REQ's "
            f"semantics, then re-run `uv run gz arb red --req {req_id}`."
        ),
    )


def audit_red_parity(project_root: Path) -> list[ValidationError]:
    """Post-cutover heavy-lane BEHAVIOR REQs must carry a non-'none' RED witness."""
    adr_root = project_root / _ADR_ROOT_REL
    if not adr_root.is_dir():
        return []

    witnesses, completions = _collect(project_root)
    errors: list[ValidationError] = []

    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        obpi_id = brief.stem
        completed_at = completions.get(obpi_id)
        if completed_at is None or completed_at < CUTOVER:
            continue
        try:
            text = brief.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not _brief_is_in_scope(text):
            continue

        brief_rel = brief.relative_to(project_root).as_posix()
        for req_id in _behavior_reqs(brief):
            witness = witnesses.get(req_id)
            if witness is None:
                errors.append(_missing_witness_error(obpi_id, req_id, brief_rel))
            elif witness.get("failure_class") == "none":
                errors.append(_unfalsifiable_error(obpi_id, req_id, brief_rel))

    return errors
