"""Enforcement claim for `.gzkit/rules/cli.md` § Exit Codes code 2 (GHI #1001).

Every parse error exits 2 (attested REQ-0.0.4-02-03), so code 2 means a usage
error OR a system/IO error, and the help epilog every command prints must say so.
Until rule `0.7.0` the map and the epilog called 2 System/IO alone, so a typo was
reported to the operator as a disk fault. The advisory scorecard's Mechanical
row for that clause cites this claim.

Imported lazily from ``gzkit.enforcement._ensure_production_claims_registered``,
never from the parser tree, so ``gz --help`` pays nothing for it.
"""

from __future__ import annotations

import io
from contextlib import redirect_stderr
from pathlib import Path

CLI_USAGE_ERROR_EXIT_TWO_CLAIM_ID = "cli-usage-error-exit-two"

CLI_EXIT_CODE_CLAIM_IDS: frozenset[str] = frozenset({CLI_USAGE_ERROR_EXIT_TWO_CLAIM_ID})


def _build_usage_error_fixture() -> Path:
    """Return a runner-owned temp root whose NAME seeds a runtime-unique flag.

    A fixed flag would let a broken parser special-case one sentinel; the token
    is unknowable when a mutation is authored.
    """
    from gzkit.enforcement import create_fixture_tempdir  # noqa: PLC0415

    return create_fixture_tempdir(prefix="gzkit-cli-exit-two-nc-")


def _exit_code_of(parse) -> int | None:
    """Run ``parse`` and return the SystemExit code it raised, or None if it returned."""
    try:
        with redirect_stderr(io.StringIO()):
            parse()
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    return None


def _ep_usage_error_exit_two(root: Path) -> int:
    """Truthy only when all three poles hold.

    Refuse: an undeclared flag exits 2 with the ``BLOCKERS:`` prefix on stderr.
    Permit: a declared flag parses without exiting, so an always-exit parser
    cannot discharge the claim. Label: the shared epilog's code-2 line names both
    usage and system/IO — the help text is the operator's reading of the code.
    """
    from gzkit.cli.helpers import exit_codes  # noqa: PLC0415
    from gzkit.cli.parser import StableArgumentParser  # noqa: PLC0415

    token = f"--nc-{root.name.lower().replace('_', '-')}"
    parser = StableArgumentParser(prog="gz-nc")
    parser.add_argument("--declared", action="store_true")

    stderr = io.StringIO()
    try:
        with redirect_stderr(stderr):
            parser.parse_args([token])
        refused = False
    except SystemExit as exc:
        refused = exc.code == 2 and stderr.getvalue().startswith("BLOCKERS:")

    permitted = _exit_code_of(lambda: parser.parse_args(["--declared"])) is None

    code_two = next(
        (
            line.strip().lower()
            for line in exit_codes.STANDARD_EXIT_CODES_EPILOG.splitlines()
            if line.strip().startswith("2 ")
        ),
        "",
    )
    labelled = "usage" in code_two and "system/io" in code_two
    return 1 if (refused and permitted and labelled) else 0


def _cli_exit_code_marker() -> None:
    """Inert carrier for the exit-code ``@enforces`` registration."""


def ensure_cli_exit_code_claims_registered() -> None:
    """(Re)register the exit-code-2 enforcement claim (idempotent, reset-safe).

    MUST stay wired into ``_ensure_production_claims_registered`` — a
    registration reachable from nowhere else is an orphan whose floor
    membership is a facade.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        enforces,
        extend_known_claims,
        get_enforcement_registry,
    )

    extend_known_claims(CLI_EXIT_CODE_CLAIM_IDS)
    if CLI_USAGE_ERROR_EXIT_TWO_CLAIM_ID not in {r.claim_id for r in get_enforcement_registry()}:
        enforces(
            CLI_USAGE_ERROR_EXIT_TWO_CLAIM_ID,
            _build_usage_error_fixture,
            _ep_usage_error_exit_two,
            exempts=EXEMPTS_NONE,
        )(_cli_exit_code_marker)
