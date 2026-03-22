# Part 1: Why Governed Development?

## CIDM 6330/6395 — Video Tutorial Series

**Target duration:** 8-10 minutes
**Slide deck:** `part1-slides.pptx`

---

## Slide 1: Title Slide

**CIDM 6330/6395 — Governed Software Development**
**Part 1: Why Governed Development?**

- Welcome to the series
- Six parts covering the full governance cycle
- By the end you'll know how to keep yourself in the architect's seat
  when AI is writing code

---

## Slide 2: The AI Coding Revolution

**Talking points:**

- AI coding assistants (Claude, Copilot, etc.) are transforming software development
- They can write functions, tests, entire features in seconds
- This is genuinely powerful — you will use these tools professionally
- But there's a problem nobody warns you about

**Key phrase:** "The tools are incredible. The question is: who's actually
making the design decisions?"

---

## Slide 3: The Degradation Pattern

**Talking points:**

- Walk through the four-week pattern (show the table):
  - Week 1: You prompt carefully, review every line, understand what's built
  - Week 2: You start skimming diffs, trust the green checkmarks
  - Week 3: You batch approvals, "looks good" becomes reflexive
  - Week 4: You're approving PRs you didn't read, for code you don't understand
- This happens to professionals, not just students
- By month two, you're a rubber stamp. The AI is the architect.

**Key phrase:** "You didn't lose control in one dramatic moment. It slipped
away one 'looks good' at a time."

---

## Slide 4: Why This Matters for You

**Talking points:**

- In this course, you're learning to be software engineers, not AI operators
- Employers hire you for judgment — the ability to make design decisions
  and explain why
- If you can't articulate why the system is built the way it is, what do
  you actually know?
- The goal isn't to stop using AI. The goal is to stay the architect.

**Key phrase:** "The AI is the engine. You are the driver. Governance is
the steering wheel."

---

## Slide 5: The Zero Doctrine

**Talking points:**

- Introduce the philosophy: "The human is index zero"
  - First in priority — your intent drives every decision
  - Final in authority — you sign off, not the AI
  - Cannot be automated away — some steps require a human
- This is a covenant with two sides:
  1. Gates constrain agents — they can't skip checkpoints
  2. Humans must engage — read everything, question everything
- Without both sides, governance fails silently

**Key phrase:** "Index zero means you come first, and you come last.
The AI doesn't ship without you."

---

## Slide 6: The Governance Chain

**Talking points:**

- Show the chain diagram:

```text
PRD  →  ADR  →  Tasks  →  Code  →  Verify  →  Attest
WHAT     HOW    PIECES   BUILD    CHECK     SIGN OFF
```

- Walk through each link briefly:
  - **PRD**: Define what you're building and why (the problem)
  - **ADR**: Record how you'll approach each major feature (the decisions)
  - **Tasks**: Break each ADR into small, testable deliverables (the work items)
  - **Code**: Implement one task at a time
  - **Verify**: Run tests, check acceptance criteria
  - **Attest**: Human reviews and signs off — "I observed this, and it works"
- Every link is a document you create. Every document is evidence.

**Key phrase:** "When your instructor asks 'why did you choose SQLite?',
the answer isn't in your memory — it's in your ADR."

---

## Slide 7: What You'll Use — Templates

**Talking points:**

- In this course, you'll govern your projects using three templates:
  - **PRD template** — defines the product (Part 2)
  - **ADR template** — records design decisions (Part 3)
  - **Task template** — scopes individual work items (Part 4)
- These are markdown files you fill in and commit to your repo
- No special tools required — just a text editor and git
- The templates are provided in `docs/examples/templates/`

**Transition:** "There is a CLI tool called gzkit that automates this
workflow. We'll preview it in Part 6. For now, you'll learn the thinking
first, and the tooling follows naturally."

---

## Slide 8: What This Series Covers

**Talking points:**

- Quick overview of all six parts:
  - Part 1 (this one): Why governance matters
  - Part 2: Writing PRDs — defining what to build
  - Part 3: Writing ADRs — recording design decisions
  - Part 4: Task decomposition — breaking features into work items
  - Part 5: Implementation and verification — code, tests, and proof
  - Part 6: The full cycle and gzkit CLI preview
- Running example throughout: a reading list tracker CLI
- Each part ends with an activity you can do immediately

---

## Slide 9: Activity — Observe the Degradation Pattern

**Talking points:**

- Before the next video, try this experiment:
  - Ask an AI assistant to build a small feature (anything you like)
  - Accept its output
  - Ask it to add another feature
  - Notice: how carefully did you review the second output vs. the first?
- This is the degradation pattern in miniature
- In Part 2, you'll learn the first defense: writing a PRD before any code

**Key phrase:** "The best time to think about architecture is before you
start coding. The second best time is now."

---

## Slide 10: Closing

- Next: Part 2 — Product Requirements Documents
- Resources: templates, guides, and glossary in `docs/examples/`
- Questions? Post in the course discussion board


---
---

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


---
---

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


---
---

# Part 4: Task Decomposition

## CIDM 6330/6395 — Video Tutorial Series

**Target duration:** 10-12 minutes
**Slide deck:** `part4-slides.pptx`

---

## Slide 1: Title Slide

**Part 4: Task Decomposition**

- Your ADR's Feature Checklist lists observable outcomes
- Now: break each checklist item into a task with clear acceptance criteria
- Tasks are how you control the work — and how you steer AI assistants

---

## Slide 2: Why Decompose?

**Talking points:**

- The "Big Feature" Trap:

| Monolith Approach | Decomposed Approach |
|---|---|
| "Build the search feature" (3 weeks) | Task 1: Search method (2 hours) |
| No checkpoints until "done" | Each task testable independently |
| One bug blocks everything | Bugs isolated to one task |

- The "I'll Know When It's Done" Trap:
  - "Pretty much finished" vs. "3 of 4 tasks completed; task 4 blocked"
  - Tasks make progress visible and measurable

**Key phrase:** "If you can't describe 'done' in a sentence,
the task is too big."

---

## Slide 3: From ADR Checklist to Tasks

**Talking points:**

- Each ADR checklist item maps to exactly one task
- Example from our Book Storage ADR:

| # | ADR Checklist Item | Task |
|---|---|---|
| 1 | Book model with Pydantic | Implement Book model |
| 2 | SQLite repository | Build repository class |
| 3 | CLI commands | Add CLI interface |
| 4 | Unit tests | Write test suite |

- The mapping is 1:1 — no gaps, no bundles

---

## Slide 4: The Task Template — Five Sections

**Talking points:**

- A task brief needs exactly five things:

1. **Objective** — One sentence: what does "done" look like?
2. **Scope** — What files/modules will you touch?
3. **Requirements** — MUST/MUST NOT constraints
4. **Acceptance Criteria** — Testable checkboxes
5. **Verification** — Commands to prove it works

- Template is in `docs/examples/templates/task-template.md`
- This is a simplified version of professional OBPI briefs (5 sections vs. 12+)

---

## Slide 5: Writing Good Acceptance Criteria

**Talking points:**

- Every criterion must be testable — either by code or by demonstration
- Good criteria:
  - "Book model validates title is non-empty"
  - "Invalid status raises ValidationError"
  - "All tests pass: `python -m unittest tests.test_models`"
- Bad criteria:
  - "Code is clean" (subjective)
  - "Works properly" (vague)
  - "Looks good" (untestable)
- End with a verification command that anyone can run

---

## Slide 6: The INVEST Criteria

**Talking points:**

- Good tasks follow the INVEST pattern:

| Letter | Meaning | Example |
|---|---|---|
| **I**ndependent | Completable alone | "Add search method" works standalone |
| **N**egotiable | Details can adjust | Filter syntax can evolve |
| **V**aluable | Delivers something useful | A working method has value |
| **E**stimable | Predictable effort | "2-4 hours" is estimable |
| **S**mall | One focused session | Not "build the entire backend" |
| **T**estable | Provable with a test | "Returns matching results" |

---

## Slide 7: Right-Sizing Tasks

**Talking points:**

| Too Big | Just Right | Too Small |
|---|---|---|
| "Build the search feature" | "Implement search with filters" | "Add import for sqlite3" |
| Takes a week, no checkpoints | 2-6 hours, testable result | 5 minutes, not worth tracking |

- Rule of thumb: 2-8 hours per task
- If it takes more than one work session, break it down further
- If it takes less than 30 minutes, it's part of a larger task

---

## Slide 8: Worked Example — Book Model Task

**Talking points:**

- Walk through Task 1 from our ADR:
  - Objective: Create Pydantic model for Book with validated fields
  - Scope: `src/reading_list/models.py` (new), `tests/test_models.py` (new)
  - Requirements: MUST use Pydantic, MUST constrain status to 3 values,
    MUST reject empty strings
  - Acceptance Criteria: 6 testable checkboxes
  - Verification: `python -m unittest tests.test_models -v`

- Notice the Scope section lists allowed AND denied paths
- This is your steering wheel when working with AI assistants

---

## Slide 9: Tasks and AI Assistants

**Talking points:**

- Without a task brief:
  - "Build the search feature" → AI generates 500 lines across 8 files
  - You spend an hour reviewing code you don't fully understand
- With a task brief:
  - "Implement Task 2 — here are the acceptance criteria" →
    AI generates a focused file you can review in 10 minutes
- The task brief SCOPES the AI's work
  - Allowed paths: where it can write
  - Requirements: what it MUST and MUST NOT do
  - Acceptance criteria: how you verify it's correct

**Key phrase:** "The task brief is your steering wheel.
The AI is the engine — powerful but directionless without you."

---

## Slide 10: Dependency Mapping

**Talking points:**

- Some tasks depend on others. Map before starting:

```
Task 1: Book model         ─── no dependencies
Task 2: SQLite repository  ─── depends on Task 1
Task 3: CLI commands       ─── depends on Task 1 + 2
Task 4: Unit tests         ─── depends on Task 1
```

- Tasks 2 and 4 can be done in parallel
- Task 3 must wait for 1 and 2
- One task in progress at a time — finish before moving on

---

## Slide 11: Activity — Decompose Your ADR

**Talking points:**

- Before Part 5, create tasks from your ADR:
  1. Copy `templates/task-template.md` for each checklist item
  2. Write acceptance criteria as testable checkboxes
  3. Define scope — which files will you create or modify?
  4. Map dependencies — which tasks block which?
  5. Verify each task is INVEST-compliant (especially S and T)

---

## Slide 12: Closing

- Tasks scope the work and steer AI assistants
- Good tasks are Small, Testable, and Independent
- The chain so far: PRD → ADR → **Tasks** → Code → Verify → Attest
- Next: Part 5 — Implementation and Verification


---
---

# Part 5: Implementation and Verification

## CIDM 6330/6395 — Video Tutorial Series

**Target duration:** 10-12 minutes
**Slide deck:** `part5-slides.pptx`

---

## Slide 1: Title Slide

**Part 5: Implementation and Verification**

- You have a PRD, ADR, and task briefs
- Now: write code, write tests, and prove your work
- The goal is evidence — not just "it works on my machine"

---

## Slide 2: The Implementation Loop

**Talking points:**

- For each task, the loop is:
  1. Read the task brief (objective, requirements, criteria)
  2. Write the code
  3. Write the tests
  4. Run the tests — all acceptance criteria must pass
  5. Update the task status to Completed
- One task at a time. Finish before moving to the next.
- If using an AI assistant, give it the task brief — not a vague prompt

---

## Slide 3: Worked Example — Book Model Code

**Talking points:**

- Show the Book model implementation:
  - `ReadingStatus` enum: to-read, reading, done
  - `Book` Pydantic model: title, author, status, date_added
  - `Field(..., min_length=1)` rejects empty strings
  - `default_factory=date.today` for automatic dates
- This code directly satisfies the task brief's requirements:
  - MUST use Pydantic BaseModel ✓
  - MUST constrain status to three values ✓
  - MUST reject empty strings ✓

---

## Slide 4: Worked Example — Tests

**Talking points:**

- Show the test file:
  - `test_valid_book`: Creates a book, checks defaults
  - `test_defaults_date_added`: Verifies automatic date
  - `test_rejects_empty_title`: Empty string raises ValidationError
  - `test_rejects_empty_author`: Same for author
  - `test_rejects_invalid_status`: "burned" is not a valid status
  - `test_accepts_all_valid_statuses`: All three enum values work
- Each test maps to an acceptance criterion in the task brief
- Using stdlib `unittest` — no pytest needed

**Key phrase:** "Every acceptance criterion should have a test.
If you can't test it, rewrite the criterion."

---

## Slide 5: Running Tests and Checking Criteria

**Talking points:**

- Run the verification command from the task brief:
  - `python -m unittest tests.test_models -v`
- Walk through the output:
  - 6 tests, all pass, ~0.01 seconds
- Now check each acceptance criterion:
  - [x] Book model validates title is non-empty
  - [x] Book model validates author is non-empty
  - [x] Book model constrains status to three values
  - [x] Book model defaults date_added to current date
  - [x] Invalid inputs raise ValidationError
  - [x] All tests pass
- Task 1 is DONE. Update the brief status.

---

## Slide 6: Quality Gates

**Talking points:**

- Gates are checkpoints that must pass before work is complete
- For student projects (Lite lane), two gates apply:

| Gate | Name | What It Checks |
|---|---|---|
| 1 | ADR | Design decision is recorded |
| 2 | TDD | Tests pass with adequate coverage |

- Gate 1: Your ADR exists and has a decision + checklist
- Gate 2: All tests pass; coverage is reasonable
- Heavy lane adds Gates 3-5 (docs, BDD, human attestation)
- The point: you can't declare "done" without evidence

---

## Slide 7: The Closeout Concept

**Talking points:**

- Once all tasks are complete and gates pass, you present your work
- Closeout is a ceremony — you show what you built:
  1. Run the verification commands
  2. Show the output (tests passing, code running)
  3. Explain what you built and what decisions you made
  4. Point to the artifacts: PRD, ADR, task briefs, code, tests
- In a classroom: this is your demo
- The point: governance artifacts aren't paperwork — they're your evidence

---

## Slide 8: Attestation — Human Sign-Off

**Talking points:**

- Attestation is the final step: a human declares the work is done
- Three possible outcomes:
  - **Completed** — All work done, all claims verified
  - **Partial** — Some work deferred with documented reason
  - **Dropped** — Decision reversed, documented why
- This is Gate 5 — the gate AI cannot pass
- In a classroom: the instructor reviews and attests
- In Lite lane: you can self-attest (but the record still exists)

**Key phrase:** "Attestation means 'I observed this, and it works.'
Not 'the tests are green.' YOU observed it."

---

## Slide 9: The Evidence Chain

**Talking points:**

- Show the complete evidence chain for one feature:

```
PRD ...................... Problem defined, requirements listed
  └── ADR ................ Design decision recorded
        └── Task 1 ....... Brief written, code + tests pass
        └── Task 2 ....... Brief written, code + tests pass
        └── Task 3 ....... Brief written, code + tests pass
        └── Task 4 ....... Brief written, code + tests pass
        └── Gates ........ Quality checkpoints passed
        └── Closeout ..... Work presented
        └── Attestation .. Human signed off
```

- When your instructor asks "why did you choose SQLite?" — ADR
- When they ask "how did you verify it?" — tests + gate evidence
- When they ask "who made the design decisions?" — you did, and it's proven

---

## Slide 10: Activity — Implement Your First Task

**Talking points:**

- Implement one task from your ADR:
  1. Read your task brief (objective, requirements, acceptance criteria)
  2. Write the code — match the scope in the brief
  3. Write tests for each acceptance criterion
  4. Run the verification command from the brief
  5. Check all acceptance criteria boxes
  6. Update the task brief status to Completed

---

## Slide 11: Closing

- Implementation follows the task brief — no more, no less
- Tests verify acceptance criteria, not just "it runs"
- Closeout presents evidence; attestation records human judgment
- The chain so far: PRD → ADR → Tasks → **Code → Verify → Attest**
- Next: Part 6 — Putting It All Together


---
---

# Part 6: Putting It Together + gzkit Preview

## CIDM 6330/6395 — Video Tutorial Series

**Target duration:** 8-10 minutes
**Slide deck:** `part6-slides.pptx`

---

## Slide 1: Title Slide

**Part 6: Putting It All Together**

- The full governance cycle in review
- What your governed project looks like
- Preview: the gzkit CLI that automates this workflow

---

## Slide 2: The Complete Cycle

**Talking points:**

- Review the governance chain one more time:

```
PRD  →  ADR  →  Tasks  →  Code  →  Verify  →  Attest
```

- Each link produces an artifact:
  - PRD file: defines the product
  - ADR file: records design decisions
  - Task briefs: scope each work item
  - Source code + tests: the implementation
  - Test output: verification evidence
  - Attestation record: human judgment
- Every artifact lives in your git repository — version-controlled evidence

---

## Slide 3: Your Project File Structure

**Talking points:**

- Show what a governed project looks like on disk:

```
my-project/
├── docs/design/
│   ├── prd/
│   │   └── PRD-MYPROJECT-1.0.0.md
│   └── adr/
│       └── ADR-0.1.0/
│           ├── ADR-0.1.0.md
│           └── tasks/
│               ├── TASK-01-model.md
│               ├── TASK-02-repository.md
│               ├── TASK-03-cli.md
│               └── TASK-04-tests.md
├── src/
│   └── (your code)
├── tests/
│   └── (your tests)
└── README.md
```

- The governance artifacts are part of the project, not separate
- They are committed to git alongside the code

---

## Slide 4: The Repeating Cycle

**Talking points:**

- Your PRD likely has multiple features
- Each feature gets its own ADR:
  - ADR-0.1.0: Book storage and retrieval
  - ADR-0.2.0: Reading statistics
  - ADR-0.3.0: Book recommendations
- Each ADR gets its own tasks
- The cycle repeats until the PRD is fulfilled
- You can also write new PRDs for major version changes

**Key phrase:** "Governance isn't a one-time setup. It's a rhythm:
plan, decide, decompose, implement, verify, attest. Repeat."

---

## Slide 5: What You've Learned

**Talking points:**

- Summary of all six parts:

| Part | You Learned | Artifact Created |
|---|---|---|
| 1 | Why governance matters | (understanding) |
| 2 | Defining what to build | PRD |
| 3 | Recording design decisions | ADR |
| 4 | Breaking features into tasks | Task briefs |
| 5 | Implementing and verifying | Code + tests |
| 6 | The full cycle | Governed project |

- You now have a repeatable process for ANY software project

---

## Slide 6: gzkit CLI Preview (Coming Soon)

**Talking points:**

- Everything you've done manually, gzkit can automate:

| You Did Manually | gzkit Automates |
|---|---|
| Created PRD file from template | `gz prd` scaffolds with interview |
| Created ADR file from template | `gz plan` creates ADR with scorecard |
| Created task files from template | `gz specify` generates task briefs |
| Ran tests manually | `gz gates` runs quality checkpoints |
| Presented work informally | `gz closeout` generates evidence summary |
| Self-attested completion | `gz attest` records human sign-off |
| Tracked status in your head | `gz status` shows everything at a glance |

- The CLI also maintains an immutable audit ledger (JSONL)
- Install: `uv tool install py-gzkit` (or download `gz.exe`)

**Transition:** "The manual process you learned IS the gzkit workflow.
The CLI just removes the boilerplate."

---

## Slide 7: The Governance Ledger

**Talking points:**

- gzkit maintains an append-only ledger (`.gzkit/ledger.jsonl`)
- Every governance action becomes an event:
  - `project_init`, `prd_created`, `adr_created`
  - `obpi_created`, `gate_checked`, `attested`
- Events are timestamped and immutable — no one can silently delete history
- The ledger is the source of truth for project state
- This is what makes gzkit different from just "writing markdown files"

---

## Slide 8: Lanes — Lite vs. Heavy

**Talking points:**

- Not all work needs all five gates:

| Lane | Gates Required | When to Use |
|---|---|---|
| Lite | 1 (ADR) + 2 (TDD) | Internal changes, refactoring |
| Heavy | All 5 gates | External contracts, CLI, APIs |

- For coursework, Lite lane is sufficient for most tasks
- Heavy lane adds docs (Gate 3), behavior tests (Gate 4),
  and mandatory human attestation (Gate 5)
- Rule of thumb: if a user would notice, it's Heavy

---

## Slide 9: Course Resources

**Talking points:**

- Everything you need is in `docs/examples/`:

| Resource | Location |
|---|---|
| PRD Template | `templates/prd-template.md` |
| ADR Template | `templates/adr-template.md` |
| Task Template | `templates/task-template.md` |
| PRD Guide (deep dive) | `guide-prd.md` |
| ADR Guide (deep dive) | `guide-adr.md` |
| Task Guide (deep dive) | `guide-tasks.md` |
| Glossary (25+ terms) | `glossary.md` |
| Worked tutorial | `tutorial-first-project.md` |

- The written guides go deeper than these videos
- The glossary defines every governance term you'll encounter

---

## Slide 10: Closing — The Big Idea

**Talking points:**

- Governance isn't bureaucracy — it's evidence
- When AI writes code, governance proves YOU are the architect
- The artifacts survive sessions, contexts, and semesters
- Start simple: PRD → ADR → Tasks → Code → Tests → Done
- The tools come later. The thinking comes first.

**Final key phrase:** "The best time to think about architecture
is before you start coding. You now know how."
