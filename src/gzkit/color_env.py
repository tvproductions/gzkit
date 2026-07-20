"""Terminal-colour environment semantics (GHI #663).

Single source for the ``NO_COLOR`` / ``FORCE_COLOR`` decision every console
construction site shares. Both prior sites decided by *presence*
(``os.environ.get("FORCE_COLOR") is not None``), which inverted the convention:
``FORCE_COLOR=0`` — the documented way to turn forcing off — is a non-``None``
string, so it forced colour ON. ``NO_COLOR`` never suppressed ``force_terminal``,
so Rich kept emitting bold SGR codes into non-TTY captures.

Conventions implemented:
  * https://no-color.org — ``NO_COLOR`` set to a **non-empty** value disables
    colour, and wins over ``FORCE_COLOR``.
  * ``FORCE_COLOR`` is read by value: ``0``/``false`` disable forcing, any other
    value (``1``, ``2``, ``3``, ``true``) enables it.

Both helpers take the environment as a parameter rather than reaching for
``os.environ`` internally, per `.claude/rules/hexagonal-architecture.md`
§ operative rule 4 — which keeps them exercisable without mutating process
state.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

# Values that mean "off" for FORCE_COLOR. Compared case-insensitively.
_FALSEY = frozenset({"0", "false"})


def _resolve(env: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if env is None else env


def should_disable_color(env: Mapping[str, str] | None = None) -> bool:
    """Return True when ``NO_COLOR`` is set to a non-empty value.

    An empty ``NO_COLOR`` is *not* set, per no-color.org — the prior
    ``is not None`` check treated ``NO_COLOR=""`` as a request to disable.
    """
    return bool(_resolve(env).get("NO_COLOR", ""))


def should_force_terminal(env: Mapping[str, str] | None = None) -> bool:
    """Return True when colour output should be forced on a non-TTY.

    ``NO_COLOR`` takes precedence: forcing a terminal while colour is disabled
    still emits bold SGR codes, which is what made ``NO_COLOR`` alone
    insufficient to get clean captured output.
    """
    resolved = _resolve(env)
    if should_disable_color(resolved):
        return False
    raw = resolved.get("FORCE_COLOR")
    if raw is None:
        return False
    return raw.strip().lower() not in _FALSEY
