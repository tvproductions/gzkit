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
from collections.abc import Sequence
from pathlib import Path

from gzkit.executables import resolve_argv
from gzkit.mx import marker


def alarms_off(project_root: Path | None = None) -> bool:
    """Return True while an open safe-mode marker holds the alarms off."""
    held = marker.read(project_root) if marker.is_active(project_root) else None
    return held is not None and held.mode == "safe" and not held.exiting


def main(argv: Sequence[str] | None = None) -> int:
    """Run ``<command...>`` unless safe mode holds the alarms off."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 3 or args[1] != "--":
        print("usage: python -m gzkit.mx.alarms <hook-id> -- <command...>", file=sys.stderr)
        return 2
    if alarms_off():
        print(f"[safe mode] {args[0]} is off until gz mx exit", file=sys.stderr)
        return 0
    return subprocess.run(resolve_argv(args[2:]), check=False).returncode  # noqa: S603


if __name__ == "__main__":
    sys.exit(main())
