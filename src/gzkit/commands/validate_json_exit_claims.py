"""Enforcement claims for ``gz validate --json`` exit classification (GHI #1155, gate GHI #995).

``validate_cmd.validate`` once returned from its ``as_json`` branch before the exit
classification, so every aggregate scope exited 0 in ``--json`` mode whatever it found: the
payload said ``"valid": false`` while the status said success. It was repaired, but no
registered claim named the handler (``validate-default-scopes`` names ``_collect_errors``,
the finder, not the exit path), so the repair's green was unfalsified.

Two claims, on the exemption-half precedent (GHI #797).

* ``validate-json-exit-classified`` runs the real handler in ``--json`` mode over a tree
  that really fails each class of finding (a policy breach, a non-policy error) and
  requires a non-zero exit. A body that reports failure while the status reports success is
  the present-but-false input.
* ``validate-json-exit-clean-passes`` is the admit control: a clean tree in ``--json`` mode
  still returns, so an always-exit-nonzero handler cannot discharge the first alone.
"""

from __future__ import annotations

import contextlib
import inspect
import io
import sys
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType

REFUSE_CLAIM_ID = "validate-json-exit-classified"
ADMIT_CLAIM_ID = "validate-json-exit-clean-passes"
JSON_EXIT_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_POLICY = "policy-breach"
_NON_POLICY = "non-policy-error"
_CLASSIFIED = "--json exit classified"

#: The classes of finding the 4-code map distinguishes (``validate``'s docstring: 3 for a
#: policy breach, 1 for any other error). Declared here rather than read from the
#: handler's ``_POLICY_BREACH_ERROR_TYPES``, which is the code under test.
_FINDING_CLASSES = (_POLICY, _NON_POLICY)


def finding_class_population() -> list[str]:
    """Return every class of finding whose ``--json`` exit must be non-zero."""
    return list(_FINDING_CLASSES)


def _plant(root: Path, finding_class: str | None) -> str:
    """Plant a tree that fails *finding_class* for real; return the scope that finds it.

    ``None`` plants a tree the same scope finds clean. A malformed insights line is a
    policy-breach finding (``insights_shape``); an uninitialised tree has no manifest,
    a non-policy ``manifest`` finding.
    """
    if finding_class == _NON_POLICY:
        return "check_manifest"
    if finding_class == _POLICY:
        insights = root / ".gzkit" / "insights"
        insights.mkdir(parents=True)
        (insights / "agent-insights.jsonl").write_text("not a json record\n", encoding="utf-8")
    return "check_insights_shape"


@contextlib.contextmanager
def _project_root_is(module: ModuleType, root: Path) -> Iterator[None]:
    """Point *module*'s ``get_project_root`` at *root* for the block, then restore it.

    The handler reads the project root from the process cwd. Binding it here, instead of
    changing directory, keeps the claim independent of the cwd of whoever runs the floor
    (the pre-commit guard runs it with ``Path.cwd`` patched).
    """
    original = module.get_project_root
    module.get_project_root = lambda: root  # ty: ignore[unresolved-attribute]
    try:
        yield
    finally:
        module.get_project_root = original  # ty: ignore[unresolved-attribute]


def _json_exit(handler: Callable[..., None], finding_class: str | None) -> int:
    """Run the real *handler* in ``--json`` mode on a planted tree; return its exit code.

    ``0`` means the handler returned without exiting: it signalled success.
    """
    params = inspect.signature(handler).parameters
    kwargs = {
        name: p.default is not inspect.Parameter.empty and p.default for name, p in params.items()
    }
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        scope = _plant(root, finding_class)
        code = 0
        try:
            with (
                _project_root_is(sys.modules[handler.__module__], root),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                handler(**{**kwargs, scope: True, "as_json": True})
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
    return code


# Each entrypoint imports the handler itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _build_finding_class(member: str | None = None) -> str | None:
    """Name the finding class to plant; ``None`` plants a clean tree."""
    return member


def _ep_json_exit_classified(finding_class: str | None) -> list[str]:
    """Return a finding when the handler's ``--json`` mode exits non-zero on a failing tree."""
    from gzkit.commands.validate_cmd import validate  # noqa: PLC0415

    code = _json_exit(validate, finding_class)
    return [f"{finding_class}: {_CLASSIFIED} as {code}"] if code else []


def _ep_clean_json_returns(finding_class: str | None) -> int:
    """Truthy only when a clean tree in ``--json`` mode returns without a non-zero exit."""
    from gzkit.commands.validate_cmd import validate  # noqa: PLC0415

    return 0 if _json_exit(validate, finding_class) else 1


class _JsonExitMarker:
    """Inert carrier for the ``--json`` exit ``@enforces`` registrations."""


def ensure_json_exit_claims_registered() -> None:
    """(Re)register the ``validate --json`` exit claims (idempotent, reset-safe).

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

    extend_known_claims(JSON_EXIT_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_finding_class,
            _ep_json_exit_classified,
            expect=_CLASSIFIED,
            exempts=ADMIT_CLAIM_ID,
            population=finding_class_population,
        )(_JsonExitMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_finding_class,
            _ep_clean_json_returns,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_JsonExitMarker)
