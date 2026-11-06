"""Typed producer-probe contract failures (RO-9, TRY003).

Kept beside :mod:`gzkit.ledger_producer_probe` because that module is over the
authoring-time module size limit (``.gzkit/rules/pythonic.md``). Each class is
one way a producer can break its write contract; all subclass ``ValueError``,
the type the probes raised before.
"""


class AcceptanceRecordCountError(ValueError):
    """The acceptance producer persisted other than one initial contract record."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Producer must persist exactly one initial contract record")


class AcceptanceEventTypeError(ValueError):
    """The acceptance producer persisted an event of the wrong type."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Producer persisted the wrong event type")


class AcceptanceSubjectError(ValueError):
    """The acceptance producer persisted the wrong subject or record kind."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Producer persisted the wrong subject or acceptance record kind")


class AcceptancePopulationError(ValueError):
    """The acceptance producer dropped the author or the obligation population."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Producer did not preserve the author and obligation population")


class AcceptanceObligationMismatchError(ValueError):
    """The persisted obligation differs from the canonical fixture."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Persisted obligation disagrees with the canonical fixture")


class ReportRecordCountError(ValueError):
    """The report producer persisted other than one publication record."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Report producer must persist exactly one publication record")


class ReportEventTypeError(ValueError):
    """The report producer persisted an event of the wrong type."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Report producer persisted the wrong event type")


class PublicationMismatchError(ValueError):
    """The publication witness differs from the authored fixture."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Publication witness disagrees with the authored fixture")


class PublishedBytesError(ValueError):
    """A published assessment or its current view differs from the source bytes."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Published assessment or current view differs from exact source bytes")


class ArchiveIndexLinkError(ValueError):
    """The report archive index does not link the retained assessment."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Archive index does not link the retained assessment")


class ExpiredLockEvictedError(ValueError):
    """The reaper evicted an expired work lock instead of keeping it held."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Reaper evicted an expired work lock instead of keeping it held")


class LeaseExpiryRecordCountError(ValueError):
    """The reaper persisted other than one lease-expiry record."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Reaper must persist exactly one lease-expiry record")


class LeaseExpiryEventTypeError(ValueError):
    """The reaper persisted an event of the wrong type."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Reaper persisted the wrong event type")


class LeaseExpiryMismatchError(ValueError):
    """The lease-expiry record differs from the expired lock."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Lease-expiry record disagrees with the expired lock")


class RenewalEndedSessionError(ValueError):
    """The mx lease renewal ended the session or dropped its marker."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Renewal ended the session or dropped its marker")


class RenewalRecordCountError(ValueError):
    """The renewal persisted other than one renewal record, or a close."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Renewal must persist exactly one renewal record and no close")


class RenewalEventTypeError(ValueError):
    """The renewal persisted an event of the wrong type."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Renewal persisted the wrong event type")


class RenewedLeaseMissingError(ValueError):
    """The session lock does not carry the renewed lease."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("The session lock does not carry the renewed lease")


class WriterRecordCountError(ValueError):
    """A catalog writer persisted other than one record, or booked a refusal."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Writer must persist exactly one record and nothing for a refusal")


class WriterEventTypeError(ValueError):
    """A catalog writer persisted an event of the wrong type."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Writer persisted the wrong event type")


class TransitionMismatchError(ValueError):
    """The outcome transition record differs from the one-step move."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Transition record disagrees with the one-step move")


class ProofMismatchError(ValueError):
    """The REQ proof record differs from the REQ the catalog holds."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Proof record disagrees with the REQ the catalog holds")


class RenewalRefusedError(ValueError):
    """The mx lease renewal exited instead of renewing."""

    def __init__(self, code: object) -> None:
        """Build the message from ``code``."""
        self.code = code
        super().__init__(f"Renewal refused with exit {code}")


class WriterAcceptedRefusalError(ValueError):
    """A ledger writer booked an input its grammar must refuse."""

    def __init__(self, case: str) -> None:
        """Build the message from ``case``."""
        self.case = case
        super().__init__(f"Writer accepted {case}")
