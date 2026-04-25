---
id: OBPI-0.0.32-02-rules-canonical-promotion
parent: ADR-0.0.32-canonical-surface-packaging
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.32-02-rules-canonical-promotion: Rules Canonical Promotion

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #2 — "Author `src/gzkit/rules/` package surface; convert `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py`; build `CORE_RULES` registry, `scaffold_core_rules`; integrate with `init_cmd.py` and `_repair_missing_artifacts`"

**Status:** Draft

## Objective

Move 14 hand-authored canonical rule files from `.gzkit/rules/<slug>.md` into wheel-shipped package data at `src/gzkit/rules/<slug>.md` (file-not-dir layout, distinct from skills/chores). Convert `src/gzkit/rules.py` (563 lines) into `src/gzkit/rules/__init__.py` so `from gzkit.rules import X` import sites continue to resolve. Author a new `CORE_RULES` registry symmetric to `CORE_SKILLS` and `CORE_CHORES`. Author `scaffold_core_rules` mirroring `scaffold_core_chores`/`scaffold_core_skills` semantics. Wire `scaffold_core_rules` into `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair). After this OBPI lands, `pip install py-gzkit && gz init` produces canonical rule files at `.gzkit/rules/` — closing failure class A from GHI #318 (rules entirely unscaffolded).

## Lane

**Heavy** — restructures Python package layout (module → package), introduces a new public registry (`CORE_RULES`) and a new public scaffolder (`scaffold_core_rules`), and changes what the wheel ships. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/rules.py` — convert to package; delete the file after content moves
- `src/gzkit/rules/__init__.py` — receives the contents of the former `src/gzkit/rules.py` plus `CORE_RULES`, `_iter_canonical_rule_slugs`, `scaffold_core_rules`
- `src/gzkit/rules/<slug>.md` — destination of `git mv` from `.gzkit/rules/<slug>.md` (14 files, including `AGENTS.md` if it lives under `.gzkit/rules/`)
- `.gzkit/rules/<slug>.md` — source of `git mv`; project-overlay layer remains valid for project-local rules but canonical content moves to package
- `pyproject.toml` — extend `[tool.hatch.build.targets.wheel] include:` with `src/gzkit/rules/**/*.md`
- `src/gzkit/commands/init_cmd.py` — add `scaffold_core_rules` invocation in `_scaffold_project_skeleton` and `_repair_missing_artifacts`
- `tests/test_rules.py`, `tests/commands/test_init.py` — unit tests for `CORE_RULES`, `scaffold_core_rules`, init-cmd integration, project-first → package-fallback resolution

## Denied Paths

- `src/gzkit/skills.py`, `src/gzkit/skills/**` — skills promotion is OBPI-0.0.32-01; no bundling
- `src/gzkit/hooks/**`, `src/gzkit/personas/**`, `src/gzkit/templates/*.md` — out of scope for this OBPI
- `features/distribution_invariant.feature` — T0 smoke test belongs to OBPI-0.0.32-04
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-0.0.32-05
- `.claude/rules/`, `.github/instructions/` — mirror regeneration belongs to OBPI-0.0.32-06; mirrors may be temporarily stale
- `docs/governance/trust-doctrine.md` — T0 doctrine paragraph belongs to OBPI-0.0.31-01
- Any rule file content edits — this OBPI moves files byte-identical; semantic edits to rules are out of scope

## Requirements (FAIL-CLOSED)

1. `git mv .gzkit/rules/<slug>.md src/gzkit/rules/<slug>.md` MUST be used for every one of the 14 canonical rules so git history is preserved.
2. After the moves, `src/gzkit/rules/<slug>.md` MUST be byte-identical to the pre-move `.gzkit/rules/<slug>.md`. No content edits in this OBPI.
3. `src/gzkit/rules.py` MUST NOT exist after this OBPI. Its contents MUST move to `src/gzkit/rules/__init__.py` such that every `from gzkit.rules import X` import site in `src/` and `tests/` continues to resolve without modification.
4. `CORE_RULES` MUST be authored as a registry (list of slugs OR dict-of-slug-to-metadata, mirroring `CORE_SKILLS` / `CORE_CHORES` shape) in `src/gzkit/rules/__init__.py`. Every one of the 14 canonical rule slugs MUST appear in `CORE_RULES`.
5. `scaffold_core_rules(project_root, config, *, skip_existing=False)` MUST exist in `src/gzkit/rules/__init__.py` and MUST mirror `scaffold_core_chores` semantics: enumerate canonical rules from `importlib.resources.files("gzkit.rules")`, write each to `<project_root>/.gzkit/rules/<slug>.md`, honor `skip_existing`, return the list of newly-created slugs.
6. `init_cmd._scaffold_project_skeleton` MUST invoke `scaffold_core_rules` for fresh init; `_repair_missing_artifacts` MUST invoke it with `skip_existing=True` for re-run repair.
7. Project-first → package-fallback resolution MUST hold: a project-local `.gzkit/rules/<slug>.md` is preserved; a missing one is filled from package canonical via `importlib.resources`.
8. `pyproject.toml [tool.hatch.build.targets.wheel] include:` MUST grow to include `src/gzkit/rules/**/*.md`.
9. Unit tests MUST cover: (a) `CORE_RULES` enumerates all 14 slugs, (b) `scaffold_core_rules` writes byte-identical content, (c) `skip_existing=True` preserves operator edits, (d) `init_cmd` integration produces `.gzkit/rules/` content in a fresh tempdir, (e) `from gzkit.rules import X` continues to work for every previously-public symbol (`RuleFrontmatter`, `load_rules`, `render_rules_to_dir`, `sync_claude_rules`, `sync_nested_agents_md`, `_parse_instruction_frontmatter`, `_extract_body_after_frontmatter`, `_extract_subtree_prefix`, `validate_rule_placement`, `ClassifiedRule`).
10. The 14 moved files MUST appear in the built wheel: `unzip -l dist/py_gzkit-*.whl | grep "gzkit/rules/.*\.md" | wc -l` MUST return ≥14.
11. `uv run gz check` MUST exit 0 after the conversion lands.

> STOP-on-BLOCKERS:
> - If `src/gzkit/rules/` already exists as a directory (sanity check), STOP and investigate.
> - If `.gzkit/rules/` contains files OTHER than `.md` (e.g. JSON, YAML), STOP and decide per-file whether to move with.
> - If `src/gzkit/rules/__init__.py` schema (`RuleFrontmatter`) and `CORE_RULES` registry would conflict (e.g. a slug containing `/`), STOP and decide on the registry shape before authoring.
> - If `scaffold_core_rules` integration in `init_cmd.py` would conflict with the existing `scaffold_core_chores` and `scaffold_core_skills` ordering (rules must scaffold BEFORE chores/skills if any of them reference rule files), STOP and document the dependency order.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Intent — names failure class A (rules entirely unscaffolded)
- [ ] Parent ADR § Decision — package layout block, `src/gzkit/rules/<slug>.md` (file-not-dir layout)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/skill-surface-sync.md` — body-level rule-version marker convention; the new package layout must preserve this
- [ ] `.gzkit/rules/tests.md` — RGR discipline
- [ ] `.gzkit/rules/cross-platform.md` — `pathlib.Path`, UTF-8 encoding rules apply

**Context — chores precedent (read closely):**

- [ ] `src/gzkit/chores/__init__.py` — `_iter_canonical_chore_slugs`, `scaffold_core_chores`, `_CANONICAL_RESOURCE`
- [ ] `src/gzkit/commands/init_cmd.py` lines 26 (`from gzkit.chores import …`), 242 (`scaffold_core_chores` call) — the integration pattern to mirror
- [ ] OBPI-0.0.32-01 (sibling) — same conversion pattern applied to skills

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/rules.py` exists at 563 lines
- [ ] 14 files under `.gzkit/rules/` (`ls .gzkit/rules/*.md | wc -l` returns 14)
- [ ] `src/gzkit/rules/` does NOT yet exist as a directory
- [ ] `src/gzkit/chores/__init__.py` exists (precedent)
- [ ] Git working tree clean before starting

**Existing Code (understand current state):**

- [ ] Every public symbol in `src/gzkit/rules.py` enumerated for re-export
- [ ] Every `from gzkit.rules import X` and `import gzkit.rules` site enumerated (`grep -rn "from gzkit.rules\|import gzkit.rules" src/ tests/`)
- [ ] `src/gzkit/commands/init_cmd.py` `_scaffold_project_skeleton` and `_repair_missing_artifacts` read end-to-end before integration

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #2 quoted verbatim above

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for `CORE_RULES` and `scaffold_core_rules` fail before implementation
- [ ] GREEN: tests pass after package conversion + scaffolder authoring + init integration
- [ ] Coverage above 40% floor
- [ ] `uv run gz test` passes

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-init.md` updated to mention rule scaffolding
- [ ] `docs/user/runbook.md` rules section updated
- [ ] `.claude/rules/skill-surface-sync.md` updated — references to "hand-authored canonical rules at `.gzkit/rules/`" become "package-shipped canonical rules under `src/gzkit/rules/`"
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] `features/init.feature` extended with a scenario asserting fresh-init produces canonical rule files at `.gzkit/rules/`

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test ! -f src/gzkit/rules.py
test -f src/gzkit/rules/__init__.py
ls src/gzkit/rules/*.md | wc -l
python -c "from gzkit.rules import CORE_RULES, scaffold_core_rules, RuleFrontmatter, load_rules; print('imports OK', len(CORE_RULES))"
python -c "import importlib.resources; r=importlib.resources.files('gzkit.rules'); print(sum(1 for e in r.iterdir() if e.name.endswith('.md')))"

uv build
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/rules/.*\.md"

# Integration smoke (manual)
mkdir /tmp/gz-rules-smoke && cd /tmp/gz-rules-smoke && uv run gz init && ls .gzkit/rules/
```

## Acceptance Criteria

- [ ] REQ-0.0.32-02-01: All 14 rule files moved via `git mv` from `.gzkit/rules/<slug>.md` to `src/gzkit/rules/<slug>.md`; git history preserved
- [ ] REQ-0.0.32-02-02: `src/gzkit/rules.py` does not exist post-OBPI; its contents live at `src/gzkit/rules/__init__.py`
- [ ] REQ-0.0.32-02-03: `CORE_RULES` registry exists in `src/gzkit/rules/__init__.py` and enumerates all 14 canonical slugs
- [ ] REQ-0.0.32-02-04: `scaffold_core_rules(project_root, config, *, skip_existing=False)` exists with the same surface as `scaffold_core_chores`/`scaffold_core_skills`
- [ ] REQ-0.0.32-02-05: `init_cmd._scaffold_project_skeleton` invokes `scaffold_core_rules` for fresh init
- [ ] REQ-0.0.32-02-06: `init_cmd._repair_missing_artifacts` invokes `scaffold_core_rules(skip_existing=True)` for re-run repair
- [ ] REQ-0.0.32-02-07: Project-first → package-fallback resolution holds for rules
- [ ] REQ-0.0.32-02-08: `pyproject.toml` wheel `include:` covers `src/gzkit/rules/**/*.md`; built wheel contains ≥14 .md files under `gzkit/rules/`
- [ ] REQ-0.0.32-02-09: Every previously-public symbol in `gzkit.rules` (RuleFrontmatter, load_rules, render_rules_to_dir, sync_claude_rules, sync_nested_agents_md, validate_rule_placement, ClassifiedRule, plus internal helpers used by tests) remains importable
- [ ] REQ-0.0.32-02-10: `uv run gz check` exits 0
- [ ] REQ-0.0.32-02-11: A fresh `gz init` in a temp directory produces 14 rule files at `.gzkit/rules/`

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed; tests + coverage recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage + runbook + skill-surface-sync rule updated; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Fresh-init scenario added and passing
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output (RED then GREEN), coverage delta
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
# Paste behave scenario output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: `pip install py-gzkit && gz init` produced zero rule files. Contextual rule loading silently no-opped because `.gzkit/rules/` did not exist. After this OBPI: fresh init produces all 14 canonical rule files; `CORE_RULES` is the symmetric counterpart to `CORE_SKILLS`/`CORE_CHORES`; future rule promotions follow the documented two-surface pattern. Closes failure class A from GHI #318.

### Key Proof

```bash
mkdir /tmp/gz-rules-smoke && cd /tmp/gz-rules-smoke && uv run gz init && ls .gzkit/rules/ | wc -l
# Expected: 14
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — failure class A addressed by this OBPI

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
