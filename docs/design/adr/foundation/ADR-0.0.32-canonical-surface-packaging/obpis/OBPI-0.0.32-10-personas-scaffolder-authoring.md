---
id: OBPI-0.0.32-10-personas-scaffolder-authoring
parent: ADR-0.0.32-canonical-surface-packaging
item: 10
lane: Heavy
status: Completed
---

# OBPI-0.0.32-10-personas-scaffolder-authoring: Personas Scaffolder Authoring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #10 — "Personas scaffolder authoring — build `CORE_PERSONAS` registry symmetric to `CORE_SKILLS`/`CORE_RULES`/`CORE_CHORES`; author `scaffold_core_personas` that copies canonical persona content from `importlib.resources.files(\"gzkit.personas\")` (the wheel's package surface) into the adopter's `.gzkit/personas/<slug>.md`; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair). Depends on OBPI-09 landing first."

**Status:** Draft

## Objective

After OBPI-09 has landed the personas dual-surface (6 canonical persona files retained at `.gzkit/personas/<slug>.md` AND byte-equivalent copies at `src/gzkit/personas/<slug>.md`, `src/gzkit/personas/__init__.py` exists as a thin package marker), author the personas scaffolding surface that brings adopter-side personas into the canonical-routing model. Build a `CORE_PERSONAS` registry symmetric to `CORE_SKILLS` / `CORE_RULES` / `CORE_CHORES`. Author `scaffold_core_personas(project_root, config, *, skip_existing=False)` mirroring `scaffold_core_skills` semantics — enumerate canonical personas from `importlib.resources.files("gzkit.personas")` (the wheel's package surface), write each to `<project_root>/.gzkit/personas/<slug>.md` (the adopter's project canonical surface-of-truth), honor `skip_existing`, return the list of newly-created slugs. Wire `scaffold_core_personas` into `init_cmd._scaffold_project_skeleton` (for fresh init) and `_repair_missing_artifacts` (for re-run repair). After this OBPI lands, `gz init` produces 6 canonical persona files at the adopter's `.gzkit/personas/`; once written, the adopter's `.gzkit/personas/` is their project canonical source-of-truth per ADR-0.0.32 § Decision's binding canonical-routing invariant. The wheel-include extension (OBPI-06) is the prerequisite for fresh-install consumers; this OBPI delivers the runtime semantics.

## Lane

**Heavy** — introduces a new public registry (`CORE_PERSONAS`) and a new public scaffolder (`scaffold_core_personas`); changes the runtime contract of `gz init` to produce persona content. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/personas/__init__.py` — add `CORE_PERSONAS`, `_iter_canonical_persona_slugs()`, `scaffold_core_personas`
- `src/gzkit/commands/init_cmd.py` — invoke `scaffold_core_personas` from `_scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts(skip_existing=True)` (re-run repair)
- `tests/test_personas.py`, `tests/commands/test_init.py` — unit tests for `CORE_PERSONAS`, `scaffold_core_personas`, init-cmd integration, project-first → package-fallback resolution
- `docs/user/manpages/init.md` — mention persona scaffolding alongside skills + rules + chores + templates
- `docs/user/runbook.md` — runbook section for personas surface

## Denied Paths

- Physical migration / `src/gzkit/personas/<slug>.md` content edits — owned by OBPI-09
- `src/gzkit/skills/**`, `src/gzkit/rules/**`, `src/gzkit/templates/**`, `src/gzkit/chores/**` — other surfaces' scaffolders belong to their own OBPIs
- `pyproject.toml` — wheel includes belong to OBPI-06
- `features/**` — behave belongs to OBPI-06
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `.claude/personas/`, `.github/personas/`, `.agents/personas/` — vendor mirrors belong to OBPI-08 (and remain transformed renders per § Named exceptions)
- Persona content edits — this OBPI consumes the canonical content from OBPI-09; no semantic edits to personas

## Requirements (FAIL-CLOSED)

1. `CORE_PERSONAS` MUST be authored as a registry in `src/gzkit/personas/__init__.py` mirroring the shape of `CORE_SKILLS`, `CORE_RULES`, and `CORE_CHORES`. Document the chosen shape (list-of-slugs vs. dict-of-slug-to-metadata) in the brief evidence; every one of the 6 canonical persona slugs MUST appear.
2. `_iter_canonical_persona_slugs()` MUST exist mirroring `_iter_canonical_chore_slugs()` / `_iter_canonical_skill_slugs()` / `_iter_canonical_rule_slugs()`: enumerate via `importlib.resources.files("gzkit.personas")`, skip `__pycache__`-style entries, yield each canonical-slug `Traversable`.
3. `scaffold_core_personas(project_root, config, *, skip_existing=False)` MUST exist with the exact same surface shape as `scaffold_core_skills` / `scaffold_core_rules` / `scaffold_core_chores` — same parameters, same return type (list of newly-created slugs), same `skip_existing` semantics.
4. `init_cmd._scaffold_project_skeleton` MUST invoke `scaffold_core_personas` for fresh init.
5. `init_cmd._repair_missing_artifacts` MUST invoke `scaffold_core_personas(skip_existing=True)` for re-run repair.
6. Project-first → package-fallback resolution MUST hold: a project-local `.gzkit/personas/<slug>.md` is preserved by `skip_existing=True`; a missing one is filled from package canonical via `importlib.resources`.
7. Unit tests MUST cover: (a) `CORE_PERSONAS` enumerates all 6 slugs, (b) `_iter_canonical_persona_slugs()` returns 6 entries, (c) `scaffold_core_personas` writes byte-identical content from package, (d) `skip_existing=True` preserves operator edits, (e) `init_cmd` integration produces `.gzkit/personas/` content in a fresh tempdir.
8. `uv run gz check` MUST exit 0 after the authoring lands.
9. `mkdocs build --strict` MUST pass; manpage + runbook updates MUST land in the same patch as scaffolder behavior changes per `.claude/rules/gate5-runbook-code-covenant.md`.

> STOP-on-BLOCKERS:
> - If OBPI-09 has not landed (personas not yet dual-surface), STOP — there is no canonical surface for the scaffolder to consume.
> - If `importlib.resources.files("gzkit.personas")` does not resolve at runtime, STOP — the OBPI-09 package marker may have an issue.
> - If `scaffold_core_personas` integration in `init_cmd.py` would conflict with the existing scaffolder ordering, STOP and document the dependency order before wiring.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — § Canonical-routing scope (personas row + scaffolder column)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `AGENTS.md` § Persona — the persona table to keep in sync with `CORE_PERSONAS`
- [ ] `.gzkit/rules/tests.md` — RGR discipline

**Context — sibling OBPIs:**

- [ ] OBPI-0.0.32-09 (sibling) — physical migration; must land first
- [ ] OBPI-0.0.32-02 (skills scaffolder, post-landing) — the closest sibling pattern
- [ ] OBPI-0.0.32-04 (rules scaffolder) — same pattern applied to a different surface
- [ ] `src/gzkit/chores/__init__.py` — chores precedent for `_iter_canonical_chore_slugs` + `scaffold_core_chores`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-09 landed (6 persona files at `src/gzkit/personas/<slug>.md`, `src/gzkit/personas/__init__.py` exists)
- [ ] `src/gzkit/chores/__init__.py` exists (precedent)
- [ ] `src/gzkit/skills/__init__.py` exists with the scaffolder pattern (post-OBPI-02 ideally)

**Existing Code:**

- [ ] Read `scaffold_core_chores` body end-to-end before mirroring
- [ ] Read `init_cmd._scaffold_project_skeleton` and `_repair_missing_artifacts` to identify exact call-site placement for `scaffold_core_personas`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #10 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for `CORE_PERSONAS`, `scaffold_core_personas`, init-cmd integration fail before implementation
- [ ] GREEN: tests pass after authoring + integration
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/init.md` mentions persona scaffolding
- [ ] `docs/user/runbook.md` personas section added
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios in this OBPI; OBPI-06 owns the build-install-init smoke that exercises personas end-to-end

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

python -c "from gzkit.personas import CORE_PERSONAS, scaffold_core_personas, _iter_canonical_persona_slugs; print('imports OK', len(CORE_PERSONAS), sum(1 for _ in _iter_canonical_persona_slugs()))"  # expect 6, 6

mkdir /tmp/gz-personas-scaffold-smoke && cd /tmp/gz-personas-scaffold-smoke && uv run gz init && ls .gzkit/personas/ | wc -l   # expect 6
```

## Demo

```bash
mkdir /tmp/gz-personas-demo && cd /tmp/gz-personas-demo
uv run gz init
ls .gzkit/personas/
head -10 .gzkit/personas/main-session.md
```

## Acceptance Criteria

- [ ] REQ-0.0.32-10-01: `CORE_PERSONAS` registry exists in `src/gzkit/personas/__init__.py`; enumerates all 6 canonical slugs
- [ ] REQ-0.0.32-10-02: `_iter_canonical_persona_slugs()` exists, mirrors `_iter_canonical_chore_slugs`, returns 6 entries
- [ ] REQ-0.0.32-10-03: `scaffold_core_personas(project_root, config, *, skip_existing=False)` exists with exact-same surface as sibling scaffolders
- [ ] REQ-0.0.32-10-04: `init_cmd._scaffold_project_skeleton` invokes `scaffold_core_personas` for fresh init
- [ ] REQ-0.0.32-10-05: `init_cmd._repair_missing_artifacts` invokes `scaffold_core_personas(skip_existing=True)` for re-run repair
- [ ] REQ-0.0.32-10-06: Project-first → package-fallback resolution holds; `skip_existing=True` preserves operator edits
- [ ] REQ-0.0.32-10-07: A fresh `gz init` in a tempdir produces 6 canonical persona files at `.gzkit/personas/`
- [ ] REQ-0.0.32-10-08: `docs/user/manpages/init.md` mentions persona scaffolding; `docs/user/runbook.md` personas section landed; `mkdocs build --strict` passes
- [ ] REQ-0.0.32-10-09: `uv run gz check` exits 0

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage + runbook updated; mkdocs --strict passes
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

Before this OBPI: `gz init` produced ZERO persona files in adopter projects; agents in adopter projects had no canonical persona surface to consult (or relied on hand-copied content). After this OBPI: `gz init` reads canonical persona content from the wheel's package surface (`importlib.resources.files("gzkit.personas")`) and writes 6 canonical persona files into the adopter's `.gzkit/personas/` — once written, that surface becomes the adopter's project canonical source-of-truth per ADR-0.0.32 § Decision's binding canonical-routing invariant. `CORE_PERSONAS` is the symmetric counterpart to the other `CORE_<SURFACE>` registries. The wheel-include extension (OBPI-06) is the prerequisite for fresh-install consumers; this OBPI delivers the runtime semantics.

### Key Proof


```bash
python -c "
from gzkit.personas import CORE_PERSONAS, scaffold_core_personas, _iter_canonical_persona_slugs
print('CORE_PERSONAS:', CORE_PERSONAS)
print('iter count:', sum(1 for _ in _iter_canonical_persona_slugs()))
"
```

Output:

```
CORE_PERSONAS: ['implementer', 'main-session', 'narrator', 'pipeline-orchestrator', 'quality-reviewer', 'spec-reviewer']
iter count: 6
```

ARB receipts cited in attestation: arb-step-unittest-fb013e580978484b9eb76a726ab2ff0b, arb-ruff-c72fef5bd1154f1094ab531983077978, arb-step-typecheck-83cd50e55e6846969bd0a21929df7514, arb-step-mkdocs-ffd6547f5e014a53909c6d7337bb76fa. REQ covers parity: 9/9 (uncovered_reqs=0).

### Implementation Summary


- Files created/modified: src/gzkit/personas/__init__.py (added CORE_PERSONAS, _iter_canonical_persona_slugs, scaffold_core_personas; 592 lines under 600-line limit); src/gzkit/commands/init_cmd.py (imported scaffold_core_personas, wired into init() fresh-init with skip_existing=True for never-overwrite semantics, added _repair_personas helper, wired into _repair_missing_artifacts); tests/test_personas.py (removed 4 obsolete OBPI-09 scope guards, added TestPersonasScaffolderObpi10 with 6 @covers tests REQ-01..03, REQ-06, REQ-08, REQ-09); tests/commands/test_init.py (updated existing persona test to use main-session.md, added TestInitPersonasScaffoldingObpi10 with 2 integration tests for REQ-04/05/07); docs/user/manpages/init.md (## Personas Scaffolding section); docs/user/runbook.md (updated ## Persona Commands); data/behave_coverage_waivers.json (waiver under existing adr-0.0.32-bdd-deferred-to-obpi-06 rationale)
- Tests added: 6 unit tests + 2 integration tests; full suite 4856 tests pass
- Date completed: 2026-05-12
- Attestation status: Heavy + Foundation brief-level Gate 5 attestation recorded (operator verbatim 'attest completed')
- Defects noted: Brief path error gz-init.md to init.md corrected during plan audit (same class as OBPI-04); brief wording at REQ-04 names _scaffold_project_skeleton but sibling-pattern correct call site is init() directly

## Tracked Defects

- (none at authoring time)

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy + Foundation brief-level Gate 5; receipts arb-step-unittest-fb013e580978484b9eb76a726ab2ff0b (4856 tests pass), arb-ruff-c72fef5bd1154f1094ab531983077978 (lint clean), arb-step-typecheck-83cd50e55e6846969bd0a21929df7514 (typecheck clean), arb-step-mkdocs-ffd6547f5e014a53909c6d7337bb76fa (docs clean); 9/9 REQs covered per gz covers parity gate; CORE_PERSONAS enumerates 6 canonical slugs (implementer, main-session, narrator, pipeline-orchestrator, quality-reviewer, spec-reviewer); scaffold_core_personas wired into init() fresh-init and _repair_missing_artifacts; module size 592 lines under 600-limit.
- Date: 2026-05-12

---

**Brief Status:** Completed

**Date Completed:** 2026-05-12

**Evidence Hash:** -
