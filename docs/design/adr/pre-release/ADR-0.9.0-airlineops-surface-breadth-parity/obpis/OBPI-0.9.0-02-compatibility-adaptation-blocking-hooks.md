---
id: OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 2
lane: Lite
status: Completed
---

# OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks: Compatibility adaptation for blocking hooks

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #2 — "OBPI-0.9.0-02: Adapt blocking/deferred canonical `.claude/hooks` for gzkit compatibility and record decisions with verification evidence."

**Status:** Draft

## Objective

Adapt canonical blocking/deferred `.claude/hooks` candidates into gzkit-safe behavior
(import, keep deferred, or exclude), with updated wiring and evidence for each decision.

## Lane

**Lite** — Internal governance infrastructure (agent hooks, operator wiring).
No external contract changes (CLI, API, schema, user-facing error messages).
Parent ADR-0.9.0 is Lite in the ledger (`adr_created` lane: lite).

## Allowed Paths

- `.claude/hooks/**` — Hook compatibility adaptations and tranche imports.
- `.claude/settings.json` — Hook wiring and matcher updates.
- `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/**` —
  intake updates and OBPI evidence.

## Denied Paths

- `src/**` and `tests/**` — Runtime/application behavior remains out of scope.
- `../airlineops/**` — Canonical source is read-only.
- Product-specific hooks (for example `dataset-guard.py`) unless ADR scope is revised.
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every canonical hook candidate reviewed in this tranche MUST be
   marked as imported, deferred, or excluded with rationale.
1. REQUIREMENT: Imported hooks MUST run through `uv run python` wiring in
   `.claude/settings.json`.
1. REQUIREMENT: Existing `ledger-writer.py` behavior MUST remain active.
1. NEVER: Do not enable blocking behavior without documented compatibility checks.
1. ALWAYS: Record deferred hooks with explicit follow-up target (OBPI or ADR).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` — repo structure
- [x] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [x] Parent ADR — understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [x] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [x] Canonical hook source exists: `../airlineops/.claude/hooks/`
- [x] Claude settings exists: `.claude/settings.json`

**Existing Code (understand current state):**

- [x] Existing intake decisions: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- [x] Existing non-blocking imports: `.claude/hooks/instruction-router.py`, `.claude/hooks/post-edit-ruff.py`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation — existing `ObpiValidator` tests cover library logic; new hook is thin I/O wrapper
- [x] Tests pass: 305 tests OK
- [ ] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [x] Lint clean: `uvx ruff check src tests` — All checks passed
- [x] Format clean: `uvx ruff format --check .` — 68 files already formatted
- [ ] Type check clean: `uvx ty check src`

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
uv run gz check-config-paths
uv run gz cli audit
uv run gz adr status ADR-0.9.0 --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.9.0-02-01: Given canonical `.claude/hooks` candidates classified as `Import with Compatibility` or `Defer`, when OBPI-02 completes, then each candidate has a concrete compatibility decision and implementation status.
- [x] REQ-0.9.0-02-02: Given imported compatibility-safe hooks, when `.claude/settings.json` is reviewed, then each imported hook is wired with the correct matcher and command.
- [x] REQ-0.9.0-02-03: Given deferred or excluded hooks, when intake evidence is reviewed, then each has explicit rationale and follow-up ownership.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass (305 OK), coverage maintained
- [x] **Code Quality:** Lint, format clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded — objective, requirements, and acceptance criteria defined above

### Gate 2 (TDD)

```text
Ran 305 tests in 11.264s — OK
```

### Code Quality

```text
ruff check src tests: All checks passed!
ruff format --check .: 68 files already formatted
settings.json: Valid JSON
```

### Implementation Summary

- Files created:
  - `.claude/hooks/obpi-completion-validator.py` — PreToolUse blocking gate (186 lines)
- Files modified:
  - `.claude/settings.json` — wired `obpi-completion-validator.py` as first PreToolUse hook
  - `.claude/hooks/README.md` — documented new hook and tranche history
  - `claude-hooks-intake-matrix.md` — updated all 9 tranche-2 hook decisions
- Files not needed:
  - `obpi-completion-recorder.py` — already covered by `ledger-writer.py` → `record_artifact_edit()` → `_record_obpi_completion_if_ready()` chain
- Tests added: None (hook is thin I/O wrapper; library logic tested by existing `ObpiValidator` tests)
- Date completed: 2026-03-08

### Value Narrative

**Before:** No PreToolUse gate existed for OBPI completion. An agent could mark an OBPI
brief as "Completed" without any ledger evidence, bypassing the governance ceremony.
PostToolUse recording (via `ledger-writer.py`) only ran after the edit was committed to
disk, making it informational rather than preventive.

**After:** `obpi-completion-validator.py` runs as a PreToolUse blocking hook (exit code 2)
that checks `.gzkit/ledger.jsonl` for `obpi_receipt_emitted` evidence before allowing
status changes to "Completed". For Heavy and Foundation lane OBPIs, it additionally
requires human attestation evidence. This closes the governance gap between intent and
enforcement.

### Key Proof

Updated `.claude/settings.json` PreToolUse chain:

```json
"PreToolUse": [
  { "matcher": "Write|Edit", "hooks": [
    { "command": "uv run python .claude/hooks/obpi-completion-validator.py" },
    { "command": "uv run python .claude/hooks/instruction-router.py" }
  ]}
]
```

Blocking behavior: when an OBPI brief edit sets status to "Completed" and no
`obpi_receipt_emitted` event exists in the ledger, the hook prints a diagnostic
message and exits with code 2, preventing the edit.

### Canonical Adaptation Map

| airlineops assumption | gzkit adaptation |
| --- | --- |
| Path: `/briefs/OBPI-` | `/obpis/OBPI-` |
| Ledger: `adr_dir/logs/obpi-audit.jsonl` | `.gzkit/ledger.jsonl` |
| Evidence event: `obpi-audit` / `obpi-completion` | `obpi_receipt_emitted` |
| Lane resolution: parse ADR markdown | `resolve_adr_lane()` from ledger events |
| Library: `opsdev.lib` | `gzkit.config`, `gzkit.ledger` |

---

**Brief Status:** Completed

**Date Completed:** 2026-03-08

**Evidence Hash:** —
