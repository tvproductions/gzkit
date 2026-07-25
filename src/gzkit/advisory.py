"""The advisory channel: findings that must surface without changing an exit code.

``ValidationError`` carries no severity field, and ``gz validate`` treats every
returned entry as exit-code-changing (exit 1 for ordinary types, exit 3 for
policy breaches). An audit whose finding must *not* gate therefore has no way to
speak through its return value — it has to write to a stream as a side effect.
:mod:`gzkit.governance.trust_audits.complexity_thresholds` states the rule
outright: *"A warning that should surface but not change exit code must be
emitted as a side effect, not as a list entry."*

That left the channel informal. Four audits invented four different prefixes
(``Bootstrap-mode:``, ``scenario-reachability:``, ``WARNING [x, staged warn]:``,
``NOTE [x]``), and the ``gz check`` aggregator — which renders a step's captured
output only when the step *fails* — could not recognize any of them, so every
advisory was discarded on the green path (GHI #713).

This module makes the channel explicit. An advisory is a line carrying
:data:`ADVISORY_MARKER`; anything else on the stream is ordinary chatter. That
distinction cannot be skipped: ``unittest`` writes its entire summary to stderr,
so "render a passing step's stderr" would bury the signal it was meant to carry.
"""

from __future__ import annotations

import sys
from typing import TextIO

#: Leading token identifying a line as advisory. Deliberately a *prefix* so an
#: emitter's existing prose is preserved verbatim rather than restructured.
ADVISORY_MARKER = "[advisory]"


def emit_advisory(message: str, *, stream: TextIO | None = None) -> None:
    """Emit one advisory line (default stderr); never changes any exit code.

    *message* must identify its own scope — the renderer surfaces the line
    alongside its step name, but the prose has to stand alone when the scope is
    run directly. Prefer ``"<scope>: <finding>"``.
    """
    print(f"{ADVISORY_MARKER} {message}", file=stream if stream is not None else sys.stderr)


def advisory_lines(*captured: str) -> list[str]:
    """Return the advisory lines found in captured command output.

    Accepts several chunks (a step's stdout and stderr) because emitters differ
    on which stream they use. Unmarked lines are dropped.
    """
    return [
        stripped
        for chunk in captured
        for line in chunk.splitlines()
        if (stripped := line.strip()).startswith(ADVISORY_MARKER)
    ]
