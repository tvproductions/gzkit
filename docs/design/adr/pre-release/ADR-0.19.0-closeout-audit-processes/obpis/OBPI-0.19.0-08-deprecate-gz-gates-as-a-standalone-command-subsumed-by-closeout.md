---
id: OBPI-0.19.0-08-deprecate-gz-gates-as-a-standalone-command-subsumed-by-closeout
parent: ADR-0.19.0-closeout-audit-processes
item: 8
lane: Lite
status: Draft
---

# OBPI-0.19.0-08: Deprecate `gz gates` as Standalone Command (Subsumed by Closeout)

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #8 — "Deprecate `gz gates` as a standalone command (subsumed by closeout)"

**Status:** Draft

## Objective

Add a deprecation warning to `gates_cmd()` in `src/gzkit/cli.py` so that when operators invoke `gz gates` directly, they see a clear message directing them to `gz closeout` which now orchestrates gate execution as part of the closeout pipeline. The gate runner functions (`_run_gate_1` through `_run_gate_5`) remain intact for internal consumption by `closeout_cmd()` and `audit_cmd()`. The command docs in `docs/user/commands/gates.md` are updated to reflect the deprecation.

## Lane

**Lite** — No new CLI subcommands, flags, or output schemas. The `gz gates` command continues to function but emits a deprecation warning to stderr. Gate runner internals are unchanged. This is an internal housekeeping change that points operators toward the consolidated closeout workflow.

## Allowed Paths

- `src/gzkit/cli.py` — `gates_cmd()` function (around line 2305) to add deprecation warning at entry
- `docs/user/commands/gates.md` — update command documentation with deprecation notice
- `tests/test_gates_deprecation.py` — new test verifying deprecation warning is emitted

## Denied Paths

- `src/gzkit/commands/` — gate runner functions `_run_gate_1` through `_run_gate_5` must not be removed or altered
- `src/gzkit/cli.py` gate handler dict and runner logic — must remain functional
- `.gzkit/manifest.json` — gate configuration unchanged
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gates_cmd()` MUST emit a deprecation warning to stderr on every invocation before executing gates.
1. REQUIREMENT: The deprecation warning MUST include the text "deprecated" and reference `gz closeout` as the replacement.
1. REQUIREMENT: After emitting the warning, `gates_cmd()` MUST continue to execute gates normally (not a hard removal).
1. REQUIREMENT: The `_run_gate_1` through `_run_gate_5` functions MUST remain unchanged and callable by other commands (closeout, audit).
1. REQUIREMENT: `docs/user/commands/gates.md` MUST include a deprecation notice at the top of the document.
1. NEVER: Remove the `gz gates` command registration or its Click/Typer decorator — the command must still be invocable.
1. NEVER: Alter the exit codes or gate execution behavior — only the warning is added.
1. ALWAYS: Use `console.print("[yellow]...[/yellow]", ...)` or `warnings.warn()` for the deprecation message consistent with existing gzkit patterns.

> STOP-on-BLOCKERS: if `gates_cmd` is not present in `src/gzkit/cli.py`, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`

**Context:**

- [ ] `src/gzkit/cli.py` lines 2305-2354 — `gates_cmd()` current implementation
- [ ] `src/gzkit/cli.py` lines 2494-2632 — `closeout_cmd()` which subsumes gate execution
- [ ] `docs/user/commands/gates.md` — current command documentation

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/cli.py` exists with `gates_cmd()` function
- [ ] `docs/user/commands/gates.md` exists

**Existing Code (understand current state):**

- [ ] Pattern to follow: existing deprecation patterns in the codebase (search for "deprecated" in cli.py)
- [ ] Test patterns: `tests/test_lifecycle.py` for test structure conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [ ] REQ-0.19.0-08-01: Given an operator invokes `gz gates`, when the command starts, then a deprecation warning containing "deprecated" and "gz closeout" is printed to stderr before gate execution begins.
- [ ] REQ-0.19.0-08-02: Given an operator invokes `gz gates --gate 2`, when the command completes, then Gate 2 executes normally and produces the same exit code and ledger events as before the deprecation.
- [ ] REQ-0.19.0-08-03: Given `closeout_cmd()` calls `_run_gate_1` through `_run_gate_5` internally, when closeout runs, then no deprecation warning is emitted (only `gates_cmd` entry point triggers the warning).
- [ ] REQ-0.19.0-08-04: Given `docs/user/commands/gates.md`, when an operator reads the documentation, then a deprecation notice is visible at the top stating the command is subsumed by `gz closeout`.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_gates_deprecation -v

# Manual check: run gz gates and observe deprecation warning
uv run gz gates --help
```

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

## Value Narrative

**Before:** `gz gates` runs as a standalone command with no indication that it has been subsumed by `gz closeout`. Operators use two separate commands (`gz gates` then `gz closeout`) creating confusion about the canonical workflow and risking incomplete closeout procedures.

**After:** `gz gates` prints a clear deprecation warning on every invocation directing operators to `gz closeout`, while continuing to function for backward compatibility. The command docs reflect the deprecation, guiding new operators to the consolidated pipeline from the start.

## Key Proof

```bash
# After implementation:
$ uv run gz gates --adr ADR-0.19.0
[yellow]Deprecated:[/yellow] `gz gates` is deprecated and will be removed in a future release.
Use `gz closeout ADR-0.19.0` instead, which runs gates as part of the closeout pipeline.

[bold]Gate 1 (ADR):[/bold] ...
[bold]Gate 2 (TDD):[/bold] ...
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

- Attestor: `n/a` (Lite lane — self-closeable after evidence)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
