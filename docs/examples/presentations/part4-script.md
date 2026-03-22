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
