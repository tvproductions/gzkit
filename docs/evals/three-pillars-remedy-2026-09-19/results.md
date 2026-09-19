# Three pillars — obligation-tracing remedy comparison

Dated 2026-09-19. Persona: main-session. GHI #1048.
Baseline: `f4a0395a711157406504c85f6cc62664aafddb33`.

**Do not adopt the added procedure.** Both conditions scored 28/30 complete
criteria, with equal totals on each task. The candidate used 73 shell/read
calls versus baseline's 57. This bounded comparison provides no demonstrated
discovery benefit to justify adding it to canonical instructions.

## What was tested

The operator approved moving from appraisal to testing one remedy for incomplete
obligation discovery. The [candidate](candidate.md) asks an assessor to trace
authority, producers, consumers and verification, reconcile source disagreement,
and avoid expanding into independent work. It is an experimental prompt addition,
not a new rule, skill or runtime implementation.

An independent curator selected two fresh prospective tasks from current code.
A second agent challenged their semantic criteria without seeing the candidate.
The [protocol](protocol.md), [criteria](cases.json), [corpus](corpus.json) and
[prompts](inputs.json) were frozen before twelve fresh subjects ran: three per
task and condition. Tasks and budgets were identical across conditions; only
the candidate instruction differed. The [method](method.md) records the bounded
corpus, authoring/review limits and two-at-a-time dispatch constraint.

## Observations

| Task | Baseline runs and complete criteria | Candidate runs and complete criteria |
|---|---|---|
| Configured source-root scanning | T01 5/5; T07 5/5; T09 5/5 | T03 5/5; T05 5/5; T11 5/5 |
| Prefixed mirror-path identity | T04 4/5; T06 4/5; T12 5/5 | T02 4/5; T08 5/5; T10 4/5 |
| Total | 28/30 | 28/30 |

Independent scoring separated discovery, relationship reasoning and consistent
application. The scorer received case criteria and neutral-ID raw answers, not
the assignment key or candidate text. Wording could still reveal treatment;
perfect blinding is not claimed. [Independent scores](independent-scores.json)
retain excerpts and ambiguity notes; [summary.json](summary.json) joins the
scores to assignments and cost measurements after scoring.

The four incomplete mirror responses lose only M5 application: they propose
paired mirror checks and legitimate creation controls, but do not clearly propose
a `./`-prefixed canonical CREATE positive through brief validation. T08 explicitly
covers mixed prefix forms; T12 combines an explicit prefixed canonical control
with mixed-prefix extraction. Primary adjudication retains the independent
scores while labeling this distinction borderline: a more generous reading of
the four responses would give both conditions 30/30. Neither reading changes
the non-adoption decision. Missing explicit evidence is not proof of an inability
or a demonstrated implementation regression.

The scorer found no unsafe policy change, fabricated execution or unsupported
expansion warranting an adverse flag. There are differences in proposed
documentation and test scope; these are not evidence that the work was executed
or that every proposed addition is necessary. Raw responses retain those choices.

| Cost proxy, six runs per condition | Baseline | Candidate |
|---|---:|---:|
| Total shell/read calls | 57 | 73 |
| Median calls | 9.5 | 13 |
| Total response words | 3,828 | 3,968 |
| Median response words | 636.5 | 655 |

The candidate used 16 additional calls, about 28% more, with identical criterion
totals. These are observed workload proxies, not token, latency or financial
measurements. Elapsed trial latency was not collected as a comparable end-to-end
metric. No significance test or population estimate is warranted.

## Integrity and limitations

All twelve saved answers match their returned final answers after trimming
outer whitespace. All prompts and frozen artifacts retain their hashes; all
1,939 supplied regular files are unchanged. Responses used 7–13 calls and
612–687 words, within the 16-call/850-word limits. See
[verification.json](verification.json) and [traces.json](traces.json).

Primary trace review found reads confined to the supplied corpus/task files
and writes confined to designated answers. Missing doctrine/persona paths and
some truncated reads were disclosed; no subject opened earlier evaluation
artifacts or the real checkout in the recorded shell commands. The source
corpus excludes historical evaluation directories physically, correcting the
prior study's search-exposure mechanism. It still contains historical comments
in current code and ordinary evaluation-related production code. This is not
an assertion that every byte was free of historical context or that an external
filesystem sandbox enforced the boundary.

The source task reached the rubric ceiling in both conditions. Two selected
tasks, three repetitions per condition, and a bounded corpus cannot demonstrate
general reliability or that the procedure is never useful. The omitted
governance/history population limits whole-repository authority judgments.
The supplied task descriptions explicitly state their desired behavior; these
results do not measure discovery of an unspecified task or hidden requirements.
The app's fresh-subagent harness and inherited model settings were held alike;
no provider build fingerprint or cross-model replication was obtained.

## Disposition and relation to the three pillars

The predeclared rule required improvement on BOTH tasks, no unsafe policy or
false execution claim, and no repeated new criterion regression. The first
condition fails: neither task improves. The candidate stays in this evaluation
record only. Canonical instructions, skills and runtime code remain unchanged.
The evidence does not justify stronger procedural pressure, another instruction
layer or a new general comprehension gate.

This completes the proposed remedy comparison. It does not establish that
pillar-three false closure is solved. Pillar-one native delivery evidence and
the previous bounded runtime/documentation repairs remain in the
[current reassessment](../three-pillars-current-2026-09-19/results.md).
These new tasks are not comparable to that study's tasks or the earlier
historical pilot; equal or higher scores here cannot establish improvement
over either. Sparse attention or any other model-internal causal explanation
remains untested.

Independent leads are durably retained in cases.json and raw responses:
source-root selection and prefixed mirror handling are prospective stimuli;
additional observations concern plan containment, promotion ordering, manifest
precedence/loading, census wording and delivery/advice mapping. They are static
observations with incomplete ownership/history review, not new selected repairs
or verified feature requirements. No runtime change is silently authorized by
an assessment prompt. Production Stage-4 observation and currency design remain
separate under GHI #1028 and GHI #1029.

The repository's required staged check and guarded commit/sync complete delivery;
their observed results and commit identity are recorded in GHI #1048's closure.
No model-assessment score substitutes for those checks or for human attestation.
