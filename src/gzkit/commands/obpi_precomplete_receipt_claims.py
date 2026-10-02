"""Enforcement claims for the precomplete ARB-receipt gate (GHI #1155, gate GHI #889).

``obpi_precomplete._check_arb_receipts_passed`` once counted receipt files and passed
over 577 failed runs among 3718 receipts. It was repaired, but no registered claim named
it, so its green was unfalsified: a test that seeds receipts with a recorded exit status
proves the gate reads the status, and nothing required the gate to keep reading it.

Two claims, on the exemption-half precedent (GHI #797).

* ``arb-receipt-red-run-refused`` plants, for each required step, a traversal in which
  every step has a green receipt since the lock claim EXCEPT that step, whose newest
  receipt records a failed run (an older green one for it also exists). That is the
  present-but-false input: a receipt exists and its content says the run failed. The
  gate must refuse and name the step's ``exit_status``.
* ``arb-receipt-green-run-admitted`` is the admit control: a fully green traversal is
  not refused, so an always-refuse gate cannot discharge the first claim alone.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

REFUSE_CLAIM_ID = "arb-receipt-red-run-refused"
ADMIT_CLAIM_ID = "arb-receipt-green-run-admitted"
RECEIPT_GATE_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

#: The steps attestation evidence needs, as the operator ruling of GHI #889 names them
#: (lint, typecheck, unittest). Declared here, not read from the gate's own
#: ``_REQUIRED_RECEIPT_STEPS``: a population read from the code under test narrows
#: whenever the witness does and proves nothing.
_REQUIRED_STEPS = ("lint", "typecheck", "unittest")

_OBPI = "OBPI-0.0.0-00-claim-fixture"
_CLAIMED = "2026-09-10T12:00:00+00:00"
_OLDER = "2026-09-11T12:00:00Z"
_NEWER = "2026-09-12T12:00:00Z"
_EXIT_STATUS = "exit_status"


def required_step_population() -> list[str]:
    """Return every step whose red receipt the gate must refuse."""
    return list(_REQUIRED_STEPS)


def _write_receipt(receipts_dir: Path, step: str, stamp: str, exit_status: int) -> None:
    """Write a receipt in the real ARB shape: a lint receipt for ``lint``, else a step receipt."""
    run_id = f"arb-{step}-{stamp[:10]}-{exit_status}"
    identity: dict[str, object] = (
        {"schema": "gzkit.arb.lint_receipt.v1", "tool": {"name": "ruff"}}
        if step == "lint"
        else {"schema": "gzkit.arb.step_receipt.v1", "step": {"name": step, "command": []}}
    )
    payload = {**identity, "run_id": run_id, "timestamp_utc": stamp, "exit_status": exit_status}
    (receipts_dir / f"{run_id}.json").write_text(json.dumps(payload), encoding="utf-8")


def _seed(root: Path, red_step: str | None) -> None:
    """Claim the OBPI and write a green traversal, with ``red_step`` ending on a failed run."""
    locks = root / ".gzkit" / "locks" / "obpi"
    locks.mkdir(parents=True)
    (locks / f"{_OBPI}.lock.json").write_text(
        json.dumps({"obpi_id": _OBPI, "agent": "claim-fixture", "claimed_at": _CLAIMED}),
        encoding="utf-8",
    )
    receipts = root / "artifacts" / "receipts"
    receipts.mkdir(parents=True)
    for step in _REQUIRED_STEPS:
        _write_receipt(receipts, step, _OLDER, 0)
        _write_receipt(receipts, step, _NEWER, int(step == red_step))


def _build_traversal(member: str | None = None) -> str | None:
    """Name the step whose newest receipt is red; ``None`` plants a fully green traversal."""
    return member


# Each entrypoint imports the gate itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _ep_red_run_refused(step: str) -> list[str]:
    """Return a finding naming *step* when the gate refuses its red newest receipt, else nothing.

    The receipt exists and its content records a failed run; the gate must refuse it and name
    the recorded exit status, not merely refuse for some other reason (GHI #699).
    """
    from gzkit.commands.obpi_precomplete import _check_arb_receipts_passed  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed(root, red_step=step)
        result = _check_arb_receipts_passed(root, _OBPI)
    refused = not result.ok and f"{step}: " in result.message and _EXIT_STATUS in result.message
    return [f"refused red {step}: {result.message}"] if refused else []


def _ep_green_run_admitted(red_step: str | None) -> int:
    """Truthy only when a fully green traversal is NOT refused."""
    from gzkit.commands.obpi_precomplete import _check_arb_receipts_passed  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed(root, red_step=red_step)
        return 1 if _check_arb_receipts_passed(root, _OBPI).ok else 0


class _ReceiptGateMarker:
    """Inert carrier for the receipt-gate ``@enforces`` registrations."""


def ensure_receipt_gate_claims_registered() -> None:
    """(Re)register the precomplete receipt-gate claims (idempotent, reset-safe).

    MUST stay wired into ``enforcement._ensure_production_claims_registered``: a
    registration authored but un-wired there is an ORPHAN whose floor membership is a
    facade.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        POPULATION_NONE,
        enforces,
        extend_known_claims,
        get_enforcement_registry,
    )

    extend_known_claims(RECEIPT_GATE_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_traversal,
            _ep_red_run_refused,
            expect=_EXIT_STATUS,
            exempts=ADMIT_CLAIM_ID,
            population=required_step_population,
        )(_ReceiptGateMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_traversal,
            _ep_green_run_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_ReceiptGateMarker)
