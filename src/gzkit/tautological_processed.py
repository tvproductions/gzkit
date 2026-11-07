"""Book a tautological-test op the decommission chore processed (GHI #1305 item 2).

The chore promised a ``chore_decommission_processed`` ledger event per processed
item (OBPI-0.0.59-04, checklist item 4) and no verb wrote one, so a batch run
under the chore's Workflow left no Layer-2 record. ``record_processed`` is that
producer. It checks every input before it writes, so a refusal leaves the ledger
untouched: the work order is exactly one of an OBPI id or a TASK id (operator
ruling 2026-11-07, verbatim: "A"), the disposition is one the ledger schema
admits, and the file is one the tautological baseline knew, so an op the chore
never flagged cannot be booked as processed.
"""

from pathlib import Path

from gzkit.core.exceptions import ValidationError
from gzkit.ledger import Ledger
from gzkit.ledger_events import chore_decommission_processed_event
from gzkit.models.tautological_tests import Baseline
from gzkit.registries import RegistryError, load_registry

_BASELINE_NAME = "tautological_test_baseline.json"

#: The dispositions the ledger schema admits for this event.
DISPOSITIONS: tuple[str, ...] = (
    "convert",
    "replace-with-ledger",
    "fold-to-validator",
    "keep-as-fixture",
    "fold-to-validator+keep-as-fixture",
    "fold-to-validator-whole-file-delete",
    "no-op-already-clean",
)


class WorkOrderAmbiguousError(ValidationError):
    """A processed op names no work order, or names both an OBPI and a TASK."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Name exactly one work order: --obpi OBPI-... or --task TASK-...")


class WorkOrderMalformedError(ValidationError):
    """A work order id does not carry the prefix of its kind."""

    def __init__(self, value: str, prefix: str) -> None:
        """Record the id given and the prefix it lacks."""
        self.value = value
        self.prefix = prefix
        super().__init__(f"Work order {value!r} must start with {prefix!r}")


class UnknownDispositionError(ValidationError):
    """A disposition outside the set the ledger schema admits."""

    def __init__(self, disposition: str) -> None:
        """Record the disposition given."""
        self.disposition = disposition
        super().__init__(
            f"Unknown disposition {disposition!r}; expected one of: {', '.join(DISPOSITIONS)}"
        )


class FileNotInBaselineError(ValidationError):
    """A file the tautological baseline never flagged cannot be booked as processed."""

    def __init__(self, file_path: str) -> None:
        """Record the file given."""
        self.file_path = file_path
        super().__init__(
            f"{file_path} holds no op in data/tautological_test_baseline.json, so the chore "
            "never flagged it; only a baselined file can be booked as processed"
        )


def _work_order(obpi_id: str | None, task_id: str | None) -> tuple[str | None, str | None]:
    """Return the one work order, stripped, refusing none, both or a wrong prefix.

    Returns:
        ``(obpi_id, task_id)`` with exactly one set.

    Raises:
        WorkOrderAmbiguousError: neither or both is given.
        WorkOrderMalformedError: the given id lacks its kind's prefix.

    """
    obpi = (obpi_id or "").strip() or None
    task = (task_id or "").strip() or None
    if (obpi is None) == (task is None):
        raise WorkOrderAmbiguousError
    if obpi is not None and not obpi.startswith("OBPI-"):
        raise WorkOrderMalformedError(obpi, "OBPI-")
    if task is not None and not task.startswith("TASK-"):
        raise WorkOrderMalformedError(task, "TASK-")
    return obpi, task


def _baselined_files(project_root: Path) -> set[str]:
    """Return the files the tautological baseline holds an op for, none when it is absent.

    Returns:
        The baseline's file paths; empty when the registry is missing or unreadable.

    """
    try:
        raw = load_registry(project_root, _BASELINE_NAME)
    except RegistryError:
        return set()
    return {op.file_path for op in Baseline.model_validate(raw).operations}


def record_processed(
    project_root: Path,
    *,
    file_path: str,
    disposition: str,
    obpi_id: str | None = None,
    task_id: str | None = None,
    ledger_path: Path,
) -> dict[str, str]:
    """Book one ``chore_decommission_processed`` event for a processed tautological op.

    Returns:
        The fields booked: ``file_path``, ``disposition`` and the one work order.

    Raises:
        UnknownDispositionError: the disposition is outside the schema's set.
        FileNotInBaselineError: the baseline holds no op for the file.

    """
    obpi, task = _work_order(obpi_id, task_id)
    if disposition not in DISPOSITIONS:
        raise UnknownDispositionError(disposition)
    rel = Path(file_path).as_posix()
    if rel not in _baselined_files(project_root):
        raise FileNotInBaselineError(rel)
    Ledger(ledger_path).append(
        chore_decommission_processed_event(rel, disposition, obpi_id=obpi, task_id=task)
    )
    booked = {"file_path": rel, "disposition": disposition}
    booked.update({"obpi_id": obpi} if obpi else {"task_id": task or ""})
    return booked
