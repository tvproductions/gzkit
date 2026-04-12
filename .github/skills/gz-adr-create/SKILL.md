---
name: gz-adr-create
persona: main-session
description: Create and book a GovZero ADR with its OBPI briefs. Enforces minor-version odometer and five-gate compliance. Portable skill for GovZero-compliant repositories.
category: adr-lifecycle
compatibility: Requires GovZero v6 framework; provides governance rules internally for portable use across repositories
metadata:
  skill-version: "6.0.3"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero-compliance-areas: "charter (gates 1-5), lifecycle (state machine), linkage (ADR/OBPI/GHI), minor-release (odometer discipline)"
  govzero_layer: "Layer 3 - File Sync"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-adr-create (v6.0.0)

## Purpose

Create GovZero-compliant ADR files with proper SemVer versioning, OBPI briefs, and registry booking.

**This skill enforces GovZero v6 compliance rules internally and is portable to any GovZero-compliant repository.**

### Common Rationalizations

| Thought | Reality |
|---------|---------|
| "The intent is already clear from the discussion, skip the interview" | Uninterviewed ADRs produce vague intent that drifts during implementation. The interview forces structured articulation. |
| "I'll create the ADR first and backfill the interview answers" | Interview answers shape the ADR content. Backfilling reverses the causality. |
| "This is a small change, it doesn't need a full ADR ceremony" | Small changes that skip the ceremony produce ADRs with missing sections that block downstream gates. |
| "OBPIs can be created later, after the ADR is reviewed" | Co-creation is mandatory. Deferred OBPIs create orphaned checklist items and scope ambiguity. |
| "The user already explained what they want, I can fill in the interview myself" | The interview captures what the human adds that the agent couldn't generate. Agent-fabricated answers miss risk instincts and cross-project connections. |
| "I'll skip the design forcing functions -- the pro-forma questions cover the essentials" | The forcing functions stress-test the decision. Pro-forma questions document it. Both are required. |

### Red Flags

- ADR file exists but no interview answers JSON file alongside it
- ADR marked Proposed with zero OBPI brief files in `obpis/`
- Interview questions bundled into a single message instead of one at a time
- ADR Feature Checklist has more items than there are OBPI briefs
- Agent creates ADR files before any conversation with the human

---

## Persona

**Active persona:** `main-session` — read `.gzkit/personas/main-session.md` and adopt its behavioral identity before executing this skill. The interview is collaborative authoring, not interrogation. Draft first, ask second. Capture what the human adds that you could not have generated.

## Trust Model

**Layer 3 — File Sync:** This tool creates files without verification.

- **Reads:** User input, templates, existing ADR registry
- **Writes:** ADR files, OBPI brief files, registry entries
- **Does NOT verify:** Evidence, test coverage, or criteria
- **Does NOT touch:** Ledger files

---

## GovZero Compliance Rules

ADRs propel MINOR versions only -- each ADR increments the minor odometer (human gate required for version bumps).

> See references/govzero-compliance-rules.md for the full versioning, lifecycle states, five gates, OBPI discipline, and co-creation rules.

---

## Versioning Covenant

This skill maintains explicit alignment between skill version and GovZero version:

**Format:** `{govzero_major}.{skill_minor}.{skill_patch}`

- **{govzero_major}**: Tracks GovZero major version (e.g., v6 → 6)
- **{skill_minor}**: Increments when GovZero governance rules change
- **{skill_patch}**: Increments for tooling/template improvements, no governance changes

**Examples:**

- `6.0.0` — Initial GovZero v6 implementation
- `6.1.0` — GovZero v6 governance rules updated (charter/lifecycle/gates)
- `6.0.1` — Template or procedure fix, no governance change
- `7.0.0` — GovZero v7 released; major rewrite

**Consistency rule:** The skill version's major component MUST always match the GovZero version it enforces.

---

## Inputs

- `adr_id`: Example `ADR-0.0.7`.
- `title`: Example `agent-skills-foundation`.
- `series`: Example `adr-0.0.x`.
- `brief_count`: Number of OBPI briefs to create (if requested).

## Assets

- **ADR Template:** `assets/ADR_TEMPLATE_SEMVER.md` (co-located with this skill)
- **OBPI Brief Template:** `src/gzkit/templates/obpi.md` (canonical; `.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md` is the authoring guide)
- **Closeout Form:** Use pattern from existing ADR closeout forms

## Outputs

- ADR markdown file under `docs/design/adr/{series}/ADR-{id}-{slug}/`.
- ADR closeout form: `ADR-CLOSEOUT-FORM.md` in the same folder.
- OBPIs folder: `docs/design/adr/{series}/ADR-{id}-{slug}/obpis/` (canonical).
- Updated registries:
  - `docs/design/adr/adr_index.md`
  - `docs/design/adr/adr_status.md`
  - `docs/governance/GovZero/adr-status.md` (governance copy)
- OBPI briefs under the `obpis/` folder (when requested).

## Procedure

### Step 0: Interview (MANDATORY — NON-NEGOTIABLE)

**No ADR may be authored without first completing a structured interview.**

The interview captures problem, decision, alternatives, consequences, and scope
before any template work, file creation, or registry updates.

#### Agent-Driven Interview (preferred)

The agent conducts the Q&A conversationally, then records answers deterministically:

1. **Skip deducible fields.** ID, title, lane, semver — if already known from
   context, state them and move on. Don't waste the human's time on mechanical
   fields the agent can fill.

2. **For each substantive question, draft first, then ask.** By the time an ADR
   is being created, there's usually conversation context — a design discussion,
   a defect, a discovered need. The agent reads the question, drafts an answer
   from what's already known, and presents it for the human's input, correction,
   or acceptance. This is collaborative authoring, not interrogation.

3. **One question at a time.** Never batch questions. The human's response to
   one question often reshapes the next answer. Each exchange is a design
   conversation, not a form fill.

4. **Capture the human's additions.** The best interview content comes from what
   the human adds that the agent couldn't have generated — broader patterns,
   risk instincts, connections to other work. These additions are the interview's
   primary value.

5. **Record via `--from`.** After the conversation, write answers to a JSON file
   and record deterministically:

```bash
uv run gz interview adr --from <answers-file>.json
```

6. **Keep the answers file with the ADR.** The JSON file is a permanent artifact
   — store it alongside the ADR document (in the ADR directory for promoted ADRs,
   in the pool directory for pool ADRs).

#### Human-Interactive Interview (terminal)

For humans working without an agent, the interactive mode still works:

```bash
uv run gz interview adr
```

#### Question Protocol

The deducible fields (id, title, semver, lane, parent) are mechanical — skip
them or confirm from context. The interview's value comes from two tiers:

**Tier 1 — ADR Pro-Forma (required, populate the template):**

- **What problem are we solving?** — forces concrete articulation of the need
- **What did we decide?** — forces specificity beyond "we'll add a field"
- **What alternatives were considered?** — forces decision justification
- **What are the positive consequences?** — forces articulation of value
- **What are the negative consequences?** — forces honest risk assessment
- **What are the checklist items?** — forces decomposition into deliverables

**Tier 2 — Design Forcing Functions (required, stress-test the decision):**

These questions turn the interview from "document what you decided" into
"stress-test the decision before committing." Each one works with the
draft-first pattern — the agent proposes an answer, the human corrects.

1. **Pre-Mortem** (Gary Klein): "It is 18 months from now. This decision
   has failed spectacularly. Why?" — bypasses optimism bias. The agent
   drafts failure scenarios, the human adds the ones the agent can't see.

2. **What Would Have to Be True** (Roger Martin): "What would have to be
   true for this to be the right decision?" then "What would have to be
   true for Alternative B to have been better?" — the agent lists conditions,
   the human flags which are shaky. The shakiest condition is the biggest risk.

3. **Constraint Archaeology**: "Is this constraint real, inherited, or
   assumed? When was it last tested?" — forces examination of whether
   constraints are still load-bearing or just inherited convention nobody
   re-examined.

4. **Assumption Surfacing**: "Which assumptions here are implicit and
   undocumented? What if the opposite of your core assumption were true?"
   — different from constraints. Constraints are things we know are fixed.
   Assumptions are things we don't realize we're relying on.

5. **The 2am Operator Question**: "You are on-call at 2am and this is
   broken. What do you need that the design doesn't provide?" — forces the
   operational perspective that architecture documents chronically miss.
   Especially strong for Heavy lane ADRs.

6. **Reversibility Assessment**: "Is this a one-way door or a two-way door?
   If we need to reverse this in 12 months, what does that cost?" — affects
   lane assignment, ceremony level, and how much evidence is warranted.

7. **Scope Minimization**: "What's the smallest version of this that delivers
   value? If you had half the time, what would you cut?" — different from
   non-goals. Non-goals say what's out. Minimization says what's essential.
   The second question forces prioritization under pressure.

**Closing question (always ask last):**

> "What subsequent decisions does this force? What ADRs will we need to
> write because of this one?"

Forward-looking — surfaces downstream commitments the decision creates.

**Sources:** Klein (pre-mortem), Martin (WWHTBT), Amazon (one-way/two-way
doors), Kubernetes Production Readiness Review (operator perspective),
SAST (assumption surfacing), Fairbanks (risk-driven architecture).

**Why this is non-negotiable:** Uninterviewed ADRs produce vague intent documents
that drift during implementation. The interview forces structured articulation of
the decision before any artifacts exist, preventing scope ambiguity at the source.

**Prohibited patterns:**

- Creating ADR files first, then "backfilling" interview answers
- Agent fabricating answers without asking the human
- Skipping the interview because "the intent is already clear"
- Running the interview after OBPI co-creation

---

1. **Read the canonical template** at `assets/ADR_TEMPLATE_SEMVER.md` (co-located with this skill).
2. **Verify GovZero compliance:** ADR ID follows 0.y.z format; status uses canonical lifecycle states.
3. Create the ADR folder: `docs/design/adr/{series}/ADR-{id}-{slug}/`.
4. Create the ADR markdown file using the template structure (all sections required).
5. Create the OBPIs subfolder: `obpis/`.
6. Create `ADR-CLOSEOUT-FORM.md` following existing closeout form patterns.
7. Add the ADR entry to `docs/design/adr/adr_index.md`.
8. Add/refresh the ADR row in `docs/design/adr/adr_status.md`.
9. Add/refresh the ADR row in `docs/governance/GovZero/adr-status.md`.
10. **OBPI Co-Creation (Mandatory):** Create one OBPI brief per checklist item.
    - Count checklist items in Feature Checklist
    - **Preferred:** Run `uv run gz specify <slug> --parent ADR-X.Y.Z --item N --author` for each item
    - After generation, author each brief semantically from the ADR before treating the package as ready
    - **Alternative:** Create files manually in `obpis/` with YAML frontmatter (`id:`, `parent:`, `item:`, `lane:`, `status:`)
    - **Then register:** Run `uv run gz register-adrs ADR-X.Y.Z --all` to ensure `obpi_created` ledger events
    - Verify: `ls obpis/ | wc -l` matches checklist item count
    - Validate authored readiness: `uv run gz obpi validate --adr ADR-X.Y.Z --authored`
    - This is NOT optional — briefs are co-created with the ADR, never deferred
11. **Post-Authoring QC (Mandatory before proposal/defense):**
    Invoke `gz-adr-evaluate ADR-X.Y.Z` to run the ADR and its OBPIs through the
    evaluation framework.
    - Score the ADR on all 8 dimensions
    - Score each OBPI on all 5 dimensions
    - Any ADR dimension scoring 1 or any OBPI dimension scoring 1 must be revised
      before proceeding
    - Optionally use `gz-adr-evaluate ADR-X.Y.Z --red-team` for adversarial review
    - Record the output as `EVALUATION_SCORECARD.md` in the ADR directory
12. Validate:

```bash
uv run -m unittest -q
uv run mkdocs build --strict
```

## Template Sections (Required)

The ADR template includes these sections that must be populated:

- Tidy First Plan
- Feature Checklist — Appraisal of Completeness
- Intent
- Decision
- Interfaces
- Rationale
- Consequences
- Evidence (Four Gates)
- OBPI Acceptance Note
- Evidence Ledger (with subsections)
- Completion Checklist — Post-Ship Tidy
- OBPI Briefs table

## Failure Modes

- ADR created without using the canonical template.
- ADR references files that don't exist.
- Registries drift (ADR exists but isn't indexed or has conflicting status).
- Governance copy not updated (out of sync with main status).

## Acceptance Rules

- ADR uses the canonical template structure.
- No duplicate ADR IDs.
- Registries and ADR content agree on status and series.
- All three registry files are in sync.
- Markdown lint stays clean for `docs/`.

## Related Skills

- `gz-adr-evaluate`: Post-authoring QC evaluation before proposal/defense
- `gz-obpi-specify`: Create and author OBPI briefs from ADR decomposition
- `gz-adr-closeout-ceremony`: Execute closeout ceremony
- `gz-adr-audit`: Verify ADR evidence (includes evidence checks and coverage discovery)
- `gz-adr-sync`: Sync ADR index/status from ADR files (includes registration)
