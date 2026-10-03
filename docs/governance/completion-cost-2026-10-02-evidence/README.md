# Evidence — why repair displaced feature work, measured 2026-10-02

This is a **dated record**, not a ruling. It holds the measurement behind the campaign
amendment draft [`amendment-draft-r2.md`](amendment-draft-r2.md), which is **DRAFT, NOT
RATIFIED** and binds nothing until the operator rules on it. Re-run the scripts rather than
trusting the figures the draft transcribes.

**Ruled 2026-10-03.** The operator ratified all six proposals, three of them with a change.
The ruling is § Amendments 2026-10-03 of
[`build-to-1.0-campaign-2026-09-20.md`](../build-to-1.0-campaign-2026-09-20.md); the draft
is kept unedited as the record of what was put to the operator. The operator rescinded
P3's batch initiation the same day (§ Amendments 2026-10-03 (2)); P3's draw order stands.

## Cost per OBPI completion (`cost_per_completion.py`)

Read-only. It reads `.gzkit/ledger.jsonl` and two inputs fetched into this directory:

```
git log --format='%x1e%H%x1f%aI%x1f%s%x1f%b' > cost_gitlog.txt
gh issue list --state all --limit 5000 --json createdAt,number > cost_issues.json
uv run python cost_per_completion.py
```

Run the commands from this directory. For each OBPI whose first `completed` receipt falls
on or after 2026-04-01, it reports, by completion month:

- lock-to-receipt hours;
- ledger events naming the OBPI;
- retry and refusal signals;
- in-window commits citing the OBPI;
- handoffs written in the window;
- GitHub issues opened in the window.

Each is given as a median and p90. Signals introduced on known dates (Stage-2 dispatch
records, acceptance records, TTL warnings) are new instrumentation, so the draft counts only
signals instrumented the same way across July–September: re-claimed locks and relaunched
pipelines.

## Completion-path size (`gate_population_snapshot.py`)

It re-applies HEAD's `gate_population` membership rule
(`src/gzkit/governance/trust_audits/gate_population.py`) to one snapshot's `src` tree and
prints the precomplete checks, the complete refusals and the `gz check` steps as JSON. Run it
once per snapshot, from an extracted copy:

```
git archive <sha> src | tar -x -C <dir>
cd <dir> && PYTHONPATH=src uv run python <path-to>/gate_population_snapshot.py
```

The snapshots the draft uses are the last commits before each date:

| Date | Commit |
|---|---|
| 2026-04-15 | `9de9554b9` |
| 2026-05-15 | `7c5dc526a` |
| 2026-06-15 | `5f8c5975e` |
| 2026-07-15 | `c55c810e7` |
| 2026-08-15 | `d1862cdf1` |
| 2026-09-15 | `95d8e243d` |
| HEAD at measurement | `25ac528f8` |

The rule follows same-module reachability only, so function counts understate depth.

## Review

A read-only Codex sanity pass reviewed the first draft. What it changed is recorded in the
draft's own § Review record.
