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
