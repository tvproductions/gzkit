# Part 3: Architecture Decision Records

## CIDM 6330/6395 — Video Tutorial Series

**Target duration:** 10-12 minutes
**Slide deck:** `part3-slides.pptx`

---

## Slide 1: Title Slide

**Part 3: Architecture Decision Records**

- Your PRD defines WHAT to build
- Now: decide HOW to approach each major feature
- ADRs capture design decisions before implementation

---

## Slide 2: What Is an ADR?

**Talking points:**

- An ADR captures a single design decision: what, why, consequences
- Think of it as a lab notebook entry for software design
- Scientists don't just record results — they record what they tried and why
- What counts as "architecture"? Anything hard to reverse or system-wide:
  - "SQLite instead of PostgreSQL"
  - "JWT tokens for authentication"
  - "REST API, not GraphQL"
- What is NOT an ADR: bug fixes, formatting, variable names (reversible)

---

## Slide 3: Why Write ADRs?

**Talking points:**

- Three problems ADRs solve:
  1. **Knowledge Loss**: You forget WHY you made a choice. Three months later,
     you waste time re-discovering reasoning or re-introduce solved problems.
  2. **Communication**: Team members (and future-you) need shared, explicit
     decisions — not tribal knowledge.
  3. **Accountability**: When AI writes code, the human must remain the architect.
     ADRs prove YOU made the design decisions.

**Key phrase:** "The human is index zero. ADRs are how you prove it."

---

## Slide 4: The ADR Template — Overview

**Talking points:**

- Show the template structure:

```
Intent ..................... WHAT problem are we solving?
Decision ................... WHAT did we decide?
Consequences ............... WHAT are the tradeoffs?
  Positive / Negative
Alternatives Considered .... WHAT else did we consider?
Feature Checklist .......... WHAT are the observable outcomes?
```

- Each section serves a specific purpose
- Template is in `docs/examples/templates/adr-template.md`
- The Feature Checklist is the bridge to tasks (Part 4)

---

## Slide 5: Writing the Decision

**Talking points:**

- The Decision section is a numbered list of concrete commitments
- Each item should be specific enough to implement
- Example:
  1. Use SQLite as the persistence layer
  2. Store the database at `data/reading_list.db`
  3. Use the repository pattern to abstract database access
  4. Support in-memory SQLite for testing
  5. Model books with Pydantic BaseModel

- If a teammate reads this list, they should know exactly what to build
- Vague decisions ("use a good database") are worse than no decision

---

## Slide 6: Consequences and Alternatives

**Talking points:**

- Consequences: Be honest about BOTH sides
  - Positive: "SQLite is in Python's stdlib — no extra dependencies"
  - Negative: "SQLite has limited concurrent writes"
- Every decision has tradeoffs. Hiding negatives doesn't make them disappear.
- Alternatives Considered: What else you looked at and why not
  - "PostgreSQL — better concurrency, but requires server setup"
  - "JSON file — simpler but fragile for concurrent access"
  - "Plain dictionaries — no persistence between sessions"
- This section proves you THOUGHT THROUGH OPTIONS

**Key phrase:** "If you can't name two alternatives you rejected,
you haven't really made a decision."

---

## Slide 7: The Decomposition Scorecard

**Talking points:**

- How many tasks does an ADR need? The scorecard helps estimate.
- Five dimensions, each scored 0-2:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Data state | No new storage | Simple schema | Complex migration |
| Logic | Trivial | Moderate | Complex multi-step |
| Interface | No user surface | One command | Multiple surfaces |
| Observability | None | Logging | Metrics + alerting |
| Lineage | No dependencies | One upstream | Multiple |

- Total score suggests task count: score 3 = 3-4 tasks
- Prevents under-decomposition (one giant task) AND over-decomposition (ten trivial tasks)

---

## Slide 8: Worked Example — Book Storage ADR

**Talking points:**

- Walk through the Reading List Tracker's first ADR:
  - Intent: Need persistent storage for books with title, author, status
  - Decision: SQLite + repository pattern + Pydantic model
  - Positive: stdlib, fast tests, validated data
  - Negative: limited concurrent writes, extra abstraction layer
  - Alternatives: PostgreSQL (overkill), JSON file (fragile), TinyDB (limited)
  - Scorecard: Data=1, Logic=1, Interface=1, Obs=0, Lineage=0 → Total 3
  - Checklist: 4 items → 4 tasks

**Key phrase:** "Notice: the ADR was written BEFORE any code.
The decisions drive the implementation, not the other way around."

---

## Slide 9: ADR Lifecycle

**Talking points:**

- ADRs move through states:

```
Draft → Proposed → Accepted → Completed
                      |
                      ├→ Superseded (replaced by newer ADR)
                      └→ Abandoned (reversed with reason)
```

- Draft: Still being written
- Proposed: Ready for review
- Accepted: Approved — implementation can begin
- Completed: All checklist items done and verified
- Update status as work progresses — stale ADRs rot

---

## Slide 10: Common Mistakes

**Talking points:**

| Mistake | Fix |
|---|---|
| Too many decisions in one ADR | One decision per ADR |
| No alternatives section | Always list at least 2 alternatives |
| Vague decisions | Numbered, specific commitments |
| Skipping consequences | Be honest about negatives |
| Writing ADRs after coding | Write BEFORE you implement |

---

## Slide 11: Activity — Write Your First ADR

**Talking points:**

- Before Part 4, write an ADR for your first feature:
  1. Copy `templates/adr-template.md` into your project
  2. Connect the Intent to your PRD's problem statement
  3. Write 3-5 numbered decision commitments
  4. List at least 2 alternatives you rejected (and why)
  5. Score the Decomposition Scorecard
  6. Write the Feature Checklist (these become your tasks)

---

## Slide 12: Closing

- ADRs capture HOW decisions before implementation
- The Feature Checklist becomes your task list (Part 4)
- The chain so far: PRD → **ADR** → Tasks → Code → Verify → Attest
- Next: Part 4 — Task Decomposition
