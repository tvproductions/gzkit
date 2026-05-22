---
id: OBPI-0.0.56-01-closeout-defect-baseline-snapshot
parent: ADR-0.0.56-closeout-defect-accounting-invariant
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.56-01-closeout-defect-baseline-snapshot: Closeout Defect Baseline Snapshot

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- **Checklist Item:** #1 - "OBPI-0.0.56-01: Closeout defect-baseline snapshot — extend `gz closeout` to run `gz check --json`, fingerprint the defect set, and emit a `closeout_defect_snapshot` ledger event; add the `CloseoutDefectSnapshot` frozen Pydantic model and the ledger event schema. Defect fingerprint = scope + predicate + structural location, excluding volatile fields."

**Status:** Draft

## Objective

Closeout defect-baseline snapshot — extend `gz closeout` to run `gz check --json`, fingerprint the defect set, and emit a `closeout_defect_snapshot` ledger event; add the `CloseoutDefectSnapshot` frozen Pydantic model and the ledger event schema. Defect fingerprint = scope + predicate + structural location, excluding volatile fields.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md` — parent ADR; READ reference for intent and the § Decision item 1 contract
- `src/gzkit/commands/closeout.py` — `gz closeout` command; the snapshot-emit site (alongside `_record_closeout_initiation`, line ~359, which already records the `closeout_initiated` event)
- `src/gzkit/events.py` — frozen Pydantic event models; add the `CloseoutDefectSnapshot` payload model and a `CloseoutDefectSnapshotEvent` class (sibling shape: `CloseoutInitiatedEvent`, line ~346)
- `src/gzkit/ledger_events.py` — event-factory functions; add a `closeout_defect_snapshot_event(...)` factory (sibling shape: `closeout_initiated_event`, line ~129)
- `src/gzkit/schemas/ledger.json` — ledger event schema; add the `closeout_defect_snapshot` event entry under `events` (sibling: the `closeout_initiated` entry)
- `tests/test_closeout_pipeline.py` — closeout command tests; add snapshot-emit and fingerprint-stability tests here
- `tests/governance/test_ledger_event_schema_coverage.py` — ledger event-schema coverage tests; the new event must be covered

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/validate_cmd.py`, `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/governance/trust_audits/` — the `gz validate --closeout-defect-accounting` reconcile scope is OBPI-02 scope
- `src/gzkit/governance/trust_audits/reconcile.py` — reconcile predicate belongs to OBPI-02
- `RoutingReceipt` model and the `gz closeout` fail-closed completion wiring — OBPI-03 scope (this OBPI only emits the snapshot; it does not gate completion)
- `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/obpi_stages.py` — OBPI-completion extension is OBPI-04 scope
- `.claude/hooks/`, `.gzkit/skills/ghi-close/` — ghi-close backstop is OBPI-05 scope
- `docs/governance/advisory-rules-audit.md`, `docs/user/runbook.md`, `docs/user/manpages/validate.md` — docs + scorecard reclassification is OBPI-06 scope
- Paths not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz closeout`, at the closeout-open anchor where it already records the `closeout_initiated` ledger event, MUST additionally run `gz check --json`, extract the structured defect set, and emit a new `closeout_defect_snapshot` ledger event in the same closeout-open transaction. NEVER emit the snapshot from a different ceremony verb or a side path.
2. REQUIREMENT: The `closeout_defect_snapshot` event payload MUST carry exactly `{closeout_id, defect_fingerprints, gz_check_invocation, captured_at}` — `closeout_id` linking the snapshot to its closeout, `defect_fingerprints` the diffable defect set, `gz_check_invocation` the args + sha of the `gz check` run, `captured_at` an ISO-8601 timestamp.
3. REQUIREMENT: The defect fingerprint MUST be a stable, diffable identity derived from scope + predicate + structural location ONLY. The fingerprint MUST exclude volatile fields — line numbers, run timestamps, result ordering — so the same defect produces an identical fingerprint across two `gz check` runs. This is the load-bearing risk named in the parent ADR § Consequences/Negative #1; it gets its own dedicated test.
4. REQUIREMENT: A `CloseoutDefectSnapshot` frozen Pydantic model (`model_config` frozen) MUST be added to `src/gzkit/events.py`, and the `closeout_defect_snapshot` event MUST be added to the `src/gzkit/schemas/ledger.json` `events` block. The model and the schema MUST agree on field names and types — schema/model drift is fail-closed by existing ledger-schema coverage tests.
5. REQUIREMENT: The `gz_check_invocation` field MUST record the actual `gz check` invocation (canonical full args + commit sha) so a downstream reconcile can reject a snapshot captured under a narrowed scope (parent ADR § Consequences/Negative #8, performative-snapshot risk).
6. REQUIREMENT: Before relying on `gz check --json` as the fingerprint source, the implementation MUST verify the `--json` payload shape is diffable — each defect carries a scope, a predicate, and a structural location distinguishable from volatile run metadata (parent ADR § Consequences/Negative #3a).
7. REQUIREMENT: This OBPI emits the snapshot ONLY. It MUST NOT add the reconcile predicate, the `RoutingReceipt` model, or any fail-closed completion gate — a `gz closeout` with no recorded snapshot still completes after this OBPI (the gate lands in OBPI-03). NEVER bundle OBPI-02/03 surfaces into this brief.
8. REQUIREMENT: Work MUST stay inside the Allowed Paths; NEVER touch `.gzkit/ledger.jsonl` directly — ledger writes go through the event factory and `Ledger.append`.

> STOP-on-BLOCKERS: if `src/gzkit/commands/closeout.py`, `src/gzkit/events.py`, or `src/gzkit/schemas/ledger.json` is absent, or `gz check --json` does not emit structured output, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] `src/gzkit/commands/closeout.py` `_record_closeout_initiation` (line ~359) — sibling pattern for emitting a closeout-open ledger event
- [ ] `src/gzkit/events.py` `CloseoutInitiatedEvent` (line ~346) — sibling frozen-event-model shape
- [ ] `src/gzkit/ledger_events.py` `closeout_initiated_event` (line ~129) — sibling event-factory shape
- [ ] `src/gzkit/commands/quality.py` `check` (line ~331) — the `gz check --json` surface this OBPI captures from
- [ ] **Related OBPIs:** this OBPI is the load-bearing primitive — OBPI-02 reconciles against this snapshot, OBPI-03 wires the gate. Sequencing 01 → 02 → 03 (this is step 01).

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/**`
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

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_closeout_pipeline -v
uv run -m unittest tests.governance.test_ledger_event_schema_coverage -v
uv run gz check --json   # confirm the --json payload exposes scope/predicate/location per defect
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Open an ADR closeout — gz closeout now captures a defect baseline at the open anchor.
uv run gz closeout ADR-0.0.56 --dry-run

# Inspect the closeout_defect_snapshot event written to the ledger at closeout-open:
uv run python -c "import json; [print(json.dumps(json.loads(l), indent=1)) for l in open('.gzkit/ledger.jsonl') if json.loads(l).get('event') == 'closeout_defect_snapshot']"

# Confirm the fingerprint is stable across two gz check runs (volatile fields excluded):
uv run gz check --json > /tmp/check-a.json
uv run gz check --json > /tmp/check-b.json
# The defect fingerprints (scope + predicate + structural location) must match between runs.
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.56-01-01: Given an ADR closeout being opened by `gz closeout`, when the closeout-open anchor runs, then a `closeout_defect_snapshot` ledger event is emitted in the same transaction as the `closeout_initiated` event, carrying `{closeout_id, defect_fingerprints, gz_check_invocation, captured_at}`.
- [ ] REQ-0.0.56-01-02: Given the same defect surfaced by two separate `gz check --json` runs, when each defect is fingerprinted, then the two fingerprints are byte-identical — the fingerprint is derived from scope + predicate + structural location and excludes line numbers, timestamps, and result ordering.
- [ ] REQ-0.0.56-01-03: Given the new `closeout_defect_snapshot` event, when the ledger event-schema coverage tests run, then the `CloseoutDefectSnapshot` frozen Pydantic model and the `src/gzkit/schemas/ledger.json` event entry agree on field names and types with no drift.
- [ ] REQ-0.0.56-01-04: Given a `gz check` run captured into a snapshot, when the `gz_check_invocation` field is read, then it records the canonical full `gz check` args plus the commit sha, sufficient for a downstream reconcile to reject a narrowed-scope snapshot.
- [ ] REQ-0.0.56-01-05: Given this OBPI delivers only the snapshot, when `gz closeout` runs with no reconcile gate present, then the closeout still completes — no fail-closed completion condition is introduced by this OBPI (the gate is OBPI-03).

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

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
