---
id: OBPI-0.0.63-05-dual-runtime-collapse
parent: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
item: 5
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.63-05-01
    receipt_ids:
      - arb-step-unittest-11700c9918c44344b82419ec546b65c1
  - req_id: REQ-0.0.63-05-02
    receipt_ids:
      - arb-step-unittest-11700c9918c44344b82419ec546b65c1
  - req_id: REQ-0.0.63-05-03
    receipt_ids:
      - arb-step-unittest-11700c9918c44344b82419ec546b65c1
  - req_id: REQ-0.0.63-05-04
    receipt_ids:
      - arb-step-unittest-11700c9918c44344b82419ec546b65c1
---

# OBPI-0.0.63-05-dual-runtime-collapse: **dual-runtime-collapse** — `gz closeout --ceremony --attest` vs Step 7 pipeline emit identical ledger surfaces. The runtime engine is single source; `--attest` becomes an orchestration shortcut.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`
- **Checklist Item:** #5 - "OBPI-0.0.63-05: **dual-runtime-collapse** — `gz closeout --ceremony --attest` vs Step 7 pipeline emit identical ledger surfaces. The runtime engine is single source; `--attest` becomes an orchestration shortcut."

**Status:** Completed

## Objective

Collapse the transitional double-emit of the `attested` ledger surface (the interim state OBPI-0.0.63-01 explicitly created and deferred to here) so that one logical closeout produces exactly **one** `attested` event regardless of path. Today a ceremony-driven closeout emits `attested` **twice**: once by the ceremony at Step 6 (`closeout_ceremony.py:549`, the BI-3 gate's fresh-receipt pass-path) and again by the Step-7 closeout pipeline (`closeout.py:504`), even though the pipeline has *already consumed* the same operator verdict from ceremony state via `_consume_ceremony_attestation` (`closeout.py:213-231`, GHI #351). The two events carry identical `(status, reason, attester)` (the classifiers `_classify_attestation_verdict` and `_parse_ceremony_attestation_text` are mirrors; both attesters are `get_git_user()`), so the second is pure redundancy.

After this OBPI: when `_complete_closeout_pipeline` consumes a ceremony attestation (`consumed is not None`), it MUST NOT re-append the `attested` event — the ceremony's Step-6 emission is the single authoritative source. When there is **no** ceremony (`consumed is None`, the direct interactive `gz closeout <adr>` path), the pipeline remains the sole emitter and emits as today. The result: a ceremony-driven closeout and a direct closeout leave byte-identical ledger surfaces (modulo timestamps/event UUIDs) for the same logical closeout — BI-2 holds.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Non-Goals

> **Non-Goal — BI-2/BI-3 reconciliation: the surviving emitter is the ceremony, NOT the pipeline.** Read literally, BI-2's "`--attest` is an orchestration shortcut, never a parallel emitter" could tilt toward the *pipeline* being the single source and `--attest` not emitting at all. That reading is **foreclosed** by BI-3, which is already attested-completed under OBPI-0.0.63-01 and cannot be reopened here: BI-3's Step 6→7 gate (`_gate_attestation_boundary`) fail-closes unless a *fresh `attested` ledger event* for the current run exists, and `--attest` is the path that produces it (`closeout_ceremony.py:549`). Removing the ceremony's emission would break the BI-3 gate. OBPI-01's own non-goal note already fixed the collapse direction: *"Reuses the existing `attested` surface (BI-2: `--attest` is not a parallel emitter); the transitional double-emit with the Step-7 closeout (`closeout.py`) is collapsed by OBPI-0.0.63-05."* So **"runtime engine = single source"** resolves to the ceremony state machine (the CLI state machine Decision item 1 built); the **pipeline** is the path that stops re-emitting when it consumes a ceremony attestation. `--attest` is "never a parallel emitter" because after this fix it is the *sole* emitter for ceremony-driven closeouts — not running in parallel with the pipeline's emit.

> **Non-Goal — do NOT modify `closeout_ceremony.py`'s Step-6 emission.** The ceremony's `attested` emission at `closeout_ceremony.py:549` is the surviving single source and the BI-3 gate's expected receipt. Touching it reopens OBPI-0.0.63-01 (attested-completed). This OBPI's entire edit surface is the *pipeline* side: the `attested` re-emit in `_complete_closeout_pipeline`.

> **Non-Goal — do NOT change the `attested_event` schema or other closeout events.** The `closeout_initiated`, `gate_checked`, and `lifecycle_transition` events emitted by the pipeline have **no ceremony-side counterpart** — they are emitted once, by the pipeline, in both ceremony-driven and direct closeouts (Step 7 runs `gz closeout <adr>` either way). They are already path-identical and are out of scope. Only the duplicate `attested` is the divergence.

> **Non-Goal — no version-sync or audit behavior change.** `attested` is an idempotent boolean graph flag (`ledger.py:589-590`); `version_sync` reads the *latest* `attested` event (`commands/version_sync.py:200-207`) and the surviving ceremony event carries identical `status`/`by`; presence-based audit (`ledger.py:74` `_AUDIT_HUMAN_ATTESTATION_EVENTS`) is satisfied by exactly one event. Collapsing two→one changes none of these readers' observed state.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md` — parent ADR (read-only reference for Decision item 6 + BI-2)
- `src/gzkit/commands/closeout.py` — guard the `attested_event` re-emit in `_complete_closeout_pipeline` (line ~504) so it only fires when `consumed is None`; the consume branch (`consumed is not None`, lines 491-499) keeps the status/reason/text it already derives for the closeout form, minus the duplicate ledger append
- `tests/test_closeout_pipeline.py` — new `@covers`-decorated BI-2 parity tests (single-emit regression, ceremony-vs-direct surface equality, direct-path-still-emits guard)
- `data/behave_coverage_waivers.json` — **coupled-surface coherence (AGENTS.md 1a).** Add an in-progress behave waiver for REQ-01..04 deferred to ADR-0.0.63 closeout (sibling OBPI-01/03 pattern — REQs are unit-tested; REQ-04 is STRUCTURAL-FENCE proven by the parent ADR BI-2 entry).
- `tests/test_closeout_ceremony_consumption.py` — **coupled-surface coherence (AGENTS.md 1a, scope amendment).** Three GHI #351 consumption tests asserted the *pre-BI-2* contract (the pipeline emits the `attested` event from the consumed ceremony verdict). BI-2 moves that emission to the ceremony's single source, so these fixtures must model reality — seed the ceremony's Step-6 `attested` emission, then assert the pipeline consumes without re-prompting and without duplicating. The GHI #351 no-re-prompt contract is preserved; only the now-removed pipeline re-emit is updated.

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/closeout_ceremony.py` — the ceremony's Step-6 `attested` emission (line 549) is the surviving single source AND the BI-3 gate's expected receipt; modifying it reopens OBPI-0.0.63-01 (attested-completed). Read-only reference.
- `src/gzkit/events.py`, `src/gzkit/ledger.py`, `src/gzkit/ledger_events.py` — `attested_event` is reused as-is; no schema change
- `src/gzkit/commands/ceremony_data.py`, `src/gzkit/commands/ceremony_steps.py` — other OBPI surfaces
- `src/gzkit/commands/version_sync.py` — read-only reader; verified unchanged-by-design (Non-Goal)
- Paths not listed in Allowed Paths; new dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: When `_complete_closeout_pipeline` consumes a ceremony attestation (`_consume_ceremony_attestation` returns non-`None`), the pipeline MUST NOT append an `attested` event — the ceremony's Step-6 emission is the single authoritative source. Exactly one `attested` event lands per ceremony-driven logical closeout.
2. ALWAYS: When there is no ceremony attestation to consume (`consumed is None`, direct interactive `gz closeout <adr>`), the pipeline MUST still append exactly one `attested` event — it remains the sole emitter on the direct path. (Guards against over-correction that would drop attestation entirely.)
3. NEVER: Modify the ceremony's Step-6 `attested` emission (`closeout_ceremony.py:549`) or the `attested_event` schema — collapse is a pipeline-side suppression, not a ceremony-side or schema change. Reopening OBPI-01 / BI-3 is out of scope.
4. ALWAYS: A ceremony-driven closeout and a direct closeout MUST leave byte-identical ledger surfaces (modulo timestamps and event UUIDs) for the same logical closeout — the ordered set of `(event_type, status, attester)` tuples appended by the closeout MUST be equal across both paths.
5. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
6. ALWAYS: Reconcile the brief with the parent ADR (Decision item 6 + BI-2) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision item 6 (verbatim):** "Collapse dual-runtime paths. `gz closeout --ceremony --attest` and the Step 7 pipeline must emit identical ledger surfaces. The runtime engine is the single source; the `--attest` flag is an orchestration shortcut, not a parallel emitter." Anchored by **BI-2** (`## Boundary Invariants`, verbatim): "Single-runtime-engine ledger parity. `gz closeout --ceremony --next`, `gz closeout --ceremony --attest`, and the Step 7 pipeline emit byte-identical ledger surfaces for the same logical closeout; the runtime engine is the single source and `--attest` is an orchestration shortcut, never a parallel emitter. Spans OBPI-01 (state machine) and OBPI-05 (dual-runtime collapse)."
- [x] Parent ADR § Intent — closeout-runtime parity with `gz obpi pipeline`'s CLI state machine; ledger evidence (not agent claims) is the source of truth.
- [x] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [x] OBPI-0.0.63-01 (BI-2 co-anchor): its non-goal note names this collapse as OBPI-05's explicit scope and fixes the direction (keep ceremony emission, remove pipeline duplicate).
- [x] `closeout.py:474-559` `_complete_closeout_pipeline` (the consuming emitter); `closeout.py:213-231` `_consume_ceremony_attestation`; `closeout_ceremony.py:511-561` `_record_attestation` (the surviving emitter).

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `src/gzkit/commands/closeout.py`
- [x] Required path exists: `tests/test_closeout_pipeline.py`
- [x] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [x] `tests/test_closeout_pipeline.py` (attestation/ledger assertions) and `tests/test_closeout_ceremony_consumption.py` reviewed before implementation
- [x] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below. -->

<!-- Single-program, shell-less invocations only (BI-1): no &&, ||, |, ;, $(...), redirects. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_closeout_pipeline
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. The closeout ceremony
     walkthrough harvests this section (parser-validated; unregistered verbs are
     dropped) and re-executes it (OBPI-02) — must exit 0 and be shell-less (BI-1). -->

<!-- Demo runs the BI-2 parity test suite (exit 0, shell-less): it exercises the
     single-emit regression (one attested event per ceremony-driven closeout),
     the ceremony-vs-direct surface-equality assertion, and the direct-path
     still-emits guard. -->

```bash
uv run -m unittest tests.test_closeout_pipeline
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.63-05-01 [BEHAVIOR]: Given a ceremony-driven closeout where the operator has attested at Step 6 (so `_consume_ceremony_attestation` returns non-`None`), when the Step-7 pipeline `gz closeout <adr>` runs, then exactly **one** `attested` event for the ADR exists in the ledger afterward (the ceremony's Step-6 emission) — the pipeline does NOT append a second, collapsing the OBPI-01 transitional double-emit.
- [ ] REQ-0.0.63-05-02 [BEHAVIOR]: Given the same logical closeout run two ways — once ceremony-driven (`--attest` then pipeline) and once directly (`gz closeout <adr>` with no ceremony) — when each completes, then the ordered set of `(event_type, status, attester)` tuples the closeout appends is **equal** across both paths (byte-identical ledger surface modulo timestamps/UUIDs); the duplicate `attested` is the only prior divergence and is gone.
- [ ] REQ-0.0.63-05-03 [BEHAVIOR]: Given a direct interactive closeout with no ceremony state to consume (`consumed is None`), when `gz closeout <adr>` runs, then the pipeline still appends exactly one `attested` event — it remains the sole emitter on the direct path, so the collapse does not over-correct into dropping attestation.
- [ ] REQ-0.0.63-05-04 [STRUCTURAL-FENCE]: `gz closeout --ceremony --next`, `gz closeout --ceremony --attest`, and the Step 7 pipeline emit byte-identical ledger surfaces for the same logical closeout; the runtime engine (ceremony state machine) is the single source and `--attest` is never a parallel emitter alongside the pipeline. ADR-0.0.63 `## Boundary Invariants` BI-2, audited at ADR closeout.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


`uv run -m unittest tests.test_closeout_pipeline.TestDualRuntimeCollapseBI2` -> 3/3 pass. RED against the pre-fix code (`AssertionError: 2 != 1` — ceremony AND pipeline both emitted `attested` for one logical closeout); GREEN after the `if consumed is None:` guard in `_complete_closeout_pipeline` (exactly one `attested` per logical closeout; ceremony-driven path count == direct path count == 1). Receipts: arb-step-unittest-11700c9918c44344b82419ec546b65c1, arb-ruff-c2c4b0ef66104711a82b738d6e6d7557, arb-step-typecheck-cff7c9a20ce64671831765ec0d293ec9, arb-step-mkdocs-296f143046c74b74a28133211f23915f.

### Implementation Summary


- Files modified: src/gzkit/commands/closeout.py (guard `attested_event` re-emit with `if consumed is None`); tests/test_closeout_pipeline.py (TestDualRuntimeCollapseBI2 + `_count_attested`/`_seed_consumed_ceremony` helpers); tests/test_closeout_ceremony_consumption.py (coupled-surface fix — 3 GHI #351 fixtures now model the ceremony's Step-6 emission as the single source); data/behave_coverage_waivers.json (in-progress waiver REQ-01..04); this brief.
- Mechanism: `_complete_closeout_pipeline` appends the `attested` event only on the direct path (`consumed is None`). On the ceremony-consumed path the ceremony's Step-6 emission (closeout_ceremony.py:549) is the single authoritative source — collapsing the OBPI-01 transitional double-emit. BI-3 gate and the `attested_event` schema untouched.
- Tests added: TestDualRuntimeCollapseBI2 — REQ-01 (single-emit regression, RED 2!=1 → GREEN), REQ-02 (ceremony-vs-direct surface equality), REQ-03 (direct-path remains sole emitter).
- Date completed: 2026-05-29. Attestation status: operator-attested (g0, "attest completed").
- Scope notes: Allowed-Paths amended for coupled surfaces (consumption tests + behave waiver) per AGENTS.md 1a. REQ-04 STRUCTURAL-FENCE accepted-uncovered (BI-2, audited at ADR-0.0.63 closeout).

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Gate-5 human attestation (g0) for OBPI-0.0.63-05 dual-runtime-collapse, the BI-2 implementer of ADR-0.0.63: the Step-7 closeout pipeline (_complete_closeout_pipeline) no longer re-emits the `attested` ledger event when it consumes a ceremony attestation, collapsing the OBPI-01 transitional double-emit to the ceremony's single source while leaving the attested-locked BI-3 gate untouched. 3 REQ-derived tests green (TestDualRuntimeCollapseBI2); receipts arb-step-unittest-11700c9918c44344b82419ec546b65c1, arb-ruff-c2c4b0ef66104711a82b738d6e6d7557, arb-step-typecheck-cff7c9a20ce64671831765ec0d293ec9, arb-step-mkdocs-296f143046c74b74a28133211f23915f.
- Date: 2026-05-29

---

**Date Completed:** 2026-05-29

**Evidence Hash:** -
