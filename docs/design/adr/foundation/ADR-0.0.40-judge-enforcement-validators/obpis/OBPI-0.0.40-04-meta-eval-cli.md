---
id: OBPI-0.0.40-04-meta-eval-cli
parent: ADR-0.0.40-judge-enforcement-validators
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.40-04-meta-eval-cli: gz judge meta-eval CLI Verb (Human-Agreement Metric)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
- **Checklist Item:** #4 — `meta-eval-cli` — Implement `gz judge meta-eval` (Evidentiary axis CLI verb): Cohen's kappa over a sampled window with configurable floor; ledger event; receipt prefix; manpage + runbook.

**Status:** Draft

## Objective

Implement `gz judge meta-eval` as a new top-level CLI verb classified Evidentiary per ADR-0.0.38. The command takes `--window <start-ts> <end-ts>` (receipt corpus window) and `--human-attestations <path>` (operator-sampled human verdicts on a subset of those receipts), computes Cohen's kappa (default; alternatives via `--metric krippendorffs-alpha` or `--metric fleiss-kappa`) measuring agreement between judge verdicts and human verdicts, emits a `judge_meta_eval` ledger event recording the metric, sample size, window timestamps, and metric choice. Reads the configurable floor from `data/judge_meta_eval_floor.json` (default kappa=0.6 per Landis-Koch substantial-agreement). The metric NEVER itself a gate — when below floor, the surface is flagged in `gz status` as drift-suspect; the operator decides remediation. Manpage + runbook entries land per gate5-runbook-code-covenant.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/**` — parent ADR package
- `src/gzkit/commands/judge_meta_eval.py` (new) — command implementation
- `src/gzkit/governance/judge_metrics.py` (new) — metric computation (Cohen's kappa, Krippendorff's alpha, Fleiss' kappa)
- `src/gzkit/cli/parser_judge.py` (new) — `gz judge` subcommand parser
- `src/gzkit/cli/__init__.py` or active dispatcher — register `gz judge` top-level verb
- `data/judge_meta_eval_floor.json` (new) — frozen Pydantic-validated floor configuration
- `.gzkit/schemas/ledger_events.json` — register `judge_meta_eval` event family
- `tests/commands/test_judge_meta_eval.py` (new) — REQ-derived assertions
- `tests/governance/test_judge_metrics.py` (new) — metric-computation correctness assertions
- `features/governance/judge_meta_eval.feature` (new) — BDD scenarios tagged `@REQ-0.0.40-04-NN`
- `docs/user/manpages/gz-judge.md` (new) — manpage for `gz judge meta-eval`
- `docs/user/runbook.md` — operator workflow entry
- `docs/governance/governance_runbook.md` — governance-maintainer workflow entry

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/arb/validator.py`, `src/gzkit/arb/middleware.py` — OBPI-0.0.40-01's scope
- `src/gzkit/governance/judge_invocation.py`, `src/gzkit/schemas/judge_invocation.json` — OBPI-0.0.39-02's
- `src/gzkit/governance/judge_leakage.py`, `data/judge_leakage_waivers.json`, `data/judge_model_families.json` — OBPI-0.0.40-02's
- `src/gzkit/governance/judge_output_discipline.py` — OBPI-0.0.40-03's
- `src/gzkit/commands/adr_evaluate.py` — retrofit is OBPI-0.0.40-05's
- `CLAUDE.md` § Advisor Tool — OBPI-0.0.40-05's scope
- New runtime dependencies (note: scipy or numpy may already be a dependency; verify before importing — if not, the metric computation must use stdlib `statistics` or be implemented from first principles)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz judge meta-eval` is registered as a new top-level CLI verb structure (`gz judge` is the namespace; `meta-eval` is the subcommand) at `src/gzkit/cli/parser_judge.py`, dispatching to `src/gzkit/commands/judge_meta_eval.py`. The verb classification is `axis: evidentiary` per ADR-0.0.38.
2. REQUIREMENT: The command accepts: `--window <start-iso8601> <end-iso8601>` (REQUIRED), `--human-attestations <path>` (REQUIRED, path to JSON or JSONL file with sampled human verdicts), `--metric {cohens-kappa,krippendorffs-alpha,fleiss-kappa}` (default `cohens-kappa`), `--surface <surface-id>` (OPTIONAL, filters to a specific judge surface; default scans all), `--json` (machine-readable output).
3. REQUIREMENT: The human-attestations file format is documented and validated. Schema (Pydantic): `HumanAttestationSet(records: list[HumanAttestationRecord])` where `HumanAttestationRecord(receipt_id: str, human_verdict: str, attestor: str, attestation_timestamp: str)`. Each record's `receipt_id` MUST match a receipt in the receipt corpus within the window; non-matching records fail-close with a diagnostic.
4. REQUIREMENT: `judge_metrics.py` defines pure functions: `compute_cohens_kappa(judge_verdicts: list[str], human_verdicts: list[str]) -> float`, `compute_krippendorffs_alpha(...)`, `compute_fleiss_kappa(...)`. Each function is implemented from first principles using stdlib `statistics` (no scipy unless already a dependency); each is tested against published reference values from the literature.
5. REQUIREMENT: `data/judge_meta_eval_floor.json` is a frozen Pydantic-validated floor configuration. Schema: `MetaEvalFloor(metric: str, floor_value: float, applied_to_surface: str | None, cited_authority: str)`. Default entries: kappa=0.6 (Landis-Koch substantial agreement) for `*` (all surfaces); operators may override per surface.
6. REQUIREMENT: A `judge_meta_eval` ledger event is emitted for each invocation. Event payload: `{metric_name, metric_value, sample_size, window_start, window_end, surface, floor_value, below_floor: bool, source_commit, timestamp}`. The event family is registered in `.gzkit/schemas/ledger_events.json`.
7. REQUIREMENT: An ARB receipt with prefix `arb-step-judge-meta-eval-*` is emitted under canonical-step provenance per the slot reserved in OBPI-0.0.40-01.
8. REQUIREMENT: When the computed metric is below the floor, the command exits 0 (Evidentiary; never gate-binding) BUT the output explicitly marks "below_floor=True" and the next `gz status` call reflects "drift-suspect" classification on the surface. The drift-suspect status is informational, not gating.
9. REQUIREMENT: When the receipt corpus in the window has fewer than 10 receipts OR the human-attestation set has fewer than 5 records, the command emits a `sample_too_small` warning and recommends a larger window or more samples. The metric is still computed but flagged as low-confidence in the diagnostic.
10. REQUIREMENT: `tests/governance/test_judge_metrics.py` asserts each metric function returns published reference values for at least three documented test cases per metric (e.g., Cohen's 1960 paper's worked examples). Numerical tolerance ≤ 1e-6.
11. REQUIREMENT: `tests/commands/test_judge_meta_eval.py` asserts: (a) clean run produces the documented output and ledger event; (b) missing required flags fail with usage error; (c) malformed human-attestations file fails with schema diagnostic; (d) below-floor case marks `below_floor=True` and exits 0; (e) sample-too-small case warns but completes; (f) `--metric` switch selects alternative metrics correctly.
12. REQUIREMENT: `features/governance/judge_meta_eval.feature` covers the cases above. Tags `@REQ-0.0.40-04-NN`.
13. REQUIREMENT: `docs/user/manpages/gz-judge.md` is authored with EXAMPLES section showing real CLI output for both above-floor and below-floor cases. Runbook entries added per gate5-runbook-code-covenant.
14. REQUIREMENT: `gz cli audit` and `gz validate --cli-alignment` exit 0 with `gz judge meta-eval` appearing in manpage + command doc index + SKILL coverage roster.
15. REQUIREMENT: Pythonic size limits per `.gzkit/rules/pythonic.md` — each metric function and each command branch fits within ≤50 lines.
16. REQUIREMENT: NEVER let the metric become a fail-closed gate. Adding an `--enforce-floor` flag that exits 3 when below floor is a doctrine violation per ADR-0.0.39 § Invariant 9 — the metric is **NEVER** itself a gate.
17. REQUIREMENT: NEVER add scopes / verbs / files outside this OBPI's allowlist. ARB middleware (-01), leakage validator (-02), output-discipline validator (-03), and retrofit (-05) are out of scope.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
- [ ] Required path exists or is intentionally created in this OBPI: `data/judge_meta_eval_floor.json`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
# OBPI-specific tests
uv run -m unittest tests/governance/test_judge_metrics.py -v
uv run -m unittest tests/commands/test_judge_meta_eval.py -v

# BDD scenarios (Gate 4)
uv run -m behave features/governance/judge_meta_eval.feature

# CLI alignment + manpage coverage
uv run gz cli audit
uv run gz validate --cli-alignment
uv run gz judge meta-eval --help

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run mkdocs build --strict

# ARB-wrapped receipt for attestation (uses fixture human-attestation set)
uv run gz arb step --name judge-meta-eval -- uv run gz judge meta-eval --window 2026-01-01T00:00:00 2026-05-06T23:59:59 --human-attestations tests/fixtures/judge_meta_eval/sample.json

# Confirm canonical artifacts
test -f src/gzkit/commands/judge_meta_eval.py
test -f src/gzkit/governance/judge_metrics.py
test -f data/judge_meta_eval_floor.json
test -f docs/user/manpages/gz-judge.md
test -f features/governance/judge_meta_eval.feature
grep -q "judge_meta_eval" .gzkit/schemas/ledger_events.json
grep -q "gz judge meta-eval" docs/user/runbook.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.40-04-01: Given a valid `--window` and `--human-attestations` file, when `uv run gz judge meta-eval` runs, then it computes Cohen's kappa (default), prints metric value + sample size + below-floor status, and exits 0.
- [ ] REQ-0.0.40-04-02: Given Cohen's 1960 worked example inputs, when `compute_cohens_kappa` is called, then the returned value matches the published reference within 1e-6 tolerance.
- [ ] REQ-0.0.40-04-03: Given Krippendorff's documented test data, when `compute_krippendorffs_alpha` is called via `--metric krippendorffs-alpha`, then the result matches reference within 1e-6.
- [ ] REQ-0.0.40-04-04: Given Fleiss' >2-rater reference data, when `compute_fleiss_kappa` is called via `--metric fleiss-kappa`, then the result matches reference within 1e-6.
- [ ] REQ-0.0.40-04-05: Given a malformed `--human-attestations` file (missing required field), when the command runs, then it exits 1 (User/Config Error) with a Pydantic schema diagnostic.
- [ ] REQ-0.0.40-04-06: Given the metric is below the floor, when the command completes, then exit code is 0 (Evidentiary), output marks `below_floor=True`, and the ledger event records `below_floor: true`.
- [ ] REQ-0.0.40-04-07: Given a corpus window with fewer than 10 receipts, when the command runs, then a `sample_too_small` warning is printed and the metric is computed but flagged low-confidence.
- [ ] REQ-0.0.40-04-08: Given `--json` flag, when the command runs, then stdout is JSON-parseable with shape `{metric_name, metric_value, sample_size, window: {start, end}, surface, floor_value, below_floor: bool, sample_too_small: bool}`.
- [ ] REQ-0.0.40-04-09: Given the ledger after a successful run, when filtered for `judge_meta_eval` events, then the most recent event matches the documented payload schema.
- [ ] REQ-0.0.40-04-10: Given `data/judge_meta_eval_floor.json`, when read, then it validates against `MetaEvalFloor` schema with at least one default entry (kappa=0.6 for `*`).
- [ ] REQ-0.0.40-04-11: Given `gz cli audit` and `gz validate --cli-alignment`, when run, then both exit 0 with `gz judge meta-eval` in manpage + command doc index + SKILL coverage.
- [ ] REQ-0.0.40-04-12: Given the Pythonic size-limit rule (≤50 lines/function), when `uv run gz lint` runs, then each metric function and command branch fits within the limit.
- [ ] REQ-0.0.40-04-13: Given the never-a-gate requirement, when source is read, then no `--enforce-floor` flag exists; the metric is informational only.
- [ ] REQ-0.0.40-04-14: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no edits to ARB middleware (-01's), no `--judge-leakage`/`--judge-output-discipline` scopes (-02/03's), no `adr_evaluate.py` retrofit (-05's), no `CLAUDE.md` updates.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
