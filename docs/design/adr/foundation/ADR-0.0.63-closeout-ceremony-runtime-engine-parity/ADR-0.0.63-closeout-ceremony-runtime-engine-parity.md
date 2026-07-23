---
id: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
status: Validated
kind: foundation
semver: 0.0.63
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-26
promoted_from: ADR-pool.closeout-ceremony-runtime-engine-parity
---

# ADR-0.0.63-closeout-ceremony-runtime-engine-parity: Closeout Ceremony Runtime Engine Parity

## Persona

You hold the ledger as the source of truth over agent narration. Every closeout
transition is a state-machine edge that MUST consult recorded evidence before it
advances — never a step counter the agent can walk past. You verify observed
behavior: a re-executed command, an observed exit code, a stdout SHA — never the
prose claim of what a command would have done. When a brief authors a command,
you treat the runtime that executes it as the contract, not the shell the author
imagined. Craftsperson, governance-aware, whole-file-reasoning, direct.

## Intent

ADR-0.19.0 validated the closeout-pipeline *shell* (consolidate `gz closeout` into a single orchestrated command). The runtime engine behind that shell has structural-parity gaps with `gz obpi pipeline`. `gz obpi pipeline` runs a CLI state machine (`src/gzkit/commands/obpi_cmd.py:446-494`) that fail-closes on stage boundaries; `gz closeout --ceremony --next` walks a step-counter that the CLI does not gate against the operator's actual completion of Gate 5. This pool ADR scopes the runtime-engine parity work that ADR-0.19.0 deliberately deferred ("orchestrating existing capabilities into single commands. No new quality checks are added").

Surfaced by cross-analyst diagnosis in GHI #517 (`artifacts/reports/ghi-517-cross-analyst-reconciliation.md`).

## Why foundation tier?

**Invariance test:** Without this ADR, the project would not be the project because the closeout ceremony's `--next` step counter would let agents self-advance past Gate 5, breaking the universal human-attestation invariant (ADR-0.0.36) that anchors every audit receipt and turning the ledger trust chain into agent-narrated state. Closeout-runtime parity with `gz obpi pipeline`'s CLI state machine is structural identity for gzkit: it is the mechanism that makes ledger evidence — not agent claims — the source of truth at the moment of attestation.

**Port-vs-adapter framing:** This ADR is a **port** — it specifies that closeout transitions MUST consult ledger state for the prior step's expected receipt and fail-close on absence, that demo-extraction ARB receipts MUST bind to re-executed observations rather than T1 prose, and that `--ceremony --attest` and the Step 7 pipeline MUST emit identical ledger surfaces. The CLI state machine in `closeout_ceremony.py` is the canonical adapter; `gz validate --closeout-proof-binding` is the mechanical adapter for the REQ↔receipt-ID binding rule.

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

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Every closeout-bound REQ binds to a ledger-present receipt-ID; the closeout proof-binding gate fails closed on an unbound REQ. | uv run gz validate --closeout-proof | 0 |

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
- Baseline Selected: 7
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 7

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.63-01: **step-advance-gate-5-enforcement** — `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`. Step 6→7 `--next` reads ledger for the prior step's expected receipt and fail-closes if absent. Eliminates the Gate 5 bypass.
- [ ] OBPI-0.0.63-02: **demo-and-arb-receipt-discipline** — `src/gzkit/commands/ceremony_data.py:288-342`. Demo extraction re-executes the demo command and binds the ARB receipt to observed exit code + stdout SHA. ARB generators accept multi-line command strings as a single quoted argv list.
- [ ] OBPI-0.0.63-03: **evidence-summary-and-proof-binding** — `obpi_brief_structure.json` + `BriefStructure` gain the optional `ln` (`ReqEvidence`) field (`{req_id, receipt_ids, file_lines}`, relocated from `ADR-pool.obpi-authoring-mechanical-floor` item 2); `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339` Evidence Summary Template gains a REQ column; new CLI validator `gz validate --closeout-proof-binding` binds `(REQ-ID, receipt-ID, file-line range)` in markdown + structured JSON and exits 3 on a REQ with no ledger-present receipt-ID binding.
- [ ] OBPI-0.0.63-04: **closeout-skill-reverify-wording-fix** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:60-65`. Wording fix resolving the "Does NOT re-verify" vs spec-reviewer "Independent re-verification" contradiction (CLI pipeline does not re-execute; spec-reviewer persona-dispatch retains independent re-verification).
- [ ] OBPI-0.0.63-05: **dual-runtime-collapse** — `gz closeout --ceremony --attest` vs Step 7 pipeline emit identical ledger surfaces. The runtime engine is single source; `--attest` becomes an orchestration shortcut.
- [ ] OBPI-0.0.63-06: **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose.
- [ ] OBPI-0.0.63-07: **verify-stage-command-shape-gate** — `src/gzkit/commands/obpi_stages.py:140-147` + `src/gzkit/quality.py:41-94`. The OBPI-pipeline verify stage and a fail-closed `gz validate` scope reject brief `## Verification` commands that are not single-program shell-less invocations (`&&`, `||`, `|`, `;`, `$(...)`, redirects), so authoring-vs-runtime mismatch (GHI #550) fails closed at authoring time rather than erroring confusingly at the verify gate. Reuses the shell-less command classifier built by OBPI-0.0.63-02.

## Target Scope

- **step-advance-gate-5-enforcement** — `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`. Step 6→7 `--next` reads ledger for the prior step's expected receipt and fail-closes if absent. Eliminates the Gate 5 bypass.
- **demo-and-arb-receipt-discipline** — `src/gzkit/commands/ceremony_data.py:288-342`. Demo extraction re-executes the demo command and binds the ARB receipt to observed exit code + stdout SHA. ARB generators accept multi-line command strings as a single quoted argv list.
- **evidence-summary-and-proof-binding** — `obpi_brief_structure.json` + `BriefStructure` gain the optional `ln` (`ReqEvidence`) field (`{req_id, receipt_ids, file_lines}`, relocated from `ADR-pool.obpi-authoring-mechanical-floor` item 2); `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339` Evidence Summary Template gains a REQ column; new CLI validator `gz validate --closeout-proof-binding` binds `(REQ-ID, receipt-ID, file-line range)` in markdown + structured JSON and exits 3 on a REQ with no ledger-present receipt-ID binding. Opt-in scope (not default `gz check`); in-scope = ADRs with a persisted closeout ceremony state.
- **closeout-skill-reverify-wording-fix** — `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:60-65`. Wording fix resolving the "Does NOT re-verify" vs spec-reviewer "Independent re-verification" contradiction (CLI pipeline does not re-execute; spec-reviewer persona-dispatch retains independent re-verification).
- **dual-runtime-collapse** — `gz closeout --ceremony --attest` vs Step 7 pipeline emit identical ledger surfaces. The runtime engine is single source; `--attest` becomes an orchestration shortcut.
- **req-evidence-schema-consumption** — Post-P2 increment. The runtime engine consumes the `req_evidence:` field added to `obpi_brief_structure.json` by `ADR-pool.obpi-authoring-mechanical-floor`; binding logic is mechanical, not prose.
- **verify-stage-command-shape-gate** — `src/gzkit/commands/obpi_stages.py:140-147` + `src/gzkit/quality.py:41-94`. The verify-stage extractor and a fail-closed `gz validate` scope classify each brief `## Verification` command against the shell-less executor's contract (`shlex.split` + `shell=False`, GHI #415) and reject compound forms (`&&`, `||`, `|`, `;`, `$(...)`, redirects) at authoring time. Closes GHI #550 by making the authoring-vs-runtime mismatch fail closed rather than surface as `test: unexpected operator` at the verify gate. The `## Verification` brief template gains guidance naming the single-program-only contract. Reuses the shell-less command classifier built by OBPI-0.0.63-02.

## Non-Goals

1. **Closeout layers do not re-execute claimed receipts.** Per operator tie-break D9 (`artifacts/reports/ghi-517-cross-analyst-reconciliation.md`), presenter posture is preserved; re-verification stays with the spec-reviewer persona-dispatch step. This ADR adds *binding*, not *re-execution*.
2. **Audit-ceremony runtime parity is out of scope.** Audit-side defects (F7, F8, P3-r5) route via `ADR-pool.receipt-taxonomy-audit-passed-vs-validated` (amended 2026-05-26).
3. **Persona-dispatch attestation is out of scope.** Pattern A's persona-dispatch defects route via `ADR-pool.obpi-pipeline-dispatch-attestation` (amended 2026-05-26).
4. **Backfill of prior closeouts is out of scope.** This ADR gates forward closeouts only; retroactive re-attestation is a separate operator decision.
5. **No new quality checks are added** beyond `gz validate --closeout-proof-binding` and the brief-command-shape fail-close added by OBPI-0.0.63-07 (GHI #550). Per ADR-0.19.0's scope ceiling, this ADR otherwise orchestrates and gates existing checks. **Amendment (2026-05-29, operator-approved):** OBPI-07 was added to absorb GHI #550 — the verify-stage authoring-vs-runtime mismatch — because it is the same root-cause family as F3/#539 (briefs authored as shell-compatible text, executed under the shell-less runtime) and shares OBPI-02's command classifier. The `--closeout-proof-binding` ceiling stands for the *closeout* surface; the OBPI-07 gate fences the *verify* surface, which is upstream of closeout and was not in the original GHI #517 diagnosis scope. Demo-execution evidence (GHI #540) is achieved by OBPI-02's re-execution preflight (ARB receipt binds to observed exit code + stdout SHA), not by a separate validator, and therefore needs no carve-out here.

## Boundary Invariants

Cross-OBPI invariants auditable only at ADR closeout (the proof channel for
`[STRUCTURAL-FENCE]` REQs per ADR-0.0.59). Each spans more than one OBPI in this
ADR and cannot be verified inside a single brief.

- **BI-1 — Shell-less brief-command executability.** Every command harvested from
  an OBPI brief's `## Verification`, `## Demo`, or `## Examples` section MUST be a
  single-program, shell-less-executable invocation: `shlex.split`-parseable argv,
  no `&&`, `||`, `|`, `;`, `$(...)`, or redirects. Multi-line quoted constructs
  (e.g. `python -c "…"` spanning lines) are joined into one logical command, never
  split per physical line. Spans OBPI-02 (Demo/Examples extractor) and OBPI-07
  (Verification extractor + validator); both consume one shared classifier.
- **BI-2 — Single-runtime-engine ledger parity.** `gz closeout --ceremony --next`,
  `gz closeout --ceremony --attest`, and the Step 7 pipeline emit byte-identical
  ledger surfaces for the same logical closeout; the runtime engine is the single
  source and `--attest` is an orchestration shortcut, never a parallel emitter.
  Spans OBPI-01 (state machine) and OBPI-05 (dual-runtime collapse).
- **BI-3 — Gate-5 cannot be self-advanced.** No closeout step transition past the
  human-attestation boundary succeeds without ledger evidence of the prior step's
  expected receipt; the step counter is replaced by ledger-gated edges. Anchored
  by OBPI-01; consumed by OBPI-03 (proof-binding) and OBPI-06 (req-evidence).

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
| 0.0.63 | Completed | Jeffry | 2026-05-30 | attest completed — ADR-0.0.63 closeout-ceremony-runtime-engine-parity: 7/7 OBPIs attested; 29 Acceptance-Criteria REQs bound via ln: to passing ARB receipts, gz validate --closeout-proof-binding exit 0; fresh closeout QA green: arb-ruff-f05703d8b5c74730b3be0fb2619cda93, arb-step-unittest-4bd33eccdf254997adc0a56dfe0f017e, arb-step-typecheck-3ef794e4b89d4cc5a13863aa2276e9b9, arb-step-mkdocs-3dbefdf3c0f14c6bac637cce21f2e59b; 67 ceremony/pipeline/brief-shape tests green across 12 live demos. |
