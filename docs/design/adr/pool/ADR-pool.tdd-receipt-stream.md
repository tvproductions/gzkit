---
id: ADR-pool.tdd-receipt-stream
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: GHI-157
---

# ADR-pool.tdd-receipt-stream: Dedicated TDD RED/GREEN Receipt Stream

## Status

Pool

## Date

2026-04-18

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

TDD RED/GREEN observations are **governance events**, not QA-step outcomes. ARB step receipts (`src/gzkit/arb/`) encode `exit_status=0` as success and `exit_status=1` as failure; a TDD RED test that fails on first run is the *correct* outcome, and a test that passes on first run is the defect signal. ARB is therefore the wrong semantic home for RED evidence — using it pollutes `gz arb validate`, `gz arb advise`, and `gz arb patterns` with intentional failures that look like anti-patterns.

This ADR tracks the tooling half of GHI #157: a dedicated RED/GREEN receipt stream where Gate 2 TDD claims can be cited without conflating with ARB's failure semantics, and where the per-increment RED→GREEN chain is structurally auditable as a governance event sequence. The behavior half of GHI #157 (per-increment rhythm in rule text, test-dump and stop-and-ask anti-patterns in the canon) landed as a direct `fix(rules): ...` patch referencing this pool ADR; this ADR is the home for the tool/schema work that remains.

## Design Tensions

These are the key architectural questions to resolve during promotion:

| Tension | Option A | Option B |
|---------|----------|----------|
| **Receipt home** | First-class `tdd_red_observed` / `tdd_green_observed` ledger events (L2 governance proof in `.gzkit/ledger.jsonl`, paired by test-id + brief-id + timestamp, auditable via `gz` queries) | ARB extension: `gz tdd red|green` subcommands emit receipts tagged `kind=tdd_red\|tdd_green`; validator/advisor/patterns gain a kind-filter clause |
| **Pairing semantics** | Strict pairing — every RED must be followed by a matching GREEN (same test id, same REQ) before TDD coverage is credited; ledger rejects orphan RED beyond a TTL | Soft pairing — RED and GREEN are recorded but not gated; auditors compute pairing in post |
| **Test-id identity** | Fully-qualified test name (`tests.module.TestClass.test_method`) + source-file hash — robust but brittle across refactors | REQ identity via `@covers` — a RED is "a RED for REQ-X.Y.Z-NN-MM observed at time T," de-coupled from test-name renames |
| **CLI shape** | `gz tdd red <test-selector>` / `gz tdd green <test-selector>` — direct RED/GREEN verbs wrapping a test runner invocation | `gz tdd observe --expect red\|green <test-selector>` — one verb, expectation flag; allows future `--expect skip`, `--expect error` without new verbs |
| **Attestation integration** | Extend `.gzkit/rules/attestation-enrichment.md` receipt table with a TDD row citing ledger event IDs; Gate 2 claims MUST cite at least one paired RED→GREEN event per REQ | Advisory — ledger events are available for audit but not required at Gate 2 until a later increment |
| **Relationship to `gz task`** | TASK lifecycle transitions (`gz task start` → `gz task complete`) auto-emit the RED/GREEN envelope; operator cites the TASK, the ledger carries the pair | Decoupled — `gz tdd` is independent of `gz task` and can be used outside the TASK flow (ad-hoc experiments, exploratory TDD) |

## Potential OBPI Decomposition (Sketch)

1. Schema: `data/schemas/tdd_red_receipt.schema.json` and `tdd_green_receipt.schema.json` (or a single `tdd_observation.schema.json` with a `phase: red|green` field, depending on Option A/B resolution).
2. Ledger event types: `tdd_red_observed`, `tdd_green_observed` registered in the event-type registry, with pairing semantics enforced at write time or audited at query time per the tension resolution.
3. CLI surface: `gz tdd red` / `gz tdd green` (or `gz tdd observe`) with test-selector argument parsing, invocation of the underlying `unittest` runner, exit-code inversion for RED, receipt and ledger emission.
4. Attestation rule update: `.gzkit/rules/attestation-enrichment.md` gains a TDD receipt row; Gate 2 TDD claims cite paired ledger events; lane behavior (lite warn, heavy fail-closed) mirrors ARB.
5. `gz task` integration: TASK-scoped RED/GREEN pairing — `gz task complete` may require at least one paired pair per REQ the TASK claims to cover (Option A of the `gz task` tension).
6. Backfill strategy for historical GHIs: decide whether any existing attestations need retroactive TDD ledger events or whether the stream is forward-only from promotion.

## Dependencies

- ARB receipt corpus (`src/gzkit/arb/`) — reference implementation for the wrapper/emit pattern; TDD stream should share receipt-path conventions where sensible
- Ledger event-type registry — the home for the new event types (and the validator that ensures pairing)
- `gz task` / `gz covers` — the REQ-granular coverage graph TDD receipts must plug into
- `.gzkit/rules/tests.md` — the per-increment rhythm rule (landed under GHI #157 as the direct-fix half) that this tooling operationalizes
- `.gzkit/rules/attestation-enrichment.md` — the receipt table TDD events will extend

## Consequences (if promoted)

- New CLI verb group (`gz tdd`) — Heavy-lane trigger per `.gzkit/rules/cli.md`
- Two new ledger event types, with schema validation and pairing audit
- Attestation rule extension: Gate 2 TDD claims gain a dedicated receipt row
- `gz arb validate` / `gz arb advise` / `gz arb patterns` scope clarifies — ARB is QA-step receipts only; TDD evidence no longer muddies the ARB corpus
- Optional: `gz task complete` enforces paired RED→GREEN per claimed REQ
- Operator discipline shifts: per-increment RED→GREEN citation in commit bodies (the current workaround) is replaced by per-increment ledger event citation

## Origin

GHI #157 (2026-04-15), surfaced during the GHI-153/155/156 cycle where the agent executed test-dump theater (batch RED → batch GREEN) under the name of TDD, then the operator observed during ADR-0.25.0 closeout:

> *"TDD is along the way and you should not stop and ask me for every implementation... ARB may not be the best place to report RED. this would be an independent set of TDD emissions or just emissions out to the main ledger. This is certainly something you need to GHI now. You are exhibiting an improper TDD implementation - your behavior is a bug."*

The behavior half of GHI #157 landed 2026-04-18 as a direct `fix(rules): ...` patch updating `.gzkit/rules/tests.md`, `.gzkit/rules/attestation-enrichment.md`, and `src/gzkit/templates/agents.md` to codify the per-increment rhythm, flag the test-dump and stop-and-ask anti-patterns in the canon, and document the ARB-vs-TDD receipt-semantics gap. This pool ADR tracks the remaining tooling half; promotion awaits capacity behind the current committed ADR backlog.
