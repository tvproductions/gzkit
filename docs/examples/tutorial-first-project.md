# Tutorial: Your First Governed Project

## CIDM 6330/6395 — From Zero to Attested ADR

---

## What You'll Build

A **reading list tracker** — a small Python CLI where users can add books,
mark them as read, and list books by status. Simple enough to finish in a
few sessions, complex enough to make real design decisions.

This tutorial walks through the full governance cycle:

```text
gz init → gz prd → gz plan → gz specify → implement → gz gates → gz closeout → gz attest
```

By the end, you'll have a governed project with a PRD, one ADR, tasks
with passing tests, and a human attestation on the ledger.

---

## Prerequisites

```bash
# Install gzkit
uv tool install gzkit

# Verify installation
gz --help

# Create your project
mkdir reading-list && cd reading-list
git init
mkdir -p src tests docs
```

---

## Step 1: Initialize Governance

```bash
gz init --mode lite
```

**What happens:** GZKit creates its governance infrastructure in your project.

**Expected output:**

```
Initializing gzkit for reading-list in lite mode...
  Created docs/design/prd/
  Created docs/design/constitutions/
  Created docs/design/adr/
  Scaffolded 15 core skills
  Generated AGENTS.md
  Generated CLAUDE.md

gzkit initialized successfully!

Next steps:
  gz prd <name>       Create a PRD
  gz status           Check OBPI progress and lifecycle status
  gz validate         Validate artifacts
```

**What was created:**

```text
reading-list/
├── .gzkit/
│   ├── ledger.jsonl          ← Governance audit trail (1 event so far)
│   ├── manifest.json         ← Project schema and gate definitions
│   └── skills/               ← Governance skill definitions
├── .gzkit.json               ← Project config (paths, mode)
├── docs/design/
│   ├── prd/                  ← PRDs go here
│   ├── constitutions/        ← Project principles go here
│   └── adr/                  ← ADRs and tasks go here
├── AGENTS.md                 ← AI agent operating contract
└── CLAUDE.md                 ← Claude-specific overlay
```

**Check the ledger:**

```bash
cat .gzkit/ledger.jsonl
```

```json
{"schema":"gzkit.ledger.v1","event":"project_init","id":"reading-list","ts":"2026-03-08T14:00:00.000000+00:00","mode":"lite"}
```

One event — your project exists in the governance record.

`✶ Insight ─────────────────────────────────────`
The ledger is append-only JSONL (one JSON object per line). Every governance
action — creating a PRD, running gates, attesting — adds an event. This is
your audit trail. Nobody (including AI) can silently delete history.
`─────────────────────────────────────────────────`

---

## Step 2: Write Your PRD

```bash
gz prd READING-LIST-1.0.0 --title "Reading List Tracker"
```

**Expected output:**

```
Created PRD: docs/design/prd/PRD-READING-LIST-1.0.0.md
```

Now open `docs/design/prd/PRD-READING-LIST-1.0.0.md` and fill it in. Here's
what a completed student PRD looks like:

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

## Gate Mapping

| Gate | Lane | Requirement |
|------|------|-------------|
| Gate 1 (ADR) | All | All changes have ADRs |
| Gate 2 (TDD) | All | Tests pass |
| Gate 3 (Docs) | Heavy | Documentation updated |
| Gate 4 (BDD) | Heavy | Behavior tests pass |
| Gate 5 (Human) | Heavy | Human attestation recorded |

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

---

## Step 3: Create Your First ADR

Your PRD describes *what* to build. Now decide *how* to approach the first
feature — storing and retrieving books.

```bash
gz plan 0.1.0 --title "Book storage and retrieval" --lane lite
```

**Expected output:**

```
Created ADR: docs/design/adr/ADR-0.1.0/ADR-0.1.0.md
```

Open the generated ADR and fill it in:

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
| **Total** | **3** | **3-4 OBPIs recommended** |

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

`✶ Insight ─────────────────────────────────────`
Notice the Decomposition Scorecard. Each dimension is scored 0/1/2. The total
suggests how many tasks (OBPIs) this ADR needs. A score of 3 suggests 3-4
tasks. This prevents both under-decomposition (one giant task) and over-
decomposition (ten trivial tasks).
`─────────────────────────────────────────────────`

---

## Step 4: Create Tasks From the Checklist

Each ADR checklist item becomes a task. Create them with `gz specify`:

```bash
gz specify "Book model" --parent ADR-0.1.0 --item 1 --lane lite
gz specify "SQLite repository" --parent ADR-0.1.0 --item 2 --lane lite
gz specify "CLI commands" --parent ADR-0.1.0 --item 3 --lane lite
gz specify "Unit tests" --parent ADR-0.1.0 --item 4 --lane lite
```

**Expected output (for each):**

```
Created OBPI: docs/design/adr/ADR-0.1.0/obpis/OBPI-0.1.0-01-book-model.md
Created OBPI: docs/design/adr/ADR-0.1.0/obpis/OBPI-0.1.0-02-sqlite-repository.md
Created OBPI: docs/design/adr/ADR-0.1.0/obpis/OBPI-0.1.0-03-cli-commands.md
Created OBPI: docs/design/adr/ADR-0.1.0/obpis/OBPI-0.1.0-04-unit-tests.md
```

**Your project now looks like:**

```text
docs/design/adr/ADR-0.1.0/
├── ADR-0.1.0.md
└── obpis/
    ├── OBPI-0.1.0-01-book-model.md
    ├── OBPI-0.1.0-02-sqlite-repository.md
    ├── OBPI-0.1.0-03-cli-commands.md
    └── OBPI-0.1.0-04-unit-tests.md
```

Fill in each task brief. Here's Task 1 as an example:

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
from `Draft` to `Completed` (in Lite lane, you can self-close tasks).

Repeat for Tasks 2-4: implement, test, verify, update status.

---

## Step 6: Run the Gates

Once all tasks are implemented and tests pass:

```bash
gz gates --adr ADR-0.1.0
```

**Expected output (Lite lane — Gates 1 and 2):**

```
Running gates for ADR-0.1.0 (lite lane)...

Gate 1 (ADR): ✓ pass
  ADR file exists: docs/design/adr/ADR-0.1.0/ADR-0.1.0.md

Gate 2 (TDD): ✓ pass
  Command: uv run -m unittest discover tests
  Ran 18 tests in 0.045s — OK

All required gates passed.
```

**What happened in the ledger:**

```json
{"schema":"gzkit.ledger.v1","event":"gate_checked","id":"ADR-0.1.0","gate":1,"status":"pass",...}
{"schema":"gzkit.ledger.v1","event":"gate_checked","id":"ADR-0.1.0","gate":2,"status":"pass",...}
```

---

## Step 7: Closeout

Present the work for review:

```bash
gz closeout ADR-0.1.0
```

**Expected output:**

```
ADR Closeout: ADR-0.1.0

Lane: lite

Next Steps:
1. Run verification commands below
2. Observe output
3. When ready, run: gz attest ADR-0.1.0 --status <choice>

Verification Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Gate 2 (TDD):
  uv run -m unittest discover tests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Attestation choices:
  gz attest ADR-0.1.0 --status completed
  gz attest ADR-0.1.0 --status partial --reason "..."
  gz attest ADR-0.1.0 --status dropped --reason "..."
```

In a classroom setting, this is where you **show your work to the
instructor**. Run the verification commands live. The instructor observes
the output and makes an attestation decision.

---

## Step 8: Attest

After the instructor (or you, in Lite lane) reviews:

```bash
gz attest ADR-0.1.0 --status completed
```

**Expected output:**

```
Checking prerequisite gates...

Attestation recorded:
  ADR: ADR-0.1.0
  Term: Completed
  By: Your Name
  Date: 2026-03-08
```

**Final ledger state** (check with `cat .gzkit/ledger.jsonl`):

```json
{"event":"project_init","id":"reading-list",...}
{"event":"prd_created","id":"PRD-READING-LIST-1.0.0",...}
{"event":"adr_created","id":"ADR-0.1.0","lane":"lite",...}
{"event":"obpi_created","id":"OBPI-0.1.0-01-book-model","parent":"ADR-0.1.0",...}
{"event":"obpi_created","id":"OBPI-0.1.0-02-sqlite-repository","parent":"ADR-0.1.0",...}
{"event":"obpi_created","id":"OBPI-0.1.0-03-cli-commands","parent":"ADR-0.1.0",...}
{"event":"obpi_created","id":"OBPI-0.1.0-04-unit-tests","parent":"ADR-0.1.0",...}
{"event":"gate_checked","id":"ADR-0.1.0","gate":1,"status":"pass",...}
{"event":"gate_checked","id":"ADR-0.1.0","gate":2,"status":"pass",...}
{"event":"closeout_initiated","id":"ADR-0.1.0",...}
{"event":"attested","id":"ADR-0.1.0","status":"completed","by":"Your Name",...}
```

Ten events tell the complete story of your first governed feature — from
project creation to human sign-off. Every event is timestamped and immutable.

---

## Step 9: Check Status

```bash
gz status
```

**Expected output:**

```
Project: reading-list

ADRs (1 total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ADR-0.1.0 (lite)
    Status: Completed
    Gate 1 ✓ pass | Gate 2 ✓ pass
    Attested by: Your Name (2026-03-08)

Total completed: 1 / 1
```

---

## What You Just Did

```text
Step 1: gz init           → Created governance infrastructure
Step 2: gz prd            → Defined WHAT to build and WHY
Step 3: gz plan           → Decided HOW to approach one feature
Step 4: gz specify (x4)   → Decomposed the feature into 4 tasks
Step 5: (implement)       → Wrote code and tests
Step 6: gz gates          → Verified quality gates pass
Step 7: gz closeout       → Presented work for review
Step 8: gz attest         → Recorded human sign-off
Step 9: gz status         → Confirmed the record
```

The governance artifacts (PRD, ADR, task briefs, ledger) are not paperwork —
they are the **evidence that you made the design decisions**, not the AI.
When your instructor asks "why did you choose SQLite?", the answer is in
ADR-0.1.0. When they ask "how did you verify it works?", the gate evidence
is in the ledger.

---

## Next ADR

Your PRD likely has more features. Create a new ADR for the next one:

```bash
gz plan 0.2.0 --title "Reading statistics and recommendations" --lane lite
```

Each feature gets its own ADR. Each ADR gets its own tasks. The cycle
repeats until your PRD is fulfilled.

---

## Related Guides

- [PRD Guide](guide-prd.md) — Deep dive on writing PRDs
- [ADR Guide](guide-adr.md) — Deep dive on ADR structure and lifecycle
- [Task Guide](guide-tasks.md) — Deep dive on task decomposition
- [Glossary](glossary.md) — Governance terms defined
