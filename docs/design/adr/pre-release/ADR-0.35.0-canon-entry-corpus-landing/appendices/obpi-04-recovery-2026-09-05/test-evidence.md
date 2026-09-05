# OBPI-0.35.0-04 recovery test evidence

Read-only assessment of the fixed snapshot at `/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo`, 2026-09-05. Persona: quality-reviewer, with test-evidence focus. No source/test edits, new governance events, or full-suite run. The two bounded probes below use existing test fixtures in temporary directories and in-memory monkeypatches. Their printed import paths confirm the snapshot modules were exercised.

The current tests provide substantial, semantic recovery evidence. They are strongest for normal A/B/C/D replay, changed-source reconciliation, and failed unlink followed by retry. They do not yet establish the cleanup durability obligation, and a real staging-enumeration fault currently produces clean success with recovery bytes still on disk. One existing durability test accepts a sync of the wrong directory.

## State-to-evidence map

Paths and line numbers below refer to the fixed snapshot. `unown tests` means `tests/commands/test_content_unown.py`; `ownership tests` means `tests/content/test_ownership.py`.

| State or obligation | Existing behavioral evidence | What it proves and its limit |
|---|---|---|
| Before a transition: refused authorization/invalid target | `TestContentUnownFailClosed`, unown tests 192–257; identity tests in `TestContentUnownRound9`, 2204–3102 | Blank attestor/reason, unknown/already-unowned sections, aliases/foreign snapshots, and unreadable declarations are distinguished. Assertions include unchanged declaration/ledger or the canonical identity actually witnessed. These are prerequisites, not crash proofs. |
| A: journal retained; declaration unlanded; witness absent | `TestRecoveryProtocolStateA.test_the_unlanded_branch_refuses_repeatedly_then_recovers`, 3737; `test_state_a_recovery_writes_through_the_durable_writer`, 3802 | Fails the real declaration replacement twice, retains journal/source, then reaches a loadable state with exactly one raise and one witness. The second test reaches the real writer during replay and observes an attempted directory barrier. |
| B: declaration visible; durability unconfirmed; witness absent | `TestRecoveryProtocolStateB.test_landed_recovery_retries_the_barrier_and_refuses_while_it_fails`, 3271 | Fails the directory fsync following the declaration's real replacement, confirms the raised floor is visible, retries under the same fault, then heals with one witness and canonical loader acceptance. It demonstrates handling of an OS error at that boundary, not post-power-loss persistence. |
| C: declaration durable; ledger append absent | `TestContentUnownIsRecoverable.test_a_retry_completes_a_transition_interrupted_at_the_ledger_append`, 587; `test_a_recovered_transition_raises_the_floor_exactly_once`, 624 | Before retry, canonical load rejects the missing witness; retry repairs it under the declaration's existing event ID; another invocation cannot double-raise. Ledger failure is injected before `Ledger.append` or `_append_event_once`, so partial durable ledger writes are not tested here. The latter is the already-disclosed GHI #953 boundary, not a new request to broaden this work. |
| D: declaration and witness present; source unchanged; journal retained | `TestRecoveryProtocolStateD.test_a_witnessed_transition_only_clears_its_journal`, 3858; `test_the_clear_only_run_does_not_claim_the_raise_an_earlier_run_made`, 3900 | Arranges D by replacing cleanup with a no-op; retry writes no declaration or event, removes recovery state, and attributes the earlier raise correctly. This is controlled state arrangement, not a killed-process test. The directory fault injector in the first test targets declaration replacement, so adding a legitimate cleanup-directory barrier must not make the test demand zero cleanup barriers. |
| C + E: source changed after interrupted append | `TestRecoveryProtocolStateE.test_a_changed_source_recovers_from_retained_material_alone`, 3410 | Uses the implementation's retained bytes, checks the extracted digest against the journal, preserves the newer edit, blocks a different section, restores from the implementation's extract, and reaches a loadable one-witness state. It deliberately keeps no test-owned copy of the old source for recovery. |
| D + E: already-witnessed transition plus newer source | `TestRecoveryProtocolStateDPlusE`, 4303, 4340, 4369, 4423 | Separately observes one witness, non-success, unchanged newer bytes, and retained recovery material across three retries; reconciliation from retained bytes ends with cleanup and a loader-accepted state. The last test executes the described save/diff/restore/retry steps and confirms the externally saved newer edit survives. |
| Legacy journal without source digest | `TestLegacyJournalStillObservesTheLiveSurface`, 5056, 5088; prior landed replay test 1704 | A renamed section still fails coverage checks with retained journal/source; unchanged legacy state D clears successfully without duplicating its witness. This explicitly covers the legacy observation fallback, not byte-level source identity for unversioned old journals. |
| Source bytes/identity during transaction | `TestContentUnownReadsTheSurfaceInsideTheLock`, 1419, 1486, 1510; `TestContentUnownBindsTheSurfaceToTheTransaction`, 1638, 1679, 1704; `TestContentUnownRound8`, 1796–1978; CRLF tests 2354, 2395 | Covers before-lock edits, precommit edits, postcheck edits, both fresh/replay finalization, raw-byte digest distinction, and CRLF preservation/change detection. Initial non-UTF-8 source is exercised. An unreadable source during an already-pending recovery is not given the same end-to-end repeated-fault/restore/retry demonstration. |
| Failed journal removal | `TestRecoveryCleanupIsItsOwnObligation.test_a_failed_journal_removal_retains_its_dependents_and_reports_the_fault`, 4568 | `Path.unlink` raises while the journal exists: non-success, specific fault, retained journal and source, one witness. It tests an unlink that did not occur, not an unlink that occurred but whose directory metadata was not durable. |
| Journal gone, dependent removal failed | `test_a_retry_sweeps_residue_left_after_the_journal_is_already_gone`, 4611 | Snapshot removal fails after journal removal; next invocation sweeps the snapshot before its independent already-unowned refusal. It proves the no-journal sweep runs, but not retry of a failed deletion durability barrier. |
| Extraction staging family | `test_an_interrupted_extraction_leaves_staging_residue_that_is_swept`, 4651; `TestStagingResidueGlobIsLiteral`, 4906; `TestRecoveryArtifactsAreIgnored`, 4094 | Residue is produced by the real atomic writer with replacement and staging-unlink faults, and later removed. Literal metacharacter matching protects other surfaces' residue. These tests do not inject failed staging enumeration; the probe below shows that gap is live. |
| Orphan staging before any journal | `TestOrphanResidueSweepReportsOnlyWhatItObserved`, 4828 | Real snapshot staging residue, predecessor declaration unchanged, no witness/journal; failed sweep does not claim a completed transition. The test intentionally leaves the exit disposition unasserted because its comment records an unresolved operator question. Keep that limitation explicit; do not report it as proof of a particular orphan exit policy. |
| Unreadable or malformed journal/declaration | `TestJournalStorageFaultIsNotForgery`, 4945, 4992; declaration replay test 2886; `TestContentUnownReplayJournalValidation`, 836–1199; landed map/row tests 1200–1402 | Storage failure is distinguished from malformed/semantically incoherent recovery material, with no unproven witness or ownership change. Missing/altered journal fields and a same-ID but semantically different witness have rejection tests. The unreadable-journal test asserts retained journal and prose, not a repeated-failure/healed-retry lifecycle. |
| Authoritative loader and serialized writers | Ownership tests: `TestLoadDeclarationChainValidation`, 354–822; chain/prefix tests 2022–2416; `TestRecordUnownedTotalReadsTheFloorInsideTheLock`, 1658–1847; unown serialization test 374 | Canonical loader rejects wrong event type/surface/floor/map, broken chain edges and unowned-byte overflow. Writer tests ensure lock-scoped predecessor reads and preserve another committed section flip. These assertions make loader acceptance and one-witness assertions in the recovery tests substantive. |
| Atomic writer | `TestWriteDeclarationAtomically`, ownership tests 1515, 1543, 1553, 1603, 1622 | Failed replacement preserves the old target; success leaves exact bytes/no staging; regular-file fsync uses a writable handle. The directory test currently proves only that some directory was synced, as demonstrated below. |

## Concrete remaining evidence work

1. **Cleanup durability must be demonstrated at the deletion boundaries.** Production `_remove_if_present` (`unown.py:1554–1586`) only unlinks; `_clear_recovery_state:1796–1805` explicitly claims order/sweep suffice without a barrier. Existing tests 4568/4611 inject unlink failure only. They cannot establish the Sep-5 requirement quoted in their own class docstring: “Account for interruption between deletions, including their durability barriers.” Add a bounded trace/fault test that requires journal unlink → successful barrier on the journal's parent → dependent deletions, plus failure after the unlink and before that barrier: no clean success, dependents still usable, repeated retry while the fault persists, then completion once healed. The journal-absent retry must re-establish the pending deletion barrier before consuming dependents. Also prove the final dependent-removal directory barriers complete before cleanup is called complete. Use the platform contract selected by the design assessment; POSIX directory durability is what the existing writer exposes today.

2. **Failed staging enumeration currently becomes false cleanup success.** `_staging_residue` (`unown.py:1615–1618`) catches `OSError` and returns `[]`; `_sweep_recovery_residue` can then finish without learning what residue remains. The bounded probe below reaches this with a real producer-created temporary extract. Add a table-driven lifecycle over post-completion and no-journal sweeps: enumeration fails repeatedly, clean completion is not claimed, actual retained residue remains trackable, then a healed enumeration/removal clears the real artifact. Keep witness count, live source bytes, and later loader acceptance as the semantic assertions. This is the existing complete-extraction-file-family obligation.

3. **Strengthen the existing atomic-writer directory witness.** Ownership test 1622 collects directory names but at 1652 only asserts `synced_dirs` is nonempty. It passes when `os.open(path.parent, O_RDONLY)` is redirected to an unrelated directory. Assert the synced fd identifies the target parent (device/inode is preferable to `/dev/fd` display text), and record ordering: staging file fsync before replace, correct parent fsync after replace. Include wrong-directory and wrong-order negative controls. The current writer implementation is ordered correctly; the defect here is the test's claimed proof.

4. **Finish the source-readability corners without expanding the policy.** Add one small parameterized lifecycle for A + changed source, and pending A/C/D with an initial transient source-read failure: non-success, no new witness/declaration, retained usable journal/source, repeated failure safe, then restoring read access/original bytes through the already-authorized recovery route reaches the expected one-witness, loader-accepted state. Existing changed-source demonstrations cover C and D, not A; the initial unreadable/non-UTF-8 test covers fresh work. For retained-source read failure or extraction-write failure, assert the operator is never instructed to diff a nonexistent extract, and retrying after the fault clears produces the verified measured bytes. The production helper already branches this way (`unown.py:953–1003`); only the extraction replacement-failure arm currently has a lifecycle test. These are supporting completion proofs; they do not ask for arbitrary `.gzkit` tampering or a new recovery mechanism.

The minimum correction should center on items 1–3. Item 4 closes the finite source-axis evidence table using the same fixtures and existing policy. No additional grand-total suite count substitutes for any of these assertions.

## Observed bounded probes

`probe_wrong_directory_test.py` ran one existing unittest under an in-memory mutation. Observed:

```text
ownership_import: /private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/content/ownership.py
redirected_directory_opens: [(<target-parent>, <different-temp-directory>)]
existing_test_survived_wrong_directory: True
Ran 1 test in 0.001s
OK
```

`probe_residue_enumeration.py` used the existing isolated filesystem, `_crash_at_replace` producer fault, and the implementation's retained snapshot. Observed:

```text
unown_import: /private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src/gzkit/commands/content/unown.py
first_exit: 2
extraction_exit: 2
residue_before: 1
listing_fault_calls: ['.Doc.md.unowning-recovery.*.tmp']
retry_exit: 0
residue_after: ['.Doc.md.unowning-recovery.mxvlewq1.tmp']
journal_after: False
snapshot_after: False
Completed the interrupted un-owning of section 'alpha-section' of 'Doc.md'. Unowned-byte floor rose from 26 to 83. Attested by g0: probe
```

Re-run from the snapshot cwd; these commands use the live project's installed environment while forcing all project/test imports to the fixed snapshot:

```bash
UV_CACHE_DIR=/tmp/gzkit-health-uv-cache PYTHONPATH=/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src:/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo uv run --no-sync --project /Users/jeff/Documents/Code/gzkit python -B /private/tmp/gzkit-obpi04-assessment-4dt92ti0/probe_wrong_directory_test.py
UV_CACHE_DIR=/tmp/gzkit-health-uv-cache PYTHONPATH=/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src:/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo uv run --no-sync --project /Users/jeff/Documents/Code/gzkit python -B /private/tmp/gzkit-obpi04-assessment-4dt92ti0/probe_residue_enumeration.py
```

## Limit on the evidence

The present tests inject Python/OS-call exceptions and construct post-interruption states; `_crash_at_replace` injects replacement and cleanup failures, not process death. They exercise the code's handling of an observed fault while the process and filesystem cache remain alive. No test here cuts power, remounts a filesystem, or observes which directory entries survive an actual power loss. Ordered fsync assertions and a deterministic crash-state model can prove the implementation obeys the chosen durability protocol; they must not be presented as empirical proof of physical power-loss survival on every filesystem. This distinction preserves the existing scope rather than inventing a new test program.
