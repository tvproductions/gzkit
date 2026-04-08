# Plan: OBPI-0.0.15-06 — Dogfood Patch Release (Version Drift Fix)

## Context

OBPI-0.0.15-06 was written to fix version drift where pyproject.toml=0.24.1 and
__init__.py=0.24.0. That drift has since evolved:

| Location | Brief expected | Actual now |
|----------|---------------|------------|
| pyproject.toml | 0.24.1 | **0.24.2** |
| __init__.py | 0.24.0 | **0.24.1** (drifted) |
| README badge | — | 0.24.2 |
| v0.24.1 tag | missing | exists |
| v0.24.2 tag | — | exists |
| docs/releases/ | — | doesn't exist |

**Key constraint:** `gz patch release` always bumps to the NEXT patch version.
It reads pyproject.toml (0.24.2) and proposes 0.24.3. It cannot sync to an
existing version. Therefore the dogfood will produce **v0.24.3**, not v0.24.2.

All 5 GHIs discovered since v0.24.2 are excluded (no `runtime` label, no
`src/gzkit/` diff). The release will have 0 qualifying GHIs — this is valid
dogfooding of the "version sync only" scenario.

## Approach: Run Full Ceremony for v0.24.3

### Step 1: Update brief to reflect v0.24.3 target

**File:** `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/obpis/OBPI-0.0.15-06-dogfood-fix-version-drift.md`

Update:
- REQ-2: All version locations show **0.24.3** (not 0.24.1)
- REQ-3: Manifest at `docs/releases/PATCH-v0.24.3.md`
- REQ-4: RELEASE_NOTES.md has **v0.24.3** entry
- REQ-5: Git tag **v0.24.3** exists
- Allowed Paths: `docs/releases/PATCH-v0.24.3.md` (not v0.24.1)
- Objective: note the evolved drift (0.24.2/0.24.1 → 0.24.3)
- Prerequisites: update version drift description

### Step 2: Run `gz patch release` (the command)

```bash
uv run gz patch release
```

This will:
- Call `sync_project_version(root, "0.24.3")` → update pyproject.toml, __init__.py, README badge
- Create `docs/releases/PATCH-v0.24.3.md` manifest (with all 5 GHIs marked "excluded")
- Append patch-release JSONL event to ledger

### Step 3: Draft RELEASE_NOTES.md entry

Append a v0.24.3 section to `RELEASE_NOTES.md` with narrative noting:
- Version sync release (no qualifying runtime GHIs)
- Fixes __init__.py drift from 0.24.1 → 0.24.3
- First dogfood invocation of `gz patch release`

### Step 4: Git-sync + tag

```bash
uv run gz git-sync --apply --lint --test
```

This commits all changes and creates the git tag.

### Step 5: GitHub release

```bash
gh release create v0.24.3 --title "v0.24.3" --notes-file docs/releases/PATCH-v0.24.3.md
```

Non-foundation version → GitHub release is required.

## Verification

```bash
# Version sync
python -c "import gzkit; print(gzkit.__version__)"   # 0.24.3
grep '^version' pyproject.toml                         # 0.24.3
grep 'badge/version' README.md                         # 0.24.3

# Artifacts
cat docs/releases/PATCH-v0.24.3.md                     # exists
grep 'v0.24.3' RELEASE_NOTES.md                        # exists
git tag | grep v0.24.3                                  # exists
gh release view v0.24.3                                 # exists

# Quality gates
uv run gz lint
uv run gz typecheck
uv run gz test
```

## Files Modified

- `docs/design/adr/.../OBPI-0.0.15-06-dogfood-fix-version-drift.md` (brief update)
- `pyproject.toml` (via `sync_project_version` at runtime)
- `src/gzkit/__init__.py` (via `sync_project_version` at runtime)
- `README.md` (via `sync_project_version` at runtime — badge only)
- `docs/releases/PATCH-v0.24.3.md` (new manifest, created by command)
- `RELEASE_NOTES.md` (v0.24.3 entry)
- `.gzkit/ledger.jsonl` (patch-release event, written by command)

## Risk

The only risk is that `gz patch release` may behave unexpectedly when all GHIs
are excluded. The dry-run confirms it still proposes v0.24.3 and proceeds. If
the non-dry-run hits an unexpected guard, we diagnose and fix per the STOP-on-BLOCKERS
instruction in the brief.
