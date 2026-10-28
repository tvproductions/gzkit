# Problem report states

The GitHub issue's role is a **problem report**. The carrier keeps its names: *GHI* in the
tooling, *write-up* in the squawk's vocabulary. Ruled in `docs/rnd/contractor-kit.md`, decision
*B12: the GitHub issue's role is a problem report, with AC 00-71's states* (operator: *"A"*).

## The four states

The definitions are AC 00-71 § 3.2, as the R&D run's source inventory quotes them
(`docs/rnd/contractor-kit/sources/inventory-aviation-civil.md`).

| State | AC 00-71 § 3.2 | In gzkit |
|---|---|---|
| **recorded** | *"A problem that has been documented using the problem reporting process."* | filed through `ghi-author`, after Step 0's prior-art lookup |
| **classified** | *"A problem report that has been categorized in accordance with an established classification scheme."* | carries its `ghi-author` Step 1 class label and its class of failure |
| **resolved** | *"A problem report that has been corrected or fully mitigated, for which resolution of the problem has been verified but not formally reviewed and confirmed."* | the fix commit has landed with its `(GHI #N)` trailer and `ghi-close` Phase 3 has verified it. The commit SHA witnesses this state. |
| **closed** | *"A resolved problem report that underwent a formal review and confirmation of an effective resolution of the problem."* | a review on record has confirmed the resolution, and the issue is closed on GitHub with that record |

## What the ruling changes

- The fix commit's SHA witnesses **resolved**, not closed. A problem report closed by its own
  author's commit with no review on record has skipped a state.
- Only a review closes. The record names that review as the buy-back of C5 (the inspector's
  reinspection limited to the finding) and the final inspection of C10.

## What exists today, and what does not

The review step before GitHub's close, and its record, are diamond-2 work (B12 commission 5).
No mechanism separates resolved from closed yet, and GitHub knows only open and closed. Until the
step lands:

- a reviewer subagent that did not do the fix confirms the resolution against the closure
  contract, and its verdict is posted on the issue before the close (operator ruling 2026-10-28:
  *"Reviewer subagent (Recommended)"*);
- the close comment's **Review:** line (`ghi-close` step 8) names that reviewer;
- a verdict that does not confirm leaves the issue open, at resolved.

`AGENTS.md` § Defect-fix routing carries the same: the commit SHA marks a GHI resolved, and it is
closed only after a reviewer that did not do the fix confirms it (B12 commission 4, landed
2026-10-28).
