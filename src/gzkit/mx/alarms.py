"""Safe mode turns the alarms off; ``gz mx exit`` turns them back on.

Operator ruling 2026-10-25, verbatim: *"i don't want any long check at all - this is a
remodel, things are going to be broken, disarray, and messy. it is time to leave things
partially broken until the reconfiguration is complete, then we adjust tests and turn
the "security alarms" back on."*

An alarm hook runs through ``python -m gzkit.mx.alarms <hook-id> -- <command...>``.
While the marker carries ``mode: safe`` the command does not run at all; otherwise it
runs unchanged and its exit status is the hook's. The marker ``gz mx exit`` holds
through its re-run is ``exiting``, so the exit gate runs every alarm at full strength.
The secret scan and the authorship check are not alarms and never route through here.
"""

import subprocess
import sys
from typing import TYPE_CHECKING

from gzkit.executables import resolve_argv
from gzkit.mx import marker

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


def alarms_off(project_root: Path | None = None) -> bool:
    """Return True while an open safe-mode marker holds the alarms off.

    Returns:
        True when the condition is on and the marker is in safe mode.

    """
    held = marker.condition(project_root)
    return held.on and held.marker is not None and held.marker.mode == "safe"


def main(argv: Sequence[str] | None = None) -> int:
    """Run ``<command...>`` unless safe mode holds the alarms off.

    Returns:
        2 on a usage error, 0 when the alarm is off, else the command's exit status.

    """
    args = list(sys.argv[1:] if argv is None else argv)
    if args[1:2] != ["--"] or not args[2:]:
        sys.stderr.write("usage: python -m gzkit.mx.alarms <hook-id> -- <command...>\n")
        return 2
    if alarms_off():
        sys.stderr.write(f"[safe mode] {args[0]} is off until gz mx exit\n")
        return 0
    return subprocess.run(resolve_argv(args[2:]), check=False).returncode  # noqa: S603


if __name__ == "__main__":
    sys.exit(main())
