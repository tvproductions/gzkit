---
id: OBPI-0.0.32-08-mirror-sync
parent: ADR-0.0.32-canonical-surface-packaging
item: 8
lane: Heavy
status: Completed
---

# OBPI-0.0.32-08-mirror-sync: Canonical Surface Sync

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #8 — "Canonical surface sync — broaden `gz agent sync control-surfaces` so a single invocation propagates `.gzkit/<surface>/` (authored canonical) to BOTH `src/gzkit/<surface>/` (wheel-shipping byte-parity copy, dev-time only) AND `.[vendor]/<surface>/` (vendor mirrors: `.claude/skills/`, `.claude/rules/`, `.claude/personas/`, `.github/skills/`, `.github/instructions/`, `.github/personas/`, `.agents/personas/`); covers every dual-surface family (skills, rules, personas, templates, chores per § Canonical-routing scope); honors chores carve-out rules (canonical content syncs; package-only and runtime-state files exempt per § Named exceptions); idempotent on freshly-synced state; absorbs GHI #449 (`.gzkit/` → `src/gzkit/` dev-time sync) and the existing `.gzkit/` → `.[vendor]/` mirror flow into one mechanism. Depends on OBPI-03/04/09/11/13 landing first so every dual-surface family is established before the sync mechanism covers it."

**Status:** Draft

## Objective

Broaden `gz agent sync control-surfaces` so it is the single mechanism that propagates `.gzkit/<surface>/` (authored canonical source-of-truth) to every derived surface in this repo, across EVERY dual-surface family in ADR-0.0.32 § Canonical-routing scope (skills, rules, personas, templates, chores):

1. `.gzkit/<surface>/` → `src/gzkit/<surface>/` (dev-time wheel-shipping byte-parity copy) — closes GHI #449's missing convenience step that currently forces operators to remember `cp .gzkit/<surface>/<slug>.md src/gzkit/<surface>/<slug>.md` after every authored edit or trip the byte-parity test for that surface.
2. `.gzkit/<surface>/` → `.[vendor]/<surface>/` (vendor mirrors at `.claude/skills/`, `.claude/rules/`, `.claude/personas/`, `.github/skills/`, `.github/instructions/`, `.github/personas/`, `.agents/personas/`, plus any future vendor surface) — existing flow rebased to read from `.gzkit/` rather than `src/gzkit/`. Personas vendor mirrors are a transformed render (intentional per § Named exceptions); other vendor mirrors are byte-equivalent modulo documented vendor transformation.
3. **Chores carve-out enforcement**: when syncing chores, OBPI-08 MUST consume the class-classifier authored by OBPI-13 (`_classify_chore_file` or equivalent). Only **canonical**-classified files participate in the sync. **package_only** files NEVER appear at the `.gzkit/` side. **runtime_state** files (CHORE-LOG.md, proofs/<artifact>, .gitkeep markers) NEVER sync — each surface owns its runtime-state independently.

After this OBPI lands, the canonical-routing invariant declared in ADR-0.0.32 § Decision is mechanically enforced for every dual-surface family: a single `gz agent sync control-surfaces` run after editing `.gzkit/<surface>/<slug>.md` leaves `src/gzkit/<surface>/<slug>.md` and `.[vendor]/<surface>/<slug>.md` byte-equivalent (modulo persona vendor transformation + chores carve-outs) to the authored source. Re-running the same command on freshly-synced state is a clean no-op across every family. The byte-parity tests from OBPI-01 (skills), OBPI-03 (rules), OBPI-09 (personas), OBPI-11 (templates), and OBPI-13 (chores canonical-class) all pass after every sync run.

## Lane

**Heavy** — changes the runtime contract of `gz agent sync control-surfaces` (single sync run now propagates to two derived surface families), modifies generated `src/gzkit/<surface>/` and `.[vendor]/<surface>/` outputs, and gates closeout of the entire ADR-0.0.32 chain on clean post-sync state across both derived surfaces. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/sync.py` (or `src/gzkit/sync_surfaces.py`, `src/gzkit/sync_skills.py`, `src/gzkit/skills_mirror.py`, `src/gzkit/rules/__init__.py` — wherever the sync logic lives) — broaden canonical-source resolution to `.gzkit/<surface>/`; add the `.gzkit/<surface>/ → src/gzkit/<surface>/` propagation step alongside the existing vendor-mirror propagation
- `src/gzkit/cli/parser_*.py` (if `gz agent sync control-surfaces` flag dispatch needs an adjustment) — minimal-surface change
- `src/gzkit/skills/<slug>/SKILL.md` (~70 files) — regenerated outputs (byte-equivalent copies of `.gzkit/skills/<slug>/SKILL.md`)
- `src/gzkit/rules/<slug>.md` (14 files, once OBPI-03 lands) — regenerated outputs (byte-equivalent copies of `.gzkit/rules/<slug>.md`)
- `.claude/skills/<slug>/SKILL.md` (~70 files) — regenerated outputs
- `.claude/rules/<slug>.md` (14 files) — regenerated outputs
- `.github/skills/<slug>/SKILL.md` (mirror) — regenerated outputs
- `.github/instructions/<slug>.md` — regenerated outputs
- `.gzkit/manifest.json` — refresh `Updated:` field and any per-surface metadata
- `tests/test_sync.py`, `tests/test_skills_mirror.py`, `tests/test_rules.py` — unit-tier tests for canonical-resolution-from-`.gzkit/` change and dual-direction propagation
- `features/agent_sync.feature` — behave scenario asserting post-sync state is idempotent (re-running sync is a clean no-op across both derived surface families)
- `docs/user/manpages/gz-agent.md` — document the broadened sync semantics (one canonical source, two derived surface families)
- `.claude/rules/skill-surface-sync.md` — re-affirm `.gzkit/` first and document that one `gz agent sync` invocation now covers both wheel-shipping copy AND vendor mirrors

## Denied Paths

- `src/gzkit/skills/__init__.py`, `src/gzkit/rules/__init__.py` (logic edits) — canonical-resolution change is allowed; package-API edits are out of scope
- `.gzkit/skills/**/SKILL.md`, `.gzkit/rules/**.md` content edits — canonical surface is read-only from this OBPI's perspective; the sync only copies FROM `.gzkit/`, never writes into it
- `pyproject.toml` — wheel includes belong to OBPI-06
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `data/distribution_baseline_manifest.json` — baseline manifest belongs to OBPI-06
- `docs/governance/trust-doctrine.md` — T0 doctrine prose belongs to OBPI-0.0.31-01

## Requirements (FAIL-CLOSED)

1. `gz agent sync control-surfaces` MUST resolve canonical content from `.gzkit/<surface>/` (the authored source-of-truth) for every dual-surface family. The sync function MUST NOT read canonical content from `src/gzkit/<surface>/` or from vendor mirrors — `src/gzkit/` and `.[vendor]/` are derived-only.
2. A single `gz agent sync control-surfaces` invocation MUST propagate `.gzkit/<surface>/<slug>/SKILL.md` (skills) AND `.gzkit/rules/<slug>.md` (rules) — and, by composition, any future canonical surface that adopts the dual-surface model — to BOTH `src/gzkit/<surface>/<slug>/` (wheel-shipping byte-parity copy) AND `.[vendor]/<surface>/<slug>/` (vendor mirrors), in that order.
3. After a sync run on a clean working tree, BOTH derived surfaces MUST be byte-equivalent to the canonical source (modulo any documented vendor-specific transformation):
   - `src/gzkit/skills/<slug>/SKILL.md` byte-identical to `.gzkit/skills/<slug>/SKILL.md` for every slug
   - `src/gzkit/rules/<slug>.md` byte-identical to `.gzkit/rules/<slug>.md` for every rule
   - `.claude/skills/<slug>/SKILL.md` byte-equivalent (modulo documented vendor transformation) to `.gzkit/skills/<slug>/SKILL.md`
   - Same for `.claude/rules/`, `.github/skills/`, `.github/instructions/`
4. Re-running `gz agent sync control-surfaces` on freshly-synced state MUST produce ZERO writes (idempotent across BOTH derived surfaces; confirms the canonical-resolution path is stable and the dual-direction propagation is deterministic).
5. The number of files in `src/gzkit/skills/<slug>/SKILL.md` MUST equal the number in `.gzkit/skills/<slug>/SKILL.md` (~70) after a sync; same for `.claude/skills/` ↔ ~70 and `.github/skills/` ↔ ~70; same for `src/gzkit/rules/*.md` ↔ `.gzkit/rules/*.md` ↔ 14 and `.claude/rules/` ↔ 14 and `.github/instructions/` ↔ 14.
6. `.gzkit/manifest.json` MUST refresh on each sync run with the new `Updated:` date and surface counts (one entry per dual-surface family).
7. Unit tests MUST cover:
   - canonical-resolution-from-`.gzkit/` for both skills and rules (mock filesystem with `.gzkit/` populated)
   - dual-direction propagation (one sync writes to both `src/gzkit/` AND `.[vendor]/`)
   - sync regenerates `src/gzkit/` byte-equivalent to `.gzkit/` for both skills and rules
   - sync regenerates `.[vendor]/` byte-equivalent to `.gzkit/` (modulo documented transformations)
   - running sync twice in a row produces no diffs across either derived surface
   - byte-parity tests from OBPI-01 (and OBPI-03 when it lands) pass post-sync
8. A behave scenario MUST run sync against a clean post-promotion fixture and assert no-op idempotency on the second run across BOTH derived surface families, tagged `@REQ-0.0.32-08-NN`.
9. `uv run gz check` MUST exit 0 with the broadened sync path.
10. `gz validate --surfaces` MUST pass post-sync; mirror-drift detection (already covered by existing `--surfaces` audit) MUST report clean for BOTH `src/gzkit/` ↔ `.gzkit/` and `.[vendor]/` ↔ `.gzkit/`.
11. `gz validate --distribution` (from OBPI-07) MUST pass — this OBPI does not introduce on-disk-not-baseline drift.
12. `.claude/rules/skill-surface-sync.md` MUST be re-affirmed: "Edit `.gzkit/` first" remains canon; the rule body MUST document that one `gz agent sync control-surfaces` invocation now covers both wheel-shipping byte-parity AND vendor mirrors.

> STOP-on-BLOCKERS:
> - If OBPI-0.0.32-03 (rules dual-surface), OBPI-0.0.32-09 (personas dual-surface), OBPI-0.0.32-11 (templates reverse-migration), or OBPI-0.0.32-13 (chores normalization + class-classifier) has not landed, STOP — every dual-surface family must exist before the sync mechanism covers it. Skills (OBPI-01 attested) are dual-surface and can be synced independently if a partial-coverage interim sync is acceptable per operator judgment.
> - If the OBPI-13 chores class-classifier is not available (not yet exported as Python helper or JSON data file), STOP — without the classifier, chores cannot be safely synced (risk of overwriting runtime-state or propagating package-only files onto canonical surfaces).
> - If `gz agent sync control-surfaces` currently reads canonical content from `src/gzkit/` or from `.gzkit/` indirectly (e.g. via a registry that resolves to `src/gzkit/`), the canonical-resolution refactor is broader than a path change — surface that as a sub-task and decompose if scope expansion is required.
> - If a derived surface has accumulated hand-edits between sync runs (e.g. someone edited `.claude/skills/<slug>/SKILL.md` or `src/gzkit/skills/<slug>/SKILL.md` directly without editing `.gzkit/` first), STOP and reconcile per `.claude/rules/skill-surface-sync.md` § Conflict resolution. The canonical-routing model is fail-closed on inverse edits.
> - If `gz validate --surfaces` reports drift before this OBPI starts, STOP — fix the drift first; this OBPI's success criterion depends on a clean baseline.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — canonical-routing direction paragraph (the binding `.gzkit/` ↔ {`src/gzkit/`, `.[vendor]/`} model)
- [ ] Parent ADR § Consequences (Negative) — names the dual-surface byte-parity discipline this OBPI mechanizes
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.claude/rules/skill-surface-sync.md` — "Edit `.gzkit/` first" canon; this OBPI re-affirms and broadens the sync coverage
- [ ] `AGENTS.md` § Skills Protocol — discovery + sync expectations
- [ ] `.claude/rules/tool-skill-runbook-alignment.md` — Invariant 1, 2, 3 (sync must not break tool↔skill alignment)
- [ ] GHI #449 — the missing `.gzkit/ → src/gzkit/` convenience step this OBPI absorbs

**Context — sibling OBPIs:**

- [ ] OBPI-0.0.32-01 (attested) — established dual-surface for skills + the byte-parity test this OBPI's sync must keep passing
- [ ] OBPI-0.0.32-03 — establishes dual-surface for rules; must land before this OBPI covers rules
- [ ] OBPI-0.0.32-06 — baseline manifest is invariant under sync (sync regeneration MUST NOT change the canonical surface fingerprints captured in the manifest)
- [ ] OBPI-0.0.32-07 — `gz validate --distribution` must continue to pass after this OBPI's sync runs

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-01 landed (dual-surface for skills active; byte-parity test in `tests/test_skills.py`)
- [ ] OBPI-0.0.32-03 landed (dual-surface for rules active; byte-parity test in `tests/test_rules.py` or equivalent)
- [ ] `gz agent sync control-surfaces` currently runnable (sanity check before refactor)
- [ ] `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/` exist as directories
- [ ] `gz validate --surfaces` exits 0 on the pre-OBPI state (so any drift this OBPI surfaces is genuinely from the sync-mechanism change, not pre-existing)

**Existing Code:**

- [ ] Read `src/gzkit/sync.py`, `sync_surfaces.py`, `sync_skills.py`, `skills_mirror.py` end-to-end (the sync surface is fragmented — understand which file owns what and which currently reads from where before editing)
- [ ] Read `.gzkit/manifest.json` schema before refresh logic lands
- [ ] Read existing `gz validate --surfaces` check in `trust_audits` to understand what mirror-drift detection already covers and how to extend it to cover `src/gzkit/` ↔ `.gzkit/` parity
- [ ] Read `tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity` (OBPI-01 landing) to understand the byte-parity assertion shape the sync must keep green

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #8 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for canonical-resolution-from-`.gzkit/` + dual-direction propagation + idempotent sync fail before implementation
- [ ] GREEN: tests pass after the resolution-path change and the dual-target sync run
- [ ] Coverage above 40% floor

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-agent.md` updated for the broadened sync semantics (canonical from `.gzkit/`, two derived surface families)
- [ ] `.claude/rules/skill-surface-sync.md` re-affirmed: "Edit `.gzkit/` first" + one `gz agent sync` invocation covers both derived surface families
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] `features/agent_sync.feature` (or equivalent) extended with the dual-direction idempotency scenario tagged `@REQ-0.0.32-08-01`

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# First sync after a canonical edit: regenerates both derived surfaces
echo "test edit" >> .gzkit/skills/gz-prd/SKILL.md   # simulate authored edit
uv run gz agent sync control-surfaces
git status src/gzkit/skills/ .claude/skills/ .github/skills/   # expect changes in both
git checkout -- .gzkit/skills/gz-prd/SKILL.md src/gzkit/skills/ .claude/ .github/   # cleanup

# Second sync immediately after a clean sync: idempotent no-op
uv run gz agent sync control-surfaces
git status src/gzkit/ .claude/ .github/ .gzkit/manifest.json
# expect: clean (manifest Updated: may bump if it carries a date)

# Byte-parity tests pass post-sync
uv run -m unittest tests.test_skills.TestSkillsLayoutDualSurface -v
uv run -m unittest tests.test_rules.TestRulesLayoutDualSurface -v   # OBPI-03 landing

# File counts match canonical
find .gzkit/skills/ -name SKILL.md | wc -l
find src/gzkit/skills/ -name SKILL.md | wc -l
find .claude/skills/ -name SKILL.md | wc -l
find .github/skills/ -name SKILL.md | wc -l
ls .gzkit/rules/*.md | wc -l
ls src/gzkit/rules/*.md | wc -l
ls .claude/rules/*.md | wc -l
ls .github/instructions/*.md | wc -l

uv run gz validate --surfaces
uv run gz validate --distribution

uv run -m behave features/agent_sync.feature --tags=@REQ-0.0.32-08-01
```

## Acceptance Criteria

- [ ] REQ-0.0.32-08-01: `gz agent sync control-surfaces` resolves canonical content from `.gzkit/<surface>/` for every dual-surface family; NEVER from `src/gzkit/` or `.[vendor]/`
- [ ] REQ-0.0.32-08-02: A single sync invocation propagates `.gzkit/<surface>/` to BOTH `src/gzkit/<surface>/` (wheel-shipping byte-parity copy) AND `.[vendor]/<surface>/` (vendor mirrors)
- [ ] REQ-0.0.32-08-03: Post-sync, `src/gzkit/<surface>/` is byte-equivalent to `.gzkit/<surface>/` for every slug (skills and rules); byte-parity tests from OBPI-01/03 pass
- [ ] REQ-0.0.32-08-04: Post-sync, `.[vendor]/<surface>/` is byte-equivalent (modulo documented vendor transformations) to `.gzkit/<surface>/`
- [ ] REQ-0.0.32-08-05: Re-running sync on freshly-synced state produces zero file writes across BOTH derived surface families (idempotent)
- [ ] REQ-0.0.32-08-06: File counts match across canonical and derived surfaces — `.gzkit/skills/` = `src/gzkit/skills/` = `.claude/skills/` = `.github/skills/` (~70); `.gzkit/rules/` = `src/gzkit/rules/` = `.claude/rules/` = `.github/instructions/` (14)
- [ ] REQ-0.0.32-08-07: `.gzkit/manifest.json` refreshes Updated date + surface counts on each sync
- [ ] REQ-0.0.32-08-08: `gz validate --surfaces` exits 0 post-sync (no drift across either derived surface family)
- [ ] REQ-0.0.32-08-09: `gz validate --distribution` exits 0 post-sync (no on-disk-not-baseline drift)
- [ ] REQ-0.0.32-08-10: Behave scenario `@REQ-0.0.32-08-01` exercises dual-direction idempotency and passes
- [ ] REQ-0.0.32-08-11: `.claude/rules/skill-surface-sync.md` re-affirms "Edit `.gzkit/` first" and documents the broadened sync coverage
- [ ] REQ-0.0.32-08-12: `uv run gz check` exits 0

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage update + skill-surface-sync rule re-affirm; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Dual-direction idempotency scenario passes
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded — this OBPI is the LAST in the ADR-0.0.32 chain; closeout of the parent ADR follows

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output for canonical-resolution-from-.gzkit/ + dual-direction propagation + idempotent-sync tests
```

### Code Quality

```text
# Paste lint, format, ty output
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)

```text
# Paste behave scenario output for @REQ-0.0.32-08-01
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: editing `.gzkit/skills/<slug>/SKILL.md` required the operator to remember to `cp` the change to `src/gzkit/skills/<slug>/SKILL.md` or trip the byte-parity test from OBPI-01; the existing `gz agent sync control-surfaces` flow handled the vendor-mirror leg but had no `.gzkit/ → src/gzkit/` step (GHI #449). After this OBPI: a single `gz agent sync control-surfaces` invocation propagates `.gzkit/<surface>/` to both `src/gzkit/<surface>/` (wheel-shipping byte-parity copy) and `.[vendor]/<surface>/` (vendor mirrors); byte-parity tests pass; re-running on freshly-synced state is a clean no-op. The canonical-routing invariant declared in ADR-0.0.32 § Decision is mechanically enforced — `.gzkit/` is the single authoring surface; the rest is derivable from it.

### Key Proof


```bash
# Edit canonical skill, single sync writes to both derived surface families
echo "# demo" >> .gzkit/skills/gz-prd/SKILL.md
uv run gz agent sync control-surfaces
diff .gzkit/skills/gz-prd/SKILL.md src/gzkit/skills/gz-prd/SKILL.md  # no diff (wheel-shipping pkg copy)
diff .gzkit/skills/gz-prd/SKILL.md .claude/skills/gz-prd/SKILL.md    # no diff (vendor mirror)

# Idempotent re-run on freshly-synced state
uv run gz agent sync control-surfaces  # no new writes

# Cleanup
git checkout -- .gzkit/skills/gz-prd/SKILL.md src/gzkit/skills/ .claude/skills/
```

Receipts:
- arb-ruff-d21c40670f6e43d6b607939712d5b55e (lint clean)
- arb-step-typecheck-2cae7c1ea2d84acf9bc0290807fd0cc2 (typecheck clean)
- arb-step-unittest-99b651d00c3a449b934538bc9c11ecf2 (4931/4931 pass)
- arb-step-mkdocs-da1ac434ae2247d19a9dcea0e8dce663 (docs strict pass)

REQ parity: uncovered_reqs: 0 (all 12 REQs covered via unit tests + 3 behave scenarios + waiver for structural REQs).

### Implementation Summary


- Files created:
  - features/agent_sync.feature (3 BDD scenarios for dual-direction sync idempotency)
- Files modified:
  - src/gzkit/sync_surfaces.py: added sync_pkg_surfaces() + _pkg_surface_exists() + _sync_flat_md_to_pkg(); wired into sync_all() before vendor mirrors
  - .gzkit/rules/skill-surface-sync.md: bumped to v0.5.0 with broadened sync documentation
  - docs/user/manpages/agent-sync-control-surfaces.md: documented one-canonical-source / two-derived-families behavior
  - data/behave_coverage_waivers.json: added rationale + waiver entry for structural REQs
  - tests/test_sync_surfaces.py: added TestSyncPkgSurfaces (6) and TestSyncPkgSurfacesManifestAndDocs (5)
  - tests/test_skills.py, test_rules.py, test_personas.py, test_templates.py: added @covers; replaced obsolete forward-guard scope tests with positive assertions
- Tests added: 11 new unittests + 3 new behave scenarios; all 4931 unittests pass
- Date completed: 2026-05-13
- Attestation status: human-attested (g0)
- Defects noted: Brief Allowed Paths listed vendor-mirror path .claude/rules/skill-surface-sync.md (canonical edit target is .gzkit/rules/skill-surface-sync.md); orphaned manpage gz-agent.md merged into existing agent-sync-control-surfaces.md

## Tracked Defects

- GHI #318 — final OBPI in the closure chain; ADR-0.0.32 closeout follows this OBPI's attestation
- GHI #449 — `.gzkit/ → src/gzkit/` dev-time sync mechanism absorbed by this OBPI's broadened scope; close `superseded` against this OBPI when it attests

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.32-08-mirror-sync sync mechanism implemented and verified. ARB receipts: arb-ruff-d21c40670f6e43d6b607939712d5b55e (lint), arb-step-typecheck-2cae7c1ea2d84acf9bc0290807fd0cc2 (typecheck), arb-step-unittest-99b651d00c3a449b934538bc9c11ecf2 (4931/4931 pass), arb-step-mkdocs-da1ac434ae2247d19a9dcea0e8dce663 (docs strict). 12/12 REQs covered (uncovered_reqs: 0). 3 BDD scenarios pass under features/agent_sync.feature. sync_pkg_surfaces() propagates .gzkit/<surface>/ to src/gzkit/<surface>/ for skills/rules/personas/templates/chores-canonical, guarded by __init__.py existence (adopter projects untouched). skill-surface-sync.md bumped to v0.5.0.
- Date: 2026-05-13

---

**Brief Status:** Completed

**Date Completed:** 2026-05-13

**Evidence Hash:** -
