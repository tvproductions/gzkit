---
id: OBPI-0.0.43-07-legacy-mapping-classification-ratification
parent: ADR-0.0.43-ddd-domain-cascade
item: 7
lane: Heavy
status: Draft
allowlist:
- src/gzkit/governance/legacy_mapping.py
- src/gzkit/schemas/legacy_mapping.json
- src/gzkit/cli/legacy.py
- docs/design/domain/legacy-adr-bc-mapping.yaml.draft
- docs/design/domain/legacy-adr-bc-mapping.yaml
- docs/user/manpages/legacy-classify.md
- docs/user/manpages/legacy-ratify.md
- tests/governance/test_legacy_mapping.py
- tests/cli/test_legacy_classify.py
reqs:
- REQ-0.0.43-07-01
- REQ-0.0.43-07-02
- REQ-0.0.43-07-03
- REQ-0.0.43-07-04
- REQ-0.0.43-07-05
- REQ-0.0.43-07-06
- REQ-0.0.43-07-07
- REQ-0.0.43-07-08
- REQ-0.0.43-07-09
- REQ-0.0.43-07-10
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run mkdocs build --strict
- uv run gz cli audit
- uv run gz legacy classify --dry-run
---

# OBPI-0.0.43-07-legacy-mapping-classification-ratification: Legacy ADR/OBPI/Pool classification + ratification ceremony

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #7 — "Legacy mapping schema + LLM-as-judge classification + ratification ceremony — `LegacyAdrBcMapping` Pydantic; classification driver walks existing ~49 ADRs + ~118 pool entries + completed OBPIs; output to `legacy-adr-bc-mapping.yaml.draft`; ratification ceremony (operator review, corrections, accept); final file at `docs/design/domain/legacy-adr-bc-mapping.yaml`; validator dual-mode."

**Status:** Draft

## Objective

Walk the existing corpus (canonical ADRs + pool ADRs + completed OBPIs), agent-classify each to a bounded context using LLM-as-judge, surface the draft for operator ratification, and persist the ratified mapping. Validator dual-mode (frontmatter primary, legacy-mapping fallback) is the seam that lets new artifacts land cleanly while legacy artifacts remain valid without reopening closeout-attested ADRs.

## Lane

**Heavy** — produces a canonical mapping file that is the bridge between the existing corpus and the new cascade. One-way operator-attested decision; reversal would require reclassification ceremony.

## Allowed Paths

- `src/gzkit/governance/legacy_mapping.py` — NEW; loader, validator, classification driver
- `src/gzkit/schemas/legacy_mapping.json` — NEW
- `src/gzkit/cli/legacy.py` — NEW; `gz legacy classify` and `gz legacy ratify` verbs (or fold into `gz domain legacy` — implementation choice; documented in OBPI-12)
- `docs/design/domain/legacy-adr-bc-mapping.yaml.draft` — NEW (eventual, agent-produced)
- `docs/design/domain/legacy-adr-bc-mapping.yaml` — NEW (eventual, operator-ratified)
- `docs/user/manpages/legacy-classify.md` — NEW (or `gz-domain-legacy-classify.md`)
- `docs/user/manpages/legacy-ratify.md` — NEW
- `tests/governance/test_legacy_mapping.py` — NEW
- `tests/cli/test_legacy_classify.py` — NEW

## Denied Paths

- `src/gzkit/governance/domain_models.py` — OBPI-01 / 02 (consume only)
- Other schemas — other OBPI scopes
- `src/gzkit/governance/trust_audits/domain_cascade.py` — OBPI-06 (this OBPI provides the legacy-mapping data; OBPI-06 consumes it)
- `src/gzkit/cli/domain.py` — OBPI-03 (separate `gz legacy` CLI; or namespaced under `gz domain legacy`)
- Existing ADR / OBPI / GHI content files — never retroactively edited (closeout invariant); classification is meta-data, not artifact mutation
- `docs/design/prd/PRD-GZKIT-1.0.0.md` — OBPI-13 (PRD § 2.2 bootstrap comes from this OBPI's ratified mapping, but PRD authoring is OBPI-13 scope)
- `.gzkit/skills/**` — OBPI-08 / 09 / 10
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`LegacyAdrBcMapping` Pydantic).** Class with `schema_version: Literal[1]`, `ratified_by: str`, `ratified_at: date`, `mappings: list[LegacyMappingEntry]`. `extra="forbid"`. `LegacyMappingEntry`: `artifact_id: str`, `bounded_context: str | list[str]`, `confidence: Literal["high", "medium", "low"]`, `evidence: str` (≥1 sentence), `auto_classified: bool`, `ratified: bool`.
2. **REQUIREMENT (`gz legacy classify`).** Walks `docs/design/adr/foundation/**/ADR-*.md`, `docs/design/adr/feature/**/ADR-*.md`, `docs/design/adr/pool/ADR-pool.*.md`, and `docs/design/adr/foundation/**/obpis/OBPI-*.md`. For each artifact, parses intent/decision, sends to LLM-as-judge classifier with a structured prompt requesting one or more BC slugs + confidence + evidence. Writes draft to `docs/design/domain/legacy-adr-bc-mapping.yaml.draft`. Idempotent (re-running overwrites the draft, never the ratified file).
3. **REQUIREMENT (classification prompt — locked).** The LLM-as-judge prompt MUST present the artifact's Intent + Decision + (if ADR) checklist top-3-items. The prompt MUST ask the classifier to choose one or more BC slugs from a candidate list emerging from the corpus itself (no a-priori BC list required). Prompt + few-shot examples land at `src/gzkit/governance/legacy_classification_prompt.md` (NEW under this OBPI's allowed paths).
4. **REQUIREMENT (`gz legacy ratify`).** Operator-interactive ceremony. Walks each entry in `legacy-adr-bc-mapping.yaml.draft`, prints the agent's proposed classification + evidence, prompts for accept / edit / reject. Accepted entries are added to `docs/design/domain/legacy-adr-bc-mapping.yaml` with `ratified: true`. Rejected entries are dropped. Edited entries replace the agent's classification. Final write is atomic. Emits one `legacy_mapping_ratified` event with `count` at end.
5. **REQUIREMENT (classification target ≥70% accuracy on operator spot-check).** OBPI completion evidence MUST include a measurement: operator samples N≥20 artifacts at random from the draft, scores each as correct/incorrect, and reports the accuracy ratio. <70% accuracy = abandon LLM step and author the mapping directly (operator override path; STOP-on-BLOCKERS escape).
6. **REQUIREMENT (validator dual-mode).** OBPI-06's `--domain-cascade` validator MUST consult both frontmatter `bounded_context` (primary) and `legacy-adr-bc-mapping.yaml` (fallback for artifacts without frontmatter). This OBPI exposes the API `gzkit.governance.legacy_mapping.resolve_bc(artifact_id) -> str | None` used by OBPI-06.
7. **REQUIREMENT (one-way promotion).** When a legacy ADR is next modified (frontmatter edit), the operator MAY write `bounded_context` into the frontmatter and remove the legacy-mapping entry. Direction is index → frontmatter, never reverse. No tooling enforces; rule documented in OBPI-12 doctrine page.
8. **REQUIREMENT (no retroactive ADR modification).** This OBPI MUST NOT edit any existing ADR/OBPI/GHI content file. The mapping is metadata external to the artifacts. Closeout-attested artifacts remain attested without modification.
9. **REQUIREMENT (bootstrap BC list).** The set of BC slugs appearing in the ratified mapping IS the canonical input for PRD § 2.2 bootstrap by OBPI-13. This OBPI's ratification ceremony is the BC-discovery step.

> STOP-on-BLOCKERS: if classification accuracy <70% on operator spot-check, abandon the LLM step and author the mapping directly. Document the override in the brief's evidence with the measured accuracy.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #7 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § OBPI Acceptance Protocol — closeout invariant
- [ ] `.gzkit/rules/governance-core.md`
- [ ] `docs/governance/state-doctrine.md`
- [ ] `docs/governance/llm-as-judge-doctrine.md` (if present — ADR-0.0.39)

**Context:**

- [ ] OBPI-01 strategic models landed
- [ ] OBPI-04 frontmatter schemas landed (for the dual-mode contract)
- [ ] Existing corpus: ~49 canonical ADRs + ~118 pool entries + completed OBPIs
- [ ] LLM-as-judge infrastructure (ADR-0.0.39 + ADR-0.0.40 if landed)

**Prerequisites:**

- [ ] OBPI-01 landed
- [ ] LLM-as-judge surface usable (or stubbed for tests; live LLM use deferred to OBPI runtime)

**Existing Code:**

- [ ] Existing ADR/OBPI/GHI parsers in `src/gzkit/governance/`
- [ ] Existing LLM-as-judge prompts (ADR-0.0.39 if landed)

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #7 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] `LegacyAdrBcMapping` schema/model round-trip
- [ ] `gz legacy classify` produces a draft YAML containing every existing ADR / pool / OBPI artifact
- [ ] Idempotence: re-running `classify` overwrites the draft byte-equal
- [ ] `gz legacy ratify` interactive flow tested via subprocess + stdin fixtures (accept all, accept some, edit one, reject one)
- [ ] `resolve_bc(artifact_id)` returns the ratified BC for a known legacy artifact; returns `None` for unknown
- [ ] No existing ADR / OBPI / GHI file is modified during classify or ratify (regression test: file mtime preserved)
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] Two new manpages (`gz-legacy-classify`, `gz-legacy-ratify`) pass `gz cli audit`

### Gate 4: BDD (Heavy only)

- [ ] One BDD scenario: operator runs `gz legacy classify`, reviews draft, runs `gz legacy ratify`, ratification completes, `gz check` passes

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded — operator confirms accuracy spot-check ≥70% (or operator override path documented)
- [ ] Attestor: operator name only (never email per AGENTS.md PII rule)

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz cli audit

uv run gz legacy classify --dry-run
test -f src/gzkit/governance/legacy_mapping.py
test -f src/gzkit/schemas/legacy_mapping.json
```

## Demo

```bash
# Classify the corpus (writes draft only; safe to re-run)
uv run gz legacy classify

# Inspect draft
head -30 docs/design/domain/legacy-adr-bc-mapping.yaml.draft

# Ratify (interactive; operator drives)
uv run gz legacy ratify

# Verify validator dual-mode reads ratified file
uv run python -c "
from gzkit.governance.legacy_mapping import resolve_bc
print(resolve_bc('ADR-0.0.3'))  # expected: governance (or whichever BC was ratified)
"
```

## Acceptance Criteria

- [ ] REQ-0.0.43-07-01: Given `LegacyAdrBcMapping`, when constructed with valid mapping list, then round-trips through JSON Schema
- [ ] REQ-0.0.43-07-02: Given `LegacyAdrBcMapping`, when an entry has invalid `confidence` value, then `ValidationError`
- [ ] REQ-0.0.43-07-03: Given `gz legacy classify`, when run against the current corpus, then draft file contains entries for every ADR / pool / completed OBPI
- [ ] REQ-0.0.43-07-04: Given two consecutive `gz legacy classify` runs with no canon changes, then drafts are byte-equal (idempotence)
- [ ] REQ-0.0.43-07-05: Given `gz legacy ratify` with operator accepting all entries, when ceremony completes, then ratified file written and `legacy_mapping_ratified` event emitted with `count` = total entries
- [ ] REQ-0.0.43-07-06: Given `gz legacy ratify` with operator editing one entry, when ceremony completes, then ratified file reflects the operator's edit, not the agent's draft
- [ ] REQ-0.0.43-07-07: Given `resolve_bc("ADR-0.0.3")` after ratification, when called, then returns the ratified BC slug (e.g., `"governance"`)
- [ ] REQ-0.0.43-07-08: Given `resolve_bc("ADR-unknown")`, when called, then returns `None`
- [ ] REQ-0.0.43-07-09: Given any existing ADR / OBPI / GHI file, when `gz legacy classify` and `gz legacy ratify` run, then file content and mtime are unchanged
- [ ] REQ-0.0.43-07-10: Given operator spot-check of N≥20 classifications, when accuracy is measured, then evidence section records the ratio; if <70%, the override path was taken with documented override

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Clean
- [ ] **Gate 3 (Docs):** mkdocs + cli audit clean
- [ ] **Gate 4 (BDD):** Scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded with accuracy measurement
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs + cli audit output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here, including operator-measured classification accuracy
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`; MUST include measured classification accuracy
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
