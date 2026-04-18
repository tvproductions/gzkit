---
id: OBPI-0.22.0-03-git-commit-linkage
parent: ADR-0.22.0-task-level-governance
item: 3
lane: Lite
status: attested_completed
---

# OBPI-0.22.0-03: Git Commit Linkage

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- **Checklist Item:** #3 — "Git commit linkage: TASK ID in commit trailers, parsing for traceability"

**Status:** Completed

## Objective

Define the git commit linkage contract: TASK IDs appear in commit message trailers, and a parser extracts them for four-tier traceability (TASK → REQ → OBPI → ADR) from git history.

## Lane

**Lite** — Internal contract and parser; no CLI changes.

## Allowed Paths

- `src/gzkit/tasks.py` — commit trailer parser and formatter
- `tests/test_tasks.py` — commit linkage unit tests

## Denied Paths

- `src/gzkit/commands/` — CLI belongs to OBPI-04
- `.git/` — no git hook changes in this OBPI
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Define commit trailer format: `Task: TASK-<semver>-<obpi>-<req>-<seq>`.
1. REQUIREMENT: Parser MUST extract TASK IDs from commit message text (trailer section).
1. REQUIREMENT: Multiple TASK trailers in one commit MUST all be extracted.
1. REQUIREMENT: Parser MUST resolve TASK → REQ → OBPI → ADR chain from the identifier components.
1. REQUIREMENT: Formatter MUST produce a valid trailer line from a TASK entity.
1. NEVER: Modify git hooks or commit automation — this OBPI defines the contract only.

> STOP-on-BLOCKERS: OBPI-01 must be complete (TASK identifier scheme).

## Acceptance Criteria

- [x] REQ-0.22.0-03-01: Given a commit message with `Task: TASK-0.20.0-01-01-01`, when parsed, then the TASK ID is extracted.
- [x] REQ-0.22.0-03-02: Given a TASK entity, when formatted as a trailer, then produces `Task: TASK-0.20.0-01-01-01`.
- [x] REQ-0.22.0-03-03: Given a commit with two Task trailers, when parsed, then both TASK IDs are returned.
- [x] REQ-0.22.0-03-04: Given TASK-0.20.0-01-01-01, when resolved, then chain is: TASK→REQ-0.20.0-01-01→OBPI-0.20.0-01→ADR-0.20.0.

## Verification Commands (Concrete)

```bash
uv run -m unittest tests.test_tasks -v
# Expected: trailer parsing and formatting tests pass

uv run gz lint
# Expected: lint passes after commit-linkage edits

uv run gz typecheck
# Expected: commit-linkage types remain clean
```

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean

### Implementation Summary

- Trailer format: `Task: TASK-<semver>-<obpi>-<req>-<seq>` defined via `_TRAILER_LINE_RE` regex
- Parser: `parse_task_trailers()` extracts TASK IDs from the trailer section of commit messages
- Multi-trailer: Parser returns all `Task:` trailers, ignoring body text and non-Task trailers
- Chain resolver: `resolve_task_chain()` maps TASK → REQ → OBPI → ADR from identifier components
- Formatter: `format_commit_trailer()` produces trailer lines from TaskEntity or TaskId

### Key Proof

```
$ uv run -m unittest tests.test_tasks.TestParseTaskTrailers tests.test_tasks.TestResolveTaskChain tests.test_tasks.TestFormatCommitTrailer -v
test_format_trailer_from_task_entity ... ok
test_format_trailer_from_task_id ... ok
test_ignores_non_task_trailers ... ok
test_ignores_task_keyword_in_body ... ok
test_no_trailers_returns_empty ... ok
test_parse_multiple_trailers ... ok
test_parse_single_trailer ... ok
test_resolve_chain ... ok
test_resolve_chain_different_ids ... ok
test_resolve_chain_keys ... ok
Ran 10 tests in 0.000s — OK
```

---

**Brief Status:** Completed

**Date Completed:** 2026-03-28

**Evidence Hash:** -
