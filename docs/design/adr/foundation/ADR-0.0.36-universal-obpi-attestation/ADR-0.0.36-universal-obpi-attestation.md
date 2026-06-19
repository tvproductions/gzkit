---
id: ADR-0.0.36-universal-obpi-attestation
status: Validated
kind: foundation
semver: 0.0.36
lane: heavy
parent: ADR-0.0.18
date: 2026-04-26
---

# ADR-0.0.36-universal-obpi-attestation: Universal OBPI Attestation (Zero-Maxxing)

## Persona

**Active persona:** `main-session` — doctrine author treating OBPI completion attestation as a load-bearing invariant, not a configurable workflow knob. The craft standard for this ADR is *every state shape that pre-doctrine permitted self-close becomes structurally unreachable post-doctrine*. The reviewer test: an adopter cannot construct a valid OBPI completion path that omits brief-level human attestation, regardless of which combination of `kind` and `lane` they choose for the parent ADR.

## Why foundation tier?

Without this ADR, OBPI attestation surface varies by lane/kind — heavy and lite paths take different code routes, attestation events emit with inconsistent payloads, and adopters can't reason uniformly about what an OBPI completion event actually proves.

This ADR authors a port: the universal OBPI attestation contract every closeout, complete, and receipt-emit surface honors regardless of lane or kind.

## Intent

> **Operator course correction (2026-04-26, GHI #331 closure):** *"drop all ideas of self-closing... agents vibe too much. ABANDON that idea. GovZero is Zero-maxxing."*

GovZero's posture is that every governance lever maximizes attestation surface, never relaxes it. The Lane & Kind Attestation Matrix in `AGENTS.md` § OBPI Acceptance Protocol carried one row that violated this posture:

| Parent Kind | Parent Lane | Brief-level Human Attestation |
|-------------|-------------|-------------------------------|
| `feature`   | `lite`      | Self-closeable after evidence |

The "self-closeable" cell is the doctrine smell. Every state shape that surfaced in the GHI #332 audit of ADR-0.16.0 closeout drift (`attestation_requirement: optional`, `obpi_completion: completed` without the `attested_` prefix, `attestor: agent:claude-code`) exists *only because* the matrix permits the cell. The runtime gate's foundation/lane branching, the receipt schema's `optional` enum value, the skill prose's "self-closeable after evidence" language — all of these are downstream rationalizations of the matrix's permission. Closing the cell at the doctrine layer collapses the entire branch.

The companion defenses (`_enforce_human_attestation_authenticity`'s TTY + `ATTEST` confirmation gate, the validator's existing receipt-shape checks) are necessary but not sufficient — they prevent forged attestation, they do not prevent the absence of attestation when the matrix says absence is acceptable. Universal attestation is the upstream surface that makes those defenses meaningful.

This ADR amends `AGENTS.md` § OBPI Acceptance Protocol to bind brief-level human attestation universally, collapses the runtime gate, extends the validator to refuse the deprecated receipt shapes on new entries, documents the historical drift via a closed waiver list, and sweeps the dependent skills. It is the destination ADR that closes GHI #342.

> **Addendum (2026-05-14, canon-owner declaration).** Non-goal #2 below — "remove the TTY + `ATTEST` gate" — is **superseded**. The operator (canon owner) declared verbatim across 2026-05-12 (×2) and 2026-05-14 that operator-verbatim conversational attestation IS the Gate-5 attestation: *"WHEN I SAY ATTEST COMPLETED IT IS MOTHERFUCKING COMPLETE — ALWAYS, ALWAYS, ALWAYS"*, *"MY WORD IS AUTHORITY IN ALL CASES"*, *"WHEN I SAY 'ATTEST COMPLETED' THAT IS MY ZERO MAXXING"*. The TTY `ATTEST` authenticity gate (`_enforce_human_attestation_authenticity`) was removed as a direct fix on 2026-05-14: it had grown from a forged-attestation defense into a mechanism that gated the canon owner out of their own system. This does **not** relax the universal-attestation foundation — every OBPI still requires brief-level human attestation; that attestation is now satisfied by the operator's verbatim `--attestation-text` (`attestation_type: operator-verbatim-conversational`) rather than a separate TTY ceremony. The forged-attestation boundary is held instead by `AGENTS.md` § Never #1 and audit. `OBPI-0.0.36-02-runtime-gate-collapse`'s gate-collapse intent is partially delivered by this fix.

## Decision

**Brief-level human attestation is required for every OBPI completion, regardless of parent ADR kind or lane. There is no self-close path.**

**Rationale:** the Lane & Kind Attestation Matrix's `feature × lite → Self-closeable` cell is the single matrix entry that violates GovZero zero-maxxing posture, and it is the structural cause of every deprecated state shape surfaced in the GHI #332 audit. Because the cell is upstream of the runtime gate, the receipt schema, and the skill prose, closing it at the doctrine layer collapses every downstream rationalization simultaneously. Hardening any single downstream surface (TTY gate, schema enum, skill language) without closing the matrix leaves the doctrine smell intact and merely re-routes vibing through whichever next-easiest surface — therefore the matrix collapse is the load-bearing change, and the runtime/validator/skill changes are mechanical enforcement of the doctrine, not independent decisions.

Concrete bindings:

1. **AGENTS.md § OBPI Acceptance Protocol** — the Lane & Kind Attestation Matrix collapses to a single row stating universal attestation. Lane and kind continue to determine *which gates fire* (Gate 3 docs scope, Gate 4 BDD scope); they no longer determine *whether Gate 5 brief-level attestation fires*. Gate 5 at the brief level is universal.

2. **`src/gzkit/commands/adr_audit.py::_requires_human_obpi_attestation`** collapses to `return True`. Signature is preserved (callers do not change). The `_is_foundation_adr` helper becomes orphaned by this collapse and is grepped + removed (or retained with a deprecation marker if other call-sites exist) under OBPI-0.0.36-02.

3. **`gz validate` gains a fail-closed scope (working name `--receipt-shape`)** that refuses any receipt dated after this ADR's `date:` cutoff carrying `attestation_requirement: optional`, `obpi_completion: completed` without the `attested_` prefix, or `attestor` matching `^agent:`. Exit 3 on any unwaived violation.

4. **`data/historical_self_close_waivers.json`** lists every closed-ADR receipt that pre-dates this doctrine and would otherwise fail the new validator scope. The waiver list is closed to new entries — adding a waiver after this ADR's authoring is itself a doctrine breach. Validator schema-checks the waiver list and refuses any entry whose `added_under` is not OBPI-0.0.36-04 or a future-authored explicit "waiver-extension" ADR (which would require its own ceremony to author).

5. **Skill prose sweep** — `.gzkit/skills/gz-obpi-pipeline`, `.gzkit/skills/gz-obpi-reconcile`, `.gzkit/skills/ghi-close`, `.gzkit/skills/gz-adr-closeout-ceremony`, and any `.claude/rules/` or `.gzkit/rules/` file referencing the deleted lite-lane self-close path updates to the universal-attestation rule. The mirror sync (`gz agent sync control-surfaces`) propagates.

Historical receipts with the deprecated shapes are preserved per ledger immutability. They are documented as historical drift in the GHI #332 audit and the OBPI-0.0.36-04 waiver list — **not** retroactively re-attested. The doctrine binds going forward.

## Non-goals (explicit exclusions)

- **Retroactive re-attestation of historical receipts.** Ledger immutability binds; pre-doctrine receipts are documented via the waiver list, not rewritten.
- ~~**Removal of `_enforce_human_attestation_authenticity` (TTY + `ATTEST` gate).** Authenticity defense remains as-is; this ADR addresses the absence-of-attestation surface, not the forged-attestation surface. The two defenses compose.~~ **SUPERSEDED 2026-05-14** (see Intent addendum) — the TTY gate was removed by direct fix per the canon-owner declaration; the forged-attestation boundary is now held by `AGENTS.md` § Never #1 and audit.
- **Changes to lane/kind axes for *gate-firing scope*.** Lane still determines whether Gate 3 (docs) and Gate 4 (BDD) fire. Kind still determines foundation-vs-feature classification per ADR-0.0.18. Only Gate 5 brief-level attestation becomes universal.
- **A new CLI verb.** Validator scope is added under existing `gz validate --<scope>` shape; no new top-level command.
- **Migration of existing closed ADRs to a new attestation format.** Closed ADRs stay closed; this ADR binds going forward from its `date:` cutoff.

## Precedent and architectural alignment

This ADR sits inside the same lineage as the OBPI completion / attestation foundation series and inherits their patterns:

- **ADR-0.0.18 (ADR Taxonomy Doctrine)** — supplied the matrix this ADR amends; `kind`/`lane` axes remain valid for gate-firing scope, only the Gate 5 attestation column collapses. Parent of this ADR.
- **ADR-0.0.23 (Agent Failure Mode Taxonomy)** — names the agent-vibing failure class this ADR's mechanical defenses close (`attestor: agent:*` is the canonical instance).
- **ADR-0.0.24 (Attestation Receipt Binding)** — locks receipt-shape canon; this ADR extends the receipt-shape contract by removing the `optional` enum value and the un-prefixed `completed` term as valid for new entries.
- **ADR-0.0.25 (OBPI Completion REQ Coverage Gate)** — the structural-gate exemplar this ADR follows: a single binding rule plus mechanical validator scope, no per-case configuration.
- **ADR-0.0.33 / ADR-0.0.34 (Agent Control Surface Fidelity / Rendering Substrate)** — adjacent foundation work; this ADR's skill prose sweep flows through the surface-sync ceremony those ADRs canonize.

The exemplar pattern across this lineage: doctrine in `AGENTS.md`, mechanical defense in a `gz validate --<scope>` flag, runtime-gate simplification in the relevant command module, fail-closed exit 3 on breach. This ADR follows that pattern exactly.

## Comparator Uplift (2026-05-07)

Borrowed workflow strengths increase, rather than reduce, the need for
attestation. If gzkit imports staged specs, task waves, fresh subagent reviews,
or compounding pattern capture, each imported step must still terminate in
human-witnessed OBPI completion. Universal attestation is the guardrail that
keeps ergonomic front doors from becoming self-close paths.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| No post-cutoff receipt carries a deprecated self-close shape; the universal-attestation receipt-shape gate holds. | uv run gz validate --receipt-shape | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.36-universal-obpi-attestation --check | 0 |

## Consequences

### Positive

- The vibing-leak surface that produced GHI #332's deprecated state shapes is closed at the doctrine layer; no schema, runtime gate, or skill prose can rationalize the self-close path back into existence.
- Every OBPI completion gets a witnessed, dated, attestable Gate 5 ceremony. The 5:1 governance-to-output ratio (`AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT) is enforced uniformly rather than waived per-cell.
- The runtime gate simplifies (`return True`) — fewer code paths, fewer test cases, fewer rationalizations available to future agents reading the gate.
- Validator scope becomes the mechanical defense. Doctrine drift between releases would now require either editing the validator (visible diff, attestable change) or adding a new waiver (also visible, also attestable). Silent drift is structurally unreachable.
- Adopters inherit a stronger default — gzkit-governed projects get universal-attestation discipline without per-project re-derivation.

### Negative

- Headless CI workflows that previously self-closed lite-lane feature OBPIs must route attestation through a human-attended ceremony. Operator typing burden per OBPI completion increases by one TTY+`ATTEST` confirmation.
- The historical waiver list is a one-time cleanup cost — every ADR-0.16.0-style legacy receipt has to be enumerated, classified, and registered.
- The `_is_foundation_adr` helper's value diminishes (it was load-bearing for the foundation/lane attestation branch); other call-sites need an audit pass to confirm no dependency rot.
- Skill prose sweep crosses 4+ skill files plus the rules surface; sync ceremony must propagate cleanly to all vendor mirrors (`.claude/skills`, `.github/skills`, `.agents/skills`).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 2
- Dimension Total: 7
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 5

The surface-boundary split fires because the work crosses five distinct surfaces — doctrine markdown (AGENTS.md), Python runtime gate (`adr_audit.py`), Python validator scope (`trust_audits.py` or successor), JSON data artifact (waiver list) plus its validator integration, and markdown skill prose across four skill files. Each surface attests independently; bundling violates the OBPI Decomposition Mandate's 1:1 sync.

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.36-01: AGENTS.md matrix collapse — replace Lane & Kind Attestation Matrix with universal-attestation binding rule; preserve lane/kind axes for gate-firing scope only
- [ ] OBPI-0.0.36-02: Runtime gate collapse — `_requires_human_obpi_attestation` returns `True` unconditionally; tests assert universality; orphaned-helper audit pass on `_is_foundation_adr`
- [ ] OBPI-0.0.36-03: Validator scope `--receipt-shape` fail-closed on `attestation_requirement: optional`, `obpi_completion: completed` (without `attested_`), `attestor: ^agent:` for receipts dated after ADR cutoff
- [ ] OBPI-0.0.36-04: Historical-receipt waiver list `data/historical_self_close_waivers.json` enumerating every pre-doctrine receipt the new validator would otherwise refuse; waiver schema closes new entries to OBPI-0.0.36-04 origin only
- [ ] OBPI-0.0.36-05: Skill and rule prose sweep across `gz-obpi-pipeline`, `gz-obpi-reconcile`, `ghi-close`, `gz-adr-closeout-ceremony`, plus any `.gzkit/rules/` or `.claude/rules/` file referencing the deleted lite-lane self-close path; sync to all vendor mirrors

## Q&A Transcript

**Origin:** GHI #342, opened 2026-04-26 during GHI #331 closure. Operator's verbatim direction: *"drop all ideas of self-closing... agents vibe too much. ABANDON that idea. GovZero is Zero-maxxing."*

**Design dialogue (this session, 2026-04-26):**
- Operator invoked `/ghi-close 342`. Initial close attempted `withdrawn` route correction with promise-to-route to `/gz-design` — operator named this as a dead-letter pattern.
- `ghi-close` skill bumped to v2.3.0 with binding "NEVER, EVER, EVER dead-letter a GHI" doctrine; destination ADR must be authored in-session before close.
- GHI #342 reopened; this ADR is the destination.
- Decomposition shape decided: Approach A (5 small OBPIs, one per acceptance bullet) over Approach B (3 bundled OBPIs). Operator: "proceed A."
- Design sections approved as drafted.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/commands/test_adr_audit.py` (universality assertions for `_requires_human_obpi_attestation`); `tests/governance/test_validate_receipt_shape.py` (fail-closed assertions for new validator scope)
- [ ] Docs: `AGENTS.md` § OBPI Acceptance Protocol (matrix collapse); `.gzkit/skills/*/SKILL.md` (prose sweep); `data/historical_self_close_waivers.json` (waiver authoring)

## Alternatives Considered

1. **Keep matrix, harden TTY/ATTEST gate only.** Rejected — `_enforce_human_attestation_authenticity` already exists and did not prevent the GHI #332 instances. Authenticity is a complementary defense; the matrix is the upstream surface that has to close. Hardening the authenticity gate without closing the matrix leaves the doctrine smell intact and re-routes vibing through whichever next-easiest surface.

2. **Make self-close opt-in via per-ADR frontmatter (e.g. `allow_self_close: true`).** Rejected — pushes the doctrine question onto every adopter and creates a new vibing surface ("just set the flag"). Doctrine-as-default is the only stable posture; per-ADR opt-in inverts the GovZero zero-maxxing principle by making the un-attested path one frontmatter line away.

3. **Retroactively re-attest the historical receipts.** Rejected — violates ledger immutability (`AGENTS.md` Behavior Rules — Never #2). Historical drift is documented via the waiver list, not rewritten. The waiver list is itself attestable and bounded.

4. **Single OBPI for all five work items.** Rejected — violates `AGENTS.md` § OBPI Decomposition Mandate. A brief crossing five surfaces (doctrine, runtime gate, validator, data, skill prose) cannot be meaningfully attested in a single Gate 5 ceremony — the operator would be attesting five distinct invariants at once.

5. **Three OBPIs (doctrine / runtime+validator+waiver / skill sweep) — Approach B in design dialogue.** Rejected — bundles runtime gate change with new validator scope and a new data file in OBPI-02. Larger surface per attestation re-introduces the same vibing-leak shape (one attestation covering three distinct invariants) that this ADR exists to close. Operator confirmed Approach A.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.36 | Completed | Jeffry | 2026-05-18 | Completed — operator attested verbatim 'attest completed' on 2026-05-18; 5/5 OBPIs completed with brief-level human attestation, validator --receipt-shape scope landed (arb receipts: ruff ff45cc0a, unittest 130a76b7 [5300 tests], typecheck 19a1a3dd, mkdocs d703186e), GHIs #342 and #332 already closed, doctrine boundary holding with zero post-cutoff ledger drift. |
