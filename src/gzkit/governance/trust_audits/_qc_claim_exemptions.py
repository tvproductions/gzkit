"""Per-claim ``exempts`` declarations for the qc negative-control claims (GHI #797).

Split out of ``_qc_negative_controls`` when the drain pass pushed that module over
the ``radon_raw_nloc`` block band. The split is by COHESION, not to go green: a
claim's registration (fixture + production entrypoint) and the judgment about
whether its gate has an exemption surface are different questions with different
evidence. The registration table is mechanical — it wires a control to a gate. This
map is an authoring judgment about what a gate *admits*, and it carries the bar
that judgment was made against. Grandfathering the oversize module instead would
have been the laundering ADR-0.0.73 Boundary Invariant #8 forbids, which is the
same doctrine this map exists to serve.

**The bar.** A claim is declared ``EXEMPTS_NONE`` only when no input makes its gate
ADMIT an item it has judged in violation. These are exemptions:

* a waiver / grandfather table (``data/*_waivers.json``, ``data/*_grandfather*.json``)
* an ``excluded`` / allowlist entry
* an escape marker or skip token in the scanned content
* an opt-in arm that is off by default, or an opt-out config that disables the check
* an authorization booking (the ``handoff-resume-*`` shape)

These are NOT: scope predicates (which artifacts the gate examines), threshold
parameters (a budget defines what a violation *is*), artifact-absent returns
(nothing to compare), and error-path returns.

**Membership is a reading, never a scan.** Two heuristics have already failed this
exact question — a naming-convention scan over ``source_file`` matched 0 of 70, and
correlating claim ids against module stems matched 7 of 71 (see
``_derive_gate_targets``). A wrong entry here is worse than an absent one: it
launders an unexercised admit path into "nothing is owed". A gate WITH an exemption
is deliberately absent and stays on the disclosed list in
``data/exemption_control_grandfather.json`` until a control exercises its admit path.

Per-claim admit paths already located, and the claims not yet reached, are recorded
in ``docs/governance/exemption-control-triage.md`` so the next drain pass starts
from a reading rather than re-deriving one.
"""

from __future__ import annotations

from gzkit.enforcement import EXEMPTS_NONE

#: ``{claim_id: exempts}`` for every claim whose gate was read end-to-end and found
#: to carry no admit path. Consumed by ``register_qc_negative_controls``; a claim
#: absent from this map registers with ``exempts=None`` (UNDECLARED) and is
#: disclosed by ``gz validate --exemption-controls``.
QC_CLAIM_EXEMPTS: dict[str, str] = {
    # Diffs on-disk ADR canon against the derived index; every drift entry is a
    # finding and nothing suppresses one.
    "adr-status-freshness": EXEMPTS_NONE,
    # Char budget per file. Project-overridable, but a threshold defines what a
    # violation IS — it never admits one it has found.
    "instructions-files-budget": EXEMPTS_NONE,
    # Byte-compares rendition playback against committed AGENTS.md. The only
    # non-finding return is "no committed rendition exists" — nothing to compare.
    "invariant-coherence": EXEMPTS_NONE,
    # Requires a substantive `## Why foundation tier?` on every foundation ADR.
    # The sidecar filter selects WHICH files are ADRs; it admits no failing ADR.
    "kind-invariance": EXEMPTS_NONE,
    # Two arms, both fail-closed: `.gitattributes` must carry the LF directive,
    # and no tracked text surface may be committed CRLF. No per-file waiver.
    "line-endings": EXEMPTS_NONE,
    # Asserts the SessionStart orientation hook stays wired in both harnesses.
    # Every arm yields a finding; a missing script is an error, not a pass.
    "orientation-freshness": EXEMPTS_NONE,
    # Per-surface mechanism arms of the ratchet. The umbrella `waiver-ratchet`
    # claim and its silent-bypass arm DO carry an exemption (the registry's
    # `excluded` list), which is why only these two appear here — `excluded` is
    # consulted solely by the unregistered-file scan, never by these checks.
    "waiver-ratchet-closed-set-lock": EXEMPTS_NONE,
    "waiver-ratchet-dated-cutover": EXEMPTS_NONE,
}
