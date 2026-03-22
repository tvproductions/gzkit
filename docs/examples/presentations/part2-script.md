# Part 2: Product Requirements Documents

## CIDM 6330/6395 — Video Tutorial Series

**Target duration:** 10-12 minutes
**Slide deck:** `part2-slides.pptx`

---

## Slide 1: Title Slide

**Part 2: Product Requirements Documents**

- In Part 1 we learned why governance matters
- Now we start building: the PRD is the first artifact you create
- Everything flows from the problem statement

---

## Slide 2: What Is a PRD?

**Talking points:**

- A PRD is a written contract between you and your stakeholders
- It answers three questions:
  1. What problem exists today?
  2. What will the product do about it?
  3. How will we know it worked?
- A PRD is NOT a design document — it describes WHAT, not HOW
- No code, no frameworks, no database schemas — just the user's needs

**Key phrase:** "If you can't explain the problem without mentioning
technology, you don't understand the problem yet."

---

## Slide 3: Why Write One?

**Talking points:**

- Show the comparison table:

| Without a PRD | With a PRD |
|---|---|
| "I'll just start coding" | You know what "done" looks like before line 1 |
| Scope creeps silently | Scope is explicit; additions require decisions |
| Misalignment surfaces at demo time | Misalignment surfaces at review time |

- The core principle: every requirement traces back to the problem statement
- If a feature doesn't serve the problem, it doesn't belong

---

## Slide 4: The PRD Template — Overview

**Talking points:**

- Show the template structure (anatomy diagram):

```
Problem Statement .......... WHY are we building this?
North Star ................. WHAT does ideal look like?
User Stories ............... WHO benefits and HOW?
Functional Requirements .... WHAT must the product do?
  Must Have / Should Have / Could Have
Non-Goals .................. WHAT are we NOT doing?
Risks & Assumptions ........ WHAT could go wrong?
Success Metrics ............ HOW do we measure success?
```

- Each section has a specific purpose — we'll walk through them
- Template is in `docs/examples/templates/prd-template.md`

---

## Slide 5: Problem Statement and North Star

**Talking points:**

- Problem Statement: 2-3 sentences describing the problem AS THE USER experiences it
- No technical jargon — a non-technical person should nod and say "yes, that's frustrating"
- Show weak vs. strong examples:
  - Weak: "The system lacks a REST API for CRUD operations on user entities"
  - Strong: "Students accumulate book recommendations but have no simple way to
    track what they want to read, what they're reading, and what they've finished"
- North Star: one sentence capturing the ideal outcome
  - "A student can manage their entire reading list from one CLI command"

---

## Slide 6: Requirements and MoSCoW

**Talking points:**

- Group requirements using MoSCoW prioritization:

| Priority | Meaning |
|---|---|
| Must have | The product is useless without this |
| Should have | Important, but a workaround exists |
| Could have | Nice to have if time permits |
| Won't have | Explicitly out of scope this release |

- Each requirement should be Observable, Testable, Independent
- "Won't Have" is not failure — it's scope discipline
- Explicitly stating what you're NOT building prevents scope creep

---

## Slide 7: Non-Goals, Risks, and Assumptions

**Talking points:**

- Non-Goals: 3-5 things the product will explicitly NOT do
  - "Will not include a web interface"
  - "Will not sync across devices"
  - "Will not integrate with Goodreads"
- Risks: What could go wrong? What's your mitigation?
  - Risk: "JSON storage may not handle large lists" → Mitigation: "Use SQLite"
- Assumptions: What are you assuming to be true?
  - Assumption: "Users have Python installed" → If wrong: "Provide binary distribution"

---

## Slide 8: Worked Example — Reading List Tracker PRD

**Talking points:**

- Walk through the completed PRD for our running example
- Problem: Students accumulate book recommendations but lose track
- North Star: Manage entire reading list from one CLI command
- Must Have: Add books, list by status, mark as read
- Won't Have: Web interface, cloud sync, social features
- This PRD drives everything we build in Parts 3-5

**Key phrase:** "Notice how the PRD says nothing about SQLite, Pydantic,
or Python. Those are design decisions — they come in the ADR."

---

## Slide 9: Common Mistakes

**Talking points:**

- Show the mistakes table:

| Mistake | Fix |
|---|---|
| Writing requirements as implementation | "Use React" is design, not a requirement |
| Skipping non-goals | Everything seems in scope; you drown |
| Vague requirements ("should be fast") | "Results appear within 2 seconds" |
| No user stories | Requirements float without context |
| Writing it alone | Blind spots go unchallenged |

- The biggest mistake: jumping to code before writing the PRD
- "The PRD is your defense against building the wrong thing"

---

## Slide 10: Activity — Write Your PRD

**Talking points:**

- Before Part 3, write a PRD for YOUR project:
  1. Copy `templates/prd-template.md` into your project
  2. Write the problem statement first — no technology words allowed
  3. Define your North Star in one sentence
  4. List Must Have and Won't Have requirements
  5. Identify at least 3 non-goals
- Share it with a classmate or teammate for review
- In Part 3, you'll create your first ADR from this PRD

---

## Slide 11: Closing

- The PRD answers WHAT and WHY — never HOW
- Next: Part 3 — Architecture Decision Records
- The chain so far: **PRD** → ADR → Tasks → Code → Verify → Attest
- Resources: PRD Guide, PRD Template in `docs/examples/`
