---
id: OBPI-0.0.15-06-dogfood-fix-version-drift
parent: ADR-0.0.15-ghi-driven-patch-release-ceremony
item: 6
lane: Heavy
status: Completed
---

# OBPI-0.0.15-06: Dogfood — Fix 0.24.1 Version Drift

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- **Checklist Item:** #6 - "Dogfood: fix 0.24.1 version drift as first invocation"

**Status:** Draft

## Objective

Run `gz patch release` for real against existing version drift (pyproject.toml
says 0.24.2, `__init__.py` says 0.24.1). The original 0.24.0/0.24.1 drift was
resolved by prior releases; the current drift is between 0.24.2 and 0.24.1.
The command bumps to the next patch version (0.24.3), fixing the drift by
moving forward. This is the first real invocation — proving the command works
end-to-end and fixing a real governance gap simultaneously.

## Lane

**Heavy** - Creates a GitHub release and git tag, which are external-facing
artifacts. Requires human attestation that the release is correct.

## Allowed Paths

- `pyproject.toml` (via `sync_project_version` at runtime)
- `src/gzkit/__init__.py` (via `sync_project_version` at runtime)
- `RELEASE_NOTES.md`
- `docs/releases/PATCH-v0.24.3.md` (new manifest)

## Denied Paths

- `src/gzkit/commands/patch_release.py` — no code changes, just invocation
- `src/gzkit/commands/closeout.py` — no modifications

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz patch release` MUST be invoked as the fix mechanism —
   NEVER manually edit version files
2. REQUIREMENT: After completion, pyproject.toml, `__init__.py`, and README
   badge MUST all show 0.24.3
3. REQUIREMENT: A `PATCH-v0.24.3.md` manifest MUST exist in `docs/releases/`
4. REQUIREMENT: RELEASE_NOTES.md MUST have a v0.24.3 entry
5. REQUIREMENT: Git tag `v0.24.3` MUST exist (non-foundation — this is a
   feature-line patch, not a foundation patch)

> STOP-on-BLOCKERS: if `gz patch release` has bugs discovered during dogfooding,
> fix them in earlier OBPIs before retrying.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- [ ] OBPI-0.0.15-01 through OBPI-0.0.15-05 (all prerequisites)

**Prerequisites (check existence, STOP if missing):**

- [ ] `gz patch release` command fully operational
- [ ] Ceremony skill exists and is registered
- [ ] Current version drift confirmed: pyproject.toml=0.24.2, __init__.py=0.24.1

**Existing Code (understand current state):**

- [ ] Current git tags: `git tag --sort=-v:refname | head -5`
- [ ] Current GitHub releases: `gh release list --limit 5`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] RELEASE_NOTES.md updated with v0.24.1 entry

### Gate 4: BDD (Heavy)

- [ ] N/A — dogfood invocation, not new code

### Gate 5: Human (Heavy)

- [ ] Human attestation that version drift is resolved and release is correct

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "import gzkit; print(gzkit.__version__)"  # Should print 0.24.3
grep version pyproject.toml | head -1                # Should show 0.24.3
git tag | grep v0.24.3                               # Should exist
gh release view v0.24.3                              # Should exist
cat docs/releases/PATCH-v0.24.3.md                   # Should exist
```

## Acceptance Criteria

- [ ] REQ-0.0.15-06-01: Version drift resolved via `gz patch release`
- [ ] REQ-0.0.15-06-02: All version locations agree on 0.24.3
- [ ] REQ-0.0.15-06-03: Patch manifest exists at `docs/releases/PATCH-v0.24.3.md`
- [ ] REQ-0.0.15-06-04: RELEASE_NOTES.md has v0.24.3 entry
- [ ] REQ-0.0.15-06-05: Git tag and GitHub release for v0.24.3 exist

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


uv run gz patch release -> Version bumped: 0.24.2 -> 0.24.3. Updated: pyproject.toml, src/gzkit/__init__.py, README.md. Manifest: docs/releases/PATCH-v0.24.3.md. Ledger: patch-release event appended.

### Implementation Summary


- Files created/modified: docs/releases/PATCH-v0.24.3.md (new), pyproject.toml, src/gzkit/__init__.py, README.md, RELEASE_NOTES.md, .gzkit/ledger.jsonl
- Tests added: none (dogfood invocation, not new code)
- Date completed: 2026-04-08
- Attestation status: Human attested (Jeffry)
- Defects noted: Brief frontmatter id used short-form OBPI-0.0.15-06 instead of full slug (fixed inline)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: Completed
- Date: 2026-04-08

---

**Brief Status:** Completed

**Date Completed:** 2026-04-08

**Evidence Hash:** -
