"""Registry of deprecated `gz` verbs (GHI #705).

Single source for two surfaces that must never disagree:

* the runtime notice a deprecated command prints (`gz gates`);
* `gz validate --deprecated-verb-prescription`, which fails closed when a
  binding rule, skill, or runbook still prescribes one.

Keeping both readers on one registry is the coupled-surface-coherence rule
(AGENTS.md § DO IT RIGHT 1a) applied to deprecation: before this module the
notice lived as a bare string literal in `gates_cmd`, so the CLI could announce
a retirement that no governed surface ever heard about. That gap is exactly what
GHI #705 recorded — `gz gates` announced its own removal while
`.gzkit/rules/governance-core.md` still named it as step 5 of the required
workflow order.

**Scope discipline.** Register a verb here only when the deprecation is
unconditional. `gz attest` is deprecated *during closeout* but remains valid
standalone; registering it would flag every legitimate reference, so it stays
out until the deprecation is total.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["DEPRECATED_VERBS", "DeprecatedVerb", "deprecation_notice", "find_deprecated_verb"]


class DeprecatedVerb(BaseModel):
    """One retired `gz` verb and the invocation that replaces it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    verb: str = Field(..., description="The deprecated verb path, e.g. 'gates'")
    successor: str = Field(..., description="Runnable replacement, e.g. 'gz closeout'")
    ghi: str = Field(..., description="GHI that recorded the prescription ban, e.g. '#705'")


DEPRECATED_VERBS: tuple[DeprecatedVerb, ...] = (
    DeprecatedVerb(verb="gates", successor="gz closeout", ghi="#705"),
)


def find_deprecated_verb(verb: str) -> DeprecatedVerb | None:
    """Return the registry entry for ``verb``, or ``None`` when it is live."""
    return next((entry for entry in DEPRECATED_VERBS if entry.verb == verb), None)


def deprecation_notice(verb: str) -> str:
    """Render the runtime deprecation notice for ``verb``.

    Raises ``KeyError`` when the verb is not registered — a command cannot
    announce a deprecation the registry does not carry, because the validator
    would then never learn to police its prescriptions.
    """
    entry = find_deprecated_verb(verb)
    if entry is None:
        raise KeyError(f"{verb!r} is not a registered deprecated verb")
    return (
        f"⚠ Deprecated: `gz {entry.verb}` will be removed in a future release. "
        f"Use `{entry.successor}` instead."
    )
