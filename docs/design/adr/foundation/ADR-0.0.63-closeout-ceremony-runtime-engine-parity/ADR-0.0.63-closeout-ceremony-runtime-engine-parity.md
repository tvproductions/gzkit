---
id: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
status: Proposed
kind: foundation
semver: 0.0.63
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-26
promoted_from: ADR-pool.closeout-ceremony-runtime-engine-parity
---

# ADR-0.0.63-closeout-ceremony-runtime-engine-parity: Closeout Ceremony Runtime Engine Parity

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Intent

ADR-0.19.0 validated the closeout-pipeline *shell* (consolidate `gz closeout` into a single orchestrated command). The runtime engine behind that shell has structural-parity gaps with `gz obpi pipeline`. `gz obpi pipeline` runs a CLI state machine (`src/gzkit/commands/obpi_cmd.py:446-494`) that fail-closes on stage boundaries; `gz closeout --ceremony --next` walks a step-counter that the CLI does not gate against the operator's actual completion of Gate 5. This pool ADR scopes the runtime-engine parity work that ADR-0.19.0 deliberately deferred ("orchestrating existing capabilities into single commands. No new quality checks are added").

Surfaced by cross-analyst diagnosis in GHI #517 (`artifacts/reports/ghi-517-cross-analyst-reconciliation.md`).

### Absorbed findings

| ID | Surface | Defect |
|---|---|---|
| F1 | `closeout_ceremony.py:401, 416-426, 449-456` | Step 6→7 `--next` advances without consulting Gate 5 attestation state — agent can self-advance past human-attestation gate |
| F2 | `ceremony_data.py:288, 290-291` | Demo-extraction emits ARB receipt without re-execution preflight; trusts T1 prose claim |
| F3 | `ceremony_data.py:326, 332, 342` | Multi-line ARB command strings are fragment-split before quoting; receipts cite truncated invocations |
| F9 | `gz-adr-closeout-ceremony/SKILL.md:285-339` | Evidence Summary Template has no REQ column — receipts can't bind to specific REQs (related D9 proof-binding gap) |
| F13/F15 | `gz closeout --ceremony --attest` vs Step 7 pipeline | Dual-runtime / dual-emission paths produce different ledger surfaces for the same logical closeout |
| D9 fix | `closeout_ceremony.py` + Evidence Summary | Add mechanical REQ↔receipt-ID proof-binding with fail-close on missing bindings (presenter posture retained per operator tie-break) |

## Decision

1. **Convert `gz closeout --ceremony` to a CLI state machine.** Parallel the `_run_pipeline_*_stage` shape from `obpi_cmd.py:446-494`. Each step transition reads ledger state for the prior step's expected receipt and fail-closes if absent. Eliminates Step 6→7 self-advance.
2. **Add demo-extraction re-execution preflight.** Before emitting an ARB receipt from extracted demo content, re-execute the demo command and bind the receipt to the *observed* exit code and stdout SHA, not the T1 prose claim.
3. **Quote multi-line ARB commands.** ARB receipt generators must accept multi-line command strings as a single quoted argv list, not split-on-newline.
4. **Add REQ column to Evidence Summary Template.** Every Evidence Summary row binds (REQ-ID, receipt-ID, file-line range). Render in markdown + structured JSON for the closeout state machine to consume.
5. **Implement REQ↔receipt-ID validator with fail-close.** New `gz validate --closeout-proof-binding` checks that every REQ in the parent ADR's Acceptance Criteria has at least one binding receipt-ID cited in the closeout Evidence Summary; missing bindings exit 3.
6. **Collapse dual-runtime paths.** `gz closeout --ceremony --attest` and the Step 7 pipeline must emit identical ledger surfaces. The runtime engine is the single source; the `--attest` flag is an orchestration shortcut, not a parallel emitter.

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.63-01: **step-advance-gate-5-enforcement** — `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`. Step 6→7 `--next` reads ledger for the prior step's expected receipt and fail-closes if absent. Eliminates the Gate 5 bypass.
- [ ] OBPI-0.0.63-02: **demo-and-arb-receipt-discipline** — `src/gzkit/commands/ceremony_data.py:288-342`. Demo extraction re-executes the demo command and binds the ARB receipt to observed exit code + stdout SHA. ARB generators accept multi-line command strings as a single quoted argv list.
- [ ] OBPI-0.0.63-03: **evidence-summary-and-proof-binding** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339` plus new CLI validator `gz validate --closeout-proof-binding`. Evidence Summary Template gains a REQ column; every receipt row binds `(REQ-ID, receipt-ID, file-line range)` in markdown + structured JSON. Validator exits 3 on missing REQ↔receipt-ID bindings.
- [ ] OBPI-0.0.63-04: **closeout-skill-reverify-wording-fix** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:60-65`. Wording fix resolving the "Does NOT re-verify" vs spec-reviewer "Independent re-verification" contradiction (CLI pipeline does not re-execute; spec-reviewer persona-dispatch retains independent re-verification).
- [ ] OBPI-0.0.63-05: **dual-runtime-collapse** — `gz closeout --ceremony --attest` vs Step 7 pipeline emit identical ledger surfaces. The runtime engine is single source; `--attest` becomes an orchestration shortcut.
- [ ] OBPI-0.0.63-06: **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose.

## Target Scope

- **step-advance-gate-5-enforcement** — `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`. Step 6→7 `--next` reads ledger for the prior step's expected receipt and fail-closes if absent. Eliminates the Gate 5 bypass.
- **demo-and-arb-receipt-discipline** — `src/gzkit/commands/ceremony_data.py:288-342`. Demo extraction re-executes the demo command and binds the ARB receipt to observed exit code + stdout SHA. ARB generators accept multi-line command strings as a single quoted argv list.
- **evidence-summary-and-proof-binding** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339` plus new CLI validator `gz validate --closeout-proof-binding`. Evidence Summary Template gains a REQ column; every receipt row binds `(REQ-ID, receipt-ID, file-line range)` in markdown + structured JSON. Validator exits 3 on missing REQ↔receipt-ID bindings.
- **closeout-skill-reverify-wording-fix** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:60-65`. Wording fix resolving the "Does NOT re-verify" vs spec-reviewer "Independent re-verification" contradiction (CLI pipeline does not re-execute; spec-reviewer persona-dispatch retains independent re-verification).
- **dual-runtime-collapse** — `gz closeout --ceremony --attest` vs Step 7 pipeline emit identical ledger surfaces. The runtime engine is single source; `--attest` becomes an orchestration shortcut.
- **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose.

## Non-Goals

1. **Closeout layers do not re-execute claimed receipts.** Per operator tie-break D9 (`artifacts/reports/ghi-517-cross-analyst-reconciliation.md`), presenter posture is preserved; re-verification stays with the spec-reviewer persona-dispatch step. This ADR adds *binding*, not *re-execution*.
2. **Audit-ceremony runtime parity is out of scope.** Audit-side defects (F7, F8, P3-r5) route via `ADR-pool.receipt-taxonomy-audit-passed-vs-validated` (amended 2026-05-26).
3. **Persona-dispatch attestation is out of scope.** Pattern A's persona-dispatch defects route via `ADR-pool.obpi-pipeline-dispatch-attestation` (amended 2026-05-26).
4. **Backfill of prior closeouts is out of scope.** This ADR gates forward closeouts only; retroactive re-attestation is a separate operator decision.
5. **No new quality checks are added** beyond `gz validate --closeout-proof-binding`. Per ADR-0.19.0's scope ceiling, this ADR orchestrates and gates existing checks; it does not introduce new gates.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.closeout-ceremony-runtime-engine-parity` on 2026-05-26; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.63 | Pending | | | |
