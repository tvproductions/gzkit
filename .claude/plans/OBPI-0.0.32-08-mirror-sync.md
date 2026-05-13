# Plan: OBPI-0.0.32-08-mirror-sync — Canonical Surface Sync

## OBPI

OBPI-0.0.32-08-mirror-sync

## Context

`gz agent sync control-surfaces` currently propagates `.gzkit/<surface>/` to
vendor mirrors (`.claude/`, `.github/`, `.agents/`) but does NOT propagate to
`src/gzkit/<surface>/` (the wheel-shipping pkg copies). GHI #449 tracks this
gap for skills. OBPI-08 closes it for every dual-surface family: skills, rules,
personas, templates, and chores (canonical-class files only, per OBPI-13
classifier).

Current `sync_all()` in `src/gzkit/sync_surfaces.py`:
- Reads `.gzkit/skills/` → vendor mirrors ✓ (via `sync_skill_mirrors`)
- Reads `.gzkit/rules/` → vendor mirrors ✓ (via `render_rules_to_dir`)
- Reads `.gzkit/personas/` → vendor mirrors ✓ (via `sync_persona_mirrors`)
- Does NOT copy `.gzkit/<surface>/` → `src/gzkit/<surface>/` ✗ (the gap)

Key files:
- `src/gzkit/sync_surfaces.py` (709 lines) — `sync_all()` entry point
- `src/gzkit/sync_skills.py` (576 lines) — `sync_skill_mirror()` (file-copy primitive)
- `src/gzkit/chores/__init__.py` — `_classify_chore_file()` available

## Files

Modified:
- `src/gzkit/sync_surfaces.py` — add `sync_pkg_surfaces()` and wire into `sync_all()`
- `.gzkit/rules/skill-surface-sync.md` — re-affirm + document broadened sync coverage

Created:
- `tests/test_sync_surfaces.py` — new test class for pkg-surface sync (append to existing)
- `features/agent_sync.feature` — BDD idempotency scenario tagged @REQ-0.0.32-08-01
- `docs/user/manpages/gz-agent.md` — gz agent top-level manpage with broadened semantics

Note: `.claude/rules/skill-surface-sync.md` is a vendor mirror of `.gzkit/rules/skill-surface-sync.md`; the edit target is the canonical `.gzkit/` path; sync propagates the change.

## Steps

### Step 1 — RED: Write failing tests

Add `TestSyncPkgSurfaces` class to `tests/test_sync_surfaces.py`. Tests must
fail before Step 2 implements the function.

Tests to add:
1. `test_sync_pkg_surfaces_skills_resolves_canonical_from_gzkit` — mock fs with
   `.gzkit/skills/gz-prd/SKILL.md` populated; call `sync_pkg_surfaces()`; assert
   `src/gzkit/skills/gz-prd/SKILL.md` written with same bytes; assert
   `.gzkit/skills/gz-prd/SKILL.md` NOT modified.
2. `test_sync_pkg_surfaces_rules_resolves_canonical_from_gzkit` — same for rules;
   `.gzkit/rules/adr-audit.md` → `src/gzkit/rules/adr-audit.md`.
3. `test_sync_pkg_surfaces_dual_direction_single_call` — one `sync_pkg_surfaces()`
   call writes to both `src/gzkit/skills/` AND `src/gzkit/rules/`.
4. `test_sync_pkg_surfaces_idempotent` — call twice; second call returns empty list
   (no writes when bytes already match).
5. `test_sync_pkg_surfaces_chores_canonical_only` — chores runtime-state
   (`CHORE-LOG.md`, `proofs/`) never written to pkg; canonical `CHORE.md` IS
   written; package-only `__init__.py` never written to canonical side.

### Step 2 — GREEN: Implement `sync_pkg_surfaces()`

In `src/gzkit/sync_surfaces.py`, add:

```python
def sync_pkg_surfaces(project_root: Path, config: GzkitConfig) -> list[str]:
    """Copy .gzkit/<surface>/ → src/gzkit/<surface>/ for every dual-surface family.

    Propagation order: skills, rules, personas, templates, chores (canonical
    class only, per _classify_chore_file). Idempotent: skips files where
    source and target bytes already match.
    """
```

Surface families to cover:
- Skills: `.gzkit/skills/<slug>/SKILL.md` → `src/gzkit/skills/<slug>/SKILL.md`
- Rules: `.gzkit/rules/<slug>.md` → `src/gzkit/rules/<slug>.md`
- Personas: `.gzkit/personas/<slug>.md` → `src/gzkit/personas/<slug>.md`
- Templates: `.gzkit/templates/<name>.md` → `src/gzkit/templates/<name>.md`
- Chores: only `canonical`-classified files per `_classify_chore_file`

Re-use `sync_skill_mirror()` for the skills leg (already handles idempotency,
mkdir, excludes retired, skips `__pycache__`). For rules, write a parallel
`sync_rules_to_pkg()` helper or inline the file-copy loop.

### Step 3 — Wire `sync_pkg_surfaces()` into `sync_all()`

In `sync_all()`, insert the call BEFORE the vendor-mirror steps (after manifest
generation, after `bootstrap_canonical_skills`):

```python
# Pkg surfaces: .gzkit/<surface>/ → src/gzkit/<surface>/
updated.extend(sync_pkg_surfaces(project_root, config))
```

### Step 4 — Update `.gzkit/rules/skill-surface-sync.md`

Bump rule version (patch: `0.4.0 → 0.4.1` or minor if procedure changes).

Add to § Non-negotiable rules or § Procedure:
> One `gz agent sync control-surfaces` invocation now covers BOTH the
> wheel-shipping byte-parity copy (`src/gzkit/<surface>/`) AND vendor mirrors
> (`.[vendor]/<surface>/`). No separate copy step is needed.

After editing `.gzkit/rules/skill-surface-sync.md`, run sync to propagate to
`.claude/rules/skill-surface-sync.md`.

### Step 5 — Create `docs/user/manpages/gz-agent.md`

Top-level manpage for the `gz agent` subcommand group. Document:
- `gz agent sync control-surfaces` — the broadened semantics (one canonical
  source `.gzkit/<surface>/`, two derived surface families: `src/gzkit/` for
  wheel-shipping and `.[vendor]/` for vendor mirrors)
- Surface families covered: skills, rules, personas, templates, chores
- Chores carve-out: canonical content syncs; runtime-state and package-only exempt

### Step 6 — Create `features/agent_sync.feature`

BDD scenario exercising dual-direction idempotency.

```gherkin
@REQ-0.0.32-08-01
Scenario: sync propagates canonical to pkg and vendor mirrors
  Given a clean project with .gzkit/skills/ and .gzkit/rules/ populated
  When I run "gz agent sync control-surfaces"
  Then src/gzkit/skills/ is byte-equivalent to .gzkit/skills/
  And .claude/skills/ is byte-equivalent to .gzkit/skills/
  And src/gzkit/rules/ is byte-equivalent to .gzkit/rules/
  And .claude/rules/ is byte-equivalent to .gzkit/rules/
  When I run "gz agent sync control-surfaces" again
  Then no files are written (idempotent)
```

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.test_sync_surfaces -v

# Byte-parity tests pass post-sync
uv run -m unittest tests.test_skills.TestSkillsLayoutDualSurface -v
uv run -m unittest tests.test_rules.TestRulesLayoutDualSurface -v

# File counts match
python3 -c "
import pathlib
gzkit = pathlib.Path('.gzkit')
src = pathlib.Path('src/gzkit')
print('skills .gzkit:', len(list((gzkit/'skills').rglob('SKILL.md'))))
print('skills src/gzkit:', len(list((src/'skills').rglob('SKILL.md'))))
print('rules .gzkit:', len(list((gzkit/'rules').glob('*.md'))))
print('rules src/gzkit:', len(list((src/'rules').glob('*.md'))))
"

uv run gz validate --surfaces
uv run mkdocs build --strict
uv run -m behave features/agent_sync.feature --tags=@REQ-0.0.32-08-01
uv run gz check
```

## Notes

- Confidence: >90%. Plan grounded in direct code reading of sync_surfaces.py (709L),
  sync_skills.py (576L), and live git state.
- `sync_skill_mirror()` is the reusable primitive (handles idempotency, mkdir, retired
  exclusion, pycache skip). Extend it for rules/personas/templates or inline minimal
  parallel loops.
- Chores carve-out: import `_classify_chore_file` from `gzkit.chores` and filter to
  `class == "canonical"` before copying.
- Brief correction noted: `.claude/rules/skill-surface-sync.md` in Allowed Paths should
  be `.gzkit/rules/skill-surface-sync.md` (vendor mirror vs canonical edit target).
  Plan targets the canonical path.
- Destination-in-mind: sync_pkg_surfaces as a new function in sync_surfaces.py wired
  into sync_all() before vendor mirrors.
- Rejected alternatives: (a) adding pkg sync to sync_skill_mirror() directly — rejected
  because that function is a general "source → target" copier; adding a pkg-specific
  leg there breaks the single-responsibility; (b) separate CLI flag for pkg sync —
  rejected per ADR-08 which mandates one invocation covers both families.
