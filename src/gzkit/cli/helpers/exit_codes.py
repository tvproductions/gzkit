"""Standard exit codes and epilog for the gzkit CLI.

Implements the CLI Doctrine 4-code map.
"""

from __future__ import annotations

import textwrap

from gzkit.core.exceptions import GzkitError

EXIT_SUCCESS = 0
"""Command completed successfully."""

EXIT_USER_ERROR = 1
"""User or configuration error — fix invocation or config."""

EXIT_SYSTEM_ERROR = 2
"""Usage error, or system/I/O error.

Every parse error exits 2 (``StableArgumentParser.error``, attested
REQ-0.0.4-02-03), so 2 is not System/IO alone: fix the invocation for a
usage error; check network/disk and retry for an I/O fault (GHI #1001).
"""

EXIT_POLICY_BREACH = 3
"""Governance policy breach — review logs; partial success needs review."""

STANDARD_EXIT_CODES_EPILOG = textwrap.dedent("""\
    Exit codes
        0   Success
        1   User/config error
        2   Usage or System/IO error
        3   Policy breach
""")


def exit_code_for(exc: Exception) -> int:
    """Map an exception to the standard 4-code exit code.

    If *exc* is a :class:`GzkitError` (or subclass), the exit code is read
    from the ``exit_code`` property on the exception itself.  For any other
    exception type, the default is :data:`EXIT_USER_ERROR` (1).
    """
    if isinstance(exc, GzkitError):
        return exc.exit_code
    return EXIT_USER_ERROR
