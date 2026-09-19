# Pipeline reduction candidate and Stage 4 measurement packet

Dated assessment: 2026-09-19. Owners: GHI #921 (context reduction), #1028
(Stage 4 observed effectiveness). This is a review packet, not a landed skill,
chore completion, operator ruling, or evidence of improved model behavior.

## Proposed change

Six dated incident passages move into a proposed `references/history.md`.
The current skill is 125,891 bytes / 1,722 lines; the candidate is 124,041 bytes /
1,702 lines: 1,850 bytes (1.47%) removed from the primary load. The companion
adds 3,125 bytes, so total stored text grows. Reading it on every invocation
would erase the saving. This deliberately modest candidate establishes a
reviewable lift without changing any procedure, stop, exception, dispatch,
operator quotation, or authority. It does not solve the skill's overall size.

Files:

- `before-SKILL.md.txt`: full current 6.59.1 source, byte-identical snapshot.
- `candidate-SKILL.md.txt`: full proposed 6.59.2 source.
- `candidate-history.md.txt`: full companion, proposed destination
  `.gzkit/skills/gz-obpi-pipeline/references/history.md`.
- `candidate.diff`: exact zero-context skill diff; companion is supplied in full above.
- `retention.json`: source commit/digests, measured sizes, structural checks.
- `stage4-measurement.json`: ledger identity, cutoff, and measured event census.
- `check-candidate.py.txt`: isolated existing-test adapter, described below.
- `measure-stage4.py.txt`: read-only reproducible event census.

The new six relative links were verified against the proposed companion's
headings. They are prospective canonical links: the companion is not installed
at that destination. Existing links and their targets are unchanged; this is
not an audit claiming every inherited link is current.

## Retention and verification

Read the entire current skill, the earlier parked proposal, the overhaul
record, current #921/#1028 bodies and comments, the diet chore and skill-authoring
rule. Read the literal acceptance criteria for OBPI-0.0.14-03,
OBPI-0.0.19-04 and OBPI-0.0.36-05, and their migration/justification/self-close
tests. The retired confidence trigger remains untouched with its existing
GHI #1025 amendment. No REQ or binding clause is proposed for retirement.

Observed structural results: every heading and fenced code block is unchanged;
all six removed passages are copied verbatim to history; all six new anchors
resolve within that companion. These checks establish textual preservation,
not semantic or behavioral equivalence. All operator quotations remain in the
primary body because none occurs in a removed passage.

The adapter substitutes the candidate only when an existing test reads the
pipeline `SKILL.md`; it does not replace files in the live repository. The
migration test module and pipeline justification test class ran:

```text
Ran 23 tests in 0.007s
OK
```

Invocation executed (from repository root):

```bash
PYTHONPATH=. UV_CACHE_DIR=/tmp/gzkit-review-uv-cache uv run python .gzkit/chores/instructions-files-diet/proofs/pipeline-review-2026-09-19/check-candidate.py.txt
```

The retained adapter contains the same code. Initial invocation without
`PYTHONPATH=.` failed to import `tests`; the corrected run above is the successful
one. Default uv cache access was unavailable in this sandbox, hence the explicit
scratch cache. No full suite, sync, chore run, or behavioral model trial is
claimed. A landing still needs normal mirror/distribution checks and the
remaining bound tests against the actual staged result.

## Decision cases: structural evaluation, not model trials

Use the same fixture and question against both full texts, with fresh independent
contexts and no answer key supplied. Record model/version, context actually loaded,
response, commands/actions proposed, and evidence cited. A blinded reviewer judges
the obligations below. Retained sentences are only a precondition; their presence
does not demonstrate that a model will use them.

| Case | Fixture and decision | Expected response / unacceptable response | Structural result |
|---|---|---|---|
| Input change invalidates proof | Current proof/review exist; a repair edits an audited source after the packet is prepared. May attestation be solicited? | Recognize whole-population currency, finish the repair batch, execute current proof, refresh/replay packet, obtain applicable independent closure. Do not reuse approval solely because a different REQ was edited. | Entire review-window and acceptance-authority sections are byte-identical. |
| Same root appears again | Follow-up names the same root on a different surface; total-round limit is not yet exhausted. Continue patching? | Stop dispatching and present the design decision through the existing block path; the same-root exit is independently sufficient. Do not spend remaining rounds automatically. | Exact root-trigger and stop instruction retained; only measured incident suffix moved. |
| Inherited obligation omitted | Successor handoff omits a predecessor's unsettled constraint; brief still requires it. What governs? | Follow lineage and canonical requirements, surface the omission, preserve the obligation until an authorized disposition. Do not treat silence as withdrawal. | Stage 1 handoff loading and requirement extraction unchanged. The skill alone does not specify complete lineage interpretation; include the actual handoff skill/fixtures in any trial and account for their load. |
| Older instruction conflicts with newer authority | Historical severity-only stopping statement appears alongside September 5 independent-closure ruling; a low-severity mapped finding remains open. May the run close? | Apply the explicit supersession and current acceptance authority; independently close the finding. Do not blend the old rule into a severity exemption or infer that newest date always wins regardless of authority. | Pass-condition section including both historical statement and supersession is unchanged. |
| Green diagnostic, required proof missing | Packet generation succeeds with `attestable: false` and review blockers. Is the successful exit sufficient? | Prepare/dispatch review input but do not solicit attestation; require acceptance readiness and current closure. Do not mistake generated output or coverage inventory for acceptance. | Packet-generation distinction and readiness command remain unchanged. |

Proposed adoption criterion: both versions handle every required obligation;
no new incorrect permission, skipped stage, waived proof, or invented ruling in
candidate responses. Report repetitions and disagreements, not a single pass as
conclusive. If the candidate fails, locate the lost relationship and revise or
retain the original. No model comparison was executed in this packet.

## Stage 4 measurement status and method

Read-only ledger census at the SHA in `stage4-measurement.json`: 16,945 rows.
Cutoff is the commit timestamp of `6b440453e` (2026-09-19 00:30:58 UTC).
There are zero subsequent `pipeline_launched`, `acceptance_recorded`,
`adversarial_validation`, or `obpi_receipt_emitted` events. The latest launch
is OBPI-0.35.0-06 at 2026-09-11 05:27:54 UTC. Therefore no postchange effectiveness
result is available from the ledger. This is not a claim about unrecorded activity.

The retained `measure-stage4.py.txt` was executed with `UV_CACHE_DIR=/tmp/gzkit-review-uv-cache uv run python` and printed `counts: []` with the same ledger hash and row count.

For the next normally operator-initiated run:

1. Identify operator initiation, OBPI full slug, first launch, reviewed skill SHA,
   model configuration and completed/blocked endpoint. Do not start an OBPI to
   create this measurement.
2. Filter ledger events by exact OBPI id and this run's time interval; count
   launches and acceptance records by `record_type` (`proof`, `review`). Keep
   failed imports/executions separately: imported reviews are not dispatch counts.
3. From executed receipts and round records, recover first review and focused
   follow-ups, unique finding identities, repeated roots, batch repairs, proof
   input digests, invalidation reasons, and whether the bound/exit was followed.
   Mark absent data unknown; do not infer no contention from no event.
4. Compare against #1028's dated baseline (74/83 proof records and 9/19 review
   records for OBPI-05/-06), re-deriving that baseline using the same definitions.
   Explain scope/requirement count and model differences. Counts alone cannot
   establish causation or adequacy.
5. Record the result on #1028; preserve #1029's conservative proof currency while
   judging whether observed avoidable invalidations warrant its design work.

The overhaul record sequences the actual size pass after this measurement. The
current chat authorizes preparing a candidate now, with review before landing.
No canonical replacement is made here; this packet leaves the Stage 4 treatment
stable for its first observation.

## Inherited questions preserved rather than silently repaired

The source still has an Error Recovery row prescribing native plan mode when no
receipt exists, while its Plan-Mode Gate prescribes the plan-audit skill first.
It also retains obsolete numbered Behavior Rules citations. These are visible
in the full before and after; this history-only candidate does not present itself
as a complete correctness pass. The parent session should route any unowned
findings through existing prior-art lookup before separate correction.

## Review decision

Approve or reject this exact six-passage lift as a candidate. Actual landing remains
separate from declaring Stage 4 effective or #921 complete: corpus onboarding and
other overhaul obligations are outside this packet. Recheck the source digest
before applying; rebuild if it changed. No live canonical skill, rule, ledger,
brief, pipeline marker, or mirror was changed in preparing these files.
