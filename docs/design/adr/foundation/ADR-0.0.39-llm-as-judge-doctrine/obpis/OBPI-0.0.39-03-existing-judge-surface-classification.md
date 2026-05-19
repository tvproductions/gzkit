---
id: OBPI-0.0.39-03-existing-judge-surface-classification
parent: ADR-0.0.39-llm-as-judge-doctrine
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.39-03-existing-judge-surface-classification: Existing Judge Surface Classification

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/ADR-0.0.39-llm-as-judge-doctrine.md`
- **Checklist Item:** #3 — `existing-judge-surface-classification` — Classify every existing LLM-as-judge surface; emit `judge_surface_classified` ledger event per surface; produce `artifacts/audits/judge-surface-classification-2026-05-06.md` baseline; mark dependent pool ADRs as governed-by-ADR-0.0.39.

**Status:** Draft

## Objective

One-time audit pass: enumerate every existing LLM-as-judge surface in gzkit (`gz-adr-evaluate --red-team`, runtime `advisor()` tool, `gz-complexity-distill` advisor verdicts, and any other surface that issues an LLM judgment), classify each under ADR-0.0.39's three-axis taxonomy with cited rationale anchors, document the bias profile and current-mitigation gap (the gap will be closed under ADR-0.0.40's retrofit OBPI), emit `judge_surface_classified` ledger events, produce the canonical baseline audit at `artifacts/audits/judge-surface-classification-2026-05-06.md`, mark dependent pool ADRs (`attestation-advisory-agent`, `lightweight-pre-implementation-challenger`) as governed-by-ADR-0.0.39 in their frontmatter, and walk the operator through Gate 5 confirmation of every classification.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/**` — parent ADR package
- `data/judge_surface_inventory.json` (new) — frozen Pydantic-serialized snapshot of the inventory; machine-readable mirror of the audit. Note: a human-readable baseline audit document at `artifacts/audits/judge-surface-classification-2026-05-06.md` is also produced; it lives outside the validator-tracked path prefixes by convention
- `tests/governance/test_judge_surface_baseline.py` (new) — REQ-derived assertions on completeness and consistency
- `docs/design/adr/pool/ADR-pool.attestation-advisory-agent.md` — add `governed_by: ADR-0.0.39-llm-as-judge-doctrine` frontmatter
- `docs/design/adr/pool/ADR-pool.lightweight-pre-implementation-challenger.md` — add `governed_by: ADR-0.0.39-llm-as-judge-doctrine` frontmatter
- `.gzkit/schemas/ledger_events.json` — register `judge_surface_classified` event family

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/rules/llm-as-judge.md` — authored under OBPI-0.0.39-01; this OBPI may not edit it
- `src/gzkit/governance/judge_invocation.py` — landed under OBPI-0.0.39-02; this OBPI may not modify the schema
- `src/gzkit/schemas/judge_invocation.json` — landed under OBPI-0.0.39-02
- `src/gzkit/arb/validator.py` — landed under OBPI-0.0.39-02; this OBPI may not modify ARB integration
- `src/gzkit/commands/adr_evaluate.py` red-team path — retrofit to populate JudgeInvocation receipt fields is OBPI-0.0.40-05's scope, NOT here. This OBPI documents the current bias profile + gap; it does NOT close the gap.
- `CLAUDE.md` § Advisor Tool — bias-profile documentation update is OBPI-0.0.40-05's scope
- `data/judge_leakage_waivers.json` — historical waiver backfill is OBPI-0.0.40-05's scope
- New runtime dependencies
- CI files, lockfiles

## Creates These Files

- `data/judge_surface_inventory.json` — **CREATE** Pydantic-serialized snapshot of the inventory (the human-readable audit at `artifacts/audits/judge-surface-classification-2026-05-06.md` is also produced but lives outside the validator-tracked prefixes by convention)
- `tests/governance/test_judge_surface_baseline.py` — **CREATE** REQ-derived assertions on completeness/consistency
- `.gzkit/schemas/ledger_events.json` — **CREATE** (or extend if present) registry entry for `judge_surface_classified` event family

Existing files modified: `docs/design/adr/pool/ADR-pool.attestation-advisory-agent.md` (add `governed_by` frontmatter), `docs/design/adr/pool/ADR-pool.lightweight-pre-implementation-challenger.md` (add `governed_by` frontmatter).

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Every existing LLM-as-judge surface in gzkit is enumerated and classified. The initial inventory MUST include at least: (a) `gz-adr-evaluate --red-team`; (b) `gz-adr-evaluate` 8-dim ADR rubric scoring + 5-dim OBPI rubric scoring; (c) runtime `advisor()` tool; (d) `gz-complexity-distill` advisor verdicts. The audit pass discovers any additional judge surfaces by grep + skill-frontmatter scan and adds them to the inventory.
2. REQUIREMENT: For each classified surface, the audit document records: `surface_path`, `surface_kind` (skill/code/runtime-tool/other), `what_axis`, `how_axis`, `where_axis`, `methodology`, `judge_model_family`, `candidate_provenance` (typical pairing observed in the corpus), `bias_profile` (which biases from the canonical roster apply), `current_mitigation_state` (which mitigations are already applied vs which are missing), `rationale_anchor` (file:line citation), `governed_by` (this ADR-0.0.39 by default).
3. REQUIREMENT: The `current_mitigation_state` column MUST honestly enumerate gaps. For example: `gz-adr-evaluate --red-team` likely has NO position-bias mitigation today (single-pass, no order randomization); the audit records that gap, and the gap is OBPI-0.0.40-05's retrofit target. Concealing or under-describing a gap is a doctrine violation per AGENTS.md § Prime Directive (defects must be trackable).
4. REQUIREMENT: For each classified surface, a `judge_surface_classified` ledger event is appended via the canonical event-emit helper (NEVER hand-write to ledger.jsonl). Event payload: `{surface_path, surface_kind, what_axis, how_axis, where_axis, methodology, bias_profile, current_mitigation_state, source_commit}`.
5. REQUIREMENT: The `judge_surface_classified` event family is added to `.gzkit/schemas/ledger_events.json` in this OBPI; the schema validates against the event-payload shape.
6. REQUIREMENT: `data/judge_surface_inventory.json` is a frozen Pydantic-serialized snapshot of the inventory in machine-readable form; same shape as the audit document with a `generated_at` timestamp and a `source_commit` field. Regenerable from the enumeration helper.
7. REQUIREMENT: `ADR-pool.attestation-advisory-agent` frontmatter is updated with `governed_by: ADR-0.0.39-llm-as-judge-doctrine`. The pool ADR remains in pool (not promoted) but its invariants now inherit from this doctrine.
8. REQUIREMENT: `ADR-pool.lightweight-pre-implementation-challenger` frontmatter is updated with `governed_by: ADR-0.0.39-llm-as-judge-doctrine`. Same as #7.
9. REQUIREMENT: `tests/governance/test_judge_surface_baseline.py` asserts: (a) the baseline audit row count matches the inventory JSON; (b) every classified surface has non-empty `bias_profile` and `current_mitigation_state` fields; (c) the JSON inventory regenerates byte-identically; (d) the count of `judge_surface_classified` ledger events matches the audit row count; (e) the two governed-by-tagged pool ADRs carry the frontmatter field.
10. REQUIREMENT: Gate 5 attestation is mandatory (parent ADR foundation-kind heavy). Operator walkthrough at OBPI close MUST include: (a) operator quotes the bias-profile of `gz-adr-evaluate --red-team` and confirms which biases are currently un-mitigated; (b) operator quotes the bias-profile of runtime `advisor()` and confirms whether same-family judging is the current default; (c) operator confirms that `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` pool ADRs are correctly marked as governed-by-ADR-0.0.39. Attestation text cites the audit document by path and one canonical-step ARB receipt name (`arb-step-judge-classification-baseline-*` reserved under OBPI-0.0.39-02).
11. REQUIREMENT: NEVER close mitigation gaps in this OBPI — the retrofit (populating JudgeInvocation receipt fields on `gz-adr-evaluate --red-team`, documenting `advisor()`'s bias profile, backfilling historical waivers) is OBPI-0.0.40-05's scope. This OBPI records the gaps; ADR-0.0.40 closes them.
12. REQUIREMENT: NEVER classify a surface as "compliant" if its current mitigation state has any gap relative to the bias profile that applies. Gaps are recorded honestly; the audit's purpose is the snapshot, and ADR-0.0.40-05's retrofit is the close.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/ADR-0.0.39-llm-as-judge-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/ADR-0.0.39-llm-as-judge-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `artifacts/audits/judge-surface-classification-2026-05-06.md`
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
uv run -m unittest tests/governance/test_judge_surface_baseline.py -v

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run gz validate --advisory-scorecard
uv run mkdocs build --strict
uv run -m behave features/

# ARB receipt for attestation
uv run gz arb step --name judge-classification-baseline -- echo "baseline classification audit"

# Confirm canonical artifacts exist
test -f artifacts/audits/judge-surface-classification-2026-05-06.md
test -f data/judge_surface_inventory.json
test -f tests/governance/test_judge_surface_baseline.py

# Confirm pool ADR frontmatter updates
grep -q "governed_by: ADR-0.0.39" docs/design/adr/pool/ADR-pool.attestation-advisory-agent.md
grep -q "governed_by: ADR-0.0.39" docs/design/adr/pool/ADR-pool.lightweight-pre-implementation-challenger.md

# Confirm ledger events emitted
grep judge_surface_classified .gzkit/ledger.jsonl | wc -l

# Confirm at least four sampled judge surfaces are in the audit
grep -E "gz-adr-evaluate --red-team|advisor\(\)|gz-complexity-distill" artifacts/audits/judge-surface-classification-2026-05-06.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.39-03-01: Given the audit document, when read, then it includes at minimum the four named surfaces (`gz-adr-evaluate --red-team`, `gz-adr-evaluate` rubric scoring, runtime `advisor()`, `gz-complexity-distill`) plus any additional surfaces discovered by enumeration, with every row carrying non-empty axis, methodology, bias_profile, current_mitigation_state, and rationale_anchor.
- [ ] REQ-0.0.39-03-02: Given `data/judge_surface_inventory.json`, when regenerated by the enumeration helper, then the regenerated content is byte-identical to the committed file (excluding `generated_at`).
- [ ] REQ-0.0.39-03-03: Given the ledger after classification, when filtered for `judge_surface_classified` events, then the count matches the audit row count.
- [ ] REQ-0.0.39-03-04: Given `.gzkit/schemas/ledger_events.json`, when read, then `judge_surface_classified` is a registered event family with the documented payload shape.
- [ ] REQ-0.0.39-03-05: Given `ADR-pool.attestation-advisory-agent.md` and `ADR-pool.lightweight-pre-implementation-challenger.md`, when frontmatter is parsed, then both carry `governed_by: ADR-0.0.39-llm-as-judge-doctrine`.
- [ ] REQ-0.0.39-03-06: Given the `current_mitigation_state` column, when read for each surface, then gaps are honestly enumerated (e.g. `gz-adr-evaluate --red-team` lacks order-randomization mitigation today; this is recorded, not concealed).
- [ ] REQ-0.0.39-03-07: Given the Gate 5 walkthrough, when the operator attests, then the attestation text includes (a) bias profile of `gz-adr-evaluate --red-team` with un-mitigated biases named, (b) bias profile of runtime `advisor()` confirming current same-family-default, (c) confirmation of pool ADR frontmatter updates.
- [ ] REQ-0.0.39-03-08: Given the attestation text, when validated, then it cites at least one `arb-step-judge-classification-baseline-*` receipt per AGENTS.md § Attestation.
- [ ] REQ-0.0.39-03-09: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no edits to `src/gzkit/commands/adr_evaluate.py`, no edits to `CLAUDE.md` § Advisor Tool, no waiver-registry additions, and no schema modifications are made — those scopes belong to ADR-0.0.40.
- [ ] REQ-0.0.39-03-10: Given the audit's mitigation-state recording, when reviewed, then no surface is classified as "fully mitigated" if any bias from the applicable roster is un-mitigated. Honest gap-recording is fail-closed.

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
