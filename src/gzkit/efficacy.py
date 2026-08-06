"""Efficacy channel — measure whether a capability actually reaches its input.

gzkit had two kinds of check and was missing a third. Validators ask *does it
exist*; unit tests ask *is it correct on constructed inputs*. Neither asks *is
this capability reading the store it was built to read*, so a surface can be
present, correct, and inert at the same time — and pass every gate.

`OBPI-0.25.0-33` is the worked example. It shipped ARB and reached
``attested_completed`` on five acceptance criteria, three of which assert facts
about the brief's own prose, one of which asserts the package is *present*, and
one of which asserts six scenarios exist. Its Key Proof cites
``Receipts scanned: 0`` as a passing result. Every criterion still holds today
while ``gz arb advise`` reads 130 of 3,286 receipts, because no criterion was
ever about reaching the input.

A :class:`StoreCoverage` is the missing number, reported at the point of use so
the gap is visible when the capability runs rather than in a triage months
later. It deliberately carries the *denominator*: ``covered`` alone reads as
success, and it was ``scanned_receipts`` — a numerator with no denominator —
that let ARB look busy while skipping 96% of its store.

Domain core: stdlib + Pydantic only. Nothing here knows what a receipt is.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StoreCoverage(BaseModel):
    """What a consumer reached, against what was there to reach.

    Every field answers a question a presence check cannot:

    ``present``     what is in the store at all
    ``eligible``    what this consumer is *able* to read (its schema, its kind)
    ``covered``     what it actually read on this run
    ``truncated``   whether a limit cut the eligible set short
    ``unreadable``  what it structurally cannot read, by kind and count
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    store: str = Field(..., description="the store this consumer read, as a path or name")
    present: int = Field(..., ge=0, description="items in the store")
    eligible: int = Field(..., ge=0, description="items this consumer is able to read")
    covered: int = Field(..., ge=0, description="items actually read this run")
    truncated: bool = Field(
        default=False,
        description="a limit stopped the run before the eligible set was exhausted",
    )
    unreadable: list[tuple[str, int]] = Field(
        default_factory=list,
        description="kinds this consumer structurally skips, as (kind, count) descending",
    )

    @property
    def reach(self) -> float:
        """Fraction of the store this run actually read (0.0 when the store is empty).

        This is the efficacy number. It is deliberately ``covered / present`` and
        not ``covered / eligible``: a consumer that declares most of its store
        ineligible has not thereby succeeded, it has narrowed its own denominator.
        Measuring against ``eligible`` would have reported ARB at 100%.
        """
        return self.covered / self.present if self.present else 0.0

    @property
    def exhaustive(self) -> bool:
        """True when this run read everything it was able to read.

        A downstream retention or promotion decision needs this, not ``covered``:
        a truncated run says nothing about the items it never looked at.
        """
        return not self.truncated and self.covered >= self.eligible

    def render(self) -> str:
        """One-line human summary, denominator first so reach cannot be read alone."""
        pct = f"{self.reach * 100:.0f}%"
        line = f"coverage: read {self.covered} of {self.present} items in {self.store} ({pct})"
        if self.truncated:
            line += " — TRUNCATED by limit"
        if self.unreadable:
            skipped = ", ".join(f"{kind} x{count}" for kind, count in self.unreadable)
            line += f"; not readable by this consumer: {skipped}"
        return line


__all__ = ["StoreCoverage"]
