---
id: OBPI-0.0.39-01-rule-and-doctrine
parent: ADR-0.0.39-llm-as-judge-doctrine
item: 1
lane: Heavy
status: Draft
allowlist:
- docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/**
- .gzkit/rules/llm-as-judge.md
- docs/governance/advisory-rules-audit.md
- docs/user/runbook.md
- docs/governance/governance_runbook.md
- tests/governance/test_llm_as_judge_rule.py
reqs:
- REQ-0.0.39-01-01
- REQ-0.0.39-01-02
- REQ-0.0.39-01-03
- REQ-0.0.39-01-04
- REQ-0.0.39-01-05
- REQ-0.0.39-01-06
- REQ-0.0.39-01-07
- REQ-0.0.39-01-08
- REQ-0.0.39-01-09
verification:
- uv run gz validate --documents
- uv run gz validate --advisory-scorecard
- uv run gz lint
- uv run gz typecheck
- uv run -m unittest tests/governance/test_llm_as_judge_rule.py -v
- uv run gz agent sync control-surfaces
- uv run mkdocs build --strict
---

# OBPI-0.0.39-01-rule-and-doctrine: LLM-as-Judge Rule and Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/ADR-0.0.39-llm-as-judge-doctrine.md`
- **Checklist Item:** #1 — `rule-and-doctrine` — Author `.gzkit/rules/llm-as-judge.md`; register in advisory-rules-audit scorecard as Mechanical with forward-reference to ADR-0.0.40 validators; declare own `surface_axis: authoritative`.

**Status:** Draft

## Objective

Author the canonical foundation rule codifying the LLM-as-judge doctrine — the four inherited invariants from ADR-pool.advisory-judge-surface (never-gate, paired-with-floor, reproducibility-receipt, bounded-scope) plus the five survey-aligned invariants (three-axis declaration, named bias roster, methodology menu, explanation-precedes-verdict output discipline, meta-evaluation cadence). Register the rule in `docs/governance/advisory-rules-audit.md` as **Mechanical** with forward-references to the ADR-0.0.40 validators that will fire on its invariants. Declare the rule's own `surface_axis: authoritative` per ADR-0.0.38's body-marker convention. Update operator and governance runbooks with the judge-classification protocol.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/**` — parent ADR package
- `.gzkit/rules/llm-as-judge.md` (new) — canonical rule file
- `docs/governance/advisory-rules-audit.md` — scorecard registration
- `docs/user/runbook.md` — operator runbook entry for judge surface classification protocol
- `docs/governance/governance_runbook.md` — governance runbook entry for judge surface classification protocol
- `tests/governance/test_llm_as_judge_rule.py` (new) — REQ-derived assertions on rule shape

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/governance/judge_invocation.py` — Pydantic model is OBPI-0.0.39-02's scope
- `src/gzkit/schemas/judge_invocation.json` — JSON Schema is OBPI-0.0.39-02's scope
- `artifacts/audits/judge-surface-classification-*.md` — classification audit is OBPI-0.0.39-03's scope
- Existing skill or runtime tool surface axis declarations — backfill is OBPI-0.0.39-03's scope
- New dependencies
- CI files, lockfiles

## Creates These Files

- `.gzkit/rules/llm-as-judge.md` — **CREATE** canonical rule file with the doctrine invariants
- `tests/governance/test_llm_as_judge_rule.py` — **CREATE** REQ-derived assertions on rule shape

Existing files modified: `docs/governance/advisory-rules-audit.md` (scorecard registration), `docs/user/runbook.md`, `docs/governance/governance_runbook.md`.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `.gzkit/rules/llm-as-judge.md` exists with body-level rule version marker `<!-- rule-version: 0.1.0 -->` and visible block-quote version line, per `.gzkit/rules/skill-surface-sync.md` v0.2.0.
2. REQUIREMENT: The rule file declares the four inherited invariants (never-gate, paired-with-floor, reproducibility-receipt, bounded-scope) carried forward from ADR-pool.advisory-judge-surface unchanged.
3. REQUIREMENT: The rule file declares the five survey-aligned invariants — Invariant 5 (three-axis what/how/where), Invariant 6 (named bias roster + mitigations), Invariant 7 (methodology menu with rationale-of-choice), Invariant 8 (explanation-precedes-verdict output discipline), Invariant 9 (meta-evaluation cadence) — with the same definitions as the parent ADR § Decision.
4. REQUIREMENT: The rule file declares its own `<!-- surface-axis: authoritative -->` body marker per ADR-0.0.38 OBPI-0.0.38-01's declaration convention.
5. REQUIREMENT: For each of the nine invariants, the rule file names the mechanical witness — which validator scope or schema field will enforce it, and which OBPI under ADR-0.0.40 will land that witness. Forward-references are explicit (the OBPI ID), not generic ("a future validator").
6. REQUIREMENT: The rule file enumerates the bias roster with the survey paper's classification: **position bias** (pairwise/list-wise contexts), **verbosity bias** (length-variable contexts), **self-preference bias** (judge family ⇄ candidate family), **preference leakage** (training-relationship lineage), **calibration drift** (over-time agreement). Each bias names its default mitigation per the parent ADR § Decision § Invariant 6 table.
7. REQUIREMENT: The rule file enumerates the methodology menu with the survey paper's classification: single-grading, pairwise, list-wise, reference-based, criteria-decomposed, ensemble, red-team-challenge. Each methodology names "when appropriate" and "rationale shape" per the parent ADR § Decision § Invariant 7 table.
8. REQUIREMENT: The rule file declares the explanation-precedes-verdict mechanical floor: prompts elicit explanation before verdict; receipt fields ordered explanation_text-then-verdict; receipts with verdict populated but explanation_text empty are rejected at emit time; trivial explanations (length < 50 chars default) are flagged.
9. REQUIREMENT: The rule file declares the meta-evaluation cadence floor: every N=100 verdicts (configurable), human-agreement sample is taken; Cohen's kappa default; floor 0.6 (Landis-Koch substantial) configurable in `data/judge_meta_eval_floor.json`; metric NEVER itself a gate.
10. REQUIREMENT: `docs/governance/advisory-rules-audit.md` is updated with a new entry classifying `llm-as-judge.md` as **Mechanical**, naming the validator scopes that will fire on its invariants (`gz validate --judge-leakage`, `gz validate --judge-output-discipline`, `judge meta-eval`) and the OBPIs under ADR-0.0.40 that will land them.
11. REQUIREMENT: `docs/user/runbook.md` adds a new section under "Operator workflows" describing how an operator interprets a judge verdict (read explanation first; verify methodology declaration; check bias-mitigation receipt fields; never treat verdict as gate).
12. REQUIREMENT: `docs/governance/governance_runbook.md` adds a new section under "Foundation-rule maintenance" describing how a maintainer adds a new what/how/where axis enum value or a new bias to the roster (foundation-kind ADR amendment required).
13. REQUIREMENT: `tests/governance/test_llm_as_judge_rule.py` asserts: (a) rule file exists at canonical path; (b) version marker shape; (c) all nine invariants enumerated with forward-references to mechanical witnesses; (d) self-classification as `authoritative`; (e) bias roster covers all five named biases; (f) methodology menu covers all seven named methodologies. Assertions are semantic, not byte-level.
14. REQUIREMENT: `gz agent sync control-surfaces` runs cleanly after the rule lands; mirrors update without divergence.
15. REQUIREMENT: NEVER author the Pydantic `JudgeInvocation` model, the JSON Schema, or the receipt validator extension in this OBPI — those are OBPI-0.0.39-02's scope.
16. REQUIREMENT: NEVER backfill axis declarations on existing judge surfaces (`gz-adr-evaluate --red-team`, runtime `advisor()`, `gz-complexity-distill`) in this OBPI — that is OBPI-0.0.39-03's scope.

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
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/rules/llm-as-judge.md`
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
uv run gz validate --documents
uv run gz validate --advisory-scorecard
uv run gz lint
uv run gz typecheck

# OBPI-specific tests
uv run -m unittest tests/governance/test_llm_as_judge_rule.py -v

# Sync control surfaces (verify rule mirrors land cleanly)
uv run gz agent sync control-surfaces

# Heavy-lane gates
uv run mkdocs build --strict

# Confirm canonical artifacts exist
test -f .gzkit/rules/llm-as-judge.md
test -f .claude/rules/llm-as-judge.md
grep -q "llm-as-judge" docs/governance/advisory-rules-audit.md
grep -q "judge surface classification" docs/user/runbook.md
grep -q "judge surface classification" docs/governance/governance_runbook.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.39-01-01: Given the parent ADR § Decision § "Inherited foundation invariants", when the rule file is read, then all four inherited invariants (never-gate, paired-with-floor, reproducibility-receipt, bounded-scope) are enumerated unchanged.
- [ ] REQ-0.0.39-01-02: Given the parent ADR § Decision § "Survey-aligned invariants", when the rule file is read, then all five survey-aligned invariants (Invariants 5–9) are enumerated with their mechanical witnesses named and forward-referenced to ADR-0.0.40 OBPIs.
- [ ] REQ-0.0.39-01-03: Given the rule body, when the body marker is parsed, then the file declares `<!-- surface-axis: authoritative -->`.
- [ ] REQ-0.0.39-01-04: Given the bias roster section, when read, then five biases are named (position, verbosity, self-preference, preference leakage, calibration drift) each with default mitigation matching the parent ADR § Invariant 6 table.
- [ ] REQ-0.0.39-01-05: Given the methodology menu section, when read, then seven methodologies are named (single-grading, pairwise, list-wise, reference-based, criteria-decomposed, ensemble, red-team-challenge) with "when appropriate" and "rationale shape" per the parent ADR § Invariant 7 table.
- [ ] REQ-0.0.39-01-06: Given `docs/governance/advisory-rules-audit.md`, when read, then the new entry classifies `llm-as-judge.md` as **Mechanical** and names the three ADR-0.0.40 validator scopes (`--judge-leakage`, `--judge-output-discipline`, `judge meta-eval`).
- [ ] REQ-0.0.39-01-07: Given `gz agent sync control-surfaces`, when run after the rule lands, then mirrors at `.claude/rules/llm-as-judge.md` and `.github/instructions/llm-as-judge.md` are produced with body-content parity.
- [ ] REQ-0.0.39-01-08: Given the runbook entries, when read, then `docs/user/runbook.md` describes operator-side judge-verdict interpretation and `docs/governance/governance_runbook.md` describes the foundation-rule amendment protocol for adding axes/biases.
- [ ] REQ-0.0.39-01-09: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no `judge_invocation.py` Pydantic model, no JSON Schema, and no axis backfill on existing judge surfaces are added.

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
