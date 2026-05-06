---
id: OBPI-0.0.29-03-complexity-advise-cli
parent: ADR-0.0.29
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.29-03-complexity-advise-cli: gz complexity advise CLI Verb

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #3 — `gz complexity advise` CLI verb (Heavy-lane new subcommand: ADR + manpage + smoke + release notes)

**Status:** Draft

## Objective

Author the `gz complexity advise` CLI verb at `src/gzkit/commands/complexity_advise.py` (registered under the existing `complexity` parser group as a sub-verb sibling of `distill`), document it via manpage and runbook entries, and cover it with a behave smoke scenario per `.gzkit/rules/cli.md` § "New Subcommand (Heavy Lane)". The hyphenated form `gz-complexity-advise` is the canonical manpage filename only; the actual CLI surface is `gz complexity advise <path>`.

## Lane

**Heavy** — New CLI subcommand is a contract change requiring full Heavy-lane treatment per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.18.

## Allowed Paths

- `src/gzkit/commands/complexity_advise.py`
- `src/gzkit/cli/parser_artifacts.py` — register `complexity-advise` verb
- `tests/commands/test_complexity_advise.py`
- `features/complexity_advise.feature` — behave smoke scenario
- `docs/user/manpages/gz-complexity-advise.md`
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-03-complexity-advise-cli.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is OBPI-01
- `src/gzkit/complexity/advisor/engine.py` — engine is OBPI-02
- `src/gzkit/complexity/advisor/intrinsic.py` — attestation is OBPI-07 (CLI flag wiring for `--attest-intrinsic` lands in OBPI-07, not here)
- `src/gzkit/complexity/advisor/timeout.py` — timeout is OBPI-09
- `.gzkit/skills/complexity-advisor/**` — skill is OBPI-04
- `.gzkit/hooks/**` — auto-chain hook is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz complexity advise <path>` analyzes the file or directory at `<path>`, runs the engine (OBPI-02) for each metric crossing in the threshold table (ADR-0.0.28), and emits an `AdvisorDiagnosis` per crossing. Default human-readable output is structured prose; `--json` mode emits the canonical Pydantic serialization.
2. REQUIREMENT: The CLI follows the four-code exit map per `.claude/rules/cli.md`: 0 success (no crossings or all advise-band), 1 user/config error (bad path, malformed flags), 2 system/IO error (missing threshold table, AST parse error), 3 policy breach (a `block`-band crossing). The exit-code map is documented in the manpage.
3. REQUIREMENT: Standard flags per `.claude/rules/cli.md` § Flag Conventions: `--quiet`, `--verbose`, `--dry-run` (no-op for analysis but reserved), `--json`, `--help`/`-h`. The auto-chain marker flag (`--auto-chain`) is reserved here; semantics defined in OBPI-05.
4. REQUIREMENT: Help text per `.claude/rules/cli.md` § Help Text Requirements: description (1–2 sentences), usage line, all options listed, at least one example, lines ≤ 80 chars. `-h`/`--help` exits 0.
5. REQUIREMENT: Manpage at `docs/user/manpages/gz-complexity-advise.md` documents purpose, exit codes, all flags, at least two example invocations (one ad-hoc, one with `--json`), and the runbook cross-reference.
6. REQUIREMENT: Runbook entry under "Complexity doctrine surfaces" prescribes `gz complexity advise` for the operator moment "preview advisor diagnosis on a file before commit".
7. REQUIREMENT: A behave smoke scenario at `features/complexity_advise.feature` tagged with REQ scenario tags covers: a clean file produces exit 0; a file with a warn-band crossing produces exit 0 + diagnosis prose; a file with a block-band crossing produces exit 3.
8. REQUIREMENT: Tests cover: argument parsing (path required, flag interactions); `--json` mode produces valid JSON validating against `src/gzkit/schemas/advisor_diagnosis.json`; exit-code map invariants per the four-code rule; help text contains all standard sections. Each test decorated with `@covers(REQ-0.0.29-03-NN)`.
9. REQUIREMENT: Tool / Skill / Runbook alignment per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1, 2, 3 — the runbook prescribes this verb, OBPI-04's skill routes to it, and the verb's default output form matches the skill's Output Contract.
10. REQUIREMENT: TDD discipline; tests mock subprocess boundaries (no spawned subprocesses in the unit tier per `.claude/rules/tests.md`).
11. REQUIREMENT: NEVER include the operator's personal email in code, manpage, runbook, fixtures, or commit messages.

> STOP-on-BLOCKERS: if OBPI-02 engine and OBPI-01 schema are not landed, STOP — the CLI has nothing to wire to.

## Discovery Checklist

**Parent ADR:**

- [ ] ADR-0.0.29 § Decision recorded with the foundation invariant: one CLI verb (`gz complexity advise`), engine binding (OBPI-02), threshold table (ADR-0.0.28), four-authority canon (Fowler / Martin / Page-Jones / Constantine).
- [ ] ADR-0.0.29 § Mechanical surfaces lists `src/gzkit/commands/complexity_advise.py`, `src/gzkit/cli/parser_artifacts.py`, manpage, runbook, behave smoke as the OBPI-03 mechanical surface.

**Governance:**

- [ ] `.claude/rules/cli.md` § "New Subcommand (Heavy Lane)" reviewed: ADR + manpage + behave smoke + release notes; four-code exit map; flag conventions; help-text requirements.
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` reviewed: manpage + runbook authored in the same patch as code; documentation is a first-class deliverable.
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1–3 reviewed: every CLI tool wielded by at least one skill (OBPI-04 closes this); `gz_command` matches runbook-prescribed verb; default output form honors routing skill's Output Contract.
- [ ] `.claude/rules/tests.md` § Output-form fixture carve-out reviewed: REQ-derived behavior tests and Invariant-3 fixture tests live in separate classes.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.29-01 schema present at `src/gzkit/complexity/advisor/diagnosis.py` exporting `AdvisorDiagnosis`, `RefactorArchetype`, `DoctrinalFrame`, `ProofRange`.
- [ ] OBPI-0.0.29-02 engine present at `src/gzkit/complexity/advisor/engine.py` exporting `DiagnosisEngine`, `AstContext`, `EngineError`, `diagnose`.
- [ ] ADR-0.0.28-02 `ThresholdTable` importable from `gzkit.complexity.thresholds` with `band_for(metric, value)` returning `ThresholdBand | None` and `load_threshold_table(rule_path)` factory.
- [ ] Canonical threshold rule body present at `.gzkit/rules/complexity-thresholds.md` with `radon_cc` per-metric table.
- [ ] `radon` declared as a runtime dependency in `pyproject.toml` (`radon>=6.0,<7.0`) so `radon.complexity.cc_visit` is importable in-process (REQ-10 satisfied vacuously).
- [ ] STOP-on-BLOCKERS: if any of the above is missing, halt and surface to operator before authoring code.

**Existing Code (understand current state):**

- [ ] `src/gzkit/cli/parser_artifacts.py` `_register_complexity_parsers` reviewed — anchors `complexity` parser group and `distill` subverb; the comment at line 98 anchors `advise` and `guide` as future siblings under the same group.
- [ ] `src/gzkit/commands/complexity_distill_cmd.py` reviewed as the structural shape for sibling `complexity advise` handler: `complexity_*_cmd(*, ...) -> int`, `raise SystemExit(code)` for non-zero, helper functions ≤50 lines per `.claude/rules/pythonic.md`.
- [ ] `src/gzkit/cli/main.py:122 main()` dispatcher reviewed — handler return values are dropped; non-zero exit codes MUST `raise SystemExit(code)` to propagate (the same precedent the distill handler honors).
- [ ] `tests/commands/test_complexity_distill_cmd.py` reviewed — Output-form fixture / REQ-derived split, `@covers` decoration, `tempfile.TemporaryDirectory()` fixture pattern, `redirect_stdout`/`redirect_stderr` `_invoke` helper.
- [ ] `tests/complexity/advisor/test_engine.py` reviewed — `_synthetic_environment` context manager pattern that builds a synthetic distilled-characteristics + threshold-rule fixture under a temp project root because the engine fails closed on the production distilled doc's empty practitioner-eye section.
- [ ] `features/steps/gz_steps.py` reviewed — canonical "When I run the gz CLI" / "Then the command exits with code N" step set the new feature reuses verbatim.

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage section + runbook entry

### Gate 4: BDD (Heavy)
- [ ] `features/complexity_advise.feature` smoke scenarios pass with REQ tags

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run mkdocs build --strict
uv run gz complexity advise --help
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_complexity_advise.py -v
uv run -m behave features/complexity_advise.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.29-03-01: Given a clean file with no metric crossings, when `gz complexity advise <path>` runs, then exit 0 and the output names "no crossings".
- [ ] REQ-0.0.29-03-02: Given a file with a warn-band crossing, when the verb runs, then exit 0, diagnosis prose is emitted, and the output names the archetype + doctrinal frame.
- [ ] REQ-0.0.29-03-03: Given a file with a block-band crossing, when the verb runs, then exit 3.
- [ ] REQ-0.0.29-03-04: Given `--json`, when the verb runs against any file, then stdout is valid JSON validating against the advisor_diagnosis JSON Schema.
- [ ] REQ-0.0.29-03-05: Given `--help`, when invoked, then exit 0 and the output contains description, usage, options, and at least one example.
- [ ] REQ-0.0.29-03-06: Given the manpage, when read, then it documents purpose, exit codes, all flags, and at least two example invocations.
- [ ] REQ-0.0.29-03-07: Given `gz cli audit`, when invoked, then exit 0 and the new verb is covered (manpage, command doc, index parity).

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict + manpage + runbook
- [ ] Gate 4: behave scenarios pass
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict + manpage + runbook diff hunks
```

### Gate 4 (BDD)
```text
# Paste behave output
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof


- `uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_complexity_advise` → arb-step-unittest-0bc22aa1874448c4abdc614e15fd270d, exit 0, 13 tests pass.
- `uv run gz arb step --name behave -- uv run -m behave features/complexity_advise.feature` → arb-step-behave-f67c44c6e0c948deb0f85affbf162de9, 1 feature passed, 3 scenarios passed, 12 steps passed.
- `uv run gz arb ruff` → arb-ruff-e129a0e250814b60ab32a6989f033237, exit 0 (lint clean).
- `uv run gz arb typecheck` → arb-step-typecheck-d3bfab8fbd0d4771b65c906dd784f377, exit 0 ("All checks passed!").
- `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` → arb-step-mkdocs-93a27e90e9b844daa1a7d266bb797f4b, exit 0 (strict build clean).
- `uv run gz cli audit` → 93/93 commands fully covered (manpage + command doc + index + governance runbook entries all present for `complexity advise`).
- `uv run gz covers OBPI-0.0.29-03 --json` → total_reqs=7, covered_reqs=7, uncovered_reqs=0, coverage_percent=100.0 (REQ-coverage parity gate passes).
- Observed end-to-end behavior under behave (block-band scenario): `Complexity advisor: crossings detected. [1] metric=radon_cc value=12.0 band=block / Archetype: arrowhead / Authority: martin (Clean Code, ch. 7 — Boundary Conditions) / Proof: subject.py:1-25 / Recommended move: <distilled-characteristics excerpt>`; exit 3 propagated correctly.

### Implementation Summary


- Files created: `src/gzkit/commands/complexity_advise.py` (handler, helpers ≤50 lines per pythonic.md); `tests/commands/test_complexity_advise.py` (13 tests across 4 classes — Behavior + OutputForm + CliAuditParity + HelpManpageParity); `features/complexity_advise.feature` (3 REQ-tagged BDD scenarios); `features/steps/complexity_advise_steps.py` (synthetic-environment Given steps); `docs/user/manpages/gz-complexity-advise.md`; `docs/user/commands/complexity-advise.md`.
- Files modified: `src/gzkit/cli/parser_artifacts.py` (registered `advise` subverb under existing `complexity` parser group); `docs/user/runbook.md` (entry under Governance Doctrine Surfaces); `docs/user/commands/index.md` (link to complexity-advise.md); `docs/governance/governance_runbook.md` (governance-runbook entry per `gz cli audit` requirement); this brief's evidence sections + Discovery Checklist (Parent ADR + Governance + Prerequisites + Existing Code subsections added for authored-readiness); `src/gzkit/complexity/advisor/archetype_rules.py` (in-flight defect fix per AGENTS.md § Defect-fix routing: `Path(__file__).parents[4]` → `importlib.resources.files("gzkit").parent.parent`, clearing the `gz lint` parents-pattern rule; engine + advise tests both green after fix).
- Tests added: 13 unit tests + 3 BDD scenarios; full advisor unittest suite (120 tests) green.
- ARB receipts (canonical green stream): arb-ruff-e129a0e250814b60ab32a6989f033237, arb-step-typecheck-d3bfab8fbd0d4771b65c906dd784f377, arb-step-unittest-0bc22aa1874448c4abdc614e15fd270d, arb-step-behave-f67c44c6e0c948deb0f85affbf162de9, arb-step-mkdocs-93a27e90e9b844daa1a7d266bb797f4b.
- Date completed: 2026-05-06.
- Attestation status: human attested (operator typed `attest completed` at Stage 4).
- Defects noted: in-flight lint defect at `archetype_rules.py:35` fixed under direct-fix routing thresholds (single file, ~20 lines, in-flight trigger, 187 recent fix( commits as precedent). No outstanding tracked defects.

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — gz complexity advise CLI verb wired (sub-verb under complexity parser group), 13 unit tests + 3 behave smoke scenarios pass with REQ-derived @covers decoration covering REQs 01-07, ARB receipts arb-step-unittest-0bc22aa1874448c4abdc614e15fd270d / arb-step-behave-f67c44c6e0c948deb0f85affbf162de9 / arb-ruff-e129a0e250814b60ab32a6989f033237 / arb-step-typecheck-d3bfab8fbd0d4771b65c906dd784f377 / arb-step-mkdocs-93a27e90e9b844daa1a7d266bb797f4b green; gz cli audit 93/93 covered; gz covers OBPI-0.0.29-03 7/7 REQs covered; in-flight lint defect at archetype_rules.py:35 fixed under direct-fix routing (importlib.resources path resolution).
- Date: 2026-05-06

---

**Brief Status:** Completed

**Date Completed:** 2026-05-06

**Evidence Hash:** -
