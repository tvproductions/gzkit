---
name: gz-insights-remember
description: Record a course-correction, defect, defect-resolution, or discovery insight via the governed gz insights remember verb. Use when an operator course-corrects in flight (Behavior Rule #11), an agent surfaces a defect/discovery, or a defect-resolution outcome needs recording — never hand-append a line to .gzkit/insights/agent-insights.jsonl.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-13
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
   lesson — this is the required record for Behavior Rule #11's in-flight
   course-correction mandate), or `discovery` (a survey finding).
2. Supply `--scope` (the surface or skill the record names) and
   `--summary` (a one-sentence record body). Both are required and fail
   closed when empty.
3. Optionally attach `--evidence <command-or-path>` (repeatable — pass it
   once per witnessing command or file) and `--next-action <text>`
   (what changes structurally to prevent recurrence).
4. Run the capture:

   ```bash
   gz insights remember --type <defect|defect-resolution|improvement|discovery> \
     --scope <surface-or-skill> --summary "<one-sentence body>" \
     [--evidence <command-or-path> ...] [--next-action "<structural change>"]
   ```

5. The command fails closed (non-zero exit, no line written) when
   `--type`, `--scope`, or `--summary` is empty, or when `--type` is out
   of the `InsightType` enum — construction is what enforces the schema.

## Validation

- A new line is appended to `.gzkit/insights/agent-insights.jsonl` (the
  file/dir is created on first use).
- The line's `ts` field is stamped with the current UTC instant
  automatically — no manual timestamp is ever required.

## Example

```bash
# Record a Behavior Rule #11 course-correction insight
gz insights remember --type improvement --scope obpi-pipeline \
  --summary "governed author verb replaces hand-authored appends" \
  --next-action "delete the hand-authored append path"

# Record a defect with witnessing evidence
gz insights remember --type defect --scope gzkit.insights \
  --summary "verb drifted from schema" \
  --evidence "uv run -m unittest tests.commands.test_insights_cmd"
```
