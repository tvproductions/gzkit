# Plan: OBPI-0.0.32-03 — Rules Physical Migration

**OBPI:** OBPI-0.0.32-03-rules-physical-migration
**Parent ADR:** ADR-0.0.32-canonical-surface-packaging
**Lane:** Heavy | **Kind:** Foundation

## Context

ADR-0.0.32 promotes canonical surface files from `.gzkit/` into the Python
package under `src/gzkit/` to satisfy the T0 distribution invariant (ADR-0.0.31).
OBPI-03 mirrors what OBPI-01 did for skills, applied to rules. This is the
physical migration unit: convert `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py`
via `git mv`, and add byte-identical copies of all canonical rule files at
`src/gzkit/rules/<slug>.md` via `cp` (NOT `git mv` — the canonical
`.gzkit/rules/<slug>.md` files stay in place as the authored source-of-truth).

**Pre-migration findings (documented per brief STOP conditions):**

- On-disk rule count: **20** (brief/ADR state 14; 6 rules added post-authoring).
  Decision: migrate all 20.
- `src/gzkit/rules.py` is **594 lines** (brief says 563; drift since brief authoring).
  Not a blocker.
- All 20 files are `.md` — no JSON/YAML auxiliaries present (STOP condition clear).
- `src/gzkit/rules/` does NOT exist (STOP condition clear).
- Git working tree clean (only untracked `.claude/plans/.plan-audit-receipt-OBPI-0.0.32-03.json`).

**Scope collision advisory:**
4 sibling-ADR OBPIs (ADR-0.17.0-01, ADR-0.17.0-02, ADR-0.16.0-02, ADR-0.0.38-01)
list `src/gzkit/rules.py` as a contested path. All are Draft/future ADRs, not
in-progress. This OBPI renames the file to `__init__.py`; those sibling ADRs will
need to target the new path. Not a blocker for this OBPI.

## Files

**Converted:**
- `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` via `git mv` (no content changes)

**Created (new package copies — NOT moved from canonical):**
- `src/gzkit/rules/<slug>.md` (20 files) — byte-identical copies via `cp`
- `src/gzkit/rules/__init__.py` — receives `src/gzkit/rules.py` contents unchanged

**Modified (test additions only):**
- `tests/test_rules.py` — add `TestRulesLayoutDualSurface` class with:
  - `test_rules_py_does_not_exist` — asserts `src/gzkit/rules.py` absent
  - `test_rules_init_exists` — asserts `src/gzkit/rules/__init__.py` present
  - `test_dual_surface_byte_parity` — asserts every `.gzkit/rules/*.md` has identical copy at `src/gzkit/rules/`
  - `test_dual_surface_rule_count` — asserts count matches between both surfaces

**NOT modified (per denied paths):**
- `pyproject.toml` — no wheel-include changes (OBPI-06)
- `src/gzkit/commands/init_cmd.py` — no integration (OBPI-04)
- `src/gzkit/rules/__init__.py` — no `CORE_RULES`/`scaffold_core_rules` (OBPI-04)

## Public Symbol Enumeration (from `src/gzkit/rules.py`)

Full symbol set to be re-exported without change through `src/gzkit/rules/__init__.py`:

```
ClassifiedRule, RuleFrontmatter, CanonicalRule
classify_instruction_rules
sync_claude_rules, sync_nested_agents_md
validate_rule_placement
load_rule, load_rules
render_rule_for_claude, render_rule_for_copilot, render_rules_to_dir
_parse_instruction_frontmatter, _extract_body_after_frontmatter
_extract_subtree_prefix, _parse_canonical_frontmatter
_convert_apply_to_paths, _is_global_pattern, _is_vendor_mirror_prefix
_cleanup_stale_nested_agents, _skip_leading_comments
_GENERATED_MARKER, _RENDER_HEADER
```

Import sites confirmed (no change needed):
- `src/gzkit/sync.py`: `sync_claude_rules`, `sync_nested_agents_md`
- `src/gzkit/instruction_audit.py`: `_convert_apply_to_paths`, `_extract_body_after_frontmatter`, `_parse_instruction_frontmatter`
- `src/gzkit/sync_surfaces.py`: `load_rules`, `render_rules_to_dir`, `sync_claude_rules`, `sync_nested_agents_md`
- `src/gzkit/instruction_eval.py`: `_parse_instruction_frontmatter`, `_extract_body_after_frontmatter`
- `src/gzkit/registry.py`: `RuleFrontmatter`
- `src/gzkit/validate_pkg/surface.py`: `validate_rule_placement`

## Steps

### Step 1: Confirm test_rules.py baseline and add dual-surface regression tests (TDD — RED)

Check `tests/test_rules.py` for any existing `TestRulesLayoutDualSurface` class.
If absent, add it. The dual-surface tests will FAIL until Step 3 creates the
`src/gzkit/rules/` package.

```python
# In tests/test_rules.py — add TestRulesLayoutDualSurface:
import pathlib
class TestRulesLayoutDualSurface(unittest.TestCase):
    def _repo_root(self):
        return pathlib.Path(__file__).parent.parent

    def test_rules_py_does_not_exist(self):
        self.assertFalse((self._repo_root() / "src/gzkit/rules.py").exists(),
                         "src/gzkit/rules.py must not exist after migration")

    def test_rules_init_exists(self):
        self.assertTrue((self._repo_root() / "src/gzkit/rules/__init__.py").exists(),
                        "src/gzkit/rules/__init__.py must exist after migration")

    def test_dual_surface_byte_parity(self):
        canonical = self._repo_root() / ".gzkit/rules"
        package = self._repo_root() / "src/gzkit/rules"
        canonical_slugs = {p.name for p in canonical.glob("*.md")}
        package_slugs = {p.name for p in package.glob("*.md")} if package.exists() else set()
        missing = canonical_slugs - package_slugs
        self.assertEqual(missing, set(), f"Missing package copies: {missing}")
        for slug in canonical_slugs:
            self.assertEqual((canonical / slug).read_bytes(),
                             (package / slug).read_bytes(),
                             f"Byte drift in {slug}")

    def test_dual_surface_rule_count(self):
        canonical = self._repo_root() / ".gzkit/rules"
        package = self._repo_root() / "src/gzkit/rules"
        canonical_count = len(list(canonical.glob("*.md")))
        package_count = len(list(package.glob("*.md"))) if package.exists() else 0
        self.assertEqual(canonical_count, package_count,
                         f"Rule count mismatch: canonical={canonical_count}, package={package_count}")
```

Run `uv run -m unittest tests.test_rules.TestRulesLayoutDualSurface -v` — expect FAIL
(RED phase: `src/gzkit/rules/` doesn't exist yet).

Also run `uv run -m unittest tests.test_rules -v` to confirm all existing tests pass
before the migration begins (baseline GREEN for the public-symbol tests).

### Step 2: Create the package directory

```bash
mkdir -p src/gzkit/rules/
```

### Step 3: Convert `rules.py` → `rules/__init__.py` via git mv

```bash
git mv src/gzkit/rules.py src/gzkit/rules/__init__.py
```

This preserves git history for the module file. No content changes.

### Step 4: Copy all 20 `.gzkit/rules/*.md` to `src/gzkit/rules/` via cp

```bash
for f in .gzkit/rules/*.md; do
    cp "$f" "src/gzkit/rules/$(basename "$f")"
done
```

Verify:
```bash
ls src/gzkit/rules/*.md | wc -l                             # expect 20
diff -r .gzkit/rules/ src/gzkit/rules/ \
    --exclude=__init__.py --exclude=__pycache__              # expect no diff
```

### Step 5: Verify import continuity

```bash
python -c "
from gzkit.rules import (
    ClassifiedRule, RuleFrontmatter, CanonicalRule,
    classify_instruction_rules,
    sync_claude_rules, sync_nested_agents_md,
    validate_rule_placement,
    load_rule, load_rules,
    render_rule_for_claude, render_rule_for_copilot, render_rules_to_dir,
    _parse_instruction_frontmatter, _extract_body_after_frontmatter,
    _extract_subtree_prefix, _parse_canonical_frontmatter,
)
print('imports OK')
"
```

### Step 6: Run regression tests (GREEN)

```bash
uv run -m unittest tests.test_rules.TestRulesLayoutDualSurface -v
uv run -m unittest tests.test_rules -v
```

All must pass.

### Step 7: Run full quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
```

All must exit 0.

### Step 8: Structural assertions

```bash
test ! -f src/gzkit/rules.py && echo "rules.py gone: OK"
test -f src/gzkit/rules/__init__.py && echo "__init__.py present: OK"
ls .gzkit/rules/*.md | wc -l                                # expect 20 (canonical retained)
ls src/gzkit/rules/*.md | wc -l                             # expect 20 (package copy)
diff -r .gzkit/rules/ src/gzkit/rules/ \
    --exclude=__init__.py --exclude=__pycache__              # expect no diff
```

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test ! -f src/gzkit/rules.py
test -f src/gzkit/rules/__init__.py
ls .gzkit/rules/*.md | wc -l                                # expect 20 (retained canonical)
ls src/gzkit/rules/*.md | wc -l                             # expect 20 (package copy)
diff -r .gzkit/rules/ src/gzkit/rules/ --exclude=__init__.py --exclude=__pycache__   # no diff
python -c "from gzkit.rules import RuleFrontmatter, ClassifiedRule, load_rules, render_rules_to_dir, sync_claude_rules, sync_nested_agents_md, validate_rule_placement; print('imports OK')"
```

## Notes

- **Destination-in-mind before planning:** module-to-package conversion (`git mv`) + `cp` 20 rule files + dual-surface byte-parity test. Approach established by OBPI-01 skills precedent.
- **Rejected alternative: `git mv` for `.md` files** — brief explicitly requires `cp` because `.gzkit/rules/<slug>.md` stays as authored canonical; `src/gzkit/rules/<slug>.md` is a new artifact added alongside.
- **Stale count resolution:** 20 files, not 14. All are `.md` — no STOP condition triggered. The brief's "14" count is stale metadata; the implementation migrates all present files.
- **Import sites:** No import site modifications needed; `git mv` of `rules.py` → `rules/__init__.py` preserves all `from gzkit.rules import X` resolution automatically.
- **Scope collisions advisory:** 4 sibling-ADR OBPIs contesting `src/gzkit/rules.py` are Draft future ADRs; not in-progress; safe to proceed.
