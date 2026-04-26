---
id: ADR-pool.pre-planning-interview
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: speckit, gsd, gstack-office-hours
---

# ADR-pool.pre-planning-interview: Pre-Planning Interview Phase

## Status

Pool

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Formalize `gz interview` as an optional pre-planning step that asks structured questions
before ADR creation. Currently `gz plan` goes straight to ADR generation. Students
(and professionals) often don't know what they don't know — an interview surfaces
assumptions, constraints, and unknowns before committing to a design decision.

---

## Target Scope

### Standard Interview Mode (existing concept)

- `gz interview` runs a structured question set:
  - "Who uses this feature?" (stakeholders/personas)
  - "What's the failure mode?" (error handling strategy)
  - "What existing code does this touch?" (impact surface)
  - "What alternatives did you consider?" (decision forcing)
  - "How will you verify it works?" (test strategy)
- Output: interview transcript saved as markdown (input artifact for `gz plan`)
- Optional: `gz plan --interview` runs the interview inline before ADR generation
- Interview answers pre-populate ADR template fields (Context, Alternatives, Verification)

### Product-Stage Forcing Questions (Demand & Wedge)

A complementary question set for product/market decisions, distinct from the architecture-focused Standard Interview questions above. Lifted from Garry Tan's `gstack` `/office-hours` skill (April 2026), with the role-play frame stripped — gstack's posture is "agent challenges operator as YC partner"; gzkit's posture is "agent drafts question scaffold from session evidence; operator answers; agent seats answers into the artifact" (per AGENTS.md § Operator Economy of Effort). The questions transport cleanly; the role-play does not.

| # | Category | Operator-answered prompt | Push target | Red flags |
|---|----------|--------------------------|-------------|-----------|
| Q1 | Demand Reality | What's the strongest evidence that someone actually wants this — would be genuinely upset if it disappeared tomorrow, not "interested" or "signed up for a waitlist"? | Specific behavior evidence (payment, expanding usage, workflow dependency, panic when service breaks) | Waitlists, interest surveys, "people say it's interesting" |
| Q2 | Status Quo | What are users doing right now to solve this problem — even badly? What does the workaround cost them? | Concrete current workflow, hours wasted, dollars spent, duct-taped tools, manual labor | "Nothing exists" signals insufficient pain |
| Q3 | Desperate Specificity | Name the actual human who needs this most. Title? What gets them promoted? Fired? Keeps them up at night? | Named individual, specific role, concrete consequence | Category-level answers ("SMBs", "marketing teams") |
| Q4 | Narrowest Wedge | Smallest possible version someone would pay real money for this week — not after the platform is built? | Single feature shippable in days; bonus: zero-setup value | "Need full platform first", "stripped version lacks differentiation" |
| Q5 | Observation & Surprise | Have you watched someone use this without helping them? What surprised you? | Specific behavior contradicting assumptions; unintended usage | Survey data, demo calls, "nothing surprising" |
| Q6 | Future-Fit | If the world looks meaningfully different in 3 years, does the product become more essential or less? | Specific thesis about user environment shift | Generic market growth stats, "AI keeps getting better" |

**Routing by stage** (from gstack, adopted as-is):

| Stage | Questions |
|-------|-----------|
| Pre-product | Q1, Q2, Q3 |
| Has users | Q2, Q4, Q5 |
| Paying customers | Q4, Q5, Q6 |

**Doctrinal carve-out from gstack's frame:** the agent does not "challenge" the operator's premises with these questions. The agent drafts each question against session evidence (e.g. for Q2 the agent surfaces what the codebase or design doc already implies about current workflows), the operator answers, the agent seats the answer into the ADR/PRD draft. Same forcing-function value; no agent-judgment-on-product-strategy vector. This is the same shape as the Assumptions Mode below.

---

### Assumptions Mode (code-analysis-driven)

Alternative interview path where the agent analyzes the existing codebase and proposes decisions, asking only for corrections rather than building answers from scratch:

- `gz interview --assumptions` or `gz plan --assumptions`
- **Agent performs before asking:**
  1. Scans codebase for modules, patterns, and conventions relevant to the stated intent
  2. Identifies files that would be touched, existing abstractions that would be extended
  3. Drafts proposed answers to each interview question based on code analysis
  4. Surfaces the proposals as "here's what I'd do — correct me" rather than open-ended questions
- **Human corrects/confirms** each proposal. The human's job shifts from "answer from scratch" to "spot what the agent missed or got wrong"
- **Output:** Same interview transcript format, but annotated with `source: agent-proposed` or `source: human-corrected` per answer
- **When to use:** Incremental changes to an established codebase where the agent has enough context to make informed proposals. Not suitable for greenfield ADRs or novel architectural decisions where the agent lacks domain knowledge.
- **Value:** Faster interview cycles for experienced codebases. The agent does the research legwork; the human provides judgment. Surfaces assumptions the agent makes that the human wouldn't have noticed to challenge.

**Inspired by:** [GSD](https://github.com/gsd-build/get-shit-done) assumptions mode in `/gsd-discuss-phase` — analyzes existing code and surfaces what it would do, asking only for corrections rather than full decisions.

---

## Response Posture (Anti-Sycophancy)

When the agent runs an interview — Standard, Product-Stage, or Assumptions — its response posture is constrained by AGENTS.md § Behavior Rules — Always #14 ("push back when an approach has clear problems"). The gstack `/office-hours` skill makes the same posture mechanical with a sharper "Never say / Always do" list, lifted here as a candidate canonization on promotion. These are tactics, not new doctrine — they implement the existing anti-sycophancy invariant.

**Never say** (sycophantic deflections that lose forcing-function value):

- "That's an interesting approach"
- "There are many ways to think about this"
- "You might want to consider"
- "That could work"

**Always do** (decision-shaped responses):

- Take a position on every operator answer
- State what evidence would change the agent's position
- Challenge the strongest version of the operator's claim, not a strawman
- Name common failure patterns explicitly when the answer matches one

**Pushback pattern:** force vague → specific. "developers" → "the on-call SRE who debugs the build pipeline at 2am". "users" → "the OBPI author who needs to find a forcing-function before authoring." This is the same shape as AGENTS.md § DO IT RIGHT #4 ("verify observed behavior, not assumed behavior") at the interview surface.

These rules apply only inside an interview ceremony — they are not a global posture change. The agent's default mode remains the operator-economy-of-effort mode (draft, review, decide, attest) where the operator's verbatim phrasing is preserved unchanged. Inside the interview, the posture sharpens to forcing-function delivery; outside it, the posture stays preservation-first.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No mandatory interview requirement — experienced users skip straight to `gz plan`.
- No domain-specific question sets in initial implementation.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: gz-interview skill stub already exists

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Core question set is accepted (Standard 5, Product-Stage Q1-Q6, or composite).
3. Transcript format and storage location are decided.
4. Assumptions mode: agent proposal format and source annotation schema are defined.
5. Assumptions mode: at least 3 real interviews are run in assumptions mode to validate proposal quality vs. standard mode.
6. Response posture rules ("Never say / Always do") evaluated for canonization into AGENTS.md § Behavior Rules — Always or kept scoped to interview ceremony only.

---

## Inspired By

- [GitHub Spec Kit](https://github.com/github/spec-kit) — explicit clarification phase before planning where the AI asks questions to resolve ambiguity before writing the specification.
- [GSD](https://github.com/gsd-build/get-shit-done) — assumptions mode in `/gsd-discuss-phase` where the agent analyzes code and proposes decisions, shifting the human's role from author to reviewer.
- [gstack `/office-hours`](https://github.com/garrytan/gstack/blob/main/office-hours/SKILL.md) (Garry Tan, April 2026) — six product/market forcing questions (Demand Reality, Status Quo, Desperate Specificity, Narrowest Wedge, Observation & Surprise, Future-Fit) with explicit anti-sycophancy response-posture rules. Lifted as the Product-Stage question set above with role-play frame stripped per gzkit's Operator Economy of Effort doctrine. The role-play frame ("you are a YC partner") was not adopted — gzkit's persona doctrine (AGENTS.md § Persona) explicitly rejects job-description framings.

---

## Notes

- The skill stub exists but the question set and output format are undefined.
- For students: this is the Socratic method applied to software design.
- Key question: should interview responses persist or be consumed by plan generation?
- Consider: domain-specific question sets (web app vs. CLI vs. library) as a future extension.
- Assumptions mode risk: agent proposals anchor the human. If the agent's analysis is wrong, the human may accept flawed proposals they wouldn't have authored. Mitigation: flag low-confidence proposals explicitly and require human drafting for those items.
- The gz-adr-create skill (v6) already implements a sophisticated "draft first, then ask" interview pattern (Step 0). Assumptions mode is a natural extension — the agent drafts from code analysis rather than conversation context alone.
- gstack's design-doc structure (Problem Statement, Demand Evidence, Status Quo, Target User & Narrowest Wedge, Constraints, Premises, Approaches Considered, Recommended Approach, Open Questions, Success Criteria, Distribution Plan, Dependencies, The Assignment) overlaps heavily with gzkit's existing PRD and ADR templates. No structural change recommended on promotion — the existing templates already cover Problem Statement / Constraints / Premises / Approaches / Open Questions / Success Criteria / Dependencies. Distribution Plan and Demand Evidence are the only fields without direct counterparts and are out-of-scope for governance ADRs (they belong upstream in the PRD if anywhere).
- 2026-04-26 review: gstack-office-hours added to `inspired_by` after operator review of the gstack repo. Lift scope was deliberately narrow — question taxonomy and response-posture tactics — because gstack's broader theory of agent reliability (role-played sprint pipeline, velocity-multiplier framing) conflicts with gzkit's core doctrine (5:1 governance-to-output ratio is the product, anti-vibing mantra). Mixing the theories would produce doctrine drift, which under gzkit's own rules is invariant drift.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Subsumed by CAP-01** (structured design exploration in ADR creation). Spec integrates interview into a broader design exploration protocol with competitive analysis from superpowers and GSD patterns.
