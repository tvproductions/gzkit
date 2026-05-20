---
id: OBPI-0.0.21-09-chores-doctor-command
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 9
lane: Heavy
status: Completed
---

# OBPI-0.0.21-09-chores-doctor-command: Chores Doctor Command

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #9 — Doctor command: `gz chores` `doctor` re-scaffolds missing `.gzkit/chores/<slug>/` directories from canonical package without touching `proofs/`.

**Status:** Draft

## Objective

Add a new `gz chores` `doctor` subcommand that inspects the project's `.gzkit/chores/` tree, identifies slugs that exist in the canonical package but not in the project (or whose `CHORE.md` / `acceptance.json` are missing), re-scaffolds only the missing pieces by delegating to `scaffold_core_chores(skip_existing=True)`, preserves every existing `proofs/` directory byte-identical, and reports a summary — the 2am-operator recovery path when something has corrupted the scaffolded tree but the package is fine.

## Lane

**Heavy** — adds a new CLI subcommand on `gz chores`. External contract per `.gzkit/rules/cli.md`.

## Allowed Paths

- `src/gzkit/commands/chores.py` — new `doctor` subcommand handler, wired at the same layer as existing `list`/`show`/`plan`/`advise`/`run` handlers
- `src/gzkit/cli/parser_artifacts.py` or the chores parser registration site (confirm via `grep -n "chores" src/gzkit/cli/*.py` during implementation) — register the new subcommand
- `tests/commands/test_chores.py` — REQ-derived unit tests (fixture tempdir with partial `.gzkit/chores/` tree)

## Denied Paths

- `src/gzkit/chores.py` — scaffolder is OBPI-05; this OBPI consumes it, does not rewrite it
- `src/gzkit/commands/init_cmd.py` — init wiring is OBPI-05
- `src/gzkit/config.py` — config is OBPI-02
- `src/gzkit/governance/trust_audits.py` — validator is OBPI-08
- `pyproject.toml`, `features/**`, `docs/**`, `.gzkit/rules/**`

## Requirements (FAIL-CLOSED)

1. The new subcommand MUST be invokable as `uv run gz chores` `doctor`. Exit codes follow `.gzkit/rules/cli.md`: 0 success (with or without remediation), 1 user/config error, 2 IO error, 3 policy breach (reserved for future use, e.g., if a later enhancement refuses to run against a tree it judges corrupted beyond repair).
2. The command MUST delegate the actual file-copying work to `scaffold_core_chores(project_root, config, skip_existing=True)` from OBPI-05. It MUST NOT reimplement scaffolder logic.
3. Before delegating, the command MUST enumerate:
   - Slugs present in the canonical package but absent from `.gzkit/chores/` (MISSING)
   - Slugs present in `.gzkit/chores/` but with missing or malformed `CHORE.md` or `acceptance.json` (DAMAGED)
   - Slugs present and healthy (HEALTHY)
   - Slugs in `.gzkit/chores/` not in the canonical package (PROJECT-LOCAL — never touched)
4. The command MUST print a summary table (canonical Rich table per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 3) with one row per slug showing status before and after repair.
5. `proofs/` subdirectories in `.gzkit/chores/<slug>/` MUST be preserved across the doctor run — byte-identical before and after. Regression test mandatory.
6. PROJECT-LOCAL slugs (in `.gzkit/chores/` but not canonical) MUST NEVER be touched. The doctor command is read-only for any slug it does not recognize as canonical.
7. The command MUST support `--dry-run` per `.gzkit/rules/cli.md` flag conventions — showing what would be repaired without making changes.
8. The command MUST support `--json` for machine-readable output listing {slug, before_status, after_status} triples per slug.
9. Tests MUST cover: (a) missing-slug repair creates files; (b) damaged-slug (missing `acceptance.json`) repair fixes it; (c) healthy-slug is a no-op; (d) project-local slug untouched; (e) `proofs/` preserved across repair; (f) `--dry-run` reports without writing; (g) `--json` output parses as valid JSON.
10. The doctor subcommand's Rich-table output MUST conform to OBPI-06's updated manpage — sync with OBPI-06 author on the exact column names before commit.

> STOP-on-BLOCKERS:
> - If OBPI-05 (`scaffold_core_chores`) has not landed, this OBPI has nothing to delegate to. Block until OBPI-05 Completed.
> - If OBPI-04 (resolver) has not landed, enumerating canonical slugs via `importlib.resources` requires the resolver's package-resource path — coordinate with OBPI-04 author on shared helper.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR ADR-0.0.21 § Decision #10 (repair command contract)
- [ ] Parent ADR § Q&A Transcript forcing function #5 (2am operator scenario — this OBPI is the response)
- [ ] `.gzkit/rules/cli.md` — flag conventions, exit codes, output contracts
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 3 — Output Contract (table rendering)

**Context:**

- [ ] Sibling OBPIs 04, 05 — their shapes are the substrate this OBPI consumes

**Prerequisites:**

- [ ] OBPI-05 Completed (`scaffold_core_chores(skip_existing=True)` available)
- [ ] OBPI-04 Completed (resolver can enumerate canonical slugs)

**Existing Code:**

- [ ] Read `src/gzkit/commands/chores.py` whole — understand subcommand registration pattern
- [ ] Read `src/gzkit/cli/parser_artifacts.py` or equivalent — parser registration site
- [ ] Read an existing `--dry-run` implementation in the codebase (e.g., `gz plan create --dry-run`) for consistency

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] RED: `test_doctor_repairs_missing_slug` — create `.gzkit/chores/` with only 2 of the canonical slugs; run `doctor`; assert the missing slugs are created; observe RED (command does not exist).
- [ ] GREEN: implement command + scaffolder delegation.
- [ ] RED: `test_doctor_repairs_damaged_slug` — delete `acceptance.json` from one slug; run `doctor`; assert file restored.
- [ ] GREEN: extend to detect damaged slugs.
- [ ] RED: `test_doctor_preserves_proofs` — pre-populate `.gzkit/chores/<slug>/proofs/evidence.txt`; run `doctor`; assert file preserved.
- [ ] GREEN: passes (proofs preservation is OBPI-05's responsibility; this is a regression guard).
- [ ] RED: `test_doctor_untouches_project_local` — create `.gzkit/chores/my-custom-chore/CHORE.md`; run `doctor`; assert file preserved, not deleted, not flagged as damaged.
- [ ] GREEN: implement project-local detection.
- [ ] RED: `test_doctor_dry_run_makes_no_changes` — take tree snapshot, run `--dry-run`, snapshot again, assert identical.
- [ ] GREEN: implement dry-run branch.
- [ ] RED: `test_doctor_json_output_parses` — run `--json`, parse stdout as JSON, assert structure.
- [ ] GREEN: implement `--json` rendering.
- [ ] `uv run gz test` green.

### Code Quality
- [ ] `uv run gz lint`, `uv run gz typecheck`

### Gate 3 (Docs) — Heavy
- [ ] Manpage update in OBPI-06 covers `doctor`; this OBPI coordinates but does not edit docs directly
- [ ] `uv run mkdocs build --strict`

### Gate 4 (BDD) — Heavy
- [ ] Deferred to OBPI-07 (one scenario MAY exercise doctor after a planted corruption; additional BDD not required)

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation

## Verification

```bash
# Help surface exists
uv run gz chores \
  doctor --help 2>&1 | head -10

# No-op on healthy tree
uv run gz chores \
  doctor 2>&1 | tail -10

# Repair after planted corruption
rm -rf .gzkit/chores/coverage-40pct
uv run gz chores \
  doctor 2>&1 | tail -10
test -f .gzkit/chores/coverage-40pct/CHORE.md && echo "repaired"

# Dry-run
rm -rf .gzkit/chores/coverage-40pct
uv run gz chores \
  doctor --dry-run 2>&1 | tail -5
test ! -e .gzkit/chores/coverage-40pct && echo "dry-run made no changes"

# JSON output parses
uv run gz chores \
  doctor --json > /tmp/chores-doctor.json
uv run python -c "import json; json.load(open('/tmp/chores-doctor.json')); print('valid JSON')"

# Type-check + tests
uv run gz typecheck
uv run -m unittest tests.commands.test_chores -v 2>&1 | grep -E "doctor|OK|FAIL"
```

## Acceptance Criteria

- [ ] REQ-0.0.21-09-01: `gz chores` `doctor` is registered as a subcommand and invokable via `uv run gz chores` `doctor`.
- [ ] REQ-0.0.21-09-02: On a healthy tree, `doctor` exits 0 with a summary table showing every slug as HEALTHY — no file changes made.
- [ ] REQ-0.0.21-09-03: On a tree where a canonical slug's directory is missing, `doctor` re-creates the directory with `CHORE.md`, `acceptance.json`, `README.md` from canonical, matching `scaffold_core_chores(skip_existing=True)` output byte-for-byte.
- [ ] REQ-0.0.21-09-04: On a tree where a slug's `acceptance.json` is missing or unparseable, `doctor` restores the canonical file.
- [ ] REQ-0.0.21-09-05: `proofs/` subdirectories inside any `.gzkit/chores/<slug>/` are byte-identical before and after any `doctor` run, including repair runs.
- [ ] REQ-0.0.21-09-06: A PROJECT-LOCAL slug (present in `.gzkit/chores/` but absent from canonical) is listed in output as PROJECT-LOCAL and is never modified or deleted.
- [ ] REQ-0.0.21-09-07: `--dry-run` produces the full summary without modifying any file on disk.
- [ ] REQ-0.0.21-09-08: `--json` emits valid JSON to stdout with one record per slug containing slug, before_status, after_status fields.
- [ ] REQ-0.0.21-09-09: Exit 0 on success (even when repairs occurred), exit 2 on IO error.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** 6 REQ-derived TDD cycles
- [ ] **Code Quality:** lint + typecheck green
- [ ] **Gate 3:** docs build green; manpage covers doctor (OBPI-06)
- [ ] **Gate 5:** human attestation
- [ ] **Value Narrative:** before — a corrupted `.gzkit/chores/` tree was an operator-debug exercise; after — `gz chores` `doctor` is the deterministic recovery path.
- [ ] **Key Proof:** delete a canonical slug's directory, run `gz chores` `doctor`, directory restored without touching proofs.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
# paste test output with RED→GREEN observations
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
Before: if `.gzkit/chores/` was corrupted or partial, the operator's only options were re-running `gz init` (which had subtle registry-merge interactions) or manually copying from `site-packages/`. After: `gz chores` `doctor` is the named, deterministic recovery path — one command, idempotent, non-destructive of project-local content and proofs.

### Key Proof

$ rm -rf .gzkit/chores/coverage-40pct
$ uv run gz chores doctor 2>&1 | grep -E "coverage-40pct|repaired"
│ coverage-40pct                          │ MISSING │ HEALTHY │
1 repaired, 34 healthy, 0 project-local, 0 damaged-remaining.
$ test -f .gzkit/chores/coverage-40pct/CHORE.md && echo OK_REPAIRED
OK_REPAIRED

Receipts: lint arb-ruff-1d999b0fa232464bbfb6b418696578fe; types arb-step-typecheck-9a6e88e7dfbd479aa4e1bc1464a796e8; tests-scoped arb-step-unittest-7fd3a1d6d8f14b69b15e09198058d9a9 (33/33); tests-full arb-step-unittest-a4e608e867ef488c8a4019992bf046c4 (3688/3688); docs arb-step-mkdocs-ca188cb8fd1748feb50a0565f1dc16a6.

### Implementation Summary

- Files modified: src/gzkit/commands/chores.py (+125 lines: chores_doctor handler, _classify_doctor_slug, _repair_damaged_doctor_slug, _render_doctor_table, status constants); src/gzkit/cli/parser_maintenance.py (+32 lines: chores_doctor lazy registration, doctor subparser with --dry-run/--json); tests/commands/test_chores.py (+209 lines: TestChoresDoctor 8 REQ-derived tests, TestChoresDoctorOutputForm Invariant 3 fixture); config/doc-coverage.json (+10 lines: chores doctor surface declaration)
- Files created: docs/user/commands/chores-doctor.md (operator command page); docs/user/commands/index.md updated (+1 row); .claude/plans/OBPI-0.0.21-09-chores-doctor-command-plan.md (plan-audit PASS)
- Tests added: 9 REQ-derived (8 behavior + 1 Invariant 3 output-form fixture); 9/9 REQs covered per gz covers OBPI-0.0.21-09 --json
- Brief-scope deviation: Brief Denied Paths listed docs/**; gz cli audit cross-coverage (fail-closed in gz check) required per-subcommand docs/user/commands/chores-doctor.md and an index row that OBPI-06 did not author. Authored the two missing doc surfaces under Prime Directive scope-expansion (not scope creep)
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed - very thorough. — Confirm: gz chores doctor lands the
2am-operator recovery path for ADR-0.0.21 § Decision #10. 9/9 REQs
covered (gz covers OBPI-0.0.21-09 --json), 8 REQ-derived behavior tests
plus 1 Invariant 3 output-form fixture in TestChoresDoctor /
TestChoresDoctorOutputForm. Full unittest 3688/3688 pass; mkdocs strict
green; gz cli audit 87/87 cross-coverage. Brief-scope deviation: authored
docs/user/commands/chores-doctor.md and index.md row inside this OBPI
under Prime Directive (gz cli audit fail-closed required surfaces OBPI-06
did not deliver). Receipts: lint
arb-ruff-1d999b0fa232464bbfb6b418696578fe; types
arb-step-typecheck-9a6e88e7dfbd479aa4e1bc1464a796e8; tests-scoped
arb-step-unittest-7fd3a1d6d8f14b69b15e09198058d9a9; tests-full
arb-step-unittest-a4e608e867ef488c8a4019992bf046c4; docs
arb-step-mkdocs-ca188cb8fd1748feb50a0565f1dc16a6.
- Date: 2026-04-27

---

**Brief Status:** Completed

**Date Completed:** 2026-04-27

**Evidence Hash:** -
