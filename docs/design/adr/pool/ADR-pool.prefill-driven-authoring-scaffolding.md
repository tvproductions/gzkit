---
id: ADR-pool.prefill-driven-authoring-scaffolding
status: Pool
lane: heavy
parent:
---

# ADR-0.45.0-prefill-driven-authoring-scaffolding: Prefill-Driven Authoring Scaffolding

## Persona

`main-session` + `implementer`. Heavy-lane runtime contract change to the
authoring surfaces. Atomic edits, complete units; the prefill is the
section opener only, never the section content.

## Intent

Apply the prompt-engineering "prefill" technique — start the model's
response with structured tokens to lock output shape — to gzkit's two
agent-authored artifact surfaces: OBPI brief authoring and attestation
text composition. Today both surfaces hand the agent a free-form template
with `{intent}`/`{decision}` placeholders. The agent reads the placeholder,
re-authors from scratch, and routinely fabricates section names not in
the canonical structure (e.g., "Goals", "Stretch Goals", "Open Questions"
at the brief layer; em-dash-omitting attestation text at the attestation
layer).

The existing post-hoc validators (`gz validate --documents`,
`gz validate --brief-headings`, the attestation-receipt-binding gate
landing under ADR-0.0.24) catch the drift after authoring. Prefill is
the prevention layer — locks structure before authoring begins, removing
one whole class of authoring failure mechanically rather than via
post-hoc rejection.

External evidence: Anthropic Prompt Engineering 101 (Hannah Moran +
Christian Ryan, 2026) demonstrates the technique on JSON / XML output
shaping; same technique applies one layer up to authoring scaffolding.
Failure-mode shape: `Fabrication` (per ADR-0.0.23 taxonomy) — agents
fabricating section names that look plausible but are not in the
canonical structure.

## Decision

1. **OBPI brief prefill.** When `gz obpi specify` (or its skill
   equivalent until the CLI verb ships) hands the agent a brief skeleton,
   the skeleton includes the literal opening lines of each canonical
   section, not placeholder tokens:
   - `## ADR Item\n- **Source ADR:** ` (concrete path filled by the
     command, agent fills the checklist-item quote)
   - `## Objective\n\n` (agent fills one sentence)
   - `## Lane\n\n**<Heavy|Lite>** — ` (concrete lane filled by the
     command from parent ADR, agent fills rationale)
   - `## Allowed Paths\n\n- `, `## Denied Paths\n\n- `,
     `## Requirements (FAIL-CLOSED)\n\n1. REQUIREMENT: `,
     `## Discovery Checklist\n\n` (with the parent-ADR-Decision item
     pinned at position #1 per GHI to be filed under ADR-0.0.23)
2. **Attestation text prefill.** When `gz obpi complete` is invoked
   without `--attestation-text`, the command opens an `$EDITOR` session
   with a prefilled scaffold:
   - The user's verbatim invocation token at the start
   - The canonical em-dash separator (` — `)
   - A receipt-citation slot template (`Receipts: lint <ID>; types <ID>;
     tests <ID>; coverage <ID>.`)
   - The agent fills the concrete characterization between the em-dash
     and the receipt slot.
3. **Depth discipline.** Prefill is the *section opener only*, not the
   section content. The talk's example (single open token like `<itinerary>`)
   is the right depth — pre-write enough to lock structure, not enough
   to bias content. A prefill that includes example content for the
   agent to fill around violates this and is rejected at design review.
4. **Mechanical check.** A new `gz validate --prefill-conformance` scope
   validates that authored briefs and attestation texts include the
   canonical opening lines exactly (no agent-paraphrased section names).
   Drift exits 3.

## Comparator Uplift (2026-05-07)

Spec Kit and Kiro win the blank-page moment by turning intent into scaffolded
specs and tasks. This ADR should absorb that at the authoring boundary:
prefills should include witness slots for source prompt hash, assumption labels,
delta markers, and expected receipts while leaving substantive content for the
agent/operator loop.

## Consequences

### Positive

- Closes the section-name fabrication class at the authoring surface,
  not after the fact. Existing post-hoc validators become a backup
  rather than the primary defense.
- Pairs with ADR-0.0.24 (attestation receipt binding) — the prefill
  scaffolds the canonical receipt-citation slot, making the binding
  gate's fail-closed exit less likely to fire on well-intentioned
  authoring.
- Pairs with ADR-0.0.26 (evaluation-feedback-loop doctrine) — the
  feedback chore can pattern-match prefill-conformance failures across
  the corpus and propose tighter scaffolding.

### Negative

- Risk that prefill goes too deep and biases content. Mitigated by the
  depth-discipline rule (section opener only, never content). The first
  `gz-adr-evaluate` review of the prefill scaffolds explicitly scores
  this dimension; sub-3.0 scores trigger refinement under ADR-0.0.26's
  loop.
- Adds a `gz validate --prefill-conformance` scope; small validator,
  but extends the validate surface area.
- Backwards-compatibility for existing briefs authored without prefill:
  the conformance check applies only to briefs authored after this ADR
  lands. Older briefs are grandfathered via a corpus-frozen waiver in
  `data/prefill_conformance_waivers.json` (one entry per pre-existing
  brief at ADR closeout, no new entries permitted).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 5
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.45.0-01: Implement OBPI brief prefill in `gz obpi specify` skill / future CLI verb — section openers only, parent-ADR-Decision-pinned Discovery Checklist; backwards-compatible corpus-freeze waiver
- [ ] OBPI-0.45.0-02: Implement attestation text prefill via `$EDITOR` open in `gz obpi complete` and `gz adr emit-receipt`; em-dash separator + receipt-citation slot template
- [ ] OBPI-0.45.0-03: Implement `gz validate --prefill-conformance` scope (validate canonical opening lines, fail 3 on drift); BDD scenarios cover brief authoring + attestation authoring + grandfathered-waiver behavior

## Q&A Transcript

Authored 2026-04-25 from Anthropic Prompt Engineering 101 (Hannah Moran
+ Christian Ryan) review session. The talk demonstrated prefill at the
output-shaping layer (JSON, XML); this ADR applies the same technique at
the authoring-scaffolding layer. Key insight from the talk: prefill is
the section opener only, not the section content — the right depth is
"just enough to lock structure, not enough to bias content."

## Evidence

- [ ] Brief skeleton: `src/gzkit/skills/gz-obpi-specify/` and brief template
- [ ] Attestation prefill: `src/gzkit/commands/obpi.py` `complete` + `src/gzkit/commands/adr_emit_receipt.py`
- [ ] Validator: `src/gzkit/governance/trust_audits.py` (new `validate_prefill_conformance`)
- [ ] Tests: `tests/governance/test_prefill_conformance.py`, `tests/commands/test_obpi_complete_prefill.py`
- [ ] BDD: `features/prefill_conformance.feature`
- [ ] Corpus-freeze: `data/prefill_conformance_waivers.json`

## Alternatives Considered

1. **Deeper prefill including example content** — rejected per the
   depth-discipline rule. The talk's pattern is a single open token;
   biasing content with examples violates the technique.
2. **Apply to brief only, defer attestation** — rejected. The two
   surfaces are shape-identical (canonical structure + agent-filled
   slots), and ADR-0.0.24's receipt-binding work creates the right
   moment to land both at once. Splitting risks a second-pass surface
   change that re-touches the same files.
3. **Author as a docs-only "use this template" pattern** — rejected.
   Discipline-only enforcement is demonstrably insufficient at the
   current frontier (Opus 4.7 § 2.3.6.2: model wrote six memory files
   about a rule and re-violated). Mechanical conformance check is the
   right shape.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.45.0 | Pending | | | |
