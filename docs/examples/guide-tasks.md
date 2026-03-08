# Task Decomposition Guide

## CIDM 6330/6395 — Student Reference

---

## What Is Task Decomposition?

Task decomposition is the practice of breaking a feature into **small,
independent work items** that can each be completed, tested, and verified
on their own.

An ADR captures a design decision and lists observable outcomes (the feature
checklist). Each checklist item becomes a **task** — one concrete piece of
work with a clear definition of done.

```text
PRD (the product vision)
  └── ADR (a design decision)
        ├── Task 1 (one deliverable)
        ├── Task 2 (one deliverable)
        └── Task 3 (one deliverable)
```

---

## Why Decompose?

### The "Big Feature" Trap

Without decomposition, features become monoliths:

| Monolith Approach | Decomposed Approach |
|-------------------|---------------------|
| "Build the search feature" (3 weeks, no checkpoints) | Task 1: Search repository method (2 hours) |
| You don't know if you're on track until it's "done" | Each task is testable independently |
| Merge conflicts pile up | Small, frequent merges |
| Hard to get feedback until everything works | Feedback after each task |
| One bug blocks everything | Bugs are isolated to one task |

### The "I'll Just Know When It's Done" Trap

Without explicit acceptance criteria, "done" is subjective:

- "I think search works" vs. "All 4 filter tests pass and the CLI returns
  paginated results"
- "Pretty much finished" vs. "3 of 4 tasks completed; task 4 blocked on
  schema migration"

Tasks make progress **visible and measurable**.

---

## How to Create Tasks

### Step 1: Start From Your ADR Checklist

Your ADR's feature checklist is the source. Each checklist item maps to
exactly one task.

**ADR Checklist:**

```markdown
1. [ ] Search repository method with filter parameters
2. [ ] Unit tests for each filter type
3. [ ] CLI endpoint for search
4. [ ] Results pagination
```

**Becomes 4 tasks:**

| # | Task | Comes From |
|---|------|-----------|
| 1 | Implement search repository method | ADR-001 checklist item 1 |
| 2 | Write unit tests for search filters | ADR-001 checklist item 2 |
| 3 | Add CLI search command | ADR-001 checklist item 3 |
| 4 | Add pagination to search results | ADR-001 checklist item 4 |

### Step 2: Write the Task Brief

Each task needs just **five things**:

1. **Objective** — One sentence: what does "done" look like?
2. **Scope** — What files/modules will you touch?
3. **Requirements** — Specific constraints (must/must not)
4. **Acceptance Criteria** — Testable checkboxes
5. **Verification** — How to prove it works

### Step 3: Order Tasks by Dependency

Some tasks depend on others. Map the dependencies and work in order:

```text
Task 1: Search repository method  ─── no dependencies
Task 2: Unit tests for search     ─── depends on Task 1
Task 3: CLI search command        ─── depends on Task 1
Task 4: Pagination                ─── depends on Task 1 + Task 3
```

Tasks 2 and 3 can be done in parallel. Task 4 must wait.

---

## What Makes a Good Task?

### The INVEST Criteria

Good tasks follow the **INVEST** pattern (borrowed from user stories):

| Letter | Meaning | Example |
|--------|---------|---------|
| **I**ndependent | Can be completed without waiting for other tasks | "Add search method" works alone |
| **N**egotiable | Details can be adjusted during implementation | Filter syntax can evolve |
| **V**aluable | Delivers something useful, even if small | A working search method has standalone value |
| **E**stimable | You can roughly predict the effort | "2-4 hours" is estimable; "a while" is not |
| **S**mall | Completable in one focused session (2-8 hours) | Not "build the entire backend" |
| **T**estable | You can write a test that proves it works | "Returns courses matching department filter" |

### Right-Sizing Tasks

| Too Big | Just Right | Too Small |
|---------|-----------|-----------|
| "Build the search feature" | "Implement search repository with filter params" | "Add import statement for sqlite3" |
| Takes a week, no checkpoints | Takes 2-6 hours, testable result | Takes 5 minutes, not worth tracking |
| Multiple decisions bundled | One clear deliverable | No independent value |

**Rule of thumb:** If a task takes more than one focused work session (4-8
hours), break it down further. If it takes less than 30 minutes, it's
probably part of a larger task.

---

## Task Status Tracking

Tasks move through simple states:

```text
Not Started ──→ In Progress ──→ Done
                     │
                     └──→ Blocked (document what's blocking)
```

| Status | Meaning |
|--------|---------|
| **Not Started** | Haven't begun work |
| **In Progress** | Actively working on it |
| **Done** | All acceptance criteria met, tests pass |
| **Blocked** | Can't proceed; document the blocker |

**One task in progress at a time.** Finish what you started before moving on.
This prevents half-done work from piling up.

---

## Example: Full Task Brief

```markdown
# Task 2: Unit Tests for Search Filters

## Objective

Write unit tests that verify the search repository correctly filters
courses by department, time slot, and instructor name.

## Scope

- `tests/test_search.py` — new file
- `src/search/repository.py` — read only (implemented in Task 1)

## Requirements

1. Use stdlib unittest (no pytest)
2. Use in-memory SQLite for test isolation
3. Each filter type must have at least 2 test cases
4. Tests must run in under 5 seconds

## Acceptance Criteria

- [ ] Department filter returns only matching courses
- [ ] Time slot filter handles morning/afternoon/evening
- [ ] Instructor filter is case-insensitive
- [ ] Combined filters work together (AND logic)
- [ ] Empty results return empty list, not error
- [ ] All tests pass: `python -m unittest tests.test_search`

## Verification

    python -m unittest tests.test_search -v
```

---

## Tasks and AI Coding Assistants

When working with AI assistants (Claude, Copilot, etc.), tasks serve a
critical role: **they scope the AI's work**.

Without a task brief, you might say: "Build the search feature." The AI
generates 500 lines across 8 files and you spend an hour reviewing code
you don't fully understand.

With a task brief, you say: "Implement Task 2 — here are the acceptance
criteria." The AI generates a focused test file that you can review in
10 minutes.

**The task brief is your steering wheel.** The AI is the engine — powerful
but directionless without you.

---

## Common Mistakes

| Mistake | Why It Hurts | Fix |
|---------|-------------|-----|
| Tasks without acceptance criteria | "Done" is subjective | Every task needs testable checkboxes |
| Skipping the dependency map | You start Task 4 and realize Task 1 isn't done | Map dependencies before starting |
| Tasks that are too vague | "Improve performance" — how? where? | Name the specific file, function, or metric |
| Not tracking blocked tasks | Blockers stay invisible | Record what's blocking and what would unblock it |
| Multiple tasks in progress | Context switching wastes time | Finish one, then start the next |

---

## From GZKit's OBPI Pattern

This task approach is a simplified version of gzkit's **OBPI (One Brief Per
Item)** discipline. The full OBPI system adds governance features useful for
professional teams:

| Student Tasks | Professional OBPIs |
|---------------|-------------------|
| 5 sections (objective, scope, requirements, criteria, verification) | 12+ sections (lanes, gates, evidence, attestation) |
| Self-verified | Human attestation required for completion |
| Status tracked in project board | Status tracked in governance ledger |
| No formal ceremony | Closeout presentation + sign-off |

The core principle is identical: **one brief per deliverable, with clear
acceptance criteria and a way to verify completion.**

---

## Templates

A ready-to-use task template is available at:
[templates/task-template.md](templates/task-template.md)

---

## Related Guides

- [PRD Guide](guide-prd.md) — Defining what to build
- [ADR Guide](guide-adr.md) — Recording design decisions
