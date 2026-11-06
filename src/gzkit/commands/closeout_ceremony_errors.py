"""Typed errors for the deterministic closeout ceremony (``closeout_ceremony.py``)."""

from gzkit.commands.ceremony_state import CeremonyStep
from gzkit.commands.common import GzCliError
from gzkit.core.exceptions import PolicyBreachError


class CeremonyBlockedError(GzCliError):
    """The ceremony cannot start while readiness blockers remain."""

    def __init__(self, blockers: list[str]) -> None:
        """Build the message from *blockers*."""
        self.blockers = blockers
        super().__init__(f"Cannot start ceremony: {'; '.join(blockers)}")


class AttestationBoundaryError(PolicyBreachError):
    """``--next`` tried to self-advance past the human-attestation boundary without a receipt."""

    def __init__(self, adr_id: str) -> None:
        """Build the message from *adr_id*."""
        self.adr_id = adr_id
        super().__init__(
            f"Step {int(CeremonyStep.ATTESTATION)} (ATTESTATION) -> "
            f"{int(CeremonyStep.CLOSEOUT)} (CLOSEOUT) is the human-attestation "
            "boundary and cannot be self-advanced with --next: no `attested` ledger "
            "receipt was recorded for this ceremony run. Record the operator's "
            f'verdict first:\n  gz closeout {adr_id} --ceremony --attest "<verdict>"'
        )


class CeremonyNotInProgressError(GzCliError):
    """No ceremony state exists for the ADR; ``hint`` names the recovery when one applies."""

    def __init__(self, adr_id: str, hint: str = "") -> None:
        """Build the message from *adr_id*, *hint*."""
        self.adr_id = adr_id
        super().__init__(f"No ceremony in progress for {adr_id}.{hint}")


class CeremonyAlreadyCompletedError(GzCliError):
    """The ADR's ceremony has already completed."""

    def __init__(self, adr_id: str) -> None:
        """Build the message from *adr_id*."""
        self.adr_id = adr_id
        super().__init__(f"Ceremony for {adr_id} already completed.")


class AttestationOutsideStepError(PolicyBreachError):
    """An attestation was offered while the ceremony stands at a step other than ATTESTATION."""

    def __init__(self, current_step: int) -> None:
        """Build the message from *current_step*."""
        self.current_step = current_step
        super().__init__(
            f"Attestation only valid at step {CeremonyStep.ATTESTATION} "
            f"(current: {current_step}). "
            "Cannot attest outside the attestation step."
        )


class CeremonyFlagConflictError(GzCliError):
    """More than one of ``--next``, ``--attest`` and ``--pause`` was given."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("Cannot combine --next, --attest, and --pause.")
