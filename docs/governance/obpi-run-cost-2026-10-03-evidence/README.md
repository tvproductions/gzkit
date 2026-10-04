# Evidence — token cost of one OBPI run, measured 2026-10-03

This is a **dated record**, not a ruling. It holds the baseline for a trial the operator
ruled on 2026-10-03 (verbatim: *"yes, run the trial on obpi-10"*): run OBPI-0.35.0-10 in a
single direct session and compare its cost with the OBPI-0.35.0-08 pipeline run. Re-run the
script rather than trusting the figures transcribed here.

## Script (`session_token_cost.py`)

Read-only. It reads Claude Code session transcripts for this repository, which live outside
the repository on the machine that ran the session, and sums the usage each API call
reported. Run it from the repository root:

```
uv run python docs/governance/obpi-run-cost-2026-10-03-evidence/session_token_cost.py \
    <session-id> --siblings-between <ISO-start> <ISO-end>
```

It reports three groups: the named session, its in-process subagents, and sibling sessions
whose rows all fall inside the window. The sibling rule is a heuristic and is described in
the script's docstring.

## Baseline — OBPI-0.35.0-08, session `553e5afb-48e8-4cae-be4a-db046a3690ba`

Window `2026-10-03T06:55:00+00:00` to `2026-10-03T11:35:00+00:00`.

| Group | Transcripts | API calls | Cache-read tokens | Cache-write tokens | Output tokens | Peak context |
|---|---|---|---|---|---|---|
| Orchestrator session | 1 | 260 | 118,627,618 | 1,676,930 | 299,116 | 743,855 |
| In-process subagents | 3 | 145 | 13,390,717 | 1,712,721 | 10,698 | 232,736 |
| Sibling reviewer sessions | 12 | 152 | 21,910,398 | 2,866,542 | 358,223 | 269,644 |

The orchestrator's context was 55,206 tokens at its first call and was never compacted.
The session also resumed a handoff and amended the campaign plan before the pipeline was
launched, so its figures include that work.

The change the run landed is commit `2f39139d7`.

## Trial launch prompt

The operator launches the trial in a fresh session, without resuming a handoff in it, by
pasting the text below after `/goal`. The route it names was read from the code and the
help text on 2026-10-03 and had not been run when this record was written.

```
Every [behavior] REQ in the OBPI-0.35.0-10-classification-reader-and-ownership brief has a
passing @covers test, and every command in the brief's `verification:` list exits 0.

This is an operator-ruled trial (2026-10-03: "yes, run the trial on obpi-10").
- Do not load the gz-obpi-pipeline skill and do not dispatch subagents.
- Launch with `uv run gz obpi pipeline OBPI-0.35.0-10-classification-reader-and-ownership --no-subagents`,
  then declare it with `uv run gz obpi dispatch OBPI-0.35.0-10-classification-reader-and-ownership --single-driver --reason "operator-ruled single-session trial"`.
  Follow what the CLI prints.
- Edit only paths in the brief's allowlist.
- Anything you find that is not one of the brief's REQs: record it once with
  `uv run gz insights remember` and move on.
- While working, run only the brief's own unit test module. Run the full verification
  list once, at the end.
- Stop and show me the state when the condition holds, or when a `gz` command refuses twice
  for the same reason. Do not run `gz obpi complete` or the `human-review` operation of
  `gz obpi acceptance`; those take my words.
```

Completion on this route takes two operator rulings: the verbatim judgment recorded by the
`human-review` operation of `gz obpi acceptance`, and the attestation `gz obpi complete`
records. The ledger then marks the completion `degraded-human-only`.

## What the trial compares

The same three groups for the OBPI-0.35.0-10 session, beside the size of the change it
lands. The two OBPIs differ in scope, so the comparison is indicative, not controlled.

## Remaining evaluation

The [independent trial evaluation](trial-evaluation.md), measured 2026-10-04 UTC,
records the full-session cost comparison, verification results, requirement review,
reproducible defects and limits. The unchanged implementation fails independent
review despite passing the listed checks; the lower recorded cost does not establish
equivalent quality. No completion or apparatus change was authorized by that result.
