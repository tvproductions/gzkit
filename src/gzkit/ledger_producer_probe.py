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
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit import acceptance_store, reports
from gzkit.config import GzkitConfig, PathConfig
from gzkit.events import (
    AcceptanceRecordedEvent,
    BaselinedReq,
    LegacyUnitWithdrawnEvent,
    MxMarkerRepairedEvent,
    MxSessionLeaseRenewedEvent,
    ObpiLockLeaseExpiredEvent,
    OrderTransitionedEvent,
    OutcomeTransitionedEvent,
    ReportPublishedEvent,
    ReqProofRecordedEvent,
    WorkPackageBlockedEvent,
    WorkPackageChangedEvent,
    WorkPackageIssueClosedEvent,
    WorkPackageTransitionedEvent,
    parse_typed_event,
)
from gzkit.ledger_producer_probe_errors import (
    AcceptanceEventTypeError,
    AcceptanceObligationMismatchError,
    AcceptancePopulationError,
    AcceptanceRecordCountError,
    AcceptanceSubjectError,
    ArchiveIndexLinkError,
    ExpiredLockEvictedError,
    LeaseExpiryEventTypeError,
    LeaseExpiryMismatchError,
    LeaseExpiryRecordCountError,
    ProofMismatchError,
    PublicationMismatchError,
    PublishedBytesError,
    RenewalEndedSessionError,
    RenewalEventTypeError,
    RenewalRecordCountError,
    RenewalRefusedError,
    RenewedLeaseMissingError,
    ReportEventTypeError,
    ReportRecordCountError,
    TransitionMismatchError,
    WriterAcceptedRefusalError,
    WriterEventTypeError,
    WriterRecordCountError,
)
from gzkit.models.catalog import CATALOG_FILES, Catalog, load_catalog
from gzkit.pipeline_dispatch import MAX_REVIEW_FIX_CYCLES
from gzkit.registries import registry_path

if TYPE_CHECKING:
    from gzkit.ledger import Ledger

_OBPI = "OBPI-0.1.0-01-producer-probe"
_AUTHOR = "isolated-producer-probe"
_REQ = "REQ-0.1.0-01-01"
_OUTCOME = "H1"
_CATALOG_REQ = "REQ-1"
_WORK_PACKAGE = "WP-01-producer-probe"
_REPAIR_PACKAGE = "WP-02-producer-probe"
_ISSUE = 1
_ORDER = "ORD-01-producer-probe"
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
        raise AcceptanceRecordCountError
    event = parse_typed_event(rows[0])
    if not isinstance(event, AcceptanceRecordedEvent):
        raise AcceptanceEventTypeError
    if event.id != _OBPI or event.record_type != "contract":
        raise AcceptanceSubjectError
    contract = acceptance_store.Contract.model_validate(event.payload)
    if contract.author_id != _AUTHOR or len(contract.obligations) != 1:
        raise AcceptancePopulationError
    obligation = contract.obligations[0]
    observed = (obligation.id, obligation.kind, obligation.statement, obligation.authority)
    expected = (_REQ, "BEHAVIOR", _STATEMENT, f"{_BRIEF_PATH}#acceptance-criteria")
    if observed != expected:
        raise AcceptanceObligationMismatchError
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
        raise ReportRecordCountError
    event = parse_typed_event(rows[0])
    if not isinstance(event, ReportPublishedEvent):
        raise ReportEventTypeError
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
        raise PublicationMismatchError
    directory = (root / path).parent
    if (root / path).read_bytes() != content or (directory / "current.md").read_bytes() != content:
        raise PublishedBytesError
    index = (directory / "index.md").read_text(encoding="utf-8")
    if f"[{report_id}]({report_id}.md)" not in index:
        raise ArchiveIndexLinkError
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

    Returns:
        A ``verified`` observation of ``obpi_lock_lease_expired`` from the reaper, with the ledger's
        SHA-256, one record, and the OBPI as subject.

    Raises:
        ExpiredLockEvictedError: the reaper evicted the expired lock.
        LeaseExpiryRecordCountError: the reaper booked other than one record.
        LeaseExpiryEventTypeError: the booked record has the wrong event type.
        LeaseExpiryMismatchError: the booked record disagrees with the expired lock.

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
        raise ExpiredLockEvictedError
    persisted = ledger_path.read_bytes() if ledger_path.is_file() else b""
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 1:
        raise LeaseExpiryRecordCountError
    event = parse_typed_event(rows[0])
    if not isinstance(event, ObpiLockLeaseExpiredEvent):
        raise LeaseExpiryEventTypeError
    if (event.id, event.claimed_at, event.ttl_minutes) != (_OBPI, claimed_at, 1):
        raise LeaseExpiryMismatchError
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

    Returns:
        A ``verified`` observation of ``mx_session_lease_renewed`` from ``mx_renew_cmd``, with the
        ledger's SHA-256, one record, and the session id as subject.

    Raises:
        RenewalRefusedError: the renewal exited.
        RenewalEndedSessionError: the renewal ended the session or dropped its marker.
        RenewalRecordCountError: other than one renewal was booked, or a close was.
        RenewalEventTypeError: the booked record has the wrong event type.
        RenewedLeaseMissingError: the session lock does not carry the renewed lease.

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
        raise RenewalRefusedError(exc.code) from exc
    if not marker.is_valid(root):
        raise RenewalEndedSessionError
    ledger_path = root / ".gzkit/ledger.jsonl"
    persisted = ledger_path.read_bytes() if ledger_path.is_file() else b""
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    renewals = [row for row in rows if row.get("event") == "mx_session_lease_renewed"]
    if len(renewals) != 1 or any(row.get("event") == "mx_session_closed" for row in rows):
        raise RenewalRecordCountError
    event = parse_typed_event(renewals[0])
    if not isinstance(event, MxSessionLeaseRenewedEvent):
        raise RenewalEventTypeError
    lock = lock_manager.read_lock(root, marker.SESSION_LOCK_KEY)
    if lock is None or lock.claimed_at != event.renewed_at or lock.session_id != event.session_id:
        raise RenewedLeaseMissingError
    return ProducerObservation(
        event_type="mx_session_lease_renewed",
        producer="gzkit.commands.mx_cmd.mx_renew_cmd",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.session_id,
    )


def _probe_mx_marker_repair(root: Path) -> ProducerObservation:
    """Corrupt a live marker, repair it, and read back the one record the repair books.

    Returns:
        The verified observation of the repair's record.

    Raises:
        ValueError: When the repair refuses, leaves the condition off or books no record.
        TypeError: When the record is not an ``mx_marker_repaired`` event.

    """
    from gzkit.commands import mx_cmd  # noqa: PLC0415 - a command handler; import only when probed
    from gzkit.mx import marker  # noqa: PLC0415

    (root / ".gzkit").mkdir()
    try:
        with mx_cmd.console.capture():
            mx_cmd.mx_enter_cmd(
                reason="probe", attestor=_AUTHOR, inspection_scope=[], project_root=root
            )
            marker.marker_path(root).write_text("{not json", encoding="utf-8")
            mx_cmd.mx_repair_cmd(_AUTHOR, project_root=root)
    except SystemExit as exc:
        message = f"Repair refused with exit {exc.code}"
        raise ValueError(message) from exc
    if not marker.condition(root).on:
        message = "Repair left the condition off"
        raise ValueError(message)
    persisted = (root / ".gzkit/ledger.jsonl").read_bytes()
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    repairs = [row for row in rows if row.get("event") == "mx_marker_repaired"]
    if len(repairs) != 1:
        message = "Repair must persist exactly one record"
        raise ValueError(message)
    event = parse_typed_event(repairs[0])
    if not isinstance(event, MxMarkerRepairedEvent):
        message = "Repair persisted the wrong event type"
        raise TypeError(message)
    return ProducerObservation(
        event_type="mx_marker_repaired",
        producer="gzkit.commands.mx_cmd.mx_repair_cmd",
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
                "specialization": "catalog",
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
        "work_packages": [
            {
                "id": _WORK_PACKAGE,
                "kind": "delivery",
                "outcome": _OUTCOME,
                "issues": [],
                "lane": None,
                "aliases": [],
                "initial_conditions": "NA",
                "procedure": _STATEMENT,
                "test_and_inspection": "NA",
                "system_restoration": "NA",
                "oqe": [],
                "alterations": [],
                "departures": [],
            },
            {
                "id": _REPAIR_PACKAGE,
                "kind": "repair",
                "outcome": None,
                "issues": [_ISSUE],
                "lane": "lite",
                "aliases": [],
                "initial_conditions": "NA",
                "procedure": _STATEMENT,
                "test_and_inspection": "NA",
                "system_restoration": "NA",
                "oqe": [],
                "alterations": [],
                "departures": [],
            },
        ],
        "orders": [],
    }
    for kind, entries in files.items():
        path = registry_path(root, CATALOG_FILES[kind])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"_doc": "isolated probe", kind: entries}), encoding="utf-8")
    (root / ".gzkit").mkdir()
    return load_catalog(root)


def _expect_refusal(
    write: Callable[[], object],
    case: str,
    refusal: type[Exception] | None = None,
    reason: str = "",
) -> None:
    """Require a refusal, for ``reason`` when one is named.

    A writer that books what the grammar refuses fails its contract, and so does a
    refusal for another reason, which proves nothing about the case probed.

    Raises:
        WriterAcceptedRefusalError: The writer booked the case, or refused it for
            another reason.

    """
    from gzkit.catalog_ledger import CatalogLedgerError  # noqa: PLC0415 - import only when probed

    expected = refusal or CatalogLedgerError
    try:
        write()
    except expected as exc:
        if reason in str(exc):
            return
    raise WriterAcceptedRefusalError(case)


def _single_row(ledger_path: Path) -> tuple[bytes, dict[str, object]]:
    persisted = ledger_path.read_bytes() if ledger_path.is_file() else b""
    rows = [json.loads(line) for line in persisted.decode("utf-8").splitlines() if line.strip()]
    if len(rows) != 1:
        raise WriterRecordCountError
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
        raise WriterEventTypeError
    if (event.id, event.from_state, event.to_state) != (_OUTCOME, "queued", "designing"):
        raise TransitionMismatchError
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
        raise WriterEventTypeError
    if (event.id, event.revision, event.verdict) != (_CATALOG_REQ, 1, "SATISFIED"):
        raise ProofMismatchError
    return ProducerObservation(
        event_type="req_proof_recorded",
        producer="gzkit.catalog_ledger.record_req_proof",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_work_package_transition(root: Path) -> ProducerObservation:
    """Initiate a seated package, then try a skip; one move booked, the skip refused.

    Returns:
        The verified observation.

    Raises:
        TypeError: The writer persisted another event type.
        ValueError: The writer booked the wrong record or accepted the skip.

    """
    from gzkit import work_package_ledger as wpl  # noqa: PLC0415 - the writer; import only when probed
    from gzkit.ledger import Ledger  # noqa: PLC0415

    catalog = _seat_catalog(root)
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    wpl.record_work_package_transition(
        catalog,
        ledger,
        wpl.TransitionRequest(
            work_package=_WORK_PACKAGE,
            to_state="initiated",
            evidence=_AUTHOR,
            operator_text=_STATEMENT,
        ),
    )
    skip = wpl.TransitionRequest(work_package=_WORK_PACKAGE, to_state="commenced", evidence=_AUTHOR)
    _expect_refusal(
        lambda: wpl.record_work_package_transition(catalog, ledger, skip),
        "a transition that skips the lifecycle",
        wpl.WorkPackageLedgerError,
    )
    persisted, row = _single_row(ledger_path)
    event = parse_typed_event(row)
    if not isinstance(event, WorkPackageTransitionedEvent):
        msg = "Writer persisted the wrong event type"
        raise TypeError(msg)
    if (event.id, event.from_state, event.to_state) != (_WORK_PACKAGE, None, "initiated"):
        msg = "Transition record disagrees with the initiation"
        raise ValueError(msg)
    return ProducerObservation(
        event_type="work_package_transitioned",
        producer="gzkit.work_package_ledger.record_work_package_transition",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_work_package_change(root: Path) -> ProducerObservation:
    """Change an initiated package, then try a coordinator's change order; the second refused.

    Returns:
        The verified observation.

    Raises:
        TypeError: The writer persisted another event type.
        ValueError: The writer booked the wrong record or accepted the change order.

    """
    from gzkit import work_package_ledger as wpl  # noqa: PLC0415 - the writer; import only when probed
    from gzkit.ledger import Ledger  # noqa: PLC0415

    catalog = _seat_catalog(root)
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    wpl.record_work_package_transition(
        catalog,
        ledger,
        wpl.TransitionRequest(
            work_package=_WORK_PACKAGE,
            to_state="initiated",
            evidence=_AUTHOR,
            operator_text=_STATEMENT,
        ),
    )
    seated = ledger_path.read_bytes()
    wpl.record_work_package_change(
        catalog,
        ledger,
        wpl.ChangeRequest(
            work_package=_WORK_PACKAGE, rung="attachment", approver="operator", change=_STATEMENT
        ),
    )
    order = wpl.ChangeRequest(
        work_package=_WORK_PACKAGE,
        rung="change_order",
        approver="coordinator",
        change=_STATEMENT,
        superseded=_STATEMENT,
        work_stopped=True,
    )
    _expect_refusal(
        lambda: wpl.record_work_package_change(catalog, ledger, order),
        "a change order the coordinator approved",
        wpl.WorkPackageLedgerError,
    )
    persisted = ledger_path.read_bytes()
    added = persisted[len(seated) :].decode("utf-8").splitlines()
    if not persisted.startswith(seated) or len(added) != 1:
        msg = "Writer must persist exactly one change and nothing for a refusal"
        raise ValueError(msg)
    event = parse_typed_event(json.loads(added[0]))
    if not isinstance(event, WorkPackageChangedEvent):
        msg = "Writer persisted the wrong event type"
        raise TypeError(msg)
    if (event.id, event.rung, event.approver) != (_WORK_PACKAGE, "attachment", "operator"):
        msg = "Change record disagrees with the attachment"
        raise ValueError(msg)
    return ProducerObservation(
        event_type="work_package_changed",
        producer="gzkit.work_package_ledger.record_work_package_change",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_work_package_issue_closed(root: Path) -> ProducerObservation:
    """Close an initiated repair package's issue, then try it again; the second refused.

    Returns:
        The verified observation.

    Raises:
        TypeError: The writer persisted another event type.
        ValueError: The writer booked the wrong record or accepted the second close.

    """
    from gzkit import work_package_ledger as wpl  # noqa: PLC0415 - the writer; import only when probed
    from gzkit.ledger import Ledger  # noqa: PLC0415

    catalog = _seat_catalog(root)
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    wpl.record_work_package_transition(
        catalog,
        ledger,
        wpl.TransitionRequest(
            work_package=_REPAIR_PACKAGE,
            to_state="initiated",
            evidence=_AUTHOR,
            operator_text=_STATEMENT,
        ),
    )
    seated = ledger_path.read_bytes()
    closure = wpl.IssueClosure(
        work_package=_REPAIR_PACKAGE, issue=_ISSUE, commit=_AUTHOR, reviewer=_AUTHOR
    )
    wpl.record_work_package_issue_closed(catalog, ledger, closure)
    _expect_refusal(
        lambda: wpl.record_work_package_issue_closed(catalog, ledger, closure),
        "an issue closed twice against its package",
        wpl.WorkPackageLedgerError,
    )
    persisted = ledger_path.read_bytes()
    added = persisted[len(seated) :].decode("utf-8").splitlines()
    if not persisted.startswith(seated) or len(added) != 1:
        msg = "Writer must persist exactly one issue close and nothing for a refusal"
        raise ValueError(msg)
    event = parse_typed_event(json.loads(added[0]))
    if not isinstance(event, WorkPackageIssueClosedEvent):
        msg = "Writer persisted the wrong event type"
        raise TypeError(msg)
    if (event.id, event.issue) != (_REPAIR_PACKAGE, _ISSUE):
        msg = "Issue-close record disagrees with the close"
        raise ValueError(msg)
    return ProducerObservation(
        event_type="work_package_issue_closed",
        producer="gzkit.work_package_ledger.record_work_package_issue_closed",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_order_transition(root: Path) -> ProducerObservation:
    """Open an order in an initiated repair package, then try it again; the second refused.

    Returns:
        The verified observation.

    Raises:
        TypeError: The writer persisted another event type.
        ValueError: The writer booked the wrong record or accepted the second opening.

    """
    from gzkit import order_ledger  # noqa: PLC0415 - the writer; import only when probed
    from gzkit import work_package_ledger as wpl  # noqa: PLC0415
    from gzkit.ledger import Ledger  # noqa: PLC0415
    from gzkit.models.catalog import Order  # noqa: PLC0415

    order = Order(
        id=_ORDER, work_package=_REPAIR_PACKAGE, aliases=(), purpose=_STATEMENT, procedure="NA"
    )
    catalog = _seat_catalog(root).model_copy(update={"orders": (order,)})
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    wpl.record_work_package_transition(
        catalog,
        ledger,
        wpl.TransitionRequest(
            work_package=_REPAIR_PACKAGE,
            to_state="initiated",
            evidence=_AUTHOR,
            operator_text=_STATEMENT,
        ),
    )
    seated = ledger_path.read_bytes()
    opening = order_ledger.OrderMove(
        order=_ORDER, to_state="opened", evidence=_AUTHOR, operator_text=_STATEMENT
    )
    order_ledger.record_order_transition(catalog, ledger, opening)
    _expect_refusal(
        lambda: order_ledger.record_order_transition(catalog, ledger, opening),
        "an order opened twice",
        order_ledger.OrderLedgerError,
    )
    persisted = ledger_path.read_bytes()
    added = persisted[len(seated) :].decode("utf-8").splitlines()
    if not persisted.startswith(seated) or len(added) != 1:
        msg = "Writer must persist exactly one opening and nothing for a refusal"
        raise ValueError(msg)
    event = parse_typed_event(json.loads(added[0]))
    if not isinstance(event, OrderTransitionedEvent):
        msg = "Writer persisted the wrong event type"
        raise TypeError(msg)
    observed = (event.id, event.work_package, event.from_state, event.to_state)
    if observed != (_ORDER, _REPAIR_PACKAGE, None, "opened"):
        msg = "Order record disagrees with the opening"
        raise ValueError(msg)
    return ProducerObservation(
        event_type="order_transitioned",
        producer="gzkit.order_ledger.record_order_transition",
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _commence_delivery(catalog: Catalog, ledger: Ledger) -> None:
    """Move the probe's delivery package to commenced on its one catalog REQ."""
    from gzkit import work_package_ledger as wpl  # noqa: PLC0415 - the writer; import only when probed

    for move in (
        wpl.TransitionRequest(
            work_package=_WORK_PACKAGE,
            to_state="initiated",
            evidence=_AUTHOR,
            operator_text=_STATEMENT,
        ),
        wpl.TransitionRequest(
            work_package=_WORK_PACKAGE,
            to_state="frozen",
            evidence=_AUTHOR,
            risk_note=_AUTHOR,
            review_receipt=_AUTHOR,
            baseline=(BaselinedReq(req=_CATALOG_REQ, revision=1),),
        ),
        wpl.TransitionRequest(work_package=_WORK_PACKAGE, to_state="commenced", evidence=_AUTHOR),
    ):
        wpl.record_work_package_transition(catalog, ledger, move)


_RUN_EVENTS = frozenset(
    {"work_package_dispatched", "work_package_blocked", "work_package_unblocked"}
)


def _probe_work_package_run(root: Path, event_type: str) -> ProducerObservation:
    """Commence a delivery package, then dispatch, block and unblock; each refusal is proven.

    A repair package's run is its orders' (RP-12 ruling 44), so the package-level run
    verbs are probed on the delivery package.

    Returns:
        The verified observation of the named event.

    Raises:
        TypeError: The writer persisted another event type.
        ValueError: The writer booked for a refusal or lost a row.

    """
    from gzkit import work_package_ledger as wpl  # noqa: PLC0415 - the writer; import only when probed
    from gzkit import work_package_run as run  # noqa: PLC0415
    from gzkit.ledger import Ledger  # noqa: PLC0415

    catalog = _seat_catalog(root)
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    _commence_delivery(catalog, ledger)
    seated = ledger_path.read_bytes()
    roles = (run.IMPLEMENTER, "SpecReviewer") * (MAX_REVIEW_FIX_CYCLES + 1)
    for role in roles:
        run.record_work_package_dispatch(
            catalog,
            ledger,
            run.DispatchRequest(
                work_package=_WORK_PACKAGE,
                role=role,
                model=_AUTHOR,
                req=_CATALOG_REQ,
                root=root.resolve().as_posix(),
            ),
        )
    past_the_bound = run.DispatchRequest(
        work_package=_WORK_PACKAGE,
        role=run.IMPLEMENTER,
        model=_AUTHOR,
        req=_CATALOG_REQ,
        root=root.resolve().as_posix(),
    )
    _expect_refusal(
        lambda: run.record_work_package_dispatch(catalog, ledger, past_the_bound),
        "the fix cycle past the bound",
        wpl.WorkPackageLedgerError,
        reason="fix cycles",
    )
    block = run.BlockRequest(work_package=_WORK_PACKAGE, reason=_AUTHOR, next_action=_AUTHOR)
    run.record_work_package_block(catalog, ledger, block, refutations={})
    no_exit = run.UnblockRequest(work_package=_WORK_PACKAGE, ruling=_AUTHOR, operator=_AUTHOR)
    _expect_refusal(
        lambda: run.record_work_package_unblock(catalog, ledger, no_exit),
        "an unblock at the bound naming no exit",
        wpl.WorkPackageLedgerError,
    )
    hold = no_exit.model_copy(update={"exit_taken": "hold"})
    run.record_work_package_unblock(catalog, ledger, hold)
    persisted = ledger_path.read_bytes()
    added = [
        parse_typed_event(json.loads(line))
        for line in persisted[len(seated) :].decode("utf-8").splitlines()
    ]
    if not persisted.startswith(seated) or len(added) != len(roles) + 2:
        msg = "Writers must persist one row per act and nothing for a refusal"
        raise ValueError(msg)
    event = next((row for row in added if row.event == event_type), None)
    if event is None:
        msg = "Writer persisted the wrong event type"
        raise TypeError(msg)
    blocked = next(row for row in added if isinstance(row, WorkPackageBlockedEvent))
    if blocked.at_bound != (f"{_CATALOG_REQ}@1",):
        msg = "The block must name the subject at the bound"
        raise ValueError(msg)
    return ProducerObservation(
        event_type=event_type,
        producer=_PRODUCERS[event_type],
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _observe_dispatch_void(
    ledger: Ledger, ledger_path: Path, dispatch_id: str
) -> ProducerObservation:
    """Void a booked dispatch, then try it again and an unknown id (RP-12 ruling 42).

    Returns:
        The verified observation.

    Raises:
        ValueError: A refusal booked a row, or the void left the dispatch live.

    """
    from gzkit import work_package_ledger as wpl  # noqa: PLC0415 - the writer; import only when probed
    from gzkit import work_package_run as run  # noqa: PLC0415

    seated = ledger_path.read_bytes()
    event = run.record_dispatch_void(ledger, _WORK_PACKAGE, dispatch_id, _AUTHOR)
    for target in (dispatch_id, "D-0000000000000000"):
        _expect_refusal(
            lambda target=target: run.record_dispatch_void(ledger, _WORK_PACKAGE, target, _AUTHOR),
            "a void of no live dispatch",
            wpl.WorkPackageLedgerError,
        )
    persisted = ledger_path.read_bytes()
    added = persisted[len(seated) :].decode("utf-8").splitlines()
    if len(added) != 1 or run.find_dispatch(ledger, dispatch_id) is not None:
        msg = "A void must book one row, none for a refusal, and leave no live dispatch"
        raise ValueError(msg)
    return ProducerObservation(
        event_type="dispatch_voided",
        producer=_PRODUCERS["dispatch_voided"],
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=event.id,
    )


def _probe_dispatch_claim(root: Path, event_type: str = "dispatch_claimed") -> ProducerObservation:
    """Commence and dispatch, then claim it twice and claim an unknown id (RP-12 ruling 40).

    Returns:
        The verified observation.

    Raises:
        TypeError: The writer persisted another event type.
        ValueError: The writer booked a second claim of one pair, or a claim of
            no dispatch.

    """
    from gzkit import work_package_run as run  # noqa: PLC0415 - the writer; import only when probed
    from gzkit.ledger import Ledger  # noqa: PLC0415

    catalog = _seat_catalog(root)
    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger = Ledger(ledger_path)
    _commence_delivery(catalog, ledger)
    dispatched = run.record_work_package_dispatch(
        catalog,
        ledger,
        run.DispatchRequest(
            work_package=_WORK_PACKAGE,
            role=run.IMPLEMENTER,
            model=_AUTHOR,
            req=_CATALOG_REQ,
            root=root.resolve().as_posix(),
        ),
    )
    dispatch_id = str(dispatched.dispatch_id)
    if event_type == "dispatch_voided":
        return _observe_dispatch_void(ledger, ledger_path, dispatch_id)
    seated = ledger_path.read_bytes()
    claimed = run.record_dispatch_claim(ledger, dispatch_id, "a-probe", "stamp")
    again = run.record_dispatch_claim(ledger, dispatch_id, "a-probe", "agent_returned")
    unknown = run.record_dispatch_claim(ledger, "D-0000000000000000", "a-probe", "stamp")
    persisted = ledger_path.read_bytes()
    added = [
        parse_typed_event(json.loads(line))
        for line in persisted[len(seated) :].decode("utf-8").splitlines()
    ]
    if again is not None or unknown is not None or len(added) != 1:
        msg = "The claim writer must book one row per dispatch and agent, and none for no dispatch"
        raise ValueError(msg)
    if claimed is None or added[0].event != "dispatch_claimed":
        msg = "Writer persisted the wrong event type"
        raise TypeError(msg)
    return ProducerObservation(
        event_type="dispatch_claimed",
        producer=_PRODUCERS["dispatch_claimed"],
        status="verified",
        ledger_sha256=hashlib.sha256(persisted).hexdigest(),
        record_count=1,
        subject=added[0].id,
    )


def _probe_legacy_withdrawal(root: Path) -> ProducerObservation:
    """Withdraw a seated legacy unit, then try it again; the second is refused.

    Returns:
        The verified observation.

    Raises:
        TypeError: The writer persisted another event type.
        ValueError: The writer booked the wrong record or accepted the second withdrawal.

    """
    from gzkit import legacy_units  # noqa: PLC0415 - the writer; import only when probing
    from gzkit.ledger import Ledger, obpi_created_event  # noqa: PLC0415

    ledger_path = root / ".gzkit/ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger = Ledger(ledger_path)
    ledger.append(obpi_created_event(_OBPI, "ADR-0.0.1"))
    seated = ledger_path.read_bytes()
    legacy_units.withdraw_legacy_unit(ledger, _OBPI, _STATEMENT, _AUTHOR)
    _expect_refusal(
        lambda: legacy_units.withdraw_legacy_unit(ledger, _OBPI, _STATEMENT, _AUTHOR),
        "a unit withdrawn twice",
        legacy_units.LegacyUnitRetiredError,
    )
    persisted = ledger_path.read_bytes()
    added = persisted[len(seated) :].decode("utf-8").splitlines()
    if not persisted.startswith(seated) or len(added) != 1:
        msg = "Writer must persist exactly one withdrawal and nothing for a refusal"
        raise ValueError(msg)
    event = parse_typed_event(json.loads(added[0]))
    if not isinstance(event, LegacyUnitWithdrawnEvent):
        msg = "Writer persisted the wrong event type"
        raise TypeError(msg)
    if (event.id, event.attestor) != (_OBPI, _AUTHOR):
        msg = "Withdrawal record disagrees with the request"
        raise ValueError(msg)
    return ProducerObservation(
        event_type="legacy_unit_withdrawn",
        producer=_PRODUCERS["legacy_unit_withdrawn"],
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
    "mx_marker_repaired": "gzkit.commands.mx_cmd.mx_repair_cmd",
    "outcome_transitioned": "gzkit.catalog_ledger.record_outcome_transition",
    "req_proof_recorded": "gzkit.catalog_ledger.record_req_proof",
    "work_package_transitioned": "gzkit.work_package_ledger.record_work_package_transition",
    "work_package_changed": "gzkit.work_package_ledger.record_work_package_change",
    "work_package_issue_closed": "gzkit.work_package_ledger.record_work_package_issue_closed",
    "work_package_dispatched": "gzkit.work_package_run.record_work_package_dispatch",
    "work_package_blocked": "gzkit.work_package_run.record_work_package_block",
    "work_package_unblocked": "gzkit.work_package_run.record_work_package_unblock",
    "dispatch_claimed": "gzkit.work_package_run.record_dispatch_claim",
    "dispatch_voided": "gzkit.work_package_run.record_dispatch_void",
    "legacy_unit_withdrawn": "gzkit.legacy_units.withdraw_legacy_unit",
    "order_transitioned": "gzkit.order_ledger.record_order_transition",
}


_ROOT_PROBES = {
    "report_published": _probe_report,
    "obpi_lock_lease_expired": _probe_lock_lease_expiry,
    "mx_session_lease_renewed": _probe_mx_lease_renewal,
    "mx_marker_repaired": _probe_mx_marker_repair,
    "outcome_transitioned": _probe_outcome_transition,
    "req_proof_recorded": _probe_req_proof,
    "work_package_transitioned": _probe_work_package_transition,
    "work_package_changed": _probe_work_package_change,
    "work_package_issue_closed": _probe_work_package_issue_closed,
    "order_transitioned": _probe_order_transition,
    "legacy_unit_withdrawn": _probe_legacy_withdrawal,
    "dispatch_claimed": _probe_dispatch_claim,
    "dispatch_voided": lambda root: _probe_dispatch_claim(root, "dispatch_voided"),
}


def probe_producer(event_type: str) -> ProducerObservation:
    """Run the registered producer now; unsupported and failed probes grant no credit."""
    if event_type not in _PRODUCERS:
        return ProducerObservation(event_type=event_type, status="unsupported")
    try:
        with tempfile.TemporaryDirectory(prefix="gzkit-ledger-producer-") as directory:
            root = Path(directory)
            if event_type in _ROOT_PROBES:
                return _ROOT_PROBES[event_type](root)
            if event_type in _RUN_EVENTS:
                return _probe_work_package_run(root, event_type)
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
