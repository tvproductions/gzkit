# Plan: OBPI-0.0.57-02-gz-adr-create-nominal-allocator

**OBPI:** OBPI-0.0.57-02-gz-adr-create-nominal-allocator
**Parent ADR:** ADR-0.0.57-foundation-adr-nominal-id-triage
**Lane:** Heavy

## Context

Replace `_next_available_foundation_semver` (max+1 odometer at
`src/gzkit/commands/plan.py:113-125`) with `_next_free_nominal_foundation_id`
(lowest-unused-integer allocator). One call site at `plan.py:160` in
`_validate_kind_and_semver` error-hint. Update error message text, skill
description, and manpage. Add BDD scenario for Heavy gate.

**Destination-in-mind (plan-audit §6a):** Replace the single function and its one
call site; the rename makes the doctrine shift visible in `git log`. No other
architectural change.

**Rejected alternatives:** (1) Keep old name and just change the body — rejected:
REQ-02-02 requires the rename to be visible. (2) Auto-allocate semver on
`gz plan create --kind foundation` without `--semver` — rejected: out of scope;
user still supplies `--semver`, the hint just becomes gap-aware.

**Coupled-surface note (AGENTS.md §1a):**
`tests/test_taxonomy_validator_nominal.py:test_plan_allocator_is_unchanged`
imports `_next_available_foundation_semver` and asserts max+1 behavior. This
test was authored by OBPI-01 (ATTESTED COMPLETED) to verify OBPI-01 did NOT
change `plan.py`. After OBPI-02 renames the function, this import breaks with
`ImportError`. The test must be updated in the same commit: remove
`test_plan_allocator_is_unchanged` (its guard clause is satisfied by OBPI-01
being complete) and update the import line.

## Files

### Create
- `tests/test_plan_command.py` — nominal-allocator unit tests
- `tests/fixtures/foundation_nominal_allocator/sparse_with_gap/` — 4 stub ADR dirs (IDs 1, 2, 5, 7)
- `tests/fixtures/foundation_nominal_allocator/contiguous/` — 3 stub ADR dirs (IDs 1, 2, 3)
- `tests/fixtures/foundation_nominal_allocator/empty/` — empty dir
- `features/plan_create_nominal.feature` — BDD scenarios

### Modify
- `src/gzkit/commands/plan.py` — rename function + update call site
- `tests/test_taxonomy_validator_nominal.py` — fix broken import, remove obsolete test (coupled-surface §1a)
- `.gzkit/skills/gz-adr-create/SKILL.md` — update odometer language; bump skill-version + last_reviewed
- `docs/user/manpages/plan-create.md` — update error-hint language to "next free nominal"

## Steps

### Step 1: Create test fixtures (on-disk)

Create the committed fixture directories. Each ADR stub dir needs a `.gitkeep`
so git preserves the empty dirs.

**sparse_with_gap** — IDs 1, 2, 5, 7 present; gaps at 3, 4, 6:
- `tests/fixtures/foundation_nominal_allocator/sparse_with_gap/ADR-0.0.1-fixture-a/.gitkeep`
- `tests/fixtures/foundation_nominal_allocator/sparse_with_gap/ADR-0.0.2-fixture-b/.gitkeep`
- `tests/fixtures/foundation_nominal_allocator/sparse_with_gap/ADR-0.0.5-fixture-c/.gitkeep`
- `tests/fixtures/foundation_nominal_allocator/sparse_with_gap/ADR-0.0.7-fixture-d/.gitkeep`

**contiguous** — IDs 1, 2, 3; no gaps:
- `tests/fixtures/foundation_nominal_allocator/contiguous/ADR-0.0.1-fixture-a/.gitkeep`
- `tests/fixtures/foundation_nominal_allocator/contiguous/ADR-0.0.2-fixture-b/.gitkeep`
- `tests/fixtures/foundation_nominal_allocator/contiguous/ADR-0.0.3-fixture-c/.gitkeep`

**empty** — directory only:
- `tests/fixtures/foundation_nominal_allocator/empty/.gitkeep`

### Step 2 (RED): Write failing tests in tests/test_plan_command.py

Create `tests/test_plan_command.py`:

```python
"""Tests for gz plan create nominal allocator (OBPI-0.0.57-02).

REQ-0.0.57-02-01: sparse tree {1,2,5,7} → returns "0.0.3" (lowest gap)
REQ-0.0.57-02-02: empty tree → returns "0.0.1"
REQ-0.0.57-02-03: contiguous {1,2,3} → returns "0.0.4" (degenerate)
REQ-0.0.57-02-04: old function absent; new function present
"""
from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.commands.plan import _next_free_nominal_foundation_id
from gzkit.traceability import covers

FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "foundation_nominal_allocator"


class TestNextFreeNominalFoundationId(unittest.TestCase):

    @covers("REQ-0.0.57-02-01")
    def test_sparse_tree_returns_lowest_gap(self) -> None:
        """Given {1,2,5,7}, returns "0.0.3" — lowest unused integer."""
        result = _next_free_nominal_foundation_id(FIXTURES_ROOT / "sparse_with_gap")
        self.assertEqual(result, "0.0.3")

    @covers("REQ-0.0.57-02-02")
    def test_empty_tree_returns_0_0_1(self) -> None:
        """Given empty foundation tree, returns "0.0.1"."""
        result = _next_free_nominal_foundation_id(FIXTURES_ROOT / "empty")
        self.assertEqual(result, "0.0.1")

    @covers("REQ-0.0.57-02-03")
    def test_contiguous_tree_returns_next_after_max(self) -> None:
        """Given {1,2,3}, returns "0.0.4" — no gaps, degenerate case."""
        result = _next_free_nominal_foundation_id(FIXTURES_ROOT / "contiguous")
        self.assertEqual(result, "0.0.4")

    @covers("REQ-0.0.57-02-04")
    def test_old_odometer_name_absent(self) -> None:
        """_next_available_foundation_semver must not exist in plan module."""
        import gzkit.commands.plan as plan_module

        self.assertFalse(
            hasattr(plan_module, "_next_available_foundation_semver"),
            "_next_available_foundation_semver must be absent after rename",
        )

    @covers("REQ-0.0.57-02-04")
    def test_new_allocator_name_present(self) -> None:
        """_next_free_nominal_foundation_id must be importable from plan module."""
        import gzkit.commands.plan as plan_module

        self.assertTrue(
            hasattr(plan_module, "_next_free_nominal_foundation_id"),
            "_next_free_nominal_foundation_id must be present in plan module",
        )
```

Run → RED: `ImportError: cannot import name '_next_free_nominal_foundation_id'`

### Step 3 (GREEN): Implement _next_free_nominal_foundation_id in plan.py

In `src/gzkit/commands/plan.py`, replace the function at lines 113-125:

**Remove (lines 113-125):**
```python
def _next_available_foundation_semver(foundation_root: Path) -> str:
    """Scan existing foundation/<id>/ dirs and return next available 0.0.N."""
    if not foundation_root.exists():
        return "0.0.1"
    max_n = -1
    for entry in foundation_root.iterdir():
        if not entry.is_dir():
            continue
        match = re.match(r"^ADR-0\.0\.(\d+)(?:-.*)?$", entry.name)
        if match:
            n = int(match.group(1))
            max_n = max(max_n, n)
    return f"0.0.{max_n + 1}" if max_n >= 0 else "0.0.1"
```

**Add:**
```python
def _next_free_nominal_foundation_id(foundation_root: Path) -> str:
    """Scan foundation/<id>/ dirs and return the lowest unused 0.0.N (N >= 1).

    Nominal allocation: returns the smallest integer N >= 1 not present in
    the existing directory set, tolerating gaps.
    E.g. {0.0.1, 0.0.2, 0.0.5, 0.0.7} -> "0.0.3" (not "0.0.8").
    """
    if not foundation_root.exists():
        return "0.0.1"
    used: set[int] = set()
    for entry in foundation_root.iterdir():
        if not entry.is_dir():
            continue
        m = re.match(r"^ADR-0\.0\.(\d+)(?:-.*)?$", entry.name)
        if m:
            used.add(int(m.group(1)))
    n = 1
    while n in used:
        n += 1
    return f"0.0.{n}"
```

Update call site at ~line 160 in `_validate_kind_and_semver`:

**Replace:**
```python
        next_available = _next_available_foundation_semver(adrs_root / "foundation")
        console.print(
            f"[red]ERROR:[/red] --kind foundation requires --semver matching 0.0.x "
            f"(got {semver!r}). Next available foundation semver: "
            f"[bold]{next_available}[/bold]."
        )
```

**With:**
```python
        next_free = _next_free_nominal_foundation_id(adrs_root / "foundation")
        console.print(
            f"[red]ERROR:[/red] --kind foundation requires --semver matching 0.0.x "
            f"(got {semver!r}). Next free nominal foundation ID: "
            f"[bold]{next_free}[/bold]."
        )
```

Run tests → GREEN for all 5 nominal-allocator tests.

### Step 4: Fix coupled-surface in tests/test_taxonomy_validator_nominal.py

Update `tests/test_taxonomy_validator_nominal.py`:

1. Replace the import:
   - Remove: `from gzkit.commands.plan import _next_available_foundation_semver`
   - No replacement needed (the test using it is removed)

2. Remove `test_plan_allocator_is_unchanged` method from `TestNominalIdTaxonomyValidator`
   (REQ-0.0.57-01-05 "plan.py unchanged" was a guard for OBPI-01's scope — OBPI-01
   is ATTESTED COMPLETED, and OBPI-02 is the deliberate change that makes
   this guard obsolete).

Run full unittest suite → confirm `test_taxonomy_validator_nominal.py` still passes.

### Step 5: Update skill and run sync (REQ-05, REQ-06)

Edit `.gzkit/skills/gz-adr-create/SKILL.md`:

1. Update `description:` field (line 4):
   - From: `"Create and book a GovZero ADR with its OBPI briefs. Enforces minor-version odometer and five-gate compliance. Portable skill for GovZero-compliant repositories."`
   - To: `"Create and book a GovZero ADR with its OBPI briefs. Enforces next-free-integer nominal allocation for foundation IDs and five-gate compliance. Portable skill for GovZero-compliant repositories."`

2. Update `govzero-compliance-areas:` in metadata:
   - From: `"charter (gates 1-5), lifecycle (state machine), linkage (ADR/OBPI/GHI), minor-release (odometer discipline)"`
   - To: `"charter (gates 1-5), lifecycle (state machine), linkage (ADR/OBPI/GHI), foundation-nominal-allocation (next-free-integer)"`

3. Bump `skill-version:` from `"6.4.2"` to `"6.5.0"` (governance rule change — minor bump)

4. Update `last_reviewed:` to `2026-05-23`

Run: `uv run gz agent sync control-surfaces`

### Step 6: Update manpage (REQ-06)

In `docs/user/manpages/plan-create.md`, find any "next available" or odometer
language in the error-recovery section and update to "next free nominal" semantics.

Specifically update the `--kind foundation` example comment or description to
reflect that the suggested ID is the lowest unused (gap-filling) integer, not
just `max+1`.

### Step 7: BDD scenario (Gate 4 — Heavy lane)

Create `features/plan_create_nominal.feature`:

```gherkin
Feature: gz plan create nominal foundation ID allocator (ADR-0.0.57 / OBPI-0.0.57-02)
  As an operator,
  I want gz plan create --kind foundation to suggest the next free nominal ID,
  So that I can create foundation ADRs in impact order, not ID order.

  @REQ-0.0.57-02-01
  Scenario: Error hint shows lowest gap when foundation tree is sparse
    Given a project with foundation ADRs 0.0.1, 0.0.2, 0.0.5, 0.0.7
    When I run the gz command "plan create my-adr --kind foundation --semver 99.0.0"
    Then the command exits with code 1
    And the output contains "0.0.3"

  @REQ-0.0.57-02-03
  Scenario: Error hint shows next integer when foundation tree is contiguous
    Given a project with foundation ADRs 0.0.1, 0.0.2, 0.0.3
    When I run the gz command "plan create my-adr --kind foundation --semver 99.0.0"
    Then the command exits with code 1
    And the output contains "0.0.4"
```

### Step 8: Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.test_plan_command -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers OBPI-0.0.57-02-gz-adr-create-nominal-allocator --json

# Verify rename invariant
rg -n "_next_available_foundation_semver" src/gzkit/commands/plan.py
# Expected: no matches

rg -n "_next_free_nominal_foundation_id" src/gzkit/commands/plan.py
# Expected: definition + call site present

# Skill mirror parity
diff .gzkit/skills/gz-adr-create/SKILL.md .claude/skills/gz-adr-create/SKILL.md
# Expected: no diff after sync
```

## Verification

```bash
uv run gz validate --documents
uv run gz validate --surfaces
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.test_plan_command -v
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```
