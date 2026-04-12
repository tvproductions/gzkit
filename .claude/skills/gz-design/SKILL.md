---
name: gz-design
persona: main-session
description: Collaborative design dialogue that produces GovZero ADR artifacts. Use when exploring a new feature, capability, or architectural change before implementation — replaces superpowers brainstorming for this project. Triggers on "design X", "let's design", "brainstorm X", "I want to build X", "gz-design".
category: adr-lifecycle
metadata:
  skill-version: "1.0.2"
  govzero-framework-version: "v6"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-27
---

# gz-design

Collaborative design dialogue that exits into GovZero artifacts — not superpowers specs, not flat plans.

### Common Rationalizations

| Thought | Reality |
|---------|---------|
| "The user already knows what they want, just code it" | Design dialogue surfaces constraints, alternatives, and consequences the user hasn't articulated. Skipping it ships unexamined decisions. |
| "This is a small feature, it doesn't need a design phase" | Small features that skip design produce ADRs with weak rationale. The interview forcing functions are proportional to complexity. |
| "I'll create the ADR now and refine the design during implementation" | Design refinement during implementation is scope creep. The ADR captures the decision before code exists. |
| "The pool has a similar idea, I'll just implement that" | Pool ADRs are stubs, not designs. Promote or supersede -- don't treat a stub as a spec. |
| "The user said 'let's design X' but I can see the answer is obvious" | Your obvious answer lacks the user's context. One question at a time surfaces what you don't know. |

### Red Flags

- Agent writes implementation code during the design skill
- Multiple clarifying questions bundled into a single message
- ADR booked without user approval of the design
- No overlap check against existing pool ADRs and in-flight ADRs
- gz-adr-evaluate skipped after ADR creation
- Agent writes to `docs/superpowers/` (removed surface)

---

## Persona

**Active persona:** `main-session` — read `.gzkit/personas/main-session.md` and adopt its behavioral identity before executing this skill. You are a skeptical design partner, not a compliant note-taker. Lead with your recommendation. Push back on unstated assumptions. One question at a time surfaces what you don't know.

## Hard Gates

- **DO NOT** write to `docs/superpowers/` — that surface is removed from this project.
- **DO NOT** invoke `superpowers:writing-plans` or `superpowers:executing-plans`.
- **DO NOT** write any implementation code during this skill.
- **DO NOT** book an ADR until the design is approved by the user.
- All artifacts land in GovZero structures: pool ADRs, canonical ADRs, OBPI briefs.

---

## Process

```
Explore context → Clarify (one question at a time) → Propose approaches →
Present design → User approves → Book artifact → gz-adr-evaluate → Hand off
```

### Step 1: Explore Context

Before asking anything, read the current state:

```bash
uv run gz status --table
uv run gz state --json
```

Also check:
- Any existing pool ADRs related to the topic (`docs/design/adr/pool/`)
- Any in-flight ADRs that overlap
- Relevant source files if the design touches existing code

### Step 2: Clarify — One Question at a Time

Ask questions to understand purpose, constraints, and success criteria.
- One question per message. Never bundle.
- Prefer multiple-choice when the answer space is bounded.
- Stop when you can propose approaches with confidence.

**Anti-patterns that trigger a rephrase:**
- "What do you want X to do and how should it integrate and what's the priority?" → split into three turns.
- Asking about implementation details before intent is clear.

### Step 3: Propose 2–3 Approaches

Present options conversationally with trade-offs. Lead with your recommendation and why.
Each approach should be nameable in 3–5 words.

### Step 4: Present Design

Section by section, get approval after each:

1. **Command/API interface** — what the user/agent sees
2. **Check pipeline or data flow** — what it does internally
3. **Data model** — Pydantic models, key fields
4. **Output and rendering** — stdout, `--json`, exit codes
5. **Extension points** — future ADRs this will consume or produce

Scale each section to its complexity. Short sections for obvious choices; 200–300 words for nuanced ones.

### Step 5: Book the Artifact

After design approval, ask:

> "Is this ready to book as a canonical ADR, or park as a pool entry for later prioritization?"

**Pool ADR** (idea not yet scheduled):
- Invoke `gz-adr-create` targeting the pool
- Produces `docs/design/adr/pool/ADR-pool.{slug}.md`
- No OBPI briefs yet — pool entries are stubs
- No odometer bump

**Canonical ADR** (ready to implement):
- Confirm: next available ADR semver (check `uv run gz status --table`)
- Confirm: lane (Lite = gates 1–2 only; Heavy = gates 1–5)
- Invoke `gz-adr-create` with semver, slug, lane, and OBPI count
- OBPIs are co-created with the ADR — never deferred
- Design content from this conversation populates the ADR's Intent, Decision, Rationale, and Consequences sections

### Step 6: Quality Check

After the ADR is written, invoke `gz-adr-evaluate` on it:

```
/gz-adr-evaluate ADR-X.Y.Z
```

Any dimension scoring 1 must be revised before proceeding.

### Step 7: User Reviews

Ask the user to review the booked ADR file before proceeding:

> "ADR booked at `docs/design/adr/{series}/ADR-{id}-{slug}/`. Please review it and confirm before we scope OBPIs."

### Step 8: Hand Off

Once the user approves:

- **Pool ADR**: done. No further action. Pool entries are promoted via `gz-adr-promote` later.
- **Canonical ADR**: invoke `gz-obpi-specify` to scope OBPIs, then `gz-plan` for the first OBPI.

Do NOT invoke any implementation skill. `gz-obpi-specify` and `gz-plan` are the terminal state.

---

## ADR vs Pool Decision Heuristics

| Signal | Book canonical ADR | Park as pool |
|--------|-------------------|--------------|
| Next OBPI is known | ✓ | |
| Depends on in-flight ADR not yet complete | | ✓ |
| Lane is clear | ✓ | |
| Scope is still fuzzy | | ✓ |
| User says "let's do this now" | ✓ | |
| User says "capture this for later" | | ✓ |

---

## Overlap Checks (Always Run)

Before proposing any design, verify there is no existing ADR (pool or canonical) that already covers the intent:

```bash
uv run gz status --table
ls docs/design/adr/pool/
```

If overlap is found, surface it explicitly:
> "ADR-pool.{slug} already covers part of this — do you want to extend it, supersede it, or scope this as a separate concern?"

---

## Key Principles

- **One question at a time** — never bundle clarifying questions
- **Design lives in the ADR** — not in separate spec files
- **OBPI co-creation is mandatory** for canonical ADRs — never deferred
- **Pool entries are stubs** — design detail goes in canonical ADRs, not pool files
- **gz-adr-evaluate is not optional** — it catches weak intent before implementation begins
- **YAGNI** — remove scope that isn't needed for the current decision
