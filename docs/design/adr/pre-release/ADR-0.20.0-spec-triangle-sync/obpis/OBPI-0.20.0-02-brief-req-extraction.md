---
id: OBPI-0.20.0-02-brief-req-extraction
parent: ADR-0.20.0-spec-triangle-sync
item: 2
lane: Lite
status: in_progress
---

# OBPI-0.20.0-02: Brief REQ Extraction

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.20.0-spec-triangle-sync/ADR-0.20.0-spec-triangle-sync.md`
- **Checklist Item:** #2 — "Brief REQ extraction: parse OBPI briefs to discover REQ entities"

**Status:** Completed

## Objective

Build a parser that extracts REQ entities from OBPI brief markdown files. The parser reads the `## Acceptance Criteria` section, identifies `REQ-<semver>-<obpi>-<seq>` identifiers, and produces typed REQ entity instances with their status (checked/unchecked from the checkbox state).

## Lane

**Lite** — Internal extraction engine; no external CLI/API changes.

## Allowed Paths

- `src/gzkit/triangle.py` — REQ extraction functions (extend the module from OBPI-01)
- `tests/test_triangle.py` — extraction unit tests

## Denied Paths

- `src/gzkit/commands/` — CLI belongs to OBPI-04
- OBPI brief files themselves — read-only; extraction must not modify briefs
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Extract REQ identifiers from `## Acceptance Criteria` sections in OBPI brief markdown.
1. REQUIREMENT: Parse checkbox state (`- [ ]` = unchecked, `- [x]` = checked) to determine REQ status.
1. REQUIREMENT: Extract the description text following the REQ identifier on the same line.
1. REQUIREMENT: Scan a directory tree of briefs and return all discovered REQ entities with their source file paths.
1. REQUIREMENT: Handle malformed REQ lines gracefully — log a warning but do not fail the scan.
1. NEVER: Modify OBPI brief files during extraction.
1. ALWAYS: Return results sorted by REQ identifier (semantic version ordering).

> STOP-on-BLOCKERS: OBPI-0.20.0-01 must be complete (REQ entity model must exist).

## Quality Gates (Lite)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Unit tests validate extraction from sample brief markdown
- [x] Unit tests validate checkbox state parsing
- [x] Unit tests validate graceful handling of malformed REQ lines
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [x] REQ-0.20.0-02-01: Given an OBPI brief with `- [ ] REQ-0.15.0-03-01: Some criterion`, when extracted, then returns a REQ entity with status=unchecked and description="Some criterion".
- [x] REQ-0.20.0-02-02: Given an OBPI brief with `- [x] REQ-0.15.0-03-01: Completed criterion`, when extracted, then returns a REQ entity with status=checked.
- [x] REQ-0.20.0-02-03: Given a directory of 3 OBPI briefs with 12 total REQs, when scanned, then returns all 12 REQs with correct source file paths.
- [x] REQ-0.20.0-02-04: Given a brief with a malformed line `- [ ] REQ-bad: text`, when extracted, then logs a warning and skips the line without failing.

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Coverage:** Coverage >= 40% maintained
- [x] **OBPI Completion:** Record evidence in brief

## Evidence

### Implementation Summary

- Files modified: `src/gzkit/triangle.py`, `tests/test_triangle.py`
- Functions added: `extract_reqs_from_brief`, `scan_briefs`, `DiscoveredReq`, `_req_sort_key`, `_parse_frontmatter_id`, `_extract_obpi_short_id`
- Tests added: 17 new tests (49 total in module) covering extraction, scanning, malformed lines, sorting
- Date completed: 2026-03-27

### Key Proof

```text
$ uv run -m unittest tests.test_triangle -v
Ran 49 tests in 0.003s — OK
```

### Gate 2 (TDD)

```text
Ran 49 tests in 0.003s — OK (tests/test_triangle.py)
Full suite: 1680 tests pass
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

## Human Attestation

- Attestor: Jeffry Babb
- Attestation: completed
- Date: 2026-03-27

---

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
