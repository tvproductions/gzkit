# GZKit Go-Live Gap Analysis

## What Must Be True Before Students Can Use GZKit Independently

**Date:** 2026-03-08
**Litmus test:** RHEA (first greenfield project governed by gzkit)
**Target:** CIDM 6330/6395 graduate students

---

## Definition of "Go-Live"

A student can:

1. Install gzkit in under 5 minutes
2. Bootstrap a new project (`gz init`) without instructor help
3. Write a PRD and first ADR using templates and guides
4. Create task briefs from their ADR checklist
5. Implement, run gates, and attest — with clear error messages when
   something goes wrong
6. Present their governed project to an instructor who can verify the
   governance trail

**The instructor should not need to explain gzkit to the student.** The
documentation and error messages must do that work.

---

## Current State (v0.8.0)

| Capability | Status | Notes |
|------------|--------|-------|
| Installation | Ready | `uv tool install gzkit` works cleanly |
| `gz init` | Ready | Creates correct structure |
| `gz prd` | Ready | Generates template, writes ledger |
| `gz plan` | Ready | Generates ADR with checklist scaffolding |
| `gz specify` | Ready | Creates OBPI briefs from checklist items |
| `gz gates` | Ready | Runs gate checks, records to ledger |
| `gz closeout` | Ready | Presents verification steps |
| `gz attest` | Ready | Records attestation with prereq checks |
| `gz status` | Ready | Shows lifecycle state from ledger |
| Documentation | Partially ready | Comprehensive but assumes governance fluency |
| Error messages | Partially ready | Functional but not always instructive |
| Student onboarding | Not ready | No first-project tutorial (now provided in docs/examples/) |
| Greenfield validation | Not tested | RHEA is the test — hasn't been run yet |

---

## Blockers (Must Fix Before Go-Live)

### Blocker 1: RHEA Bootstrap Must Succeed

**What:** Run the full governance cycle on RHEA (gz init → gz prd → gz plan
→ gz specify → implement → gz gates → gz attest) and document every friction
point.

**Why it blocks:** If gzkit can't govern a simple greenfield library project,
it can't govern a student project. RHEA is the proof.

**Definition of done:**

- [ ] `gz init` creates correct structure in RHEA
- [ ] `gz prd` generates valid PRD from RHEA's vision
- [ ] `gz plan` creates ADR with parseable checklist
- [ ] `gz specify` correctly links OBPI briefs to checklist items
- [ ] `gz gates` finds and runs tests in RHEA's structure
- [ ] `gz attest` records attestation without errors
- [ ] Friction points documented as GitHub issues

**Effort estimate:** 1 focused session (2-4 hours)

### Blocker 2: Student-Facing Documentation Must Exist

**What:** The docs/examples/ directory (created in this session) must be
linked from gzkit's main documentation and discoverable by students.

**Why it blocks:** Students won't find docs/examples/ unless it's linked
from the quickstart or main docs index.

**Definition of done:**

- [ ] `docs/user/quickstart.md` links to tutorial-first-project.md
- [ ] `docs/user/index.md` or README links to docs/examples/
- [ ] Glossary is linked from concept docs
- [ ] Cross-links between guides are all valid

**Effort estimate:** 30 minutes

### Blocker 3: pyproject.toml / Project Scaffolding

**What:** `gz init` should detect or prompt for Python project structure
and optionally create `pyproject.toml` if missing.

**Why it blocks:** Students starting from `mkdir my-project && cd my-project`
won't have a `pyproject.toml`. GZKit's gate commands (`gz gates`) run
`uv run -m unittest discover tests`, which requires a valid Python project
with `uv` dependency resolution. If there's no `pyproject.toml`, this fails
with a confusing error.

**Definition of done:**

- [ ] `gz init` warns if no `pyproject.toml` found
- [ ] Error message explains: "Run `uv init` first to create a Python project"
- [ ] OR: `gz init` offers to run `uv init` for the user
- [ ] Documentation mentions `uv init` as a prerequisite

**Effort estimate:** 1-2 hours (depending on approach)

---

## Gaps (Should Fix Before Go-Live)

### Gap 1: Simplified Brief Generation

**What:** The OBPI template has 12+ sections. Students need a 5-section
version (objective, scope, requirements, acceptance criteria, verification).

**Current workaround:** Students can use the simplified task template from
docs/examples/templates/task-template.md manually, but `gz specify` still
generates the full template.

**Options:**

| Option | Effort | Impact |
|--------|--------|--------|
| A: Add `--simple` flag to `gz specify` | Medium (2-4 hrs) | Clean UX; students get right template |
| B: Add `mode: student` to `.gzkit.json` | Medium (2-4 hrs) | All commands adjust automatically |
| C: Document "ignore sections you don't need" | Low (done) | Works but feels messy |

**Recommendation:** Option B — a `mode: student` in config that generates
lighter templates across all commands. This would also suppress the
decomposition scorecard and reduce the ADR template.

### Gap 2: Glossary Integration

**What:** The glossary (now in docs/examples/glossary.md) should be part
of gzkit's published documentation, not just the examples directory.

**Action:** Move or copy to `docs/user/glossary.md` and add to mkdocs nav.

**Effort:** 15 minutes

### Gap 3: Error Message Improvement

**What:** When a gate fails, the error should explain what to do, not just
what failed.

**Current:**

```
Gate 2 FAILED
  Command: uv run -m unittest discover tests
  Return code: 1
```

**Better:**

```
Gate 2 (TDD) FAILED

  Command: uv run -m unittest discover tests
  Return code: 1

  What this means: Your tests did not pass. Gate 2 requires all unit
  tests to pass before attestation.

  Next steps:
    1. Run the command above manually to see which tests failed
    2. Fix the failing tests
    3. Run `gz gates --adr ADR-0.1.0 --gate 2` again
```

**Effort:** 2-4 hours (update gate output formatting in cli.py)

### Gap 4: Example ADR in a Non-GZKit Domain

**What:** All 9 existing ADRs are about gzkit itself. Students need to see
an ADR for a "normal" project. The first-project tutorial provides one
(reading list), but a second example in a different domain would help.

**Action:** Complete the RHEA bootstrap — it naturally produces a non-GZKit
ADR for a library project.

**Effort:** Covered by Blocker 1

### Gap 5: Instructor Verification Guide

**What:** How does an instructor verify that a student actually used gzkit
governance? What should they look at?

**Needed:**

- A 1-page "instructor checklist" showing what to inspect
- How to read `.gzkit/ledger.jsonl` to verify governance events
- How to check that attestation is recorded
- How to distinguish real governance from retroactive ceremony

**Effort:** 1-2 hours to write

---

## Nice-to-Haves (Post Go-Live)

| Feature | Value | Effort |
|---------|-------|--------|
| `gz init --template student` | One-command setup with student mode, simplified templates, pyproject.toml | High (8+ hrs) |
| `gz explain <concept>` | CLI command that prints glossary definitions inline | Medium (4 hrs) |
| Learning-mode verbose output | Commands print "why" explanations alongside "what" | High (8+ hrs) |
| Student project gallery | Curated examples of governed student projects | Ongoing |
| Curriculum mapping guide | How to map gzkit ceremonies to sprint milestones | Medium (4 hrs) |
| Video walkthrough | Screen recording of the first-project tutorial | Medium (2-3 hrs) |

---

## Go-Live Checklist

### Must be complete

- [ ] **RHEA bootstrap succeeds end-to-end** (Blocker 1)
- [ ] **Student docs linked from main gzkit docs** (Blocker 2)
- [ ] **pyproject.toml prerequisite documented or handled** (Blocker 3)

### Should be complete

- [ ] Simplified brief generation (Gap 1)
- [ ] Glossary in published docs (Gap 2)
- [ ] Improved gate error messages (Gap 3)
- [ ] Instructor verification guide (Gap 5)

### Nice to have

- [ ] `gz init --template student`
- [ ] `gz explain <concept>`
- [ ] Video walkthrough

---

## Recommended Sequence

```text
Week 1:  Bootstrap RHEA (Blocker 1)
         ├── Run gz init → gz attest cycle
         ├── File friction points as GitHub issues
         └── Fix any CLI bugs discovered

Week 2:  Documentation integration (Blocker 2 + Gap 2)
         ├── Link docs/examples/ from quickstart
         ├── Move glossary to docs/user/
         └── Validate all cross-links

Week 2:  pyproject.toml handling (Blocker 3)
         └── Add warning or prompt to gz init

Week 3:  Student UX improvements (Gaps 1, 3, 5)
         ├── Simplified brief template (--simple or mode: student)
         ├── Better gate error messages
         └── Instructor verification guide

Week 4:  Dry run with 1-2 students
         ├── Observe where they get stuck
         ├── Fix discovered issues
         └── Declare go-live ready
```

**Total estimated effort:** 2-3 focused work sessions (8-12 hours) for the
blockers, plus 1-2 sessions for the gaps.

---

## The Litmus Test

RHEA answers the fundamental question:

> **Can a developer (or student) go from an empty directory to a governed,
> attested feature using only gzkit's CLI and documentation?**

If yes → gzkit is ready for classroom use.
If no → the specific failure points become the go-live backlog.

Everything in this document flows from that single question.
