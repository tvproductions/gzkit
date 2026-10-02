"""Enforcement claims for the ``gz tidy`` verdict (GHI #1155, gate GHI #1124).

``tidy.tidy`` once exited 0 with 456 findings and printed "Project is tidy" over an
actionable settings-vault notice. It was repaired so that findings set the exit code, but no
registered claim named the handler, so the repair's green was unfalsified.

Two claims, on the exemption-half precedent (GHI #797).

* ``tidy-breach-exits-three`` runs the real handler over each class of finding it must gate on
  (a validation issue, an orphaned OBPI, every actionable settings-vault state, and a finding
  that ``--fix`` leaves open) and requires exit 3 with the success line withheld. A handler
  that reports a finding and exits 0 is the present-but-false input.
* ``tidy-clean-exits-zero`` is the admit control: a clean tree, a queue of ADRs pending
  attestation (informational, operator ruling 2026-09-28) and a finding that ``--fix``
  repaired all exit 0 with the success line, so an always-exit-3 handler cannot discharge the
  first claim alone.

The handler has no seam for its collaborators, so each run binds them on the handler's module
for the call and restores them after, the way the findings themselves would arrive.
"""

from __future__ import annotations

import contextlib
import io
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

REFUSE_CLAIM_ID = "tidy-breach-exits-three"
ADMIT_CLAIM_ID = "tidy-clean-exits-zero"
TIDY_VERDICT_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_TIDY_MODULE = "gzkit.commands.tidy"
_SUCCESS = "Project is tidy"
_EXITED = "exited 3 without the success line"
_VALIDATION = "validation-issue"
_ORPHAN = "orphaned-obpi"
_UNREPAIRED = "unrepaired-after-fix"
_VAULT_PREFIX = "vault-"
_FINDING = SimpleNamespace(type="header", message="claim fixture finding")
_ORPHANED_GRAPH = {"OBPI-0.0.0-00-claim": {"type": "obpi", "parent": "ADR-0.0.0-missing"}}


def _actionable_vault_states() -> list[str]:
    """Return every settings-vault state the vault module itself calls actionable."""
    from gzkit.settings_vault import VaultState, VaultStatus  # noqa: PLC0415

    return [
        state.name
        for state in VaultState
        if VaultStatus(state=state, directory=Path(), snapshot_count=0, message="").is_actionable
    ]


def breach_population() -> list[str]:
    """Return every class of finding the verdict must gate on."""
    return [
        _VALIDATION,
        _ORPHAN,
        *(f"{_VAULT_PREFIX}{name}" for name in _actionable_vault_states()),
        _UNREPAIRED,
    ]


@contextlib.contextmanager
def _bound(module: ModuleType, **names: Any) -> Iterator[None]:
    """Bind *names* on *module* for the block, then restore every one of them."""
    saved = {name: getattr(module, name) for name in names}
    for name, value in names.items():
        setattr(module, name, value)
    try:
        yield
    finally:
        for name, value in saved.items():
            setattr(module, name, value)


def _run_tidy(
    handler: Callable[..., None],
    *,
    errors: tuple[Any, ...] = (),
    graph: dict[str, Any] | None = None,
    pending: tuple[str, ...] = (),
    vault_state: str = "CURRENT",
    fix: bool = False,
    errors_after_fix: tuple[Any, ...] = (),
) -> tuple[int, str]:
    """Run the real *handler* over the given findings; return (exit code, rendered output).

    The collaborators are bound on the handler's own module, ``gzkit.commands.tidy``.
    """
    from rich.console import Console  # noqa: PLC0415

    from gzkit.settings_vault import VaultState, VaultStatus  # noqa: PLC0415

    module = sys.modules[_TIDY_MODULE]
    runs = iter([errors, errors_after_fix])
    ledger = SimpleNamespace(
        get_artifact_graph=lambda: graph or {}, get_pending_attestations=lambda: list(pending)
    )
    vault = VaultStatus(
        state=VaultState[vault_state], directory=Path(), snapshot_count=1, message="note"
    )
    buffer = io.StringIO()
    with _bound(
        module,
        console=Console(file=buffer, width=200, color_system=None),
        ensure_initialized=lambda: SimpleNamespace(paths=SimpleNamespace(ledger="ledger.jsonl")),
        get_project_root=lambda: Path(),
        validate_all=lambda _root: SimpleNamespace(errors=list(next(runs))),
        Ledger=lambda _path: ledger,
        vault_status=lambda _root: vault,
        refuse_on_sync_blockers=lambda *_args: None,
        sync_all=lambda *_args: None,
        _post_sync_check=lambda *_args: None,
    ):
        try:
            handler(check_only=False, fix=fix, dry_run=False)
        except SystemExit as exc:
            return (exc.code if isinstance(exc.code, int) else 1), buffer.getvalue()
    return 0, buffer.getvalue()


def _plant(member: str) -> dict[str, Any]:
    """Return the findings to feed the handler for the breach class *member*."""
    if member == _VALIDATION:
        return {"errors": (_FINDING,)}
    if member == _ORPHAN:
        return {"graph": _ORPHANED_GRAPH}
    if member == _UNREPAIRED:
        return {"errors": (_FINDING,), "fix": True, "errors_after_fix": (_FINDING,)}
    return {"vault_state": member.removeprefix(_VAULT_PREFIX)}


def _build_breach(member: str | None = None) -> str | None:
    """Name the breach class to plant; ``None`` plants the admit scenarios."""
    return member


# Each entrypoint imports the handler itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _ep_breach_exits_three(member: str) -> list[str]:
    """Return a finding naming *member* when the handler exits 3 and withholds the success line."""
    from gzkit.commands.tidy import tidy  # noqa: PLC0415

    code, output = _run_tidy(tidy, **_plant(member))
    return [f"{member}: {_EXITED}"] if code == 3 and _SUCCESS not in output else []


def _ep_clean_exits_zero(_member: str | None) -> int:
    """Truthy only when every non-breach scenario exits 0 with the success line."""
    from gzkit.commands.tidy import tidy  # noqa: PLC0415

    scenarios: tuple[dict[str, Any], ...] = (
        {},
        {"pending": ("ADR-pool.claim-fixture",)},
        {"errors": (_FINDING,), "fix": True, "errors_after_fix": ()},
    )
    results = [_run_tidy(tidy, **scenario) for scenario in scenarios]
    return 1 if all(code == 0 and _SUCCESS in out for code, out in results) else 0


class _TidyVerdictMarker:
    """Inert carrier for the ``gz tidy`` verdict ``@enforces`` registrations."""


def ensure_tidy_verdict_claims_registered() -> None:
    """(Re)register the ``gz tidy`` verdict claims (idempotent, reset-safe).

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

    extend_known_claims(TIDY_VERDICT_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_breach,
            _ep_breach_exits_three,
            expect=_EXITED,
            exempts=ADMIT_CLAIM_ID,
            population=breach_population,
        )(_TidyVerdictMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_breach,
            _ep_clean_exits_zero,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_TidyVerdictMarker)
