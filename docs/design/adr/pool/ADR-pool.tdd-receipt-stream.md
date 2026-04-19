---
id: ADR-pool.tdd-receipt-stream
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: GHI-157
amendments:
  - date: 2026-04-19
    scope: Generalized from TDD-only receipt stream to governance-event receipt stream (TDD RED/GREEN retained as inaugural kind). Motivated by /insights session surfacing ARB coverage gap (33 receipts across 341 hours of work); the structural "ARB-unsafe" property applies to every governance event whose semantics are not expressible as a command exit code, not only to TDD RED.
---

# ADR-pool.tdd-receipt-stream: Governance-Event Receipt Stream (inaugural kind: TDD RED/GREEN)

## Status

Pool

## Date

2026-04-18 (original) / 2026-04-19 (scope generalization — see Amendment History)

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

TDD RED/GREEN observations are **governance events**, not QA-step outcomes. ARB step receipts (`src/gzkit/arb/`) encode `exit_status=0` as success and `exit_status=1` as failure; a TDD RED test that fails on first run is the *correct* outcome, and a test that passes on first run is the defect signal. ARB is therefore the wrong semantic home for RED evidence — using it pollutes `gz arb validate`, `gz arb advise`, and `gz arb patterns` with intentional failures that look like anti-patterns.

This ADR tracks the tooling half of GHI #157: a dedicated RED/GREEN receipt stream where Gate 2 TDD claims can be cited without conflating with ARB's failure semantics, and where the per-increment RED→GREEN chain is structurally auditable as a governance event sequence. The behavior half of GHI #157 (per-increment rhythm in rule text, test-dump and stop-and-ask anti-patterns in the canon) landed as a direct `fix(rules): ...` patch referencing this pool ADR; this ADR is the home for the tool/schema work that remains.

### Generalization (2026-04-19 amendment)

TDD RED/GREEN is the **inaugural kind** of a broader structural gap: governance events whose semantics are not expressible as a command exit code are ARB-unsafe for the same reason RED is. The `/insights` 2026-04-19 session supplied the quantitative evidence — **33 ARB receipts across 341 hours of work / 197 sessions**. The tooling is blind to every governance event that is not a lint/type/test/coverage/docs invocation. Session intent framing (MODE), plan-mode transitions, pipeline-stage boundaries, hook blocks and resolutions, scope-boundary decisions, and defect-routing judgments are all structurally ARB-unsafe: they have no command, no exit code, no stdout/stderr — only a governance fact. Without a receipt home, they live as narrative in commit bodies and session transcripts, which gzkit doctrine (`.gzkit/rules/attestation-enrichment.md`, citing Lindsey et al. 2025 — narrative recall and execution are structurally separate pathways) already rejects as unreliable.

This ADR therefore tracks a **generalized governance-event receipt stream** with TDD RED/GREEN as the first registered kind. Each additional kind carries its own schema, CLI emit path, and pairing semantics; the stream shape (ledger event, schema-validated, queryable via `gz`) is shared. The **tool/behavior split** from the original scope is preserved per-kind — this ADR is the tooling home; behavioral doctrine for each non-TDD kind routes to that kind's parent ADR (see § Governance-Event Kinds).

## Governance-Event Kinds

The kinds below share the "ARB-unsafe, receipt-worthy" property. Each stays in the pool (or routes to its parent ADR) until promoted; this list is the registry source-of-truth. Each kind's **behavioral half** lives in its parent ADR; this ADR owns only the shared tooling (stream, schema, emit, ledger events).

| Kind events | Semantics | Pairing | Parent ADR (behavioral half) |
|---|---|---|---|
| `tdd_red_observed` / `tdd_green_observed` | Per-increment TDD observation; RED must fail on first run, GREEN succeeds with minimal code | Strict or soft (see Design Tensions — inaugural tension set) | This ADR (inaugural kind; behavior-half already landed in `tests.md`, `attestation-enrichment.md`, `agents.md` per GHI #157) |
| `mode_declared` / `mode_resolved` | Session/skill-invocation intent framing: `READ-ONLY`, `PLAN-FIRST`, `IMPLEMENT`; resolved at scope-check or session end | Declaration↔resolution pair; action outside declared MODE is the invariant violation | `ADR-pool.agent-execution-intelligence` (CAP-08 Graduated Deviation Rules — MODE is the per-invocation surface) |
| `plan_mode_entered` / `plan_mode_exited` | Plan-mode transitions (native tool or skill-driven); captures plan scope claim at entry and evidence at exit | Enter↔exit pair | `ADR-pool.harness-aware-execution-modes` (Mode 2 hooks observe transitions) |
| `pipeline_stage_entered` | OBPI pipeline stage transition (0 → 5); captures stage, OBPI ID, and stage-evidence hash | Sequential, not strictly paired (terminal stage = completion) | `ADR-pool.gz-preflight-health-orchestration` (stage 0 = preflight) |
| `hook_blocked` / `hook_resolved` | PreToolUse/PostToolUse hook blocked an action; resolution records either the corrective edit or an explicit override | Block↔resolution pair; unresolved block beyond TTL is a governance defect | `ADR-pool.harness-aware-execution-modes` (Mode 2 hook authority) |
| `scope_widened` / `scope_narrowed` | Operator or `defect-fix-routing.md` applied a scope adjustment to in-flight work (adjacent-file defect absorb, brief-boundary honor, etc.) | Each event self-contained; audited as a sequence across the session | `ADR-pool.skill-behavioral-hardening` (circuit breakers consume the sequence) |
| `defect_routed` | Direct-fix vs. OBPI-ceremony routing decision, with the threshold facts (diff size, scope, precedent count) that drove it | Self-contained | `.gzkit/rules/defect-fix-routing.md` (canonical thresholds; ADR-less rule home) |

**Registration contract for a kind:** (a) schema exists under `data/schemas/<kind>_receipt.schema.json`; (b) CLI emit path is documented (per-kind verb or `gz event emit --kind <kind>` generic per the tension resolution); (c) the kind's parent ADR is promoted, OR this ADR is promoted with the kind in scope. The registry lives in the ledger event-type registry (§ Dependencies).

## Design Tensions

These are the key architectural questions to resolve during promotion. The first six tensions are **TDD-inaugural** (they were authored against the RED/GREEN case; they remain unresolved and are not pre-resolved by the 2026-04-19 generalization). The last three are **cross-kind** (added by the 2026-04-19 amendment; they govern how the stream accommodates kinds beyond TDD).

| Tension | Option A | Option B | Scope |
|---------|----------|----------|-------|
| **Receipt home** | First-class `tdd_red_observed` / `tdd_green_observed` ledger events (L2 governance proof in `.gzkit/ledger.jsonl`, paired by test-id + brief-id + timestamp, auditable via `gz` queries) | ARB extension: `gz tdd red|green` subcommands emit receipts tagged `kind=tdd_red\|tdd_green`; validator/advisor/patterns gain a kind-filter clause | TDD-inaugural |
| **Pairing semantics** | Strict pairing — every RED must be followed by a matching GREEN (same test id, same REQ) before TDD coverage is credited; ledger rejects orphan RED beyond a TTL | Soft pairing — RED and GREEN are recorded but not gated; auditors compute pairing in post | TDD-inaugural |
| **Test-id identity** | Fully-qualified test name (`tests.module.TestClass.test_method`) + source-file hash — robust but brittle across refactors | REQ identity via `@covers` — a RED is "a RED for REQ-X.Y.Z-NN-MM observed at time T," de-coupled from test-name renames | TDD-inaugural |
| **CLI shape** | `gz tdd red <test-selector>` / `gz tdd green <test-selector>` — direct RED/GREEN verbs wrapping a test runner invocation | `gz tdd observe --expect red\|green <test-selector>` — one verb, expectation flag; allows future `--expect skip`, `--expect error` without new verbs | TDD-inaugural |
| **Attestation integration** | Extend `.gzkit/rules/attestation-enrichment.md` receipt table with a TDD row citing ledger event IDs; Gate 2 claims MUST cite at least one paired RED→GREEN event per REQ | Advisory — ledger events are available for audit but not required at Gate 2 until a later increment | TDD-inaugural |
| **Relationship to `gz task`** | TASK lifecycle transitions (`gz task start` → `gz task complete`) auto-emit the RED/GREEN envelope; operator cites the TASK, the ledger carries the pair | Decoupled — `gz tdd` is independent of `gz task` and can be used outside the TASK flow (ad-hoc experiments, exploratory TDD) | TDD-inaugural |
| **Kind-registry extensibility** | Closed — the kind enum is frozen at promotion; new kinds require this ADR's amendment or a follow-on ADR. Stronger audit surface, slower kind onboarding. | Open — the kind enum is an append-only registry; new kinds register via schema + parent-ADR reference without amending this ADR. Faster onboarding, weaker enum discipline. | Cross-kind (2026-04-19) |
| **Cross-kind pairing uniformity** | Each kind defines its own pairing semantics (TDD = RED↔GREEN, MODE = declaration↔resolution, plan = enter↔exit, stage = sequential). Schemas per kind; audit logic per kind. | Uniform pair schema across kinds (`paired_with_event_id` field, pairing-rule enum declared in the per-kind schema). Shared audit query shape; higher schema-design burden. | Cross-kind (2026-04-19) |
| **Emit CLI shape across kinds** | Per-kind verbs: `gz tdd red\|green`, `gz mode declare\|resolve`, `gz pipeline stage enter`, `gz hook blocked\|resolved`, etc. Ergonomic per kind; proliferating verb surface. | Generic verb: `gz event emit --kind <kind> --payload <json>` with per-kind thin wrappers where ergonomics justify. One-verb CLI contract; kind-specific flags become payload keys. | Cross-kind (2026-04-19) |

## Potential OBPI Decomposition (Sketch)

Items 1–6 are the TDD-inaugural decomposition (original scope); items 7–10 are added by the 2026-04-19 generalization and are contingent on the resolution of the cross-kind tensions above.

1. Schema: `data/schemas/tdd_red_receipt.schema.json` and `tdd_green_receipt.schema.json` (or a single `tdd_observation.schema.json` with a `phase: red|green` field, depending on Option A/B resolution).
2. Ledger event types: `tdd_red_observed`, `tdd_green_observed` registered in the event-type registry, with pairing semantics enforced at write time or audited at query time per the tension resolution.
3. CLI surface: `gz tdd red` / `gz tdd green` (or `gz tdd observe`) with test-selector argument parsing, invocation of the underlying `unittest` runner, exit-code inversion for RED, receipt and ledger emission.
4. Attestation rule update: `.gzkit/rules/attestation-enrichment.md` gains a TDD receipt row; Gate 2 TDD claims cite paired ledger events; lane behavior (lite warn, heavy fail-closed) mirrors ARB.
5. `gz task` integration: TASK-scoped RED/GREEN pairing — `gz task complete` may require at least one paired pair per REQ the TASK claims to cover (Option A of the `gz task` tension).
6. Backfill strategy for historical GHIs: decide whether any existing attestations need retroactive TDD ledger events or whether the stream is forward-only from promotion.
7. **Event-kind registry** (generalization): typed enum or append-only registry per the "Kind-registry extensibility" tension; each entry records kind name, schema path, parent ADR, pairing rule, CLI emit path. Lives in the ledger event-type registry (§ Dependencies).
8. **Schemas for non-TDD inaugural kinds**: `mode_declared/resolved`, `plan_mode_entered/exited`, `pipeline_stage_entered`, `hook_blocked/resolved`, `scope_widened/narrowed`, `defect_routed`. Each under `data/schemas/<kind>_receipt.schema.json`; each referenced by the kind registry. Per-kind OBPIs may land incrementally as parent ADRs promote, rather than all in one wave.
9. **Generic `gz event emit`**: resolves the "Emit CLI shape across kinds" tension. Wraps (or is wrapped by) per-kind verbs depending on the chosen option. Ergonomic verbs may still exist for TDD and MODE; other kinds default to the generic verb until ergonomics justify otherwise.
10. **Behavioral-ADR consumer integration**: each dependent ADR (agent-execution-intelligence, skill-behavioral-hardening, session-productivity-metrics, gz-preflight-health-orchestration, harness-aware-execution-modes) adds a short integration OBPI on its own promotion — wiring its governance facts into the stream using the kind registry. This ADR does not pre-land those integrations; it declares the surface they plug into.

## Dependencies

**Original (TDD-inaugural):**

- ARB receipt corpus (`src/gzkit/arb/`) — reference implementation for the wrapper/emit pattern; TDD stream should share receipt-path conventions where sensible. **Not a competitor**: ARB continues to own QA-step receipts; this stream owns governance events whose semantics are not exit-coded.
- Ledger event-type registry — the home for the new event types (and the validator that ensures pairing)
- `gz task` / `gz covers` — the REQ-granular coverage graph TDD receipts must plug into
- `.gzkit/rules/tests.md` — the per-increment rhythm rule (landed under GHI #157 as the direct-fix half) that this tooling operationalizes
- `.gzkit/rules/attestation-enrichment.md` — the receipt table TDD events will extend

**Added by the 2026-04-19 generalization (each is a *consumer* — this ADR supplies the stream, the consumer supplies the kind's behavioral half):**

- `ADR-pool.agent-execution-intelligence` — CAP-08 (Graduated Deviation Rules) wires MODE declarations into the stream as `mode_declared`/`mode_resolved` kinds
- `ADR-pool.skill-behavioral-hardening` — circuit breakers emit `scope_widened`/`scope_narrowed` and consume the sequence for anti-rationalization audits
- `ADR-pool.session-productivity-metrics` — aggregation view over the stream; moves from proposing a parallel `session-metrics.jsonl` to reading from the unified ledger event stream
- `ADR-pool.gz-preflight-health-orchestration` — emits `pipeline_stage_entered` for stage 0 (preflight) and each subsequent stage transition
- `ADR-pool.harness-aware-execution-modes` — Mode 2 hook authority emits `hook_blocked`/`hook_resolved` and observes `plan_mode_entered`/`plan_mode_exited`
- `.gzkit/rules/defect-fix-routing.md` — supplies the payload shape for `defect_routed` events (threshold facts: diff size, scope, precedent count)

## Consequences (if promoted)

**Original (TDD-inaugural):**

- New CLI verb group (`gz tdd`) — Heavy-lane trigger per `.gzkit/rules/cli.md`
- Two new ledger event types, with schema validation and pairing audit
- Attestation rule extension: Gate 2 TDD claims gain a dedicated receipt row
- `gz arb validate` / `gz arb advise` / `gz arb patterns` scope clarifies — ARB is QA-step receipts only; TDD evidence no longer muddies the ARB corpus
- Optional: `gz task complete` enforces paired RED→GREEN per claimed REQ
- Operator discipline shifts: per-increment RED→GREEN citation in commit bodies (the current workaround) is replaced by per-increment ledger event citation

**Added by the 2026-04-19 generalization:**

- **Event-kind registry becomes a first-class governance surface.** Future behavioral ADRs reference the registry rather than inventing parallel per-ADR receipt stores; the receipt-doctrine (`attestation-enrichment.md`) applies uniformly.
- **`session-productivity-metrics` becomes a read view.** The two-ADR structure (stream + metrics) collapses the proposed parallel `session-metrics.jsonl` into a metrics read over the unified ledger stream.
- **Narrative `/insights` reports become receipt-grounded.** The current 33-receipts-over-341-hours ratio (the evidence that motivated the generalization) closes as behavioral events flow into the stream; future insights runs can cite receipts instead of reconstructing narrative.
- **Cross-vendor parity gains a structural anchor.** Any harness that emits events with the shared schema participates in the same audit surface, which is the substrate `ADR-pool.harness-aware-execution-modes` needs for Mode-1/Mode-2 observability parity.
- **Pool-dependency reshuffling.** Four consumer pool ADRs (`agent-execution-intelligence`, `skill-behavioral-hardening`, `session-productivity-metrics`, `gz-preflight-health-orchestration`) each gain an integration OBPI on their own promotion; promotion ordering should sequence this ADR (or its equivalent tooling) first, since consumers depend on the stream existing.

## Origin

GHI #157 (2026-04-15), surfaced during the GHI-153/155/156 cycle where the agent executed test-dump theater (batch RED → batch GREEN) under the name of TDD, then the operator observed during ADR-0.25.0 closeout:

> *"TDD is along the way and you should not stop and ask me for every implementation... ARB may not be the best place to report RED. this would be an independent set of TDD emissions or just emissions out to the main ledger. This is certainly something you need to GHI now. You are exhibiting an improper TDD implementation - your behavior is a bug."*

The behavior half of GHI #157 landed 2026-04-18 as a direct `fix(rules): ...` patch updating `.gzkit/rules/tests.md`, `.gzkit/rules/attestation-enrichment.md`, and `src/gzkit/templates/agents.md` to codify the per-increment rhythm, flag the test-dump and stop-and-ask anti-patterns in the canon, and document the ARB-vs-TDD receipt-semantics gap. This pool ADR tracks the remaining tooling half; promotion awaits capacity behind the current committed ADR backlog.

---

## Amendment History

### 2026-04-19 — Scope generalization (TDD-only → governance-event stream)

**Motivation.** The `/insights` 2026-04-19 session surfaced the following evidence:

- ARB receipts scanned: **33** across **341 hours** of work / **197 sessions** (2026-03-20 → 2026-04-19).
- The behavioral friction classes named by the insights report (scope drift, rogue implementation, MODE misreading, hook blocks, defect routing) produce **zero** ARB receipts.
- gzkit doctrine (`.gzkit/rules/attestation-enrichment.md`, citing Lindsey et al. 2025) already rejects narrative reconstruction as unreliable — narrative-reporting and execution pathways are structurally separate circuits. The doctrine applies to non-TDD governance events as forcefully as to QA events, but the tooling is blind to them.
- The same structural property that makes ARB the wrong home for TDD RED (exit-code semantics inverted from correctness) also makes ARB unable to home *any* governance event without a command-shaped outcome.

**What the amendment preserves.** Every load-bearing element of the original scope:

- The ARB-pollution argument (ARB exit-code semantics misaligned with RED correctness) remains the motivating concrete example.
- All six original Design Tensions remain unresolved and are now explicitly labeled *TDD-inaugural*; none is pre-resolved by the generalization.
- All six original OBPI sketch items remain verbatim; generalization adds items 7–10 and labels them *contingent on the cross-kind tensions*.
- The original Dependencies and Consequences are preserved; added entries are in separately labeled subsections.
- The tool/behavior split is preserved *per-kind*: this ADR is the tooling home for every registered kind; the behavioral half of each non-TDD kind routes to that kind's parent ADR (see § Governance-Event Kinds).
- The inaugural kind remains "TDD RED/GREEN" in the title; the ADR ID is unchanged to preserve all existing references.

**What the amendment adds.**

- A new § Governance-Event Kinds registry with seven kinds and their parent ADRs.
- Three new cross-kind Design Tensions (kind-registry extensibility, cross-kind pairing uniformity, emit CLI shape across kinds).
- Four new OBPI sketch items (event-kind registry, non-TDD schemas, generic `gz event emit`, consumer-ADR integration).
- Six consumer Dependencies and five consequences specific to generalization.

**Tracking.** A follow-on GHI will be filed to index this amendment once `ADR-pool.adr-amendment-tracking` is promoted; until then, this section is the amendment record of record. Cross-references in the consumer ADRs (the five "consumer" entries added to § Dependencies) should be added in those ADRs' own amendment cycles — this ADR does not mutate them.
