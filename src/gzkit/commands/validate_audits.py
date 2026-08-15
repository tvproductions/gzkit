"""The `gz validate --audits` umbrella runner.

GHI #704 hardened a family of validate scopes to solo-only: combining one with
any other scope is refused outright, because the earlier behavior silently
dropped it while still reporting success — a false green for a gate that never
ran. ``--audits`` set two of those scopes (``--unscoped-rules``,
``--sensitivity``) alongside six aggregate ones, so after that fix the umbrella
refused *itself* on every invocation: exit 1, nothing run.

Nothing caught it. No ``gz check`` step calls ``--audits``, and its only test
asserted that the dispatcher kwargs were threaded — which they still were. The
wiring was never what broke.

Running each solo member in a pass of its own honors both contracts at once: the
umbrella means what its help text says, and every member keeps the full 0/2/3
exit lifecycle the solo-only fence exists to protect.

Split out of ``validate_cmd.py`` for module-size discipline
(`.claude/rules/pythonic.md`).
"""

from __future__ import annotations

from typing import Any

#: Members that own a solo early-return lifecycle — each needs its own pass.
AUDITS_SOLO_MEMBERS: tuple[str, ...] = (
    "check_unscoped_rules",
    "check_sensitivity",
)

#: Members that run together on the aggregate path.
AUDITS_AGGREGATE_MEMBERS: tuple[str, ...] = (
    "check_type_ignores",
    "check_cli_alignment",
    "check_event_handlers",
    "check_validator_fields",
    "check_doc_surface_parity",
    "check_orphaned_implementation",
)

#: `validate()` requires these positionally; an audits pass never wants them.
_REQUIRED_OFF: tuple[str, ...] = (
    "check_manifest",
    "check_documents",
    "check_surfaces",
    "check_ledger",
    "check_instructions",
    "check_briefs",
)


def run_audits_pass(scopes: dict[str, bool], *, as_json: bool) -> int:
    """Run one `--audits` pass, returning its exit code rather than raising."""
    from gzkit.commands.validate_cmd import validate  # noqa: PLC0415

    kwargs: dict[str, Any] = dict.fromkeys(_REQUIRED_OFF, False)
    kwargs["as_json"] = as_json
    kwargs.update(scopes)
    try:
        validate(**kwargs)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    return 0


def run_audits_umbrella(*, as_json: bool) -> None:
    """Run every `--audits` member; solo-only members each get their own pass.

    The worst exit code across the passes wins, so a policy breach in any one
    member still surfaces as the umbrella's own exit status.
    """
    worst = 0
    for member in AUDITS_SOLO_MEMBERS:
        worst = max(worst, run_audits_pass({member: True}, as_json=as_json))
    worst = max(
        worst,
        run_audits_pass(dict.fromkeys(AUDITS_AGGREGATE_MEMBERS, True), as_json=as_json),
    )
    if worst:
        raise SystemExit(worst)
