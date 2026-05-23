"""gzkit.foundation — in-flight foundation ADR discovery and triage.

Composer surface for the gz-foundation-triage on-demand skill. Provides
read-only helpers that gather Draft/Proposed foundation ADRs and count
their governance signals (insights references, GHI mentions, invariant
references). The skill body wields these helpers via its bundled script;
external callers should treat the helpers as a diagnosis-only surface.

Rubric scoring lives in `src/gzkit/foundation/rubric.py` (the
foundation-triage-rubric OBPI's surface) and is not implemented here.
"""

from gzkit.foundation.triage import (
    count_signals,
    gather_in_flight_foundations,
    run_foundation_triage,
)

__all__ = [
    "count_signals",
    "gather_in_flight_foundations",
    "run_foundation_triage",
]
