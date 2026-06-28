"""Gate-5 invariants — the never-relax floor for MX mode.

ADR-0.0.74 Decision item #3: the integrity-class guards as a code constant
(not config). The shared checkpoint reads this constant and structurally
cannot resolve a member below CRITICAL, in or out of the hangar.

grader-gaming joins because the observability system is itself a grader and
models game graders increasingly (Opus 4.8 § 6.1.2). A grader-gaming guard
that could go advisory in the hangar would make MX the safe place to vibe
undetected. Its floor membership is made *live* (not merely named) by
OBPI-0.0.74-13's proxy-reality detector per the §5 enforcement-claim rule.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from gzkit.enforcement import enforces, get_enforcement_registry, set_known_claims

GATE5_INVARIANTS: frozenset[str] = frozenset(
    {
        "gate5-attestation",  # faked Gate-5 attestation
        "secrets",  # secrets leakage guard
        "operator-pii",  # operator-PII protection
        "ledger",  # ledger integrity (validate_cmd scope)
        "grader-gaming",  # grader-gaming (live detector: OBPI-0.0.74-13)
    }
)

# ---------------------------------------------------------------------------
# Gate5 floor enforcement-claim migration (OBPI-0.0.74-17)
# ---------------------------------------------------------------------------
#
# Four GATE5_INVARIANTS members lacked an @enforces entry (grader-gaming is
# OBPI-13). This migrates them onto the enforcement-claim surface:
#
#   * ``ledger`` and ``gate5-attestation`` are BOUND to a genuine gate5
#     production path; each carries a live UN-FORCED negative control that runs
#     that real path against a synthetic violation and asserts it is caught.
#   * ``secrets`` and ``operator-pii`` are the HONEST NEGATIVE (ADR-0.0.74
#     § Consequences/Negative #7): no unified gate5 production entrypoint exists
#     today — ``validate_no_secrets`` is handoff-scoped and ``_EMAIL_RE`` is
#     insights-scoped. They are surfaced as named-not-enforced via
#     ``_GATE5_NAMED_NOT_ENFORCED``; binding a NARROWER PROXY entrypoint to fake
#     coverage is FORBIDDEN. Standing up the real gate is named prerequisite work.
#
# Genuineness is structural (§ Boundary Invariants #7): the fixture builds the
# violation and NEVER calls the validator; only the production entrypoint decides
# catch/no-catch, and no entrypoint pre-binds a forcing kwarg.

_GATE5_NAMED_NOT_ENFORCED: frozenset[str] = frozenset({"secrets", "operator-pii"})

_GATE5_CLAIM_IDS: frozenset[str] = frozenset({"gate5-ledger", "gate5-attestation-absence"})


def _build_gate5_ledger_violation() -> Path:
    """Build a temp project whose ledger the real ``validate_ledger`` path catches.

    The gzkit ledger is append-only JSONL with no cryptographic hash chain; its
    integrity path is schema/shape conformance. The synthetic violation is a
    corrupted ledger: an invalid-JSON line plus a line missing the required
    ``id``/``ts`` fields. The runner removes the temp dir after the entrypoint runs.
    """
    root = Path(tempfile.mkdtemp(prefix="gzkit-gate5-ledger-nc-"))
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text(
        '{ this is not valid json\n{"schema": "gzkit.ledger.v1", "event": "prd_created"}\n',
        encoding="utf-8",
    )
    return root


def _ep_gate5_ledger(root: Path) -> list[Any]:
    """Production entrypoint: run the real ledger-integrity validator on the fixture.

    Returns the validator's error list — truthy (non-empty) when the corruption is
    caught. Lazy import avoids pulling the validate package into the widely-imported
    ``mx.invariants`` module at import time.
    """
    from gzkit.validate_pkg.ledger_check import validate_ledger  # noqa: PLC0415

    return validate_ledger(root / ".gzkit" / "ledger.jsonl")


def _build_gate5_attestation_absence() -> dict[str, Any]:
    """Build a heavy completion evidence payload with a MISSING attestation (the absence case).

    Every field except ``attestation_text`` is valid, so the ONLY violation the real
    attestation-field validator can complain about is the absent attestation — the
    NC isolates the absence case, not a malformed date or placeholder attestor.
    """
    return {
        "attestor": "Test Attestor",
        "evidence": {
            "human_attestation": True,
            "attestation_text": "",  # THE VIOLATION — absent attestation
            "attestation_date": "2026-01-01",
        },
    }


def _ep_gate5_attestation_absence(scenario: dict[str, Any]) -> bool:
    """Production entrypoint: reject a missing attestation through the real gates.

    Runs BOTH real production checks against the absence payload: the
    ``_requires_human_obpi_attestation`` gate (heavy completion must require human
    attestation) AND the ``_validate_obpi_human_attestation_fields`` validator that
    ``gz obpi complete`` invokes (it raises ``GzCliError`` on an empty attestation).
    Returns True when production rejects the absence. Genuine: if either check
    regressed — the gate to "no attestation required", or the field validator to
    accept empty text — the violation would slip and this returns False (FACADE).
    Forgery-detection is OUT — only the absence case is NC-able. Lazy import avoids
    pulling the commands package into ``mx.invariants`` at import time.
    """
    from gzkit.commands.adr_audit import (  # noqa: PLC0415
        _requires_human_obpi_attestation,
        _validate_obpi_human_attestation_fields,
    )
    from gzkit.commands.common import GzCliError  # noqa: PLC0415

    if not _requires_human_obpi_attestation(None, "heavy"):
        return False
    try:
        _validate_obpi_human_attestation_fields(scenario["evidence"], scenario["attestor"])
    except GzCliError:
        return True
    return False


_GATE5_ENFORCEMENT_TABLE: tuple[tuple[str, Callable[[], Any], Callable[[Any], Any]], ...] = (
    ("gate5-ledger", _build_gate5_ledger_violation, _ep_gate5_ledger),
    ("gate5-attestation-absence", _build_gate5_attestation_absence, _ep_gate5_attestation_absence),
)


def _gate5_marker() -> None:
    """Inert carrier for @enforces registration (the fixture/entrypoint are the contract)."""


def _ensure_gate5_claims_registered() -> None:
    """(Re)register the two BOUND gate5 floor enforcement claims (idempotent, reset-safe).

    ``secrets`` and ``operator-pii`` are deliberately NOT registered — they are the
    honest-negative named-not-enforced members (``_GATE5_NAMED_NOT_ENFORCED``);
    binding a narrower proxy for them is forbidden (ADR-0.0.74 § Consequences/Neg #7).

    Extends the enforcement known-claims set with the gate5 ids before decorating so
    the @enforces decoration-time validation accepts them, then registers each bound
    member, skipping any already present. Production discovery wiring into the
    meta-validator runner is OBPI-0.0.74-19 (strict-no-debt floor wiring); this
    module does not auto-register at import to keep ``mx.invariants`` lightweight.
    """
    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )

    set_known_claims(_KNOWN_QC_CLAIM_IDS | _GATE5_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    for claim_id, fixture, entrypoint in _GATE5_ENFORCEMENT_TABLE:
        if claim_id in existing:
            continue
        enforces(claim_id, fixture, entrypoint)(_gate5_marker)
