"""Gate-5 invariants — the never-relax floor for MX mode.

ADR-0.0.74 Decision item #3: the integrity-class guards as a code constant
(not config). The shared checkpoint reads this constant and structurally
cannot resolve a member below CRITICAL, in or out of the hangar.

grader-gaming joins because the observability system is itself a grader and
models game graders increasingly (Opus 4.8 § 6.1.2). A grader-gaming guard
that could go advisory in the hangar would make MX the safe place to vibe
undetected. Its floor membership is made *live* (not merely named) by
OBPI-0.0.74-13's proxy-reality detector per the §5 enforcement-claim rule.
"""

from __future__ import annotations

GATE5_INVARIANTS: frozenset[str] = frozenset(
    {
        "gate5-attestation",  # faked Gate-5 attestation
        "secrets",  # secrets leakage guard
        "operator-pii",  # operator-PII protection
        "ledger",  # ledger integrity (validate_cmd scope)
        "grader-gaming",  # grader-gaming (live detector: OBPI-0.0.74-13)
    }
)
