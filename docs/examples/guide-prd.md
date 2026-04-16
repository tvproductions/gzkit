# Product Requirements Document (PRD) Guide

## CIDM 6330/6395 — Student Reference

---

## What Is a PRD?

A **Product Requirements Document** is a written contract between you (the
builder) and your stakeholders (users, instructors, teammates) that answers
three questions:

1. **What problem exists today?** — The pain, the gap, the unmet need.
2. **What will the product do about it?** — Capabilities, not implementation.
3. **How will we know it worked?** — Observable success criteria.

A PRD is *not* a design document. It does not describe how the software is
built, what frameworks to use, or what the database schema looks like. It
describes **what the software must accomplish** from the user's perspective.

### Why Write One?

| Without a PRD | With a PRD |
|---------------|------------|
| "I'll just start coding and figure it out" | You know what "done" looks like before line 1 |
| Scope creeps silently — features appear, deadlines slip | Scope is explicit; additions require conscious decisions |
| Stakeholders discover misalignment at demo time | Misalignment surfaces at review time, when it's cheap to fix |
| "Is this feature necessary?" becomes a debate | The PRD answers it: does it serve the problem statement? |

### The Core Principle

> Every requirement in the PRD must trace back to the problem statement.
> If a feature doesn't serve the problem, it doesn't belong.

---

## How to Write a PRD

### Step 1: Start With the Problem

Write 2-3 sentences describing the problem **as the user experiences it**.
Avoid technical jargon. A good problem statement makes a non-technical person
nod and say "yes, that's frustrating."

**Weak:** "The system lacks a REST API for CRUD operations on user entities."

**Strong:** "Students registering for courses must visit three different
websites, re-enter their information each time, and have no way to check
whether a course conflicts with their existing schedule."

### Step 2: Define What Success Looks Like (North Star)

One sentence that captures the ideal outcome. This is your compass — every
decision should move toward it.

**Example:** "A student can discover, evaluate, and register for courses in
a single session without re-entering information."

### Step 3: List What the Product Must Do (Requirements)

Group requirements into categories. Each requirement should be:

- **Observable** — You can demonstrate it working.
- **Testable** — You can write a test that proves it.
- **Independent** — It describes one capability, not a bundle.

Use the MoSCoW method:

| Priority | Meaning |
|----------|---------|
| **Must have** | The product is useless without this |
| **Should have** | Important, but a workaround exists |
| **Could have** | Nice to have if time permits |
| **Won't have** | Explicitly out of scope (this release) |

### Step 4: Declare Non-Goals

Explicitly state what the product will *not* do. This prevents scope creep
and sets honest expectations.

**Example non-goals:**

- Will not integrate with the university's payment system
- Will not support mobile browsers in v1
- Will not handle instructor-side scheduling

### Step 5: Identify Risks and Assumptions

What could go wrong? What are you assuming to be true?

| Risk | Mitigation |
|------|------------|
| Course data API may be unreliable | Cache data locally; refresh on schedule |
| Students may not adopt the tool | Conduct 3 usability tests before launch |

| Assumption | If Wrong |
|------------|----------|
| Students have university email | Add alternative authentication |
| Course catalog updates weekly | Build manual refresh capability |

### Step 6: Get It Reviewed

A PRD is a living document. Share it with stakeholders (instructor, teammates,
potential users) and iterate. The goal is alignment *before* you write code.

---

## Anatomy of a Good PRD

```text
Title + Metadata (who, when, version)
   │
   ├── Problem Statement .............. WHY are we building this?
   ├── North Star ..................... WHAT does ideal look like?
   ├── User Stories ................... WHO benefits and HOW?
   ├── Functional Requirements ........ WHAT must the product do?
   │     ├── Must Have
   │     ├── Should Have
   │     └── Could Have
   ├── Non-Goals ...................... WHAT are we NOT doing?
   ├── Risks & Assumptions ........... WHAT could go wrong?
   ├── Success Metrics ................ HOW do we measure success?
   └── Approval / Sign-Off ........... WHO agrees this is right?
```

---

## Common Mistakes

| Mistake | Why It Hurts | Fix |
|---------|-------------|-----|
| Writing requirements as implementation | "Use React and PostgreSQL" is a design choice, not a requirement | Write what the user needs, not how to build it |
| Skipping non-goals | Everything seems in scope; team drowns | Explicitly exclude 3-5 things |
| Vague requirements | "The system should be fast" — how fast? | "Search results appear within 2 seconds" |
| No user stories | Requirements float without context | Each requirement should connect to a user need |
| Writing it alone | Blind spots go unchallenged | Review with at least one other person |

---

## Creating a PRD in gzkit

gzkit provides both a CLI command and a skill for creating PRDs.

**CLI (terminal):**

```bash
gz prd MYPROJECT-1.0.0 --title "My Project Name"
```

**Skill (Claude Code session):**

```text
/gz-prd
```

The `/gz-prd` skill is recommended when working in Claude Code — it guides
you through declaring project-level intent before ADR planning begins.

---

## From PRD to Action

A PRD tells you *what* to build. The next step is deciding *how* to break it
into deliverable pieces. That's where ADRs and tasks come in:

```text
PRD (what to build)
  └── ADR (how to approach a specific feature)
        └── Tasks (individual work items per feature)
```

In gzkit, the flow continues:

| Step | CLI | Skill | What it does |
|------|-----|-------|--------------|
| 1 | `gz prd` | `/gz-prd` | Declare project intent |
| 2 | `gz plan 0.1.0 --title "..."` | `/gz-plan` | Create the first ADR (skill adds design interviews) |
| 3 | `gz specify slug --parent ADR-0.1.0 --item 1` | `/gz-obpi-specify` | Break out OBPI items under the ADR |
| 4 | `gz obpi pipeline OBPI-0.1.0-01-...` | `/gz-obpi-pipeline` | Implement, verify, present evidence |
| 5 | `gz gates --adr ADR-0.1.0` | `/gz-gates` | Run gate checks |

See: [ADR Guide](guide-adr.md) and [Task Guide](guide-tasks.md)

---

## Template

A ready-to-use PRD template is available at:
[templates/prd-template.md](templates/prd-template.md)

---

## Video Companion

See [Part 2 of the video tutorial series](presentations/part2-script.md) for
a narrated walkthrough of the PRD template with the reading list example.

## Further Reading

- *Inspired* by Marty Cagan — Industry-standard on product thinking
- [gzkit PRD example](https://github.com/tvproductions/gzkit/tree/main/docs/design/prd) — A real PRD used to govern this tool
- [gzkit philosophy](../user/why.md) — Why governance matters in AI-assisted development
