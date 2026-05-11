---
id: OBPI-0.0.32-03-rules-physical-migration
parent: ADR-0.0.32-canonical-surface-packaging
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.32-03-rules-physical-migration: Rules Physical Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #3 — "Rules physical migration — establish dual-surface for all 14 canonical rules: retain `.gzkit/rules/<slug>.md` as authored source-of-truth AND add byte-equivalent copy at `src/gzkit/rules/<slug>.md` for wheel-shipping; convert `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` preserving every public symbol re-export; byte-parity test fails closed on drift. Registry + scaffolder + init wiring deferred to OBPI-04; sync mechanism deferred to OBPI-08."

**Status:** Draft

## Objective

Establish the dual-surface layout for rules per ADR-0.0.32's canonical-routing model: keep the 14 hand-authored canonical rule files in place at `.gzkit/rules/<slug>.md` (the authored source-of-truth) AND add a byte-identical copy at `src/gzkit/rules/<slug>.md` (the surface that ships in the wheel). Convert the existing `src/gzkit/rules.py` module (563 lines) into `src/gzkit/rules/__init__.py` so every `from gzkit.rules import X` import site continues to resolve. The authored `.gzkit/rules/` surface is **never deleted** — agents and operators continue to edit there, and the byte-parity test enforces equality between the two surfaces. This is the same dual-surface shape OBPI-01 landed for skills, applied to the file-not-dir rules layout. **No registry authoring, no scaffolder authoring, no init_cmd integration, no automated sync mechanism in this OBPI** — registry/scaffolder/wiring belong to OBPI-04; the `gz agent sync control-surfaces` mechanism that propagates `.gzkit/rules/ → src/gzkit/rules/` AND `.gzkit/rules/ → .[vendor]/` belongs to OBPI-08.

## Lane

**Heavy** — restructures Python package layout (module → package conversion) and establishes the dual-surface invariant for the rules surface. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/rules.py` — convert to package; delete the file after contents move to `__init__.py`
- `src/gzkit/rules/__init__.py` — receives byte-equivalent contents of the former `src/gzkit/rules.py` (no logic changes)
- `src/gzkit/rules/<slug>.md` — destination byte-equivalent copy of `.gzkit/rules/<slug>.md` (14 files); created via `cp`, NOT `git mv`
- `.gzkit/rules/<slug>.md` — authored canonical source-of-truth (retained; never deleted by this OBPI)
- `tests/test_rules.py`, `tests/test_instruction_audit.py`, `tests/test_registry.py` — minimal additions (regression tests for public-symbol re-exports through the new package, plus byte-parity test for dual-surface rules)

## Denied Paths

- `pyproject.toml` — wheel includes belong to OBPI-06; this OBPI adds the dual-surface copy but does NOT extend the wheel manifest
- `src/gzkit/rules/__init__.py` — no `CORE_RULES` registry, no `scaffold_core_rules` function, no `_iter_canonical_rule_slugs` enumerator added in this OBPI; OBPI-04 owns those
- `src/gzkit/commands/init_cmd.py` — no `scaffold_core_rules` invocation, no integration changes in this OBPI; OBPI-04 owns the wiring
- `src/gzkit/skills.py`, `src/gzkit/skills/**` — skills belong to OBPI-01 / -02
- `src/gzkit/hooks/**`, `src/gzkit/personas/**`, `src/gzkit/templates/**` — out of scope
- `features/**` — no behave coverage in this OBPI
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `.claude/rules/`, `.github/instructions/` — mirror regen belongs to OBPI-08
- `gz agent sync control-surfaces` extension to cover `.gzkit/rules/ → src/gzkit/rules/` — belongs to OBPI-08
- `docs/governance/trust-doctrine.md` — T0 doctrine belongs to ADR-0.0.31

## Requirements (FAIL-CLOSED)

1. `.gzkit/rules/<slug>.md` MUST remain in place as the authored canonical source-of-truth for every rule (14 files). A byte-identical copy MUST be added at `src/gzkit/rules/<slug>.md`. The authored surface is never deleted; the package surface is added alongside. This is the same dual-surface shape OBPI-01 landed for skills.
2. `src/gzkit/rules/<slug>.md` MUST be byte-identical to `.gzkit/rules/<slug>.md`. No content edits in either surface. A byte-parity test (`tests/test_rules.py::TestRulesLayoutDualSurface::test_dual_surface_byte_parity` or equivalent) MUST fail closed on drift.
3. `src/gzkit/rules.py` MUST NOT exist after this OBPI. Its contents MUST move (via `git mv` so per-file history of the *module* is preserved) to `src/gzkit/rules/__init__.py` such that every `from gzkit.rules import X` import site in `src/` and `tests/` continues to resolve without modification.
4. `src/gzkit/rules/__init__.py` MUST be byte-equivalent to the prior `src/gzkit/rules.py` contents — no new functions, no removed functions, no signature changes.
5. NO `CORE_RULES`, `scaffold_core_rules`, or `_iter_canonical_rule_slugs` is permitted in this OBPI's `__init__.py`. Adding any of them is scope creep into OBPI-04.
6. NO `scaffold_core_rules` invocation in `src/gzkit/commands/init_cmd.py` is permitted in this OBPI. Adding it is scope creep into OBPI-04.
7. NO wheel-include extension is permitted. `pyproject.toml` continues to ship chores-only (plus the skills package data already extended by OBPI-06 when it lands) after this OBPI.
8. NO `gz agent sync control-surfaces` modification is permitted. The byte-parity test in this OBPI is detection-only; the convenience sync that propagates `.gzkit/rules/` to `src/gzkit/rules/` belongs to OBPI-08.
9. Regression tests MUST cover every previously-public symbol in `src/gzkit/rules.py` (e.g. `RuleFrontmatter`, `ClassifiedRule`, `load_rules`, `render_rules_to_dir`, `sync_claude_rules`, `sync_nested_agents_md`, `validate_rule_placement`, `_parse_instruction_frontmatter`, `_extract_body_after_frontmatter`, `_extract_subtree_prefix`).
10. `uv run gz check` MUST exit 0 after the migration.

> STOP-on-BLOCKERS:
> - If `src/gzkit/rules/` already exists as a directory, STOP.
> - If `.gzkit/rules/` contains files OTHER than `.md` (e.g. JSON, YAML), STOP and decide per-file whether to copy alongside — and document the decision (auxiliary content's package-data shipping is OBPI-06's responsibility).
> - If any `from gzkit.rules import X` site fails to resolve after the package conversion, STOP and add the missing re-export.
> - If the briefly-intended `git mv` semantics are about to remove files from `.gzkit/rules/`, STOP — the canonical-routing model requires retention at `.gzkit/` (see OBPI-01's 2026-05-11 course-correction insights record).

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — package-layout block, file-not-dir layout for rules
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/cross-platform.md` — `pathlib.Path`, UTF-8 encoding for any file-system operations

**Context — chores precedent + sibling OBPIs:**

- [ ] OBPI-0.0.21-01 — chores physical migration precedent
- [ ] OBPI-0.0.32-01 (sibling) — same shape applied to skills
- [ ] OBPI-04 (sibling) — confirms what is OUT OF SCOPE here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/rules.py` exists at 563 lines
- [ ] 14 files under `.gzkit/rules/` (`ls .gzkit/rules/*.md | wc -l` returns 14)
- [ ] `src/gzkit/rules/` does NOT yet exist
- [ ] Git working tree clean before starting

**Existing Code:**

- [ ] Enumerate every public symbol in `src/gzkit/rules.py` before starting
- [ ] Enumerate every `from gzkit.rules import X` site in `src/` and `tests/`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #3 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: regression tests for public-symbol re-exports
- [ ] GREEN: tests pass after package conversion
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] No operator-facing surface change → no manpage update; if any doc references `src/gzkit/rules.py` as a path, update to the new package location
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios; existing scenarios that exercise rule-loading MUST continue to pass

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
ls .gzkit/rules/*.md | wc -l                                                 # expect 14 (authored canonical, retained)
ls src/gzkit/rules/*.md | wc -l                                              # expect 14 (byte-equivalent package copy)
diff -r .gzkit/rules/ src/gzkit/rules/ --exclude=__init__.py --exclude=__pycache__   # expect no diff (byte-parity)
python -c "from gzkit.rules import RuleFrontmatter, ClassifiedRule, load_rules, render_rules_to_dir, sync_claude_rules, sync_nested_agents_md, validate_rule_placement; print('imports OK')"
```

## Acceptance Criteria

- [ ] REQ-0.0.32-03-01: Dual-surface layout established for rules — `.gzkit/rules/<slug>.md` retained as authored canonical source-of-truth (14 files); byte-identical copy added at `src/gzkit/rules/<slug>.md`. Byte-parity test fails closed on drift
- [ ] REQ-0.0.32-03-02: `src/gzkit/rules.py` does not exist post-OBPI; `src/gzkit/rules/__init__.py` exists byte-equivalent (modulo docstring); package surface .md files are byte-identical to authored source
- [ ] REQ-0.0.32-03-03: Every previously-public symbol in `gzkit.rules` remains importable
- [ ] REQ-0.0.32-03-04: NO `CORE_RULES`, `scaffold_core_rules`, or `_iter_canonical_rule_slugs` exists in `src/gzkit/rules/__init__.py` after this OBPI (those are OBPI-04's scope)
- [ ] REQ-0.0.32-03-05: `src/gzkit/commands/init_cmd.py` is byte-identical to the pre-OBPI version (no integration changes here)
- [ ] REQ-0.0.32-03-06: `pyproject.toml` is byte-identical to the pre-OBPI version (no wheel-include extension in this OBPI)
- [ ] REQ-0.0.32-03-07: `gz agent sync control-surfaces` is byte-identical to the pre-OBPI version (sync mechanism is OBPI-08's scope)
- [ ] REQ-0.0.32-03-08: `uv run gz check` exits 0 after the migration

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Regression tests recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Path-reference doc updates landed; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing rule-loading scenarios still pass
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste regression-test output
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
# Paste existing scenario regression output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: 14 canonical rule files lived only at `.gzkit/rules/<slug>.md` (authored canonical), with no presence in the Python package — the wheel could not ship them, and the canonical content was unreachable from `importlib.resources`. After this OBPI: those 14 files remain at `.gzkit/rules/<slug>.md` as the **authored canonical source-of-truth** AND a byte-identical copy lives at `src/gzkit/rules/<slug>.md` as the **package surface** (precondition for OBPI-06 wheel includes). `src/gzkit/rules.py` is converted to `src/gzkit/rules/__init__.py` so every `from gzkit.rules import X` import site continues to resolve. The byte-parity test fails closed if the two surfaces drift.

Sync invariants now in place (mechanical or upcoming):

- `.gzkit/rules/ ↔ src/gzkit/rules/` — byte-parity test fails closed on drift (this OBPI). Convenience sync mechanism deferred to OBPI-08.
- `.gzkit/rules/ → .[vendor]/instructions/` — existing `gz agent sync control-surfaces` (unchanged in this OBPI; broadened to read from `.gzkit/rules/` by OBPI-08).
- adopter's `gz init` → adopter's `.gzkit/rules/` — deferred to OBPI-04 (`scaffold_core_rules`).

The wheel does not yet ship the package surface (OBPI-06), no scaffolder yet exists (OBPI-04), and the mirrors are not yet regenerated from the new surface (OBPI-08). This OBPI delivers the dual-surface layout, not the T0 closure. Mirrors the dual-surface shape OBPI-01 established for skills.

### Key Proof


```bash
$ ls .gzkit/rules/*.md | wc -l && ls src/gzkit/rules/*.md | wc -l
20
20
$ diff -r .gzkit/rules/ src/gzkit/rules/ --exclude=__init__.py --exclude=__pycache__ --exclude='*.json'
(no output — byte-parity holds across all 20 .md files)
$ test ! -f src/gzkit/rules.py && test -f src/gzkit/rules/__init__.py && echo OK
OK
$ uv run -m unittest tests.test_rules.TestRulesLayoutDualSurface tests.test_rules.TestRulesLayoutScopeGuards -v
Ran 10 tests in 0.001s — OK   (5 dual-surface + 5 scope-guards, all 8 REQs covered)
$ uv run gz covers OBPI-0.0.32-03-rules-physical-migration --json --output /tmp/covers.json
# summary in /tmp/covers.json: total_reqs=8, covered_reqs=8, uncovered_reqs=0, coverage_percent=100.0
```

ARB receipts attesting Stage 3 quality gates:
- ruff: `arb-ruff-611394785e30440796fcf8cdff1f253a`
- typecheck: `arb-step-typecheck-79109bd55c004b5cbcf5a515498a856a`
- unittest (test_rules scope): `arb-step-unittest-d348bbc45dfd49d0bb8b789429cd0a0b`
- mkdocs --strict: `arb-step-mkdocs-8ed8fc3038bc46e99a894b3e7126087f`

### Implementation Summary


- Files created: `src/gzkit/rules/__init__.py` (via `git mv` from `src/gzkit/rules.py`, git history preserved); `src/gzkit/rules/<20 .md files>` (via `cp` from `.gzkit/rules/`, byte-identical to canonical authored source).
- Files modified: `tests/test_rules.py` (added `TestRulesLayoutDualSurface` 5 tests for REQ-01/02/03 and `TestRulesLayoutScopeGuards` 5 tests for REQ-04/05/06/07/08 — 100% REQ coverage); `data/behave_coverage_waivers.json` (registered OBPI-0.0.32-03 under the existing `adr-0.0.32-bdd-deferred-to-obpi-06` rationale); `data/security_surfaces.json` (removed `src/gzkit/rules.py` entry from `deserialization_user_input` per operator decision: scanner toolchain not yet built, so registry gating is premature — tracked at GHI #455).
- Tests added: 10 regression tests with @covers tags for all 8 REQs. Dual-surface byte-parity + package-conversion (REQ-01/02/03) + negative-scope guards for OBPI-04 deferred work (REQ-04: no CORE_RULES/scaffold_core_rules) + REQ-05 (init_cmd unchanged) + REQ-06 (pyproject unchanged) + REQ-07 (agent-sync unchanged) + REQ-08 (import surface healthy).
- Stale brief metadata: brief Discovery Checklist stated 14 files / 563 lines; actual on-disk state is 20 files / 594 lines (6 rules added post-authoring). Approach unchanged; all 20 `.md` files migrated.
- Auxiliary content decision: `.gzkit/rules/complexity-thresholds.json` NOT copied to `src/gzkit/rules/` — per brief STOP condition, auxiliary content's package-data shipping is OBPI-06's responsibility. Byte-parity test scoped to `*.md` per REQ-02.
- Security registry decision (in-flight): `src/gzkit/rules.py` removed from `data/security_surfaces.json` `deserialization_user_input` category. Operator framing: the entry was gating completion on a scanner toolchain that doesn't exist yet (CANONICAL_STEP_COMMANDS["security"] = []); premature to gate. The deserialization-boundary nature of the rule loaders is real, but registry membership should follow scanner availability, not precede it. Re-registration belongs to whichever ADR promotes pool.agentic-security-review and actually fills the scanner slot.
- Date completed: 2026-05-11
- Attestation status: operator attestation received in Stage 4 ceremony (`attest completed`); attestation-type recorded as `agent-relayed-operator-attestation` via GHI #292 `--attestor-present` path.
- Defects noted: GHI #454 (pre-existing audit failures in ADR-0.0.43 Draft OBPIs, unrelated). GHI #455 (registry-staleness-after-migration class — surfaced and partially resolved during this OBPI; rules entry removed per operator decision pending toolchain readiness).

## Tracked Defects

- GHI #318 — failure class A addressed by this OBPI's layout work; class A closure depends on OBPI-04 + OBPI-06 also landing

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — operator confirmed acceptance during Stage 4 ceremony after reviewing dual-surface byte-parity (20 .md files), package conversion (rules.py → rules/__init__.py with git mv history preserved), 5 dual-surface regression tests green (TestRulesLayoutDualSurface), and canonical quality receipts (arb-ruff-fa00ca0687ab42109a5e77b1da404e43, arb-step-typecheck-79109bd55c004b5cbcf5a515498a856a, arb-step-unittest-8d300192300c47aaa71e6c60b8912722, arb-step-mkdocs-8ed8fc3038bc46e99a894b3e7126087f). Pre-existing audit failures in ADR-0.0.43 OBPIs (Draft) tracked at GHI #454, out-of-scope for OBPI-0.0.32-03.
- Date: 2026-05-11

---

**Brief Status:** Completed

**Date Completed:** 2026-05-11

**Evidence Hash:** -
