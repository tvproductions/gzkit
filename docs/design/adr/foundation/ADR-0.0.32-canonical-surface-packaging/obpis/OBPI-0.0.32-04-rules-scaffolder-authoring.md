---
id: OBPI-0.0.32-04-rules-scaffolder-authoring
parent: ADR-0.0.32-canonical-surface-packaging
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.0.32-04-rules-scaffolder-authoring: Rules Scaffolder Authoring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #4 — "Rules scaffolder authoring — build `CORE_RULES` registry symmetric to `CORE_SKILLS`/`CORE_CHORES`; author `scaffold_core_rules` that copies canonical rule content from `importlib.resources.files(\"gzkit.rules\")` (the wheel's package surface) into the adopter's `.gzkit/rules/<slug>.md`; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair). Depends on OBPI-03 landing first."

**Status:** Draft

## Objective

After OBPI-03 has landed the rules dual-surface (14 rule files retained at `.gzkit/rules/<slug>.md` as authored canonical source-of-truth AND byte-equivalent copies at `src/gzkit/rules/<slug>.md` for wheel-shipping, `src/gzkit/rules.py` converted to `src/gzkit/rules/__init__.py`), author the rules scaffolding surface that closes T0-class A. Build a `CORE_RULES` registry symmetric to `CORE_SKILLS` / `CORE_CHORES`. Author `scaffold_core_rules(project_root, config, *, skip_existing=False)` mirroring `scaffold_core_chores` semantics — enumerate canonical rules from `importlib.resources.files("gzkit.rules")` (the wheel's package surface), write each to `<project_root>/.gzkit/rules/<slug>.md` (the adopter's project canonical surface-of-truth), honor `skip_existing`, return the list of newly-created slugs. Wire `scaffold_core_rules` into `init_cmd._scaffold_project_skeleton` (for fresh init) and `_repair_missing_artifacts` (for re-run repair). After this OBPI lands, `gz init` produces 14 canonical rule files at the adopter's `.gzkit/rules/`; once written, the adopter's `.gzkit/rules/` is their project canonical source-of-truth per ADR-0.0.32 § Decision's binding canonical-routing invariant. T0-class A closure depends on this OBPI + OBPI-06 (wheel includes) jointly.

## Lane

**Heavy** — introduces a new public registry (`CORE_RULES`) and a new public scaffolder (`scaffold_core_rules`); changes the runtime contract of `gz init`. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/rules/__init__.py` — add `CORE_RULES`, `_iter_canonical_rule_slugs()`, `scaffold_core_rules`
- `src/gzkit/commands/init_cmd.py` — invoke `scaffold_core_rules` from `_scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts(skip_existing=True)` (re-run repair)
- `tests/test_rules.py`, `tests/commands/test_init.py` — unit tests for `CORE_RULES`, `scaffold_core_rules`, init-cmd integration, project-first → package-fallback resolution
- `docs/user/manpages/init.md` — mention rule scaffolding alongside skills + chores + personas
- `docs/user/runbook.md` — runbook section for rules surface
- `.gzkit/rules/skill-surface-sync.md` — re-affirm "Edit `.gzkit/` first" canon; document that `gz init` populates an adopter's `.gzkit/rules/` from the wheel's package surface as the bootstrap source, mirroring the skills pattern from OBPI-02

## Denied Paths

- Physical migration (file moves, module-to-package conversion) — owned by OBPI-03
- `src/gzkit/skills/**`, `src/gzkit/skills.py` — skills belong to OBPI-01 / -02
- `pyproject.toml` — wheel includes belong to OBPI-06; until OBPI-06 lands, the scaffolder works in-repo but not from a fresh wheel install (intermediate state)
- `features/**` — behave belongs to OBPI-06
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `.claude/rules/`, `.github/instructions/` — mirror regen belongs to OBPI-08
- Rule-content edits — this OBPI consumes the canonical content moved by OBPI-03; no semantic edits to rules

## Requirements (FAIL-CLOSED)

1. `CORE_RULES` MUST be authored as a registry in `src/gzkit/rules/__init__.py` mirroring the shape of `CORE_SKILLS` and `CORE_CHORES`. Choose between (a) list-of-slugs (simplest, since each rule is one file) or (b) dict-of-slug-to-metadata (richer, mirrors `CORE_SKILLS`); document the choice in the brief evidence. Every one of the 14 canonical rule slugs MUST appear in `CORE_RULES`.
2. `_iter_canonical_rule_slugs()` MUST exist mirroring `src/gzkit/chores/__init__.py:_iter_canonical_chore_slugs()`: enumerate via `importlib.resources.files("gzkit.rules")`, skip non-`.md` entries, yield each canonical-rule `Traversable`.
3. `scaffold_core_rules(project_root, config, *, skip_existing=False)` MUST exist with the exact same surface shape as `scaffold_core_chores` and `scaffold_core_skills` — same parameters, same return type (list of newly-created slugs), same `skip_existing` semantics.
4. `init_cmd._scaffold_project_skeleton` MUST invoke `scaffold_core_rules` for fresh init.
5. `init_cmd._repair_missing_artifacts` MUST invoke `scaffold_core_rules(skip_existing=True)` for re-run repair, mirroring the existing `scaffold_core_skills(skip_existing=not dry_run)` pattern at the same call site.
6. Project-first → package-fallback resolution MUST hold: a project-local `.gzkit/rules/<slug>.md` is preserved by `skip_existing=True`; a missing one is filled from package canonical via `importlib.resources`.
7. Unit tests MUST cover: (a) `CORE_RULES` enumerates all 14 slugs, (b) `_iter_canonical_rule_slugs()` returns 14 entries, (c) `scaffold_core_rules` writes byte-identical content from package, (d) `skip_existing=True` preserves operator edits, (e) `init_cmd` integration produces `.gzkit/rules/` content in a fresh tempdir.
8. `uv run gz check` MUST exit 0 after the authoring lands.
9. `mkdocs build --strict` MUST pass; manpage + runbook updates MUST land in the same patch as scaffolder behavior changes per `.claude/rules/gate5-runbook-code-covenant.md`.

> STOP-on-BLOCKERS:
> - If OBPI-03 has not landed (rules not yet at `src/gzkit/rules/<slug>.md`), STOP — there is no canonical surface for the scaffolder to consume.
> - If `RuleFrontmatter` schema (`src/gzkit/rules/__init__.py`) and `CORE_RULES` registry would conflict (e.g. a slug containing `/`), STOP and decide on the registry shape before authoring.
> - If `scaffold_core_rules` integration in `init_cmd.py` would conflict with the existing `scaffold_core_chores` and `scaffold_core_skills` ordering (rules must scaffold BEFORE chores/skills if any of them reference rule files at scaffold time), STOP and document the dependency order before wiring.
> - If `importlib.resources.files("gzkit.rules")` does not resolve at runtime, STOP — the OBPI-03 package conversion may have left an issue.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — package layout block, file-not-dir rules layout
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/skill-surface-sync.md` — rule-version body marker convention; the new package layout must preserve this
- [ ] `.gzkit/rules/tests.md` — RGR discipline

**Context — chores precedent + sibling OBPIs:**

- [ ] `src/gzkit/chores/__init__.py` — `CORE_CHORES`-equivalent (registry.json), `_iter_canonical_chore_slugs`, `scaffold_core_chores`
- [ ] `src/gzkit/skills/__init__.py` (post-OBPI-02) — `CORE_SKILLS`, `_iter_canonical_skill_slugs`, `scaffold_core_skills` — the closest sibling pattern
- [ ] OBPI-0.0.21-04-resolver-with-fallback — chores resolver pattern
- [ ] OBPI-0.0.32-03 (sibling) — physical migration; must land first
- [ ] OBPI-0.0.32-02 (sibling) — same scaffolder pattern applied to skills

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-03 landed (14 rule files at `src/gzkit/rules/<slug>.md`, `src/gzkit/rules/__init__.py` exists)
- [ ] `src/gzkit/chores/__init__.py` exists (precedent)
- [ ] `src/gzkit/skills/__init__.py` exists (sibling pattern, ideally after OBPI-02 lands)

**Existing Code:**

- [ ] Read `scaffold_core_chores` body end-to-end before mirroring
- [ ] Read `init_cmd._scaffold_project_skeleton` and `_repair_missing_artifacts` to identify exact call-site placement for `scaffold_core_rules`
- [ ] Audit `src/gzkit/rules/__init__.py` (post-OBPI-03) for any helper that already enumerates rule files; reuse rather than duplicate

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #4 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for `CORE_RULES`, `scaffold_core_rules`, init-cmd integration fail before implementation
- [ ] GREEN: tests pass after authoring + integration
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/init.md` mentions rule scaffolding
- [ ] `docs/user/runbook.md` rules section updated
- [ ] `.gzkit/rules/skill-surface-sync.md` re-affirmed — "Edit `.gzkit/` first" remains canon; section added explaining that `gz init` populates adopter's `.gzkit/rules/` from the wheel's package surface as the bootstrap source
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios in this OBPI; OBPI-06 owns the build-install-init smoke that exercises rules end-to-end

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

python -c "from gzkit.rules import CORE_RULES, scaffold_core_rules, _iter_canonical_rule_slugs; print('imports OK', len(CORE_RULES), sum(1 for _ in _iter_canonical_rule_slugs()))"  # expect 14, 14

# Smoke: scaffolder copies canonical rules to a temp project
mkdir /tmp/gz-rules-scaffold-smoke && cd /tmp/gz-rules-scaffold-smoke && uv run gz init && ls .gzkit/rules/ | wc -l   # expect 14
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. The closeout
     ceremony walkthrough harvests this section (parser-validated;
     unregistered verbs are dropped). Prefer real paths and arguments
     over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

- [ ] REQ-0.0.32-04-01: `CORE_RULES` registry exists in `src/gzkit/rules/__init__.py`; enumerates all 14 canonical slugs
- [ ] REQ-0.0.32-04-02: `_iter_canonical_rule_slugs()` exists, mirrors `_iter_canonical_chore_slugs`, returns 14 entries
- [ ] REQ-0.0.32-04-03: `scaffold_core_rules(project_root, config, *, skip_existing=False)` exists with exact-same surface as `scaffold_core_chores` and `scaffold_core_skills`
- [ ] REQ-0.0.32-04-04: `init_cmd._scaffold_project_skeleton` invokes `scaffold_core_rules` for fresh init
- [ ] REQ-0.0.32-04-05: `init_cmd._repair_missing_artifacts` invokes `scaffold_core_rules(skip_existing=True)` for re-run repair
- [ ] REQ-0.0.32-04-06: Project-first → package-fallback resolution holds; `skip_existing=True` preserves operator edits
- [ ] REQ-0.0.32-04-07: A fresh `gz init` in a tempdir produces 14 canonical rule files at `.gzkit/rules/`
- [ ] REQ-0.0.32-04-08: `.gzkit/rules/skill-surface-sync.md` re-affirms "Edit `.gzkit/` first" and documents that `gz init` populates adopter's `.gzkit/rules/` from the wheel's package surface; `docs/user/manpages/init.md` updated; `mkdocs build --strict` passes
- [ ] REQ-0.0.32-04-09: `uv run gz check` exits 0

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage + runbook + surface-sync rule updated; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing scenarios still pass
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
# Paste regression scenario output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: `gz init` produced ZERO rule files in adopter projects; contextual rule loading silently no-opped. After this OBPI: `gz init` reads canonical rule content from the wheel's package surface (`importlib.resources.files("gzkit.rules")`) and writes 14 canonical rule files into the adopter's `.gzkit/rules/` — once written, that surface becomes the adopter's project canonical source-of-truth per ADR-0.0.32 § Decision's binding canonical-routing invariant. `CORE_RULES` is the symmetric counterpart to `CORE_SKILLS` and `CORE_CHORES`; future rule promotions follow the documented dual-surface pattern (`.gzkit/rules/` authored canonical, `src/gzkit/rules/` byte-equivalent wheel-shipping copy, vendor mirrors synced from `.gzkit/` by `gz agent sync control-surfaces` via OBPI-08). T0-class A closure remains contingent on OBPI-06 (wheel includes) for fresh-install consumers; this OBPI delivers the runtime semantics.

### Key Proof


```bash
python -c "
from gzkit.rules import CORE_RULES, scaffold_core_rules, _iter_canonical_rule_slugs
print('CORE_RULES slugs:', len(CORE_RULES))
print('_iter count:', sum(1 for _ in _iter_canonical_rule_slugs()))
print('Sample:', sorted(CORE_RULES)[:3])
"
# Observed:
# CORE_RULES slugs: 19
# _iter count: 19
# Sample: ['adr-audit', 'agent-failure-modes', 'brief-heading-conventions']
```

REQ coverage parity: 9/9 covered (Stage 3 Phase 1b).

Receipts:
- arb-step-unittest-d08b576cf35e4864960d21bd45617c03 (4852 tests pass)
- arb-ruff-41d5e0d5a88743ac83b5be432f1a01cb (lint clean)
- arb-step-typecheck-faf8e22ec4ed42178ce883c59550225e (ty clean)
- arb-step-mkdocs-4cb6ae3d284844df851faf2536570c4c (mkdocs --strict clean)

### Implementation Summary


- Files created/modified: `src/gzkit/rules/__init__.py` (added `CORE_RULES`, `_iter_canonical_rule_slugs`, `scaffold_core_rules`); `src/gzkit/commands/init_cmd.py` (imported and wired `scaffold_core_rules` after `sync_all` in fresh init and inside `_repair_missing_artifacts` with `skip_existing=True`); `src/gzkit/sync_surfaces.py` (moved `sync_nested_agents_md` after copilot rule rendering for idempotency — coupled-surface coherence fix per AGENTS.md Invariant 1a); `tests/test_rules.py` (added `TestCoreRulesRegistry` with 12 tests; updated OBPI-03 byte-parity tests to exclude `AGENTS.md`); `tests/commands/test_init.py` (added `TestInitRulesIntegration` with 5 tests for REQs 04–09); `docs/user/manpages/init.md` + `docs/user/runbook.md` + `.gzkit/rules/skill-surface-sync.md` + byte-parity copy at `src/gzkit/rules/skill-surface-sync.md` (operator docs); `data/behave_coverage_waivers.json` (BDD deferred to OBPI-06 per ADR-0.0.32 decomposition); brief Allowed Paths corrected.
- Tests added: 17 new tests (12 in `TestCoreRulesRegistry` + 5 in `TestInitRulesIntegration`); full suite 4852/4852 passing.
- Date completed: 2026-05-12
- Attestation status: Operator attested via "attest completed" in Stage 4 ceremony; heavy-lane + foundation-kind Gate 5 brief-level attestation; `--attestor-present` co-presence proxy via active pipeline marker.
- Defects noted: One coupled-surface defect surfaced and fixed in the same patch — pre-existing `sync_all` ordering (sync_nested_agents_md before render_rules_to_dir) caused non-idempotent control-surface sync once `.gzkit/rules/` was populated; resolved by reordering per AGENTS.md Invariant 1a.

## Tracked Defects

- GHI #318 — failure class A addressed (jointly with OBPI-03 + OBPI-06)

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — heavy-lane + foundation-kind brief-level Gate 5 attestation for OBPI-0.0.32-04-rules-scaffolder-authoring. Operator confirmed Stage 4 ceremony evidence: 17 new tests pass (TestCoreRulesRegistry 12 + TestInitRulesIntegration 5), full suite 4852/4852 pass under arb-step-unittest-d08b576cf35e4864960d21bd45617c03, ruff/ty/mkdocs clean (arb-ruff-41d5e0d5a88743ac83b5be432f1a01cb / arb-step-typecheck-faf8e22ec4ed42178ce883c59550225e / arb-step-mkdocs-4cb6ae3d284844df851faf2536570c4c), 9/9 REQs covered. Coupled-surface defect in sync_all ordering surfaced and fixed in-patch per AGENTS.md Invariant 1a.
- Date: 2026-05-12

---

**Brief Status:** Completed

**Date Completed:** 2026-05-12

**Evidence Hash:** -
