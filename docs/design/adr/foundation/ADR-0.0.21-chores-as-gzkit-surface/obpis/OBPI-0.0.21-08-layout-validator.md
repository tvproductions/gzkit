---
id: OBPI-0.0.21-08-layout-validator
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 8
lane: Heavy
status: Completed
---

# OBPI-0.0.21-08-layout-validator: Layout Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #8 — Layout validator: `gz validate --chores-layout` fail-closing (exit 3) on any `CHORE.md` or `acceptance.json` outside `src/gzkit/chores/` or `.gzkit/chores/`.

**Status:** Draft

## Objective

Add a `--chores-layout` scope to `gz validate` that walks the tree, flags any `CHORE.md` or `acceptance.json` file located outside the two canonical roots (`src/gzkit/chores/` in this repo, `.gzkit/chores/` in consumer projects), and exits 3 on any unwaived violation — preventing future authoring drift that would re-create the `ops/chores/` layout this ADR exists to close.

## Lane

**Heavy** — adds a new CLI surface (new `--chores-layout` scope on `gz validate`) and a new failure exit path. External contract per `.gzkit/rules/cli.md`.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — new `audit_chores_layout(project_root: Path) -> list[ValidationError]` function following the pattern at `audit_utf8_prefix` (same file, line 424)
- `src/gzkit/commands/validate_cmd.py` — wire the new scope into the registry at the existing extension points (pattern from `utf8_prefix` at lines 280, 319, 386, 555, 639)
- `src/gzkit/cli/parser_maintenance.py` — add the `--chores-layout` flag alongside `--utf8-prefix` (line 385) and `--brief-headings` (line 450)
- `tests/governance/test_trust_audits.py` (or `tests/test_trust_audits.py`) — REQ-derived tests with fixture tempdirs
- `data/chores_layout_waivers.json` — optional waivers file if the validator needs to exempt specific paths (e.g., ADR evidence files that reference the old layout)

## Denied Paths

- `src/gzkit/commands/chores.py`, `chores_exec.py` — resolver is OBPI-04
- `src/gzkit/chores.py` — scaffolder is OBPI-05
- `src/gzkit/chores/**`, `pyproject.toml`, `features/**`, `docs/**`, `.gzkit/rules/**` — unrelated surfaces

## Requirements (FAIL-CLOSED)

1. A new function `audit_chores_layout(project_root: Path) -> list[ValidationError]` MUST exist in `src/gzkit/governance/trust_audits.py`, matching the signature and return type of sibling `audit_utf8_prefix` at line 424.
2. The audit MUST walk the project tree and return a `ValidationError` for every `CHORE.md` file and every `acceptance.json` file whose path does NOT start with `src/gzkit/chores/` (canonical in the gzkit repo) OR `{config.paths.chores}/` (project-scaffolded, default `.gzkit/chores/`).
3. The audit MUST ignore paths under `.git/`, `__pycache__/`, `.venv/`, `dist/`, `build/`, `node_modules/`, and any path whose any-segment starts with `.` (dotfile-hidden) per the same exclusions used in `audit_utf8_prefix`.
4. The audit MUST support a waiver file at `data/chores_layout_waivers.json` — a JSON list of path strings exempted from the check. Waivers are explicit and reviewable, matching the `_UTF8_PIPE_WAIVERS` pattern per trust-doctrine T2.
5. The CLI MUST expose `--chores-layout` on `gz validate` that runs the audit and exits 3 on any unwaived violation. Exit 0 on success, exit 2 on IO error (matching sibling scopes).
6. Every `ValidationError` raised MUST carry `type="chores_layout"` and a message naming the offending path and the canonical roots — so operators see exactly why the audit fired.
7. `audit_chores_layout` MUST be added to the `__all__` export in `trust_audits.py` (per the pattern at line 1524).
8. `gz validate` (no-arg default) MUST NOT invoke this scope automatically unless all scopes are requested; operators opt in via `--chores-layout` or `--all`.
9. Tests MUST cover: (a) clean tree passes; (b) a planted `CHORE.md` at `ops/chores/test-slug/CHORE.md` fails with exit 3; (c) a planted file inside `src/gzkit/chores/` passes; (d) a planted file inside `.gzkit/chores/` passes; (e) a waived path passes; (f) the dotfile/`.git/` exclusions work.
10. The validator MUST run in <2 seconds on a typical tree; walking the full repo file list is fine (the pattern has no subprocess boundary).

> STOP-on-BLOCKERS:
> - If OBPI-01 has not landed, `src/gzkit/chores/` may not yet exist and the validator cannot be tested in this repo realistically. Block until OBPI-01 lands.
> - If OBPI-02 (`paths.chores`) has not landed, the canonical "project-scaffolded" root has no config source — hardcoding `.gzkit/chores` is acceptable as a fallback but the config key MUST be consulted when available.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR ADR-0.0.21 § Decision #9
- [ ] `.gzkit/rules/cli.md` — exit code doctrine (3 for policy breach)
- [ ] `docs/governance/advisory-rules-audit.md` + `docs/governance/trust-doctrine.md` — new validator scorecard entry requirement

**Context:**

- [ ] Existing audits in `src/gzkit/governance/trust_audits.py` — `audit_utf8_prefix`, `audit_brief_headings` shapes
- [ ] Existing waivers in the repo (e.g. `_UTF8_PIPE_WAIVERS`) — waiver storage pattern

**Prerequisites:**

- [ ] OBPI-01 (layout migration) Completed so `src/gzkit/chores/` is a valid canonical root
- [ ] OBPI-02 (`paths.chores`) Completed so the config-driven second root is resolvable

**Existing Code:**

- [ ] Read `src/gzkit/governance/trust_audits.py:424-540` — `audit_utf8_prefix` as exemplar
- [ ] Read `src/gzkit/commands/validate_cmd.py:280, 319, 386, 555, 639` — how a scope wires in
- [ ] Read `src/gzkit/cli/parser_maintenance.py:380-490` — how flags register

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] RED: `test_audit_chores_layout_flags_stray_chore_md` — plant `tmp/ops/chores/x/CHORE.md`, call `audit_chores_layout(tmp)`, assert one `ValidationError` returned with `type="chores_layout"`.
- [ ] GREEN: implement walker.
- [ ] RED: `test_audit_chores_layout_accepts_canonical_root` — plant `tmp/src/gzkit/chores/x/CHORE.md`, assert empty.
- [ ] GREEN: passes.
- [ ] RED: `test_audit_chores_layout_accepts_project_root` — plant `tmp/.gzkit/chores/x/CHORE.md`, assert empty.
- [ ] GREEN: passes.
- [ ] RED: `test_audit_chores_layout_honors_waivers` — plant `tmp/legacy/CHORE.md`, add it to waivers JSON, assert empty.
- [ ] GREEN: implement waiver loading.
- [ ] RED: `test_cli_validate_chores_layout_exits_3_on_drift` — plant stray, invoke `gz validate --chores-layout`, assert exit code 3.
- [ ] GREEN: wire parser + dispatcher.
- [ ] `uv run gz test` green.

### Code Quality
- [ ] `uv run gz lint`, `uv run gz typecheck`

### Gate 3 (Docs) — Heavy
- [ ] Manpage update (lives in OBPI-06): ensure `gz validate --chores-layout` is documented. This OBPI coordinates with OBPI-06 but does not edit docs directly.
- [ ] `uv run mkdocs build --strict`

### Gate 4 (BDD) — Heavy
- [ ] Deferred to OBPI-07 (one scenario in the distribution feature MAY exercise the validator; additional BDD not required for this OBPI alone).

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation

## Verification

```bash
# Audit runs on current tree
uv run gz validate --chores-layout 2>&1 | tail -10

# Fail-closed smoke: plant a stray CHORE.md and confirm exit 3
mkdir -p /tmp/layout-drift/ops/chores/bogus
echo "# bogus" > /tmp/layout-drift/ops/chores/bogus/CHORE.md
cd /tmp/layout-drift && uv run gz validate --chores-layout; echo "exit: $?"
# expect exit 3

# Unit tests
uv run -m unittest tests.governance.test_trust_audits -v 2>&1 | grep -E "chores_layout|OK|FAIL"
```

## Acceptance Criteria

- [ ] REQ-0.0.21-08-01: `audit_chores_layout(project_root)` exists in `src/gzkit/governance/trust_audits.py` with signature `(Path) -> list[ValidationError]` and is exported via `__all__`.
- [ ] REQ-0.0.21-08-02: The audit returns zero violations when all `CHORE.md` and `acceptance.json` files live under `src/gzkit/chores/` or `.gzkit/chores/` (or the configured `paths.chores`).
- [ ] REQ-0.0.21-08-03: The audit returns one `ValidationError(type="chores_layout")` per stray `CHORE.md` or `acceptance.json`; each error names the offending path.
- [ ] REQ-0.0.21-08-04: `uv run gz validate --chores-layout` exits 3 on any unwaived violation, exit 0 on clean tree.
- [ ] REQ-0.0.21-08-05: The waiver file at `data/chores_layout_waivers.json` exempts explicitly-listed paths; waiver drift across ADRs requires an explicit add rather than a silent skip.
- [ ] REQ-0.0.21-08-06: Dotfile-hidden paths, `.git/`, `__pycache__/`, `.venv/`, `dist/`, `build/`, `node_modules/` are skipped during the walk.
- [ ] REQ-0.0.21-08-07: The audit completes in <2s on a typical gzkit tree.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** 5 REQ-derived TDD cycles with planted fixtures
- [ ] **Code Quality:** lint + typecheck green
- [ ] **Gate 3:** docs build green; OBPI-06 documents the flag
- [ ] **Gate 5:** human attestation
- [ ] **Value Narrative:** before — layout drift (re-emergence of `ops/chores/`) would be silent; after — any stray `CHORE.md` outside canonical roots fails CI.
- [ ] **Key Proof:** plant a stray `CHORE.md`, run `gz validate --chores-layout`, observe exit 3.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
# paste test output + fixture observations
```

### Code Quality
```text
# paste lint + typecheck output
```

### Gate 3 (Docs)
```text
# paste mkdocs output
```

### Gate 5 (Human)
```text
# attestation text
```

### Value Narrative
Before: re-emergence of `ops/chores/` in a future PR would pass review because no automated check fired. After: `gz validate --chores-layout` fails the PR with exit 3 and a message naming the stray path.

### Key Proof

Fail-closed smoke (exit 3 confirmed):

```bash
$ mkdir -p /tmp/layout-drift/ops/chores/bogus
$ echo "# bogus" > /tmp/layout-drift/ops/chores/bogus/CHORE.md
$ (cd /tmp/layout-drift && uv run --project /Users/jeff/Documents/Code/gzkit gz validate --chores-layout); echo "exit:$?"
Validated: chores_layout

Validation failed with 1 error(s):

   ->  ops/chores/bogus/CHORE.md
    stray CHORE.md outside canonical chores roots (src/gzkit/chores/, .gzkit/chores/).
    ADR-0.0.21 Decision #9 forbids ad-hoc chore layouts.

exit:3
```

Clean tree (exit 0):

```bash
$ uv run gz validate --chores-layout
Validated: chores_layout
All validations passed (1 scopes).
exit:0
```

Quality receipts (ARB-wrapped):
- arb-ruff-5a35e6c5534240aba9bd7ed715a276b1 (lint)
- arb-step-typecheck-5ba92ba1c17347f5a95436b9148e6eb0 (typecheck)
- arb-step-unittest-234fa6acd5364a54b66d8c07a5d47f68 (10/10 tests, 0.224s)
- arb-step-mkdocs-7cf595948d254211a3d25c9b81dafd63 (docs build, 2.19s)

REQ -> @covers parity: 7/7 (100%) via `uv run gz covers OBPI-0.0.21-08 --json`.

### Implementation Summary

- Files created: tests/governance/test_audit_chores_layout.py (10 REQ-derived tests across 5 fixture classes), data/chores_layout_waivers.json (empty future-waiver scaffold)
- Files modified: src/gzkit/governance/trust_audits.py (+86 lines: audit_chores_layout, _load_chores_layout_waivers, __all__ export), src/gzkit/commands/validate_cmd.py (+18 lines: 5-surface scope wiring + _POLICY_BREACH_ERROR_TYPES routing chores_layout drift to exit 3 per REQ-08-04), src/gzkit/cli/parser_maintenance.py (+7 lines: --chores-layout flag)
- Tests added: 10 (StrayLayoutFlaggedTests x2, CanonicalRootsAcceptedTests x3, WaiversAndExclusionsTests x2, PerformanceBudgetTests x1, CliExitCodeTests x2)
- @covers parity: 7/7 REQs covered (100%) via gz covers OBPI-0.0.21-08
- Date completed: 2026-04-27
- Attestation status: agent-relayed-operator-attestation (operator attested "attest completed" in Stage 4)
- Defects noted: GHI #347 (STATUS_VOCAB_MAPPING missing 'Withdrawn') in-flight direct-fix bundled into Stage 5 commit per AGENTS.md Defect-fix routing

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy + Foundation OBPI-0.0.21-08 lands the gz validate --chores-layout fail-closed mechanical backstop ADR-0.0.21 Decision #9 mandates: walker (audit_chores_layout) accepts the two canonical roots (src/gzkit/chores/ canonical-shipped + paths.chores project-overlay default .gzkit/chores/) and rejects any other CHORE.md/acceptance.json with type=chores_layout, exit 3 routed via new _POLICY_BREACH_ERROR_TYPES taxonomy honoring REQ-08-04. 7/7 REQs covered (gz covers OBPI-0.0.21-08), 10/10 tests green (arb-step-unittest-234fa6acd5364a54b66d8c07a5d47f68), lint+typecheck+mkdocs clean (arb-ruff-5a35e6c5534240aba9bd7ed715a276b1; arb-step-typecheck-5ba92ba1c17347f5a95436b9148e6eb0; arb-step-mkdocs-7cf595948d254211a3d25c9b81dafd63). Two-root design intentionally preserved (operator surveyed wheel-distribution architecture; ADR-0.0.31 distribution-invariant-doctrine + ADR-0.0.32 canonical-surface-packaging confirm chores precedent is the model skills/rules/personas should follow, not collapse). In-flight defect GHI #347 (STATUS_VOCAB_MAPPING missing Withdrawn term) directly fixed in same Stage 5 to unblock precomplete; bundled in commit per AGENTS.md § Defect-fix routing thresholds.
- Date: 2026-04-27

---

**Brief Status:** Completed

**Date Completed:** 2026-04-27

**Evidence Hash:** -
