---
id: OBPI-0.0.32-12-templates-scaffolder-authoring
parent: ADR-0.0.32-canonical-surface-packaging
item: 12
lane: Heavy
status: Draft
---

# OBPI-0.0.32-12-templates-scaffolder-authoring: Templates Scaffolder Authoring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #12 — "Templates scaffolder authoring — build `CORE_TEMPLATES` registry symmetric to `CORE_SKILLS`/`CORE_RULES`/`CORE_PERSONAS`/`CORE_CHORES`; author `scaffold_core_templates` that copies canonical template content from `importlib.resources.files(\"gzkit.templates\")` (the wheel's package surface) into the adopter's `.gzkit/templates/<name>.md`; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair); preserve `render_template()` resolution semantics so it consults the adopter's `.gzkit/templates/` project-first per the same project-first → package-fallback shape. Depends on OBPI-11 landing first."

**Status:** Draft

## Objective

After OBPI-11 has landed the templates dual-surface (13+ canonical template files retained at `.gzkit/templates/<name>.md` AND byte-equivalent copies at `src/gzkit/templates/<name>.md`, `src/gzkit/templates/__init__.py` exists), author the templates scaffolding surface that brings adopter-side templates into the canonical-routing model. Build a `CORE_TEMPLATES` registry symmetric to the other `CORE_<SURFACE>` registries. Author `scaffold_core_templates(project_root, config, *, skip_existing=False)` mirroring sibling scaffolder semantics — enumerate canonical templates from `importlib.resources.files("gzkit.templates")` (the wheel's package surface), write each to `<project_root>/.gzkit/templates/<name>.md` (the adopter's project canonical surface-of-truth), honor `skip_existing`, return the list of newly-created slugs. Wire `scaffold_core_templates` into `init_cmd._scaffold_project_skeleton` (for fresh init) and `_repair_missing_artifacts` (for re-run repair).

**Project-first → package-fallback resolution for `render_template()`** — after this OBPI lands, `render_template(name, ...)` in an adopter project MUST consult the adopter's `.gzkit/templates/<name>.md` FIRST (preserving operator edits to the project canonical surface); if absent, fall back to the wheel's package surface via `importlib.resources.files("gzkit.templates")`. This shifts the resolution semantics from "templates are package-internal only" (today) to "templates are operator-editable at the adopter's `.gzkit/templates/`, with the wheel as bootstrap source". After OBPI-11 + OBPI-12 land jointly, the adopter's `.gzkit/templates/` is their project canonical source-of-truth per ADR-0.0.32 § Decision's binding canonical-routing invariant.

## Lane

**Heavy** — introduces a new public registry (`CORE_TEMPLATES`) and a new public scaffolder (`scaffold_core_templates`); changes the runtime contract of `gz init` to produce template content AND changes the runtime contract of `render_template()` to consult the project-canonical surface first. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/templates/__init__.py` — add `CORE_TEMPLATES`, `_iter_canonical_template_slugs()`, `scaffold_core_templates`; update `render_template()` (if it lives here) to project-first → package-fallback resolution
- `src/gzkit/commands/init_cmd.py` — invoke `scaffold_core_templates` from `_scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts(skip_existing=True)` (re-run repair)
- `tests/test_templates.py`, `tests/commands/test_init.py` — unit tests for `CORE_TEMPLATES`, `scaffold_core_templates`, init-cmd integration, project-first → package-fallback resolution, `render_template()` project-first behavior
- `docs/user/manpages/gz-init.md` — mention template scaffolding alongside skills + rules + personas + chores
- `docs/user/runbook.md` — runbook section for templates surface

## Denied Paths

- Physical migration / `src/gzkit/templates/<name>.md` content edits — owned by OBPI-11
- `src/gzkit/skills/**`, `src/gzkit/rules/**`, `src/gzkit/personas/**`, `src/gzkit/chores/**` — other surfaces' scaffolders belong to their own OBPIs
- `pyproject.toml` — wheel includes belong to OBPI-06
- `features/**` — behave belongs to OBPI-06
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- Template content edits — this OBPI consumes the canonical content from OBPI-11; no semantic edits to templates

## Requirements (FAIL-CLOSED)

1. `CORE_TEMPLATES` MUST be authored as a registry in `src/gzkit/templates/__init__.py` mirroring the shape of `CORE_SKILLS`, `CORE_RULES`, `CORE_PERSONAS`, and `CORE_CHORES`. Every canonical template name (13+ slugs at this OBPI's authoring time) MUST appear.
2. `_iter_canonical_template_slugs()` MUST exist mirroring the sibling enumerators: enumerate via `importlib.resources.files("gzkit.templates")`, skip `__pycache__`-style entries and non-`.md` adjuncts, yield each canonical-slug `Traversable`.
3. `scaffold_core_templates(project_root, config, *, skip_existing=False)` MUST exist with the exact same surface shape as sibling scaffolders.
4. `init_cmd._scaffold_project_skeleton` MUST invoke `scaffold_core_templates` for fresh init.
5. `init_cmd._repair_missing_artifacts` MUST invoke `scaffold_core_templates(skip_existing=True)` for re-run repair.
6. `render_template(name, context)` MUST adopt project-first → package-fallback resolution: when running in a project where `.gzkit/templates/<name>.md` exists, that file is the template source; otherwise the wheel's package surface (`importlib.resources.files("gzkit.templates")/<name>.md`) is consulted. The pre-OBPI behavior (package-only) MUST NOT silently survive.
7. Unit tests MUST cover: (a) `CORE_TEMPLATES` enumerates all canonical slugs, (b) `_iter_canonical_template_slugs()` returns the same count, (c) `scaffold_core_templates` writes byte-identical content from package, (d) `skip_existing=True` preserves operator edits, (e) `init_cmd` integration produces `.gzkit/templates/` content in a fresh tempdir, (f) `render_template()` project-first resolution chooses the project copy when present.
8. `uv run gz check` MUST exit 0 after the authoring lands.
9. `mkdocs build --strict` MUST pass; manpage + runbook updates MUST land in the same patch as scaffolder behavior changes per `.claude/rules/gate5-runbook-code-covenant.md`.

> STOP-on-BLOCKERS:
> - If OBPI-11 has not landed (templates not yet dual-surface), STOP — there is no canonical surface for the scaffolder to consume.
> - If `importlib.resources.files("gzkit.templates")` does not resolve at runtime, STOP — the OBPI-11 package state may have an issue.
> - If `render_template()` is currently consumed in a way that depends on package-only resolution semantics (e.g., a test that mocks `importlib.resources` directly), STOP and reconcile the consumer before changing the resolution path.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — § Canonical-routing scope (templates row + scaffolder column)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.gzkit/rules/tests.md` — RGR discipline
- [ ] `.claude/rules/skill-surface-sync.md` — project-first → package-fallback resolution semantics for adopter project-local edits

**Context — sibling OBPIs:**

- [ ] OBPI-0.0.32-11 (sibling) — physical reverse-migration; must land first
- [ ] OBPI-0.0.32-02 / -04 / -10 — same scaffolder pattern applied to other surfaces
- [ ] `src/gzkit/chores/__init__.py` — chores precedent for `_iter_canonical_chore_slugs` + `scaffold_core_chores`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-11 landed (13+ template files at `src/gzkit/templates/<name>.md` AND at `.gzkit/templates/<name>.md` byte-equivalent)
- [ ] `src/gzkit/templates/__init__.py` exists (post-OBPI-11)
- [ ] `src/gzkit/chores/__init__.py` exists (precedent)

**Existing Code:**

- [ ] Read existing `render_template()` body end-to-end before changing resolution semantics
- [ ] Read `init_cmd._scaffold_project_skeleton` and `_repair_missing_artifacts` to identify exact call-site placement for `scaffold_core_templates`
- [ ] Enumerate every `render_template()` call site in `src/`, `tests/`, and `features/`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #12 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for `CORE_TEMPLATES`, `scaffold_core_templates`, init-cmd integration, and `render_template()` project-first resolution fail before implementation
- [ ] GREEN: tests pass after authoring + integration + resolution-path change
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-init.md` mentions template scaffolding
- [ ] `docs/user/runbook.md` templates section added
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios in this OBPI; OBPI-06 owns the build-install-init smoke that exercises templates end-to-end

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

python -c "from gzkit.templates import CORE_TEMPLATES, scaffold_core_templates, _iter_canonical_template_slugs; print('imports OK', len(CORE_TEMPLATES), sum(1 for _ in _iter_canonical_template_slugs()))"  # expect 13+, 13+

mkdir /tmp/gz-templates-scaffold-smoke && cd /tmp/gz-templates-scaffold-smoke && uv run gz init && ls .gzkit/templates/*.md | wc -l   # expect 13+

# Project-first resolution: edit a project-local template, render uses the edit
echo "PROJECT-EDIT" >> /tmp/gz-templates-scaffold-smoke/.gzkit/templates/adr.md
cd /tmp/gz-templates-scaffold-smoke && uv run python -c "from gzkit.templates import render_template; print('PROJECT-EDIT' in render_template('adr.md', {'id':'T','title':'T'}))"  # expect True
```

## Demo

```bash
mkdir /tmp/gz-templates-demo && cd /tmp/gz-templates-demo
uv run gz init
ls .gzkit/templates/
head -10 .gzkit/templates/adr.md
```

## Acceptance Criteria

- [ ] REQ-0.0.32-12-01: `CORE_TEMPLATES` registry exists in `src/gzkit/templates/__init__.py`; enumerates all 13+ canonical template slugs
- [ ] REQ-0.0.32-12-02: `_iter_canonical_template_slugs()` exists, mirrors sibling enumerators, returns same count
- [ ] REQ-0.0.32-12-03: `scaffold_core_templates(project_root, config, *, skip_existing=False)` exists with exact-same surface as sibling scaffolders
- [ ] REQ-0.0.32-12-04: `init_cmd._scaffold_project_skeleton` invokes `scaffold_core_templates` for fresh init
- [ ] REQ-0.0.32-12-05: `init_cmd._repair_missing_artifacts` invokes `scaffold_core_templates(skip_existing=True)` for re-run repair
- [ ] REQ-0.0.32-12-06: `render_template()` adopts project-first → package-fallback resolution; project-local `.gzkit/templates/<name>.md` (when present) is consulted before package surface
- [ ] REQ-0.0.32-12-07: A fresh `gz init` in a tempdir produces 13+ canonical template files at `.gzkit/templates/`
- [ ] REQ-0.0.32-12-08: `skip_existing=True` preserves operator edits to `.gzkit/templates/<name>.md`
- [ ] REQ-0.0.32-12-09: `docs/user/manpages/gz-init.md` mentions template scaffolding; `docs/user/runbook.md` templates section landed; `mkdocs build --strict` passes
- [ ] REQ-0.0.32-12-10: `uv run gz check` exits 0

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

Before this OBPI: templates were package-internal scaffolder inputs; `render_template()` consulted the package surface only; adopters had no path to override templates without monkey-patching gzkit's package data. After this OBPI: `gz init` reads canonical template content from the wheel's package surface (`importlib.resources.files("gzkit.templates")`) and writes 13+ canonical templates into the adopter's `.gzkit/templates/`. `render_template()` adopts project-first → package-fallback resolution so adopter edits to `.gzkit/templates/<name>.md` take effect immediately. Once written, the adopter's `.gzkit/templates/` is their project canonical source-of-truth per ADR-0.0.32 § Decision's binding canonical-routing invariant.

### Key Proof

```bash
mkdir /tmp/gz-templates-scaffold-smoke && cd /tmp/gz-templates-scaffold-smoke && uv run gz init && ls .gzkit/templates/*.md | wc -l
# Expected: 13+
echo "PROJECT-EDIT" >> .gzkit/templates/adr.md
uv run python -c "from gzkit.templates import render_template; print('PROJECT-EDIT' in render_template('adr.md', {'id':'T','title':'T'}))"
# Expected: True (project-first resolution honored operator edit)
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- (none at authoring time)

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
