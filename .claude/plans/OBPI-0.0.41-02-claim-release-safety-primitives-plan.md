# Plan: OBPI-0.0.41-02-claim-release-safety-primitives

## Context

**OBPI:** OBPI-0.0.41-02-claim-release-safety-primitives
**Parent ADR:** ADR-0.0.41-token-block-lock-discipline (foundation, Heavy lane)
**Objective:** Close the check-then-write race in OBPI lock claiming via exclusive-creation; introduce `--abandon <category>:<reason>` flag for degenerate-handoff writing on `gz obpi lock release`; emit warning when release proceeds without a register entry (staging window for OBPI-03's fail-closed flip).

**Key Constraints:**
- All work confined to ALLOWED PATHS in the brief
- `--abandon` categories are a closed enum from `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1
- Release semantics remain WARNING-ONLY in OBPI-02 (still succeed without handoff/abandon)
- `obpi_lock_released_event` payload gains optional `handoff_path: str | None = None` field; backward-compatible
- 9 BEHAVIOR/SUPPORT REQs must each have a `@covers`-decorated test

**Files to Create/Modify:**
- `src/gzkit/lock_manager.py` — `write_lock` rewritten to exclusive-creation (`open(path, "x")`)
- `src/gzkit/commands/obpi_lock.py` — claim conflict handling, --abandon flag, degenerate-handoff writer
- `src/gzkit/cli/parser_artifacts.py` — register --abandon argument on lock release parser
- `src/gzkit/ledger_events.py` — extend obpi_lock_released_event with optional handoff_path
- `src/gzkit/content/models/handoff.py` — optional abandoned/category/reason fields if not present
- `src/gzkit/handoff_validation.py` — --abandon category validator
- `docs/user/manpages/obpi-lock-release.md` — document --abandon flag
- `docs/user/manpages/obpi-lock-claim.md` — document claim-conflict exit code
- `tests/test_lock_manager.py` — exclusive-creation tests
- `tests/test_obpi_lock_cmd.py` — claim conflict and release --abandon tests
- `tests/governance/test_token_block_discipline.py` — degenerate-handoff, warning behavior, category validation tests

## Implementation Steps

### 1. Read Current Implementation (TDD RED baseline)

- [ ] Read `src/gzkit/lock_manager.py:write_lock` (lines 118-129) — understand current `path.write_text()` race
- [ ] Read `src/gzkit/commands/obpi_lock.py:obpi_lock_claim_cmd` (lines 29-89) — the check-then-write window (lines 40-64)
- [ ] Read `src/gzkit/commands/obpi_lock.py:obpi_lock_release_cmd` (lines ~200+) — current release flow
- [ ] Read `src/gzkit/ledger_events.py:obpi_lock_released_event` (line 354) — current payload shape
- [ ] Read `src/gzkit/content/models/handoff.py` — current handoff model
- [ ] Examine `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1 for the closed abandon-category enum

**Precondition:** `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1 MUST name the closed category enum (network_loss, external_blocker, wrong_obpi_claimed, tool_failure). STOP if missing.

### 2. TDD RED: Write Tests Before Implementation

Write tests RED (all fail before code change) in this order:

#### 2a. Race-condition tests (REQ-01, REQ-02, REQ-03)

- [ ] `tests/test_lock_manager.py::test_write_lock_exclusive_creation_raises_on_second_call` — calls `write_lock` twice on same path; second call MUST raise `FileExistsError`
- [ ] `tests/test_obpi_lock_cmd.py::test_claim_handles_file_exists_error_as_conflict` — obpi_lock_claim_cmd catches `FileExistsError`; returns `conflict` exit 1
- [ ] `tests/test_obpi_lock_cmd.py::test_claim_race_exactly_one_winner` — two concurrent claim attempts; exactly one succeeds, one fails with conflict

All tests use `@covers(REQ-0.0.41-02-0N)` decorator.

#### 2b. --abandon flag parsing tests (REQ-04, REQ-06)

- [ ] `tests/test_obpi_lock_cmd.py::test_release_parses_abandon_flag` — `--abandon network_loss:reason` parses; colon delimiter validated; whitespace rejected
- [ ] `tests/governance/test_token_block_discipline.py::test_release_abandon_rejects_unregistered_category` — `--abandon unknown_category:reason` exits 1 with enum list in stderr

#### 2c. Degenerate-handoff tests (REQ-05)

- [ ] `tests/governance/test_token_block_discipline.py::test_release_abandon_writes_degenerate_handoff_and_records_path` — `obpi_lock_release_cmd --abandon network_loss:reason` writes a handoff under `.gzkit/handoffs/` with frontmatter `abandoned: true`, `category`, `reason`, plus four minimum-info fields; `obpi_lock_released_event` includes `handoff_path`

#### 2d. Warning-only release tests (REQ-07)

- [ ] `tests/governance/test_token_block_discipline.py::test_release_without_handoff_warns_but_succeeds` — release without `--abandon` and no handoff prints WARNING to stderr; exit 0 (still succeeds in OBPI-02 staging)

#### 2e. Backward-compat event tests (REQ-08)

- [ ] `tests/test_ledger_events.py::test_obpi_lock_released_handoff_path_optional` — legacy `obpi_lock_released_event` without `handoff_path` field validates against schema

**Deliverable:** All tests written, all fail RED. Commit: `WIP: tests for OBPI-0.0.41-02 (RED baseline)`.

### 3. Implement Race-Condition Interlock (TDD GREEN)

#### 3a. Rewrite lock_manager.write_lock for exclusive-creation

- [ ] `src/gzkit/lock_manager.py:write_lock` — replace `path.write_text()` with `open(path, "x")` context manager
- [ ] Handle `FileExistsError` propagation (let it bubble; caller decides interpretation)
- [ ] Preserve existing surface: on success, creates lock file with JSON content; no signature change

**Code form:**
```python
def write_lock(path: Path, content: dict) -> None:
    """Write lock atomically via exclusive-creation. Raises FileExistsError if lock exists."""
    with open(path, "x") as f:
        json.dump(content, f)
```

#### 3b. Update obpi_lock_claim_cmd to handle FileExistsError

- [ ] Catch `FileExistsError` from `write_lock`
- [ ] Load existing lock file and extract holder identity
- [ ] Return exit 1 with JSON status: `{"status": "conflict", "holder": {...}, "message": "..."}`
- [ ] Distinguish from ownership-error path (different message, same exit code 1)

**Test:** `test_claim_handles_file_exists_error_as_conflict` now PASSES GREEN.

### 4. Implement --abandon Flag and Degenerate Handoff (TDD GREEN)

#### 4a. Extend obpi_lock_release_cmd with --abandon parsing

- [ ] Update `src/gzkit/commands/obpi_lock.py:obpi_lock_release_cmd` signature: add `abandon_category_reason: str | None = None` parameter
- [ ] Parse `--abandon <category>:<reason>` using colon delimiter; validate format (no leading/trailing whitespace on category)
- [ ] Validate `category` against closed enum from `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1

#### 4b. Write degenerate handoff when --abandon provided

- [ ] On `--abandon <category>:<reason>`, write a degenerate handoff under `.gzkit/handoffs/` with:
  - Frontmatter: `abandoned: true`, `category: <category>`, `reason: <reason>`, `created_at: <ISO-timestamp>`, `previous_lock_claimed_at: <matching-claim-timestamp>`, `commit_sha: <HEAD>`, `branch: <current-branch>`
  - Body: statement of reason for abandonment
  - Filename: `.gzkit/handoffs/{TIMESTAMP}-{OBPI-ID}-abandoned.md` (standard handoff naming)
- [ ] Extract/compute these fields before release is invoked

**Test:** `test_release_abandon_writes_degenerate_handoff_and_records_path` now PASSES GREEN.

#### 4c. Validate category against closed enum

- [ ] `src/gzkit/handoff_validation.py` (new or existing) — function `validate_abandon_category(category: str)` that checks against enum
- [ ] Enum source: read from `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1 comment or mirror with code comment naming the rule as source-of-truth

**Test:** `test_release_abandon_rejects_unregistered_category` now PASSES GREEN.

### 5. Implement Warning-Only Release Precondition

#### 5a. Add warning when release proceeds without handoff/--abandon

- [ ] After validating `--abandon` category (or absence), check: does a matching handoff exist on disk?
- [ ] If no `--abandon` AND no handoff, print WARNING to stderr naming `gz-session-handoff` skill and OBPI-03 fail-closed flip
- [ ] Release exits 0 (still succeeds in OBPI-02 staging window)

**Test:** `test_release_without_handoff_warns_but_succeeds` now PASSES GREEN.

### 6. Extend obpi_lock_released_event Payload (Backward-Compatible)

#### 6a. Update ledger_events.py

- [ ] `src/gzkit/ledger_events.py:obpi_lock_released_event` — extend `extra: dict` to accept optional `handoff_path: str | None = None`
- [ ] When `--abandon` is used, emit event with `handoff_path` pointing at the written degenerate handoff
- [ ] When no handoff and no `--abandon`, emit event with `handoff_path: None`
- [ ] Preserve backward-compatibility: legacy events without the field continue to validate

**Test:** `test_obpi_lock_released_handoff_path_optional` now PASSES GREEN.

### 7. Update Handoff Model (Conditional)

#### 7a. Check src/gzkit/content/models/handoff.py

- [ ] Read current model
- [ ] If `abandoned`, `category`, `reason` fields don't exist, add them as optional: `abandoned: bool = False`, `category: str | None = None`, `reason: str | None = None`
- [ ] If fields already exist, skip

### 8. Register --abandon Argument on CLI Parser

#### 8a. Update src/gzkit/cli/parser_artifacts.py

- [ ] Locate `p_lock_release` parser (around line 1381)
- [ ] Add argument: `parser.add_argument('--abandon', type=str, help='Category:reason for lock abandonment ...')`
- [ ] Document categories and example

### 9. Update Documentation

#### 9a. docs/user/manpages/obpi-lock-release.md

- [ ] Document `--abandon <category>:<reason>` flag
- [ ] List closed categories from `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1
- [ ] Include example: `gz obpi lock release OBPI-0.0.41-02 --abandon network_loss:"session interrupted"`
- [ ] Document warning behavior (warning emitted when released without handoff/--abandon, but exit 0 in OBPI-02)
- [ ] Document degenerate-handoff creation

#### 9b. docs/user/manpages/obpi-lock-claim.md

- [ ] Document claim-conflict case: exit 1, status `conflict`, holder info in JSON output

**Tests:** `uv run mkdocs build --strict` passes; docs sections are read by Stage 4 ceremony.

### 10. Code Quality and Tests

#### 10a. TDD Green: All tests pass

- [ ] `uv run -m unittest -q` — all 9+ tests PASS with correct behavior
- [ ] All tests have `@covers(REQ-0.0.41-02-0N)` decorators

#### 10b. Lint and format

- [ ] `uv run ruff check . --fix && uv run ruff format .`

#### 10c. Type check

- [ ] `uv run mypy` or equivalent — no errors

#### 10d. Coverage

- [ ] Run with `coverage` flag; verify coverage >= 40% (or project baseline)

### 11. Verification Commands (before Stage 3)

- [ ] `uv run gz lint`
- [ ] `uv run gz typecheck`
- [ ] `uv run gz test`
- [ ] `uv run mkdocs build --strict`

## Verification

All REQ-derived tests pass and are decorated with `@covers(REQ-...)`:

```bash
uv run -m unittest -q
uv run mkdocs build --strict
uv run gz lint
uv run gz typecheck
```

Expected: all green, no warnings or errors.

## Notes

- **Category enum source:** Must ground in `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1. Do not redefine in code without a comment citing the rule.
- **Degenerate-handoff filename:** Follow the standard handoff naming pattern (timestamp-prefixed, in `.gzkit/handoffs/`).
- **Warning text:** Name `gz-session-handoff` skill and mention OBPI-03 fail-closed flip (forward-compatibility signal for operators).
- **Backward-compatibility:** The `handoff_path` field is optional (`str | None = None`). Legacy ledger events without it must validate.
- **Stage 2 entry point:** Begin with TDD RED step (write all tests first); do not implement code until tests exist and fail.

## Acceptance

This plan is accepted when:
1. All 9+ tests are written, fail RED, and match the REQ descriptions.
2. After GREEN phase, `uv run -m unittest -q` passes.
3. All quality gates (lint, format, type, docs) pass.
4. `uv run gz covers OBPI-0.0.41-02 --json` shows `uncovered_reqs: 0`.

---

**Plan Status:** Ready for execution
**Author:** claude-code (plan-audit)
**Date:** 2026-06-07
