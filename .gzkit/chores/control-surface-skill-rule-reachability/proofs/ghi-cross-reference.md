# GHI Cross-Reference — Pass B

> Chore: `control-surface-skill-rule-reachability` (Lite lane, audit-only)
> Run: **2026-10-10**, maintenance visit E. Supersedes the 2026-08-09 cross-reference.

A gap is **known-blocking** when a filed GHI, or a rule's own version note, records the defect
its pattern produces. It is **latent** when no record was found. Each lookup below was a named
issue read by number, or one scoped keyword search of the first four matches. A scoped search
supports "no match in the first four", never "no such issue exists" (`gh-cli.md` § Census).
Issue states are not transcribed here; GitHub renders them at each reference.

## Known-blocking (17)

| Row | Record | Why it matches |
|---|---|---|
| N1 | #492 | the missing coupling check between `skill-version` and `last_reviewed` |
| N7 | #317 | bare verification commands where ARB receipts are required |
| N8 | #373 | the instructions-files budget the skill restates as a line count |
| N9 | #552, #1017 | src and tests commits landing without a `Task:` trailer |
| N10, B23 | #652 | the 600-line module limit applied as a binding threshold |
| B01 | #1139 | worktree-and-branch premises falsified by later canon |
| B06 | #710 | the whole cumulative `RELEASE_NOTES.md` passed as a release body; fixed in `gz-patch-release`, not here |
| B08 | `gh-cli.md` 0.6.0 and 0.7.0 notes | the operator twice widened the allowlist after a skill step proved unreachable (`comment`, `reopen`); `gh issue edit` is the third instance |
| B12 | #643 | agent-authored acceptance evidence presented unverified; fixed for the pipeline, not for the closeout ceremony |
| B14, B21 | #822 | "Gate 5" naming a step that is not OBPI or ADR completion; these two skills were not swept |
| B15 | insight `session/uv-run-rule` | 40 bare interpreter calls in the session that ran this audit, 2026-10-10 |
| B18, B22 | #1044 | the canonical chore copy; the rule changed on 2026-09-28 and four skills kept the old label or the old recovery step |
| B20 | #837 | promotion criteria routed through the sealed foundation kind |
| B26 | #492 | a skill edit with no version or review-date bump |

## Latent (18)

N5, B02, B03, B04, B05, B07, B09, B10, B11, B13, B16, B17, B19, B24, B25, B27, B28, B29.

Notes on the nearest records found, none of which is the same defect:

- B02 is latent by design: `weaponeering.md` landed 2026-10-10 as advisory, and the pipeline change belongs to the sortie layer proposed in `ADR-pool.sortie-layer-crew-split`.
- B05: #886 records pipeline state living in a Layer-3 marker; it does not record the hand-author fallback.
- B07, B11: #1030 records that the `gz issue file` Step 0 pre-flight has no mechanism.
- B13: #262 records the closeout ceremony running on whatever model defaulted.
- B17: #818 re-ratified the boundaries on 2026-09-29; the skill predates that ruling.
- B04: #284 was N2's record and concerns a pinned model, not tier selection by file count.

## Found while cross-referencing

- #1013 records that the verifier-pipe gate reads heredoc bodies as shell commands. This session met it four times while writing proofs; it is tracked.
- #1125 and #1124 bear on the stale `gz-tidy` rationalization row recorded below the bar.
