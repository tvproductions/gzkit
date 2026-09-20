"""Observe registered ledger producers in fresh disposable projects (GHI #985).

These executions demonstrate wiring, never live project activity or acceptance.
No report is loaded as evidence, and the caller's project is never a write target.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit import acceptance_store, reports
from gzkit.config import GzkitConfig, PathConfig
from gzkit.events import AcceptanceRecordedEvent, ReportPublishedEvent, parse_typed_event

_OBPI = "OBPI-0.1.0-01-producer-probe"
_AUTHOR = "isolated-producer-probe"
_REQ = "REQ-0.1.0-01-01"
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


def probe_producer(event_type: str) -> ProducerObservation:
    """Run the registered producer now; unsupported and failed probes grant no credit."""
    if event_type not in {"acceptance_recorded", "report_published"}:
        return ProducerObservation(event_type=event_type, status="unsupported")
    try:
        with tempfile.TemporaryDirectory(prefix="gzkit-ledger-producer-") as directory:
            root = Path(directory)
            if event_type == "report_published":
                return _probe_report(root)
            _prepare_acceptance_project(root)
            acceptance_store.initialize(root, _OBPI, _AUTHOR)
            return _observe_acceptance_contract(root)
    except Exception as exc:  # noqa: BLE001 - a broken producer must fail this observation closed
        return ProducerObservation(
            event_type=event_type,
            producer=(
                "gzkit.reports.publish_report"
                if event_type == "report_published"
                else "gzkit.acceptance_store.initialize"
            ),
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )
