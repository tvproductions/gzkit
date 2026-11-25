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
| Lite | 1 (ADR) + 2 (TDD) + 5 (Human) | Internal changes, refactoring |
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
