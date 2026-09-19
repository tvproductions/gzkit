---
name: gz-adr-create
persona: main-session
description: Create and book a GovZero ADR with its OBPI briefs. Enforces next-free-integer nominal allocation for foundation IDs and five-gate compliance. Portable skill for GovZero-compliant repositories.
category: adr-lifecycle
compatibility: Requires GovZero v6 framework; provides governance rules internally for portable use across repositories
metadata:
  skill-version: "6.9.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero-compliance-areas: "charter (gates 1-5), lifecycle (state machine), linkage (ADR/OBPI/GHI), foundation-nominal-allocation (next-free-integer)"
  govzero_layer: "Layer 3 - File Sync"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-19
model: opus
---

# gz-adr-create

## Purpose


> **Self-Escalation (opus-tier).** The dialogue with the operator stays in the main session: a subagent cannot ask the operator a question or hear the answer, and what the operator adds is this skill's primary input. When the session model is below opus-tier, you may spawn an `Agent` with `model="opus"` for a bounded drafting or QC track that needs no operator input — pass the operator's words verbatim and the relevant context (ADR IDs, OBPI IDs, prior decisions), and treat what it returns as a draft you verify, not as the operator-facing result.

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
- **Books:** an `adr_created` ledger event on authoring — **for non-pool kinds only**. `gz interview adr` and `gz plan create --kind {foundation,feature}` append it through `register_adr_in_ledger` (`src/gzkit/commands/plan.py`), which registers the ADR's existence, not its completion; the ledger IS touched. **`--kind pool` books nothing** — the pool branch returns before the register call, and the dry-run preview suppresses the ledger line to match. Pool entries reach Layer 2 through `uv run gz register-adrs`, which reconciles ADR packages that exist in canon but are missing from ledger state.

---

## GovZero Compliance Rules

ADRs propel MINOR versions only -- each ADR increments the minor odometer (human gate required for version bumps).

> See references/govzero-compliance-rules.md for the full versioning, lifecycle states, five gates, OBPI discipline, and co-creation rules.

---

## Inputs

- `adr_id`: Example `ADR-0.36.0` (feature) or `ADR-pool.<slug>` (pool).
- `title`: Example `agent-skills-foundation`.
- `brief_count`: Number of OBPI briefs to create — one per Feature Checklist item.

## Assets

- **ADR Template:** `src/gzkit/templates/adr.md` (canonical in-repo shape; the gold standard recent foundation ADRs use).
- **OBPI Brief Template:** `src/gzkit/templates/obpi.md` (canonical; `.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md` is the authoring guide)

## Outputs

- ADR markdown file under `docs/design/adr/<kind-dir>/ADR-{id}-{slug}/` — the scaffolder picks the directory (`foundation/`, `pre-release/`, `pool/`).
- OBPIs folder: `obpis/` inside the ADR folder (canonical).
- **Not at authoring:** `ADR-CLOSEOUT-FORM.md` is written later by `gz closeout` (`src/gzkit/commands/closeout_form.py`).
- The ADR status index `docs/governance/GovZero/adr-status.md` — a Layer-3 derived view regenerated by `gz register-adrs`, never hand-edited (see `AGENTS.md` § Governance doctrine surfaces).
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
   fields the agent can fill. **`--kind` is not deducible** — it is a
   substantive design question (see Tier 1), always asked, never guessed.

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

5. **Record via `--from` (feature / release-carrying ADRs).** For a non-pool
   ADR, after the conversation write answers to a JSON file and scaffold + record
   deterministically:

```bash
uv run gz interview adr --from <answers-file>.json
```

   **Pool ADRs take a different path — `gz interview adr` does NOT record them.**
   `gz interview adr --from` scaffolds non-pool ADRs only: it fails closed on a
   pool id (`ADR-pool.<slug>`), which does not match the canonical
   `ADR-<semver>-<slug>` form, and its error redirects to `gz plan create`. For a
   pool ADR, write the same-shape answers as a hand-authored JSON artifact kept
   alongside the ADR, and scaffold the stub with:

```bash
uv run gz plan create <slug> --kind pool --lane <lite|heavy>
```

   then populate the generated `## Intent` / `## Decision` / `## Alternatives
   Considered` / `## Notes` sections from those answers.

6. **Keep the answers file with the ADR.** The JSON file is a permanent artifact
   — store it alongside the ADR document (in the ADR directory for promoted ADRs,
   in the pool directory for pool ADRs). For a pool ADR it is the *only* record
   of the Step-0 interview: no tool validates its shape today (tracked at
   GHI #718), so authoring it faithfully is the operator's discipline, not a
   gate's.

#### Human-Interactive Interview (terminal)

For humans working without an agent, the interactive mode still works:

```bash
uv run gz interview adr
```

#### Question Protocol

The deducible fields (id, title, semver, lane, parent) are mechanical — skip
them or confirm from context. The interview's value comes from two tiers:

**Tier 1 — ADR Pro-Forma (required, populate the template):**

- **What kind of ADR is this?** — `foundation` (app/system invariant, always 0.0.x) / `feature` (release-carrying capability) / `pool` (noted, not committed). Heuristic: Does this decision shape what the app IS (identity/invariant)? → `foundation`. Does this decision ship a named capability to users? → `feature`. Is this decision noted but not committed? → `pool`. For deeper context see `docs/user/concepts/adr-taxonomy.md`. **Invariance Test (Foundation/Feature Boundary):** *"Foundation = without it, we wouldn't be doing the project."* Use the hexagonal-ports lens to resolve edge cases: **ports point to invariance; adapters are features**. See `docs/user/concepts/foundation-feature-invariance-test.md` for worked examples and anti-patterns. `gz plan create` and `gz adr promote` require `--kind` with **no default** — the operator must choose. Never pre-fill; never propose a default.
- **What problem are we solving?** — forces concrete articulation of the need
- **What did we decide?** — forces specificity beyond "we'll add a field"
- **What alternatives were considered?** — forces decision justification
- **What are the positive consequences?** — forces articulation of value
- **What are the negative consequences?** — forces honest risk assessment
- **What are the checklist items?** — forces decomposition into deliverables

**In gzkit itself `foundation` is CLOSED to new authoring** (`AGENTS.md` § Gate Covenant; roster `data/foundation_grandfather.json`; `gz validate --taxonomy` enforces it), so the choice here is `feature` or `pool`. Adopter repositories scaffold open.

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

1. **Read the canonical template** at `src/gzkit/templates/adr.md` (the in-repo shape recent foundation ADRs use).
2. **Verify GovZero compliance:** ADR ID follows 0.y.z format; status uses canonical lifecycle states.
3. **Scaffold through the CLI, not by hand.** Step 0's `gz interview adr --from` (non-pool) or `gz plan create --kind pool` writes the ADR folder and file from the template.
4. Populate every section the scaffold left as a placeholder (§ Template Sections).
5. `obpis/` is created when the briefs are scaffolded (step 8).
6. Do not author `ADR-CLOSEOUT-FORM.md` — `gz closeout` writes it.
7. **Confirm the ADR is in the ledger (Mandatory):** the non-pool scaffolders book `adr_created` themselves (§ Trust Model); a pool ADR, or any ADR file that reached disk another way, is booked by `uv run gz register-adrs ADR-X.Y.Z`. Run it whenever `uv run gz adr report` does not show the ADR. It also regenerates the Layer-3 status index `docs/governance/GovZero/adr-status.md` from on-disk frontmatter. **Never hand-edit that index** — it is a derived view (`AGENTS.md` § Governance doctrine surfaces). Skipping this step is the canonical failure that produces "ADR exists on disk but is not registered in ledger" warnings.
8. **OBPI Co-Creation (Mandatory):** Create one OBPI brief per checklist item.
    - Count checklist items in Feature Checklist
    - **Preferred:** Run `uv run gz specify <slug> --parent ADR-X.Y.Z --item N` for each item to scaffold, then author each brief semantically from the ADR. **Do NOT pass `--author` on a fresh scaffold** — it requires authored-ready content that does not yet exist and fails closed; author the body first, then validate.
    - **Alternative:** Create files manually in `obpis/` with YAML frontmatter (`id:`, `parent:`, `item:`, `lane:`, `status:`)
    - **Re-register after OBPIs exist:** Run `uv run gz register-adrs ADR-X.Y.Z --all` to emit `obpi_created` ledger events for the newly authored briefs
    - Verify: `ls obpis/ | wc -l` matches checklist item count
    - Validate authored readiness: `uv run gz obpi validate --adr ADR-X.Y.Z --authored`
    - This is NOT optional — briefs are co-created with the ADR, never deferred
9. **Post-Authoring QC (Mandatory before proposal/defense; N/A for pool ADRs):**
    Invoke `gz-adr-evaluate ADR-X.Y.Z` to run the ADR and its OBPIs through the
    evaluation framework. **Pool ADRs are exempt** — `gz adr evaluate` resolves
    an ADR package, which a pool ADR (flat stub file, no OBPIs yet) does not
    have; the CLI errors if invoked on one. The evaluate gate fires at
    **promotion** (`gz adr promote` builds the package), not at pool authoring.
    - Score the ADR on all 8 dimensions
    - Score each OBPI on all 5 dimensions
    - Any ADR dimension scoring 1 or any OBPI dimension scoring 1 must be revised
      before proceeding
    - **The CLI scorer is a pattern-matching pre-screen, not a truth oracle.** When it
      false-negatives on format/keywords (e.g. flags a missing "before/after" token or a
      bold-numbered vs markdown-numbered list), fix the genuine content weakness it
      points at — do NOT reword solely to feed the matcher the tokens it wants. Gaming
      the scorer's shape heuristics is the same theater this skill's ADRs exist to kill.
    - Optionally use `gz-adr-evaluate ADR-X.Y.Z --red-team` for adversarial review
    - Record the judged output as `EVALUATION_SUBSTANCE.md` in the ADR directory
      — `EVALUATION_SCORECARD.md` is machine-owned and regenerated by
      `gz adr evaluate` (GHI #769)
10. Validate:

```bash
uv run gz test
uv run mkdocs build --strict
```

## Template Sections (Required)

The `##` headings of `src/gzkit/templates/adr.md` are the authority — populate every one. Illustratively, at 2026-09-19: Persona, Intent, Decision, Consequences (Positive / Negative), Fidelity Assertions, Decomposition Scorecard, Checklist, Q&A Transcript, Evidence, Alternatives Considered, Forcing Functions (the seven, plus Downstream Decisions Forced), Attestation Block.

## Failure Modes

- ADR created without using the canonical template.
- ADR references files that don't exist.
- ADR exists on disk but is not booked in the ledger (step 7).

## Acceptance Rules

- ADR uses the canonical template structure.
- No duplicate ADR IDs.
- `uv run gz adr report` shows the ADR, and `docs/governance/GovZero/adr-status.md` was regenerated, not edited.
- Markdown lint stays clean for `docs/`.

## Related Skills

- `gz-adr-evaluate`: Post-authoring QC evaluation before proposal/defense
- `gz-obpi-specify`: Create and author OBPI briefs from ADR decomposition
- `gz-adr-closeout-ceremony`: Execute closeout ceremony
- `gz-adr-audit`: Verify ADR evidence (includes evidence checks and coverage discovery)
- `gz-adr-sync`: Sync ADR index/status from ADR files (includes registration)
