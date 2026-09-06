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

**The severity line, sharpened by the Tier-B pass (2026-08-14).** Eight of the
seventeen gates read in that pass turned on a distinction the five bullets above
do not settle on their own: a gate that FINDS something and does not exit
non-zero on it. The line that separates the two cases is WHO CONTROLS THE
ADMISSION.

* A finding the gate classifies as advisory/non-blocking by a **fixed code
  property** — a separate finding type, a ``required: False`` in an in-code check
  table, a question that declares no validator — is OUTSIDE the judged set. The
  gate never claimed to enforce it, so there is nothing to admit.
* A finding the gate WOULD fail on, admitted by a **project-controllable input**
  — a flag whose default is off, a manifest entry, a config value, a data file,
  a marker, a ledger booking — is an exemption, however well justified.

That line is what separates ``readiness-audit`` (in-code ``required`` bits plus a
score threshold, declared ``'none'`` below) from ``skill-audit`` (identical
blocking/non-blocking split, but gated on ``--strict``, which is off by default —
disclosed, control owed). Justification is irrelevant to membership: the
``enforcement-floor`` exclusion is deliberate and ADR-backed and is STILL an
exemption, because the disclosed list is an inventory, not an accusation.

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
    "corpus-retirement-witness": EXEMPTS_NONE,
    # AST-scans producers for payload keys neither ledger contract declares. No
    # waiver table, allowlist, escape marker or opt-in flag: every undeclared key
    # it finds is a finding. Its static-analysis scope (literal keys only) limits
    # what it CAN see and is disclosed in the audit docstring — a scope predicate,
    # not an exemption, and the committed-row parity fence covers the other side.
    "producer-field-parity": EXEMPTS_NONE,
    # Scans wheel-shipped Markdown for environment-rooted path literals. Nothing
    # project-controllable admits a literal it has judged in violation: there is no
    # waiver table, allowlist, escape marker or opt-in flag. The roots it does NOT
    # flag (~/, $HOME/, /tmp, /usr, /var, /private) are a fixed code property that
    # defines what a violation IS -- the threshold case the bar above excludes --
    # and the .md-only walk is a scope predicate, also excluded. GHI #900.
    "wheel-path-literals": EXEMPTS_NONE,
    # Requires a substantive `## Why foundation tier?` on every foundation ADR.
    # The sidecar filter selects WHICH files are ADRs; it admits no failing ADR.
    "kind-invariance": EXEMPTS_NONE,
    # Two arms, both fail-closed: `.gitattributes` must carry the LF directive,
    # and no tracked text surface may be committed CRLF. No per-file waiver.
    "line-endings": EXEMPTS_NONE,
    # Asserts the SessionStart orientation hook stays wired in both harnesses.
    # Every arm yields a finding; a missing script is an error, not a pass.
    "orientation-freshness": EXEMPTS_NONE,
    # Compares every interpreter declaration under `.github/workflows/**`
    # against `.python-version`. Read end-to-end: there is no allowlist, no
    # waiver file, and no per-site suppression. The only empty returns are
    # "everything agrees" and "nothing is declared anywhere" — neither admits
    # a mismatch it has found. The `requires-python` floor is read but never
    # compared for equality, which is a scope decision, not an admit path.
    "python-version-pins": EXEMPTS_NONE,
    # Per-surface mechanism arms of the ratchet. The umbrella `waiver-ratchet`
    # claim and its silent-bypass arm DO carry an exemption (the registry's
    # `excluded` list), which is why only these two appear here — `excluded` is
    # consulted solely by the unregistered-file scan, never by these checks.
    "waiver-ratchet-closed-set-lock": EXEMPTS_NONE,
    "waiver-ratchet-dated-cutover": EXEMPTS_NONE,
    # Companion gate to `waiver-ratchet` (GHI #929). Unlike that umbrella claim it
    # carries NO exemption surface at all: `data/config_registry.json` has no
    # `excluded` list, so every top-level `data/*.json` must be owned by it or by
    # the waiver registry. The two are exhaustive by construction, and an escape
    # hatch here would reopen exactly the unowned-config hole the gate closes.
    "config-registry": EXEMPTS_NONE,
    # --- Tier-B pass, 2026-08-14 (GHI #797) --------------------------------
    # Criteria (a)-(d) over the AGENTS.md template and rendered file. Table rows
    # and fenced blocks are excluded from paragraph counting because neither IS a
    # paragraph (scope), and the budget overlay is a threshold. The prohibited-title
    # match is case-insensitive precisely so authoring case is not an escape. The
    # `_advisory` finding type is a SEPARATE heuristic ADR-0.0.54 reserves from hard
    # rejection, not a downgrade of criteria a/b/c/d.
    "agents-md-map-conformance": EXEMPTS_NONE,
    # Schema/shape conformance over ledger lines. An unreadable line, a non-object
    # entry, and an UNKNOWN EVENT TYPE are each findings — the three shapes that
    # would otherwise be the skip. A missing ledger and a missing schema are findings
    # too, which is stronger than the artifact-absent carve-out requires. Gate 5 is
    # never demoted by the MX marker (mx-mode.md § Honor the marker).
    "gate5-ledger": EXEMPTS_NONE,
    # `_requires_human_obpi_attestation` returns True unconditionally — ADR-0.0.36
    # collapsed the kind/lane/sensitivity branching, so there is no arm to take.
    # `_validate_obpi_human_attestation_fields` fails closed on a placeholder
    # attestor, a non-true human_attestation, empty text, and a malformed date.
    "gate5-attestation-absence": EXEMPTS_NONE,
    # Counts `obpi_completion_repudiated` events whose cause is model-induced
    # fabrication. A detector that reports every match, not a gate that judges then
    # admits: the cause filter selects which events ARE the signal.
    "grader-gaming": EXEMPTS_NONE,
    # Asserts one frontmatter marker on one pool ADR. Both arms return exit 3 — a
    # MISSING pool ADR is a finding, not a skip, so even the artifact-absent path
    # fails closed.
    "dispatch-absorption-marker": EXEMPTS_NONE,
    # Scans for stale pipeline markers, orphan receipts, and expired locks. An
    # unreadable receipt is reported as an orphan and an unreadable lock as expired,
    # so the error paths accuse rather than excuse. `--apply` cleans up; it never
    # suppresses.
    "preflight": EXEMPTS_NONE,
    # Scores four disciplines against an IN-CODE check table and exits non-zero on
    # any required failure or a sub-2.0 overall score. The `required` bit is a fixed
    # property of each check definition and the floor is a threshold — neither is
    # project-settable, and every failure is reported in `issues` regardless. Contrast
    # `skill-audit`, whose identical split is gated on an off-by-default `--strict`.
    "readiness-audit": EXEMPTS_NONE,
    # Grammar + completeness over committed pool interview records. A record the
    # audit CANNOT READ is a finding by explicit design (the GHI #736 correction).
    # `question.required` and the per-question validator set are fixed in
    # ADR_QUESTIONS, the single authority the CLI loader also reads.
    "pool-interview-schema": EXEMPTS_NONE,
}
