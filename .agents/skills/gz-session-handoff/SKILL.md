---
name: gz-session-handoff
persona: main-session
description: Create and resume session handoff documents for agent context preservation across engineering sessions.
category: agent-operations
compatibility: Requires GovZero v6 framework; works with any agent operating under GovZero governance
metadata:
  skill-version: "6.19.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero-compliance-areas: "charter (gates 1-5), lifecycle (state machine), session continuity"
  govzero_layer: "Layer 3 - File Sync"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-26
model: sonnet
---

# gz-session-handoff (v6.18.0)

## Purpose

Create and resume session handoff documents that preserve agent context across engineering sessions. When an agent pauses work on an ADR or OBPI, a handoff document captures the full state — what was done, what decisions were made, and what comes next — so that a resuming agent (or the same agent in a new session) can continue without losing context.

---

## CLI surface: `gz handoff` (ADR-0.0.65)

This skill wields the `gz handoff` verb — the governed CLI surface over the
handoff authoring API. Authoring routes through the fail-closed
`validate_handoff_document` gate rather than hand-written markdown:

```bash
uv run gz handoff list --adr ADR-<X.Y.Z>       # list handoffs newest-first (read-only)
uv run gz handoff resume --adr ADR-<X.Y.Z>     # newest handoff + staleness + first next step (read-only)
uv run gz handoff create [--adr ADR-<X.Y.Z>] --slug <slug> --agent <id> \
  --summary "<text>" --context "<text>" --decisions "<text>" --next-steps "<text>" \
  --pending "<text>" --verification "<text>" --evidence "<text>"
uv run gz handoff authorize --handoff <path> --operator-text "<operator's exact words>"
uv run gz handoff archive --older-than 30d --dry-run  # preview move-not-delete retention (read-only)
uv run gz handoff archive --older-than 30d            # move handoffs older than the threshold into archive/
```

`create` is fail-closed and requires **all seven** sections populated — each has
its own flag, and an unsupplied section is a refusal, not an empty heading
(GHI #692). `authorize` books the operator's ruling on a resumed handoff and is
what lifts the § Operator Authorization Gate for the session (GHI #574); until it
is booked, every mutating tool call is refused. `archive` is move-not-delete: it
relocates handoffs older than `--older-than` into `.gzkit/handoffs/archive/`,
skipping any that are lock-coupled or are the `continues_from:` target of a
still-canonical handoff, so the audit trail is preserved and no resume chain is
orphaned. See the manpages under `docs/user/manpages/handoff*.md`.

---

## Trust Model

**Layer 3 — File Sync:** This tool creates files without verification.

- **Reads:** User input, handoff template, canonical handoff directory `.gzkit/handoffs/`
- **Writes:** Handoff markdown files under `.gzkit/handoffs/` (canonical storage per ADR-0.0.41 / OBPI-0.0.41-03)
- **Validates:** No placeholders, no secrets, all sections present **and populated**, referenced files exist
- **Blocks (RESUME):** every mutating tool call until the operator's ruling is booked via `gz handoff authorize` (§ Operator Authorization Gate; `.claude/hooks/handoff-resume-gate.py`)
- **Reads (RESUME only, read-only):** Ledger and `gz` state surfaces (`gz obpi status`, `gz obpi lock list`, `gz status`, `gz state`), GitHub issue/PR/release state via `gh` read verbs (`gh issue view|list`, `gh pr view|list|diff`, `gh release view|list`), and plain shell reads (`git`, `grep`, `rg`, `cat`, …) to verify a handoff's claims against Layer-2 (§ Claim Verification Gate). **This list is illustrative, not the allowlist's authority** — the allowlist derives from the § Claim Verification Gate's *obligation* to verify every claim. Enumerating examples here is what under-covered it twice (GHI #574 follow-ups).
- **Does NOT write:** Ledger files, ADR status, OBPI brief status

---

## Inputs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `adr_id` | No | ADR identifier (e.g. `ADR-0.0.25`). Omit for work with no parent ADR — a handoff carries continuity for **any** work, not only ADR-scoped work (GHI #709). `mode`, not `adr_id`, is the is-this-a-handoff discriminator. |
| `branch` | Yes | Current git branch (or use `git branch --show-current`) |
| `agent` | Yes | Agent identifier (e.g. `claude-code`, `codex`, `copilot`) |
| `slug` | Yes | Short descriptor for filename (e.g. `create-workflow`) |
| `obpi_id` | No | OBPI identifier if handoff is scoped to a specific brief |
| `last_lock_event_timestamp` | When concluding a held lock | Frontmatter key — ts of the matching `obpi_lock_claimed` event (Sub-Invariant 2; read by `gz validate --lock-handoff-coupling`) |
| `last_commit_sha` | When concluding a held lock | Frontmatter key — HEAD at handoff creation (`git rev-parse --short HEAD`) |
| `session_id` | No | Session identifier for tracing |
| `continues_from` | No | Path to previous handoff document (for chained sessions) |

## Outputs

- Handoff markdown file at `.gzkit/handoffs/{timestamp}-{slug}.md`
- Validation result (pass/fail with error details)
- First next action from "Immediate Next Steps" section, surfaced as an **advisory** for operator review on resume (not a license to execute — see the RESUME Resume contract)

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

5. **Ensure the canonical handoff directory** `.gzkit/handoffs/` exists at the project root. Create if missing (the directory is doctrine-canonical per ADR-0.0.41 / OBPI-0.0.41-03; `gz init` provisions it on bootstrap but defensive creation is acceptable on a stale clone).

6. **Write the scaffold** to `.gzkit/handoffs/{timestamp}-{slug}.md` where the timestamp is filesystem-safe (e.g. `20260201T100000Z-create-workflow.md`).

7. **Populate each required section** with session-specific content. The agent must replace the HTML comment guidance in each section with actual content describing the session state:

   | Section | Content |
   |---------|---------|
   | Current State Summary | What was done, what phase the work is in, last action status |
   | Important Context | Architectural constraints, non-obvious dependencies, gotchas |
   | Decisions Made | Decisions with rationale and rejected alternatives. **Lead each entry with `[operator-ruled]` or `[agent-chose]`** (GHI #696 defect 4) |
   | Immediate Next Steps | Ordered list of 3-5 concrete next actions |
   | Pending Work / Open Loops | Deferred items, blockers, discovered work |
   | Verification Checklist | Commands and checks for the resuming agent |
   | Evidence / Artifacts | File paths (backtick-quoted) produced during the session |

   **Attribute every decision, and write it as a list item.** An operator ruling
   and an agent's own choice rendered identically is what made both equally
   re-arguable in the next session (GHI #696 defect 4) — operator canon is
   verbatim, *"MY WORD IS AUTHORITY IN ALL CASES."* Each entry MUST begin with a
   list marker (`- `, `* `, or `N. `) and then lead with `[operator-ruled]` or
   `[agent-chose]`; attribution matching is case- and spacing-tolerant. An
   unmarked entry parses as **unattributed** and is never promoted to a ruling nor
   demoted to a preference — but it also does not carry forward, so an unmarked
   operator ruling is a ruling you will re-argue.

   ```markdown
   - [operator-ruled] Ship the thing (verbatim: "ship it").
   - [agent-chose] Used a temp dir for the fixture.
   ```

   **The list marker is load-bearing, not styling (GHI #722).** `_section_items`
   only treats a line as an entry when it carries one, so
   `[operator-ruled] ...` with no `- ` parses to NOTHING — `parse_decisions`
   returns an empty list and the successor's `Settled Rulings` promotes zero
   rulings. Ten operator rulings left the chain that way across two handoffs
   before it was caught. This paragraph exists because the contract previously
   said only "lead each entry with `[operator-ruled]`", and an author following
   that literally produced a section the promoter could not read. Now fail-closed:
   `validate_decision_markers` refuses the shape at authoring, so the gate catches
   it instead of the next session discovering a ruling it has to re-argue.

   **`Settled Rulings` is written for you — do NOT hand-fill it.** The optional
   `## Settled Rulings` section is composed by construction: `create_handoff`
   carries the predecessor's settled entries forward and promotes its
   `[operator-ruled]` decisions into it, de-duplicated (GHI #696 defect 3). A
   ruling booked once keeps arriving, so it is never re-filed as an open loop and
   re-adjudicated. It is deliberately NOT a required section — the
   `handoff-documents` gate validates the whole post-cutover corpus, and a
   required section would fail all of it.

   **A ruling that arrives AFTER the handoff is committed must be seated in the
   next one.** Composition runs at authoring time, so a late ruling — the operator
   rules on a GHI once the session's handoff is already written — has no home in
   that handoff. On the next CREATE, pass it via `--settled "<ruling>"`
   (repeatable). It unions with the carried set and never replaces it, so seating
   one late ruling cannot drop the booked history. Check the prior session's
   trailing rulings before authoring: if one is not already carried, seat it.
   Routine use of the flag is a signal that rulings are arriving outside the
   handoff cycle and belong in a durable ruling store (campaign Movement D box 3).

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

### Programmatic API (`gzkit.handoff_api`)

The handoff authoring/resume API is a real runtime module (OBPI-0.0.65-02):
`create_handoff`, `scaffold_handoff`, `list_handoffs`, `load_handoff_chain`, and
`resume_handoff`. Every authoring path routes the produced document through
`gzkit.handoff_validation.validate_handoff_document`, so a handoff that fails the
gate is **never written** (fail-closed — `create_handoff` raises
`HandoffValidationError` carrying the violation list). `scaffold_handoff`
deterministically pre-fills the factual sections (Current State Summary, Evidence /
Artifacts, Verification Checklist) from injected observed state with **no LLM or
network call**; only the judgment sections (Decisions Made, Important Context) are
author-supplied.

```python
from pathlib import Path
from gzkit.handoff_api import create_handoff

path = create_handoff(
    adr_id="ADR-0.0.65",
    branch="main",
    agent="claude-code",
    slug="session-end",
    sections={"Current State Summary": "All tests passing.", ...},
    obpi_id="OBPI-0.0.65-02-programmatic-api-implementation",
    base_path=Path("."),
)  # HandoffValidationError (nothing written) if the document fails the gate
```

---

## Auto-load on session start (CAP-13, GHI #326)

A SessionStart hook (`.claude/settings.json` for Claude Code,
`.codex/hooks.json` for Codex CLI) runs `scripts/session_orientation.py` on
every session boot. The orientation script's "Most-recent handoff" section
selects the newest file under `.gzkit/handoffs/` and classifies its age via
the same Fresh / Slightly-Stale / Stale / Very-Stale buckets this skill
uses. The hook output is injected as session context, so the resuming
agent sees the handoff path, freshness bucket, and first-next-step before
its first response without operator prompting.

The hook is the mechanical floor; this skill's RESUME workflow remains the
canonical path when an operator wants the full chain traversal, branch
verification, or staleness gate. Operators who do not want orientation
injection can disable the hook in their local settings.

## RESUME Procedure

The RESUME workflow discovers, loads, validates, and reports on existing handoff documents so a resuming agent can continue work.

> **Resume contract — a handoff ADVISES; it does not authorize.** A handoff
> records a *proposed* plan and its context. It is **NOT** a clearance to execute
> that plan. On resume — at **every** freshness level, including Fresh — you MUST:
> (1) present the advised next steps and current state to the operator;
> (2) obtain explicit operator authorization before executing any of them — no
> file mutation, no `gz` ceremony, no migration until the operator says go;
> (3) treat the human-as-final-witness doctrine as binding from the first step —
> **you advise; the operator rules; you note variance and stop.**
> Barreling into execution from a handoff is the exact failure this contract
> exists to prevent. The plan is the destination; operator authorization is the
> ignition. Staleness escalates *verification depth* (below); it never relaxes the
> authorization requirement, and freshness never waives it.

### Steps

1. **List available handoffs** for the ADR using `list_handoffs(adr_id)`. This scans `.gzkit/handoffs/` for `.md` files whose `adr_id:` frontmatter matches, parses each frontmatter, and returns them sorted newest-first.

2. **Select a handoff** — either the newest (default) or a specific file if `handoff_path` is provided.

3. **Classify staleness** using `classify_staleness(timestamp)`. Staleness sets
   how much you re-verify before presenting — it does **not** decide whether you
   need operator authorization (you always do, per the Resume contract above):
   - **Fresh** (< 24h): present advised steps + state; verify branch and evidence paths; await operator authorization
   - **Slightly Stale** (24-72h): also re-verify key assumptions before presenting
   - **Stale** (72h-7d): deep re-verification required; `requires_human_verification` flag set
   - **Very Stale** (> 7d): deep re-verification required; `requires_human_verification` set; consider re-creating the handoff

4. **Load the handoff content** — read the file and parse frontmatter.

5. **Follow the handoff chain** via `load_handoff_chain(handoff_path)` — recursively traverse `continues_from` links (depth limit: 20) to reconstruct session lineage from oldest ancestor to current document.

6. **Verify context** using `verify_context(content)`:
   - Check branch mismatch (handoff branch vs. current branch)
   - Re-validate referenced file paths in Evidence section

7. **Verify the handoff's claims against Layer-2 (Claim Verification Gate).** Walk
   the Current State Summary, Decisions Made, and Immediate Next Steps; for every
   completion / lock / gate / readiness claim, run the matching Layer-2 check from
   the § Claim Verification Gate table and tag the claim **VERIFIED**, **STALE**,
   or **UNVERIFIABLE**. Verify the **precondition of each advised step** too — a
   step whose precondition is STALE is void. Never relay a handoff claim as fact
   without this check.

   **`uv run gz handoff resume` runs the advised-step arm of this gate for you**
   (GHI #696 defect 2). It extracts every governance reference each step cites and
   resolves GHI state through `gh`, rendering `live` / `settled` / `unknown` per
   reference and marking a step **CITES SETTLED** when a citation is `settled`.
   Start there rather than hand-rolling the `gh` calls — then hand-verify what it
   reports as `unknown` (ADR and OBPI references always resolve `unknown`, because
   their only repo-local index is a Layer-3 derived view).

   **The flag is a citation, not a verdict — you still adjudicate.** A step may
   name a closed GHI as a *precondition* (the work is done, the step is a STALE
   claim, do not relay it) or as *provenance* ("the fix that landed in #696", the
   step still stands). No available signal distinguishes them, so the tool reports
   and you decide. Treating every flagged step as void discards live work; treating
   none as void is the decay this gate exists to catch.

8. **Extract the next steps** from the "Immediate Next Steps" section — `resume_handoff` returns `ResumeResult.steps`, one entry per authored step (with its references), and `next_steps` / `first_next_step` as derived text projections. An enumeration collapsed onto one line still yields one entry per step.

9. **Report** the result, then **stop and await operator authorization** (do not begin executing):
   - File path of the resumed handoff
   - Staleness classification and re-verification depth applied
   - **Each presented claim tagged VERIFIED / STALE / UNVERIFIABLE** with its Layer-2 receipt; STALE claims and the advised steps they void called out explicitly
   - First next step, presented **for operator review and authorization** (not for immediate action)
   - Validation errors and context warnings
   - Chain of predecessor handoffs

### Operator Authorization Gate (universal) — MECHANIZED

**Every resume requires explicit operator authorization before any execution, at
every freshness level — Fresh included.** The agent presents the advised next
steps and current state, then waits for the operator to rule. This is the
human-as-final-witness doctrine applied to session resumption: the agent advises,
the operator rules, the agent notes variance and stops.

**This gate binds mechanically (GHI #574).** It was prose plus a template banner
until 2026-07-16 — an agent could read the banner and proceed, and nothing
stopped it. `.claude/hooks/handoff-resume-gate.py` (PreToolUse on
`Write|Edit|NotebookEdit` **and** `Bash`) now refuses every mutating tool call
while this session has resumed a handoff with no operator ruling on the ledger.
The decision is `gzkit.handoff_resume_gate.decide`; two live negative controls
(`handoff-resume-unauthorized-write` / `-bash`) fail `gz check` if it stops
refusing.

**Booking the ruling.** When the operator rules, record their VERBATIM words:

```bash
uv run gz handoff authorize --handoff <path> --operator-text "<their exact words>"
```

The gate reads Layer-2, so a ruling given in conversation and never booked leaves
the gate armed — by design. Never author `--operator-text` for words the operator
did not say: that is fabrication, the same failure as fabricating a receipt id.

**What stays permitted while unauthorized:** the § Trust Model reads this skill
requires *before* presenting — `gz state`, `gz status`, `gz obpi status`,
`gz obpi lock list`, `gz handoff list|resume` — **plus `gh` read verbs**
(`gh issue view|list`, `gh pr view|list|diff`, `gh release view|list`) — **plus
plain shell reads** (`git status|log|diff|show`, `grep`, `rg`, `cat`, `ls`,
`head`, `tail`, `find`, `jq`) — plus `gz handoff authorize` itself. These are
load-bearing, not convenience: the § Claim Verification Gate below MANDATES
verifying claims against Layer-2 before presenting. The harness does not always
expose `Grep`/`Glob`, so Bash is the read path; and a handoff's GHI-state claims
("GHI #N CLOSED", "rule on GHI #M") have **no** Layer-2 surface except `gh`. A
gate that forbids the verification its own skill requires cannot be complied
with, and an un-compliable gate gets worked around.

`gh` is admitted as a **read** surface only. `gh issue create` is independently
forbidden by AGENTS.md § Behavior Rules — Always #13 (author GHIs through
`/ghi-author`), and `gh api` is excluded because `-X POST` mutates.

Everything else fails closed — including compound commands (`gz state && rm -rf x`
is not a read of `gz state`), command substitution in **any** quoting form
(`"$(…)"` expands under bash, and posix tokenization cannot tell it from the
inert `'$(…)'`, so both are refused), and write-capable flags on a read's name
(`find -delete`, `sed -i`). Shell metacharacters *inside quotes* are data, not
operators: `grep "A\|B"` and `gh issue list -q '.[] | select(…)'` are reads and
are permitted. The gate blocks execution, never the verification that precedes
it, and never its own recovery path.

Staleness escalates *re-verification depth*, not the authorization requirement:
when staleness is **Stale** or **Very Stale**, the `requires_human_verification`
flag is additionally set to `True`, signaling that the agent must deeply
re-verify the handoff's assumptions (branch, evidence paths, world-state drift)
*before* presenting — but a **Fresh** handoff still does not authorize execution.
Freshness shortens the verification; it never converts an advisory into a license.

### Claim Verification Gate (universal)

**A handoff is Layer-1 narrative authorship. Every assertion it makes about
completion, lock state, gate status, or "now unblocked / now satisfiable" is
UNVERIFIED until checked against Layer-2 truth (the ledger and `gz` state).**
This is AGENTS.md § Behavior Rules — Never #7 applied to resume: *do not read a
status claim as proof of the status — read the ledger.* The Operator
Authorization Gate governs whether you may **execute**; this gate governs whether
you may **believe or relay** what the handoff says. Both fire at every freshness
level, Fresh included.

Before you present any handoff claim to the operator, and before you suggest any
advised step, verify the claim — and verify the **precondition of each advised
step**, because an advised step is only actionable while its precondition still
holds:

| Handoff claim shape | Layer-2 check | Source of truth |
|---------------------|---------------|-----------------|
| "OBPI complete" / "attested-complete" | `uv run gz obpi status <OBPI-ID>` → `Runtime State` / `Completion` | ledger |
| "lock still held" / advises "release the lock" | `uv run gz obpi lock list` | lock registry |
| "Gate N passed" / "gates green" | `uv run gz status` | ledger |
| any artifact-state / readiness claim | `uv run gz state` | artifact graph |
| "tests were green" / coverage claim | re-run the canonical step (see Verification Checklist) | observed output |
| "GHI #N CLOSED / OPEN" / advises "rule on GHI #M" | `uv run gz handoff resume` (**mechanized** for advised steps — GHI #696), else `gh issue view <N> --json state,title` | GitHub issue state |
| "PR #N merged" / "released vX.Y.Z" | `gh pr view <N>` / `gh release view vX.Y.Z` | GitHub |

**This table is the allowlist's authority.** The gate's permitted-read set is
derived from the claim shapes named here — so a claim shape MISSING from this
table becomes a claim the gate structurally forbids you to verify. That is not
hypothetical: the GHI-state rows above were absent until 2026-07-17, `gh` was
therefore never derived into `_PERMITTED_BASH`, and a resume whose advised steps
were both GHI rulings could not check either one. When you add a claim shape,
add its instrument to the allowlist in the same commit.

**Tag every claim you present** as **VERIFIED**, **STALE**, or **UNVERIFIABLE**.
A STALE claim voids any advised step that depends on it: surface the variance and
stop — do not relay the step as actionable. Worked example (2026-06-14): a handoff
asserted *"OBPI lock still held (release is step 1)"*; `gz obpi lock list`
returned **no active locks** — the lock had already been released in a later
session. Relaying "release the lock" as the next action would have acted on a
claim that was false at read-time. The completion claim in the same handoff
verified TRUE (`gz obpi status` → `ATTESTED COMPLETED`); claims are verified
**individually**, never trusted as a block.

### Programmatic RESUME API (`gzkit.handoff_api`)

`resume_handoff`, `list_handoffs`, `load_handoff_chain`, and the `HandoffInfo` /
`ResumeResult` / `StalenessLevel` models are real (OBPI-0.0.65-02). `resume_handoff`
selects the newest handoff for an ADR, classifies staleness
(Fresh / Slightly-Stale / Stale / Very-Stale), flags `requires_human_verification`
for Stale / Very-Stale, and extracts the first next step. Staleness is derived from
an injected `now` timestamp so the classification is deterministic and testable.

```python
from pathlib import Path
from gzkit.handoff_api import resume_handoff

result = resume_handoff(adr_id="ADR-0.0.65", base_path=Path("."), now="2026-07-13T00:00:00Z")
# → result.staleness, result.requires_human_verification,
#   result.first_next_step, result.chain (oldest-first paths)
```

---

## Failure Modes

| Failure | Cause | Resolution |
|---------|-------|------------|
| Template not found | `assets/handoff-template.md` missing or path incorrect | Verify skill directory structure |
| Canonical handoff directory missing | `.gzkit/handoffs/` does not exist at project root | Run `gz init` or create the directory; the path is doctrine-canonical per ADR-0.0.41 |
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
- All 7 required sections populated with session-specific content (no HTML comments or placeholders remaining) — **mechanized** by `validate_sections_populated` since GHI #692; an empty required section is a refusal, not a warning
- Frontmatter validates against `HandoffFrontmatter` Pydantic model
- Full validation pipeline passes (no placeholders, no secrets, sections present **and populated**, references exist)
- File written to correct path: `.gzkit/handoffs/{timestamp}-{slug}.md`

### RESUME
- `list_handoffs()` discovers and sorts available handoffs newest-first
- `classify_staleness()` correctly categorizes handoff age (Fresh / Slightly Stale / Stale / Very Stale)
- Stale and Very Stale handoffs set `requires_human_verification = True`
- `extract_first_next_step()` extracts the first action item for quick resumption
- `load_handoff_chain()` traverses `continues_from` links with depth limiting and cycle detection
- `verify_context()` detects branch mismatches and missing referenced files
- `resume_handoff()` orchestrates the full workflow and returns a `ResumeResult`

---

## Common Rationalizations

These thoughts mean STOP — you are about to lose context across the session boundary:

| Thought | Reality |
|---------|---------|
| "The handoff says the OBPI is complete, so it's done" | The handoff is Layer-1 narrative; completion is a Layer-2 fact. Run `gz obpi status <OBPI-ID>` and read `Completion` before you say "done." AGENTS.md § Never #7. |
| "The handoff says the lock is held — I'll release it (step 1)" | The lock-held claim is unverified until `gz obpi lock list` confirms it. If the lock was already released in a later session, "release the lock" is a void step acting on a stale precondition. Check before relaying. |
| "I'll just relay the handoff's next steps to the operator as the plan" | Relaying a claim is asserting it. An advised step whose precondition is STALE is not a plan, it's misinformation. Tag each claim VERIFIED / STALE / UNVERIFIABLE first. |
| "The handoff is Fresh, so I can just start on its next steps" | Freshness shortens re-verification; it never authorizes execution. The Operator Authorization Gate is universal. Present the advised steps, then wait for the operator to rule. |
| "The handoff is slightly stale but I remember the work" | Stale handoffs trigger the human verification gate for a reason. Memory is not a substitute for explicit verification. Present to the human and wait. |
| "Branch mismatch is fine, I know what I'm doing" | The branch field exists because branch state is part of session context. Mismatch means the world changed under the handoff. Verify with the human. |
| "I'll fill the placeholders in later — let me write the scaffold first" | The validation gate rejects placeholders. "Later" means the next agent inherits TBD/TODO markers. Populate every section now. |
| "All 7 sections are overkill for a 30-minute session" | The 7 sections are the minimum for context preservation. Skipping any one strands the resuming agent in exactly the place that section would have explained. |
| "The Evidence section references files that exist locally — close enough" | Validation checks every referenced path on disk. A broken reference in a handoff is a broken handoff. Fix or remove. |
| "I can summarize the chain in one document instead of following continues_from" | The chain is the lineage. Summarizing it loses the audit trail and the rationale that led to the current state. Traverse it. |
| "This work is uncommitted — I'll handoff after I commit" | Handoffs preserve the in-flight state including uncommitted decisions. Commit pressure is exactly when context is most fragile. Write the handoff now. |

## Red Flags

- Writing a handoff with HTML-comment placeholders still present in any section
- Relaying a handoff's completion / lock / gate claim as fact without a Layer-2 check (`gz obpi status`, `gz obpi lock list`, `gz status`, `gz state`)
- Suggesting an advised step whose precondition you have not re-verified at read-time (the lock-already-released trap)
- Executing a handoff's next steps without explicit operator authorization — at any freshness level (the Operator Authorization Gate is universal)
- Resuming a Stale or Very Stale handoff without presenting it to the human first
- Resuming with a branch mismatch and "I'll fix it as I go"
- Creating a handoff that references files via prose instead of backtick-quoted paths
- Skipping the Decisions Made section because "nothing important was decided"
- Filling Immediate Next Steps with vague intent ("continue the work") instead of concrete actions
- Creating a chained handoff without setting `continues_from`

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `gz-adr-create` | Creates ADR packages this handoff's `adr_id:` may reference (handoff storage is canonical at `.gzkit/handoffs/`, independent of ADR package layout) |
| `gz-obpi-specify` | OBPI briefs that handoffs may reference |
| `gz-adr-closeout-ceremony` | Closeout may reference handoff chain as evidence |
