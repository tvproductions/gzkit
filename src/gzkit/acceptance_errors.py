"""Typed refusals of the durable acceptance store (GHI #985).

Each class names one failure ``gzkit.acceptance_store`` refuses and subclasses
the ``ValueError`` it raised before, so every existing handler and message
assertion still holds. They live here because the store module is already past
the module size guidance in ``.gzkit/rules/pythonic.md``.
"""


class NoCanonicalBriefError(ValueError):
    """An OBPI ID resolves to no canonical brief."""

    def __init__(self, obpi_id: str) -> None:
        """Build the refusal message from ``obpi_id``."""
        self.obpi_id = obpi_id
        super().__init__(f"No canonical brief for {obpi_id}")


class ContractReplacedError(ValueError):
    """A recorded acceptance contract differs from the one already on the ledger."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Acceptance contract cannot be silently replaced")


class UnknownAcceptanceRecordTypeError(ValueError):
    """An acceptance ledger record carries a record type the store does not know."""

    def __init__(self, kind: object) -> None:
        """Build the refusal message from ``kind``."""
        self.kind = kind
        super().__init__(f"Unknown acceptance record type: {kind}")


class AcceptanceAlreadyInitializedError(ValueError):
    """Re-initialization would change the recorded author or obligation identities."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__(
            "Acceptance already initialized; preserve its author and obligation identities"
        )


class AcceptanceUninitializedError(ValueError):
    """A proof or review is recorded before acceptance was initialized."""

    def __init__(self, record: str) -> None:
        """Build the refusal message from ``record``."""
        self.record = record
        super().__init__(f"Initialize acceptance before recording {record}")


class StaleProofObligationError(ValueError):
    """A proof names no current canonical obligation at its contract digest."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Proof does not describe a current canonical obligation")


class ProofIdReplacedError(ValueError):
    """A proof reuses the ID of an earlier recorded execution."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("A proof ID cannot replace an earlier execution")


class UnsuccessfulReviewReceiptError(ValueError):
    """A review is extracted from something other than a successful ARB step receipt."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Review requires a successful ARB step receipt")


class ReviewReceiptIdentityError(ValueError):
    """A review receipt carries no ARB step run ID."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Review receipt has no execution identity")


class ReviewReceiptOutputError(ValueError):
    """A review receipt's output holds other than exactly one review object."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__(
            "Receipt output must contain exactly one gzkit.acceptance.review.v1 object"
        )


class ReviewReceiptCommandError(ValueError):
    """A review receipt records no executable command."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Review receipt has no executable command")


class ReviewInvocationUnrecordedError(ValueError):
    """A review receipt does not record an independent agent invocation."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Acceptance review receipt must record the independent agent invocation")


class TierTwoAdversarialFallbackError(ValueError):
    """A tier-2 adversarial review omits the observed cross-vendor unavailability."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__(
            "Tier-2 adversarial review requires the observed cross-vendor unavailability"
        )


class CallerSuppliedReviewTierError(ValueError):
    """A review payload supplies the tier the execution transport derives."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Review tier is derived from the execution transport")


class CallerSuppliedReviewIdError(ValueError):
    """A review payload supplies an ID the executed receipt assigns."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Review IDs are assigned from the executed receipt, never caller supplied")


class HumanReviewAttestorError(ValueError):
    """A human review names no attestor."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Human review requires an identified attestor")


class HumanReviewRulingError(ValueError):
    """A human review carries no verbatim operator ruling."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("Human review requires the operator's verbatim ruling")


class MissingAcceptanceHistoryError(ValueError):
    """Readiness is asked of an OBPI with no durable acceptance contract."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__("No durable acceptance contract/proof history")


class ObligationRosterChangedError(ValueError):
    """The canonical obligation roster no longer matches the recorded contract scope."""

    def __init__(self) -> None:
        """Build the fixed refusal message."""
        super().__init__(
            "Canonical obligation roster changed; it cannot silently replace acceptance scope"
        )
