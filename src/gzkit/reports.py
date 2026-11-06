"""Retained big-picture assessments and ledger-derived publication views.

The report bytes are authored evidence; index/current are replaceable views.
An interrupted publication is retried with the same identity and inputs.
"""

import hashlib
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from gzkit.config import GzkitConfig
from gzkit.durability import commit_directory_entry
from gzkit.events import parse_typed_event
from gzkit.file_lock import exclusive_file_lock
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.ledger_events import report_published_event


class ReportPathEscapeError(ValueError):
    """A report publication path resolves outside the project root, or to the root itself."""

    def __init__(self, value: str) -> None:
        """Build the message from *value*."""
        self.value = value
        super().__init__(f"Report publication path must stay inside project: {value}")


class DuplicateReportIdentityError(ValueError):
    """The ledger records the same report publication identity more than once."""

    def __init__(self, report_id: str) -> None:
        """Build the message from *report_id*."""
        self.report_id = report_id
        super().__init__(f"Duplicate report publication identity in ledger: {report_id}")


class ReportWitnessMismatchError(ValueError):
    """A published report's bytes no longer match the hash its ledger event witnessed."""

    def __init__(self, path: Path) -> None:
        """Build the message from *path*."""
        self.path = path
        super().__init__(f"Published report differs from its ledger witness: {path}")


class InvalidReportIdError(ValueError):
    """A report id falls outside the permitted lowercase ASCII shape."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__(
            "Report id must be 1–128 lowercase ASCII letters, digits, underscores or hyphens"
        )


class ReservedReportIdError(ValueError):
    """A report id names a derived view or a reserved device name."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Report id is reserved for a derived view")


class EmptyReportError(ValueError):
    """A report source holds no non-whitespace UTF-8 text."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Report must contain non-empty UTF-8 text")


class LedgerInsideReportDirectoryError(ValueError):
    """The configured ledger lives inside the report publication directory."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Ledger must be outside the report directory")


class ReportDestinationSymlinkError(ValueError):
    """A report destination path is a symbolic link."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Report destination must not be a symbolic link")


class ReportInputsConflictError(ValueError):
    """A report id the ledger already witnessed was republished with different inputs."""

    def __init__(self, report_id: str) -> None:
        """Build the message from *report_id*."""
        self.report_id = report_id
        super().__init__(f"Report id already published with different inputs: {report_id}")


class RetainedReportBytesError(ValueError):
    """An unwitnessed retained report file holds bytes other than the ones being published."""

    def __init__(self, path: Path) -> None:
        """Build the message from *path*."""
        self.path = path
        super().__init__(f"Retained report has different bytes: {path}")


def _contained(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ReportPathEscapeError(value)
    return path


def _write_atomic(path: Path, content: bytes) -> None:
    """Flush bytes before replacing a derived view or installing new source."""
    fd, name = tempfile.mkstemp(prefix=".report-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        commit_directory_entry(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _history(root: Path, ledger: Ledger) -> list[LedgerEvent]:
    events = [event for event in ledger.read_all() if event.event == "report_published"]
    seen: set[str] = set()
    for event in events:
        parse_typed_event(event.model_dump())
        if event.id in seen:
            raise DuplicateReportIdentityError(event.id)
        seen.add(event.id)
        path = _contained(root, event.extra["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != event.extra["sha256"]:
            raise ReportWitnessMismatchError(path)
    return events


def _refresh_views(root: Path, directory: Path, events: list[LedgerEvent]) -> None:
    latest = events[-1]
    lines = ["# Big-picture reports", "", "Published assessments; retained without deletion.", ""]
    for event in reversed(events):
        path = _contained(root, event.extra["path"])
        link = os.path.relpath(path, directory).replace(os.sep, "/")
        lines.append(f"- [{event.id}]({link}) — {event.ts}")
    _write_atomic(directory / "index.md", ("\n".join(lines) + "\n").encode())
    _write_atomic(directory / "current.md", _contained(root, latest.extra["path"]).read_bytes())


def publish_report(
    root: Path,
    config: GzkitConfig,
    source: Path,
    report_id: str,
    *,
    period: str = "",
    evidence_cutoff: str = "",
) -> dict[str, Any]:
    """Publish immutable UTF-8 bytes, witness them, then rotate derived views.

    Report IDs and metadata are immutable. Retry the same inputs after an IO
    failure: a retained but unwitnessed file is adopted only if bytes agree;
    an already-witnessed report merely rebuilds views from ledger order.

    Returns:
        The report's `id` and metadata (`series`, `path`, `sha256`, `period`, `evidence_cutoff`)
        with `published` True and `already_published` True when the ledger already witnessed this
        report, False when this call published it.

    Raises:
        InvalidReportIdError: When ``report_id`` falls outside the permitted shape.
        ReservedReportIdError: When ``report_id`` names a derived view or reserved name.
        EmptyReportError: When ``source`` holds no non-whitespace UTF-8 text.
        LedgerInsideReportDirectoryError: When the ledger lives inside the report directory.
        ReportDestinationSymlinkError: When the report destination is a symbolic link.
        ReportInputsConflictError: When ``report_id`` was published with different inputs.
        RetainedReportBytesError: When an unwitnessed retained file holds different bytes.

    """
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,127}", report_id):
        raise InvalidReportIdError
    if report_id in {"index", "current", "con", "prn", "aux", "nul"} or re.fullmatch(
        r"(?:com|lpt)[0-9]", report_id
    ):
        raise ReservedReportIdError
    content = source.read_bytes()
    if not content.decode("utf-8").strip():
        raise EmptyReportError
    root = root.resolve()
    directory = _contained(root, f"{config.paths.docs_root}/reports/big-picture")
    ledger_path = _contained(root, config.paths.ledger)
    if ledger_path.is_relative_to(directory):
        raise LedgerInsideReportDirectoryError
    directory.mkdir(parents=True, exist_ok=True)
    # Flush each newly created ancestor as well as the eventual report entry.
    ancestor = directory
    while ancestor != root:
        commit_directory_entry(ancestor.parent)
        ancestor = ancestor.parent
    path = directory / f"{report_id}.md"
    if path.is_symlink():
        raise ReportDestinationSymlinkError
    metadata = {
        "series": "big-picture",
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(content).hexdigest(),
        "period": period,
        "evidence_cutoff": evidence_cutoff,
    }
    ledger = Ledger(ledger_path)
    # A dedicated publication lock serializes history/predecessor/rotation.
    with exclusive_file_lock(directory / "publication"):
        events = _history(root, ledger)
        existing = next((event for event in events if event.id == report_id), None)
        if existing:
            if any(existing.extra[key] != value for key, value in metadata.items()):
                raise ReportInputsConflictError(report_id)
        else:
            if path.exists() and path.read_bytes() != content:
                raise RetainedReportBytesError(path)
            _write_atomic(path, content)
            event = report_published_event(
                report_id,
                path=metadata["path"],
                sha256=metadata["sha256"],
                period=period,
                evidence_cutoff=evidence_cutoff,
                predecessor=events[-1].id if events else None,
            )
            parse_typed_event(event.model_dump())
            ledger.append(event)
            events.append(event)
        _refresh_views(root, directory, events)
    return {
        "id": report_id,
        **metadata,
        "published": True,
        "already_published": existing is not None,
    }
