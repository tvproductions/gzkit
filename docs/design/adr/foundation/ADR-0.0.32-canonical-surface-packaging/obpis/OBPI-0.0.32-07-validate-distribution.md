---
id: OBPI-0.0.32-07-validate-distribution
parent: ADR-0.0.32-canonical-surface-packaging
item: 7
lane: Heavy
status: Draft
---

# OBPI-0.0.32-07-validate-distribution: gz validate --distribution Scope

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #7 — "Extend `gz validate --surfaces` (or add `--distribution`) with T0 enforcement — verify every canonical surface in manifest is wheel-deliverable from `src/gzkit/`; fail-closed exit 3 on any package-data omission; flip T0 scorecard Promotable→Mechanical."

**Status:** Draft

## Objective

Promote the T0 distribution invariant from advisory doctrine (ADR-0.0.31) to mechanical fail-closed enforcement at the validator surface. Add `gz validate --distribution` (or extend an existing `--surfaces` scope) so that every commit that adds a canonical surface without wheel coverage exits 3 BEFORE the build stage. The static check operates on `pyproject.toml [tool.hatch.build.targets.wheel] include:` + `data/distribution_baseline_manifest.json` + the on-disk canonical-content trees at `src/gzkit/<surface>/` (the wheel-shipping byte-equivalent copies of `.gzkit/<surface>/`) — no actual wheel build required, so the check fits in the standard `gz validate` runtime budget. The validator's source-of-truth for "what should ship in the wheel" is `src/gzkit/<surface>/` (because that is what the wheel literally includes); `.gzkit/<surface>/` byte-parity with `src/gzkit/<surface>/` is separately gated by OBPI-01/03's byte-parity tests and the OBPI-08 sync mechanism. This OBPI is the static counterpart to OBPI-06's behave smoke; together they fail-close T0 from two angles.

## Lane

**Heavy** — adds a new `gz validate` scope, exits with policy-breach code 3 on violation, must be wired into CI. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — add T0 distribution check function
- `src/gzkit/validate.py` (or wherever the `--distribution` / `--surfaces` flag dispatch lives) — register the new scope
- `src/gzkit/cli/parser_validate.py` — register the `--distribution` flag if added as a new scope
- `tests/governance/test_distribution_audit.py` — unit tests for the audit function (every code path: missing include, baseline drift, on-disk-not-included, etc.)
- `docs/user/manpages/gz-validate.md` — document the new scope
- `.gzkit/rules/governance-core.md` (or the appropriate rule file) — register the validator's scope name in the proof-commands list
- `docs/governance/advisory-rules-audit.md` — flip the T0 scorecard entry from Promotable to Mechanical (with this OBPI as the promotion landing point)

## Denied Paths

- `pyproject.toml` — wheel include extension belongs to OBPI-0.0.32-06; this OBPI consumes the include list as input
- `src/gzkit/skills/**`, `src/gzkit/rules/**` — content moves belong to OBPI-0.0.32-01 / -02
- `data/distribution_baseline_manifest.json` — baseline manifest is authored by OBPI-0.0.32-06; this OBPI consumes it as input (loading + parsing only)
- `features/distribution_invariant.feature` — behave smoke belongs to OBPI-0.0.32-06
- `.claude/skills/`, `.github/skills/` — mirror sync belongs to OBPI-0.0.32-08
- `docs/governance/trust-doctrine.md` — T0 doctrine prose belongs to OBPI-0.0.31-01

## Requirements (FAIL-CLOSED)

1. `gz validate --distribution` (or `gz validate --surfaces` extended) MUST exist as a registered scope in the validator's flag list and MUST appear in `gz validate --help` output.
2. The check MUST be a static analysis: load `pyproject.toml [tool.hatch.build.targets.wheel] include:`, load `data/distribution_baseline_manifest.json`, walk on-disk canonical-surface trees (`src/gzkit/skills/`, `src/gzkit/rules/`, `src/gzkit/templates/`, `src/gzkit/hooks/`, `src/gzkit/personas/`), and detect three drift classes:
   (a) ON_DISK_NOT_INCLUDED — file exists under a canonical-surface tree but is NOT covered by any include glob;
   (b) BASELINE_NOT_ON_DISK — baseline manifest names a file that does not exist on disk;
   (c) ON_DISK_NOT_BASELINE — file exists on disk and is in the include but is NOT in the baseline manifest.
3. ANY drift in any class MUST exit 3 with a structured per-violation report. NO drift MUST exit 0.
4. The check MUST NOT build a wheel (no subprocess calls to `uv build` or `hatch build`); the static check is the fast complement to OBPI-0.0.32-04's full build smoke.
5. Per-violation report MUST name: the file path, the drift class, the include glob (if any) that covers it, and the resolution hint (e.g. "extend include block in pyproject.toml" / "remove from baseline manifest" / "add to baseline manifest").
6. Unit tests MUST cover every drift class: (a) missing include detected; (b) phantom baseline entry detected; (c) untracked-but-included file detected; (d) clean state exits 0; (e) malformed `pyproject.toml` produces a clear error (exit 2, not 3 — system error vs policy breach).
7. The validator MUST surface in `gz validate --help` and MUST be runnable via `uv run gz validate --distribution` (operator surface) and importable via the `_run_validations` dispatcher (CI surface).
8. `docs/user/manpages/gz-validate.md` MUST document the new scope, the three drift classes, the exit codes (0 / 2 / 3), and a worked recovery example.
9. The advisory-rules-audit scorecard entry for T0 MUST flip from Promotable to Mechanical at this OBPI's landing time, with the receipt receipt-id pattern recorded.
10. `uv run gz check` MUST exit 0 with the new scope registered (the check itself runs as part of `gz validate`, which `gz check` invokes).

> STOP-on-BLOCKERS:
> - If OBPI-0.0.32-04 has not landed (no `data/distribution_baseline_manifest.json`), STOP — the validator has nothing to compare against.
> - If `pyproject.toml [tool.hatch.build.targets.wheel] include:` parsing requires a TOML library not in the standard library (Python 3.11+ has `tomllib` stdlib, so this should not be a problem) — verify before authoring.
> - If the on-disk walk would touch `__pycache__` or other non-canonical content, STOP and define the canonical-surface walk filter explicitly (skip dunder, skip non-shipped extensions).

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Intent — names the two-angle T0 fail-closure (smoke + static)
- [ ] Parent ADR § Decision — the validate-distribution scope item
- [ ] ADR-0.0.31 § Decision — Mechanical-enforcement contract item #1 ("A T0 audit MUST detect missing package data without depending on downstream installation evidence")
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/cli.md` § Exit codes — exit 3 = policy breach (this is the canonical exit for T0 drift)
- [ ] `.gzkit/rules/governance-core.md` § Proof commands — the new validator joins that list
- [ ] `docs/governance/advisory-rules-audit.md` — Promotable → Mechanical promotion procedure

**Context — chores precedent + sibling OBPIs:**

- [ ] `gz validate --chores-layout` — analogous static layout check (`src/gzkit/governance/trust_audits.py` _CHORES_LAYOUT_*); the implementation pattern transfers
- [ ] `gz validate --utf8-prefix` — another static check with three drift classes; pattern transfers
- [ ] OBPI-0.0.32-06 — produces the baseline manifest this OBPI consumes; produces the wheel includes this OBPI verifies

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/governance/trust_audits.py` exists and contains existing `--surfaces` / `--chores-layout` / `--utf8-prefix` checks (the patterns this OBPI extends)
- [ ] OBPI-0.0.32-06 baseline manifest exists at `data/distribution_baseline_manifest.json`
- [ ] OBPI-0.0.32-01 + OBPI-0.0.32-02 wheel includes are landed (so the include block parses cleanly)
- [ ] Python 3.11+ stdlib `tomllib` is available (sanity check via `python -c "import tomllib"`)

**Existing Code:**

- [ ] Read at least two existing trust_audits checks end-to-end before authoring (the chores-layout one is closest in shape)
- [ ] Read `src/gzkit/cli/parser_validate.py` to understand how new `--scope` flags get registered
- [ ] Read `docs/user/manpages/gz-validate.md` to understand the manpage shape; the new scope joins the table

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #5 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for each drift class fail before the audit function is authored
- [ ] GREEN: tests pass after the function and scope registration land
- [ ] Coverage above 40% floor

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-validate.md` documents the new scope
- [ ] `docs/governance/advisory-rules-audit.md` T0 entry flipped from Promotable to Mechanical
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] At least one scenario in `features/validate.feature` (or equivalent) exercises `gz validate --distribution` against a fixture with each drift class; tagged `@REQ-0.0.32-07-NN`

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

uv run gz validate --help | grep -- --distribution
uv run gz validate --distribution                                  # expect exit 0 in clean state

# Drift simulation (run in scratch worktree)
git clean -fd src/gzkit/skills/test-untracked/                      # add an untracked canonical file
uv run gz validate --distribution                                   # expect exit 3 with ON_DISK_NOT_INCLUDED report

uv run -m behave features/validate.feature --tags=@REQ-0.0.32-07-01
```

## Acceptance Criteria

- [ ] REQ-0.0.32-07-01: `gz validate --distribution` (or `--surfaces` extended) exists as a documented scope and appears in `gz validate --help`
- [ ] REQ-0.0.32-07-02: ON_DISK_NOT_INCLUDED drift class detected; per-violation report names file, glob context, and resolution hint
- [ ] REQ-0.0.32-07-03: BASELINE_NOT_ON_DISK drift class detected; per-violation report names manifest entry and resolution hint
- [ ] REQ-0.0.32-07-04: ON_DISK_NOT_BASELINE drift class detected; per-violation report names file and resolution hint
- [ ] REQ-0.0.32-07-05: Clean state exits 0; any drift exits 3
- [ ] REQ-0.0.32-07-06: Malformed `pyproject.toml` exits 2 (system error), not 3 (policy breach)
- [ ] REQ-0.0.32-07-07: Static-only — no `uv build` / `hatch build` subprocess invocations
- [ ] REQ-0.0.32-07-08: `docs/user/manpages/gz-validate.md` documents the scope, drift classes, exit codes, recovery example
- [ ] REQ-0.0.32-07-09: T0 scorecard entry flipped Promotable → Mechanical in `docs/governance/advisory-rules-audit.md`
- [ ] REQ-0.0.32-07-10: `uv run gz check` exits 0 with the new scope registered
- [ ] REQ-0.0.32-07-11: Behave scenario `@REQ-0.0.32-07-01` exercises at least one drift class against a fixture and passes

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage + scorecard updated; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Drift-class scenario passes
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output covering each drift class
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
# Paste behave scenario output for @REQ-0.0.32-07-01
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: T0 enforcement depended on the OBPI-0.0.32-04 build-install-init smoke, which is necessary but slow (full wheel build). After this OBPI: `gz validate --distribution` fails-closed in seconds against the static surfaces (pyproject.toml + baseline manifest + on-disk trees), so a commit that adds a canonical surface without wheel coverage breaks the precommit / `gz check` pass instantly. The smoke remains the source-of-truth for end-to-end install behavior; the validator is the fast guardrail.

### Key Proof

```bash
uv run gz validate --distribution
# Expected: exit 0 in clean state; exit 3 with structured per-violation report on any drift class
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — failure-class enforcement gate landed by this OBPI

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
