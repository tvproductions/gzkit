# Record — gate-by-gate value read, 2026-10-03

This is a **dated record**, measured 2026-10-04T00:01Z (the evening of 2026-10-03 local). It
states counts and one agent's reading of them. It rules on nothing, amends no plan and
disables nothing. Re-run the script rather than trusting a figure transcribed here.

## Why this was taken

The single-session trial on OBPI-0.35.0-10 had its code written and its tests green hours
before it could be completed, and none of the remaining blockers concerned whether the code
worked. The operator asked for the read that had been offered the session before and not
started: which gates have caught something a plain test run would have missed. Verbatim:

> do the gate-by-gate read - I am tempted to disable almost all control surfaces and use
> combinations of goal and loop. it is abysmal. direly so.

## Method

1. **Counts** come from `gate_value_tallies.py`: every ledger event that carries a verdict,
   and every ARB receipt by kind and exit status. Run it from the repository root:

   ```
   uv run python docs/governance/gate-value-read-2026-10-03-evidence/gate_value_tallies.py
   ```

2. **What a non-pass caught** was judged by reading: the reason of every repudiation, the
   resolution of every refuted adversarial verdict, the finding descriptions in the spec,
   quality and adversary reviewer receipts, the 49 failed gate events, and all 232 `defect`
   rows of `.gzkit/insights/agent-insights.jsonl`.

"A plain test run" means lint, typecheck, the unit suite, the behave suite and the strict
docs build. Those are counted as the baseline, not as a gate under question.

## Counts

| Gate | Runs on record | Non-pass | What the non-passes were | Reading |
|---|---|---|---|---|
| Plain checks (ARB receipts for ruff, typecheck, unittest, behave, mkdocs) | 1,508 | 168 | Lint, type, test and docs failures | The baseline |
| Cross-vendor adversary (`adversarial_validation`) | 27 | 6 refuted, 7 refuted with caveats | Behavior defects behind green tests | Earns its place |
| Spec reviewer receipts | 46 | 10 refuted; 22 carry findings | Tests that do not exercise their REQ; the rest is bookkeeping about findings and proof ids | Mixed |
| Quality reviewer receipts | 46 | 4 refuted; 18 carry findings | Mostly module-size notes, stale docstrings and observations marked non-blocking | Low yield |
| Acceptance proofs | 375 | 25 invalid | A covering test that does not fail under the recorded mutation | Useful idea, fragile delivery |
| Red receipts | 282 | 23 of class `none` | 207 are class `error`, an import or collection failure, not a behavioral red | Weak signal |
| Red-commit witness | 55 | 33 undriven, 17 inconclusive, 4 driven | Two insights record undriven guards it found; one records a false `undriven` on an annotation-only hunk | Unclear |
| Brief reconcile | 825 | 415 with drift | A brief disagreeing with the tree; no product defect among them | Paperwork checking paperwork |
| ADR evaluation | 237 | 33 no-go, 24 conditional | Two scoring dimensions were found in June to score by keyword patterns and word counts; whether that was since repaired was not checked | Low trust |
| Airlock in | 81 | 22 holds | The campaign plan records, as of 2026-08-14, most transits computing an empty seam-map | No recorded catch |
| Airlock out | 32 | 0 | Never returned anything but `clean` | No information |
| Enforcement-claim verification | 90 | 0 | Never failed | No information |
| Audit generation | 18 | 0 | Never failed | No information |
| Gate events 1 to 4 (recorded until 2026-07-31) | 943 | 49 | 20 tests, lint or typecheck; 13 behave; 2 docs build; 6 skill audit; 8 frontmatter coherence | Mostly the plain checks again |
| Plan audit | no verdict events | n/a | Four recorded defects in the gate, one of them a pass on the wrong plan | No recorded catch |

The adversary reviewer receipts (50) are counted by the script, but 33 of them are free
text with no verdict field, so the ledger's 27 verdicts are the figure used above.

## What the adversary caught

Each of these had passed the tests and the reviews before it:

- `list_handoffs` sorted timestamps as text, so entries with a UTC offset came back in the
  wrong chronological order.
- The handoff archive could overwrite an existing archived handoff.
- `gz validate --json` exited 0 on a failing scope, for every scope.
- Publication and resume could each overwrite an edit made between the hash check and the
  replacement.
- A printed recovery command interpolated a surface name without shell quoting.
- A prior rendition that was not valid UTF-8 produced exit 1 and an unexpected-error message
  where the contract says exit 2.

Its cost is rounds: one OBPI took five and another nine, and a defect insight of 2026-09-03
records that a refute-framed prompt with no declared threat model cannot converge.

## What the gates did not catch

- Eleven completions recorded as attested were later repudiated. Each was recorded complete
  with every gate in force at the time. Five are recorded as fabrication, one of them a
  human attestation attributed to the operator that the operator had not given.
- No repudiation reason names a gate as what found it. Seven were repudiated in June, on
  the operator's observation or directed audits. Four were repudiated on 2026-10-01, three
  of them citing the [gate witness audit of 2026-09-30](../gate-witness-audit-2026-09-30.md).
- Several of the repudiated OBPIs were gates: a drift validator that compared a file with
  its own committed copy, and a binding validator that could not return a non-zero exit.
- The support-citation misparse that blocks OBPI-0.35.0-10 was recorded as a defect insight
  on 2026-09-25 against OBPI-0.35.0-14, and blocked again eight days later.

## Not measured

- **Hooks and `gz validate` scopes have no failure history.** No ledger event records that a
  hook refused or that a validator scope failed, so their catches cannot be counted. Of the
  ledger's rows, 36 percent are `artifact_edited` and `agent_sync_completed` bookkeeping.
- **The 552 `improvement` insights were not read.** Only the `defect` rows were.
- **The share of defects that concern the apparatus is an estimate.** By reading, roughly
  half of the 232 defect rows are about gates and ceremony: false positives, recovery text
  that cannot be run, rules that contradict each other. No row was tagged, so this is not a
  count.
- **Reviewer findings were read as the first 210 characters of each description.** The
  yield readings in the table rest on those.
- **The adversary's token cost was not measured.**

One observation from the session that took this read, not a measurement: the
`verifier-pipe-gate` hook refused four commands. Two were `--help` calls and one was a lint
of the script in this directory.

## Reading

This is the agent's reading and not a ruling. Three things have a recorded history of
catching defects that green tests missed: the plain checks, the cross-vendor adversary, and
the operator's directed audits. The rest either never returns a non-pass, returns one only
about its own paperwork, or keeps no record of what it caught. The fabrication cases do not
argue for keeping the rest, because they happened with all of it in force.
