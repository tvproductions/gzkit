"""STRUCTURAL-FENCE channel proof resolver (ADR-0.0.69-channels-first-closeout-proof).

Extracted from ``req_kind.py`` (GHI #652 module-size split). Owns the
STRUCTURAL-FENCE proof channel (`PARENT_ADR_INVARIANT`): resolving whether a
`[structural-fence]` REQ is proven, either via a parent-ADR ``## Boundary
Invariants`` anchor (state-property fences) or a registered ``@enforces`` claim
(enforcement-asserting fences). Behaviour-preserving move — no logic changed.

The sibling ``req_kind_support`` owns the SUPPORT channel; ``req_kind`` retains
the taxonomy models and the three-channel enrichment orchestrator that calls
both resolvers.
"""

from __future__ import annotations

import re
from pathlib import Path

# Regex to parse the ADR semver from a REQ id (e.g. "REQ-0.0.69-02-04" → "0.0.69").
_REQ_SEMVER_RE: re.Pattern[str] = re.compile(r"REQ-(\d+\.\d+\.\d+)-")

# Regex to parse semver + OBPI index from a REQ id
# (e.g. "REQ-0.0.69-02-04" → ("0.0.69", "02")).
_REQ_SEMVER_OBPI_RE: re.Pattern[str] = re.compile(r"REQ-(\d+\.\d+\.\d+)-(\d+)-\d+")

# Heading that marks the STRUCTURAL-FENCE proof anchor in a parent ADR.
_BOUNDARY_INVARIANTS_HEADING: str = "## Boundary Invariants"


def _boundary_invariants_section(content: str) -> str | None:
    """Return the ``## Boundary Invariants`` section body, or None when absent.

    Spans from the heading to the next H2 (``## ``) or end-of-file.
    """
    m = re.search(
        r"^##\s+Boundary Invariants\b(.*?)(?=^##\s|\Z)",
        content,
        re.DOTALL | re.MULTILINE,
    )
    return m.group(1) if m else None


def _fence_obpi_anchored(section: str, req_id: str) -> bool:
    """Return True when the Boundary Invariants ``section`` anchors ``req_id``'s OBPI.

    Per ``docs/governance/req-scope-discipline.md`` § STRUCTURAL-FENCE (GHI #538)
    a state-property fence's proof is an invariant naming the OBPI combination
    whose completion satisfies it. The canonical anchor is the OBPI-combination
    token ``(OBPI-NN[, OBPI-MM, …])``; the ADR-0.0.71 per-REQ token
    (``REQ-X.Y.Z-NN-MM …``) is an accepted stricter form. Heading presence alone
    is NOT proof — an invariant list naming no OBPI cannot say which invariant
    proves which fence.
    """
    m = _REQ_SEMVER_OBPI_RE.match(req_id)
    if m is None:
        return False
    semver, obpi = m.group(1), m.group(2)
    obpi_int = int(obpi)
    obpi_prefix = f"REQ-{semver}-{obpi}"
    patterns = (
        rf"OBPI-0*{obpi_int}\b",  # short form: (OBPI-04) / (OBPI-4)
        rf"OBPI-{re.escape(semver)}-{obpi}\b",  # full form: (OBPI-0.32.0-04)
    )
    if any(re.search(p, section) for p in patterns):
        return True
    # Stricter per-REQ token (ADR-0.0.71 form): the exact REQ id or its OBPI prefix.
    return req_id in section or obpi_prefix in section


# Keywords that mark a [structural-fence] REQ as enforcement-asserting.
# An enforcement-asserting fence requires a live @enforces NC in the registry
# (not merely a ## Boundary Invariants anchor) to resolve to "pass".
_ENFORCEMENT_FENCE_KEYWORDS: tuple[str, ...] = (
    "@enforces",
    "enforcement",
    "fail-closes",
    "live nc",
    "live negative control",
    "_negative_control_debt",
)


def _is_enforcement_asserting(req_text: str) -> bool:
    """Return True if the REQ text asserts enforcement rather than a state-property."""
    lower = req_text.lower()
    return any(kw in lower for kw in _ENFORCEMENT_FENCE_KEYWORDS)


# Backtick-delimited tokens in a REQ text are the claim-id candidates. An
# enforcement-asserting fence names its claim as a backticked slug (e.g.
# ``grader-gaming``); matching only backticked tokens against the registered
# claim set avoids false-positives on short common words ("test", "lint") that
# would appear in arbitrary prose.
_BACKTICK_TOKEN_RE: re.Pattern[str] = re.compile(r"`([^`]+)`")


def _enforcement_claim_registered(req_text: str) -> bool:
    """Return True if req_text names a registered ``@enforces`` claim.

    Binds the fence to *its* claim (REQ-18-01 "for that claim"): a backtick-
    delimited token in the REQ text must exactly match a registered claim id.
    Production claims are registered first via the canonical idempotent
    entrypoint so the result does not depend on import order — a fence whose
    claim genuinely exists never spuriously resolves unproven because some
    registering module had not yet been imported.

    A meta-property fence that names no single claim (e.g. "the registry has no
    `_NEGATIVE_CONTROL_DEBT` escape") matches nothing and returns False — those
    are not per-claim bindable and prove via the OBPI-19 floor at ADR closeout,
    not here.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        _ensure_production_claims_registered,
        registered_claims,
    )

    _ensure_production_claims_registered()
    registered = set(registered_claims())
    tokens = {token.strip() for token in _BACKTICK_TOKEN_RE.findall(req_text)}
    return bool(tokens & registered)


# A backtick token shaped like an enforcement claim id: a hyphenated lowercase
# slug (e.g. ``grader-gaming``, ``gate5-ledger``). A fence naming such a token
# asserts a SINGLE claim and keeps the OBPI-18 teeth (the named claim must be
# registered to resolve "pass"); a fence naming none is a meta-property fence.
# Authority for the claim-id shape is ``enforcement._CLAIM_ID_RE``; this is the
# hyphenated subset used to tell a real claim slug from enforcement prose.
_CLAIM_CANDIDATE_RE: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$")


def _names_claim_candidate(req_text: str) -> bool:
    """Return True if req_text backticks a token shaped like a single claim id.

    Enforcement-vocabulary keywords that happen to be hyphenated slugs
    (``fail-closes``) are excluded — they are the enforcement trigger, not a claim.
    """
    keywords = {kw.lower() for kw in _ENFORCEMENT_FENCE_KEYWORDS}
    tokens = {token.strip() for token in _BACKTICK_TOKEN_RE.findall(req_text)}
    return any(_CLAIM_CANDIDATE_RE.match(t) and t.lower() not in keywords for t in tokens)


def is_meta_property_enforcement_fence(req_text: str) -> bool:
    """Return True for an enforcement-asserting fence that names no single claim.

    A meta-property fence asserts a property of the enforcement *system* itself
    (e.g. "the registry has no `_NEGATIVE_CONTROL_DEBT` escape", "one
    enforcement-claim surface, not two") rather than the liveness of one named
    guard. Per ``_enforcement_claim_registered``'s contract these are not
    per-claim bindable; they prove via the OBPI-19 enforcement floor at ADR
    closeout, not via a named ``@enforces`` claim. The closeout-proof consumer
    (``trust_audits.closeout_proof``) defers them to the floor — proven iff the
    floor is green — while a single-claim fence keeps the OBPI-18 teeth.

    ``resolve_fence_proof`` deliberately still returns ``"unproven-fence"`` for
    these (the attested REQ-0.0.74-18-01 behavior, "prove via the floor ... not
    via this resolver"); the deferral lives in the consumer, not the resolver.
    """
    return _is_enforcement_asserting(req_text) and not _names_claim_candidate(req_text)


def _find_parent_adr_file(semver: str, project_root: Path) -> Path | None:
    """Find the parent ADR file for a given semver under project_root."""
    adr_root = project_root / "docs" / "design" / "adr"
    for adr_file in adr_root.rglob(f"ADR-{semver}-*.md"):
        # The ADR file lives directly inside a package dir named ADR-{semver}-*.
        if adr_file.parent.name.startswith(f"ADR-{semver}-"):
            return adr_file
    return None


def resolve_fence_proof(req_id: str, project_root: Path, req_text: str = "") -> str:
    """Resolve STRUCTURAL-FENCE proof status.

    For enforcement-asserting fences (REQ text declares something is enforced,
    validated, fail-closed, or gated) — resolves to ``"pass"`` only when the
    fence's own ``@enforces`` claim (named as a backticked slug in the REQ text)
    is registered; ``"unproven-fence"`` when the claim is absent or unnamed.

    For state-property fences (non-enforcement) — resolves via parent-ADR
    ``## Boundary Invariants`` anchor, unchanged from prior behavior.

    Returns one of:
    - ``"pass"`` — proof resolved (the fence's named claim is registered, or the
      anchor is present for a state-property fence).
    - ``"unproven-fence"`` — proof absent (the fence's claim is unregistered or
      unnamed for an enforcement fence, anchor absent for a state-property fence,
      or req_id unparseable).
    """
    m = _REQ_SEMVER_RE.match(req_id)
    if m is None:
        return "unproven-fence"
    semver = m.group(1)

    if _is_enforcement_asserting(req_text):
        return "pass" if _enforcement_claim_registered(req_text) else "unproven-fence"

    adr_path = _find_parent_adr_file(semver, project_root)
    if adr_path is None:
        return "unproven-fence"
    section = _boundary_invariants_section(adr_path.read_text(encoding="utf-8"))
    if section is None:
        return "unproven-fence"
    return "pass" if _fence_obpi_anchored(section, req_id) else "unproven-fence"
