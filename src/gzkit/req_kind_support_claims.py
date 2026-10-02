"""Enforcement claims for the SUPPORT-REQ proof declaration (GHI #1155, gate GHI #888).

``req_kind_support.parse_support_citation`` once decided a SUPPORT REQ's proof channel by
scanning the whole REQ body for known event names with ``in``: a REQ that DENIED an event
existed ("the ledger carries NO <event>") returned that event as its proof and resolved
green for the very reason it had been amended. It was repaired to read only a declared
witness clause, but no registered claim named the parser, so the repair's green was
unfalsified.

Two claims, on the exemption-half precedent (GHI #797).

* ``support-citation-declared-only`` plants, for each shape of REQ text that mentions a real
  ledger event and a real validator scope without declaring them as its witness (a denial, a
  rejected alternative, a doubled clause, two events, two scopes, a longer token, a scope or an
  event left outside the clause), a REQ the parser must refuse to read as a proof channel.
* ``support-citation-declared-admitted`` is the admit control: a REQ that declares one clause
  is read as exactly that event, scope and path, whatever its body also mentions, so an
  always-refuse parser cannot discharge the first claim alone.
"""

from __future__ import annotations

REFUSE_CLAIM_ID = "support-citation-declared-only"
ADMIT_CLAIM_ID = "support-citation-declared-admitted"
SUPPORT_CITATION_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_SCOPE = "ledger"
_OTHER_SCOPE = "manifest"
_PATH = "src/gzkit/claim_fixture.py"
_REFUSED = "refused as a proof channel"


def _two_events() -> tuple[str, str]:
    """Return two distinct recognized ledger event types, chosen deterministically."""
    from gzkit.req_kind_support import _KNOWN_LEDGER_EVENT_TYPES  # noqa: PLC0415

    first, second, *_ = sorted(_KNOWN_LEDGER_EVENT_TYPES)
    return first, second


def undeclared_shapes() -> dict[str, str]:
    """Return each REQ text that names an event and a scope without declaring a witness.

    Every text mentions a recognized event type, the property that makes it a
    present-but-false input: the substring parser read each of these as a citation.
    """
    a, b = _two_events()
    clause = f"Witnessed by `{a}` + `gz validate --{_SCOPE}`."
    return {
        "denial": (
            f"The ledger carries NO {a} event for these ids, measured 0 of 8. "
            f"Proven instead by the corpus row; gz validate --{_SCOPE} passes."
        ),
        "rejected-alternative": f"Rejected: proof by {a}. Use gz validate --{_SCOPE} only.",
        "doubled-clause": f"{clause} {clause}",
        "two-events": f"Witnessed by `{a}` and `{b}` + `gz validate --{_SCOPE}`.",
        "two-scopes": (
            f"Witnessed by `{a}` + `gz validate --{_SCOPE}` and `gz validate --{_OTHER_SCOPE}`."
        ),
        "longer-token": f"Witnessed by `{a}_variant` + `gz validate --{_SCOPE}`.",
        "scope-outside-clause": f"gz validate --{_SCOPE} passes. Witnessed by `{a}`.",
        "event-outside-clause": f"`{a}` is emitted. Witnessed by `gz validate --{_SCOPE}`.",
    }


def undeclared_shape_population() -> list[str]:
    """Return every shape of undeclared REQ text the parser must refuse."""
    return list(undeclared_shapes())


def _build_shape(member: str | None = None) -> str | None:
    """Name the REQ-text shape to plant; ``None`` plants the declared REQ."""
    return member


def declared_req() -> tuple[str, str]:
    """Return a REQ that declares one witness clause and the event it declares.

    The body names a second event outside the clause, which must not reach the channel.
    """
    a, b = _two_events()
    text = (
        f"The artifact exists; {b} is unrelated commentary. "
        f"Witnessed by `{a}` citing `{_PATH}` + `gz validate --{_SCOPE}`."
    )
    return text, a


# Each entrypoint imports the parser itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _ep_undeclared_refused(shape: str) -> list[str]:
    """Return a finding naming *shape* when the parser refuses it as a proof channel."""
    from gzkit.req_kind_support import parse_support_citation  # noqa: PLC0415

    citation = parse_support_citation(undeclared_shapes()[shape])
    return [f"{shape}: {_REFUSED}"] if citation is None else []


def _ep_declared_admitted(_shape: str | None) -> int:
    """Truthy only when the declared REQ is read as exactly its declared channel."""
    from gzkit.req_kind_support import parse_support_citation  # noqa: PLC0415

    text, event = declared_req()
    citation = parse_support_citation(text)
    declared = (
        citation is not None
        and citation.event_types == [event]
        and citation.scope == _SCOPE
        and citation.artifact_path == _PATH
    )
    return 1 if declared else 0


class _SupportCitationMarker:
    """Inert carrier for the SUPPORT-citation ``@enforces`` registrations."""


def ensure_support_citation_claims_registered() -> None:
    """(Re)register the SUPPORT-citation claims (idempotent, reset-safe).

    MUST stay wired into ``enforcement._ensure_production_claims_registered``: a
    registration authored but un-wired there is an ORPHAN whose floor membership is a
    facade.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        POPULATION_NONE,
        enforces,
        extend_known_claims,
        get_enforcement_registry,
    )

    extend_known_claims(SUPPORT_CITATION_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_shape,
            _ep_undeclared_refused,
            expect=_REFUSED,
            exempts=ADMIT_CLAIM_ID,
            population=undeclared_shape_population,
        )(_SupportCitationMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_shape,
            _ep_declared_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_SupportCitationMarker)
