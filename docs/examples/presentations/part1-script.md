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
