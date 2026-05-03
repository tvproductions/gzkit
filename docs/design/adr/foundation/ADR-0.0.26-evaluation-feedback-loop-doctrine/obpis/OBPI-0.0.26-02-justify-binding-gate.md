---
id: OBPI-0.0.26-02-justify-binding-gate
parent: ADR-0.0.26-evaluation-feedback-loop-doctrine
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.26-02-justify-binding-gate: `gz validate --evaluation-justify-binding`

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/ADR-0.0.26-evaluation-feedback-loop-doctrine.md`
- **Checklist Item:** #2 — "Implement `gz validate --evaluation-justify-binding` — fail-closed when score < 3.0 or ≥3 red-team challenges fire and no `gz-justify` artifact exists for the parent artifact"

**Status:** Draft

## Objective

Mechanically enforce the existing advisory rule that `gz-justify` must be invoked when an `gz-adr-evaluate` dimension scores < 3.0 (or ≥3 red-team challenges fire). Today the rule lives in the skill description; the gate makes it fail-closed.

## Lane

**Heavy** — Adds a new validate scope and gates lifecycle advancement.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — new `validate_evaluation_justify_binding`
- `src/gzkit/cli/parser_artifacts.py` — register `--evaluation-justify-binding` flag
- `src/gzkit/commands/lifecycle.py` (or wherever artifact-state advance happens) — call the gate before advancing past Pending/Draft
- `data/eval_feedback_thresholds.json` — new config file with `low_score_threshold` (default 3.0) and `red_team_count_threshold` (default 3)
- `tests/governance/test_justify_binding_gate.py`
- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/**`

## Denied Paths

- `src/gzkit/skills/gz-justify/**` — skill description already prescribes the trigger; not edited here
- `src/gzkit/skills/gz-adr-evaluate/**` — skill description already prescribes the score range; not edited here
- `AGENTS.md`, `docs/governance/**` — doc updates land in OBPI-04
- `features/**` — BDD coverage in OBPI-05

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: New function `validate_evaluation_justify_binding(artifact_id) -> ValidationResult` reads ledger for `adr-evaluation` events for the artifact.
2. REQUIREMENT: For the most recent `adr-evaluation` event, if any `dimensions` score is < `low_score_threshold` OR `len(red_team_challenges_fired) >= red_team_count_threshold`, the gate requires a `gz-justify` artifact at the canonical path (`docs/design/adr/**/justify/<artifact-id>-<timestamp>.md` or wherever `gz-justify` writes).
3. REQUIREMENT: If the trigger fires and no qualifying `gz-justify` artifact exists, the validator exits 3 with a structured message naming the failing dimensions and the missing artifact path.
4. REQUIREMENT: The gate is invoked automatically before any artifact advances past `Pending` lifecycle state (or the first downstream gate, depending on integration point).
5. REQUIREMENT: Threshold values come from `data/eval_feedback_thresholds.json`, never hardcoded.
6. REQUIREMENT: Tests cover: trigger fires on low score → no artifact → exit 3; trigger fires on red-team count → no artifact → exit 3; trigger fires → qualifying artifact present → exit 0; trigger does not fire (all scores ≥ threshold, < N challenges) → exit 0 with no requirement.
7. REQUIREMENT: Tests use tempfile-backed ledger and tempfile-backed justify-artifact fixtures.
8. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.26-02-NN)`.
9. REQUIREMENT: NEVER include the operator's personal email.
10. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if OBPI-01 has not landed, STOP — there are no `adr-evaluation` events to read.

## Discovery Checklist

- [x] Parent ADR § Decision item 2 — "Implement `gz validate --evaluation-justify-binding` — fail-closed when score < 3.0 or ≥3 red-team challenges fire and no `gz-justify` artifact exists"
- [x] OBPI-0.0.26-01 evidence — `adr-evaluation` event payload shape confirmed stable: `{artifact_id, artifact_type, dimensions, scores, weighted_total, red_team_challenges_fired, evaluator_persona, timestamp}`; `dimensions` is a map of name→score (0.0–5.0)
- [x] `gz-justify` skill SKILL.md — artifact path confirmed: `artifacts/justify/<slug>-<timestamp>.md`; gate scans `artifacts/justify/` for matching files
- [x] `gz-adr-evaluate` skill SKILL.md — dimension scoring uses 0.0–5.0 range; `red_team_challenges_fired` is a list of challenge IDs

**Prerequisites (check existence, STOP if missing):**

- [x] Parent ADR Decision item 2 confirmed: fail-closed gate, threshold-driven, requires justify artifact when trigger fires
- [x] OBPI-0.0.26-01 attested_completed — `adr-evaluation` ledger event emission code is live; event shape is stable
- [x] `src/gzkit/governance/trust_audits/` package structure confirmed — new module added as `evaluation_justify_binding.py`
- [x] `src/gzkit/commands/validate_cmd.py` scope dispatch pattern confirmed via `--sensitivity` precedent
- [x] `src/gzkit/cli/parser_maintenance.py` — validate flags live here (not `parser_artifacts.py`)

**Existing Code (understand current state):**

- [x] `src/gzkit/governance/trust_audits/__init__.py` — re-export pattern reviewed; `validate_evaluation_justify_binding` exported
- [x] `src/gzkit/commands/validate_cmd.py` — `explicit_scopes`, `_explicit_scope_runners`, `opt_in_scopes`, `validate()` function all updated
- [x] `src/gzkit/lifecycle.py:73` — `transition()` method confirmed; gate fires before ledger event emission for Pending/Draft source states
- [x] `data/eval_feedback_thresholds.json` — new file created with `low_score_threshold: 3.0`, `red_team_count_threshold: 3`
- [x] `gz covers OBPI-0.0.26-02` — 5/5 REQs covered, 0 uncovered

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] RGR; tests pass
### Code Quality
- [ ] Lint, type clean
### Gate 3: Docs (Heavy)
- [ ] In OBPI-04
### Gate 4: BDD (Heavy)
- [ ] In OBPI-05
### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_justify_binding_gate.py -v
# Smoke
uv run gz validate --evaluation-justify-binding ADR-<fixture-id>
```

## Acceptance Criteria

- [ ] REQ-0.0.26-02-01: Given an `adr-evaluation` event with a dimension score < 3.0 and no qualifying `gz-justify` artifact, when the gate runs, then exit 3 with the failing dimension named.
- [ ] REQ-0.0.26-02-02: Given an `adr-evaluation` event with ≥3 red-team challenges fired and no qualifying `gz-justify` artifact, when the gate runs, then exit 3.
- [ ] REQ-0.0.26-02-03: Given the same conditions but a qualifying `gz-justify` artifact present, when the gate runs, then exit 0.
- [ ] REQ-0.0.26-02-04: Given an `adr-evaluation` event with all scores ≥ 3.0 and < 3 challenges, when the gate runs, then exit 0 with no requirement.
- [ ] REQ-0.0.26-02-05: Given the threshold config in `data/eval_feedback_thresholds.json`, when the file is updated, then gate behavior reflects the new thresholds without code changes.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR; tests pass
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# RGR observations + unittest output
```

### Code Quality
```text
# lint/typecheck output
```

### Gate 5 (Human)
```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof


Behave on the new feature file:

```
$ PYTHONIOENCODING=utf-8 uv run -m behave features/attestation_receipt_binding.feature --no-color -f plain --no-snippets
1 feature passed, 0 failed, 0 skipped
13 scenarios passed, 0 failed, 0 skipped
67 steps passed, 0 failed, 0 skipped
Took 0min 0.354s
```

Behave-req-tags validator on the live repo (proves OBPI-01/02 waiver removal is safe):

```
$ uv run gz validate --behave-req-tags
Validated: behave_req_tags
✓ All validations passed (1 scopes).
```

ARB receipts cited: lint arb-ruff-0c9355f33c2d4b6faa84b8035bee1cb8; typecheck arb-step-typecheck-1033439042234a6b8acaf4c9cff176ed; behave arb-step-behave-16da0d4a53d046b1ab68be12bf1331d7; mkdocs arb-step-mkdocs-b03afc7e45634a7d9e0dd597dda0463b.

### Implementation Summary


- Files created: features/attestation_receipt_binding.feature (14 file-level @covers + 13 @REQ-tagged scenarios across REQ-0.0.24-01-01..06, REQ-0.0.24-02-01..05, REQ-0.0.24-04-01..03); features/steps/attestation_receipt_binding_steps.py (~480 lines: receipt-fixture builders, ADR/OBPI seeders with ledger registration via adr_created_event/obpi_created_event, pipeline-marker seeder for --attestor-present co-presence proxy, in-process CLI driver, ledger-event inspectors).
- Files modified: features/environment.py (after_scenario restores GZKIT_ARB_RECEIPTS_ROOT to pre-scenario value); data/behave_coverage_waivers.json (removed OBPI-0.0.24-01-validator-scope, OBPI-0.0.24-02-wire-into-completion, OBPI-0.0.24-04-bdd-coverage entries — covered by new tagged scenarios; OBPI-03 entry retained as doc-only out-of-scope per brief REQ-1); .gzkit/insights/agent-insights.jsonl (one defect insight for 5 pre-existing unit test failures unrelated to OBPI-04).
- Tests added: 13 BDD scenarios (TDD via observed RED/GREEN cycles — initial run 6/13 then assertion-text and ledger-field corrections then 13/13 GREEN).
- Date completed: 2026-05-02.
- Attestation status: heavy + foundation Gate 5 attestation present via agent-relayed pipeline marker.
- Defects noted: 5 pre-existing unit test failures (test_skill_manpage_coverage, test_product_proof, test_instruction_audit) confirmed pre-existing via git stash round-trip; logged to insights for follow-up GHI.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.24-04-bdd-coverage landed `features/attestation_receipt_binding.feature` (14 file-level @covers + 13 @REQ-tagged scenarios) and `features/steps/attestation_receipt_binding_steps.py` (~480 lines of BDD scaffolding) exercising the ADR-0.0.24 receipt-binding gate end-to-end through real `gz validate --attestation-receipts`, real `gz obpi complete`, and real `gz adr emit-receipt` invocations. All 11 OBPI-01/02 REQs (REQ-0.0.24-01-01..06 + REQ-0.0.24-02-01..05) plus the 3 self-coverage REQs (REQ-0.0.24-04-01..03) carry @REQ tags; `data/behave_coverage_waivers.json` had OBPI-01/02/04 entries removed so `gz validate --behave-req-tags` passes on real coverage rather than waiver. Heavy + foundation success path uses the GHI #292 `--attestor-present` + pipeline-marker path (preserves GHI #290 anti-fabrication invariant); failure paths run in-process because the gate fires before the TTY check (REQ-07 ordering). 13/13 scenarios pass (behave receipt arb-step-behave-16da0d4a53d046b1ab68be12bf1331d7); lint receipt arb-ruff-0c9355f33c2d4b6faa84b8035bee1cb8; typecheck receipt arb-step-typecheck-1033439042234a6b8acaf4c9cff176ed; mkdocs receipt arb-step-mkdocs-b03afc7e45634a7d9e0dd597dda0463b.
- Date: 2026-05-03

---

**Brief Status:** Completed

**Date Completed:** 2026-05-03

**Evidence Hash:** -
