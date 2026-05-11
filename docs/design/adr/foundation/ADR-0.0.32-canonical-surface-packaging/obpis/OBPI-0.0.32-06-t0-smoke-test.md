---
id: OBPI-0.0.32-06-t0-smoke-test
parent: ADR-0.0.32-canonical-surface-packaging
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.32-06-t0-smoke-test: T0 Smoke Test + Wheel Includes Audit

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #6 — "Author T0 smoke test (build wheel, install into temp venv, run `gz init`, assert byte-equivalence of the resulting `.gzkit/` tree against frozen baseline manifest); audit and extend `pyproject.toml [tool.hatch.build.targets.wheel] include:`; author `data/distribution_baseline_manifest.json`."

**Status:** Draft

## Objective

Author the build-then-install smoke test that mechanically enforces the T0 distribution invariant authored by ADR-0.0.31. Concretely: a behave scenario (or equivalent) that builds the wheel via `uv build`, installs it into a temp venv via `uv pip install`, runs `gz init` in a fresh adopter project, and asserts every canonical-surface file the wheel ships (sourced from `src/gzkit/<surface>/` in the gzkit dev repo — the byte-equivalent copy of `.gzkit/<surface>/` authored canonical) lands in the adopter's `.gzkit/<surface>/` byte-equivalent (modulo project-name substitution) against a frozen baseline manifest checked in at `data/distribution_baseline_manifest.json`. The smoke test exercises the full canonical-routing chain end-to-end: gzkit-dev-repo `.gzkit/<surface>/` (authored) → `src/gzkit/<surface>/` (byte-equivalent, wheel-shipped via includes) → adopter's `.gzkit/<surface>/` (post-`gz init`). Audit and extend `pyproject.toml [tool.hatch.build.targets.wheel] include:` to cover every canonical surface (skills, rules, hooks, templates, personas) under `src/gzkit/` — closing failure class C from GHI #318.

## Lane

**Heavy** — adds a build-tier test surface, modifies the wheel ship contract via `pyproject.toml`, introduces a baseline manifest as part of the build invariant. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `pyproject.toml` — extend `[tool.hatch.build.targets.wheel] include:` for `src/gzkit/skills/**/*.md`, `src/gzkit/rules/**/*.md`, `src/gzkit/templates/*.md`, `src/gzkit/hooks/scripts/**`, `src/gzkit/personas/**`; audit exclude block to avoid stripping the new content
- `features/distribution_invariant.feature` — new behave feature for the T0 smoke test
- `features/steps/distribution_invariant_steps.py` — step definitions for build-install-init scenario
- `data/distribution_baseline_manifest.json` — frozen baseline naming every file the wheel MUST deliver to a fresh `gz init` (per-surface lists; one entry per canonical artifact)
- `tests/distribution/test_baseline_manifest.py` — unit-level coverage of baseline-manifest schema and load/parse logic; the build-install-init scenario itself lives in behave per `.gzkit/rules/tests.md` § Two runners
- `docs/governance/distribution_baseline.md` — short doc explaining the baseline manifest's role, refresh discipline, and how to update it when a new canonical surface lands

## Denied Paths

- `src/gzkit/skills/**`, `src/gzkit/rules/**` — content moves belong to OBPI-0.0.32-01 / -02; this OBPI consumes those moves to assert wheel coverage
- `src/gzkit/commands/init_cmd.py` — `--update` belongs to OBPI-0.0.32-05; init dispatch unchanged here
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-0.0.32-07
- `.claude/skills/**`, `.github/skills/**`, `.github/instructions/**` — mirror sync belongs to OBPI-0.0.32-08
- `docs/governance/trust-doctrine.md` — T0 doctrine prose belongs to OBPI-0.0.31-01
- Canonical content edits in this OBPI — the baseline manifest captures the current canonical state; content authoring is out of scope

## Requirements (FAIL-CLOSED)

1. `pyproject.toml [tool.hatch.build.targets.wheel] include:` MUST grow to cover every canonical surface that ships with the wheel: skills (already added by OBPI-0.0.32-01), rules (added by OBPI-0.0.32-02), templates (`src/gzkit/templates/*.md`), hooks (`src/gzkit/hooks/scripts/**`), personas (`src/gzkit/personas/**`). Audit gap: every directory under `src/gzkit/` that contains operator-facing canonical content MUST be in the include list.
2. The `exclude` block MUST NOT strip any newly-included content. Verify by `python -m build && unzip -l dist/py_gzkit-*.whl` after each include addition.
3. `data/distribution_baseline_manifest.json` MUST be authored at this OBPI's landing time and MUST list every canonical artifact the wheel ships, organized by surface. Schema (proposed):
   ```json
   {
     "schema_version": "1.0",
     "gzkit_version": "X.Y.Z",
     "surfaces": {
       "skills": ["gz-prd/SKILL.md", "gz-plan/SKILL.md", ...],
       "rules": ["cli.md", "tests.md", ...],
       "templates": ["adr.md", "obpi.md", ...],
       "hooks": ["scripts/<name>.sh", ...],
       "personas": ["main-session.md", ...]
     }
   }
   ```
4. The behave scenario MUST execute end-to-end: `uv build` → `uv venv .smoke-venv` → `uv pip install dist/py_gzkit-*.whl` → run `gz init` in a fresh tempdir using the smoke venv's `gz` binary → enumerate `.gzkit/` artifacts → cross-check against `data/distribution_baseline_manifest.json` → assert byte-equivalence (or content-equivalence after project-name substitution where applicable).
5. The scenario MUST tag with `@REQ-0.0.32-06-NN` per `.gzkit/rules/tests.md` behave-tagging.
6. The scenario MUST clean up the smoke venv and tempdir on success AND failure (use behave fixtures or hooks).
7. The scenario MUST exit non-zero if any baseline-manifest entry is missing from the install or if any installed canonical artifact is NOT in the baseline (catches both directions of drift).
8. `mkdocs build --strict` MUST pass after the new doc + baseline manifest land.
9. Unit tests in `tests/distribution/test_baseline_manifest.py` MUST cover: (a) manifest parses against a frozen schema, (b) every entry resolves to a real file under the canonical source, (c) duplicate detection.
10. The scenario's runtime cost (build + install + init + assert) MUST be documented; if it exceeds 60s, it MUST be tagged so it can be excluded from the standard `gz test` smoke run and gated behind `gz check` or a CI-only marker.
11. `uv run gz check` MUST exit 0 with the new wheel includes; the smoke scenario itself runs under `uv run -m behave features/distribution_invariant.feature`.

> STOP-on-BLOCKERS:
> - If OBPI-0.0.32-01 or OBPI-0.0.32-02 has not landed (no canonical package surfaces exist for skills/rules), STOP — the smoke test would assert against an unshipped surface.
> - If `uv build` fails for unrelated reasons (existing pyproject.toml issues), STOP and surface the build defect as a separate GHI before extending includes.
> - If a canonical-surface directory has files OTHER than the expected types (e.g. a binary in `src/gzkit/templates/`), STOP and decide whether the include glob covers it; the baseline manifest is only valid if it captures every shipped file.
> - If the smoke test's runtime exceeds the project's CI budget (today ~10 minutes total for `gz check`), STOP and decide whether to tag it `@slow` and run only on release branches.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Intent — the dogfood-loop blindness that the smoke test falsifies
- [ ] Parent ADR § Decision — package layout + smoke-test scope
- [ ] Parent ADR § Alternatives Considered E — why we chose the build-then-install smoke over trusting unit tests
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] ADR-0.0.31 § Decision — Mechanical-enforcement contract (this OBPI is the smoke-test arm of that contract)
- [ ] `.gzkit/rules/tests.md` § Two runners — why the smoke test belongs in `features/`, not `tests/`
- [ ] `.gzkit/rules/tests.md` § Behave scenario tagging — `@REQ-0.0.32-06-NN` requirement
- [ ] `.claude/rules/cross-platform.md` — UTF-8 + subprocess discipline; the smoke test invokes `uv build` and `uv pip install` which must work on Windows + macOS + Linux

**Context — chores precedent + sibling OBPIs:**

- [ ] `pyproject.toml [tool.hatch.build.targets.wheel] include:` current state — chores entries are the template
- [ ] `features/chores_distribution.feature` (OBPI-0.0.21-07) — likely already exists as a chores-distribution scenario; read it as a precedent for the build-install-init shape
- [ ] OBPI-0.0.32-01 + -02 — the canonical-surface promotions this OBPI consumes

**Prerequisites (check existence, STOP if missing):**

- [ ] `uv build` works on the current `pyproject.toml` (run once; if it fails for unrelated reasons, escalate)
- [ ] `features/` directory exists with at least one existing `.feature` file (sanity-check the runner is configured)
- [ ] `data/` directory exists or is intentionally created for the baseline manifest

**Existing Code:**

- [ ] Read `pyproject.toml` `[tool.hatch.build.targets.wheel]` block end-to-end before extending
- [ ] Read `src/gzkit/chores/__init__.py` — chores ships with the chores-distribution behave precedent; the test pattern likely transfers
- [ ] Audit every directory under `src/gzkit/` that ships canonical content: `skills/`, `rules/`, `chores/`, `templates/`, `hooks/`, `personas/`; enumerate the file types and confirm the include globs cover them

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #4 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: behave scenario fails before wheel includes are extended (the install would be missing canonical content)
- [ ] GREEN: scenario passes after includes are extended and baseline manifest is authored
- [ ] Coverage above 40% floor (unit-tier baseline-manifest tests count toward coverage; the behave scenario does not)

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `docs/governance/distribution_baseline.md` documents the baseline manifest, refresh discipline, and how to update on new surface promotion
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] `features/distribution_invariant.feature` exists with at least one scenario tagged `@REQ-0.0.32-06-01`
- [ ] `uv run -m behave features/distribution_invariant.feature` passes

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

uv build
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/skills/.*SKILL\.md"     # expect 61
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/rules/.*\.md"           # expect ≥14
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/templates/.*"           # expect non-zero
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/hooks/scripts/"         # expect non-zero (when hooks ship)
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/personas/"              # expect non-zero (when personas ship)

uv run -m behave features/distribution_invariant.feature --tags=@REQ-0.0.32-06-01

python -c "import json; m=json.load(open('data/distribution_baseline_manifest.json')); print('surfaces:', list(m['surfaces'].keys()))"
```

## Acceptance Criteria

- [ ] REQ-0.0.32-06-01: `features/distribution_invariant.feature` exists with the build-install-init smoke scenario tagged `@REQ-0.0.32-06-01`; the scenario passes
- [ ] REQ-0.0.32-06-02: `pyproject.toml [tool.hatch.build.targets.wheel] include:` covers every canonical surface (skills, rules, templates, hooks, personas)
- [ ] REQ-0.0.32-06-03: `data/distribution_baseline_manifest.json` exists, validates against a frozen schema, lists every canonical artifact organized by surface
- [ ] REQ-0.0.32-06-04: The smoke scenario detects DRIFT in both directions — missing baseline entries in install AND extra installed artifacts not in baseline
- [ ] REQ-0.0.32-06-05: `tests/distribution/test_baseline_manifest.py` covers schema parse, file-resolution, and duplicate detection
- [ ] REQ-0.0.32-06-06: `docs/governance/distribution_baseline.md` documents baseline-manifest role, refresh discipline, and update-on-surface-promotion procedure; `mkdocs build --strict` passes
- [ ] REQ-0.0.32-06-07: Smoke-test runtime is documented; if >60s, tagged so `gz test` smoke can exclude it
- [ ] REQ-0.0.32-06-08: `uv run gz check` exits 0 with the new includes
- [ ] REQ-0.0.32-06-09: Built wheel contains 61 SKILL.md files + ≥14 rule .md files + canonical templates + canonical hook scripts + canonical personas

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Baseline-manifest doc + mkdocs --strict pass
- [ ] **Gate 4 (BDD):** Smoke scenario passes
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output for baseline-manifest tests
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

Before this OBPI: T0 was advisory doctrine; the wheel could ship without canonical content and the only signal was a downstream consumer noticing. After this OBPI: a build-install-init smoke scenario fails CI any time a canonical artifact stops shipping, and the baseline manifest gives every future surface promotion a checklist entry. The dogfood loop is no longer the only line of defense. Closes failure class C from GHI #318.

### Key Proof

```bash
uv run -m behave features/distribution_invariant.feature
# Expected: scenario passes; CI fails on any T0 drift in either direction
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — failure class C addressed by this OBPI

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
