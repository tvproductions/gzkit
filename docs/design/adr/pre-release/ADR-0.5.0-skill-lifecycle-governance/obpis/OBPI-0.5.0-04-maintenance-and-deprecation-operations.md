---
id: OBPI-0.5.0-04-maintenance-and-deprecation-operations
parent: ADR-0.5.0-skill-lifecycle-governance
item: 4
lane: Heavy
status: in_progress
---

# OBPI-0.5.0-04-maintenance-and-deprecation-operations

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #4 -- "Define maintenance and deprecation operations."

## Objective

Define repeatable maintenance operations for skill lifecycle updates, deprecations, and parity hygiene so operations remain sustainable after initial migration.

## Lane

**Heavy**

## Allowed Paths

- `.gzkit/skills/**`
- `.agents/skills/**`
- `.claude/skills/**`
- `.github/skills/**`
- `docs/user/**`
- `docs/governance/**`
- `src/gzkit/skills.py`
- `src/gzkit/cli.py`
- `src/gzkit/sync.py`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Maintenance operations MUST define cadence and ownership for lifecycle metadata review.
2. Deprecation operations MUST define mirror behavior and operator communication requirements.
3. Maintenance workflow MUST preserve canonical-first synchronization semantics.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [x] Maintenance/deprecation behavior tests added and passing.

### Gate 3: Docs

- [x] Maintenance runbook and deprecation policy updated.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] Human attestation received for OBPI completion (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] REQ-0.5.0-04-01: Maintenance cadence and ownership are explicit.
- [x] REQ-0.5.0-04-02: Deprecation semantics are documented and enforceable.
- [x] REQ-0.5.0-04-03: Sync + audit behavior remains deterministic across lifecycle operations.

## Evidence

### Implementation Summary

- Files created/modified:
  - `src/gzkit/skills.py`
  - `src/gzkit/cli.py`
  - `src/gzkit/sync.py`
  - `tests/test_skills_audit.py`
  - `tests/test_sync.py`
  - `tests/test_cli.py`
  - `docs/user/commands/skill-audit.md`
  - `docs/user/commands/agent-sync-control-surfaces.md`
  - `docs/governance/GovZero/layered-trust.md`
  - `docs/governance/governance_runbook.md`
- Maintenance/deprecation policy/runtime updates:
  - Added state-conditional deprecation/retirement metadata contract checks.
  - Added fail-closed stale `last_reviewed` enforcement (default 90 days).
  - Added `gz skill audit --max-review-age-days` runtime override and JSON fields:
    `max_review_age_days`, `stale_review_count`.
  - Extended mirror drift enforcement to include deprecation fields when canonical defines them.
  - Extended sync preflight blockers for stale review metadata and deprecation contract violations.
- Tests added/updated:
  - `tests/test_skills_audit.py`: stale review failures, override behavior, deprecation required/forbidden fields, retirement evidence requirement, deprecation mirror drift.
  - `tests/test_sync.py`: stale review preflight blocker, deprecated/retired metadata blocker scenarios.
  - `tests/test_cli.py`: new audit JSON fields, invalid `--max-review-age-days` handling, override behavior scenario.
- Date implemented: 2026-03-01

### Verification Commands Run (2026-03-01)

```text
uv run -m unittest tests.test_skills_audit tests.test_sync tests.test_cli.TestSkillCommands
Ran 66 tests in 0.198s
OK

uv run gz lint
All checks passed

uv run gz test
Ran 262 tests in 2.163s
OK

uv run gz skill audit
Skill audit passed
Checked 45 canonical skills across 4 roots
Blocking: 0  Non-blocking: 0
Max review age: 90 days

uv run gz skill audit --json
{
  "valid": true,
  "checked_skills": 45,
  "checked_roots": [".gzkit/skills", ".agents/skills", ".claude/skills", ".github/skills"],
  "issues": [],
  "strict": false,
  "max_review_age_days": 90,
  "success": true,
  "error_count": 0,
  "warning_count": 0,
  "blocking_error_count": 0,
  "non_blocking_warning_count": 0,
  "stale_review_count": 0
}

uv run gz skill audit --max-review-age-days 365
Skill audit passed
Checked 45 canonical skills across 4 roots
Blocking: 0  Non-blocking: 0
Max review age: 365 days

uv run gz agent sync control-surfaces --dry-run
Dry run completed with expected targets listed

uv run gz agent sync control-surfaces
Sync complete

uv run gz validate --documents
All validations passed
```

### Human Attestation

- Attestor: Human operator (in-session)
- Attestation: "attest completed"
- Date: 2026-03-01
- Scope: OBPI-0.5.0-04 implementation evidence reviewed and accepted

**Brief Status:** Completed
