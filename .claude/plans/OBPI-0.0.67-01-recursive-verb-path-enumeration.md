# Plan: OBPI-0.0.67-01-recursive-verb-path-enumeration

**OBPI:** OBPI-0.0.67-01-recursive-verb-path-enumeration
**Parent ADR:** ADR-0.0.67-tool-skill-invariant1-enforcement
**Lane:** Heavy

## Context

The `_known_cli_verb_paths`, `_verb_path_waived`, `_waiver_targets_live_verb`, and
rewritten `audit_skill_alignment` functions are **already implemented** in the working
tree (per ADR-0.0.67 § Decision item 1 "Status: already implemented"). OBPI-02 (wiring)
and OBPI-03 (deletion) have both landed (status: Completed).

What is missing: `@covers` decorators and 3 new tests for REQ-0.0.67-01-02 through
REQ-0.0.67-01-04. REQ-0.0.67-01-01 has a matching test
(`test_skill_alignment_enumerates_multiword_subcommands`) but lacks a `@covers` decorator.

## Files

- `tests/governance/test_promoted_advisory_audits.py` — all test changes land here

## Steps

### Step 1: Add @covers(REQ-0.0.67-01-01) to existing test

Add `@covers("REQ-0.0.67-01-01")` decorator to
`PromotedAdvisoryAudits.test_skill_alignment_enumerates_multiword_subcommands`.

The test already asserts:
1. `_known_cli_verb_paths()` includes `"obpi complete"`, `"adr status"`, `"obpi lock claim"`
2. `audit_skill_alignment(_PROJECT_ROOT)` is clean

These cover REQ-0.0.67-01-01: "Given the registered CLI tree, when
`_known_cli_verb_paths()` runs, then it returns space-joined leaf paths recursing into
nested subparsers."

### Step 2: Add test_skill_alignment_non_vacuous (REQ-0.0.67-01-02)

Add `@covers("REQ-0.0.67-01-02")` decorated test to `PromotedAdvisoryAudits`.

Strategy: patch `_known_cli_verb_paths` to return the real set plus one synthetic
unwaived/unwired path `"fake synthetic audit-test-verb"`. Call `audit_skill_alignment`.
Assert exactly one `skill_alignment` error fires whose `artifact` equals
`"gz fake synthetic audit-test-verb"`.

This proves the audit is non-vacuous: an unwielded, unwaived multi-word verb produces
exactly one `skill_alignment` error.

### Step 3: Add test_skill_alignment_cascade_and_stale (REQ-0.0.67-01-03)

Add `@covers("REQ-0.0.67-01-03")` decorated test that exercises `_verb_path_waived` and
`_waiver_targets_live_verb` directly:

- `_verb_path_waived("task")` → True (exact key in `_NO_SKILL_VERBS`)
- `_verb_path_waived("task start")` → True (group cascade: "task" prefix matches)
- `_verb_path_waived("nonexistent")` → False (not in `_NO_SKILL_VERBS`)
- `_waiver_targets_live_verb("task", frozenset(["task start", "task complete"]))` → True
- `_waiver_targets_live_verb("orphan", frozenset(["task start"]))` → False
- audit_skill_alignment on live tree has no stale `_NO_SKILL_VERBS` entries (the
  stale-waiver check is covered by `test_skill_alignment_invariant_1` but we assert
  no stale type explicitly here)

### Step 4: Add test_skill_alignment_cli_verbs_top_level_only (REQ-0.0.67-01-04)

Add `@covers("REQ-0.0.67-01-04")` decorated test asserting:

- `_known_cli_verbs()` returns a frozenset where no token contains a space (top-level
  only, not the recursive set)
- `audit_cli_alignment(_PROJECT_ROOT)` returns no errors (cli-alignment unchanged)

### Step 5: Start tasks, verify RED→GREEN, run quality gates

For each REQ, start a task via `gz task start --req REQ-0.0.67-01-NN --seq next`.

Run `uv run -m unittest tests/governance/test_promoted_advisory_audits.py -v` after
adding each @covers/test to observe RED (before decorator) then GREEN (after).

Run full quality suite:
- `uv run gz arb ruff`
- `uv run gz arb typecheck`
- `uv run gz arb step --name unittest -- uv run -m unittest -q`

Verify `uv run gz validate --skill-alignment` and `uv run gz validate --cli-alignment`
both pass.

Run `uv run gz covers OBPI-0.0.67-01-recursive-verb-path-enumeration --json` to confirm
all 4 REQs show `covered: true`.

## Verification

```bash
uv run gz validate --skill-alignment
uv run gz validate --cli-alignment
uv run -m unittest discover -s tests -t . -p test_promoted_advisory_audits.py
uv run gz lint
uv run gz typecheck
```

## Notes

- Implementation is pre-existing; no `src/gzkit/` edits are expected.
- `@covers` decorator import already present in the test file (`from gzkit.traceability import covers`).
- Denied path: `_known_cli_verbs()` semantics — must NOT be altered.
- Sequencing: OBPI-02 + OBPI-03 confirmed Completed before this plan.
