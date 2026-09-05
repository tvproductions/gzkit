# OBPI-0.35.0-04: assessment and execution path

Prepared 2026-09-05. Persona: main-session. This is execution assistance for the existing OBPI and Claude's active implementation. It is not an OBPI completion or human attestation.

## Decision

**Update after the user's platform findings:** the lifecycle corrections below are bounded, but the platform durability contract is not yet established. Read `PLATFORM-FINDING.md` first. The subsequent live change now treats an unavailable mandatory barrier as a warning; it violates the current preservation/non-success rule without making fresh operations usable on the same filesystem. That change must not be counted as a closed finding.

Keep the current implementation and complete the recovery, evidence, and documentation corrections against a consistent platform contract. The evidence does not justify a rewrite, another ADR, a scope split, a generic transaction manager, or reopening the accepted ledger exceptions. The earlier assessment's unconditional statement that the design could converge within all accepted constraints was too strong: Windows support and equivalent durability remain unproved.

This OBPI classifies sections as corpus-owned or unowned, measures their byte spans, maintains the unowned-byte allowance, and provides an attested command to un-own a section and raise that allowance. Its difficult part is making the declaration, ledger witness, retained source, and recovery files agree across interruption and concurrent editor saves.

The reported history and current artifacts show why it consumed days: recovery obligations were being established and corrected during implementation review. Completion of one obligation repeatedly became an unsupported premise for another branch. Passing tests covered many individual failures without establishing the complete lifecycle. Long histories and stale delivery text then gave subsequent implementers conflicting guidance. My earlier incremental prescriptions contributed to that approach; this assessment replaces them with one contract and executable evidence.

## What was actually examined and executed

The assessment read the complete brief, plan, ownership implementation, unown implementation, recovery tests, and relevant manpage/rulings. Two stable snapshots captured the active dirty work without modifying Claude's production files. All test imports were verified to resolve to the selected snapshot.

| Evidence | Earlier snapshot | Later candidate |
|---|---:|---:|
| Existing unown, ownership, and declaration-validation tests | 170 pass | 176 pass |
| Added finite recovery diagnostics | 2 of 7 methods pass | 6 of 7 methods pass |
| Journal-present/absent cleanup ordering and repeated barrier failures | Four methods fail | All four pass |
| Correct-parent writer check and wrong-directory negative control | Both pass | Both pass |
| Real extraction staging, listing failure on two retries, then healed cleanup | Fails on both faulted retries | Fails on both faulted retries |

The seven diagnostics are in `test_recovery_contract.py`; commands and proof limits are in `recovery-contract-runner.md`. Results preserve fault calls, actual outputs, artifact state, source identity and witness checks. These are diagnostic tests, not a full quality-gate attestation or empirical power-loss experiment.

Candidate identity:

- Base commit: `397301c629bf3007943c43295f0adaafbd8c7fa8` plus the recorded dirty patch.
- `unown.py` SHA256: `e08c3ba587ec04206473635e5d76e7dcb2d2471df430f051884786a88d7f5b6d`.
- `ownership.py` SHA256: `9cb125685de5c87907d5d73e3b20dd79a3aeffe69048ab469b500f3b491c3360`.
- Full capture: `candidate.json` and `candidate-input.patch`.

A later read confirmed the live production files still matched these hashes; Claude's test file had continued changing. The 176-test result belongs to the captured candidate, not every subsequent test edit.

Scoped baseline receipts are `arb-step-obpibaseline-0608f3b81cd945d9a4fc6e0976f1958d` and `arb-step-obpicandidate-76c9f5b8312942ada61d3c6f1d5e5f87`, under each snapshot's `artifacts/receipts/` directory.

## One contract to finish against

Keep three obligations independent:

1. The intended declaration transition has its exact ledger witness, subject to the accepted ledger limitations.
2. The source version observed for completion reconciles with the measured transaction version.
3. This transaction's required recovery cleanup has completed.

An existing witness does not establish source reconciliation or cleanup. A missing journal does not establish the history of orphan files. A failed directory listing does not establish that the directory contains no relevant files.

The source guarantee concerns the bytes actually observed at the completion check. It cannot prevent an independent editor from saving afterward. Retain #952/#953 as the accepted ledger boundary; do not extend those exceptions to ownership/source/cleanup failures. Do not reopen arbitrary `.gzkit/` forgery or the inactive ordinary-ratchet helper's already-disclosed OBPI-05 sequencing.

The complete existing-contract matrix is in `contract-assessment.md` (A1–A20). It organizes existing requirements; it is not twenty new tasks or twenty new reviews. Existing tests already cover much of it, as mapped in `test-evidence.md`.

## Ordered execution work

### 1. Retain the candidate's verified cleanup correction

The candidate now establishes durable journal absence before removing or reusing dependent material, including an invocation that starts with no journal. The new tests verify the actual parent directory, operation ordering, two failed retries, preservation of measured bytes, and healed completion without another witness. Do not reimplement this correction based on the earlier snapshot reports.

This paragraph refers to candidate `e08c3ba5`, not the later platform change `ab23a8eb`. The latter catches unsupported-barrier errors and bypasses this boundary; its counterexample and disposition are in `PLATFORM-FINDING.md`.

The candidate also carries explicitly observed orphan paths through finalization and excludes the reused snapshot path from that exemption. Continue under the current plan's orphan policy. No new policy ruling is needed for the following defect.

### 2. Correct failed discovery of recovery files

`_staging_residue` currently turns a failed listing into an empty list. A real interrupted extraction leaves a real temporary file; with listing failure, the retry exits 0 and announces completed recovery while that file remains. The next invocation also omits the storage fault. Once listing heals, the same implementation can find and remove it.

Use an enumeration operation that surfaces I/O errors, preserve literal filename matching, and carry discovery errors into the existing current-transaction versus orphan reporting paths. The report must name the directory/file family that could not be inspected and the storage error; it must not claim an observed file list or completed sweep. An unknown file family is not a set of known, previously warned orphan paths.

Removing only the local `except OSError: return []` is insufficient: the installed Python 3.13 `glob._Globber.wildcard_selector` itself suppresses directory-enumeration `OSError`. `Path.iterdir`/`os.scandir` can provide an error-reporting boundary. Match the literal `.<target-name>.` prefix and `.tmp` suffix, preserving the existing filename-metacharacter and neighboring-file protections.

The supplied failing test is the acceptance case: an implementation-created extraction staging file; positive evidence that listing failed on two invocations; truthful non-success for incomplete current-transaction cleanup; fault disclosure on later entry; a healed sweep; unchanged live source; canonical-loader acceptance; exactly one witness. Keep existing warning behavior for individually identified old residue.

### 3. Strengthen the proof and finish truthful recovery instructions

- The current writer correctly syncs the actual parent after replacement. Its existing test nevertheless survives a mutation that syncs an unrelated directory. Adopt the supplied device/inode and ordering assertion plus its wrong-directory negative control into the governed test suite.
- Remove the advertised remedy that un-owning another section creates headroom for oversized edits in an already-unowned section. Unown adds the same measured span to both the floor and live unowned total; their difference does not increase. Recovery ends with deliberately restored measured bytes, a successful retry, and canonical-loader acceptance. Preserve the newer edit outside the repository; its later reapplication remains a separate operation subject to the ratchet.
- A failed extract write does not prove the final extract is absent: replacement may have occurred before a failed barrier, or an older extract may exist. Print restoration advice only for a verified usable copy; otherwise identify the retained snapshot and the actual failure.
- Pending recovery with an unreadable/non-UTF-8 source already preserves its snapshot. Improve the early refusal so it identifies that retained material and a usable recovery route. A concrete probe repeated the refusal twice, then saved the newer raw bytes externally, restored solely from the implementation's snapshot, retried successfully, and passed the canonical loader with one witness. This is a delivery gap, not demonstrated data loss or unrecoverability. See `probe_source_recovery.py`; receipt `arb-step-sourcerecovery-163044ab29684de191659a87665642d3`.
- Correct the manpage's blanket “Exit 1 means nothing was written”: recovering a different pending section can perform writes and then return 1. Align orphan warnings with the current plan. Reconcile the brief's coverage-persistence wording with its runtime-derived contract and qualify “floor changes only through unown” as the raise path; ordinary decreases remain specified.

### 4. Close against a fixed revision

Run the new diagnostic suite and the existing scoped tests after correction. Integrate the semantic tests with the existing REQ coverage and update the mutation evidence to the final file hashes. Execute the already-booked recovery demonstrations using implementation-retained bytes, then complete the required quality gates and independent Step 4b review through the existing pipeline.

The existing acceptance rule remains positive demonstrated behavior and no unresolved in-scope critical/high finding. Track other findings according to the existing policy. A novel finding must identify the violated current requirement and an executable reproduction within the accepted failure model; it does not silently expand the contract. Do not claim a guaranteed number of remaining review rounds.

## Ready-to-use direction for the active implementer

Continue OBPI-0.35.0-04 under its current plan and ledger exceptions. Use this document as the consolidated execution checklist and run `test_recovery_contract.py` before making the remaining cleanup change. Preserve the four now-passing journal-boundary cases. Repair error-reporting enumeration, strengthen the directory-identity test, and correct the bounded recovery diagnostics/docs described above. Integrate the tests, run the fixed acceptance matrix using existing evidence where it applies, and refresh final-revision proof before the required review. Do not dispatch another broad adversarial round as the first execution of these known cases, or ask the operator to re-rule settled behavior.

Before that review, resolve the newly identified platform mismatch as described in `PLATFORM-FINDING.md`. A warning is not evidence that a mandatory durability boundary was established. Windows being supported is not evidence that a POSIX-only no-op supplies an equivalent guarantee.

The live implementation, existing tests, brief, plan, locks and pipeline markers were not edited by this assessment. Only the governed course-correction insight was recorded in the live repository; diagnostic code and reports were written in this isolated assessment directory.
