"""CLI command handler for OKF knowledge bundle operations (ADR-0.30.0, OBPI-0.30.0-04).

Provides the `gz knowledge generate` and `gz knowledge refresh` commands to emit
and refresh the OKF orientation bundle over the governance tracer slice.
"""

import sys

from gzkit.cli.helpers.exit_codes import EXIT_SUCCESS, EXIT_SYSTEM_ERROR
from gzkit.knowledge import generate_bundle
from gzkit.knowledge.generate import BUNDLE_OUTPUT, TRACER_SLICE


def knowledge_cmd(*, subverb: str | None = None) -> None:
    """Handle 'gz knowledge generate' or 'gz knowledge refresh'.

    Both subcommands invoke the same idempotent generator (subverb is ignored).
    Exit 0 on success; exit 2 on system/IO error.
    """
    try:
        generate_bundle(TRACER_SLICE, BUNDLE_OUTPUT)
        sys.exit(EXIT_SUCCESS)
    except (OSError, FileNotFoundError) as e:
        print(f"Error generating knowledge bundle: {e}", file=sys.stderr)
        sys.exit(EXIT_SYSTEM_ERROR)
