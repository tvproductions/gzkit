# /gz-insights-remember

Record a course-correction, defect, defect-resolution, or discovery insight via the governed `gz insights remember` verb. Use when an operator course-corrects in flight (Behavior Rule #11), an agent surfaces a defect/discovery, or a defect-resolution outcome needs recording — never hand-append a line to `.gzkit/insights/agent-insights.jsonl`.

---

## Purpose

`gz insights remember` is the **governed author verb** for the append-only
insights trust surface at `.gzkit/insights/agent-insights.jsonl` (GHI #575).
It wraps the mechanical writer `gzkit.insights.append.append_insight_record`:
the payload is *constructed* into an `InsightRecord` (stamping `ts`, validating
`type`/`scope`/`summary`) and only then serialized to a single JSONL line, so a
missing or malformed required field fails closed — non-zero exit, no line
written — instead of drifting past the schema the way hand-authored appends did
(contradiction C4, ADR-0.0.72). It is the surface Behavior Rule 11 directs
agents to.

## Invocation

```bash
gz insights remember --type <improvement|defect|defect-resolution|discovery> \
  --scope "<surface or skill the record names>" \
  --summary "<one-sentence record body>" \
  [--evidence "<command or path>" ...] \
  [--next-action "<what changes structurally to prevent recurrence>"]
```

- `--type` is validated against the `InsightRecord` enum; an out-of-enum value
  fails closed at argparse (non-zero exit, no write).
- `--type`/`--scope`/`--summary` are required; an empty value raises a
  `ValidationError` at record construction — the verb exits 1 and writes no line.
- `--evidence` is repeatable and becomes the record's `evidence` list.
- `ts` is stamped automatically (ISO8601 with timezone; date-only is rejected).

## When to use

- **Course-correction (Behavior Rule 11):** the operator names a wrong
  assumption, redirects an interpretation, or calls out drift in flight — record
  an `improvement` before completing the corrected work.
- **Defect / discovery:** an out-of-scope defect that cannot be fixed now, or a
  survey finding worth persisting, when a GHI is not the right home.
- **Defect-resolution:** the outcome of a fix worth witnessing in the T2
  insight stream.

## Related

- `gz validate --insights-shape` — every record validates against `InsightRecord`
  (`extra="forbid"`, ISO8601 `ts`, `type` enum, `evidence: list[str]`).
- ADR-0.0.72 (meta-governance coherence); GHI #575, GHI #358, GHI #357.
