---
id: ADR-pool.rulings-as-first-class-events
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.rulings-as-first-class-events: Rulings as First-Class Ledger Events

## Status

Pool

## Intent

**Nothing in gzkit represents the state "settled."** The ledger carries 55
distinct typed event kinds (measured 2026-08-21 via a census of
`.gzkit/ledger.jsonl`; run the census rather than trusting this figure) and
**none** of them is a ruling event. A decision the operator has already made
has no Layer-2 representation, so every surface that needs to know a question
is closed must re-derive that fact from prose — and re-deriving is
re-adjudicating.

This is the diagnosis the active campaign already records at Movement D
(*"Rulings become first-class"*, unchecked). This pool ADR exists to give that
diagnosis a **registered artifact**, because a campaign checkbox is not one:
three open GHIs name Movement D as their destination and none of them can close
`superseded` against a checkbox.

### Evidence — the cost is measured, not asserted

The handoff system is where the absence is paid for. Measured 2026-08-21
(`git log`, `.gzkit/handoffs/`); re-measure rather than citing these numbers:

- Handoff-related repair commits, **excluding** the one-time resume-gate
  dismantling: `2026-05: 3` → `06: 10` → `07: 24` → `08: 30` (month incomplete).
  Monotonic growth; the largest repair sink measured across all mechanisms in a
  180-day window.
- Corpus at time of measurement: 431 documents, ~7.6 MB, authored ~192/month.
- GHI #838 reports *Settled Rulings* occupying ~85% of a handoff document
  **while re-adjudication still happens** — the manual stand-in is both the
  bulk of the artifact and insufficient.

The August commits fall into three families. The third is the compounding one:

| Family | Character | Bounded? |
|---|---|---|
| Resume-gate shell parsing | Gate re-implements a shell parser, patched per construct | Yes — finite grammar |
| Transcribed live counts going stale | Handoffs embed measurements that decay | Yes — the `governance-core.md` illustrative-values rule already names it |
| **Settled-rulings chain integrity** | Inheritance across ancestors, clipped/abridged rulings, chain-head healing, selection ranking | **No — scales with corpus depth** |

Every session authors a handoff, so every later session's inheritance and
selection logic ranks over a larger corpus. Repair rate tracks corpus growth
rather than declining toward a fixed point. A mechanism *can* converge here —
`brief_reconcile` absorbed nine GHIs and did (drift detections 292 → 110 → 4
across Jun/Jul/Aug 2026) — so non-convergence is a property of this design, not
an inevitability.

### The canon this serves

Operator canon (`AGENTS.md`, verbatim) declares synthetic memory vital:

> handoff (synthetic memory refresh, from agent session to agent session, for
> context management). Three vital features, that, as it turns out, are vital
> for campaign success.

> The airlock and the handoff COOPERATE to provide synthetic memory... NEITHER
> ALONE gives an agent a resident model of the project.

**This ADR does not contest that.** It records that the current implementation
does not fulfil it, which under operator doctrine is a **correction**, not an
enhancement: *"discovering that more is needed to fulfil the intent of a feature
is not an enhancement, it is a correction."*

## Decision

Represent rulings as first-class Layer-2 state, so that "settled" is a fact the
ledger carries rather than a paragraph each session re-reads and re-derives.

1. **Typed ledger events** — `ruling_issued` and `ruling_superseded`, joining
   the existing typed-event vocabulary with the same schema discipline
   (`src/gzkit/events.py`, `src/gzkit/ledger_events.py`).
2. **A `ruling` verb** — capture and query, following the capture-must-never-be-
   blocked posture of ADR-0.35.0 Decision 7. Attestation on a ruling is
   **recorded provenance, never a blocking gate**.
3. **The handoff *Settled* section becomes a rendered projection** — a Layer-3
   derived view over ruling events, never hand-authored prose. Per-decision
   operator-ruled/agent-chose attribution renders from the event, not from the
   author's recollection.
4. **The campaign body becomes a rendered Layer-3 view** on the same basis.
5. **Supersession fails closed on orphaned rulings** — a ruling superseding a
   ruling that does not exist is an error, not a silent no-op.

Scope boundary: this ADR governs the *representation* of settled decisions. It
does **not** redesign the handoff document, the airlock, or the transit/exchange
fence, and it must not conflate them — the three-system fence in `AGENTS.md`
binds here (transit = ecosystem, exchange = one block's occupancy, handoff = one
session).

**Explicitly NOT the implementation:** widening `_ruling_key` in
`src/gzkit/handoff_api.py`. That is the locally obvious patch; it makes the
silent-loss direction of GHI #717 and GHI #790 *more* likely, which the
docstring at lines 439-456 deliberately chose against.

## Alternatives Considered

1. **Keep the manual § Rulings Register and fix the chain logic.** Rejected:
   this is what the measured 3 → 10 → 24 → 30 trend already is. Four of the
   August commits are chain-integrity repairs; the family scales with corpus
   depth, so more of the same work does not reach a fixed point.

2. **Widen `_ruling_key` so more rulings match across ancestors.** Rejected on
   the existing docstring's own reasoning (`handoff_api.py:439-456`): a looser
   key trades a visible miss for a silent wrong-match, which is the failure
   direction GHI #717 and GHI #790 record. Cheapest patch, wrong axis.

3. **Retire the Settled Rulings section entirely and re-derive per session.**
   Rejected: re-deriving *is* re-adjudicating — the exact diagnosis Movement D
   records. This removes the cost by removing the capability.

4. **Amend `ADR-0.0.65-handoff-system-consolidation` instead.** Not available by
   construction: `ADR-0.0.65` is `Validated` with 5/5 OBPIs `attested_completed`
   — terminal — and the `foundation` kind is SEALED to new authoring
   (ADR-0.34.0). A terminal foundation ADR cannot absorb new scope.

5. **Reserve a feature semver now (e.g. `ADR-0.39.0`).** Rejected at pool stage:
   ADR-order-is-absolute is operator canon, and `ADR-0.38.0` is a *reserved*
   ID gated behind `0.35.0`/`0.36.0`/`0.37.0` landing — it is not authored on
   disk. Reserving a higher ID ahead of it would break strict order. Pool
   carries no semver, so this ADR creates no ordering obligation; promotion
   (kind and semver) remains an operator decision at `gz adr promote` time.

## Notes

**Routed GHIs.** This pool ADR is the registered destination for:

- GHI #841 — handoff steady-state repair grows with the corpus (class-level cost)
- GHI #838 — Settled Rulings is 85% of the document and re-adjudication happens
- GHI #611 — no general append-only corrective-action primitive

Per `ghi-author` § Doctrine, multiple GHIs may share one destination; each is a
different cut into the same finding.

**Campaign linkage.** Movement D, *"Rulings become first-class"* — this ADR is
the registered artifact that Movement checkbox lacked. Whether Movement D is
promoted to a carrying feature ADR remains an operator decision and is
deliberately not taken here.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
