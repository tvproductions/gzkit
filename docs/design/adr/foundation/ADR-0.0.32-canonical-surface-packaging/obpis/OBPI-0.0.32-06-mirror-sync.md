---
id: OBPI-0.0.32-06-mirror-sync
parent: ADR-0.0.32-canonical-surface-packaging
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.32-06-mirror-sync: Mirror Sync Post-Promotion

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #6 — "Sync mirrors after surfaces promote: `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/` regenerated from new package surface; verify `gz agent sync control-surfaces` no-ops cleanly post-promotion"

**Status:** Draft

## Objective

After OBPI-0.0.32-01 (skills) and OBPI-0.0.32-02 (rules) move canonical content from `.gzkit/skills/<slug>/SKILL.md` and `.gzkit/rules/<slug>.md` into `src/gzkit/skills/<slug>/SKILL.md` and `src/gzkit/rules/<slug>.md`, the vendor mirror tree (`.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/`) becomes stale. This OBPI updates `gz agent sync control-surfaces` so it reads canonical content from the new package surfaces (via `importlib.resources` or the equivalent project-first → package-fallback resolution), regenerates every mirror cleanly, and asserts that re-running sync on freshly-synced state is a clean no-op (the operator-facing health signal that mirrors are in canonical agreement). After this OBPI lands, the mirror tree is a wheel-derivable artifact, not a separately-maintained source of truth.

## Lane

**Heavy** — changes the runtime contract of `gz agent sync control-surfaces` (the canonical resolution path), modifies generated vendor mirror outputs, and gates closeout of the entire ADR-0.0.32 chain on clean post-promotion mirror state. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/sync.py` (or `src/gzkit/sync_surfaces.py`, `src/gzkit/sync_skills.py`, `src/gzkit/skills_mirror.py`, `src/gzkit/rules.py` — wherever the sync logic lives) — update canonical-content resolution to project-first → package-fallback per the new layout
- `src/gzkit/cli/parser_*.py` (if `gz agent sync control-surfaces` flag dispatch needs an adjustment) — minimal-surface change
- `.claude/skills/<slug>/SKILL.md` (61 files) — regenerated outputs
- `.claude/rules/<slug>.md` (14 files) — regenerated outputs
- `.github/skills/<slug>/SKILL.md` (mirror) — regenerated outputs
- `.github/instructions/<slug>.md` — regenerated outputs
- `.gzkit/manifest.json` — refresh `Updated:` field and any per-surface metadata
- `tests/test_sync.py`, `tests/test_skills_mirror.py` — unit-tier tests for canonical-resolution change
- `features/agent_sync.feature` — behave scenario asserting post-promotion sync is a clean no-op (idempotency test)
- `docs/user/manpages/gz-agent.md` — document the canonical-resolution change if it surfaces operator-facing behavior

## Denied Paths

- `src/gzkit/skills/**`, `src/gzkit/rules/**` — canonical content moves belong to OBPI-0.0.32-01 / -02
- `pyproject.toml` — wheel includes belong to OBPI-0.0.32-04
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-0.0.32-05
- `data/distribution_baseline_manifest.json` — baseline manifest belongs to OBPI-0.0.32-04
- `docs/governance/trust-doctrine.md` — T0 doctrine prose belongs to OBPI-0.0.31-01
- Canonical content edits — mirrors are byte-derived from canonical; this OBPI does not author content

## Requirements (FAIL-CLOSED)

1. `gz agent sync control-surfaces` MUST resolve canonical skill content from `src/gzkit/skills/<slug>/SKILL.md` (the package surface) when no project-local override exists at `.gzkit/skills/<slug>/SKILL.md`; same project-first → package-fallback shape for rules.
2. After running `gz agent sync control-surfaces` once on a clean post-promotion working tree, every vendor mirror MUST be byte-equivalent to the corresponding canonical source (modulo any documented vendor-specific transformation).
3. Re-running `gz agent sync control-surfaces` on freshly-synced state MUST produce ZERO writes (idempotent; confirms the canonical-resolution path is stable).
4. The number of files in `.claude/skills/` MUST equal the number of files in `src/gzkit/skills/<slug>/SKILL.md` (61); same for `.claude/rules/` ↔ 14 rule files; same for `.github/skills/` ↔ 61 and `.github/instructions/` ↔ 14.
5. `.gzkit/manifest.json` MUST refresh on each sync run with the new `Updated:` date and surface counts.
6. Unit tests MUST cover: (a) canonical-resolution returns content from the package when no project override exists, (b) canonical-resolution returns the project override when one exists, (c) the sync function regenerates mirrors byte-equivalent to canonical, (d) running sync twice in a row produces no diffs.
7. A behave scenario MUST run sync against a clean post-promotion fixture and assert no-op idempotency on the second run, tagged `@REQ-0.0.32-06-NN`.
8. `uv run gz check` MUST exit 0 with the new resolution path.
9. `gz validate --surfaces` MUST pass post-sync; mirror drift detection (already covered by existing `--surfaces` audit) MUST report clean.
10. `gz validate --distribution` (from OBPI-0.0.32-05) MUST pass — this OBPI does not introduce on-disk-not-baseline drift.

> STOP-on-BLOCKERS:
> - If OBPI-0.0.32-01 or OBPI-0.0.32-02 has not landed (canonical content still at `.gzkit/`), STOP — there is nothing to re-resolve.
> - If `gz agent sync control-surfaces` currently has no project-first → package-fallback path (it always reads from `.gzkit/`), the sync function needs a deeper refactor than a path change; surface that as a sub-task and decompose if scope expansion is required.
> - If a vendor mirror has accumulated hand-edits between sync runs (e.g. someone edited `.claude/skills/<slug>/SKILL.md` directly without bumping `skill-version`), STOP and reconcile per `.claude/rules/skill-surface-sync.md` § Conflict resolution.
> - If `gz validate --surfaces` reports drift before this OBPI starts, STOP — fix the drift first; this OBPI's success criterion depends on a clean baseline.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — package-layout block + project-first resolution
- [ ] Parent ADR § Consequences (Negative) — names the temporary mirror-stale state during the OBPI chain
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.claude/rules/skill-surface-sync.md` — surface layout table, conflict resolution, version discipline
- [ ] `AGENTS.md` § Skills Protocol — discovery + sync expectations
- [ ] `.claude/rules/tool-skill-runbook-alignment.md` — Invariant 1, 2, 3 (mirror sync must not break tool↔skill alignment)

**Context — sibling OBPIs:**

- [ ] OBPI-0.0.32-01 + -02 — canonical content moves; this OBPI consumes the new surface layout
- [ ] OBPI-0.0.32-04 — baseline manifest is invariant under sync (mirror regeneration MUST NOT change the canonical surface fingerprints captured in the manifest)
- [ ] OBPI-0.0.32-05 — `gz validate --distribution` must continue to pass after this OBPI's sync runs

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-01 + OBPI-0.0.32-02 landed; canonical content at `src/gzkit/skills/` and `src/gzkit/rules/`
- [ ] `gz agent sync control-surfaces` currently runnable (sanity check before refactor)
- [ ] `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/` exist as directories
- [ ] `gz validate --surfaces` exits 0 on the pre-OBPI state (so any drift this OBPI surfaces is genuinely from the resolution-path change, not pre-existing)

**Existing Code:**

- [ ] Read `src/gzkit/sync.py`, `sync_surfaces.py`, `sync_skills.py`, `skills_mirror.py` end-to-end (the sync surface is fragmented — understand which file owns what before editing)
- [ ] Read `.gzkit/manifest.json` schema before refresh logic lands
- [ ] Read existing `gz validate --surfaces` check in trust_audits to understand what mirror-drift detection already covers

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #6 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for canonical-resolution + idempotent sync fail before implementation
- [ ] GREEN: tests pass after the resolution-path change and sync run
- [ ] Coverage above 40% floor

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-agent.md` updated if operator-facing behavior changed (likely minimal — resolution path is internal)
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] `features/agent_sync.feature` (or equivalent) extended with the post-promotion idempotency scenario tagged `@REQ-0.0.32-06-01`

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# First sync after promotion: regenerates mirrors
uv run gz agent sync control-surfaces
git status .claude/ .github/ .gzkit/manifest.json    # expect changes (mirrors regenerating to canonical)

# Second sync immediately after: idempotent no-op
uv run gz agent sync control-surfaces
git status .claude/ .github/ .gzkit/manifest.json    # expect clean (manifest Updated: may bump if it carries a date)

# Mirror counts match canonical
find src/gzkit/skills/ -name SKILL.md | wc -l                      # 61
find .claude/skills/ -name SKILL.md | wc -l                        # 61
find .github/skills/ -name SKILL.md | wc -l                        # 61
ls src/gzkit/rules/*.md | wc -l                                    # 14
ls .claude/rules/*.md | wc -l                                      # 14
ls .github/instructions/*.md | wc -l                               # 14

uv run gz validate --surfaces
uv run gz validate --distribution

uv run -m behave features/agent_sync.feature --tags=@REQ-0.0.32-06-01
```

## Acceptance Criteria

- [ ] REQ-0.0.32-06-01: `gz agent sync control-surfaces` resolves canonical skill content from `src/gzkit/skills/<slug>/SKILL.md` when no project-local override exists; same project-first → package-fallback shape for rules
- [ ] REQ-0.0.32-06-02: Post-sync mirror trees match canonical sources byte-equivalent (modulo documented vendor transformations)
- [ ] REQ-0.0.32-06-03: Re-running sync on freshly-synced state produces zero file writes (idempotent)
- [ ] REQ-0.0.32-06-04: Mirror counts match canonical: `.claude/skills/` = 61; `.claude/rules/` = 14; `.github/skills/` = 61; `.github/instructions/` = 14
- [ ] REQ-0.0.32-06-05: `.gzkit/manifest.json` refreshes Updated date + surface counts on each sync
- [ ] REQ-0.0.32-06-06: `gz validate --surfaces` exits 0 post-sync (no mirror drift)
- [ ] REQ-0.0.32-06-07: `gz validate --distribution` exits 0 post-sync (no on-disk-not-baseline drift)
- [ ] REQ-0.0.32-06-08: Behave scenario `@REQ-0.0.32-06-01` exercises post-promotion idempotency and passes
- [ ] REQ-0.0.32-06-09: `uv run gz check` exits 0

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage update (minimal); mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Idempotency scenario passes
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded — this OBPI is the LAST in the ADR-0.0.32 chain; closeout of the parent ADR follows

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output for canonical-resolution + idempotent-sync tests
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
# Paste behave scenario output for @REQ-0.0.32-06-01
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: vendor mirrors at `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/` would have gone stale immediately when OBPI-0.0.32-01 / -02 moved canonical content to the package surface, leaving the agent runtime reading inconsistent state. After this OBPI: `gz agent sync control-surfaces` resolves canonical content from the new package layout via project-first → package-fallback, regenerates every mirror byte-equivalent, and asserts idempotency on the second run as the operator-facing health signal that the mirror tree is a wheel-derivable artifact.

### Key Proof

```bash
uv run gz agent sync control-surfaces && uv run gz agent sync control-surfaces
git diff --stat .claude/ .github/   # Expected: empty (idempotent)
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — final OBPI in the closure chain; ADR-0.0.32 closeout follows this OBPI's attestation

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
