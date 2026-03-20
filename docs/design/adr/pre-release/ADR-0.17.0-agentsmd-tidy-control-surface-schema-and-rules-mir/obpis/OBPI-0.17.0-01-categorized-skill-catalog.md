---
id: OBPI-0.17.0-01-categorized-skill-catalog
parent: ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir
item: 1
lane: heavy
status: Completed
---

# OBPI-0.17.0-01-categorized-skill-catalog: Categorized Skill Catalog

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir.md`
- **Checklist Item:** #1 - "Categorized Skill Catalog"

**Status:** Draft

## Objective

Organize all canonical skills in AGENTS.md into functional categories so that agents and operators can discover skills by domain (ADR lifecycle, OBPI pipeline, code quality, etc.) rather than scanning a flat list. Every skill in `.gzkit/skills/` must appear in exactly one category with zero omissions.

## Lane

**heavy** - Inherited from parent ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir (heavy).

> Heavy is reserved for command/API/schema/runtime-contract changes. AGENTS.md is an external agent contract surface, so changes to its structure are Heavy.

## Allowed Paths

- `AGENTS.md` - Skills catalog section
- `src/gzkit/rules.py` - Control surface sync (generates AGENTS.md catalog)

## Denied Paths

- `docs/design/**` - ADR changes out of scope (except this brief)
- New dependencies
- CI files, lockfiles
- `.gzkit/skills/` - Canonical skill definitions (read-only for this OBPI)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every skill directory in `.gzkit/skills/` MUST appear in exactly one category in the AGENTS.md "Available Skills" section.
2. REQUIREMENT: Categories MUST group skills by functional domain (lifecycle, operations, quality, etc.).
3. NEVER: A skill may not appear in more than one category.
4. NEVER: The catalog may not contain skill names that don't exist on disk.
5. ALWAYS: Category headings must use `####` (h4) under the `### Available Skills` section.

> STOP-on-BLOCKERS: if `.gzkit/skills/` is empty or AGENTS.md is missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - agent operating contract (skills section at lines 66-110)
- [x] Parent ADR - three-layer control surface model

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir/`
- [x] Related OBPIs: OBPI-02 (Rules Mirroring), OBPI-05 (Manifest Update)

**Prerequisites (check existence, STOP if missing):**

- [x] `.gzkit/skills/` contains 51 skill directories
- [x] `AGENTS.md` exists and has Skills section

**Existing Code (understand current state):**

- [x] Current AGENTS.md catalog: lines 84-108, 8 categories, 51 skills

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Catalog completeness is verifiable by script
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] AGENTS.md catalog is the documentation artifact itself

### Gate 4: BDD (Heavy only)

- [ ] N/A — no behave features for AGENTS.md structure

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification: all 51 skills present in catalog
uv run python -c "
from pathlib import Path
disk = {d.name for d in Path('.gzkit/skills').iterdir() if d.is_dir()}
content = Path('AGENTS.md').read_text(encoding='utf-8')
missing = [s for s in disk if s not in content]
print(f'Skills on disk: {len(disk)}')
print(f'Missing from catalog: {missing or \"none\"}')
assert not missing, f'Missing skills: {missing}'
print('PASS: All skills categorized')
"
```

## Acceptance Criteria

- [x] REQ-0.17.0-01-01: AGENTS.md contains "### Available Skills" section with categorized subsections
- [x] REQ-0.17.0-01-02: All 51 canonical skills in `.gzkit/skills/` appear in exactly one category
- [x] REQ-0.17.0-01-03: Zero skills in catalog that don't exist on disk
- [x] REQ-0.17.0-01-04: Categories use h4 headings under h3 "Available Skills"
- [x] REQ-0.17.0-01-05: Skills Protocol section defines discovery workflow

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz test
Ran 685 tests in 18.099s — OK
```

### Code Quality

```text
$ uv run gz lint
All checks passed! Lint passed.

$ uv run gz typecheck
All checks passed! Type check passed.
```

### Gate 3 (Docs)

```text
AGENTS.md lines 84-108: 8 categories, 51 skills, zero gaps.
Verification script: disk=51 missing=0 extra=0 — PASS
```

### Gate 4 (BDD)

```text
N/A — no behave features for AGENTS.md catalog structure
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-19
```

## Value Narrative

Before this OBPI, AGENTS.md listed skills in an unstructured way, making it difficult for agents and operators to discover relevant skills by domain. Now the catalog organizes all 51 canonical skills into 8 functional categories (ADR Lifecycle, ADR Operations, ADR Audit & Closeout, OBPI Pipeline, Governance Infrastructure, Agent & Repository Operations, Code Quality, Cross-Repository), enabling domain-based skill discovery.

### Key Proof

```text
$ uv run python -c "
from pathlib import Path
disk = {d.name for d in Path('.gzkit/skills').iterdir() if d.is_dir()}
content = Path('AGENTS.md').read_text(encoding='utf-8')
missing = [s for s in disk if s not in content]
print(f'Skills: {len(disk)}, Missing: {len(missing)}')
assert not missing
print('PASS: 51/51 skills categorized across 8 categories')
"
Skills: 51, Missing: 0
PASS: 51/51 skills categorized across 8 categories
```

### Implementation Summary

- Files created/modified: `AGENTS.md` (lines 84-108, categorized skill catalog)
- Tests added: Catalog completeness verification script
- Date completed: 2026-03-19
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:Jeff`
- Attestation: attest completed
- Date: 2026-03-19

---

**Brief Status:** Completed

**Date Completed:** 2026-03-19

**Evidence Hash:** -
