# OBPI-0.35.0-04: bounded end-to-end recovery assessment

Assessment input: frozen repository `/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo`; supplied fingerprints `input.patch f040de32`, source `702d569f`. Consultant-only source assessment, not an execution gate. The complete `src/gzkit/commands/content/unown.py`, `src/gzkit/content/ownership.py`, current 312-line plan and 1396-line brief were read. The ledger append boundary and coupled manpage were checked. No implementation, mutation experiment, or physical crash reproduction was performed by this assessor.

All line references below refer to this frozen repository. Evidence subsequently supplied by the parent/test assessor is identified separately.

## Judgment

The current architecture can converge without splitting the OBPI, replacing the journal format, introducing a new framework, or extending the ledger exception. The implementation already has the necessary durable measured-source snapshot, journal, fixed target identity, exact witness matching, declaration barrier retry, and orthogonal source-reconciliation check. The missing pieces are a bounded finalization protocol and proofs covering complete artifact observation, error reporting, and restart.

The design must state its temporal source guarantee precisely: source reconciliation means the raw bytes observed by the finalization read equal the measured, retained bytes. The lock excludes other governed declaration writers, not an ordinary editor. No finite last-read protocol proves that an uncooperative editor cannot save new bytes afterward. This is a clarification of the point at which the existing digest check takes effect; it must not silently replace the accepted requirement to refuse an edit already observed before finalization.

## Binding contract and boundaries

- Plan 156–176 and brief 1025–1054 separate three obligations: declaration/witness settled, source reconciled, recovery cleanup complete. D+E must refuse and preserve both measured bytes and the operator's newer work; witnessing never settles the other obligations.
- Plan 227–241 explicitly requires durable journal absence before dependent deletion **or reuse**, including a retry that enters with no journal. Failure preserves dependents and returns non-success.
- Plan 243–257 distinguishes unrelated orphan residue from current-transaction cleanup. Orphan warnings may permit fresh work after the durability boundary; unchanged old orphans must retain that classification through finalization. This is a permitted recovery policy, not evidence that every non-success on old residue violates safety.
- Plan 220–225 and 261–291 require executing the actual recovery instructions using only retained bytes, reaching a loadable declaration while saving the newer edit externally. They do not require successful reapplication of ratchet-invalid growth.
- Brief 1081–1120 binds ordinary CLI use, ordinary source editing and I/O/interruption/crash failures, with conditional ledger correctness. Brief 1206–1243 explicitly retains #952/#953; no new append/fsync/rollback work becomes an OBPI-04 prerequisite here.
- Direct coherent alteration of `.gzkit` internals is excluded, per brief 1124–1139 and 1245–1258. Existing identity, map and chain checks remain useful; they do not justify reopening that boundary.
- `record_unowned_total` remains an accepted unjournalled future activation seam: ownership.py 1094–1103; brief 696–700 and 1260–1275 require OBPI-05 to lift the journal before activating its production caller.

## Finite proof obligations

1. **One target, one predecessor.** Resolve the stable physical surface alias, acquire its declaration lock, and consume only a declaration with that target identity. Retain the case-variant CLI success case. All computed paths and subsequent snapshot checks remain bound to that target.
2. **One measured version.** Compute section membership, byte span, successor floor and successor map from one raw UTF-8 source version. Retain those exact bytes before publishing a journal. Blank attestation and ordinary invalid fresh input do not create a transition.
3. **Publication order.** Durable retained source precedes a durable journal; durable declaration precedes witness append; witness append is interpreted under the accepted ledger assumptions. Treat replace-before-directory-barrier failure as visible but durability unknown, never as proof that nothing landed.
4. **Restartable store states.** A predecessor+journal derives the same successor and event ID; a landed but unwitnessed declaration re-establishes its durability before witnessing; a witnessed successor matches the exact existing witness and never duplicates it. Persistent storage failure retains enough material for another retry.
5. **Source reconciliation stays independent.** Changed source in A/B/C/D cannot be treated as clean completion. Preserve the measured snapshot and never overwrite the user's source automatically. An unreadable/missing/undecodable live source also must have a truthful retained-byte recovery route; automatic extraction on every such error is not required.
6. **Finite final source observation.** Both fresh commit and replay compare the final raw source observation with the journal's digest before cleanup. An edit detected there refuses. A later independent edit is outside what that completed observation proves; do not invent endless rereads or a new editor-lock requirement.
7. **Durable journal absence.** Remove the journal, then establish durability of its absence in its actual parent directory before removing or reusing companions. Apply the same boundary when no journal is visible on entry. Failure cannot delete/reuse the old source snapshot or extract.
8. **Complete, classified artifact observation.** Observe the final and staging extraction families without mistaking a failed directory listing for an empty result. Current-transaction cleanup errors prevent success; an observed old orphan may warn under the accepted policy, retaining its old classification through later cleanup. Ignore coverage and cleanup cover the same generated filename families.
9. **Executable recovery and honest accounting.** The printed next steps use verified retained bytes, preserve newer bytes externally, and end at actual canonical loader acceptance. Diagnostics distinguish a failed attempt from a proven absence, identify existing durable effects, and do not promise an unsupported ratchet increase. Evidence for these obligations must identify the final source revision.

## State and persistence inventory

| Cut or retry state | What is already established | Remaining obligation |
| --- | --- | --- |
| Before a new retained-source write | Fresh declaration was validated under the target lock | Establish durable journal absence before reusing fixed names; publish the new snapshot durably |
| Retained-source write failed, no journal | No new declaration or witness; final/staging snapshot may exist | Confirm durable journal absence; classify residue without asserting a transition completed |
| Journal publication fails | Source was retained; journal may be absent, old, or newly visible depending on cut | Retain bytes; an existing valid journal is replayable, absence requires the durable-absence boundary before reuse |
| A: valid journal + predecessor | Journal contains attestation, successor and measured digest | Refuse observed source divergence; derive successor from the valid predecessor; durably land declaration then witness |
| B/C: successor landed + witness absent | Successor visible; declaration durability may be unknown | Refuse observed divergence; re-establish declaration barrier; append exactly the expected witness |
| D: successor + exact witness | Store obligation settled under accepted ledger assumptions | Independently check source; then cleanup |
| D+E | Stores settled, observed source differs | Non-success, no duplicate witness, no automatic source rewrite, retain restore material |
| Journal unlink failed | Journal still may be needed on retry | Non-success; do not delete dependent files |
| Journal unlink visible, absence not yet durable | Process observes no journal, restart might still recover it | Barrier before companion deletion or fixed-name reuse; failure retains companions |
| Journal absence durable | Old journal cannot later regain authority under the storage assumptions | Cleanup/reclassify residue; a new transaction still needs normal validation and its own durable snapshot |
| Final raw source read matched | This observed source version reconciles with the transition | Cleanup and accounting; no claim that later external editor writes are prevented |

All generated journal and source files share the declaration parent (`ownership.py` 960–1008); extraction can be in another directory. Ordered calls alone do not establish the cross-directory deletion order. The source and journal publication paths already use a shared writer; successful declaration barrier on replay also commits prior directory metadata in that same parent. Do not invent an additional journal-publication defect merely because replay does not call a separately named journal-fsync function.

## Observed implementation gaps

### 1. Required durable-absence boundary is missing — implementation defect

`unown.py` 1783–1812 unlinks the journal then sweeps companions without a directory durability barrier. Its explanation at 1796–1805 explicitly argues the barrier is unnecessary; plan 227–241 supersedes that argument. The no-journal-on-entry branch at 1318–1327 also sweeps immediately. Either path can remove or later overwrite a fixed-name snapshot before journal deletion is durable. This is a code/protocol ordering defect within the declared crash model; this assessment does not claim a reproduced physical power loss.

Correction: one shared operation establishes durable journal absence in the journal's actual parent and fails before dependent mutation when it cannot. Use it both after unlink and on absent-on-entry retry, before cleanup or any new snapshot write. Keep the existing failure classes and journal format.

### 2. Artifact discovery can report complete cleanup without observing the family — implementation and proof defect

`_staging_residue` at 1589–1618 converts a listing `OSError` into `[]`, asserting that named-file removals will report the fault. They need not: listing and removal are different operations. `_sweep_recovery_residue` at 1751–1780 can therefore report success with an unobserved staging copy still present. The parent reports its test assessor independently observed this using a real staging file plus a simulated listing error; that observation is separate from this source assessment.

Correction: carry a failed/unknown discovery result into the existing current-versus-orphan policy, instead of treating it as observed absence. Test the concrete full filename family and exact parent directories, not merely a mocked call count. Parent also reports that an existing directory-fsync assertion accepted any directory descriptor and a wrong-parent mutation passed; the required proof must identify the actual parent being made durable.

### 3. Accepted orphan policy needs a coherent implementation, not a one-line warning change — policy completion

The entry orphan handler at 1699–1748 still exits 2. The sweep at 1751–1780 has only `after_completion: bool`, and final cleanup scans the same names again. Simply replacing the entry exit with a warning would reclassify a persistent old orphan as a new transaction's failure at finalization, contrary to plan 249–251.

Correction: after durable journal absence, record the observed unrelated orphan failures and retain that distinction through finalization. Fresh validation and durable snapshot publication remain mandatory. A fixed snapshot successfully replaced for the new transaction is then current material; a persistent unrelated old staging file stays an old orphan. No need for persistent new schema or a general transaction framework.

### 4. Recovery prose still overstates what it proves — implementation defect, bounded diagnostic work

- `_reconciliation_sequence` at 1859–1863 still advises raising the floor using `unown` before restoring an enlarged unowned edit; the manpage repeats it at line 351. If unowning another owned section adds span `x`, both floor and live unowned span increase by `x`; available slack is unchanged. This is not a general route for accepting an enlarged already-unowned section. End the recovery at restored measured bytes plus successful retry and canonical load, with newer work saved externally. Reapplication remains a separate coverage decision.
- Extraction failure at 992 says no extract exists, although `write_bytes_atomically` can replace the file and then fail its directory barrier (`ownership.py` 911–930), or an older extract can remain. D+E prose at 1968–1970 also states extraction is retained without conditioning that statement on successful extraction. Report unconfirmed extraction/durability accurately; do not infer absence or a verified restore file from an exception.
- `_read_surface_or_exit` at 2051–2062 runs before replay at 2164–2167. For a pending journal plus missing/non-UTF-8/unreadable current source, it only says verify existence and UTF-8. The retained snapshot remains intact and the manpage names it at 373; this is **not** proof of data loss or an intrinsically unrecoverable transaction. Demonstrate the route using that retained snapshot and make this early refusal point to it. Do not require automatic extraction merely for uniformity.

## What is already sound within the boundary

- Fixed transaction target and consumed declaration identity checks: `unown.py` 86–261, 443–483, 614–729, and fresh load 2196 onward. With governed writers serialized, repeated reads of `.gzkit` state do not by themselves establish an ordinary identity race.
- Exact existing-witness comparison, including landed section-map digest: 486–543. Witness existence alone no longer licenses cleanup.
- Retained raw bytes before journal publication: 1430–1494. Byte-oriented writer uses file fsync before replace and POSIX parent-directory fsync after replace: `ownership.py` 860–930.
- B/C declaration durability retry before append: `unown.py` 1046–1099 and 1398–1402. A persistent barrier failure does not license witnessing.
- Final source binding on both fresh and replay paths: 1424, 1549, 1871–1974. Witnessed D no longer bypasses source reconciliation.
- Current journal-unlink failure retains companions: 1807–1811. The missing piece is the durability ordering after successful/previously completed unlink.

## Accepted residuals and optional hardening

Ledger append currently flushes but does not fsync and rollback uses the pre-append size (`ledger.py` 250–280). These are the named #952/#953 dependencies, not fresh OBPI-04 blockers. Keep the conditional claim explicit; do not market the overall operation as unconditional power-loss-safe while those assumptions are unmet.

Windows uses the file barrier but the shared writer's directory barrier is explicitly POSIX-only (`ownership.py` 922–930). The finite proof must identify the actual platform/storage guarantee exercised; an arbitrary fsync count or historic Windows import/suite success is not proof of directory-entry persistence. This assessment does not prescribe an unexamined Windows API or create a new platform waiver.

Legacy journals without the digest or retained source cannot supply a modern retained-version guarantee merely because replay accepts them. Keep legacy compatibility claims distinct from the current writer's proof. No schema redesign is required to prove the current producer and its crash/retry states.

Cryptographic journal authentication, immunity to coordinated `.gzkit` rewrites, global editor exclusion, continuous source coherence after final observation, and a reusable generic transaction framework are optional hardening or different contracts, not acceptance requirements for this repair.

## Bounded convergence path

1. Record the final source-observation boundary and recovery success endpoint in the existing plan/manpage. Keep all accepted ledger and threat-model boundaries unchanged.
2. Implement the shared durable-journal-absence operation and use it on both cleanup entry paths before dependent deletion or fixed-name reuse. Verify the exact parent directory and each failed-barrier branch.
3. Complete the current-versus-orphan artifact policy across discovery, entry cleanup, new snapshot publication, and finalization. An unknown listing is not an empty family; old orphan identity survives the invocation.
4. Correct the coupled recovery messages and prove the retained-byte route for ordinary changed, missing, invalidly encoded, or temporarily unreadable source as applicable. End the route at restored source plus loader acceptance, with newer bytes kept externally.
5. Run one finite state/cut matrix: fresh source publication; journal publication; A replay; B/C barrier retry; D replay; E and D+E refusal; journal unlink/barrier; absent-on-entry reuse; final/staging cleanup/discovery faults. For each, observe declaration, exact witness count, source bytes, retained files, exit and next-step truth; then recover using only retained bytes. Include repeated failures and the fixed-name reuse sequence. Exercise a source edit before the final read and identify the boundary of an edit afterward.
6. Bind the targeted tests, mutation demonstrations, coupled docs and required quality checks to the final source revision before the existing Step 4b review. Use the same finite acceptance obligations to judge the result; do not create another unbounded adversarial expansion loop.
