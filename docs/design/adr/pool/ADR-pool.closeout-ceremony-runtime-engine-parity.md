---
id: ADR-pool.closeout-ceremony-runtime-engine-parity
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: GHI #517
promoted_to: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
---

# ADR-pool.closeout-ceremony-runtime-engine-parity: Closeout Ceremony Runtime Engine Parity
> Promoted to `ADR-0.0.63-closeout-ceremony-runtime-engine-parity` on 2026-05-26. This pool file is retained as historical intake context.


## Status

Superseded

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

## Target Scope

- **step-advance-gate-5-enforcement** — `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`. Step 6→7 `--next` reads ledger for the prior step's expected receipt and fail-closes if absent. Eliminates the Gate 5 bypass.
- **demo-and-arb-receipt-discipline** — `src/gzkit/commands/ceremony_data.py:288-342`. Demo extraction re-executes the demo command and binds the ARB receipt to observed exit code + stdout SHA. ARB generators accept multi-line command strings as a single quoted argv list.
- **evidence-summary-and-proof-binding** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339` plus new CLI validator `gz validate --closeout-proof-binding`. Evidence Summary Template gains a REQ column; every receipt row binds `(REQ-ID, receipt-ID, file-line range)` in markdown + structured JSON. Validator exits 3 on missing REQ↔receipt-ID bindings.
- **closeout-skill-reverify-wording-fix** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:60-65`. Wording fix resolving the "Does NOT re-verify" vs spec-reviewer "Independent re-verification" contradiction (CLI pipeline does not re-execute; spec-reviewer persona-dispatch retains independent re-verification).
- **dual-runtime-collapse** — `gz closeout --ceremony --attest` vs Step 7 pipeline emit identical ledger surfaces. The runtime engine is single source; `--attest` becomes an orchestration shortcut.
- **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose.

## Proposed OBPI Decomposition

| Slug | Description |
|---|---|
| `step-advance-gate-5-enforcement` | Gate Step 6→7 advance on ledger evidence of prior step's expected receipt at `closeout_ceremony.py:401`; fail-close at boundaries; mirror the `_run_pipeline_*_stage` shape from `obpi_cmd.py:446-494`. |
| `demo-and-arb-receipt-discipline` | Re-execute demo commands before ARB-receipt emission at `ceremony_data.py:288-291`; quote multi-line ARB commands as a single argv list at `:326, 332, 342`; receipts cite observed exit code + stdout SHA. |
| `evidence-summary-and-proof-binding` | Add REQ column to Evidence Summary Template at SKILL.md:285-339; render markdown + structured JSON; implement `gz validate --closeout-proof-binding` to fail-close on missing REQ↔receipt-ID bindings. |
| `closeout-skill-reverify-wording-fix` | Reconcile "Does NOT re-verify" wording at SKILL.md:60-65 with the spec-reviewer "Independent re-verification" persona-dispatch step; resolves D9 internal contradiction surfaced by GHI #517. |
| `dual-runtime-collapse` | Collapse `gz closeout --ceremony --attest` and Step 7 pipeline emission paths to a single runtime engine; `--attest` becomes an orchestration shortcut, not a parallel emitter. |
| `req-evidence-schema-consumption` | Wire the runtime engine to consume the `req_evidence:` field once added by `ADR-pool.obpi-authoring-mechanical-floor`; mechanical proof-binding replaces prose evidence claims. |

## Non-Goals

1. **Closeout layers do not re-execute claimed receipts.** Per operator tie-break D9 (`artifacts/reports/ghi-517-cross-analyst-reconciliation.md`), presenter posture is preserved; re-verification stays with the spec-reviewer persona-dispatch step. This ADR adds *binding*, not *re-execution*.
2. **Audit-ceremony runtime parity is out of scope.** Audit-side defects (F7, F8, P3-r5) route via `ADR-pool.receipt-taxonomy-audit-passed-vs-validated` (amended 2026-05-26).
3. **Persona-dispatch attestation is out of scope.** Pattern A's persona-dispatch defects route via `ADR-pool.obpi-pipeline-dispatch-attestation` (amended 2026-05-26).
4. **Backfill of prior closeouts is out of scope.** This ADR gates forward closeouts only; retroactive re-attestation is a separate operator decision.
5. **No new quality checks are added** beyond `gz validate --closeout-proof-binding`. Per ADR-0.19.0's scope ceiling, this ADR orchestrates and gates existing checks; it does not introduce new gates.

## Decision

1. **Convert `gz closeout --ceremony` to a CLI state machine.** Parallel the `_run_pipeline_*_stage` shape from `obpi_cmd.py:446-494`. Each step transition reads ledger state for the prior step's expected receipt and fail-closes if absent. Eliminates Step 6→7 self-advance.
2. **Add demo-extraction re-execution preflight.** Before emitting an ARB receipt from extracted demo content, re-execute the demo command and bind the receipt to the *observed* exit code and stdout SHA, not the T1 prose claim.
3. **Quote multi-line ARB commands.** ARB receipt generators must accept multi-line command strings as a single quoted argv list, not split-on-newline.
4. **Add REQ column to Evidence Summary Template.** Every Evidence Summary row binds (REQ-ID, receipt-ID, file-line range). Render in markdown + structured JSON for the closeout state machine to consume.
5. **Implement REQ↔receipt-ID validator with fail-close.** New `gz validate --closeout-proof-binding` checks that every REQ in the parent ADR's Acceptance Criteria has at least one binding receipt-ID cited in the closeout Evidence Summary; missing bindings exit 3.
6. **Collapse dual-runtime paths.** `gz closeout --ceremony --attest` and the Step 7 pipeline must emit identical ledger surfaces. The runtime engine is the single source; the `--attest` flag is an orchestration shortcut, not a parallel emitter.

## Alternatives Considered

1. **Convert closeout layers to active re-verifier posture (D9 alternative).** Closeout would re-execute every claimed receipt rather than trusting Layer-1 self-declaration. **Rejected** by operator tie-break (2026-05-26): cheapest fix is proof-binding + fail-close while preserving presenter posture; the spec-reviewer persona-dispatch step retains the actual re-verification role.
2. **Patch closeout in place without state-machine conversion.** Leave the step-counter shape, add Gate 5 guard at the specific `--next` call site. **Rejected:** the step-counter is itself the defect — every future step boundary is a regression risk without the runtime gate.

## Patterns surfaced

Per GHI #517 § Dispute D8 (operator tie-break: two parallel dominant patterns):

- **Prose-vs-mechanics.** Closeout currently presents prose evidence and emits ledger receipts that trust the prose; the state-machine conversion replaces narrative recall with mechanical receipt-binding.
- **Tautological-test-surface (GHI #531).** Tests on closeout currently assert filesystem shape (file exists, contains string X), not semantics (the receipt's claimed invocation matches the actual invocation). REQ-derived assertions per `.gzkit/rules/tests.md` § "Tests assert semantics, not strings" must accompany each runtime-engine change.

## Origin

`artifacts/reports/ghi-517-cross-analyst-reconciliation.md` §§ Confirmed across analysts (items 1-3, 5-7), Dispute D9, Revised P5 framing.
