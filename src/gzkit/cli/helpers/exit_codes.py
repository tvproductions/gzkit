"""Standard exit codes and epilog for the gzkit CLI.

Implements the CLI Doctrine 4-code map.
"""

import textwrap

EXIT_SUCCESS = 0
"""Command completed successfully."""

EXIT_USER_ERROR = 1
"""User or configuration error — fix invocation or config."""

EXIT_SYSTEM_ERROR = 2
"""System or I/O error — check network/disk; retry."""

EXIT_POLICY_BREACH = 3
"""Governance policy breach — review logs; partial success needs review."""

STANDARD_EXIT_CODES_EPILOG = textwrap.dedent("""\
    Exit codes
        0   Success
        1   User/config error
        2   System/IO error
        3   Policy breach
""")
