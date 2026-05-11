# Plan: OBPI-0.0.32-01 — Skills Physical Migration

**OBPI:** OBPI-0.0.32-01-skills-physical-migration
**Parent ADR:** ADR-0.0.32-canonical-surface-packaging
**Lane:** Heavy | **Kind:** Foundation

## Context

ADR-0.0.32 promotes canonical surface files from `.gzkit/` into the Python
package under `src/gzkit/` to satisfy the T0 distribution invariant (ADR-0.0.31).
OBPI-01 is the physical migration unit: `git mv` all canonical SKILL.md files and
convert `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py`. No scaffolder or
wheel changes in this OBPI.

**Pre-migration findings (documented per brief STOP condition):**

- On-disk skill count: **70** (ADR/brief state 61; 9 skills added post-authoring).
  Decision: migrate all 70.
- 38 skill directories contain auxiliary subdirectories (`agents/`, `assets/`,
  `references/`, `scripts/`). Decision: only `SKILL.md` moves via `git mv`; aux
  content stays in `.gzkit/skills/<slug>/` until OBPI-06 handles package-data.
- `src/gzkit/skills.py` is 479 lines (brief says 438; extra re-export block added
  since brief authoring). Not a blocker.

## Files

**Modified/deleted:**
- `src/gzkit/skills.py` — deleted after conversion (contents move to `__init__.py`)
- `.gzkit/skills/<slug>/SKILL.md` (70 files) — source of `git mv`

**Created:**
- `src/gzkit/skills/__init__.py` — receives `src/gzkit/skills.py` contents unchanged
- `src/gzkit/skills/<slug>/SKILL.md` (70 files) — destination of `git mv`
- `tests/test_skills.py` — regression tests for all public-symbol re-exports

## Public Symbol Enumeration (from `__all__`)

The definitive set to test (derived from `__all__` in `src/gzkit/skills.py`):

```
CORE_SKILLS, DEFAULT_MAX_REVIEW_AGE_DAYS, Skill, SkillAuditIssue, SkillAuditReport,
audit_skills, get_skill, list_skills, scaffold_core_skills, scaffold_skill
```

Plus non-`__all__` symbol used by import sites: `_parse_frontmatter`

## Steps

### Step 1: Write regression tests (TDD — write first, then verify RED→GREEN)

Create `tests/test_skills.py` covering every symbol in `__all__` plus `_parse_frontmatter`.
Tests confirm imports resolve both before and after migration.

```python
# tests/test_skills.py
import unittest
from gzkit.skills import (
    CORE_SKILLS, DEFAULT_MAX_REVIEW_AGE_DAYS, Skill,
    SkillAuditIssue, SkillAuditReport, audit_skills,
    get_skill, list_skills, scaffold_core_skills,
    scaffold_skill, _parse_frontmatter,
)
# Tests: isinstance/callable checks for each symbol
```

Run `uv run -m unittest tests.test_skills -v` — should PASS (baseline before migration).

### Step 2: Create destination directory structure

```bash
mkdir -p src/gzkit/skills/
for slug in $(ls .gzkit/skills/); do
    if [ -d ".gzkit/skills/$slug" ] && [ -f ".gzkit/skills/$slug/SKILL.md" ]; then
        mkdir -p "src/gzkit/skills/$slug"
    fi
done
```

### Step 3: Convert `skills.py` → `skills/__init__.py` via git mv

```bash
git mv src/gzkit/skills.py src/gzkit/skills/__init__.py
```

This preserves git history for the module. No content changes to the file.

### Step 4: Migrate all 70 SKILL.md files via git mv

```bash
find .gzkit/skills -maxdepth 2 -name "SKILL.md" | while read src; do
    slug=$(basename $(dirname "$src"))
    git mv "$src" "src/gzkit/skills/$slug/SKILL.md"
done
```

Verify: `find src/gzkit/skills/ -name SKILL.md | wc -l` → expect 70.
Verify: `test ! -f src/gzkit/skills.py` → file gone.
Verify: `test -f src/gzkit/skills/__init__.py` → file present.

### Step 5: Verify import continuity

```bash
python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills, audit_skills, SkillAuditIssue, SkillAuditReport, _parse_frontmatter, DEFAULT_MAX_REVIEW_AGE_DAYS, list_skills, scaffold_skill, Skill, get_skill; print('imports OK')"
python -c "from gzkit.skills_audit import DEFAULT_MAX_REVIEW_AGE_DAYS, audit_skills; print('skills_audit imports OK')"
```

### Step 6: Run full quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
```

All must exit 0.

### Step 7: Verify structural assertions

```bash
test ! -f src/gzkit/skills.py && echo "skills.py gone: OK"
test -f src/gzkit/skills/__init__.py && echo "__init__.py present: OK"
find src/gzkit/skills/ -name SKILL.md | wc -l  # expect 70
ls src/gzkit/skills/ | grep -v __init__.py | grep -v __pycache__ | wc -l  # expect 70
```

### Step 8: Run regression tests again (GREEN)

```bash
uv run -m unittest tests.test_skills -v
```

All must pass.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test ! -f src/gzkit/skills.py
test -f src/gzkit/skills/__init__.py
ls src/gzkit/skills/ | grep -v __init__.py | grep -v __pycache__ | wc -l    # expect 70
find src/gzkit/skills/ -name SKILL.md | wc -l                               # expect 70
python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills, audit_skills, SkillAuditIssue, _parse_frontmatter, DEFAULT_MAX_REVIEW_AGE_DAYS, list_skills, scaffold_skill; print('imports OK')"
```

## Notes

- Destination-in-mind before planning: `git mv` all SKILL.md files + module-to-package
  conversion, tested with import regression tests. Approach was clear from the chores
  precedent (OBPI-0.0.21-01).
- Rejected alternative: `cp` + `rm` — brief explicitly forbids; git history preservation
  requires `git mv`.
- Auxiliary content decision: SKILL.md moves; `agents/`, `assets/`, `references/`,
  `scripts/` subdirectories stay at `.gzkit/skills/<slug>/` for OBPI-06 to address.
- Scope collisions advisory: ADR-0.5.0 and ADR-0.4.0 OBPIs also list `src/gzkit/skills.py`
  as a contested path; those are pool/future ADRs, not in-progress — safe to proceed.
