---
name: gz-session-handoff
description: Create and resume session handoff documents for agent context preservation across engineering sessions.
compatibility: Requires GovZero v6 framework; works with any agent operating under GovZero governance
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero-compliance-areas: "charter (gates 1-5), lifecycle (state machine), session continuity"
  govzero_layer: "Layer 3 — File Sync"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-session-handoff (v6.0.0)

## Purpose

Create and resume session handoff documents that preserve agent context across engineering sessions. When an agent pauses work on an ADR or OBPI, a handoff document captures the full state — what was done, what decisions were made, and what comes next — so that a resuming agent (or the same agent in a new session) can continue without losing context.

---

## Trust Model

**Layer 3 — File Sync:** This tool creates files without verification.

- **Reads:** User input, handoff template, ADR package directory structure
- **Writes:** Handoff markdown files under `{ADR-package}/handoffs/`
- **Validates:** No placeholders, no secrets, all sections present, referenced files exist
- **Does NOT touch:** Ledger files, ADR status, OBPI brief status

---

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `adr_id` | Yes | ADR identifier (e.g. `ADR-0.0.25`) |
| `branch` | Yes | Current git branch (or use `git branch --show-current`) |
| `agent` | Yes | Agent identifier (e.g. `claude-code`, `codex`, `copilot`) |
| `slug` | Yes | Short descriptor for filename (e.g. `create-workflow`) |
| `obpi_id` | No | OBPI identifier if handoff is scoped to a specific brief |
| `session_id` | No | Session identifier for tracing |
| `continues_from` | No | Path to previous handoff document (for chained sessions) |

## Outputs

- Handoff markdown file at `{ADR-package}/handoffs/{timestamp}-{slug}.md`
- Validation result (pass/fail with error details)
- First next action from "Immediate Next Steps" section (for quick resumption)

## Assets

- **Handoff Template:** `assets/handoff-template.md` (co-located with this skill)

---

## CREATE Procedure

The CREATE workflow scaffolds a new handoff document when an agent is pausing work.

### Steps

1. **Read the template** from `assets/handoff-template.md` (co-located with this skill).

2. **Generate timestamp** in ISO 8601 UTC format (e.g. `2026-02-01T10:00:00Z`).

3. **Get current branch** via `git branch --show-current`.

4. **Fill frontmatter fields:**
   - `mode: CREATE`
   - `adr_id`, `branch`, `timestamp`, `agent` — from inputs
   - `obpi_id`, `session_id`, `continues_from` — from optional inputs (leave empty if not provided)

5. **Create `handoffs/` directory** under the ADR package if it does not exist:
   - Scan `docs/design/adr/` for a directory matching the ADR ID pattern
   - Create `{ADR-package}/handoffs/` if needed

6. **Write the scaffold** to `{ADR-package}/handoffs/{timestamp}-{slug}.md` where the timestamp is filesystem-safe (e.g. `20260201T100000Z-create-workflow.md`).

7. **Populate each required section** with session-specific content. The agent must replace the HTML comment guidance in each section with actual content describing the session state:

   | Section | Content |
   |---------|---------|
   | Current State Summary | What was done, what phase the work is in, last action status |
   | Important Context | Architectural constraints, non-obvious dependencies, gotchas |
   | Decisions Made | Decisions with rationale and rejected alternatives |
   | Immediate Next Steps | Ordered list of 3-5 concrete next actions |
   | Pending Work / Open Loops | Deferred items, blockers, discovered work |
   | Verification Checklist | Commands and checks for the resuming agent |
   | Evidence / Artifacts | File paths (backtick-quoted) produced during the session |

8. **Validate** the completed document:
   - Parse frontmatter and validate with `HandoffFrontmatter` model
   - No placeholder markers (TBD, TODO, FIXME, ...) in the body
   - No secrets (passwords, API keys, tokens, private keys)
   - All 7 required sections present
   - All file paths referenced in Evidence / Artifacts exist on disk

9. **Report** the result:
   - File path where the handoff was written
   - Validation result (pass or list of errors)
   - First item from "Immediate Next Steps" (for quick resumption context)

### Programmatic API

The CREATE workflow is implemented as Python functions importable from `tests.governance.test_session_handoff`:

```python
from tests.governance.test_session_handoff import (
    scaffold_handoff,
    resolve_handoff_dir,
    generate_handoff_filename,
    create_handoff,
    CreateResult,
)

# Full workflow
result = create_handoff(
    adr_id="ADR-0.0.25",
    branch="feature/handoff",
    agent="claude-code",
    slug="session-end",
    sections={"Current State Summary": "All tests passing.", ...},
    obpi_id="OBPI-0.0.25-03",
    base_path=Path("."),
)

assert result.is_valid
print(result.file_path)
```

---

## RESUME Procedure

The RESUME workflow discovers, loads, validates, and reports on existing handoff documents so a resuming agent can continue work.

### Steps

1. **List available handoffs** for the ADR using `list_handoffs(adr_id)`. This scans `{ADR-package}/handoffs/` for `.md` files, parses frontmatter, and returns them sorted newest-first.

2. **Select a handoff** — either the newest (default) or a specific file if `handoff_path` is provided.

3. **Classify staleness** using `classify_staleness(timestamp)`:
   - **Fresh** (< 24h): Resume directly
   - **Slightly Stale** (24-72h): Resume with caution, verify key assumptions
   - **Stale** (72h-7d): Human verification required before resume
   - **Very Stale** (> 7d): Human verification required; consider re-creating

4. **Load the handoff content** — read the file and parse frontmatter.

5. **Follow the handoff chain** via `load_handoff_chain(handoff_path)` — recursively traverse `continues_from` links (depth limit: 20) to reconstruct session lineage from oldest ancestor to current document.

6. **Verify context** using `verify_context(content)`:
   - Check branch mismatch (handoff branch vs. current branch)
   - Re-validate referenced file paths in Evidence section

7. **Extract first next step** from the "Immediate Next Steps" section using `extract_first_next_step(content)` — returns the text of the first numbered or bulleted item for quick resumption.

8. **Report** the result:
   - File path of the resumed handoff
   - Staleness classification and human verification requirement
   - First next step for immediate action
   - Validation errors and context warnings
   - Chain of predecessor handoffs

### Human Verification Gate

When staleness is **Stale** or **Very Stale**, the `requires_human_verification` flag is set to `True`. The agent MUST present the handoff summary to the human operator and wait for explicit approval before proceeding with the next steps.

### Programmatic API

The RESUME workflow is implemented as Python functions importable from `tests.governance.test_session_handoff`:

```python
from tests.governance.test_session_handoff import (
    classify_staleness,
    extract_first_next_step,
    list_handoffs,
    load_handoff_chain,
    verify_context,
    resume_handoff,
    HandoffInfo,
    ResumeResult,
    StalenessLevel,
)

# Full workflow — auto-selects newest handoff
result = resume_handoff(
    adr_id="ADR-0.0.25",
    expected_branch="feature/handoff",
    base_path=Path("."),
)

print(f"Staleness: {result.staleness}")
print(f"Human verification: {result.requires_human_verification}")
print(f"First next step: {result.first_next_step}")
print(f"Chain length: {len(result.chain)}")

if result.is_valid:
    print("Ready to resume")
else:
    for err in result.validation_errors:
        print(f"  WARNING: {err}")

# List all handoffs for an ADR
handoffs = list_handoffs("ADR-0.0.25")
for h in handoffs:
    print(f"{h.file_path.name}: {h.staleness} ({h.agent})")
```

---

## Failure Modes

| Failure | Cause | Resolution |
|---------|-------|------------|
| Template not found | `assets/handoff-template.md` missing or path incorrect | Verify skill directory structure |
| ADR package not found | No directory matching ADR ID pattern in `docs/design/adr/` | Verify ADR exists and is properly structured |
| Validation: placeholders | Body contains TBD, TODO, FIXME, or `...` markers | Replace all placeholder text with actual content |
| Validation: secrets | Body contains password=, api_key=, Bearer tokens, etc. | Remove all secret material from the document |
| Validation: missing sections | One or more of the 7 required sections not present | Add all required section headings |
| Validation: missing files | Evidence section references files that don't exist on disk | Verify file paths or remove stale references |
| No handoffs found | `list_handoffs()` returns empty for the ADR | Create a handoff first using the CREATE workflow |
| Stale handoff | Handoff age exceeds 72 hours | Present to human for verification before resuming |
| Branch mismatch | Handoff branch differs from current branch | Verify with human whether branch change is intentional |
| Broken chain | `continues_from` points to a non-existent file | Treat current handoff as chain start; note missing predecessor |

---

## Acceptance Rules

### CREATE
- All 7 required sections populated with session-specific content (no HTML comments or placeholders remaining)
- Frontmatter validates against `HandoffFrontmatter` Pydantic model
- Full validation pipeline passes (no placeholders, no secrets, sections present, references exist)
- File written to correct path: `{ADR-package}/handoffs/{timestamp}-{slug}.md`

### RESUME
- `list_handoffs()` discovers and sorts available handoffs newest-first
- `classify_staleness()` correctly categorizes handoff age (Fresh / Slightly Stale / Stale / Very Stale)
- Stale and Very Stale handoffs set `requires_human_verification = True`
- `extract_first_next_step()` extracts the first action item for quick resumption
- `load_handoff_chain()` traverses `continues_from` links with depth limiting and cycle detection
- `verify_context()` detects branch mismatches and missing referenced files
- `resume_handoff()` orchestrates the full workflow and returns a `ResumeResult`

---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `gz-adr-create` | Creates ADR packages where handoffs are stored |
| `gz-obpi-brief` | OBPI briefs that handoffs may reference |
| `gz-adr-closeout-ceremony` | Closeout may reference handoff chain as evidence |
