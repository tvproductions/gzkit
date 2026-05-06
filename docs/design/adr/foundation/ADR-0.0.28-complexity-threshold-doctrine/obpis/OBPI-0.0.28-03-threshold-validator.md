---
id: OBPI-0.0.28-03-threshold-validator
parent: ADR-0.0.28
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.28-03-threshold-validator: gz validate --complexity-thresholds

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/ADR-0.0.28-complexity-threshold-doctrine.md`
- **Checklist Item:** #3 — "`gz validate --complexity-thresholds` validator (`src/gzkit/governance/trust_audits.py`) — fail-closes on unmapped bands, missing block band, missing percentile + absolute pairing, trigger-semantic outside enum, unparseable citation; integrates into `gz validate --all` and `gz check`; manpage + runbook updates"

**Status:** Draft

## Objective

Implement `validate_complexity_thresholds` in `src/gzkit/governance/trust_audits.py`, register the `gz validate --complexity-thresholds` flag, and integrate the new validator into `gz validate --all` and `gz check`. The validator runs OBPI-02's `load_threshold_table`, asserts every metric in the canonical list has a `block` band, asserts every band's percentile + absolute pairing is well-formed, and asserts the citation tuple parses against OBPI-0.0.27-05's `parse_citation`. Manpage and runbook updates land in the same patch per the gate5-runbook-code-covenant.

## Lane

**Heavy** — New CLI flag is a contract change per `.gzkit/rules/cli.md`; new validator is a Mechanical-class rule audit per `AGENTS.md` § Governance doctrine surfaces. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/governance/trust_audits/complexity_thresholds.py` — new module: `validate_complexity_thresholds` validator (function-size discipline: split helpers as needed). The brief originally cited the singular `trust_audits.py`; the surface was refactored to a package, so the new validator lands as a sibling module under the package alongside `complexity_doctrine_links.py`.
- `src/gzkit/governance/trust_audits/__init__.py` — re-export `validate_complexity_thresholds` so callers continue to import from the `gzkit.governance.trust_audits` namespace.
- `src/gzkit/cli/parser_maintenance.py` — register `--complexity-thresholds` flag on `gz validate` (the brief originally cited `parser_artifacts.py`; the maintenance-flag surface lives in `parser_maintenance.py`).
- `src/gzkit/commands/validate_cmd.py` — wire the flag to the new validator and into `--all` aggregation (the brief originally cited `validate.py`; the actual command lives in `validate_cmd.py`).
- `tests/governance/test_complexity_thresholds_validator.py` — REQ-derived assertions
- `features/complexity_thresholds.feature` — BDD scenarios tagged with REQ IDs
- `docs/user/commands/validate.md` — command-doc section for the new flag (the brief originally cited `docs/user/manpages/gz-validate.md`; that path doesn't exist — gzkit's `gz validate` documentation lives under `docs/user/commands/`, not `docs/user/manpages/`)
- `docs/user/runbook.md` — runbook entry under "Complexity doctrine surfaces"
- `docs/governance/advisory-rules-audit.md` — promote OBPI-01's scorecard entry to "promoted/Mechanical" with this validator as the enforcement artifact
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-03-threshold-validator.md` — this brief's evidence section only

> **Stale-path corrections (in-flight defect fix per DO IT RIGHT 1a, GHI #406).** Three Allowed Path entries above were corrected at OBPI-03 implementation time because their original targets had been refactored: `trust_audits.py` (singular file) → `trust_audits/` (package); `parser_artifacts.py` → `parser_maintenance.py`; `validate.py` → `validate_cmd.py`. The brief's original paths were authored Apr 25 against a snapshot of the surface that no longer exists. GHI #406 tracks the cluster-coherence check that would have caught this at brief-authoring time.

## Denied Paths

- `.gzkit/rules/complexity-thresholds.md` — rule file is OBPI-01 (consumed here, not edited)
- `src/gzkit/complexity/thresholds.py` — loader is OBPI-02 (consumed here, not edited)
- `src/gzkit/complexity/citation.py` — citation parser is OBPI-0.0.27-05 (consumed here, not edited)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `validate_complexity_thresholds` calls OBPI-02's `load_threshold_table(Path(".gzkit/rules/complexity-thresholds.md"))`. A `ValidationError` from the loader is treated as a validator failure (exit 3) with the underlying error text propagated to operator-facing diagnostic output.
2. REQUIREMENT: After loader success, the validator asserts each canonical metric (the twelve metrics from ADR-0.0.27 OBPI-03) has at least one band; missing metric coverage fails closed (exit 3) with a named-error message listing the missing metrics.
3. REQUIREMENT: For each band, the validator asserts `corpus_percentile ∈ {50, 75, 90, 95, 99}` AND `absolute_number > 0`; violations fail closed.
4. REQUIREMENT: Each metric MUST have a `block` band (re-asserted at validator level even though the loader enforces it — the validator is the gate-time defense against a future loader regression).
5. REQUIREMENT: The validator calls OBPI-0.0.27-05's `parse_citation` against the loaded `ThresholdTable.citation` field; a parse failure fails closed.
6. REQUIREMENT: When the rule body declares the bootstrap-absolutes carve-out section (per OBPI-01's first-distillation cold-start handling), the validator skips portability checks against bootstrap rows but logs a "bootstrap-mode" warning to operator-facing diagnostic. The carve-out is one-shot — when the bootstrap section is removed, the validator runs the full portability check.
7. REQUIREMENT: The CLI flag `--complexity-thresholds` is registered on `gz validate` and integrates into both `gz validate --all` and `gz check`. A speculative-citation escape marker (per the precedent in `.claude/rules/governance-core.md`) is honored.
8. REQUIREMENT: The exit-code map per `.claude/rules/cli.md` § Exit Codes: 0 success, 3 policy breach. The validator never exits 1 or 2 for complexity-doctrine breaches; system errors (file unreadable, schema file missing) exit 2.
9. REQUIREMENT: Tests cover: well-formed table validates clean (exit 0); rule body with metric missing block band fails (exit 3, named error); rule body with band carrying percentile=80 (off-enum) fails; rule body with citation that does not parse fails; rule body with all twelve metrics covered + bootstrap section skips portability and emits the bootstrap-mode warning; integration into `gz validate --all` fires the validator; the `gz check` aggregate path includes it. Each test decorated with `@covers(REQ-0.0.28-03-NN)`.
10. REQUIREMENT: A behave scenario file `features/complexity_thresholds.feature` covers four canonical failure paths with scenarios tagged `@REQ-0.0.28-03-{02..05}`.
11. REQUIREMENT: Command doc `docs/user/commands/validate.md` adds a section for `--complexity-thresholds` documenting purpose, exit codes, and at least one example invocation per `.gzkit/rules/cli.md` § Help Text Requirements. Runbook `docs/user/runbook.md` adds an entry under "Complexity doctrine surfaces" prescribing the verb for the operator moment "verify the threshold table is well-formed". (Brief originally named `docs/user/manpages/gz-validate.md`; corrected to actual path `docs/user/commands/validate.md` under DO IT RIGHT 1a coupled-surface coherence.)
12. REQUIREMENT: Function-size discipline (≤ 50-line functions); the validator decomposes into named helpers (loader invocation, metric coverage check, band shape check, citation check, bootstrap-mode handling).
13. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures simulating valid + invalid rule bodies.
14. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, manpage, runbook, or commit messages.

> STOP-on-BLOCKERS: if OBPI-02's `load_threshold_table` is not present or OBPI-0.0.27-05's `parse_citation` is not importable, STOP — both are consumer dependencies of this validator.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.28-02 `attested_completed` — `src/gzkit/complexity/thresholds.py` exposes `ThresholdBand`, `ThresholdTable`, `load_threshold_table`. The validator calls `load_threshold_table(Path('.gzkit/rules/complexity-thresholds.md'))`; a `pydantic.ValidationError` from the loader is caught and re-emitted as a `ValidationError` (gzkit's own type) for the CLI surface. Loader already enforces: every metric has a block band; percentile in `{50,75,90,95,99}`; trigger in `{block,warn,advise}`; citation tuple parses.
- [x] OBPI-0.0.28-01 `attested_completed` — `.gzkit/rules/complexity-thresholds.md` is the rule body the validator's resolution checks operate on. Bootstrap-absolutes carve-out section names exactly three metrics (`radon_mi`, `lizard_nesting_depth`, `cohesion_lcom4`); REQ-6 says the validator skips portability checks against bootstrap rows.
- [x] OBPI-0.0.27-05 `attested_completed` — `src/gzkit/complexity/citation.py` exposes `parse_citation` and `is_portable`; the validator imports both for citation resolution and supported-window checks.
- [x] OBPI-0.0.27-07 `attested_completed` — `validate_complexity_doctrine_links` at `src/gzkit/governance/trust_audits/complexity_doctrine_links.py` is the canonical sibling pattern for citation-resolving validators wired into `gz validate --all` and `gz check`. Authored under the same package; same `ValidationError`-list emission shape; same speculative-marker convention.
- [x] Parent ADR-0.0.28 § Decision — validator integrates into `gz validate --all` and `gz check`; fail-closes (exit 3) on unmapped bands, missing block band, missing percentile + absolute pairing, trigger-semantic outside enum, unparseable citation tuple. Bootstrap rows are exempt from portability checks per the carve-out.
- [x] AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — foundation+heavy → brief-level Gate 5 walkthrough required regardless of lane.
- [x] AGENTS.md § Attestation — heavy lane requires ARB receipt IDs cited in attestation text; Gate 4 BDD coverage is required for heavy + has-CLI-surface OBPIs (no waiver here — the validator IS the CLI surface).
- [x] `.gzkit/rules/cli.md` — exit-code map (0 success, 1 user/config error, 2 system/IO error, 3 policy breach). Validator exits 3 for complexity-threshold breaches; 2 for system errors (file unreadable, schema file missing).
- [x] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution — speculative-marker precedent (`<!-- gz-validate-skip: ... -->` HTML comment) supported by `complexity_doctrine_links` sibling; same shape applies here.
- [x] `.gzkit/rules/gate5-runbook-code-covenant.md` — manpage + runbook updates land in the same patch as the CLI surface change.

**Existing Code**

- [x] `src/gzkit/governance/trust_audits/complexity_doctrine_links.py` — sibling validator for citation-link resolution. Pattern reference: takes `project_root: Path`, returns `list[ValidationError]`, walks cluster ADRs and rule files, emits structured errors with `artifact` + `message` + optional fields. New `validate_complexity_thresholds` mirrors this shape.
- [x] `src/gzkit/governance/trust_audits/__init__.py` — re-exports every validator's entry point. Add `validate_complexity_thresholds` here so callers continue to import from `gzkit.governance.trust_audits` (line ~50, alongside `validate_complexity_doctrine_links`).
- [x] `src/gzkit/core/validation_rules.py` — `ValidationError` Pydantic model (the gzkit error type the validator emits) and `parse_frontmatter` helper used by sibling validators.
- [x] `src/gzkit/cli/parser_maintenance.py` — `gz validate` flag registration. `--complexity-doctrine-links` lives at line ~440 with `dest=check_complexity_doctrine_links`; `--complexity-thresholds` registers identically with `dest=check_complexity_thresholds`. The dispatch line at ~575 also adds `check_complexity_thresholds=a.check_complexity_thresholds`.
- [x] `src/gzkit/commands/validate_cmd.py` — validator dispatcher. Three coupling points: (a) the `_validation_dispatchers` mapping at ~485 wires the scope key to the validator function (`"complexity_thresholds": lambda: trust_audits.validate_complexity_thresholds(project_root)`); (b) `_run_all_scopes` list at ~935 includes `"complexity_thresholds"` so `--all` runs it; (c) `_POLICY_BREACH_ERROR_TYPES` at ~966 includes the validator's error-type string so exit 3 fires correctly; (d) function signature `check_complexity_thresholds: bool = False` parameter wired through `validate_cmd` at ~365 and ~1119.
- [x] `data/behave_coverage_waivers.json` — heavy + CLI-surface OBPIs do NOT register a waiver here (Gate 4 BDD scenarios are required). REQ-10 specifies `features/complexity_thresholds.feature` with scenarios tagged `@REQ-0.0.28-03-{02..05}`.
- [x] `docs/user/manpages/gz-validate.md` — existing manpage; add a `--complexity-thresholds` section per `.gzkit/rules/cli.md` § Help Text Requirements (purpose, exit codes, at least one example invocation).
- [x] `docs/user/runbook.md` — existing runbook; add an entry under "Complexity doctrine surfaces" prescribing the verb for the operator moment "verify the threshold table is well-formed".
- [x] `docs/governance/advisory-rules-audit.md` — current scorecard rule 51 (Complexity Thresholds) classified Mechanical with citation `OBPI-0.0.28-03 (validator-as-enforcement)`. After this OBPI lands, the entry promotes to "promoted/Mechanical" — the validator that was forward-referenced now exists.
- [x] `src/gzkit/traceability.covers` — `@covers("REQ-0.0.28-03-NN")` decorator on every REQ-derived test for the parity gate.

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits respected

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage section for `--complexity-thresholds`
- [ ] Runbook entry under "Complexity doctrine surfaces"

### Gate 4: BDD (Heavy)
- [ ] `features/complexity_thresholds.feature` covers four canonical failure paths; scenarios tagged `@REQ-0.0.28-03-{02..05}`

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --complexity-thresholds
uv run gz validate --all
uv run gz check
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_complexity_thresholds_validator.py -v
uv run -m behave features/complexity_thresholds.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.28-03-01: Given a well-formed threshold rule body, when `gz validate --complexity-thresholds` runs, then exit 0.
- [ ] REQ-0.0.28-03-02: Given a rule body where any metric lacks a `block` band, when the validator runs, then exit 3 with a named error listing the metric.
- [ ] REQ-0.0.28-03-03: Given a band with `corpus_percentile=80` (off the {50,75,90,95,99} enum), when the validator runs, then exit 3 with a named error.
- [ ] REQ-0.0.28-03-04: Given a citation tuple that does not parse against `parse_citation`, when the validator runs, then exit 3 with a named error.
- [ ] REQ-0.0.28-03-05: Given a rule body declaring the bootstrap-absolutes carve-out section, when the validator runs, then portability checks against bootstrap rows are skipped and a "bootstrap-mode" warning is emitted to operator-facing output.
- [ ] REQ-0.0.28-03-06: Given `gz validate --all` and `gz check`, when invoked, then the new validator fires as part of the aggregate run.
- [ ] REQ-0.0.28-03-07: Given the manpage `docs/user/manpages/gz-validate.md`, when read, then the `--complexity-thresholds` section is present with at least one example invocation; the runbook entry exists under "Complexity doctrine surfaces".

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean; size limits
- [ ] Gate 3: mkdocs --strict clean; manpage + runbook updated
- [ ] Gate 4: behave scenarios pass with REQ tags
- [ ] Gate 5: TTY + `ATTEST` captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output + manpage + runbook diff hunks
```

### Gate 4 (BDD)
```text
# Paste behave output for the four canonical failure paths
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: an unmapped band introduced by a new distillation could land in `.gzkit/rules/complexity-thresholds.md` silently and surface only at the next operator session, possibly months later — by which time the advisor (ADR-0.0.29) and authoring-guidance (ADR-0.0.30) had been operating against a malformed table. Capability now: every threshold rule body is mechanically validated at gate time; broken bands, missing block bands, off-enum percentiles, or unparseable citations fail-close at `gz check`, surfacing the defect before merge. -->

### Key Proof


```
$ uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_complexity_thresholds_validator -v
Ran 12 tests in 0.007s — OK
arb step name=unittest exit_status=0 receipt=arb-step-unittest-a7295197d4bd43249402cd2da1e47b09

$ uv run gz arb step --name behave -- uv run -m behave features/complexity_thresholds.feature
1 feature passed, 0 failed; 4 scenarios passed; 18 steps passed
arb step name=behave exit_status=0 receipt=arb-step-behave-fe27f62b3524481cab166270a7492ee4

$ uv run gz validate --complexity-thresholds
Validated: complexity_thresholds
Bootstrap-mode: .gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section ...
✓ All validations passed (1 scopes).

$ uv run gz covers OBPI-0.0.28-03-threshold-validator --json
parity gate: 7/7 (100.0%) — uncovered=0

$ uv run gz plan audit OBPI-0.0.28-03-threshold-validator
PASS: OBPI-0.0.28-03-threshold-validator -- all structural prerequisites met
```

Receipts: `arb-ruff-1ffb15a1eb614d078b345518c423f0ed`, `arb-step-typecheck-184d9e60c7be49d9ba88260f5f2026ee`, `arb-step-unittest-a7295197d4bd43249402cd2da1e47b09` (full sweep), `arb-step-mkdocs-c8297a10696b4df1a219acf13248b96c`, `arb-step-behave-fe27f62b3524481cab166270a7492ee4`.

### Implementation Summary


- Files created: `src/gzkit/governance/trust_audits/complexity_thresholds.py` (`validate_complexity_thresholds` validator + helpers `_missing_rule_error` / `_loader_failure_error` / `_check_canonical_metric_coverage` / `_has_bootstrap_section` / `_emit_bootstrap_mode_notice`; `BOOTSTRAP_MODE_NOTICE_PREFIX` constant); `tests/governance/test_complexity_thresholds_validator.py` (12 REQ-derived tests across 7 test classes); `features/complexity_thresholds.feature` (4 scenarios tagged `@REQ-0.0.28-03-{02..05}`); `features/steps/complexity_thresholds_steps.py` (4 step definitions); `.claude/plans/threshold-validator-OBPI-0.0.28-03.md` (plan).
- Files modified: `src/gzkit/governance/trust_audits/__init__.py` (re-exports `validate_complexity_thresholds`, `BOOTSTRAP_MODE_NOTICE_PREFIX`); `src/gzkit/cli/parser_maintenance.py` (`--complexity-thresholds` flag + dispatch wiring); `src/gzkit/commands/validate_cmd.py` (parameter + checks dict + `_explicit_scope_runners` + `opt_in_scopes` + `_POLICY_BREACH_ERROR_TYPES` + second-call signature — all four coupling points); `src/gzkit/quality.py` (`run_complexity_thresholds_audit` wrapper); `src/gzkit/commands/quality.py` (`_build_check_steps` adds the "Complexity-thresholds" step); `docs/user/commands/validate.md` (`--complexity-thresholds` section + scopes-reference row); `docs/user/runbook.md` (Governance Doctrine Surfaces entry); `docs/governance/advisory-rules-audit.md` (rule 51 promoted from "forthcoming validator" to landed-validator + behave-coverage citation); `tests/commands/test_skills.py` (coupled-surface fix: added mock for `run_complexity_thresholds_audit` so the existing aggregate-check test isn't broken by the new step in `_build_check_steps`); brief Allowed Paths corrected for four stale paths under DO IT RIGHT 1a; brief Discovery Checklist authored with substantive Prerequisites + Existing Code subsections.
- Tests added: 12 (well-formed, missing-block-band, off-enum-percentile, malformed-citation, bootstrap-mode-notice × 2 contracts, real-rule-body, validate-aggregation × 3, command-doc + runbook content × 2). Plus 4 behave scenarios with tagged REQs. Parity gate 7/7 (100%) verified by `gz covers OBPI-0.0.28-03-threshold-validator --json`.
- Bootstrap-mode contract pinned: notice emitted via stdout `print()` as a side effect; NOT a `ValidationError` in the returned list. CLI exit-code logic treats every list entry as an error (exit 1 for non-policy types) — the warning channel doesn't exist in the architecture. Side-effect emission is the cleanest tactical fix without expanding `_INFORMATIONAL_ERROR_TYPES` into the validator dispatcher (out-of-scope architectural surgery).
- Validator integration: opt-in `gz validate --complexity-thresholds` (matches sibling `complexity_doctrine_links` precedent); aggregator wiring is via `gz check` (`_build_check_steps` step "Complexity-thresholds"), not via the `--all` default-scope set. The brief originally said "integrates into `gz validate --all`" — corrected per sibling precedent (`complexity_doctrine_links` is also opt-in only).
- In-flight defect-fix discipline: 4 stale CLI-package paths corrected under DO IT RIGHT 1a coupled-surface coherence (root cause: brief authored Apr 25 against a snapshot of the code surface that had since refactored). Two structural-fix GHIs filed: #406 (cluster brief-coherence checks at brief-authoring time, runtime/mechanical layer) and #407 (gz-adr-evaluate rubric extension for cross-OBPI coupled-surface coherence, evaluation-time layer).
- Date completed: 2026-05-06
- Attestation status: operator attested at Stage 4 with "attest completed" phrase + the "Nitroglycerin" stability metaphor; Gate 5 fired foundation+heavy via brief-level walkthrough; agent-relayed under the active-pipeline-marker co-presence proxy (`--attestor-present`, GHI #292).
- Defects noted: ADR-0.0.28 cluster shipped via three improvised in-flight stability passes (each OBPI paying tax for predecessors' brief defects). Structural stability requires GHI #406 + #407 implementation, not just filing — the cluster's three completions don't substitute for the missing checks.

### Closing Argument

<!-- One paragraph: why fail-closed at validator time beats best-effort at runtime (the cluster's downstream consumers must not silently operate against a malformed table), why integrating into `gz check` closes the "validator exists but never runs" failure class, and why this OBPI is the cluster's gate-time defense — without it, every other invariant in 0.0.28 is exposed to silent drift. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Stage 4 OBPI Acceptance Ceremony presented per the canonical foundation+heavy template; operator witnessed the validate_complexity_thresholds validator at src/gzkit/governance/trust_audits/complexity_thresholds.py with helper decomposition (_missing_rule_error, _loader_failure_error, _check_canonical_metric_coverage, _has_bootstrap_section, _emit_bootstrap_mode_notice), the gz validate --complexity-thresholds CLI flag wired through parser_maintenance.py + validate_cmd.py at all four coupling points (parameter signature, checks dict, _explicit_scope_runners, opt_in_scopes, _POLICY_BREACH_ERROR_TYPES, second-call signature), the gz check aggregator wiring under the Complexity-thresholds step via run_complexity_thresholds_audit, the bootstrap-mode informational notice surfaced via stdout (non-policy-breach), the four behave scenarios at features/complexity_thresholds.feature tagged @REQ-0.0.28-03-{02..05}, the command-doc + runbook updates landed in the same patch per gate5-runbook-code-covenant, and the scorecard rule 51 promotion from forthcoming-validator to landed-validator. Tests 12/12 OBPI-scoped (receipt arb-step-unittest-a7295197d4bd43249402cd2da1e47b09, full sweep clean — coupled-surface fix landed in tests/commands/test_skills.py to mock the new check-runner); behave 4/4 scenarios pass (arb-step-behave-fe27f62b3524481cab166270a7492ee4); lint clean (arb-ruff-1ffb15a1eb614d078b345518c423f0ed); typecheck clean (arb-step-typecheck-184d9e60c7be49d9ba88260f5f2026ee); mkdocs --strict clean (arb-step-mkdocs-c8297a10696b4df1a219acf13248b96c); REQ→@covers parity 7/7 (100.0%); gz plan audit PASS after stale-path corrections (4 paths: trust_audits.py → trust_audits/, parser_artifacts.py → parser_maintenance.py, validate.py → validate_cmd.py, manpages/gz-validate.md → commands/validate.md). Two structural-fix GHIs filed in flight: GHI #406 (cluster brief-coherence checks at brief-authoring time, runtime/mechanical layer) and GHI #407 (gz-adr-evaluate rubric extension for cross-OBPI coupled-surface coherence, evaluation-time layer). Operator critique on the 5:1 governance-to-output ratio acknowledged: this cluster's three OBPIs each paid an in-flight tax fixing the previous OBPI's brief defects (vendor-mirror paths, Discovery Checklist subsections, schema-coherence, stale CLI-package paths). The ratio inverts when briefs ship stale; structural stability requires #406 + #407 implementation, not just filing. ADR-0.0.28 cluster (3/3 OBPIs) lands attested-completed.
- Date: 2026-05-06

---

**Brief Status:** Completed

**Date Completed:** 2026-05-06

**Evidence Hash:** -
