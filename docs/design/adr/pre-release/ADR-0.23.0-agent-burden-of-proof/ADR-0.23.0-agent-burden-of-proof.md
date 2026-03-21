<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.23.0 — Agent Burden of Proof at ADR Closeout

## Tidy First Plan

Prep tidyings (behavior-preserving):

1. Audit the existing closeout ceremony skill to catalog which checks are automated vs manual-checklist
1. Review the OBPI brief template's Value Narrative section to understand current expectations
1. Inventory `closeout_cmd()` in `cli.py` and `quality.py` for documentation-related gates

State how prep → change → polish: Prep is research-only (no code). Changes are incremental per OBPI.
STOP/BLOCKERS if the closeout command structure requires refactoring beyond additive changes — propose minimal tidying first.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.23.0
**Area:** Governance — Closeout & Attestation Ceremony

## Agent Context Frame — MANDATORY

**Role:** Governance architect strengthening the closeout ceremony to enforce operator-facing evidence quality.

**Purpose:** When an ADR closes, the human attestor receives a compelling case — built from delivered evidence — that each increment actually serves the operator. The agent must earn closure, not declare it.

**Goals:**

- Value narratives are authored at closeout from delivered evidence, not echoed from planning briefs
- Product proof (runbook entry, manpage, docstring) is a blocking closeout gate
- A separate reviewer agent validates delivered work against OBPI promises with fresh eyes
- The closeout ceremony enforces these requirements, making rubber-stamp closure impossible

**Critical Constraint:** Implementations MUST ensure the burden of proof falls on the completing agent at the END of the run. No closeout can succeed by merely declaring "I'm done" — the agent must present evidence that impresses a skeptical human attestor.

**Anti-Pattern Warning:** A failed implementation looks like: adding more checklist items that agents can mechanically tick without engaging with the substance of what was delivered. The trap is "more checkboxes = more rigor." True rigor comes from requiring the agent to articulate — from evidence — why the delivered work matters to the operator, and having a separate agent challenge that articulation.

**Integration Points:**

- `src/gzkit/cli.py` — `closeout_cmd()` (lines ~2286-2505)
- `src/gzkit/quality.py` — quality check functions
- `src/gzkit/commands/common.py` — `_render_adr_closeout_form()` (lines ~448-593)
- `.claude/skills/gz-adr-closeout-ceremony/SKILL.md` — ceremony skill definition
- `.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md` — brief template (Value Narrative section)
- `src/gzkit/commands/pipeline.py` — OBPI pipeline dispatch (reviewer agent role)

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract changed: closeout ceremony behavior, CLI closeout output, OBPI brief template (Heavy lane)
  - CLI `gz closeout` gains new product-proof validation steps
- Config & calendars
  - No config/calendar changes
- Registry & resolvers
  - No registry changes
- Warehouse & lineage
  - No warehouse changes
- Tests
  - Unit tests for product proof detection logic
  - BDD for closeout ceremony with product proof gate
- Docs
  - Closeout manpage updated with new product-proof requirements
  - Governance runbook updated with reviewer agent protocol
  - OBPI brief template updated: Value Narrative section becomes Closing Argument
- Ops ergonomics
  - `gz closeout ADR-X.Y.Z` shows value narratives and product proof status before prompting attestation
  - Failure modes: missing runbook entry, missing manpage, empty value narrative
- OBPI mapping
  - 4 OBPIs, 1:1 with feature checklist areas

## Intent

Establish that ADR closeout is a **defense**, not a declaration. The completing agent bears the burden of proving — through delivered evidence, operator documentation, and a value narrative written from the merits of actual work — that each product increment serves the operator. A separate reviewer agent provides adversarial scrutiny before human attestation.

## Decision

- The OBPI Value Narrative section is renamed "Closing Argument" and must be authored at completion time from delivered evidence, not copied from planning intent
- `gz closeout` validates product proof (runbook entry, manpage, or public docstring) for each OBPI before proceeding
- The OBPI pipeline dispatches a reviewer agent with fresh context to verify delivered work against OBPI promises
- The closeout ceremony skill blocks on missing product proof and requires the reviewer's assessment before human attestation

### Decision Justification (Alternatives Considered)

**Alternative 1 — More checklist items.** Add documentation checkboxes to the existing ceremony. Rejected: this is the anti-pattern. ADR-0.15.0 had a complete checklist (all items ticked) but its Summary Deltas still read "TBD" and its completion table contained only "Diff link" placeholders at attestation time. More boxes did not produce more substance.

**Alternative 2 — Human-only review.** Rely entirely on the human attestor to catch weak docs. Rejected: at scale, agents present too much material for a human to independently verify every claim. The reviewer agent acts as a first-pass adversarial filter, surfacing discrepancies before the human sees them.

**Alternative 3 — Automated prose quality scoring.** Use NLP metrics to grade documentation quality. Rejected: over-engineered for the current need. The reviewer agent provides qualitative judgment without introducing a scoring system that agents would optimize for mechanically.

**Exemplar precedent:** ADR-0.12.0 (obpi-pipeline-enforcement-parity) demonstrates what strong closeout evidence looks like — concrete post-attestation ceremony with recorded commands, explicit operator-facing value narratives with before/after framing, and specific CLI verification examples in every brief. This ADR formalizes ADR-0.12.0's approach as a requirement rather than a best practice.

## Interfaces

- **CLI (external contract):** `uv run gz closeout ADR-X.Y.Z`
  - New output: value narrative summary per OBPI, product proof status table
  - New validation: product proof gate (exit 1 if missing)
- **Ceremony skill:** Updated checklist with blocking product proof and reviewer assessment sections
- **OBPI brief template:** "Value Narrative" → "Closing Argument" with earned-evidence framing

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.23.0-01 | Value narrative becomes closing argument — earned from delivered evidence, not echoed from planning | Lite | Pending |
| 2 | OBPI-0.23.0-02 | Product proof gate — automated runbook/manpage/docstring checks block closeout | Heavy | Pending |
| 3 | OBPI-0.23.0-03 | Reviewer agent role — fresh-eyes verification of delivered work against OBPI promises | Heavy | Pending |
| 4 | OBPI-0.23.0-04 | Ceremony skill enforcement — closeout skill blocks on missing product proof and reviewer assessment | Heavy | Pending |

**Briefs location:** `briefs/OBPI-0.23.0-*.md`

**WBS Completeness Rule:** Every row in this table MUST have a corresponding brief file.

**Parallelization:** OBPIs 01, 02, and 03 are fully independent and can execute in parallel. OBPI 04 depends on all three (integrator role). Critical path = max(01, 02, 03) + 04, not 01 + 02 + 03 + 04.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

---

## Rationale

Agentic coding creates a systemic bias toward "code complete = done." Agents optimize for passing tests and satisfying gates, not for operator comprehension. The current closeout ceremony has a manual documentation checklist that agents can satisfy superficially — files exist, headings are present, but the operator still doesn't understand the increment.

**Cautionary exemplar — ADR-0.15.0 (pydantic-schema-enforcement):** This ADR was attested and validated, yet its Summary Deltas still read "TBD", its completion checklist contained only "Diff link" placeholders, and no operator runbook entries were updated. Every gate passed. Every checklist box was ticked. The operator got nothing they could use. This is the failure mode this ADR prevents.

**Strong exemplar — ADR-0.12.0 (obpi-pipeline-enforcement-parity):** By contrast, ADR-0.12.0 recorded concrete post-attestation ceremony steps, operator-facing value narratives with before/after capability framing, specific CLI verification commands in every brief, and explicit failure-closed requirements. An operator reading ADR-0.12.0's closeout can immediately understand what changed and how to verify it. This ADR codifies ADR-0.12.0's discipline as a requirement.

This ADR inverts the burden: the agent must **prove** its work serves the operator, not merely assert it. The value narrative becomes a closing argument written from evidence. Product proof becomes a blocking gate. And a separate reviewer agent — with fresh context and no sunk-cost bias — challenges the completing agent's claims.

This aligns with the multi-agent architecture (ADR-0.18.0) where specialized agents handle distinct phases, and with the principle that governance exists to protect the human's ability to understand and control the system.

### Lite-Lane Applicability

This ADR applies to **both** Lite and Heavy lanes, with proportional rigor:

- **Lite-lane ADRs:** Closing arguments and product proof (docstrings on public interfaces) are required. Reviewer agent assessment is advisory (warning if absent, not blocking). The ceremony presents evidence but does not require Gate 5 human attestation.
- **Heavy-lane ADRs:** Full enforcement — closing arguments, product proof (runbook/manpage/docstring), reviewer agent assessment, and human attestation all required and blocking.
- **Rationale:** Even internal changes deserve operator comprehension. A Lite refactoring that changes public module APIs without updating docstrings is a silent contract break.

## Consequences

- Closeout takes longer: agents must write substantive closing arguments and pass product proof checks
- The reviewer agent adds a second opinion before human attestation, reducing rubber-stamp risk
- OBPI brief template changes require a clear migration path:
  - **Completed/Validated OBPIs:** No migration — existing Value Narratives stand as-is
  - **In-progress OBPIs (Accepted status):** Agent writes a Closing Argument section at completion; existing Value Narrative can remain as planning context
  - **New OBPIs (created after this ADR):** Use the updated template with Closing Argument section; no Value Narrative section
  - **Template compatibility:** The brief template retains a comment explaining the rename for agents encountering older briefs
- Operators gain confidence that each increment is documented and comprehensible

## Non-Goals (Explicit Exclusions)

1. **Retroactive migration of completed OBPIs.** Completed/Validated briefs with Value Narrative sections are not rewritten. The cost exceeds the benefit — those ADRs are already attested.
2. **Automated prose quality scoring.** No NLP metrics, readability scores, or style enforcement on closing arguments. Quality judgment belongs to the reviewer agent and the human attestor, not a formula.
3. **Replacing human attestation.** The reviewer agent informs the human's judgment; it does not replace it. The human attestor retains final authority.
4. **Scope expansion to non-closeout phases.** This ADR governs closeout and attestation only. Planning-phase briefs, implementation workflow, and gate verification are out of scope.
5. **Changing the attestation response format.** The existing Completed / Completed-Partial / Dropped response vocabulary is unchanged.

**Guardrails against scope creep:** If implementation touches `closeout_cmd()` logic beyond the product-proof gate (e.g., refactoring gate orchestration), split that work into a separate OBPI or defer to ADR-0.19.0 (closeout-audit-processes).

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_product_proof.py`, `tests/test_closeout_enhanced.py`
- **BDD (external contract changed):** `features/closeout_product_proof.feature`
- **Docs:** `docs/user/commands/closeout.md`, `docs/governance/governance_runbook.md`

---

## OBPI Acceptance Note (Human Acknowledgment)

Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note in the brief once Four Gates are green.

`uv run gz closeout ADR-0.23.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.23.0`
- **Related issues:** (to be filed if defects found)

### Source & Contracts

- CLI / contracts: `src/gzkit/cli.py`
- Core modules: `src/gzkit/quality.py`, `src/gzkit/commands/common.py`, `src/gzkit/commands/pipeline.py`
- Skills: `.claude/skills/gz-adr-closeout-ceremony/SKILL.md`
- Templates: `.github/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md`

### Tests

- Unit: `tests/test_product_proof.py`, `tests/test_closeout_enhanced.py`
- BDD: `features/closeout_product_proof.feature`, `features/steps/closeout_product_proof_steps.py`

### Docs

- Commands: `docs/user/commands/closeout.md`
- Governance: `docs/governance/governance_runbook.md`
- Manpages: `docs/user/manpages/closeout.md`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD
- Notes: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors (observable, reproducible) | Evidence (link/snippet/hash) | Notes |
| --- | --- | --- | --- | --- |
| OBPI brief template | M | Closing Argument section replaces Value Narrative | Template diff | |
| `gz closeout` CLI | M | Product proof gate blocks closeout on missing docs | CLI output | |
| Reviewer agent dispatch | P | Separate agent validates work against promises | Pipeline trace | |
| Ceremony skill | M | Blocks on missing product proof and reviewer assessment | Skill diff | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. ...

1. ...
