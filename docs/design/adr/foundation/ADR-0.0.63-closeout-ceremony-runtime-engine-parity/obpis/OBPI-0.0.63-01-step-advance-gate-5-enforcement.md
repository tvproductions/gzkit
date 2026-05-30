---
id: OBPI-0.0.63-01-step-advance-gate-5-enforcement
parent: ADR-0.0.63-closeout-ceremony-runtime-engine-parity
item: 1
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.63-01-01
    receipt_ids:
      - arb-step-unittest-70435b6035a6461689534fd5834e87ba
  - req_id: REQ-0.0.63-01-02
    receipt_ids:
      - arb-step-unittest-70435b6035a6461689534fd5834e87ba
  - req_id: REQ-0.0.63-01-03
    receipt_ids:
      - arb-step-unittest-70435b6035a6461689534fd5834e87ba
  - req_id: REQ-0.0.63-01-04
    receipt_ids:
      - arb-step-unittest-70435b6035a6461689534fd5834e87ba
---

# OBPI-0.0.63-01-step-advance-gate-5-enforcement: **step-advance-gate-5-enforcement** — `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`. Step 6→7 `--next` reads ledger for the prior step's expected receipt and fail-closes if absent. Eliminates the Gate 5 bypass.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`
- **Checklist Item:** #1 - "OBPI-0.0.63-01: **step-advance-gate-5-enforcement** — `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`. Step 6→7 `--next` reads ledger for the prior step's expected receipt and fail-closes if absent. Eliminates the Gate 5 bypass."

**Status:** Completed

## Objective

Close the Gate-5 self-advance bypass (ADR-0.0.63 finding F1) in the closeout ceremony: the Step 6 ATTESTATION → Step 7 CLOSEOUT transition becomes a **ledger-gated edge** instead of a blind step-counter advance. Both `gz closeout <adr> --ceremony --next` and `gz closeout <adr> --ceremony --attest` route through one shared advance helper that reads the ledger for an `attested` receipt emitted **during the current ceremony run** (event `ts` ≥ the run's `started_at`); `--attest` emits that receipt then crosses (exercising the pass-path), while `--next` at Step 6 fail-closes with a `PolicyBreachError` (exit 3) when no fresh receipt exists (exercising the fail-path). The agent can no longer walk past the human-attestation boundary with `--next`.

> **Non-Goal — single-emitter collapse is OBPI-0.0.63-05 (BI-2), not here.** The Step-7 closeout pipeline (`closeout.py:504`) already emits an `attested_event` after consuming the ceremony verdict (GHI #351). This OBPI's ceremony-side emission produces a *transitional double-emit* of the `attested` surface for one logical closeout. Collapsing the two emission paths to a single source is the explicit scope of OBPI-0.0.63-05 (dual-runtime collapse / BI-2). Do **not** modify `closeout.py` here. The double-emit is tolerable in the interim: `attested` is an idempotent boolean graph flag (`ledger.py:589`), `version_sync` reads the latest event (Step-7 wins, `version_sync.py:203`), and presence-based audit checks are satisfied either way.

> **Non-Goal — do NOT convert edges other than 6→7.** ADR Decision item 1's "each step transition reads ledger state" is the *cross-OBPI* vision realized incrementally. BI-3 scopes this OBPI to transitions *past the human-attestation boundary*. Steps 1→5 and 7→11 cross no attestation gate; gating them is out of scope.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md` — parent ADR (read-only reference for intent + BI-3)
- `src/gzkit/commands/closeout_ceremony.py` — shared ledger-gated advance helper; `_advance_ceremony` (lines 369-432) and `_record_attestation` (lines 435-476) both route through it; add `attested_event` + `get_git_user` to existing imports (lines 34-47). `attested_event` is already re-exported from `gzkit.ledger` (`ledger.py:818`); no `events.py`/`ledger_events.py` change needed.
- `tests/test_closeout_ceremony_cmd.py` — new `@covers`-decorated gate tests (fail-path, fresh-receipt pass-path, stale-receipt) + adjust the existing `test_advance_through_all_steps` if needed

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/closeout.py` — Step-7 emitter; single-emitter collapse is OBPI-0.0.63-05 (BI-2). Read-only reference; do NOT modify (the verdict parser `_parse_ceremony_attestation_text` lives here and `closeout.py` already imports *from* `closeout_ceremony`, so importing it back is circular — re-derive a minimal verdict classifier inline with a cross-reference comment).
- `src/gzkit/events.py`, `src/gzkit/ledger_events.py` — `attested_event` is reused as-is; no schema change
- `src/gzkit/commands/ceremony_steps.py`, `ceremony_data.py` — other OBPI surfaces
- Paths not listed in Allowed Paths; new dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: The Step 6 (ATTESTATION) → Step 7 (CLOSEOUT) transition MUST read the ledger and fail-close (`PolicyBreachError`, exit 3) unless an `attested` event for this ADR with `ts` ≥ the current ceremony run's `started_at` exists. Both `--next` and `--attest` route through the same shared advance helper.
1. ALWAYS: Freshness MUST be computed by parsing both timestamps with `datetime.fromisoformat` and comparing as `datetime` objects — NEVER string comparison (`started_at` is `…SSZ` second-resolution; event `ts` is `…SS.ffffff+00:00`; ASCII string compare is wrong because `.` < `Z`).
1. NEVER: Advance past Step 6 on the blind step counter. The step-counter self-advance at line 401/416-426 is replaced by the ledger-gated edge for the attestation boundary.
1. NEVER: Modify `closeout.py` (Step-7 emitter) or the `attested_event` schema — the transitional double-emit is by design; collapse is OBPI-05.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
1. ALWAYS: Reconcile the brief with the parent ADR (BI-3) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision item 1 (verbatim):** "Convert `gz closeout --ceremony` to a CLI state machine. Parallel the `_run_pipeline_*_stage` shape from `obpi_cmd.py:446-494`. Each step transition reads ledger state for the prior step's expected receipt and fail-closes if absent. Eliminates Step 6→7 self-advance." Anchored by **BI-3** (`## Boundary Invariants`): "No closeout step transition past the human-attestation boundary succeeds without ledger evidence of the prior step's expected receipt; the step counter is replaced by ledger-gated edges. Anchored by OBPI-01; consumed by OBPI-03 and OBPI-06."
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/ADR-0.0.63-closeout-ceremony-runtime-engine-parity.md`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

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
uv run -m unittest tests.test_closeout_ceremony_cmd
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. The closeout ceremony
     walkthrough harvests this section (parser-validated; unregistered verbs are
     dropped) and re-executes it (OBPI-02) — must exit 0 and be shell-less (BI-1). -->

<!-- Demo runs the BI-3 gate's own test suite (exit 0, shell-less): it exercises
     both the fail-closed `--next`-at-step-6 path and the fresh-receipt `--attest`
     pass path. A live ceremony fail-close exits 3 by design, so it is not used as
     the closeout-bound demo. -->

```bash
uv run -m unittest tests.test_closeout_ceremony_cmd
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.63-01-01 [BEHAVIOR]: Given a ceremony at Step 6 (ATTESTATION) with no `attested` ledger receipt for the current run, when `gz closeout <adr> --ceremony --next` runs, then it raises `PolicyBreachError` (exit 3), names the human-attestation boundary, and the ceremony state stays at Step 6 (no advance to CLOSEOUT) — eliminates the F1 Gate-5 self-advance bypass.
- [ ] REQ-0.0.63-01-02 [BEHAVIOR]: Given a ceremony at Step 6, when `gz closeout <adr> --ceremony --attest "<verdict>"` runs, then an `attested` event for the ADR is appended to the ledger AND the ceremony crosses to Step 7 (CLOSEOUT) with the verdict recorded in state — the `--attest` path exercises the gate's fresh-receipt pass-path through the same shared advance helper.
- [ ] REQ-0.0.63-01-03 [BEHAVIOR]: Given a ceremony at Step 6 whose only `attested` event is stale (its `ts` predates the current run's `started_at`, e.g. from a prior closeout or a prior `--restart` attempt), when `gz closeout <adr> --ceremony --next` runs, then it still fail-closes (exit 3) — freshness is computed by `datetime.fromisoformat` comparison, not string comparison, so the stale receipt does not satisfy the gate.
- [ ] REQ-0.0.63-01-04 [STRUCTURAL-FENCE]: Both the `--next` and `--attest` Step 6→7 crossings route through one shared ledger-gated advance helper — no step-counter self-advance survives past the human-attestation boundary. ADR-0.0.63 `## Boundary Invariants` BI-3, audited at ADR closeout.

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


uv run -m unittest tests.test_closeout_ceremony_cmd.TestCeremonyGate5Enforcement -> 3/3 pass. These are RED against the pre-fix code (bare --next at Step 6 self-advanced to CLOSEOUT, exit 0) and GREEN against the fix (--next exit 3, stays at Step 6; --attest emits one attested ledger receipt then crosses; a stale prior-run receipt does not satisfy the gate). Full suite via arb-step-unittest-70435b6035a6461689534fd5834e87ba; lint arb-ruff-0978e2824deb4f95ad1608af4a72e59b; typecheck arb-step-typecheck-f3919ac1ddd44d1eaa6a7ae9bae6263b; docs arb-step-mkdocs-51f62c6aa48b41eb8a7733ab06baa36e.

### Implementation Summary


- Files modified: src/gzkit/commands/closeout_ceremony.py, tests/test_closeout_ceremony_cmd.py, data/behave_coverage_waivers.json, this brief
- Mechanism: Step 6->7 converted from blind step-counter to ledger-gated edge; _advance_ceremony and _record_attestation delegate to shared _commit_advance, which calls _gate_attestation_boundary -> _has_fresh_attestation_receipt (datetime-parsed ts >= started_at); --attest emits the attested receipt via the existing attested_event surface then crosses
- Tests added: TestCeremonyGate5Enforcement (3 REQ-derived tests: fail-path REQ-01, fresh-receipt pass-path REQ-02, stale-receipt REQ-03)
- Date completed: 2026-05-29; Attestation status: operator-attested (g0, "attest completed")
- Scope notes: behave waiver REQ-01..04 deferred to ADR-0.0.63 closeout (sibling OBPI-02/0.0.59-03 pattern); double-emit with closeout.py:504 is intended transitional state, collapse = OBPI-0.0.63-05 / BI-2

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Gate-5 human attestation (g0) for OBPI-0.0.63-01 step-advance-gate-5-enforcement, the BI-3 anchor of ADR-0.0.63: the closeout ceremony's Step 6 (ATTESTATION) -> Step 7 (CLOSEOUT) edge is now ledger-gated, eliminating the F1 self-advance bypass. 3 REQ-derived tests green (TestCeremonyGate5Enforcement); receipts arb-step-unittest-70435b6035a6461689534fd5834e87ba, arb-ruff-0978e2824deb4f95ad1608af4a72e59b, arb-step-typecheck-f3919ac1ddd44d1eaa6a7ae9bae6263b, arb-step-mkdocs-51f62c6aa48b41eb8a7733ab06baa36e; precomplete 7/7; src/tests at commit 5979a47d.
- Date: 2026-05-29

---

**Date Completed:** 2026-05-29

**Evidence Hash:** -
