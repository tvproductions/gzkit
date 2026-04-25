---
id: OBPI-0.0.32-05-init-update-flag
parent: ADR-0.0.32-canonical-surface-packaging
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.32-05-init-update-flag: gz init --update Flag

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #3 — "Add `gz init --update` flag with version-aware refresh + manpage + behave coverage"

**Status:** Draft

## Objective

Add a third `gz init` mode — `--update` — that performs version-aware refresh of canonical surfaces (rules, skills, hooks, templates, personas) shipped by the wheel, preserving project-local edits via marker-comment detection or content-hash comparison. The current `gz init` is binary: default re-run repairs only missing artifacts (skip-existing); `--force` wipes and recreates. The middle case — *the package canonical content has evolved between gzkit versions; refresh stale project copies in place without losing operator edits* — has no path today. This OBPI closes failure class D from GHI #318.

## Lane

**Heavy** — adds a CLI flag, changes the `gz init` runtime contract, requires manpage + behave coverage. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/commands/init_cmd.py` — add `--update` mode and refresh dispatch logic
- `src/gzkit/cli/parser_init.py` (or wherever the init subparser lives) — register the `--update` flag
- `src/gzkit/skills/__init__.py`, `src/gzkit/rules/__init__.py`, `src/gzkit/chores/__init__.py` — add `refresh_*` companion functions to existing scaffolders if required (small additive surface)
- `docs/user/manpages/gz-init.md` — document `--update` semantics, marker-comment / hash-comparison contract, conflict resolution
- `docs/user/runbook.md` — runbook section for the upgrade workflow
- `features/init.feature` — behave scenarios covering `--update` happy path, project-local-edit preservation, conflict surfacing
- `tests/commands/test_init.py` — unit tests for `--update` dispatch and refresh logic (mocked subprocess boundary; behavior-tier coverage in features)

## Denied Paths

- `src/gzkit/skills/<slug>/SKILL.md`, `src/gzkit/rules/<slug>.md` — canonical content moves belong to OBPI-0.0.32-01 / -02
- `pyproject.toml` — wheel includes belong to OBPI-0.0.32-04
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-0.0.32-05
- `.claude/skills/`, `.github/skills/`, `.github/instructions/` — mirror sync belongs to OBPI-0.0.32-06
- Any rule, skill, hook, template, persona content edits in this OBPI — refresh logic is content-agnostic

## Requirements (FAIL-CLOSED)

1. `gz init --update` MUST be a third mode distinct from default (repair-missing) and `--force` (wipe-and-recreate). Mutually exclusive with `--force`; passing both is a usage error (exit 1).
2. `--update` MUST iterate every canonical-surface scaffolder (`scaffold_core_skills`, `scaffold_core_rules`, `scaffold_core_chores`, plus future hooks/templates/personas if their canonical mechanism exists) in refresh mode.
3. Refresh mode MUST detect three states per canonical artifact: (a) IDENTICAL — project copy bytes match canonical; no action; (b) STALE — project copy differs but contains no operator-edit marker (e.g. unedited since last init); refresh in place; (c) EDITED — project copy differs and contains an operator-edit marker OR has a content hash that doesn't match a known prior canonical version; surface the conflict, do NOT overwrite.
4. The "operator-edit marker" mechanism MUST be one of: (a) a `<!-- gzkit-canonical-version: X.Y.Z -->` body marker that the scaffolder writes when it copies content (refresh updates the marker; manual edits remove or invalidate it); (b) content-hash comparison against a frozen-version manifest shipped with the wheel; (c) three-way merge against the prior package version. Choose one and document the choice in the manpage.
5. `--update --dry-run` MUST exist and MUST print the per-artifact action (IDENTICAL/STALE/EDITED) without writing.
6. Conflicts (EDITED state) MUST be reported as a structured summary at the end of the run, not silently skipped or overwritten. Exit code 3 if any conflict is unresolved at end-of-run.
7. Manpage `docs/user/manpages/gz-init.md` MUST document: the three modes, the operator-edit detection contract, the dry-run surface, the exit-code contract.
8. At least three behave scenarios in `features/init.feature`: (i) happy path — stale canonical refreshes cleanly; (ii) project-edit preservation — EDITED artifacts are NOT overwritten; (iii) conflict reporting — exit 3 + summary on unresolved conflicts.
9. Unit tests MUST cover the three-state detection function in isolation (mocked file system) and the dispatch logic (`--update` invokes refresh, not scaffold-missing).
10. `uv run gz check` MUST exit 0; `mkdocs build --strict` MUST exit 0.

> STOP-on-BLOCKERS:
> - If OBPI-0.0.32-01 or OBPI-0.0.32-02 has not landed (no canonical package surfaces exist for skills/rules), STOP — `--update` has nothing to refresh from.
> - If the operator-edit marker mechanism conflicts with an existing convention in `.gzkit/rules/skill-surface-sync.md` (which already specifies frontmatter `skill-version` for skills and body-level `<!-- rule-version: ... -->` for rules), STOP and reconcile — the canonical-version marker should compose with, not replace, the existing version markers.
> - If a refresh would touch a file that the planned chores-doctor surface (per `.claude/rules/chores.md`) intends to manage, STOP and decide whether to compose with the chores-doctor pattern or have `--update` own all canonical surfaces.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Intent — names failure class D (re-run upgrade path only adds missing)
- [ ] Parent ADR § Decision — `gz init --update` paragraph
- [ ] Parent ADR § Consequences — version-aware upgrade rationale
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/skill-surface-sync.md` — version-bump invariant for skills (`skill-version` frontmatter) and rules (body marker); operator-edit detection must compose with this
- [ ] `.claude/rules/cli.md` — flag conventions, exit code contract, `--dry-run` semantics
- [ ] `.gzkit/rules/tests.md` — RGR + behave-tier scenario tagging

**Context — chores precedent:**

- [ ] `src/gzkit/commands/chores_exec.py` — the existing project-local repair pattern (chores doctor surface, planned; pattern reference even if verb unregistered); `--update` may compose with this for chores
- [ ] `src/gzkit/commands/init_cmd.py` `_repair_missing_artifacts` — current `skip_existing=True` semantics; `--update` is the inverse contract
- [ ] OBPI-0.0.32-01 / -02 (siblings) — the canonical package surfaces this OBPI consumes

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/init_cmd.py` exists and contains `_scaffold_project_skeleton` and `_repair_missing_artifacts`
- [ ] `gz init --force` exists and is the wipe-and-recreate path (sanity check)
- [ ] OBPI-0.0.32-01 + OBPI-0.0.32-02 are at minimum Draft status (downstream OBPIs landing first is OK; status check just verifies the scope is decomposed)
- [ ] `features/init.feature` exists or is created

**Existing Code:**

- [ ] Read `src/gzkit/commands/init_cmd.py` end-to-end before adding `--update` dispatch
- [ ] Read `src/gzkit/chores/__init__.py` `doctor`-related functions for marker pattern precedent
- [ ] Read `.claude/rules/skill-surface-sync.md` § "Conflict resolution" — the version-mismatch resolution rules apply directly to `--update`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #3 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for three-state detection + `--update` dispatch fail before implementation
- [ ] GREEN: tests pass after `--update` lands
- [ ] Coverage above 40% floor

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-init.md` documents three modes, marker contract, exit codes
- [ ] `docs/user/runbook.md` upgrade workflow section added
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] Three scenarios in `features/init.feature` tagged with `@REQ-0.0.32-05-NN` per `.gzkit/rules/tests.md` § "Behave scenario tagging"
- [ ] `uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-01` (and -02, -03) all pass

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

uv run gz init --help | grep -- --update
uv run gz init --update --dry-run /tmp/gz-update-smoke

uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-01
uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-02
uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-03
```

## Acceptance Criteria

- [ ] REQ-0.0.32-05-01: `gz init --update` exists as a documented flag and is mutually exclusive with `--force`
- [ ] REQ-0.0.32-05-02: Three-state detection (IDENTICAL/STALE/EDITED) is implemented as a pure function with unit-test coverage
- [ ] REQ-0.0.32-05-03: STALE artifacts are refreshed in place; EDITED artifacts are NOT overwritten and surface as conflicts
- [ ] REQ-0.0.32-05-04: `--update --dry-run` prints per-artifact action without writing
- [ ] REQ-0.0.32-05-05: Unresolved conflicts at end-of-run produce exit code 3 with a structured summary
- [ ] REQ-0.0.32-05-06: Operator-edit marker mechanism (frontmatter / body marker / content hash) is documented in the manpage and composes with existing `skill-version` / `rule-version` markers per `.claude/rules/skill-surface-sync.md`
- [ ] REQ-0.0.32-05-07: Three behave scenarios exist and pass (`@REQ-0.0.32-05-01/-02/-03`)
- [ ] REQ-0.0.32-05-08: Manpage `docs/user/manpages/gz-init.md` documents the three modes, marker contract, and exit codes; `mkdocs build --strict` passes

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage + runbook updated; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Three scenarios passing
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output, coverage delta
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
# Paste behave scenario output for the three @REQ tags
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: cross-version upgrades silently leave stale artifacts in place. The only refresh path was `--force` (full wipe, destroys operator edits). After this OBPI: `--update` refreshes stale canonical content while preserving operator edits, and surfaces conflicts as structured exit-3 reports rather than silent overwrites or silent skips. Closes failure class D from GHI #318.

### Key Proof

```bash
uv run gz init --update --dry-run /tmp/gz-update-smoke
# Expected: per-artifact IDENTICAL/STALE/EDITED report; exit 0 if no conflicts; exit 3 if conflicts
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — failure class D addressed by this OBPI

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
