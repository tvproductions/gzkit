"""Observe registered ledger producers in fresh disposable projects (GHI #985).

These executions demonstrate wiring, never live project activity or acceptance.
No report is loaded as evidence, and the caller's project is never a write target.
"""

import hashlib
import json
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit import acceptance_store, reports
from gzkit.config import GzkitConfig, PathConfig
from gzkit.events import (
    AcceptanceRecordedEvent,
    MxSessionLeaseRenewedEvent,
    ObpiLockLeaseExpiredEvent,
    OutcomeTransitionedEvent,
    ReportPublishedEvent,
    ReqProofRecordedEvent,
    parse_typed_event,
)
from gzkit.models.catalog import CATALOG_FILES, Catalog, load_catalog
from gzkit.registries import registry_path

_OBPI = "OBPI-0.1.0-01-producer-probe"
_AUTHOR = "isolated-producer-probe"
_REQ = "REQ-0.1.0-01-01"
_OUTCOME = "H1"
_CATALOG_REQ = "REQ-1"
_BRIEF_PATH = f"design/adr/obpis/{_OBPI}.md"
_STATEMENT = "Retain the canonical acceptance obligation."


class ProducerObservation(BaseModel):
    """Result of this invocation, separated from live ledger statistics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_type: str = Field(description="Declared event type being probed")
    producer: str = Field(default="", description="Real producer invoked in isolation")
    status: Literal["verified", "failed", "unsupported"] = Field(
        description="Whether this fresh producer execution met its contract"
    )
    ledger_sha256: str = Field(default="", description="Digest of observed disposable ledger bytes")
    record_count: int = Field(default=0, ge=0, description="Verified persisted record count")
    subject: str = Field(default="", description="Verified isolated record subject")
    author_id: str = Field(default="", description="Verified contract author")
    obligation_ids: tuple[str, ...] = Field(
        default=(), description="Verified canonical obligations"
    )
    error: str = Field(default="", description="Observed failure, without granting producer credit")


def _prepare_acceptance_project(root: Path) -> None:
    """Seat a minimal canonical fixture; no ledger rows are fabricated."""
    brief = root / _BRIEF_PATH
    brief.parent.mkdir(parents=True)
    (root / ".gzkit.json").write_text(
        json.dumps({"paths": {"design_root": "design"}}), encoding="utf-8"
    )
    brief.write_text(
        f"---\nid: {_OBPI}\nparent: ADR-0.1.0-producer-probe\nreqs:\n- {_REQ}\n---\n"
        "# Producer probe\n## Objective\nCapture an acceptance contract.\n"
        f"## Acceptance Criteria\n- [ ] {_REQ} [BEHAVIOR]: {_STATEMENT}\n",
        encoding="utf-8",
    )
    (root / "design/adr/ADR-0.1.0-producer-probe.md").write_text(
        "# Producer probe\n## Decision\nPreserve canonical acceptance obligations.\n",
        encoding="utf-8",
    )


def _observe_acceptance_contract(root: Path) -> ProducerObservation:
    """Validate actual bytes independently of the initializer's return value."""
    persisted = (root / ".gzkit/ledger.jsonl").read_bytes()
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 1:
        raise ValueError("Producer must persist exactly one initial contract record")
    event = parse_typed_event(rows[0])
    if not isinstance(event, AcceptanceRecordedEvent):
        raise ValueError("Producer persisted the wrong event type")
    if event.id != _OBPI or event.record_type != "contract":
        raise ValueError("Producer persisted the wrong subject or acceptance record kind")
    contract = acceptance_store.Contract.model_validate(event.payload)
    if contract.author_id != _AUTHOR or len(contract.obligations) != 1:
        raise ValueError("Producer did not preserve the author and obligation population")
    obligation = contract.obligations[0]
    observed = (obligation.id, obligation.kind, obligation.statement, obligation.authority)
    expected = (_REQ, "BEHAVIOR", _STATEMENT, f"{_BRIEF_PATH}#acceptance-criteria")
    if observed != expected:
        raise ValueError("Persisted obligation disagrees with the canonical fixture")
    return ProducerObservation(
        event_type="acceptance_recorded",
        producer="gzkit.acceptance_store.initialize",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
        author_id=contract.author_id,
        obligation_ids=(obligation.id,),
    )


def _probe_report(root: Path) -> ProducerObservation:
    """Publish fixture bytes and independently inspect durable source, event and views."""
    content = b"# Isolated producer probe\r\n\r\nNot a live project assessment.\r\n"
    report_id = "isolated-report-probe"
    path = f"manual/reports/big-picture/{report_id}.md"
    source = root / "draft.md"
    source.write_bytes(content)
    config = GzkitConfig(paths=PathConfig(docs_root="manual", ledger="state/events.jsonl"))
    reports.publish_report(
        root, config, source, report_id, period="isolated fixture", evidence_cutoff="fixture"
    )
    persisted = (root / "state/events.jsonl").read_bytes()
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 1:
        raise ValueError("Report producer must persist exactly one publication record")
    event = parse_typed_event(rows[0])
    if not isinstance(event, ReportPublishedEvent):
        raise ValueError("Report producer persisted the wrong event type")
    observed = (
        event.id,
        event.path,
        event.sha256,
        event.period,
        event.evidence_cutoff,
        event.predecessor,
    )
    expected = (
        report_id,
        path,
        hashlib.sha256(content).hexdigest(),
        "isolated fixture",
        "fixture",
        None,
    )
    if observed != expected:
        raise ValueError("Publication witness disagrees with the authored fixture")
    directory = (root / path).parent
    if (root / path).read_bytes() != content or (directory / "current.md").read_bytes() != content:
        raise ValueError("Published assessment or current view differs from exact source bytes")
    index = (directory / "index.md").read_text(encoding="utf-8")
    if f"[{report_id}]({report_id}.md)" not in index:
        raise ValueError("Archive index does not link the retained assessment")
    return ProducerObservation(
        event_type="report_published",
        producer="gzkit.reports.publish_report",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_lock_lease_expiry(root: Path) -> ProducerObservation:
    """Seat one expired work lock and reap; the expiry must be booked and the lock kept.

    Operator ruling 2026-10-18: an expired work lock is booked, never evicted. A reaper
    that books nothing, or books and evicts, has not met that contract.
    """
    from gzkit import lock_manager  # noqa: PLC0415 - the data layer; import only when probed
    from gzkit.ledger import Ledger  # noqa: PLC0415

    claimed_at = (datetime.now(UTC) - timedelta(minutes=10)).isoformat()
    lock_manager.write_lock(
        root,
        lock_manager.LockData(
            obpi_id=_OBPI,
            agent=_AUTHOR,
            pid=0,
            session_id=_AUTHOR,
            claimed_at=claimed_at,
            branch="main",
            ttl_minutes=1,
        ),
    )
    ledger_path = root / ".gzkit/ledger.jsonl"
    lock_manager.reap_expired_locks(root, ledger=Ledger(ledger_path), reaper_agent=_AUTHOR)
    if lock_manager.read_lock(root, _OBPI) is None:
        raise ValueError("Reaper evicted an expired work lock instead of keeping it held")
    persisted = ledger_path.read_bytes() if ledger_path.is_file() else b""
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 1:
        raise ValueError("Reaper must persist exactly one lease-expiry record")
    event = parse_typed_event(rows[0])
    if not isinstance(event, ObpiLockLeaseExpiredEvent):
        raise ValueError("Reaper persisted the wrong event type")
    if (event.id, event.claimed_at, event.ttl_minutes) != (_OBPI, claimed_at, 1):
        raise ValueError("Lease-expiry record disagrees with the expired lock")
    return ProducerObservation(
        event_type="obpi_lock_lease_expired",
        producer="gzkit.lock_manager.reap_expired_locks",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_mx_lease_renewal(root: Path) -> ProducerObservation:
    """Open a disposable hangar and renew it; one renewal booked, the session kept open.

    Operator ruling 2026-10-20: renewal is lease-only. A renewal that books nothing, or
    that ends the session or drops the marker, has not met that contract (GHI #1261).
    """
    from gzkit import lock_manager  # noqa: PLC0415 - the data layer; import only when probed
    from gzkit.commands import mx_cmd  # noqa: PLC0415 - a command handler; import only when probed
    from gzkit.mx import marker  # noqa: PLC0415

    (root / ".gzkit").mkdir()
    try:
        with mx_cmd.console.capture():
            mx_cmd.mx_enter_cmd(
                reason="probe", attestor=_AUTHOR, inspection_scope=[], project_root=root
            )
            mx_cmd.mx_renew_cmd(_AUTHOR, project_root=root)
    except SystemExit as exc:
        raise ValueError(f"Renewal refused with exit {exc.code}") from exc
    if not marker.is_valid(root):
        raise ValueError("Renewal ended the session or dropped its marker")
    ledger_path = root / ".gzkit/ledger.jsonl"
    persisted = ledger_path.read_bytes() if ledger_path.is_file() else b""
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    renewals = [row for row in rows if row.get("event") == "mx_session_lease_renewed"]
    if len(renewals) != 1 or any(row.get("event") == "mx_session_closed" for row in rows):
        raise ValueError("Renewal must persist exactly one renewal record and no close")
    event = parse_typed_event(renewals[0])
    if not isinstance(event, MxSessionLeaseRenewedEvent):
        raise ValueError("Renewal persisted the wrong event type")
    lock = lock_manager.read_lock(root, marker.SESSION_LOCK_KEY)
    if lock is None or lock.claimed_at != event.renewed_at or lock.session_id != event.session_id:
        raise ValueError("The session lock does not carry the renewed lease")
    return ProducerObservation(
        event_type="mx_session_lease_renewed",
        producer="gzkit.commands.mx_cmd.mx_renew_cmd",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.session_id,
    )


def _seat_catalog(root: Path) -> Catalog:
    """Seat a one-outcome, one-REQ catalog and read it through the real seam."""
    files = {
        "families": [{"code": "H", "band": "product", "name": "probe", "scope": "Probe."}],
        "outcomes": [
            {
                "code": _OUTCOME,
                "statement": _STATEMENT,
                "owner": _AUTHOR,
                "user_facing": False,
                "governed_by": [],
                "depends_on": [],
                "feature": None,
                "retired": False,
            }
        ],
        "reqs": [
            {
                "id": _CATALOG_REQ,
                "member_of": _OUTCOME,
                "statement": _STATEMENT,
                "criteria": [
                    {"state_or_input": "probe", "required_outcome": "probe", "evidence": "probe"}
                ],
                "kind": "BEHAVIOR",
                "revision": 1,
                "derives_from": [],
                "applies_to": [],
            }
        ],
        "externals": [],
    }
    for kind, entries in files.items():
        path = registry_path(root, CATALOG_FILES[kind])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"_doc": "isolated probe", kind: entries}), encoding="utf-8")
    (root / ".gzkit").mkdir()
    return load_catalog(root)


def _expect_refusal(write: Callable[[], object], case: str) -> None:
    """Require a refusal; a writer that books what the grammar refuses fails its contract."""
    from gzkit.catalog_ledger import CatalogLedgerError  # noqa: PLC0415 - import only when probed

    try:
        write()
    except CatalogLedgerError:
        return
    raise ValueError(f"Writer accepted {case}")


def _single_row(ledger_path: Path) -> tuple[bytes, dict[str, object]]:
    persisted = ledger_path.read_bytes() if ledger_path.is_file() else b""
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 1:
        raise ValueError("Writer must persist exactly one record and nothing for a refusal")
    return persisted, rows[0]


def _probe_outcome_transition(root: Path) -> ProducerObservation:
    """Move a seated outcome one step, then try a skip; one move booked, the skip refused."""
    from gzkit import catalog_ledger  # noqa: PLC0415 - the writer; import only when probed
    from gzkit.ledger import Ledger  # noqa: PLC0415

    catalog = _seat_catalog(root)
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    catalog_ledger.record_outcome_transition(
        catalog, ledger, _OUTCOME, "designing", evidence=_AUTHOR
    )
    _expect_refusal(
        lambda: catalog_ledger.record_outcome_transition(
            catalog, ledger, _OUTCOME, "verified", evidence=_AUTHOR
        ),
        "a transition that skips the lifecycle",
    )
    persisted, row = _single_row(ledger_path)
    event = parse_typed_event(row)
    if not isinstance(event, OutcomeTransitionedEvent):
        raise ValueError("Writer persisted the wrong event type")
    if (event.id, event.from_state, event.to_state) != (_OUTCOME, "queued", "designing"):
        raise ValueError("Transition record disagrees with the one-step move")
    return ProducerObservation(
        event_type="outcome_transitioned",
        producer="gzkit.catalog_ledger.record_outcome_transition",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_req_proof(root: Path) -> ProducerObservation:
    """Prove a seated REQ, then try a fourth verdict; one proof booked, the verdict refused."""
    from gzkit import catalog_ledger  # noqa: PLC0415 - the writer; import only when probed
    from gzkit.ledger import Ledger  # noqa: PLC0415

    catalog = _seat_catalog(root)
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    catalog_ledger.record_req_proof(
        catalog, ledger, _CATALOG_REQ, 1, commit="0" * 7, verdict="SATISFIED", evidence=_AUTHOR
    )
    _expect_refusal(
        lambda: catalog_ledger.record_req_proof(
            catalog, ledger, _CATALOG_REQ, 1, commit="0" * 7, verdict="PASS", evidence=_AUTHOR
        ),
        "a fourth verdict",
    )
    persisted, row = _single_row(ledger_path)
    event = parse_typed_event(row)
    if not isinstance(event, ReqProofRecordedEvent):
        raise ValueError("Writer persisted the wrong event type")
    if (event.id, event.revision, event.verdict) != (_CATALOG_REQ, 1, "SATISFIED"):
        raise ValueError("Proof record disagrees with the REQ the catalog holds")
    return ProducerObservation(
        event_type="req_proof_recorded",
        producer="gzkit.catalog_ledger.record_req_proof",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


_PRODUCERS = {
    "acceptance_recorded": "gzkit.acceptance_store.initialize",
    "report_published": "gzkit.reports.publish_report",
    "obpi_lock_lease_expired": "gzkit.lock_manager.reap_expired_locks",
    "mx_session_lease_renewed": "gzkit.commands.mx_cmd.mx_renew_cmd",
    "outcome_transitioned": "gzkit.catalog_ledger.record_outcome_transition",
    "req_proof_recorded": "gzkit.catalog_ledger.record_req_proof",
}


def probe_producer(event_type: str) -> ProducerObservation:
    """Run the registered producer now; unsupported and failed probes grant no credit."""
    if event_type not in _PRODUCERS:
        return ProducerObservation(event_type=event_type, status="unsupported")
    try:
        with tempfile.TemporaryDirectory(prefix="gzkit-ledger-producer-") as directory:
            root = Path(directory)
            if event_type == "report_published":
                return _probe_report(root)
            if event_type == "obpi_lock_lease_expired":
                return _probe_lock_lease_expiry(root)
            if event_type == "mx_session_lease_renewed":
                return _probe_mx_lease_renewal(root)
            if event_type == "outcome_transitioned":
                return _probe_outcome_transition(root)
            if event_type == "req_proof_recorded":
                return _probe_req_proof(root)
            _prepare_acceptance_project(root)
            acceptance_store.initialize(root, _OBPI, _AUTHOR)
            return _observe_acceptance_contract(root)
    except Exception as exc:  # noqa: BLE001 - a broken producer must fail this observation closed
        return ProducerObservation(
            event_type=event_type,
            producer=_PRODUCERS[event_type],
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )
