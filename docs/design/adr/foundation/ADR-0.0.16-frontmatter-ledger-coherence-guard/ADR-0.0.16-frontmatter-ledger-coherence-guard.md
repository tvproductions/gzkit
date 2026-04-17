---
id: ADR-0.0.16
status: Draft
semver: 0.0.16
lane: heavy
parent: GHI-167
date: 2026-04-17
---

# ADR-0.0.16: Frontmatter-ledger coherence guard and chore audit

## Persona

**Active persona:** `main-session` — craftsperson who reads the state-doctrine before trusting any surface that claims to derive from it, keeps Layer 2 authority mechanical rather than aspirational, and treats "derived state that lies" as a first-class defect class rather than a cosmetic inconsistency.

This ADR is a Foundation addition. Foundations are baseline assumptions about good app substrates — the state-doctrine (ADR-0.0.9) asserted "ledger is authoritative, frontmatter is derived"; this ADR mechanically enforces that assertion. The anti-pattern canon in AGENTS.md applies throughout, especially the DO IT RIGHT maxim (6a — fix the class of failure, not the instance): the guard is the class fix, not a per-consumer patch. The 2am-operator rubric is load-bearing here — every OBPI must preserve operator recoverability when the guard blocks a gate.

## Intent

YAML frontmatter on ADR/OBPI files (id, parent, lane, status) is Layer 3 derived state — written as a side-effect of ledger events — but 13 code paths across 8 files consume it as if it were authoritative. With no guard gate or chore audit reconciling frontmatter against ledger truth, drift accumulates silently: 94.7% of sampled ADR status: fields (18/19) disagree with ledger lifecycle. The state-doctrine rule 'frontmatter is L3 derived state; read the ledger' (ADR-0.0.9; .gzkit/rules/constraints.md § State Doctrine) has no mechanical enforcement, so every consumer is a silent corruption vector. Operator-facing output (agent reads frontmatter → reports stale lifecycle) has already misled a design session (GHI #162 surface event, 2026-04-15, ADR-0.22.0). This ADR closes the governance cluster GHI #162, #167, #168, #169, #170 by adding the missing mechanical guard and automated reconciliation, not by rewriting the 13 consumer paths.

## Decision

Build a frontmatter-ledger coherence guard, not per-consumer rewrites. The umbrella GHI #167 explicitly reframes the 13 consumer paths as acceptable cache reads once a guard exists; rewriting each consumer is speculative cleanup with no named failure mode the guard would not already catch.

**Precedent and exemplar alignment.** This ADR follows the existing pattern established by ADR-0.0.6 (documentation-cross-coverage-enforcement) and ADR-0.0.7 (config-first-resolution-discipline): both are Foundation ADRs that added a `gz validate` check to mechanically enforce an architectural invariant declared elsewhere in canon. The validator implementation will live alongside existing `gz validate` subcommands (see `src/gzkit/commands/validate.py` as the exemplar module) and will reuse the artifact-graph API already consumed by `src/gzkit/commands/status.py` for `gz adr report` lifecycle derivation. The chore follows the precedent of existing entries under `config/chores/` and uses the `gz chores` framework (`src/gzkit/commands/chores.py`). Anti-pattern guardrails: NEVER reimplement lifecycle derivation in the validator; NEVER add a `--skip-frontmatter` bypass to `gz gates`; NEVER key ledger lookups on frontmatter `id:` (that reproduces GHI #166); NEVER mutate frontmatter outside the OBPI-03 chore.

**Four OBPIs decompose the decision:**

**OBPI-A — Guard function:** `gz validate --frontmatter` parses every ADR/OBPI file, compares id/parent/lane/status against the ledger's artifact graph, and emits a per-file per-field drift report in both human and --json modes. Scoped to the four governed fields; ignores ungoverned frontmatter (tags:, related:, etc.). Exit codes follow the CLI doctrine 4-code map (0 clean, 1 user error, 2 system error, 3 policy breach = drift found). Truth source must be the same API gz adr report uses for lifecycle so two derived views cannot diverge. Supports --adr <ID> single-file scope for fast iteration. Supports --explain <ADR-ID> that names the recovery command per drifted field (e.g. 'run gz adr promote … --lane heavy' or 'run gz chore run frontmatter-ledger-coherence').

**OBPI-B — Gate integration:** Wire the guard into gz gates (Gate 1 or Gate 2) so frontmatter drift blocks progression. Error messages name recovery commands and doc anchors; never suggest hand-editing frontmatter. Canonicalizes the status vocabulary to match the ledger state machine so frontmatter uses one canon (currently Draft/Proposed/Pending/Validated/Completed are used inconsistently). Canonicalization is documented as a sticky residue (see Consequences).

**OBPI-C — Chore registration:** config/chores/frontmatter-ledger-coherence.toml registers a chore with ledger-wins auto-fix, idempotent reconciliation semantics, receipt emission per run at artifacts/receipts/frontmatter-coherence/<timestamp>.json. Receipt includes the ledger cursor sampled and every file rewritten so 'drift was introduced between event N and M' is answerable. Supports --dry-run showing the per-field diff before any destructive write. Documented operator notes state frontmatter is derived and hand-edits lose on the next run.

**OBPI-D — One-time backfill + GHI closure:** Execute the chore once against the current repo (clears the 94.7% status: drift), attach the reconciliation receipt as evidence, and close GHI #162, #167, #168, #169, #170 with receipt reference in the closeout evidence and GH issue comments.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT rewrite the 13 consumer code paths listed in GHI #167 (register.py, common.py, status.py, status_obpi.py, adr_promote_utils.py, triangle.py, hooks/obpi.py, init_cmd.py). Those remain cache reads, now guarded.
- Does NOT add an event-time sync hook that rewrites frontmatter on every ledger write. Deferred as Alternative 4; revisit only if chore cadence proves insufficient.
- Does NOT remove frontmatter status: (Alternative 2 rejected — field remains a legitimate cache).
- Does NOT extend the ledger schema with path→id mapping unless OBPI-A discovers the graph lacks canonical paths. If it does, work pauses and a follow-on ADR scopes the schema extension before OBPI-A proceeds.

**Forcing-function stress tests applied during design:**

- **Pre-mortem:** 18 months out, failure modes include guard-as-friction-tax (teams bypass with --skip-frontmatter), destructive reconciliation of operator hand-edits, chore cadence never wired to CI, canonicalization breaking downstream tooling (mkdocs macros, vendor mirrors), ledger vocabulary drift forcing perpetual canonicalization-map updates, and scope narrowness moving corruption to an ungoverned field. Mitigations: no bypass flag, --dry-run required, receipt-first diagnosis, scoped to four governed fields with explicit policy for adding new ones.
- **WWHTBT:** Ledger writes are atomic (holds — append-only single-writer); guard fast enough at repo scale (holds at ~80 ADRs, shaky at 10x); four-field scope stable (**shakiest** — if governance adds fields frequently the guard becomes perpetual catch-up); ledger status state machine canonical (mostly holds per ADR-0.0.9); operators treat frontmatter as derived (culturally shaky — the chore's destructive behavior is a stick, operator-notes are the carrot).
- **Constraint archaeology:** 'Frontmatter is L3, ledger is L2' is real and codified (ADR-0.0.9, state-doctrine.md, constraints.md); last tested negatively in GHI #162 surface event 2026-04-15. Sub-constraint 'ledger derivation of current-state is correct' is inherited — guard must use the same API gz adr report uses or two views diverge.
- **Assumption surfacing:** Frontmatter id: reliably identifies artifact (FALSE — that's GHI #166; guard must key on filesystem path, not id:); ledger graph has canonical path field (unverified — may require schema extension; if so, pauses OBPI-A); ledger-wins is operator-acceptable (culturally untested). Opposite of core assumption — 'frontmatter is authoritative, ledger is derived' — holds during gz adr create and gz register-adrs (Layer 1 bootstrap) but not after. The guard runs at gate-time, preserving this distinction by timing rather than flag.
- **2am operator:** No bypass flag; --explain prints step-by-step remediation with recovery command; --dry-run shows per-field diff; --adr single-file scope; receipts at predictable path with ledger cursor for 'what changed since'; exit codes documented in --help; gate errors name the recovery command, never 'reconcile frontmatter' as prose.
- **Reversibility:** Guard and chore are two-way (single-file unwire, ~1hr each). One-time backfill leaves sticky residue (18 files' status: values rewritten; git history preserves the originals but cultural signal of 'ledger wins' is sent). Status-vocabulary canonicalization is also sticky. Recommendation: run chore without canonicalization first if operator confidence < 90% on canon.
- **Scope minimization:** Floor is OBPI-A + OBPI-D (standalone validator + one-time backfill); ship B+C in this ADR because they are tightly coupled (chore reuses validator, gate reuses chore's ledger-wins logic). Under time pressure, drop B then C; A+D alone closes GHI #162 and gives #167 a standalone validator.

**Downstream decisions forced by this ADR:**
1. Possible follow-on ADR for ledger schema extension if OBPI-A discovers graph lacks canonical-path field (touches append-only contract, needs state-doctrine review).
2. GHI #166 closure becomes tractable once the guard enforces id: coherence (small follow-up PR, not an ADR).
3. Event-time sync hook deferred as a later ADR if chore cadence proves insufficient in 12 months.
4. Status: vocabulary canonicalization policy as a short addendum to ADR-0.0.9 (state-doctrine), not a full new ADR.
5. Chore cadence policy — who runs it, how often, where receipts live — folds into the broader chores-cadence ADR if it exists, or a follow-on governance-maintenance ADR.

## Consequences

### Positive

1. Mechanical enforcement of state-doctrine Layer 2 authority — the rule 'frontmatter is L3; read the ledger' moves from advisory prose to a gate-blocked check.
2. 13 consumer code paths become safe cache reads — no rewrite required; the guard closes GHI #168, #169, #170 architecturally per the umbrella's own reframing.
3. Drift becomes visible instead of silent — field-level diff (ledger value vs frontmatter value) turns a silent corruption vector into an inspectable report.
4. Ledger-wins reconciliation is idempotent and receipted — re-running the chore is safe; each run emits evidence consumable by audit.
5. One-time backfill clears the 94.7% status: drift as a byproduct of the first chore run (closes GHI #162) with no separate migration script.
6. Downstream confidence for GHI #166 — once the guard exists, orphan checks can trust id: because the guard enforces coherence.
7. Operator surface honesty restored — agents and humans inspecting frontmatter no longer receive stale lifecycle narration; the acute failure mode that motivated the cluster is closed.

### Negative

1. New gate surface expands CI latency — every gz gates invocation now parses all ADR/OBPI frontmatter and walks the ledger graph. Must stay sub-second at ~80 ADRs / ~200 OBPIs; budget check required as part of OBPI-A.
2. Ledger-wins reconciliation is destructive to frontmatter — hand-edits to status:/parent:/lane: vanish on the next chore run. Mitigation: document 'frontmatter is derived; edit the ledger via gz commands' in the chore's operator notes; log every overwrite in the reconciliation receipt.
3. The guard can false-block if the ledger graph is itself stale — e.g. if gz register-adrs hasn't run after ADR creation, the new ADR appears as drift. Mitigation: guard error messages must point to gz register-adrs / gz adr create as recovery, not suggest hand-editing frontmatter.
4. Frontmatter ambiguity when ledger has no equivalent — tags:, related:, and other ungoverned fields must be ignored by the guard or it false-positives on every file. Scope is explicitly the four governed fields id/parent/lane/status.
5. Chore cadence is a new operational concern — who runs it, how often, where receipts live. Mitigation: register the chore with a default cadence; integrate with gz tidy sweeps.
6. Status: vocabulary mismatch is wider than the guard alone solves — frontmatter uses Draft/Proposed/Pending/Validated/Completed inconsistently; the ledger has a canonical state machine. The guard must canonicalize frontmatter writes to match ledger vocabulary, not preserve the file's existing word. Risk: operators see an unfamiliar term appear after reconciliation.
7. Sticky residue from one-time backfill — git history preserves originals but operational workflow no longer sees them. Cultural signal 'ledger wins' becomes team convention, effectively a one-way door on the vocabulary choice.
8. Coupling of guard truth-source to gz adr report lifecycle derivation — if that derivation is itself wrong, the guard silently enforces wrong truth. Must share the same derivation API, not reimplement it.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 8
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.16-01: `gz validate --frontmatter` guard parses every ADR/OBPI file, compares four governed fields against ledger graph via path-keyed lookup, emits per-file per-field drift report (human + JSON), supports `--adr` single-file scope and `--explain` remediation mode, exit codes follow CLI doctrine 4-code map.
- [ ] OBPI-0.0.16-02: Wire guard into `gz gates` at Gate 1 so drift blocks progression; error messages name executable recovery commands; canonical status-vocabulary mapping authored as ADR-0.0.9 addendum in `docs/governance/state-doctrine.md` and exposed as typed Python constant.
- [ ] OBPI-0.0.16-03: Register `frontmatter-ledger-coherence` chore at `config/chores/frontmatter-ledger-coherence.toml` with ledger-wins reconciliation, idempotent semantics, receipt emission at `artifacts/receipts/frontmatter-coherence/<ISO8601>.json`, `--dry-run` mode, and receipt schema at `data/schemas/frontmatter_coherence_receipt.schema.json`.
- [ ] OBPI-0.0.16-04: Execute the chore once as dogfood backfill, attach reconciliation receipt as ADR evidence, verify `gz validate --frontmatter` post-run exits 0, close GHI #162/#167/#168/#169/#170 with `gh issue close` comments citing receipt path and ADR ID.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-04-17T05:00:00.695364*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.16

### Q: What is the title of this ADR?

**A:** Frontmatter-ledger coherence guard and chore audit

### Q: What is the semantic version?

**A:** 0.0.16

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** GHI-167

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** YAML frontmatter on ADR/OBPI files (id, parent, lane, status) is Layer 3 derived state — written as a side-effect of ledger events — but 13 code paths across 8 files consume it as if it were authoritative. With no guard gate or chore audit reconciling frontmatter against ledger truth, drift accumulates silently: 94.7% of sampled ADR status: fields (18/19) disagree with ledger lifecycle. The state-doctrine rule 'frontmatter is L3 derived state; read the ledger' (ADR-0.0.9; .gzkit/rules/constraints.md § State Doctrine) has no mechanical enforcement, so every consumer is a silent corruption vector. Operator-facing output (agent reads frontmatter → reports stale lifecycle) has already misled a design session (GHI #162 surface event, 2026-04-15, ADR-0.22.0). This ADR closes the governance cluster GHI #162, #167, #168, #169, #170 by adding the missing mechanical guard and automated reconciliation, not by rewriting the 13 consumer paths.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Build a frontmatter-ledger coherence guard, not per-consumer rewrites. The umbrella GHI #167 explicitly reframes the 13 consumer paths as acceptable cache reads once a guard exists; rewriting each consumer is speculative cleanup with no named failure mode the guard would not already catch.

**Four OBPIs decompose the decision:**

**OBPI-A — Guard function:** `gz validate --frontmatter` parses every ADR/OBPI file, compares id/parent/lane/status against the ledger's artifact graph, and emits a per-file per-field drift report in both human and --json modes. Scoped to the four governed fields; ignores ungoverned frontmatter (tags:, related:, etc.). Exit codes follow the CLI doctrine 4-code map (0 clean, 1 user error, 2 system error, 3 policy breach = drift found). Truth source must be the same API gz adr report uses for lifecycle so two derived views cannot diverge. Supports --adr <ID> single-file scope for fast iteration. Supports --explain <ADR-ID> that names the recovery command per drifted field (e.g. 'run gz adr promote … --lane heavy' or 'run gz chore run frontmatter-ledger-coherence').

**OBPI-B — Gate integration:** Wire the guard into gz gates (Gate 1 or Gate 2) so frontmatter drift blocks progression. Error messages name recovery commands and doc anchors; never suggest hand-editing frontmatter. Canonicalizes the status vocabulary to match the ledger state machine so frontmatter uses one canon (currently Draft/Proposed/Pending/Validated/Completed are used inconsistently). Canonicalization is documented as a sticky residue (see Consequences).

**OBPI-C — Chore registration:** config/chores/frontmatter-ledger-coherence.toml registers a chore with ledger-wins auto-fix, idempotent reconciliation semantics, receipt emission per run at artifacts/receipts/frontmatter-coherence/<timestamp>.json. Receipt includes the ledger cursor sampled and every file rewritten so 'drift was introduced between event N and M' is answerable. Supports --dry-run showing the per-field diff before any destructive write. Documented operator notes state frontmatter is derived and hand-edits lose on the next run.

**OBPI-D — One-time backfill + GHI closure:** Execute the chore once against the current repo (clears the 94.7% status: drift), attach the reconciliation receipt as evidence, and close GHI #162, #167, #168, #169, #170 with receipt reference in the closeout evidence and GH issue comments.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT rewrite the 13 consumer code paths listed in GHI #167 (register.py, common.py, status.py, status_obpi.py, adr_promote_utils.py, triangle.py, hooks/obpi.py, init_cmd.py). Those remain cache reads, now guarded.
- Does NOT add an event-time sync hook that rewrites frontmatter on every ledger write. Deferred as Alternative 4; revisit only if chore cadence proves insufficient.
- Does NOT remove frontmatter status: (Alternative 2 rejected — field remains a legitimate cache).
- Does NOT extend the ledger schema with path→id mapping unless OBPI-A discovers the graph lacks canonical paths. If it does, work pauses and a follow-on ADR scopes the schema extension before OBPI-A proceeds.

**Forcing-function stress tests applied during design:**

- **Pre-mortem:** 18 months out, failure modes include guard-as-friction-tax (teams bypass with --skip-frontmatter), destructive reconciliation of operator hand-edits, chore cadence never wired to CI, canonicalization breaking downstream tooling (mkdocs macros, vendor mirrors), ledger vocabulary drift forcing perpetual canonicalization-map updates, and scope narrowness moving corruption to an ungoverned field. Mitigations: no bypass flag, --dry-run required, receipt-first diagnosis, scoped to four governed fields with explicit policy for adding new ones.
- **WWHTBT:** Ledger writes are atomic (holds — append-only single-writer); guard fast enough at repo scale (holds at ~80 ADRs, shaky at 10x); four-field scope stable (**shakiest** — if governance adds fields frequently the guard becomes perpetual catch-up); ledger status state machine canonical (mostly holds per ADR-0.0.9); operators treat frontmatter as derived (culturally shaky — the chore's destructive behavior is a stick, operator-notes are the carrot).
- **Constraint archaeology:** 'Frontmatter is L3, ledger is L2' is real and codified (ADR-0.0.9, state-doctrine.md, constraints.md); last tested negatively in GHI #162 surface event 2026-04-15. Sub-constraint 'ledger derivation of current-state is correct' is inherited — guard must use the same API gz adr report uses or two views diverge.
- **Assumption surfacing:** Frontmatter id: reliably identifies artifact (FALSE — that's GHI #166; guard must key on filesystem path, not id:); ledger graph has canonical path field (unverified — may require schema extension; if so, pauses OBPI-A); ledger-wins is operator-acceptable (culturally untested). Opposite of core assumption — 'frontmatter is authoritative, ledger is derived' — holds during gz adr create and gz register-adrs (Layer 1 bootstrap) but not after. The guard runs at gate-time, preserving this distinction by timing rather than flag.
- **2am operator:** No bypass flag; --explain prints step-by-step remediation with recovery command; --dry-run shows per-field diff; --adr single-file scope; receipts at predictable path with ledger cursor for 'what changed since'; exit codes documented in --help; gate errors name the recovery command, never 'reconcile frontmatter' as prose.
- **Reversibility:** Guard and chore are two-way (single-file unwire, ~1hr each). One-time backfill leaves sticky residue (18 files' status: values rewritten; git history preserves the originals but cultural signal of 'ledger wins' is sent). Status-vocabulary canonicalization is also sticky. Recommendation: run chore without canonicalization first if operator confidence < 90% on canon.
- **Scope minimization:** Floor is OBPI-A + OBPI-D (standalone validator + one-time backfill); ship B+C in this ADR because they are tightly coupled (chore reuses validator, gate reuses chore's ledger-wins logic). Under time pressure, drop B then C; A+D alone closes GHI #162 and gives #167 a standalone validator.

**Downstream decisions forced by this ADR:**
1. Possible follow-on ADR for ledger schema extension if OBPI-A discovers graph lacks canonical-path field (touches append-only contract, needs state-doctrine review).
2. GHI #166 closure becomes tractable once the guard enforces id: coherence (small follow-up PR, not an ADR).
3. Event-time sync hook deferred as a later ADR if chore cadence proves insufficient in 12 months.
4. Status: vocabulary canonicalization policy as a short addendum to ADR-0.0.9 (state-doctrine), not a full new ADR.
5. Chore cadence policy — who runs it, how often, where receipts live — folds into the broader chores-cadence ADR if it exists, or a follow-on governance-maintenance ADR.

### Q: What good things result from this decision? List benefits.

**A:** 1. Mechanical enforcement of state-doctrine Layer 2 authority — the rule 'frontmatter is L3; read the ledger' moves from advisory prose to a gate-blocked check.
2. 13 consumer code paths become safe cache reads — no rewrite required; the guard closes GHI #168, #169, #170 architecturally per the umbrella's own reframing.
3. Drift becomes visible instead of silent — field-level diff (ledger value vs frontmatter value) turns a silent corruption vector into an inspectable report.
4. Ledger-wins reconciliation is idempotent and receipted — re-running the chore is safe; each run emits evidence consumable by audit.
5. One-time backfill clears the 94.7% status: drift as a byproduct of the first chore run (closes GHI #162) with no separate migration script.
6. Downstream confidence for GHI #166 — once the guard exists, orphan checks can trust id: because the guard enforces coherence.
7. Operator surface honesty restored — agents and humans inspecting frontmatter no longer receive stale lifecycle narration; the acute failure mode that motivated the cluster is closed.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. New gate surface expands CI latency — every gz gates invocation now parses all ADR/OBPI frontmatter and walks the ledger graph. Must stay sub-second at ~80 ADRs / ~200 OBPIs; budget check required as part of OBPI-A.
2. Ledger-wins reconciliation is destructive to frontmatter — hand-edits to status:/parent:/lane: vanish on the next chore run. Mitigation: document 'frontmatter is derived; edit the ledger via gz commands' in the chore's operator notes; log every overwrite in the reconciliation receipt.
3. The guard can false-block if the ledger graph is itself stale — e.g. if gz register-adrs hasn't run after ADR creation, the new ADR appears as drift. Mitigation: guard error messages must point to gz register-adrs / gz adr create as recovery, not suggest hand-editing frontmatter.
4. Frontmatter ambiguity when ledger has no equivalent — tags:, related:, and other ungoverned fields must be ignored by the guard or it false-positives on every file. Scope is explicitly the four governed fields id/parent/lane/status.
5. Chore cadence is a new operational concern — who runs it, how often, where receipts live. Mitigation: register the chore with a default cadence; integrate with gz tidy sweeps.
6. Status: vocabulary mismatch is wider than the guard alone solves — frontmatter uses Draft/Proposed/Pending/Validated/Completed inconsistently; the ledger has a canonical state machine. The guard must canonicalize frontmatter writes to match ledger vocabulary, not preserve the file's existing word. Risk: operators see an unfamiliar term appear after reconciliation.
7. Sticky residue from one-time backfill — git history preserves originals but operational workflow no longer sees them. Cultural signal 'ledger wins' becomes team convention, effectively a one-way door on the vocabulary choice.
8. Coupling of guard truth-source to gz adr report lifecycle derivation — if that derivation is itself wrong, the guard silently enforces wrong truth. Must share the same derivation API, not reimplement it.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Guard function: gz validate --frontmatter parses every ADR/OBPI file, compares four governed fields against ledger graph, emits per-file per-field drift report (human + JSON); --adr single-file scope and --explain remediation mode; exit codes per CLI doctrine 4-code map
2. Gate integration: wire guard into gz gates (Gate 1 or 2) so drift blocks progression; error messages name recovery commands and doc anchors; canonicalizes status vocabulary to ledger state machine
3. Chore registration: config/chores/frontmatter-ledger-coherence.toml with ledger-wins auto-fix, idempotent reconciliation, receipt emission per run including ledger cursor, --dry-run mode, operator notes on destructive-to-hand-edits behavior
4. One-time backfill and GHI closure: execute chore once against current repo, attach reconciliation receipt as evidence, close GHI #162, #167, #168, #169, #170 with receipt reference

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Per-consumer rewrite** — rewrite all 13 frontmatter-reading paths (register.py, common.py, status.py, status_obpi.py, adr_promote_utils.py, triangle.py, hooks/obpi.py, init_cmd.py) to query the ledger graph. Rejected: umbrella GHI #167 explicitly reframes those paths as acceptable caches once guarded; rewrite is a large speculative diff with no named failure mode the guard wouldn't already catch. The guard is a force-multiplier (one place to fix drift); consumer rewrites are not (each is an independent change).

2. **Remove frontmatter status: entirely** — eliminate the worst-offender field (94.7% drift). Rejected: the field is a legitimate cache for readers who want quick inspection without loading the ledger; removal breaks surface parity with doc/template tooling that consumes it. Keep the field; make it coherent via guard + chore.

3. **Manual one-time backfill only** — fix the 18 stale statuses once, no guard or chore. Rejected: drift would reappear the moment the next gate transitions. Without the guard, we would be back to ~95% drift within weeks. Fails the DO IT RIGHT maxim (6a — fix the class of failure, not the instance).

4. **Event-time sync hook** — every ledger event synchronously rewrites frontmatter at write time. Rejected as primary path, retained as potential follow-on: couples ledger write-path to filesystem mutation, adds failure points during gate transitions, complicates atomic testing. The chore + guard model keeps ledger writes atomic and reconciliation idempotent. Revisit only if chore cadence proves insufficient in operation.

5. **Defer the entire cluster** — wait for more drift evidence before investing. Rejected: the evidence already exists (94.7% drift rate, documented operator surface event in GHI #162), and the cluster of five GHIs represents coherent scope. Deferring leaves every consumer path as a silent corruption vector indefinitely.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Per-consumer rewrite** — rewrite all 13 frontmatter-reading paths (register.py, common.py, status.py, status_obpi.py, adr_promote_utils.py, triangle.py, hooks/obpi.py, init_cmd.py) to query the ledger graph. Rejected: umbrella GHI #167 explicitly reframes those paths as acceptable caches once guarded; rewrite is a large speculative diff with no named failure mode the guard wouldn't already catch. The guard is a force-multiplier (one place to fix drift); consumer rewrites are not (each is an independent change).

2. **Remove frontmatter status: entirely** — eliminate the worst-offender field (94.7% drift). Rejected: the field is a legitimate cache for readers who want quick inspection without loading the ledger; removal breaks surface parity with doc/template tooling that consumes it. Keep the field; make it coherent via guard + chore.

3. **Manual one-time backfill only** — fix the 18 stale statuses once, no guard or chore. Rejected: drift would reappear the moment the next gate transitions. Without the guard, we would be back to ~95% drift within weeks. Fails the DO IT RIGHT maxim (6a — fix the class of failure, not the instance).

4. **Event-time sync hook** — every ledger event synchronously rewrites frontmatter at write time. Rejected as primary path, retained as potential follow-on: couples ledger write-path to filesystem mutation, adds failure points during gate transitions, complicates atomic testing. The chore + guard model keeps ledger writes atomic and reconciliation idempotent. Revisit only if chore cadence proves insufficient in operation.

5. **Defer the entire cluster** — wait for more drift evidence before investing. Rejected: the evidence already exists (94.7% drift rate, documented operator surface event in GHI #162), and the cluster of five GHIs represents coherent scope. Deferring leaves every consumer path as a silent corruption vector indefinitely.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.16 | Pending | | | |
