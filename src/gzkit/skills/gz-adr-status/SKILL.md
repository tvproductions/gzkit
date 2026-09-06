---
name: gz-adr-status
description: Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR.
category: adr-lifecycle
compatibility: GovZero v6 framework; uses gz CLI status surfaces
metadata:
  skill-version: "1.13.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 - Evidence Gathering"
gz_command: adr status
invocation: uv run gz adr report | uv run gz adr status ADR-0.3.0
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-06
model: haiku
---

# gz-adr-status

Show ADR status using the current `gz` command surface.

## When to Use

- Inspect all ADRs for pending gates and lifecycle at a glance
- Provide repeatable operator summaries in a consistent table format
- Inspect one ADR's lifecycle, QC posture, and OBPI breakdown without reprinting the global table

## Behavior

When this skill is invoked, **immediately run the appropriate command** — do not ask clarifying questions.

- **No arguments** or `--summary`: run `uv run gz adr report` and present the output.
- **A kind filter** (e.g. "show me the feature ADRs"): run `uv run gz adr report --type feature`. Accepts `foundation`, `feature`, `pool`.
- **With an ADR ID** (e.g., `ADR-0.3.0`): run `uv run gz adr status ADR-0.3.0`. This is the focused single-ADR drilldown — detailed OBPI progress, lifecycle, QC posture, and **closeout blockers**. Pass `--show-gates` only when the user explicitly asks for gate-level diagnostics.

`gz adr report` also accepts a single ADR positionally, but it is not the drilldown: it renders the overview row plus the OBPI table and **no closeout blockers**. Reach for `adr status` whenever the question is *why is this ADR not closing out*.

## Invocation

```text
/gz-adr-status              ← summary (all ADRs)
/gz-adr-status --summary    ← summary (explicit)
/gz-adr-status ADR-0.3.0    ← focused drilldown
```

## Commands

```bash
# Summary view (table across all ADRs)
uv run gz adr report

# Summary filtered to one kind (foundation | feature | pool)
uv run gz adr report --type feature

# Focused ADR drilldown (single-ADR lifecycle, OBPI breakdown, QC posture)
uv run gz adr status ADR-0.3.0

# Focused drilldown with gate-level diagnostics (only when explicitly requested)
uv run gz adr status ADR-0.3.0 --show-gates
```

## Output Contract

Declared form: **table** (both modes).

Locked by: `tests/commands/test_status.py::TestLifecycleStatusSemantics::test_adr_status_renders_shared_table_via_deterministic_renderer` (single-ADR drilldown) and the shared `adr report` table renderer tests in the same module.

### Both modes

- The command output is already visible to the user from tool execution — do NOT re-print it.
- `--json` exists on `gz adr status` **only** — `gz adr report` does not take it (verified 2026-09-06 against the parser). It is for machine consumption; never present raw JSON to a human operator.
- Do not paraphrase, condense, or replace the table with prose unless the user explicitly asks for analysis.
- Optional commentary belongs after the command runs and only when the user asks for interpretation.

## What this output is — and is not

Both verbs render a **Layer 3 derived view** (`docs/governance/state-doctrine.md`). It is
never source-of-truth: every fact traces to Layer 1 canon or the Layer 2 ledger, and
`AGENTS.md` § Never #7 binds that distinction. Relay the table; do not promote it to
evidence for a gate decision.

One arm of it is **known stale today**. The `tracked defects:` annotation on a closeout
blocker is parsed out of the brief's own prose — an authored `(open)`/`(closed)` token is
its only state input, and nothing re-resolves it against GitHub. A defect closed after the
brief line was authored keeps rendering as live, in both directions. Observed 2026-09-06:

```text
$ uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
  - OBPI-0.35.0-10-classification-reader-and-ownership: ledger proof of
    completion is missing [tracked defects: GHI-737]
$ gh issue view 737 --json state,closedAt
  #737 CLOSED closed=2026-08-03T01:26:01Z
```

Tracked at **GHI #966** (open). Until it lands: re-resolve any `tracked defects:` reference
against live GitHub before repeating it to the operator as a live defect.

## References

- Command implementation: `src/gzkit/cli/`
- User docs: `docs/user/manpages/adr-report.md`, `docs/user/manpages/adr-status.md`, `docs/user/manpages/status.md`
