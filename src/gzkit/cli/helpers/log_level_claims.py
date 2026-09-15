"""Enforcement claim for `.gzkit/rules/cli.md` § Flag Conventions verbosity rows.

`docs/design/cli-standards-v3.md` § Verbosity Levels (canonical per ADR-0.0.4):
the default logs warnings and errors, `--quiet` errors only, `--verbose` adds
INFO, `--debug` adds DEBUG, and every log record goes to stderr. The rule row
read "`--verbose` Debug output" and the adapter's level map copied it, unnoticed
because `configure_logging` ran nowhere until GHI #1010 wired it into
`cli/main.py`. The advisory scorecard's Mechanical row for that clause cites this
claim.

Imported lazily from ``gzkit.enforcement._ensure_production_claims_registered``,
never from the parser tree, so ``gz --help`` pays nothing for it.
"""

from __future__ import annotations

import argparse
import io
import logging
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import structlog

CLI_LOG_LEVELS_CLAIM_ID = "cli-log-levels-follow-spec"

CLI_LOG_LEVEL_CLAIM_IDS: frozenset[str] = frozenset({CLI_LOG_LEVELS_CLAIM_ID})

# (flags set on the parsed namespace, level that must show, level that must not)
_POLES: tuple[tuple[dict[str, bool], int, int | None], ...] = (
    ({}, logging.WARNING, logging.INFO),
    ({"quiet": True}, logging.ERROR, logging.WARNING),
    ({"verbose": True}, logging.INFO, logging.DEBUG),
    ({"quiet": True, "debug": True}, logging.DEBUG, None),
)


def _build_log_level_fixture() -> Path:
    """Return a runner-owned temp root whose NAME seeds a runtime-unique event token.

    A fixed event name would let a broken configuration special-case one sentinel;
    the token is unknowable when a mutation is authored.
    """
    from gzkit.enforcement import create_fixture_tempdir  # noqa: PLC0415

    return create_fixture_tempdir(prefix="gzkit-cli-log-levels-nc-")


def _pole_holds(flags: dict[str, bool], shown: int, hidden: int | None, token: str) -> bool:
    """Configure logging from *flags* through the entrypoint and observe both streams."""
    from gzkit.cli.main import configure_logging_from_flags  # noqa: PLC0415

    args = argparse.Namespace(**{"quiet": False, "verbose": False, "debug": False, **flags})
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        configure_logging_from_flags(args)
        log = structlog.get_logger()
        log.log(shown, f"{token}-shown")
        if hidden is not None:
            log.log(hidden, f"{token}-hidden")
    visible = f"{token}-shown" in stderr.getvalue()
    suppressed = hidden is None or f"{token}-hidden" not in stderr.getvalue()
    return visible and suppressed and token not in stdout.getvalue()


def _ep_log_levels_follow_spec(root: Path) -> int:
    """Truthy only when every verbosity pole holds on the live entrypoint.

    Each pole names a level that must reach stderr and one that must not, so an
    always-silent or always-verbose configuration cannot discharge the claim, and
    nothing may reach stdout. Process logging state is restored afterwards: the
    enforcement floor runs in-process inside ``gz check``.
    """
    token = f"nc-{root.name.lower().replace('_', '-')}"
    root_logger = logging.getLogger()
    saved_handlers, saved_level = list(root_logger.handlers), root_logger.level
    saved_structlog = structlog.get_config()
    try:
        held = all(_pole_holds(flags, shown, hidden, token) for flags, shown, hidden in _POLES)
    finally:
        root_logger.handlers[:] = saved_handlers
        root_logger.setLevel(saved_level)
        structlog.reset_defaults()
        structlog.configure(**saved_structlog)
    return 1 if held else 0


def _cli_log_level_marker() -> None:
    """Inert carrier for the log-level ``@enforces`` registration."""


def ensure_cli_log_level_claims_registered() -> None:
    """(Re)register the log-level enforcement claim (idempotent, reset-safe).

    MUST stay wired into ``_ensure_production_claims_registered`` — a
    registration reachable from nowhere else is an orphan whose floor
    membership is a facade.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        POPULATION_NONE,
        enforces,
        extend_known_claims,
        get_enforcement_registry,
    )

    extend_known_claims(CLI_LOG_LEVEL_CLAIM_IDS)
    if CLI_LOG_LEVELS_CLAIM_ID not in {r.claim_id for r in get_enforcement_registry()}:
        enforces(
            CLI_LOG_LEVELS_CLAIM_ID,
            _build_log_level_fixture,
            _ep_log_levels_follow_spec,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_cli_log_level_marker)
