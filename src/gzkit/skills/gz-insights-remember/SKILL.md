---
name: gz-insights-remember
description: Use when the operator course-corrects or a defect, resolution or discovery needs recording through gz insights remember.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-10-18
metadata:
  skill-version: "0.3.0"
model: haiku
gz_command: gz insights remember
---

# gz insights remember

## Purpose

Wield `gz insights remember` to append one schema-valid record to the
append-only insights store at `.gzkit/insights/agent-insights.jsonl`
(GHI #575). The store accumulates four trust-bearing record kinds —
`defect`, `defect-resolution`, `improvement`, `discovery` — and was
historically hand-appended, which drifted from the `InsightRecord` schema
(date-only timestamps, malformed evidence, missing required fields).
`remember` closes that gap: it **constructs** an `InsightRecord` first
(validating `type`, `scope`, `summary`) and only then serializes and
appends — a missing or malformed required field fails closed (non-zero
exit, no line written) before it ever reaches disk. This verb **replaces**
hand-authoring a JSONL line for the insights store.

## Procedure

1. Identify the record kind via `--type`: `defect` (an observed problem),
   `defect-resolution` (the fix outcome), `improvement` (a post-correction
   lesson — the record `AGENTS.md` § Behavior Rules requires when the operator
   course-corrects in flight; rationale in `docs/governance/behavior-rules.md`
   § Always #11), or `discovery` (a survey finding).
2. Supply `--scope` (the surface or skill the record names) and
   `--summary` (a one-sentence record body). Both are required and fail
   closed when empty.
3. Optionally attach `--evidence <command-or-path>` (repeatable — pass it
   once per witnessing command or file) and `--next-action <text>`
   (what changes structurally to prevent recurrence).
   Say whose words the record carries with `--source operator|agent`
   (default `agent`): pass `operator` only for the operator's own words; an
   agent's reading of them stays `agent` (operator ruling 2026-10-18). When
   the record replaces an earlier one, name it with `--supersedes <ts>`; a
   `ts` no record carries is refused before anything is written.
4. Run the capture:

   ```bash
   uv run gz insights remember --type <defect|defect-resolution|improvement|discovery> \
     --scope <surface-or-skill> --summary "<one-sentence body>" \
     [--evidence <command-or-path> ...] [--next-action "<structural change>"] \
     [--source operator|agent] [--supersedes <ts>]
   ```

5. The command fails closed (non-zero exit, no line written) when
   `--type`, `--scope`, or `--summary` is empty, or when `--type` is out
   of the `InsightType` enum — construction is what enforces the schema.

## Validation

- A new line is appended to `.gzkit/insights/agent-insights.jsonl` (the
  file/dir is created on first use).
- The line's `ts` field is stamped with the current UTC instant
  automatically — no manual timestamp is ever required.
- One `insight_recorded` event is appended to the ledger naming the record:
  its `ts`, a SHA-256 of the line, the `source`, and any `supersedes`. A
  recorded line edited by hand afterwards fails `gz validate --insights-shape`.

## Before a recorded failure becomes a rule

A single failure stays an insight (maxim 13). To propose that a recurring failure
become a rule, cite its records and run the recurrence check; propose the rule
only on exit 0:

```bash
uv run gz insights recurrence <insight-ts> '#<N>' '#<M>'
```

You judge that the cited records share one class of failure; the verb checks
only the count against `data/recurrence_threshold.json` and that every pair is a
session lease apart. Manpage: `docs/user/manpages/insights-recurrence.md`.

## Example

```bash
# Record a course-correction insight
uv run gz insights remember --type improvement --scope obpi-pipeline \
  --summary "governed author verb replaces hand-authored appends" \
  --next-action "delete the hand-authored append path"

# Record a defect with witnessing evidence
uv run gz insights remember --type defect --scope gzkit.insights \
  --summary "verb drifted from schema" \
  --evidence "uv run -m unittest tests.commands.test_insights_cmd"
```
