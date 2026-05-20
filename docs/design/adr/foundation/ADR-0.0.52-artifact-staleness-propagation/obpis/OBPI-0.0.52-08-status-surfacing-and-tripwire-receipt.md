---
id: OBPI-0.0.52-08-status-surfacing-and-tripwire-receipt
parent: ADR-0.0.52-artifact-staleness-propagation
item: 8
lane: Heavy
status: Draft
---

# OBPI-0.0.52-08-status-surfacing-and-tripwire-receipt: Status surfacing and tripwire receipt

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #8 — "Status surfacing — `gz status --table` Stale column; `gz state --json` `staleness_flags` payload; `explain-stale` read-only query verb; tripwire `arb` analytical receipt (samples `propagation_candidates_reviewed` events, measures `confirmed_unchanged`/`amended` clearance ratio, counts distinct ever-flagged artifacts)"

**Status:** Draft

## Objective

Surface staleness flags visibly across the read-only operator surfaces: `gz status --table` gains a Stale column; `gz state --json` gains a `staleness_flags` payload; a new read-only `explain-stale` query verb surfaces full detection signal per flag; an operational tripwire `arb` analytical receipt periodically measures (a) uniform-attestation patterns in `propagation_candidates_reviewed` (Tier 2 theatre detection), (b) `confirmed_unchanged`/`amended` clearance ratio (assumption-3 detection), (c) cumulative distinct ever-flagged artifact count (one-way-door cost metric).

## Lane

**Heavy** — Augments existing CLI verbs' output schemas, adds new read-only verb, adds a new `arb` analytical-receipt scope.

## Allowed Paths

- `src/gzkit/commands/status.py` — augment `--table` with Stale column
- `src/gzkit/commands/state.py` — augment `--json` with `staleness_flags` payload per artifact
- `src/gzkit/commands/adr_explain_stale_cmd.py` — **PRIMARY:** new read-only query verb
- `src/gzkit/cli/parser_governance.py` — register `explain-stale` subcommand under `gz adr`
- `src/gzkit/arb/staleness_tripwire.py` — **PRIMARY:** analytical receipt for theatre/assumption/one-way-door metrics
- `src/gzkit/arb/__init__.py` — register the new tripwire receipt
- `tests/governance/test_status_stale_column.py` — Stale column tests
- `tests/governance/test_state_staleness_flags.py` — `--json` payload tests
- `tests/governance/test_adr_explain_stale.py` — query verb tests
- `tests/governance/test_staleness_tripwire.py` — tripwire receipt tests (per metric)
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Detection algorithm (OBPI-03)
- Trigger wiring (OBPI-04)
- Validator scopes (OBPI-05)

## Creates These Files

- `src/gzkit/commands/adr_explain_stale_cmd.py` — **CREATE** new read-only query verb
- `src/gzkit/arb/staleness_tripwire.py` — **CREATE** analytical receipt for theatre/assumption/one-way-door metrics
- `tests/governance/test_status_stale_column.py` — **CREATE** Stale column tests
- `tests/governance/test_state_staleness_flags.py` — **CREATE** `--json` payload tests
- `tests/governance/test_adr_explain_stale.py` — **CREATE** query verb tests
- `tests/governance/test_staleness_tripwire.py` — **CREATE** tripwire receipt tests

Existing files modified: `src/gzkit/commands/status.py`, `src/gzkit/commands/state.py`, `src/gzkit/cli/parser_governance.py`, `src/gzkit/arb/__init__.py`.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz status --table` MUST add a `Stale` column showing the count of unresolved `evaluation_stale` entries per artifact (with a visible warning indicator when count > 0).
2. REQUIREMENT: `gz state --json` MUST include `staleness_flags: list[StalenessEntry]` per artifact payload (empty list when artifact has no unresolved entries).
<!-- gz-validate-skip: command-shape -->
3. REQUIREMENT: `explain-stale <artifact-id> [--upstream <upstream-id>]` MUST be a read-only query verb (no side effects, no ledger writes) that prints each unresolved entry's `detection_signal`, `upstream_id`, `flagged_at`, `source`, `attested_by` (when present), `upstream_event_id`, in human-readable form. `--json` variant supported.
4. REQUIREMENT: Status surfaces and the explain verb MUST NOT cause `--adr-eval-fresh` fail-close (they are read-only; OBPI-05 already enforces this).
5. REQUIREMENT: The `arb` analytical tripwire MUST sample recent `propagation_candidates_reviewed` events over a rolling window (default: last 30 days, configurable) and report: (a) uniform-attestation pattern frequency (count of events where promote/reject reasons exhibit copy-paste-suspect uniformity), (b) `confirmed_unchanged`/`amended` clearance ratio (from `artifact_staleness_cleared` events), (c) distinct count of artifacts that have ever carried an `evaluation_stale` entry.
6. REQUIREMENT: The tripwire MUST emit as a standard `gz arb` analytical receipt (existing arb framework); does NOT gate work. Receipt format: structured JSON conforming to existing arb schema.
7. REQUIREMENT: Status surfaces MUST honor `.claude/rules/cli.md` Output Contracts — `--table` is human-readable Rich rendering; `--json` is grep-friendly machine output; both surfaces share the same underlying staleness data.
8. REQUIREMENT: Read-only surfaces MUST NOT panic on stale-flag drift (Layer 1 vs Layer 2 mismatch); they surface what they see and rely on `--staleness-coherence` (OBPI-05) for fail-closed drift detection.

> STOP-on-BLOCKERS: if `gz status --table` rendering format is unclear, read the existing implementation before authoring the new column.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"Status surfacing — `gz status --table` Stale column; `gz state --json` `staleness_flags` payload; `explain-stale` read-only query verb; tripwire `arb` analytical receipt"*.
- [ ] Parent ADR § Decision / "2am operational discipline" — `explain-stale` shape.
- [ ] Parent ADR § Decision / "Tier 2 anti-theatre defenses" — tripwire metric definitions.
- [ ] Parent ADR § Consequences/Negative items 4, 6, 8 — the three metrics' rationale (theatre, one-way-door cost, assumption #3 detectability).

**Governance:**

- [ ] `.claude/rules/cli.md` § Output Contracts — table/JSON discipline.
- [ ] `AGENTS.md` § Attestation — canonical `gz arb step` invocations.

**Prerequisites:**

- [ ] OBPI-0.0.52-02 (Pydantic models including `StalenessEntry`, `ArtifactStalenessClearedEvent`) has landed.
- [ ] OBPI-0.0.52-04 (events emittable) has landed.
- [ ] OBPI-0.0.52-07 (Tier 2 emitting `propagation_candidates_reviewed`) has landed for the tripwire's source data — though the tripwire MUST handle the case where no Tier 2 events exist yet (degraded reporting, not failure).

**Existing Code:**

- [ ] `src/gzkit/commands/status_cmd.py` reviewed for Rich table-column conventions.
- [ ] Existing `gz arb` analytical-receipt examples reviewed for receipt-format conventions.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from brief acceptance criteria
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] BDD scenarios pass (full coverage in OBPI-09)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz status --table
uv run gz state --json | head -30
uv run -m unittest tests.governance.test_status_stale_column tests.governance.test_state_staleness_flags tests.governance.test_adr_explain_stale tests.governance.test_staleness_tripwire -v
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# Stale column visible in status table
uv run gz status --table | head -20

# Staleness flags in state JSON
uv run gz state --json > /tmp/gz-state.json
python -c "import json; data=json.load(open('/tmp/gz-state.json')); print(json.dumps({k:v.get('staleness_flags',[]) for k,v in data.items() if v.get('staleness_flags')}, indent=2))"

# Read-only explain query
uv run gz adr explain-stale ADR-0.0.B
uv run gz adr explain-stale ADR-0.0.B --upstream ADR-0.0.A --json

# Tripwire analytical receipt
uv run gz arb step --name staleness-tripwire -- gz arb staleness-tripwire --window 30d
```

## Acceptance Criteria

- [ ] REQ-0.0.52-08-01: Given an artifact with N unresolved `evaluation_stale` entries, when `gz status --table` runs, then the Stale column displays N (with a warning indicator when N > 0).
- [ ] REQ-0.0.52-08-02: Given the same artifact, when `gz state --json` runs, then its payload includes `staleness_flags: [<N entries>]` matching the frontmatter.
- [ ] REQ-0.0.52-08-03: Given a flagged artifact, when `explain-stale <id>` runs, then it prints each unresolved entry with full detection_signal/upstream/flagged_at/source/upstream_event_id; exit 0.
- [ ] REQ-0.0.52-08-04: Given `explain-stale <id> --json`, when invoked, then output is a list of `StalenessEntry` objects.
- [ ] REQ-0.0.52-08-05: Given a flagged artifact, when ANY read-only command (`gz status`, `gz state`, `explain-stale`) runs, then `--adr-eval-fresh` does NOT fire (no exit 3).
- [ ] REQ-0.0.52-08-06: Given a 30-day window of `propagation_candidates_reviewed` events, when the tripwire receipt runs, then it reports (a) uniform-attestation pattern count, (b) `confirmed_unchanged`/`amended` clearance ratio, (c) distinct ever-flagged artifact count.
- [ ] REQ-0.0.52-08-07: Given the tripwire receipt, when no Tier 2 events exist in the window, then it reports degraded ("no Tier 2 data in window") rather than failing.
- [ ] REQ-0.0.52-08-08: Given the new `explain-stale` subcommand, when `gz adr --help` runs, then `explain-stale` is listed with a canonical example.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, type checks clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** included

## Evidence

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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before: a flagged artifact was invisible in operator workflows except via `gz validate` fail-close at advance time; there was no surface to query why a flag existed, and no way to detect Tier 2 theatre / assumption-3 failure / one-way-door cost growth. Now: every read-only surface shows staleness flags visibly, `explain-stale` is the 2am query verb, and the tripwire receipt surfaces operational drift before it ossifies.

### Key Proof

<!-- gz-validate-skip: command-shape -->
```bash
$ uv run gz status --table | head -10
                    Foundation ADRs
╭──────────────────────────┬─────────┬─────┬───────────┬───────┬───────╮
│ADR                       │Lifecycle│Lane │Status     │QC     │ Stale ┃
├──────────────────────────┼─────────┼─────┼───────────┼───────┼───────┤
│ADR-0.0.B                 │Pending  │HEAVY│IN_PROGRESS│PENDING│  1 ⚠  │
╰──────────────────────────┴─────────┴─────┴───────────┴───────┴───────╯

$ uv run gz adr explain-stale ADR-0.0.B
ADR-0.0.B carries 1 unresolved evaluation_stale entry:
  upstream: ADR-0.0.A
  flagged_at: 2026-05-19T01:00:00Z
  source: mechanical
  detection_signal: declared_edge:cites
  upstream_event_id: a1b2c3d4...
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
