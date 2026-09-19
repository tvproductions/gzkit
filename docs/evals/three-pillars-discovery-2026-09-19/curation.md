# Case curation and oracle challenge

Dated 2026-09-19, before subject dispatch. Work order GHI #1045.

The main-session agent curated H from the original handoff complaint and the
historical producer, both renderers, session-start budget handling and resume
skill. The issue's claim that traversal was absent was already false at the
selected snapshot: `resume_handoff` populated `chain`, while the renderers did
not consume it. The task retains the observed symptom rather than prescribing
the issue's diagnosis. Expected criteria therefore reward finding existing
machinery and its omitted consumers, not building a second traversal.

A quality-reviewer independently derived C from issue #989 and historical
acceptance input identity, review admission, readiness, provenance checks, tests
and governance prose, before comparing the repair diff. The existing test and
prose explicitly prescribed environmental invalidation. The repair's changed-file
list omitted that prose, demonstrating why historical patch recall is not the
oracle. Interpreter/platform policy is not a mandatory scored remedy.

A second quality-reviewer independently derived S from original issues #771/#708
and historical sync, trailer validation, tests and rules. The initial suggested
“fingerprint reuse” case was a mistaken recollection: this was auto-add staging
and semantic attribution. Local history resolved the repair as `45b4a51a1` and
its parent as `da4470b8d`. The reviewer also withdrew a proposed fail-closed
criterion after reading the historical function and tests' explicit fail-open
inspection-error policy. Those corrections preceded the frozen criteria and
all subject runs.

The C curator then challenged the H oracle and common protocol against the
extracted snapshot. Accepted with one clarification, incorporated before freeze:
H3 can preserve bounded traversal while explicitly declining completeness; it
must not demand new truncation metadata or traversal/API redesign. H1–H6 and the
translation of C's oracle were otherwise accepted. S is explicitly a weaker
hidden-discovery case and a useful state/attribution control.

All six runs use fresh contexts with inherited parent model settings and no
model override. The mapping lives in `inputs.json`; the scorer receives response
labels and case identities, but not that mapping. Content may reveal treatment.

Snapshots use `git archive` of the recorded parent commit. Python's safe tar
filter rejected three absolute/outside harness symlinks in H and C; each omitted
path and reason is listed in `cases.json`. All ordinary source, tests, docs and
configuration remain. No Git checkout, worktree or production workflow was
created. Historical snapshots are temporary and are not installed in main.
