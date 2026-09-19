# Decision exercise results

Dated 2026-09-19, code baseline `5c777c965`. This is an evaluation record,
not an executable policy or OBPI completion claim.

| Case | Current A | Candidate B | Evidence in both responses |
|---|---|---|---|
| 1: changed inputs | Pass | Pass | Reject stale proof/reviews, finish repair batch, refresh and independently review current proof. |
| 2: repeated root | Pass | Pass | Stop despite remaining rounds; escalate design to the operator. |
| 3: predecessor constraint | Pass | Pass | Read predecessor; omission does not withdraw the still-active gross-total requirement. |
| 4: conflicting history | Pass | Pass | Apply explicit supersession; low severity does not excuse an open mapped finding. |
| 5: successful packet | Pass | Pass | Distinguish generation success from acceptance readiness. |
| 6: indirect SQL consumer | Pass | Pass | Identify double subtraction, schema meaning and historical-data implications; require semantic execution checks. |

Primary scoring is unblinded. Raw responses are retained without rewriting.
Both distinguish source-derived arithmetic from executed results and name unknowns.
Neither executed a workflow or claimed production readiness. Independent scoring
is retained separately in [independent-score.md](independent-score.md).

The independent scorer also returned six passes for each condition. Its protocol
exposed the condition mapping, so this is independent review, **not blinded**
review. The reviewer did not independently verify subjects' file-read histories.

After scoring, the primary agent executed the fixture with Python's in-memory
SQLite driver. The actual schema, writer and SQL report produced revenue 90 for
stored gross 100 / discount 10, and 80 when the writer received net 90 / discount
10. Supplying net at the writer boundary simulates the proposed storage change;
the fixture source was not rewritten. The tuple-shape check passed in both cases.
[fixture-observation.json](fixture-observation.json) retains the observed values.
This confirms the synthetic semantic counterexample, not a defect in gzkit.

## Inputs and reproducibility

Question text and expectations were fixed in [protocol.md](protocol.md) before
dispatch. Each fresh agent received the entire pipeline text, the same entire
handoff skill, and the same fixture. The parent chat and expected answers were
not supplied. Agents report actual files read in their responses. A needed
successive reads after initial tool-output truncation; B reported reading all
1,702 candidate lines and all 514 handoff lines. Input hashes are in
[inputs.json](inputs.json).

Full pipeline texts are the `before-SKILL.md.txt` and `candidate-SKILL.md.txt`
files in `.gzkit/chores/instructions-files-diet/proofs/pipeline-review-2026-09-19/`.
The handoff input is `.gzkit/skills/gz-session-handoff/SKILL.md` at the baseline.
Small shared inputs are retained beside this record: `predecessor.md`,
`successor.md` and `fixture/`. Fixture code is synthetic, not production code.
Python snippets are retained verbatim with `.py.txt` suffixes as evidence
snapshots; the trial inputs used their original `.py` names. The first full
check rejected bare `.py` snapshots for missing module/function docstrings.
Renaming the evidence preserves exactly what the subjects saw without
pretending those deliberately inadequate examples are project modules.

## Disposition

Retain the canonical pipeline. The six-passage history lift preserves the tested
decisions in this sample but shows no decision benefit. Primary input shrinks
1,850 bytes (1.47%); companion text adds 3,125 stored bytes. Byte savings are not
token, latency, cost or comprehension measurements. The candidate remains a
reviewable proposal under #921, not an installed improvement.

There is one response per condition with inherited parent model settings; the
orchestrator exposes no per-run provider build fingerprint. Questions cue the
right obligations and the SQL fixture is small. No randomized repeated trials,
actual pipeline actions, long-session retention, unsuspected-dependency search,
or representative software-task sample was measured. Equal scores establish
neither equivalence nor general reliability. Production Stage-4 measurement
remains the separate #1028 observation task.
