# CHORE: Add Architectural Boundaries to AGENTS.md

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `agents-md-architectural-boundaries`

---

## Overview

Add the six architectural boundaries from Architecture Planning Memo Section 12
to AGENTS.md as operational guardrails. These boundaries are ratified decisions
(2026-03-29) that prevent high-risk missteps during the foundation-locking phase.

## Source

Architecture Planning Memo Section 12 (Decision Record 2026-03-29).

Companion foundation ADR to be authored separately (Negative Architecture ADR).
This chore adds the operational mirror to AGENTS.md; the ADR adds the formal
governance authority.

## Policy and Guardrails

- **Lane:** Lite — AGENTS.md content change only
- Content must match the six boundaries verbatim from the memo
- Must not modify existing AGENTS.md sections (additive only)
- New section should be clearly labeled as Architecture Planning Memo-derived

## Workflow

### 1. Read Source

Read the six boundaries from:

```text
docs/design/ARCHITECTURE-PLANNING-MEMO.md
Section 12: Architectural Boundaries (What NOT to Do)
```

### 2. Draft AGENTS.md Section

Add a new section to AGENTS.md titled "Architectural Boundaries" with:

- 12.1: Do not promote post-1.0 pool ADRs into active work
- 12.2: Do not add more pool ADRs to the runtime track
- 12.3: Do not build the graph engine without locking state doctrine first
- 12.4: Do not let reconciliation remain a maintenance chore
- 12.5: Do not let AirlineOps parity become perpetual catch-up
- 12.6: Do not let derived views silently become source-of-truth

### 3. Validate

```bash
uv run gz lint
uv run gz agent sync control-surfaces
```

### 4. Evidence

Record the diff and lint output in proofs/.

## Acceptance Criteria

1. AGENTS.md contains all six architectural boundaries from Section 12
2. Boundaries are in a dedicated, clearly labeled section
3. Lint passes after the change
4. Control surfaces sync cleanly
