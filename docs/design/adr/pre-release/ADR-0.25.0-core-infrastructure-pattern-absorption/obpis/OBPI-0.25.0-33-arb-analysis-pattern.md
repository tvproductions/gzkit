---
id: OBPI-0.25.0-33-arb-analysis-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 33
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-33: ARB Analysis Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-33 — "Evaluate and absorb opsdev/arb/ (603 lines total) — receipt advise, validate, and pattern extraction"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/arb/` (603 lines total across multiple files)
against gzkit's ARB analysis surface and determine: Absorb, Confirm, or
Exclude. The airlineops package covers receipt advise, validate, and pattern
extraction. gzkit's equivalent surface spans `commands/closeout_ceremony.py`
(579 lines), `commands/obpi_complete.py` (648 lines), `instruction_eval.py`
(465 lines), and `instruction_audit.py` (319 lines) — approximately 2000+
lines across 4+ modules providing step-driven receipt validation, OBPI
completion with evidence gathering, and instruction evaluation with pattern
extraction.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/arb/` (603 lines total)
- **gzkit equivalent:** Distributed across `src/gzkit/commands/closeout_ceremony.py`, `src/gzkit/commands/obpi_complete.py`, `src/gzkit/instruction_eval.py`, `src/gzkit/instruction_audit.py` (~2000+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 3x larger surface suggests more mature ARB handling — comparison will verify
- The airlineops ARB package may have multiple files — all must be read for complete comparison

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's ARB/receipt architecture around airlineops's package layout

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules (specifically `src/gzkit/arb/` per ADR integration points line 64)
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs
- `data/schemas/arb_lint_receipt.schema.json`, `data/schemas/arb_step_receipt.schema.json` — receipt schema definitions
- `docs/user/commands/arb.md`, `docs/user/commands/index.md` — operator command reference
- `docs/user/manpages/arb.md` — manpage per cli.md heavy-lane contract
- `docs/user/runbook.md` — reference ARB in the heavy-lane attestation flow
- `features/arb.feature`, `features/steps/arb_steps.py` — Gate 4 BDD coverage
- `.gzkit/rules/arb.md` — rule version bump and verb list update (v1.0 → v1.1)
- `.gzkit/skills/gz-arb/` — Invariant 1 skill coverage if needed

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief — ADR-0.25.0 checklist item #33 (brief line 15) and ADR integration points line 64 explicitly name `src/gzkit/arb/` as a target.

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test` — new test modules `tests/arb/test_*.py`, `tests/commands/test_arb_cmd.py`, and `tests/test_parser_arb.py` each follow a Red→Green sequence (see Stage 3 evidence).
- [x] `Absorb` outcome — gzkit package `src/gzkit/arb/` (7 modules), CLI `src/gzkit/commands/arb.py`, parser `src/gzkit/cli/parser_arb.py`, and 2 JSON schemas under `data/schemas/` now carry the pattern.

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` decision (see Decision section below).
- [x] Comparison rationale names concrete capability differences and the chosen outcome in the Comparison Evidence table.

### Gate 4: BDD

- [x] Operator-visible behavior change (`gz arb` is a new CLI surface). `features/arb.feature` adds six scenarios covering ARB help, validate zero-state, advise zero-state, patterns zero-state/compact, and validate JSON output.

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — pending Stage 4 ceremony.

## Acceptance Criteria

- [x] REQ-0.25.0-33-01: Given the completed comparison, the brief records Decision: **Absorb**.
- [x] REQ-0.25.0-33-02: Given the decision rationale, it cites concrete capability, CLI integration, storage, and governance-vacuum differences between airlineops and gzkit in the Comparison Evidence table.
- [x] REQ-0.25.0-33-03: Given an `Absorb` outcome, gzkit contains the adapted `src/gzkit/arb/` package, `gz arb` CLI dispatcher, JSON schemas, and test suite under `tests/arb/` and `tests/commands/test_arb_cmd.py`.
- [x] REQ-0.25.0-33-04: N/A — outcome is Absorb.
- [x] REQ-0.25.0-33-05: `gz arb` is a new operator-visible CLI surface, so Gate 4 behavioral proof is present (`features/arb.feature`, six scenarios).

## Verification Commands (Concrete)

```bash
test -d ../airlineops/src/opsdev/arb
# Expected: airlineops source package under review exists

test -f src/gzkit/commands/closeout_ceremony.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-33-arb-analysis-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Comparison Evidence

Both surfaces were read in full before authoring this decision. The table records concrete capability differences with file:line citations and commit references.

| Dimension | airlineops `opsdev/arb/` (~1039 L across 7 core files) | gzkit (pre-absorption) | Absorb? |
|-----------|---------------------------------------------------------|------------------------|---------|
| CLI surface | Internal Python API, invoked via `uv run -m opsdev arb <verb>` | **None** — `gz arb` did not exist as a CLI verb (verified via `uv run gz arb` returning `invalid choice: 'arb'`). `.gzkit/rules/arb.md` v1.0 documented a full `gz arb` verb tree that was vaporware | **Yes** |
| Lint receipt emission | `ruff_reporter.py:176-244` — `run_ruff()` wraps ruff, parses JSON findings, writes to `artifacts/receipts/` | None — `gz check` runs ruff directly with no receipt artifact | **Yes** |
| Step receipt emission | `step_reporter.py:51-135` — `run_step()` wraps any command, captures stdout/stderr tail, writes receipt | None — `gz check` runs the step and discards output | **Yes** |
| Schema governance | `data/schemas/arb_lint_receipt.schema.json`, `arb_step_receipt.schema.json` — Draft 2020-12 with `$id` and `schema` const validation | None under `data/schemas/` — verified empty via `ls data/schemas/arb_*.json` | **Yes** |
| Advice aggregation | `advise.py:100-165` — `collect_arb_advice()` aggregates recent lint receipts, categorizes rules (correctness/style/quality), emits `ArbAdvice` with `top_rules`, `top_paths`, `recommendations` | None — `chores_advise()` in `chores.py:267` is dry-run chore criteria, unrelated to lint telemetry | **Yes** |
| Pattern extraction | `patterns.py:130-194` — `collect_patterns()` maps recurring rules through `RULE_GUIDANCE` dict to `PatternCandidate` + `PatternReport` for agent guidance documents | None — `instruction_eval.py` and `instruction_audit.py` audit instruction surfaces, not lint findings | **Yes** |
| Receipt validation | `validate.py:59-128` — Draft 2020-12 validator, schema ID lookup, counts valid/invalid/unknown | None — `validate_pkg/ledger_check.py` validates governance ledger events (Pydantic `ObpiReceiptEvidence`), not lint/step receipts | **Yes** |
| Data model rigor | Frozen `@dataclass` (no field validators) | (pre-absorption: none); (post-absorption) Pydantic `BaseModel(frozen=True, extra="forbid")` with `Field(..., description=...)` per `.gzkit/rules/models.md` | Upgrade during absorption |
| Attestation integration | None — library-only, no link to attestation rule | `.claude/rules/attestation-enrichment.md` declares ARB receipts fail-closed for Heavy lane, but the tool to produce them did not exist — **governance vacuum** | **Yes (primary driver)** |
| Storage architecture | Per-run receipt files under `arb.receipts_root` (config-driven) | Per-run receipt files under `arb.receipts_root` (matching airlineops; added under this OBPI as `ArbConfig` on `GzkitConfig`) | Parity |
| Cross-platform subprocess | `subprocess.run(..., text=True)` without explicit encoding | (post-absorption) `subprocess.run(..., text=True, encoding="utf-8", errors="replace")` per `.gzkit/rules/cross-platform.md` | Upgrade during absorption |

## Forensic Trace of the Governance Vacuum

The vacuum this OBPI closes was created mechanically, not by design:

1. **`37c891ca` (2026-03-15, "chore: regenerate control surfaces after tidy implementation")** — `.claude/rules/arb.md` was added as a mirrored instruction file. Content was copied wholesale from airlineops, including literal commands like `uv run -m opsdev arb ruff` and schema ID `airlineops.arb.lint_receipt.v1`. No accompanying implementation.
2. **`4700b623` (2026-03-18, "chore: auto-commit staged changes (gz git-sync)")** — A mechanical find-and-replace converted `opsdev` → `gzkit` and `airlineops.arb.lint_receipt.v1` → `gzkit.arb.lint_receipt.v1` (18 insertions, 18 deletions). Bundled into an auto-commit with no semantic signal.
3. **`32dfd36b` (2026-03-18)** — `.gzkit/rules/arb.md` canonicalized the renamed content, locking in the drift.
4. **`4c7573fc` and `f350cf44`** — `attestation-enrichment.md` was added and hardened to fail-closed Heavy-lane status, prescribing ARB receipts as the canonical record without anyone verifying the infrastructure existed.
5. **2026-04-03 skill consolidation** — A prior skill consolidation marked `.gzkit/skills/gz-arb/SKILL.md` as `lifecycle_state: retired` with `archived_into: gz-check`. This was itself drift: `gz check` never implemented ARB receipt emission, so the consolidation claim was nominal rather than real.

The forensic trace is reproducible via:

```bash
git log --all --oneline -S "uv run -m gzkit arb" -- .claude/rules/arb.md .gzkit/rules/arb.md
git show 4700b623 -- .claude/rules/arb.md    # shows opsdev → gzkit rename
```

## Decision: Absorb

**Decision:** Absorb — port `airlineops/src/opsdev/arb/` into `src/gzkit/arb/` with gzkit conventions (Pydantic, pathlib, UTF-8, typed config), register `gz arb` as a new CLI subcommand surface with seven verbs, and revive the `gz-arb` skill from retired to active.

**Rationale.**

1. **ARB is not airline-specific by design.** The module docstrings and architecture treat ARB as generic agent QA middleware — wrapping ruff, ty, unittest, coverage, or any step. The subtraction test (`airlineops - gzkit = pure airline domain`) favors absorption.
2. **The attestation rule demands receipts the infrastructure did not produce.** `.claude/rules/attestation-enrichment.md` declares: *"The only faithful record of a QA step is the wrapped-command receipt."* It requires receipt IDs for every claim category in Heavy-lane attestations, fail-closed. Before this OBPI, that rule was an obligation the repository could not satisfy — every Heavy-lane closeout either cited nominal compliance or implicitly invoked the rule without producing artifacts. Closing the gap is governance-coherent and cannot be deferred without either rewriting the attestation rule or leaving it permanently non-executable.
3. **The ADR explicitly names `src/gzkit/arb/` as a target.** ADR-0.25.0 line 64 lists `src/gzkit/arb/ — ARB receipts (compare with opsdev/arb/)` as an integration point, and line 139-140 scopes OBPI-0.25.0-33 to `opsdev/arb/ (603 lines total) — receipt advise, validate, and pattern extraction`. The Absorb decision matches the ADR's pre-declared intent, not a late scope expansion.
4. **Closing the vacuum is the only outcome consistent with Invariant 1 of tool/skill/runbook alignment.** A Confirm decision would leave `.gzkit/rules/arb.md` v1.0 Active with a seven-verb surface that didn't exist (Invariant 1 violation: rule references a nonexistent CLI). An Exclude decision would force a rule deletion that contradicts the ADR's integration-point list. Absorb is the only outcome that produces mechanically-verifiable alignment across rule, runbook, skill, and CLI surfaces.
5. **The airlineops implementation is already battle-tested and clean.** The port required only three mechanical adaptations: (a) drop `github_issues.py` / `supabase_sync.py` imports, (b) rename schema IDs `airlineops.arb.*` → `gzkit.arb.*`, (c) convert frozen dataclasses to Pydantic `BaseModel(frozen=True, extra="forbid")` per `.gzkit/rules/models.md`. Business logic (rule categorization, receipt shape, advice heuristics, pattern extraction) carries over unchanged.

**Consequence.** Every future Heavy-lane OBPI attestation can now honestly cite ARB receipt IDs. The first such attestation is this OBPI's own Stage 4 ceremony — ADR-0.25.0 closes by eating its own dog food, producing receipts from the very surface it just absorbed. The `.gzkit/rules/arb.md` rule is bumped to v1.1 with the `gz arb patterns` verb added, the `gz-arb` skill is revived from retired to active with a revival note citing this OBPI, and the docs covenant is satisfied via `docs/user/commands/arb.md`, `docs/user/manpages/arb.md`, and an updated `docs/user/runbook.md` Heavy-lane attestation flow.

### Implementation Summary


- **Decision:** Absorb
- **Package created:** `src/gzkit/arb/` (7 modules, ~900 L after Pydantic conversion)
  - `__init__.py` — public surface re-exports
  - `paths.py` — `receipts_root()` wired to `ArbConfig`
  - `ruff_reporter.py` — `run_ruff_via_arb()` emits lint receipts
  - `step_reporter.py` — `run_step_via_arb()` emits step receipts
  - `validator.py` — `validate_receipts()` with Pydantic `ArbReceiptValidationResult`
  - `advisor.py` — `collect_arb_advice()` with Pydantic `ArbAdvice`
  - `patterns.py` — `collect_patterns()` with Pydantic `PatternCandidate` / `PatternReport` + `RULE_GUIDANCE` dict
- **CLI dispatcher:** `src/gzkit/commands/arb.py` — 7 verb dispatchers (`ruff`, `step`, `ty`, `coverage`, `validate`, `advise`, `patterns`)
- **Parser:** `src/gzkit/cli/parser_arb.py` — new dedicated module (parser_maintenance.py was already past the 600L soft cap)
- **Config:** `ArbConfig` added to `src/gzkit/config.py`, wired into `GzkitConfig.load()` with round-trip support
- **Schemas:** `data/schemas/arb_lint_receipt.schema.json`, `arb_step_receipt.schema.json` (schema IDs `gzkit.arb.lint_receipt.v1` / `gzkit.arb.step_receipt.v1`)
- **Dependency:** `jsonschema>=4.23` added to `pyproject.toml`
- **Tests added (all Red → Green, TDD discipline):**
  - `tests/arb/test_schemas.py` (4 tests)
  - `tests/arb/test_paths.py` (4 tests)
  - `tests/arb/test_ruff_reporter.py` (4 tests)
  - `tests/arb/test_step_reporter.py` (5 tests)
  - `tests/arb/test_validator.py` (7 tests)
  - `tests/arb/test_advisor.py` (6 tests)
  - `tests/arb/test_patterns.py` (6 tests)
  - `tests/commands/test_arb_cmd.py` (9 tests)
  - `tests/test_parser_arb.py` (4 tests)
  - `tests/test_config.py::TestArbConfig` (5 new tests)
  - **Total: 54 new tests, all green**
- **Behave:** `features/arb.feature` (6 scenarios, reuses existing `gz_steps.py` step library)
- **Docs:** `docs/user/commands/arb.md`, `docs/user/manpages/arb.md`, updated `docs/user/commands/index.md` with ARB section, updated `docs/user/runbook.md` Heavy-lane attestation flow
- **Rule:** `.gzkit/rules/arb.md` bumped 1.0 → 1.1, added `gz arb patterns` verb, updated last-reviewed date
- **Skill:** `.gzkit/skills/gz-arb/SKILL.md` revived from retired to active, with revival note citing this OBPI; propagated to `.claude/skills/gz-arb/` via `gz agent sync control-surfaces`
- **Out of scope (explicitly deferred):** `gz arb tidy` retention pruning, `gz arb ruff --file-issue` GitHub integration, airlineops `supabase_sync.py`, retrofitting prior attestations to cite real receipts

## Value Narrative

Before this OBPI, `.gzkit/rules/arb.md` v1.0 documented a full `gz arb` CLI surface as "Active" while the infrastructure did not exist. `.claude/rules/attestation-enrichment.md` required ARB receipt IDs as fail-closed evidence for every Heavy-lane claim, but the tool to produce them was vaporware. Every prior Heavy-lane OBPI in ADR-0.25.0 was attested without real receipt IDs because there was no way to produce them — the rule was an obligation the repository could not satisfy.

After this OBPI, `gz arb ruff`, `gz arb step`, `gz arb ty`, `gz arb coverage`, `gz arb validate`, `gz arb advise`, and `gz arb patterns` are real CLI verbs with schema-validated receipts, Pydantic-modeled result shapes, and first-class documentation. The first attestation in the repository to honestly satisfy the attestation-enrichment rule is this OBPI's own Stage 4 ceremony — ADR-0.25.0 closes by citing receipts emitted from the CLI surface it just created. ARB is no longer airline-internal infrastructure that gzkit nominally claimed to have; it is gzkit infrastructure that matches the rule, the runbook, the skill, and the ADR's integration-point list all at once.

### Key Proof


Run each of these after checkout to verify the absorption is complete:

```bash
uv run gz arb --help                                  # 7 verbs listed
uv run gz arb ruff --help                             # verb reachable
uv run gz arb validate                                # returns "ARB Receipt Validation / Receipts scanned: 0"
uv run gz arb advise --limit 5                        # returns "ARB Advice / ..."
uv run gz arb patterns --compact                      # returns "arb patterns: ..."

# Red→Green evidence
uv run -m unittest tests.arb -v                       # 36 ARB package tests pass
uv run -m unittest tests.commands.test_arb_cmd -v     # 9 CLI dispatcher tests pass
uv run -m unittest tests.test_parser_arb -v           # 4 parser registration tests pass
uv run -m unittest tests.test_config.TestArbConfig -v # 5 config round-trip tests pass
uv run -m behave features/arb.feature                 # 6 behave scenarios pass

# Self-referential dog-fooding
uv run gz arb ruff src/gzkit/arb tests/arb src/gzkit/commands/arb.py
uv run gz arb step --name unittest -- uv run -m unittest tests.arb tests.commands.test_arb_cmd
uv run gz arb validate --limit 10
uv run gz arb advise --limit 10
```

## Evidence

### Gate 1 (ADR)

- Intent captured verbatim from ADR-0.25.0 checklist item #33 (brief line 15) and the integration-point list (ADR line 64)
- Scope aligned with ADR Heavy lane and the Absorb / Confirm / Exclude contract
- ALLOWED PATHS amended in Stage 2 Step 0 to cover the full port surface (schemas, docs, features, rules, skills)

### Gate 2 (TDD)

- 54 new tests across 11 test modules, every module authored Red first then Green
- `uv run -m unittest tests.arb tests.commands.test_arb_cmd tests.test_parser_arb tests.test_config.TestArbConfig` — all green (Stage 3 evidence)
- Coverage: existing ≥40% floor maintained (no coverage regression; new modules each have direct test coverage)

### Gate 3 (Docs)

- `docs/user/commands/arb.md` — full command reference with 7 verbs, exit codes, schemas, examples
- `docs/user/manpages/arb.md` — man-style reference per `.gzkit/rules/cli.md` heavy-lane contract
- `docs/user/commands/index.md` — new "ARB (Agent Self-Reporting)" section added
- `docs/user/runbook.md` — Heavy-lane attestation flow updated with Step 4b instructing receipt production before attestation
- `.gzkit/rules/arb.md` — version bump 1.0 → 1.1, last-reviewed date updated to 2026-04-14, `gz arb patterns` verb added
- `uv run mkdocs build --strict` — green (Stage 3 evidence)

### Gate 4 (BDD)

- `features/arb.feature` — 6 scenarios: help-surface coverage, validate zero-state, advise zero-state, patterns zero-state, patterns compact mode, validate JSON output
- `uv run -m behave features/arb.feature` — all 6 scenarios pass (Stage 3 evidence)

### Gate 5 (Human)

- Pending Stage 4 ceremony (Heavy lane requires explicit human attestation)

### Code Quality (ARB dog-fooding — receipts emitted from the surface this OBPI just absorbed)

The first attestation evidence in this repository to satisfy `.claude/rules/attestation-enrichment.md` honestly. All receipts validated via `uv run gz arb validate --limit 20` (Receipts scanned: 5, Valid: 5, Invalid: 0):

- **ARB ruff lint receipt:** `artifacts/receipts/arb-ruff-c768f2cdb4804ba499b0b7d4d5a74c02.json` — `exit_status: 0, findings_total: 0` against `src/gzkit/arb/`, `src/gzkit/commands/arb.py`, `src/gzkit/cli/parser_arb.py`, `tests/arb/`, `tests/commands/test_arb_cmd.py`, `tests/test_parser_arb.py`
- **ARB typecheck step receipt:** `artifacts/receipts/arb-step-typecheck-6f1a8de443a3409a8dd7402402e4891c.json` — `exit_status: 0` (uvx ty check clean on the same scope)
- **ARB unittest step receipt:** `artifacts/receipts/arb-step-unittest-arb-full-15093fb206b34847b73ea5ce8749ff09.json` — `exit_status: 0, 54 tests run, OK`
- **ARB mkdocs step receipt:** `artifacts/receipts/arb-step-mkdocs-aea79ae8f8104d2a85bc5772e4bba6bb.json` — `exit_status: 0` (mkdocs build --strict green)
- **Validation report:** all 5 receipts conform to `gzkit.arb.lint_receipt.v1` / `gzkit.arb.step_receipt.v1` schemas

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — Absorb decision executed: airlineops/opsdev/arb/ ported to gzkit as a 7-module package, 7-verb CLI surface (commands/arb.py + cli/parser_arb.py new dedicated module), 2 Draft 2020-12 JSON schemas with gzkit.arb.*.v1 IDs, ArbConfig added to GzkitConfig, 54 Red-then-Green tests across 11 modules, 6 behave scenarios in features/arb.feature, docs/user/commands/arb.md + manpages/arb.md + runbook Heavy-lane flow update, .gzkit/rules/arb.md bumped 1.0 to 1.1, gz-arb skill revived from retired to active. Forensic root cause confirmed via git log -S: commit 37c891ca copied the airlineops arb rule wholesale, commit 4700b623 mechanical opsdev-to-gzkit find-and-replace without implementation. First attestation in the repository to honestly satisfy the attestation-enrichment rule. ARB receipts dog-fooded from the surface this OBPI just created: lint arb-ruff-96af31501b1e40f09ce8afd77ac93bbe, typecheck arb-step-typecheck-5cd0e1da148b4b82b938e55c9c917879, tests arb-step-unittest-arb-full-865bd7c0ce074b77bf1f92d2bd81df6e, mkdocs arb-step-mkdocs-a3947f56aa1d4887802607414708ea4c. All 4 validated via gz arb validate. Reconciled ADR-0.27.0 sibling collision: 9 of 13 briefs cross-referenced as absorbed under OBPI-0.25.0-33; 06/07/08/09 pending with Logfire telemetry-sync design preserved in 09. GHI #152 filed for plan-audit cross-ADR scope-collision check.
- Date: 2026-04-15

## Closing Argument

`airlineops/src/opsdev/arb/` is a ~1039-line package across seven core files (`advise.py`, `validate.py`, `patterns.py`, `paths.py`, `ruff_reporter.py`, `step_reporter.py`, `__init__.py`) that implements agent self-reporting middleware — wrap any QA command, emit a schema-validated JSON receipt, aggregate recent receipts into actionable lint-pattern guidance. gzkit had none of this: `uv run gz arb` was an invalid CLI choice, `data/schemas/arb_*.json` did not exist, `src/gzkit/arb/` was not a package. And yet `.gzkit/rules/arb.md` v1.0 Active documented the full seven-verb surface, and `.claude/rules/attestation-enrichment.md` hardened its receipt-ID requirement to fail-closed for Heavy-lane attestations — a rule contract the repository could not fulfill.

The forensic trace is unambiguous: a control-surface regeneration on 2026-03-15 (commit `37c891ca`) copied the airlineops arb rule wholesale into gzkit, a mechanical find-and-replace on 2026-03-18 (commit `4700b623`) rewrote `opsdev` → `gzkit` in an auto-commit whose message carried no semantic signal, and the attestation-enrichment hardening (commits `4c7573fc`, `f350cf44`) was written against the phantom surface without verification. The later 2026-04-03 skill consolidation marked `gz-arb` as retired/"consolidated into gz-check" — but `gz check` never implemented any of it. The consolidation was nominal; the drift was substantive.

This OBPI closes the vacuum by making the rule real. `src/gzkit/arb/` is now a proper gzkit package (Pydantic `BaseModel(frozen=True, extra="forbid")`, `pathlib.Path`, `encoding="utf-8"`, typed `GzkitConfig.arb` section). `src/gzkit/commands/arb.py` dispatches seven CLI verbs with deterministic exit codes (0 success, 1 command failure, 2 ARB internal). `src/gzkit/cli/parser_arb.py` registers the verbs in the main parser tree as a dedicated module because `parser_maintenance.py` was already past the 600L soft cap. `data/schemas/arb_lint_receipt.schema.json` and `arb_step_receipt.schema.json` carry the Draft 2020-12 contracts with gzkit schema IDs. 54 tests across 11 test modules enforce Red→Green discipline. `features/arb.feature` provides Gate 4 behavioral proof with 6 scenarios. `docs/user/commands/arb.md`, `docs/user/manpages/arb.md`, and `docs/user/runbook.md` satisfy the Gate 5 runbook-code covenant. `.gzkit/rules/arb.md` is bumped 1.0 → 1.1 with the new `patterns` verb and a truthful last-reviewed date. `.gzkit/skills/gz-arb/SKILL.md` is revived from retired to active with a revival note citing this OBPI.

The Absorb decision is doctrinally correct — ADR-0.25.0 line 64 pre-declared `src/gzkit/arb/` as an integration point, the subtraction test favors absorption (ARB is not airline-specific), and both the attestation rule and the rule contract are non-executable without this surface. The consequence is that every future Heavy-lane attestation in this repository can honestly satisfy the attestation-enrichment receipt-ID requirement — and the first such attestation is this OBPI's own Stage 4 ceremony, citing receipts from the very surface it just created. ADR-0.25.0 closes by eating its own dog food.

**ADR-0.27.0 collision (discovered 2026-04-14 during Stage 4 demonstration).** The operator surfaced a sibling ADR — `ADR-0.27.0-arb-receipt-system-absorption`, status Proposed, 0/13 — which was intended to perform the same absorption as 13 separate per-module OBPIs. Twelve of ADR-0.27.0's briefs are skeletal decision-brief templates (~60 lines each, boilerplate Objective/Source/Requirements/Quality Gates with `*To be authored at completion from delivered evidence.*` placeholder closing arguments). The sole exception is `OBPI-0.27.0-09-arb-telemetry-sync`, which contains genuine architectural design work: a pivot from the opsdev Supabase approach to **Pydantic Logfire** as the L3 retention backend, with state-doctrine alignment (Logfire as derived/rebuildable L3, ledger.jsonl as L2 source of truth), TOML configuration model, env overrides (`GZKIT_TELEMETRY_ENABLED`, `LOGFIRE_TOKEN`), graceful-degradation contract (`ImportError` → no-op emitter), and free-tier volume estimate (10M spans/month, ~10-20 spans per pipeline run). OBPI-0.25.0-33 did **not** implement this Logfire work and did **not** displace it.

The reconciliation: ADR-0.27.0 OBPIs 01/02/03/04/05/10/11/12/13 have been retroactively annotated with `Decision: Absorb (executed under OBPI-0.25.0-33)` cross-references preserving the per-module audit trail ADR-0.27.0's structure intended. Each of the 9 cross-referenced briefs now records which concrete gzkit file implements it (e.g., OBPI-0.27.0-01 → `src/gzkit/arb/ruff_reporter.py`), which Red→Green tests cover it, which dog-food receipts prove it, and how it differs from the opsdev source (schema rename, Pydantic conversion, path resolution via `get_project_root()`, drop of airlineops-infra imports, ruff binary vs. module invocation). ADR-0.27.0 OBPIs 06 (tidy), 07 (expunge), 08 (github-issues), and 09 (telemetry-sync/Logfire) remain `Pending` as legitimate follow-up work — none were implemented under OBPI-0.25.0-33, and OBPI-0.27.0-09 specifically preserves design thinking that deserves its own implementation pass with `logfire` added as an optional dependency and telemetry span emission from each wrapped step.

The collision surfaced a defect in the plan-audit surface (tracked as **GHI #152**): `/gz-plan-audit` checks ADR ↔ OBPI ↔ Plan alignment for the named OBPI, but does not cross-reference against sibling ADRs for scope collisions. If it had, ADR-0.27.0 would have been surfaced during OBPI-0.25.0-33's Stage 1 context load and the work could have been routed to its correct ADR home from the start. The governance lesson is that `Absorb` decisions in ADR-0.25.0 (the Tier 1 core-infrastructure pattern-harvest ADR) must cross-check against any Tier 2 dedicated-absorption ADRs that exist for the same opsdev module — ADR-0.25.0 is Tier 1 and ADR-0.27.0 is Tier 2 (per line 25 of each ADR's "Area" header), and the two-tier structure means OBPIs can scope-collide across tiers when operators run them in isolation.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.25.0 line 64 integration point + line 139-140 checklist item #33 captured verbatim.
- [x] **Gate 2 (TDD):** Tests pass — 54 new tests across 11 modules, Red→Green discipline per module.
- [x] **Gate 3 (Docs):** Decision rationale completed with forensic trace, comparison table, value narrative, and closing argument.
- [x] **Gate 4 (BDD):** Behavioral proof present — `features/arb.feature` 6 scenarios pass.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.
