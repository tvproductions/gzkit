---
id: ADR-pool.render-order-truncation-survival
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.render-order-truncation-survival: Render-Order Permutation for Truncation Survival

## Status

Pool

## Intent

Order `AGENTS.md` sections so that everything the operator has declared
must-survive renders **before** the consuming vendor's project-doc byte cap.

This is the **reorder half** of GHI #580, split by operator ruling
2026-07-25. The **witness half** landed under GHI #712 and is closed:
`src/gzkit/governance/trust_audits/surface_delivery_witness.py` plus the
declaration at `data/agents_md_survival_declaration.json`, wired through
`gz validate --instructions-files-budget` into the default `gz check`
pipeline (`src/gzkit/commands/quality.py:451`). The condition is therefore
already **observable and fail-closed**; what remains unbuilt is the act of
**permuting the surface**.

Measured warrant (do not re-derive):

```
AGENTS.md = 32,208 bytes; Codex project_doc_max_bytes default 32,768; headroom 560 bytes

   20525  Attestation
   22044  Defect-fix routing
   25210  Operator Doctrine (verbatim canon)
   29273  Governance doctrine surfaces
   31613  Architectural Boundaries      <- last 595 bytes
```

Past 32,768 bytes the tail is **not delivered at all** under Codex
(openai/codex#7138) — silently. `Operator Doctrine (verbatim canon)` holds
10 of the corpus's 50 `tier: invariant` entries, including *"MY WORD IS
AUTHORITY IN ALL CASES"*. An invariant-tier entry that is not delivered is
not an invariant.

Ratified survival declaration (operator, 2026-07-25): must-survive =
**ranks 1–11**, `operator-doctrine-verbatim-canon` first and
`architectural-boundaries` last, cumulative **21,582 B**, leaving
**11,186 B** of growth headroom. Ranks 12–20 are declared
**expendable-under-pressure because they are recoverable, not because they
are unimportant.** Ratified **as data only** — applying the order to
committed `AGENTS.md` remains a Layer-1 canon change requiring Gate-5
attestation.

## Decision

Deferred to post-1.0. Parked here rather than folded into an active ADR
because only this half is expensive, and it pays off **only once the cap
binds** — the GHI #712 witness makes the binding condition observable in
the meantime, so the permutation can wait without the risk going unwatched.

Three constraints are already measured and bind any future implementation.
They are recorded here so promotion does not re-litigate them:

1. **Do NOT repurpose `Pillar.order` as a criticality field.** It carries
   **document order** for round-trip fidelity (`markdown_parser.py:287`,
   *"in document order"*), and `gz validate --invariant-coherence` — in the
   default `gz check` scope — byte-compares deterministic rendition playback
   against the committed surface. A render-order policy therefore needs a
   **second axis** (a render-time reorder distinct from capture order), or
   the recomposed surface and its rendition must be committed together.
2. **Applying any ordering to committed `AGENTS.md` is a Layer-1 canon
   change** requiring operator Gate-5 attestation through the recompose
   ceremony. An agent silently reordering the canon it is governed by is
   the failure gzkit exists to prevent.
3. **The mechanism itself is cheap and already prototyped.** The ~60-line
   implementation from 2026-07-24 is reusable as-is — stable sort, `order`
   renumbered to match (the field means *"Render order (ascending)"*),
   permutation-safe, verbatim `lines` preserved. Only the **ranking source**
   changes: from inferred criticality to the ratified survival declaration.

Out of scope, with owners:

| Concern | Owner |
|---|---|
| Shrinking the surface (the **cure**; this ADR is a mitigation) | GHI #533 → `ADR-0.35.0` decrease-only ratchet |
| Detecting the truncation condition | GHI #712 (**landed**) |
| Re-anchoring the budget unit off char count | GHI #579 |
| Duplicating critical content at both boundaries | **Foreclosed** — 560 B of headroom cannot carry a second copy of anything |

## Alternatives Considered

1. **Fold into `ADR-0.35.0-canon-entry-corpus-landing` as a tenth OBPI.**
   Rejected: that ADR's § Intent scopes the corpus→candidate generator and
   `gz content land`, **not** render-order policy. Asserting it absorbs this
   scope without an operator ruling would be inventing a destination.
2. **Author a separate feature ADR pre-1.0.** Rejected: it adds an ADR to
   the pre-1.0 board that campaign Movement C is trying to reduce, and buys
   nothing until the cap actually binds.
3. **Rank by criticality inferred from `Bullet.classification` / `Bullet.witness`.**
   Built, measured, and **refuted** 2026-07-24. Run against live `AGENTS.md`
   it pushed § Attestation 15→18 and § Defect-fix routing 16→19 — the two
   sections GHI #580 was filed to lift — and demoted `PRIME DIRECTIVE` 3→9,
   which the original filing records as *"well-placed"*. Root cause:
   `classification` and `witness` are `Bullet` fields, and gzkit's most
   binding material (§ Attestation's canonical-invocations table,
   § Defect-fix routing's threshold table) is **tables, not bullets**, so it
   ranks 0. Corpus-layer measurement agrees no existing field can serve:
   `witness` 0/52 populated · `tier` 50/52 `invariant` (does not
   discriminate) · `classification` 36/52 `Ambiguous` · section coverage
   8/20.
4. **Keep periphery bias as the warrant.** Replaced. It rests on a single
   blog post's attention claim, with no measurement in gzkit and no possible
   mechanical witness. Truncation is measured, vendor-documented, and
   **gateable** — which is what made the witness half buildable at all.

## Notes

Routed from **GHI #580** (closed `superseded` against this ADR). The
original filing's periphery-bias measurements are preserved in that issue as
load-bearing history — the refutation in Alternative 3 is why the warrant
changed, not error to be erased.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
