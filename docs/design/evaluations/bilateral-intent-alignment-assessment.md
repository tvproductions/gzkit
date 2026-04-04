# Bilateral Intent-Alignment Assessment Framework

**Version:** 1.0
**Date:** 2026-04-04
**Scope:** Whole-project alignment between stated intent and realized surfaces
**Companion:** `governance-chain-evaluation.md` (enforcement depth)

---

## Preamble: Why This Framework Exists

A project that has shipped 34 ADRs and 299 OBPIs is not a greenfield effort following a plan. It is a system shaped by hundreds of locally-rational design decisions that may have collectively shifted the project's center of gravity away from -- or beyond -- the original intent.

Most alignment checks are unilateral: they assume the intent document is correct and look for implementation drift. This framework is **bilateral**. The evaluator is empowered to recommend changes in either direction:

- **Direction A (Align implementation toward intent):** "The PRD says X. The implementation does Y. Y is drift. Fix the implementation."
- **Direction B (Align intent toward implementation):** "The PRD says X. The implementation does Y. Y is actually better -- it emerged from real design pressure and coheres with the rest of the system. Update the PRD."

Both directions are equally valid findings. The evaluator recommends; the operator decides.

### Relationship to the Enforcement Evaluation

The Governance Chain Evaluation Framework (companion document) is a *depth* tool that evaluates enforcement strength on known-critical flows. It takes those flows as given. This framework is the *wide-angle* tool that validates whether the right flows are being evaluated -- and whether the project's actual shape matches its stated shape.

| Concern | This framework | Enforcement evaluation |
|---------|---------------|----------------------|
| Question answered | "Are we building what we said we'd build?" | "Are the things we're building working correctly?" |
| Input | PRD, Lodestar, project surfaces | Known-critical flows, hooks, CLI |
| Output | Alignment findings, directional recommendations | Scores, systemic findings, red-team results |
| Cadence | Strategic inflection points | Per-cycle, before/after major changes |
| Evaluator profile | Benefits from fresh perspective | Benefits from deep system knowledge |

They feed each other:

- This framework might discover that a critical flow is missing from the enforcement evaluation, or that an evaluated flow isn't as critical as assumed.
- The enforcement evaluation might reveal poor enforcement on a stated-critical flow, prompting this framework to ask: "is it poorly enforced because it's not actually important?"

**When both run:** Run this framework first. Its findings may add, remove, or reprioritize the flows that the enforcement evaluation examines.

---

## Part 1: Assessment Framework

### Purpose

This framework assesses alignment between gzkit's stated intent (PRD, Lodestar, architectural identity documents) and its realized surfaces (skills, hooks, CLI, ADRs, governance artifacts). It produces bilateral findings that recommend changes to either the intent documents or the implementation, and identifies emergent capabilities that may warrant formalization.

### Intent Pillars

The evaluator begins by independently reading the intent documents and deriving the project's foundational claims. The following six pillars were derived from the PRD and Lodestar as of 2026-04-04. They should be re-derived by each evaluator -- if an evaluator derives different pillars, that itself is a finding.

| # | Pillar | Source documents | Core claim |
|---|--------|-----------------|------------|
| P1 | **Human sovereignty** | PRD INV-001/002/020, govzero-doctrine SPRINT/DRIFT | The human is index zero: final authority, non-bypassable attestation, ceremonies enforce deliberate slowing |
| P2 | **Schema enforcement** | architectural-identity AI-000/011 | Every artifact is schema-validated. LLMs are loose; gzkit is strict. No drift, no vibes. |
| P3 | **Headless CMS architecture** | architectural-identity AI-001/008 | Canon in `.gzkit/`, rendered mirrors for vendors, never edit generated surfaces |
| P4 | **Append-only event-sourced ledger** | PRD INV-009, govzero-doctrine | Single source of truth; state derived from replay; ledger is immutable |
| P5 | **SPRINT/DRIFT operational rhythm** | govzero-doctrine | Agents sprint (execute fast), humans drift (slow to verify). Ceremonies are drift-enabling. |
| P6 | **AirlineOps canonical origin** | govzero-doctrine, lodestar README | gzkit is governance extracted from AirlineOps; divergence requires explicit ADR authorization |

### Alignment Classification

Each finding is classified on two axes:

**Alignment state:**

| State | Meaning |
|-------|---------|
| **Converged** | Intent and implementation agree. The pillar is realized. |
| **Intent without implementation** | The intent documents promise something the surfaces don't deliver. |
| **Implementation without intent** | A capability exists that works well but isn't described in intent documents. |
| **Tension** | Both intent and implementation exist but pull in different directions. |

**Recommended direction:**

| Direction | Meaning |
|-----------|---------|
| **A -- Align implementation** | The intent is correct; fix the implementation to match. |
| **B -- Align intent** | The implementation is correct (or better); update the intent documents to reflect reality. |
| **C -- Resolve tension** | Both sides have merit; a design decision is needed. |
| **N/A** | Converged; no action needed. |

### Assessment Dimensions

Each pillar is assessed across these five dimensions:

| # | Dimension | Question |
|---|-----------|----------|
| A1 | **Surface coverage** | Do the project's surfaces (skills, hooks, CLI, docs) embody this pillar? |
| A2 | **Enforcement depth** | Where the pillar implies constraints, are they enforced or advisory? |
| A3 | **Consistency** | Does the pillar hold uniformly, or are there exceptions/carve-outs? |
| A4 | **Emergent evolution** | Has the implementation evolved the pillar beyond the original intent? |
| A5 | **Stated boundaries** | Are the pillar's non-goals still respected, or has scope crept? |

---

## Part 2: How to Run the Assessment

### Prerequisites

- Access to the gzkit repository at HEAD
- Read access to `docs/design/prd/`, `docs/design/lodestar/`, `docs/design/adr/`, `.claude/skills/`, `.claude/hooks/`, `src/gzkit/`, `AGENTS.md`
- Familiarity with the PRD and Lodestar is NOT assumed -- the evaluator reads them fresh as Step 1

### Step 1: Derive Intent Pillars Independently

Read these documents in order:

1. `docs/design/lodestar/README.md` (orientation)
2. `docs/design/lodestar/govzero-doctrine.md` (philosophy)
3. `docs/design/lodestar/architectural-identity.md` (architecture)
4. `docs/design/lodestar/foundational-adr-pattern.md` (ADR discipline)
5. `docs/design/lodestar/project-structure.md` (structural claims)
6. `docs/design/prd/PRD-GZKIT-1.0.0.md` (product requirements)

From these, independently derive 4-8 foundational pillars. Each pillar should be a one-sentence claim about what gzkit fundamentally is or does. Compare your derived pillars against the reference set in Part 1.

**If your pillars diverge from the reference set:** Record the divergence as a finding. Either the reference set needs updating, or the intent documents are ambiguous. Do not silently adopt the reference set.

### Step 2: Survey Realized Surfaces

Inventory what actually exists in the project. Do not read intent documents during this step -- survey the implementation on its own terms.

**2a. Skill surface:**

```bash
ls .claude/skills/*/SKILL.md
```

For each skill, note: what it does, what it enforces, what ceremonies it embodies, what it automates.

**2b. Hook surface:**

Read `.claude/settings.json` for PreToolUse/PostToolUse hooks. For each hook, note: what it blocks, what it advises, what it records.

**2c. CLI surface:**

```bash
uv run gz --help
```

For each command group, note: what operations it provides, what gates it enforces, what artifacts it produces.

**2d. ADR landscape:**

```bash
uv run gz status --table
```

Note: distribution across foundation/feature/pool, lane distribution, lifecycle states, OBPI completion rates.

**2e. Governance artifacts:**

Note: what lives in `.gzkit/` (ledger, manifest, config, insights), what lives in `docs/design/`, what lives in vendor directories (`.claude/`, `.github/`).

**2f. Emergent patterns:**

Look for capabilities, conventions, or structures that are well-established in the implementation but that you did not encounter in the intent documents. These are candidates for "implementation without intent" findings.

### Step 3: Assess Each Pillar

For each pillar (your derived set or the reference set), score dimensions A1-A5:

| Pillar | A1: Coverage | A2: Enforcement | A3: Consistency | A4: Evolution | A5: Boundaries |
|--------|:-----------:|:---------------:|:---------------:|:-------------:|:--------------:|
| P1 | | | | | |
| P2 | | | | | |
| ... | | | | | |

Use the alignment states (Converged / Intent-without-impl / Impl-without-intent / Tension) rather than numeric scores. Each cell should cite specific surfaces or artifacts as evidence.

### Step 4: Identify Bilateral Findings

For each non-Converged cell in the matrix, produce a finding:

```
Finding ID: B-{pillar#}-{dimension#}
Pillar: P{n} -- {name}
Dimension: A{n} -- {name}
Alignment state: {state}
Evidence: {what you observed}
Direction A (align implementation): {what would change in code/skills/hooks}
Direction B (align intent): {what would change in PRD/Lodestar}
Recommendation: {A, B, or C with reasoning}
```

### Step 5: Identify Emergent Capabilities

From Step 2f, catalog capabilities that exist in the implementation but have no corresponding intent-document backing. For each:

- Describe what it does and how well it works
- Assess whether it coheres with the stated pillars (even if not explicitly described)
- Recommend: formalize in intent documents (Direction B), or flag as scope creep to evaluate (Direction C)

Emergent capabilities that cohere with pillars and have been validated through use are strong candidates for Direction B (update intent to reflect reality).

### Step 6: Cross-Reference with Enforcement Evaluation

If the Governance Chain Evaluation has been run:

- Do the four chain links map cleanly to the derived pillars? Which pillars do they serve?
- Are there pillars with no chain-link coverage? (These are enforcement blind spots.)
- Are there chain links that serve no pillar? (These may be over-engineered or addressing a concern the intent documents don't prioritize.)

If the enforcement evaluation has NOT been run, note which derived pillars imply critical flows that should be evaluated for enforcement depth.

### Step 7: Classify Actionable Outcomes

Each finding receives an action classification:

**Category I -- Intent Document Updates**

Direction B findings where the implementation is correct and the intent documents should be updated. These are documentation changes to PRD, Lodestar, or architectural identity files.

- Scope: Document edits only
- Sequencing: Can happen anytime; no code dependency
- Decision gate: Operator reviews and approves the updated claims

**Category II -- Implementation Alignment**

Direction A findings where the intent is correct and the implementation should change. These feed into the enforcement evaluation as new findings or into the ADR process as new work.

- Scope: Code, hook, skill, or governance artifact changes
- Sequencing: May require ADR (if external contracts change) or Category A hook fixes (if internal enforcement)
- Decision gate: Operator decides whether to create ADR, add to absorption wave, or defer

**Category III -- Design Decisions Required**

Direction C findings where both sides have merit. These require operator judgment and may result in PRD amendments, new ADRs, or explicit acceptance of the current state.

- Scope: Depends on the decision
- Sequencing: Block other work only if the tension affects active ADRs
- Decision gate: Operator decides direction, then it becomes Category I or II

### Step 8: Synthesis

Produce:

1. The derived pillar set (Step 1) with divergence notes if different from reference
2. The surface inventory summary (Step 2)
3. The pillar assessment matrix (Step 3) with evidence citations
4. The bilateral findings registry (Step 4) with directional recommendations
5. The emergent capabilities catalog (Step 5)
6. The enforcement cross-reference (Step 6, if applicable)
7. The actionable outcomes table (Step 7) with categories and sequencing
8. A clear statement of what should happen next

---

## Part 3: How to Report Results

### Report Structure

```
# Bilateral Intent-Alignment Assessment Report
## Date, Evaluator, Repository State

## 1. Executive Summary
- Number of pillars assessed
- Alignment state distribution (Converged / Intent-without / Impl-without / Tension)
- Number of Direction A vs B vs C recommendations
- Number of emergent capabilities identified
- Top 3 findings

## 2. Derived Pillars
- The evaluator's independently-derived pillar set
- Comparison to reference pillars (divergences noted)
- Rationale for any additions or omissions

## 3. Surface Inventory
- Skill count and categorization
- Hook count and enforcement coverage
- CLI command inventory
- ADR landscape summary
- Emergent pattern notes

## 4. Pillar Assessment Matrix
- Full matrix with alignment states and evidence
- Per-pillar narrative (2-3 sentences)

## 5. Bilateral Findings
- One subsection per finding
- Each contains: pillar, dimension, state, evidence,
  Direction A option, Direction B option, recommendation

## 6. Emergent Capabilities
- Capabilities found in implementation without intent-document backing
- Coherence assessment (does it fit the pillars?)
- Recommendation: formalize or flag

## 7. Enforcement Cross-Reference
- Pillar-to-chain-link mapping (if enforcement evaluation exists)
- Blind spots in both directions

## 8. Actionable Outcomes
### 8a. Category I -- Intent Document Updates
- Table: finding, document to update, proposed change

### 8b. Category II -- Implementation Alignment
- Table: finding, scope, whether ADR-level or fix-level

### 8c. Category III -- Design Decisions Required
- Table: finding, tension description, options, operator decision needed

## 9. Next Actions
- Approved Category I updates
- Category II items routed to enforcement evaluation or ADR process
- Category III decisions pending
- Date for next assessment
```

### Evidence Standards

- Pillar derivation must cite specific document sections, not just document names
- Surface inventory must cite file paths, command outputs, or skill names
- "The implementation feels aligned" is not evidence. Cite the specific skill, hook, or CLI command that embodies the pillar.
- Direction B recommendations (update intent) must argue why the implementation is better than the stated intent -- not just different
- Emergent capability claims must demonstrate the capability works (cite usage in validated ADRs or operational workflow)

### Evaluator Independence

The bilateral assessment benefits from evaluator independence. The evaluator should:

- Read intent documents without prior knowledge of what "the right answer" is
- Survey surfaces without being told which ones matter most
- Derive pillars before seeing the reference set
- Form alignment judgments before reading prior assessment reports

If the evaluator has deep prior context (e.g., the project operator or a regular contributor), they should explicitly note this and flag findings where their prior knowledge may bias the assessment.

### Versioning

- Each assessment is dated and tied to a specific git commit SHA
- The reference pillar set (Part 1) is updated when Direction B findings are accepted
- Findings use stable IDs (B-{pillar}-{dimension}) across assessments
- Resolved findings are marked RESOLVED with the commit or document change that addressed them

### Delivery

The completed report is written to `docs/design/evaluations/` with the naming convention:

```
bilateral-intent-alignment-report-YYYY-MM-DD.md
```

This framework document is updated only when the reference pillar set changes (accepted Direction B findings) or the assessment methodology evolves.
