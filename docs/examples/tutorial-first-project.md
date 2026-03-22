# Tutorial: Your First Governed Project

## CIDM 6330/6395 — From Zero to Attested ADR

---

> **Video companion:** This tutorial mirrors the six-part
> [video series](presentations/index.md). Watch Parts 1-5 first for
> the concepts, then use this tutorial as a hands-on walkthrough.

## What You'll Build

A **reading list tracker** — a small Python CLI where users can add books,
mark them as read, and list books by status. Simple enough to finish in a
few sessions, complex enough to make real design decisions.

This tutorial walks through the full governance cycle using templates:

```text
Setup → Write PRD → Write ADR → Create Tasks → Implement → Verify → Closeout → Attest
```

By the end you'll have a governed project with a PRD, one ADR, tasks
with passing tests, and a human-attested completion record.

---

## Prerequisites

- Python 3.13+ installed
- [uv](https://docs.astral.sh/uv/) installed (`pip install uv` or see uv docs)
- Git installed and configured
- A text editor (VS Code recommended)

---

## Step 1: Set Up Your Project

```bash
# Create the project with uv
uv init reading-list --python 3.13
cd reading-list

# Add pydantic (we'll need it for data models)
uv add pydantic

# Create the project structure
mkdir -p src/reading_list tests docs/design/prd docs/design/adr

# Initialize git
git init
git add -A
git commit -m "Initial project scaffold"
```

**Your project now looks like:**

```text
reading-list/
├── .python-version
├── pyproject.toml       ← uv created this for you
├── src/reading_list/    ← Your source code goes here
├── tests/               ← Your tests go here
└── docs/design/
    ├── prd/             ← PRDs go here
    └── adr/             ← ADRs and tasks go here
```

> **With gzkit CLI (coming soon):**
> ```bash
> uv tool install gzkit
> gz init --mode lite
> ```
> This will scaffold the governance structure automatically, including
> a ledger, manifest, and skill definitions.

---

## Step 2: Write Your PRD

Create a file at `docs/design/prd/PRD-READING-LIST-1.0.0.md`. You can
copy the [PRD template](templates/prd-template.md) as a starting point,
then fill in the sections.

Here's what a completed student PRD looks like:

```markdown
---
id: PRD-READING-LIST-1.0.0
status: Draft
semver: 1.0.0
date: 2026-03-08
---

# PRD-READING-LIST-1.0.0: Reading List Tracker

## Problem Statement

Students and casual readers accumulate book recommendations from classes,
friends, and articles but have no simple way to track what they want to
read, what they're currently reading, and what they've finished. Notes
get lost across sticky notes, browser bookmarks, and text messages.

## North Star

A student can manage their entire reading list from one CLI command,
seeing at a glance what to read next and what they've completed.

## Invariants

- All data persists between sessions (no in-memory-only mode)
- The CLI is the only interface (no web, no GUI)
- Data is stored locally (no cloud, no accounts)

## Q&A Transcript

Q: Why a CLI instead of a web app?
A: CLIs are faster to build, easier to test, and focus the project on
   data modeling and architecture rather than frontend concerns.

Q: Why local storage instead of a cloud database?
A: Keeps the project self-contained. Students can run it anywhere
   without network dependencies or account setup.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 1.0.0 | Pending | | | |
```

**Commit your PRD:**

```bash
git add docs/design/prd/
git commit -m "Add PRD: Reading List Tracker"
```

> **With gzkit CLI (coming soon):**
> ```bash
> gz prd READING-LIST-1.0.0 --title "Reading List Tracker"
> ```
> This generates the file from the template and records a `prd_created`
> event in the governance ledger.

---

## Step 3: Write Your First ADR

Your PRD describes *what* to build. Now decide *how* to approach the first
feature — storing and retrieving books.

Create `docs/design/adr/ADR-0.1.0/ADR-0.1.0.md`. Copy the
[ADR template](templates/adr-template.md) and fill it in:

```markdown
---
id: ADR-0.1.0
status: Draft
semver: 0.1.0
lane: lite
parent: PRD-READING-LIST-1.0.0
date: 2026-03-08
---

# ADR-0.1.0: Book Storage and Retrieval

## Intent

The reading list tracker needs persistent storage for books with title,
author, and status (to-read, reading, done). The storage must survive
between CLI sessions and support filtering by status.

## Decision

1. Use SQLite as the persistence backend (single file, no server)
2. Store the database at `data/reading_list.db`
3. Use the repository pattern to abstract database access
4. Support in-memory SQLite for unit tests
5. Model books with Pydantic BaseModel (title, author, status, date_added)

## Consequences

### Positive

- SQLite is included in Python's standard library — no extra dependencies
- Repository pattern makes it easy to swap backends later
- In-memory SQLite means tests run fast with no file cleanup
- Pydantic validates data at the boundary

### Negative

- SQLite has limited concurrent write support (acceptable for a CLI)
- Repository pattern adds a layer of abstraction over simple queries
- Pydantic adds a dependency (but it's standard in modern Python)

## Decomposition Scorecard

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Data state | 1 | New table, simple schema |
| Logic | 1 | CRUD + filter by status |
| Interface | 1 | CLI commands (add, list, update) |
| Observability | 0 | No logging or metrics needed |
| Lineage | 0 | No upstream/downstream |
| **Total** | **3** | **3-4 tasks recommended** |

## Checklist

1. [ ] Book model with Pydantic (title, author, status, date_added)
2. [ ] SQLite repository with add, list, and update operations
3. [ ] CLI commands: add, list, update-status
4. [ ] Unit tests for repository and model

## Q&A Transcript

Q: Why SQLite over a JSON file?
A: JSON files don't support concurrent access safely, and filtering
   requires loading the entire file into memory. SQLite handles both.

Q: Why Pydantic instead of a plain dataclass?
A: Pydantic validates input at creation time. A dataclass would accept
   any string for status — Pydantic can constrain it to valid values.

## Alternatives Considered

- **JSON file** — Simpler but fragile for concurrent access; no query
  capability. Rejected because filtering by status would require loading
  all records.
- **TinyDB** — Document store that wraps JSON. Adds a dependency without
  solving the query limitation well enough.
- **Plain dictionaries** — No persistence between sessions.

## Evidence

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.1.0 | Pending | | | |
```

**Commit your ADR:**

```bash
mkdir -p docs/design/adr/ADR-0.1.0
git add docs/design/adr/
git commit -m "Add ADR-0.1.0: Book storage and retrieval"
```

> **With gzkit CLI (coming soon):**
> ```bash
> gz plan 0.1.0 --title "Book storage and retrieval" --lane lite
> ```

---

## Step 4: Create Tasks From the Checklist

Each ADR checklist item becomes a task. Create a file for each one in
`docs/design/adr/ADR-0.1.0/obpis/`. Copy the
[REQ template](templates/req-template.md) as a starting point.

Here's Task 1 as a fully worked example:

**`docs/design/adr/ADR-0.1.0/obpis/OBPI-0.1.0-01-book-model.md`:**

```markdown
---
id: OBPI-0.1.0-01-book-model
parent: ADR-0.1.0
item: 1
lane: lite
status: Draft
---

# OBPI-0.1.0-01: Book Model

## ADR Item

- **Source ADR:** `docs/design/adr/ADR-0.1.0/ADR-0.1.0.md`
- **Checklist Item:** #1 - "Book model with Pydantic"

## Objective

Create a Pydantic model for Book with validated fields: title (str),
author (str), status (to-read | reading | done), and date_added (date).

## Allowed Paths

- `src/reading_list/models.py` — New file
- `tests/test_models.py` — New file

## Denied Paths

- `data/` — No database files in this task
- CLI code — Separate task

## Requirements (FAIL-CLOSED)

1. MUST use Pydantic BaseModel, not dataclass
2. MUST constrain status to exactly three values: to-read, reading, done
3. MUST default date_added to today's date
4. NEVER accept empty strings for title or author

## Acceptance Criteria

- [ ] Book model validates title is non-empty
- [ ] Book model validates author is non-empty
- [ ] Book model constrains status to three valid values
- [ ] Book model defaults date_added to current date
- [ ] Invalid inputs raise ValidationError
- [ ] All tests pass: `python -m unittest tests.test_models`

## Verification

    python -m unittest tests.test_models -v
```

Create the remaining task files in the same directory:

| File | Checklist Item |
|------|---------------|
| `OBPI-0.1.0-01-book-model.md` | #1 — Book model with Pydantic |
| `OBPI-0.1.0-02-sqlite-repository.md` | #2 — SQLite repository |
| `OBPI-0.1.0-03-cli-commands.md` | #3 — CLI commands |
| `OBPI-0.1.0-04-unit-tests.md` | #4 — Unit tests |

**Your project structure now:**

```text
docs/design/adr/ADR-0.1.0/
├── ADR-0.1.0.md
└── obpis/
    ├── OBPI-0.1.0-01-book-model.md
    ├── OBPI-0.1.0-02-sqlite-repository.md
    ├── OBPI-0.1.0-03-cli-commands.md
    └── OBPI-0.1.0-04-unit-tests.md
```

**Commit your tasks:**

```bash
git add docs/design/adr/ADR-0.1.0/obpis/
git commit -m "Add task briefs for ADR-0.1.0"
```

> **With gzkit CLI (coming soon):**
> ```bash
> gz specify "Book model" --parent ADR-0.1.0 --item 1 --lane lite
> gz specify "SQLite repository" --parent ADR-0.1.0 --item 2 --lane lite
> gz specify "CLI commands" --parent ADR-0.1.0 --item 3 --lane lite
> gz specify "Unit tests" --parent ADR-0.1.0 --item 4 --lane lite
> ```

---

## Step 5: Implement

Now write the actual code. Start with Task 1 (the model):

**`src/reading_list/models.py`:**

```python
"""Book model for the reading list tracker."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class ReadingStatus(str, Enum):
    """Valid states for a book in the reading list."""

    TO_READ = "to-read"
    READING = "reading"
    DONE = "done"


class Book(BaseModel):
    """A book in the reading list."""

    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    status: ReadingStatus = ReadingStatus.TO_READ
    date_added: date = Field(default_factory=date.today)
```

**`tests/test_models.py`:**

```python
"""Tests for Book model."""

import unittest
from datetime import date

from pydantic import ValidationError

from reading_list.models import Book, ReadingStatus


class TestBook(unittest.TestCase):
    def test_valid_book(self):
        book = Book(title="Dune", author="Frank Herbert")
        self.assertEqual(book.title, "Dune")
        self.assertEqual(book.status, ReadingStatus.TO_READ)

    def test_defaults_date_added(self):
        book = Book(title="Dune", author="Frank Herbert")
        self.assertEqual(book.date_added, date.today())

    def test_rejects_empty_title(self):
        with self.assertRaises(ValidationError):
            Book(title="", author="Frank Herbert")

    def test_rejects_empty_author(self):
        with self.assertRaises(ValidationError):
            Book(title="Dune", author="")

    def test_rejects_invalid_status(self):
        with self.assertRaises(ValidationError):
            Book(title="Dune", author="Frank Herbert", status="burned")

    def test_accepts_all_valid_statuses(self):
        for status in ReadingStatus:
            book = Book(title="Dune", author="Frank Herbert", status=status)
            self.assertEqual(book.status, status)


if __name__ == "__main__":
    unittest.main()
```

**Run the tests:**

```bash
uv run -m unittest tests.test_models -v
```

**Expected output:**

```
test_accepts_all_valid_statuses (tests.test_models.TestBook) ... ok
test_defaults_date_added (tests.test_models.TestBook) ... ok
test_rejects_empty_author (tests.test_models.TestBook) ... ok
test_rejects_empty_title (tests.test_models.TestBook) ... ok
test_rejects_invalid_status (tests.test_models.TestBook) ... ok
test_valid_book (tests.test_models.TestBook) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.012s

OK
```

All acceptance criteria for Task 1 are met. Update the task brief status
from `Draft` to `Completed`.

**Commit and repeat:**

```bash
git add src/ tests/
git commit -m "Implement Task 1: Book model with Pydantic"
```

Repeat for Tasks 2-4: implement, test, verify, update status, commit.

---

## Step 6: Verify

Once all tasks are implemented and tests pass, run a full verification:

```bash
# Run all tests
uv run -m unittest discover tests -v

# Check code quality (if you have ruff installed)
uv run ruff check .
uv run ruff format --check .
```

**Expected test output:**

```
test_accepts_all_valid_statuses (tests.test_models.TestBook) ... ok
test_defaults_date_added (tests.test_models.TestBook) ... ok
test_rejects_empty_author (tests.test_models.TestBook) ... ok
test_rejects_empty_title (tests.test_models.TestBook) ... ok
test_rejects_invalid_status (tests.test_models.TestBook) ... ok
test_valid_book (tests.test_models.TestBook) ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.045s

OK
```

Update the ADR's evidence section to record what passed:

```markdown
## Evidence

- [x] Tests: `uv run -m unittest discover tests` — 18 tests, all pass
- [x] Lint: `uv run ruff check .` — clean
```

**Commit:**

```bash
git add docs/design/adr/ADR-0.1.0/
git commit -m "Update ADR-0.1.0 evidence: all gates pass"
```

> **With gzkit CLI (coming soon):**
> ```bash
> gz gates --adr ADR-0.1.0
> ```
> This runs the gate checks automatically and records pass/fail events
> in the governance ledger.

---

## Step 7: Closeout

Present the work for review. In a classroom setting, this is where you
**show your work to the instructor**.

Create a brief summary of what was delivered, what was verified, and
what the evidence shows. Walk through:

1. The PRD — what you set out to build
2. The ADR — the design decisions you made
3. The tasks — how you decomposed the work
4. The tests — proof that acceptance criteria are met
5. The code — a quick walkthrough of the implementation

The instructor observes the test output live and reviews the artifacts.

> **With gzkit CLI (coming soon):**
> ```bash
> gz closeout ADR-0.1.0
> ```
> This generates a structured closeout report with verification commands
> and attestation choices.

---

## Step 8: Attest

After the instructor (or you, in Lite lane) reviews the work:

Update the ADR's attestation block:

```markdown
## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.1.0 | Completed | Your Name | 2026-03-08 | All tests pass, acceptance criteria met |
```

Update the ADR status from `Draft` to `Completed`.

**Commit the attestation:**

```bash
git add docs/design/adr/ADR-0.1.0/
git commit -m "Attest ADR-0.1.0: completed"
```

> **With gzkit CLI (coming soon):**
> ```bash
> gz attest ADR-0.1.0 --status completed
> ```
> This records a timestamped `attested` event in the governance ledger
> and checks prerequisite gates before allowing attestation.

---

## Step 9: Review Your Git Log

```bash
git log --oneline
```

**Expected output:**

```
abc1234 Attest ADR-0.1.0: completed
def5678 Update ADR-0.1.0 evidence: all gates pass
789abcd Implement Task 4: Unit tests
456efab Implement Task 3: CLI commands
123cdef Implement Task 2: SQLite repository
890abcd Implement Task 1: Book model with Pydantic
567efab Add task briefs for ADR-0.1.0
234cdef Add ADR-0.1.0: Book storage and retrieval
901abcd Add PRD: Reading List Tracker
678efab Initial project scaffold
```

Ten commits tell the complete story of your first governed feature — from
project setup to human sign-off. Each commit is a checkpoint you can
return to, review, or demonstrate.

---

## What You Just Did

```text
Step 1: uv init + structure   → Created project with proper tooling
Step 2: Write PRD              → Defined WHAT to build and WHY
Step 3: Write ADR              → Decided HOW to approach one feature
Step 4: Create Tasks (x4)      → Decomposed the feature into 4 tasks
Step 5: Implement              → Wrote code and tests
Step 6: Verify                 → Confirmed all tests and checks pass
Step 7: Closeout               → Presented work for review
Step 8: Attest                 → Recorded human sign-off
Step 9: Review git log         → Confirmed the record
```

The governance artifacts (PRD, ADR, task briefs, attestation) are not
paperwork — they are the **evidence that you made the design decisions**,
not the AI. When your instructor asks "why did you choose SQLite?", the
answer is in ADR-0.1.0. When they ask "how did you verify it works?",
the test results and evidence section tell the story.

---

## Next ADR

Your PRD likely has more features. Create a new ADR for the next one:

```bash
mkdir -p docs/design/adr/ADR-0.2.0
```

Create `ADR-0.2.0.md` from the template. Each feature gets its own ADR.
Each ADR gets its own tasks. The cycle repeats until your PRD is fulfilled.

---

## Related Guides

- [PRD Guide](guide-prd.md) — Deep dive on writing PRDs
  ([Video: Part 2](presentations/index.md))
- [ADR Guide](guide-adr.md) — Deep dive on ADR structure and lifecycle
  ([Video: Part 3](presentations/index.md))
- [Task Guide](guide-tasks.md) — Deep dive on task decomposition
  ([Video: Part 4](presentations/index.md))
- [Glossary](glossary.md) — Governance terms defined
- [Video Tutorial Series](presentations/index.md) — Six-part video
  companion covering the full governance cycle
