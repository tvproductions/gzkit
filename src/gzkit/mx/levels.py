"""GZ_<LEVEL> severity vocabulary for MX mode (ADR-0.0.74 Decision item 11).

STDLIB-FIRST: the ladder reuses Python ``logging``'s numeric constants rather
than re-inventing a kernel/syslog 0–7 ladder (ADR § Alternatives, rejection
(f)). The one rung Python omits — ``NOTICE`` (25) — is the agent-fidelity /
V.I.B.E.S. drift band: visible and recorded, but below the grounding threshold.

Grounding threshold: effective severity ``>= ERROR`` grounds (blocks); WARNING,
NOTICE, INFO, and DEBUG are visible-but-non-grounding. The shared checkpoint
(:mod:`gzkit.mx.checkpoint`, OBPI-0.0.74-02) resolves each guard's effective
``GZ_<LEVEL>`` against this one vocabulary — there is a single leveled severity
authority, not a per-guard ladder (parent ADR § Boundary Invariants #2).
"""

from __future__ import annotations

import logging

# The GZ_<LEVEL> ladder — reuses Python logging's constants (STDLIB-FIRST), so
# the numeric values track the stdlib rather than being hand-typed magic numbers.
CRITICAL = logging.CRITICAL  # 50
ERROR = logging.ERROR  # 40
WARNING = logging.WARNING  # 30
NOTICE = 25  # the rung Python omits — agent-fidelity / V.I.B.E.S. drift band
INFO = logging.INFO  # 20
DEBUG = logging.DEBUG  # 10

# Grounding threshold: effective severity >= ERROR grounds (blocks). Below ERROR
# is visible-but-non-grounding — the drift band lives here.
GROUNDING_THRESHOLD = ERROR


def grounds(level: int) -> bool:
    """Return True iff *level* grounds (blocks) — effective severity >= ERROR.

    WARNING, NOTICE, INFO, and DEBUG are visible-but-non-grounding (return
    False); ERROR and CRITICAL ground (return True).
    """
    return level >= GROUNDING_THRESHOLD
