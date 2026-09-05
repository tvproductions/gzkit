# Standalone OBPI04 recovery acceptance diagnostics

Run from the selected immutable source snapshot. This file and
`test_recovery_contract.py` live outside the repository. The suite invokes the
real production CLI with existing `CliRunner`/seeding helpers, writes only to
isolated temporary filesystems, and validates the imported production and fixture
paths against `--expected-root`. It does not run governance commands or modify
source/tests in either snapshot or the live checkout.

Original snapshot command (observed exit 1):

```bash
cd /private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo
UV_CACHE_DIR=/tmp/gzkit-health-uv-cache PYTHONPATH=/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo/src:/private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo uv run --no-sync --project /Users/jeff/Documents/Code/gzkit python -B /private/tmp/gzkit-obpi04-assessment-4dt92ti0/test_recovery_contract.py --expected-root /private/tmp/gzkit-obpi04-assessment-4dt92ti0/repo --result-prefix /private/tmp/gzkit-obpi04-assessment-4dt92ti0/recovery-contract-original
```

Captured candidate command (observed exit 1):

```bash
cd /private/tmp/gzkit-obpi04-assessment-4dt92ti0/candidate
UV_CACHE_DIR=/tmp/gzkit-health-uv-cache PYTHONPATH=/private/tmp/gzkit-obpi04-assessment-4dt92ti0/candidate/src:/private/tmp/gzkit-obpi04-assessment-4dt92ti0/candidate uv run --no-sync --project /Users/jeff/Documents/Code/gzkit python -B /private/tmp/gzkit-obpi04-assessment-4dt92ti0/test_recovery_contract.py --expected-root /private/tmp/gzkit-obpi04-assessment-4dt92ti0/candidate --result-prefix /private/tmp/gzkit-obpi04-assessment-4dt92ti0/recovery-contract-candidate
```

Each run writes `<result-prefix>.json` and `<result-prefix>.log`, prints its
actual unittest result, and returns exit 1 for failures/errors. The JSON separates
`assertion_failures` from `setup_or_runtime_errors` and preserves retry outputs,
filesystem observations, barrier traces and import locations. Subtest failures
are counted individually; they are not extra test methods. A changed import/API
that causes an error is a setup/runtime error, not a demonstrated contract RED.

## The finite cases

| Test method suffix | Required evidence | Original snapshot |
|---|---|---|
| `writer_syncs_actual_parent_after_replace` | File fsync before replacement; successful fsync of the actual parent's device/inode after replacement; written bytes intact | PASS |
| `writer_identity_assertion_rejects_wrong_directory_negative_control` | Redirect only the parent's directory open to an unrelated directory; the same assertion must reject it | PASS: mutation rejected |
| `journal_present_cleanup_barrier_precedes_dependents` | Actual journal unlink, then successful fsync of its parent, then dependent unlink | Assertion RED: no barrier |
| `journal_absent_cleanup_barrier_precedes_dependents` | Successful fsync proving absence before dependent unlink even when entry begins absent | Assertion RED: no barrier |
| `journal_present_barrier_failure_retries_absence_then_heals` | After actual unlink, EIO at the barrier retains measured bytes and reports non-success; retry repeats barrier despite absent journal; healed retry cleans without another witness | Two assertion REDs: both retries omit barrier |
| `journal_absent_barrier_failure_repeats_then_heals` | Already-absent entry follows the same retention/refusal/retry rule; healed cleanup canonical-loads | Two assertion REDs: both retries omit barrier |
| `real_extraction_staging_enumeration_fault_repeats_then_heals` | Real writer produces extraction staging; enumeration EACCES must be disclosed on both retries; first invocation cannot claim current-transaction completion; healed retry removes residue and canonical-loads with one witness | Two assertion REDs: failure silently becomes an empty sweep |

Final runs with the directory-listing fault injected below real `Path.glob`:

| Frozen source | Methods passed / run | Assertion/subtest failures | Setup/runtime errors |
|---|---|---|---|
| Original `repo` | 2 / 7 | 8 across 5 methods | 0 |
| Captured `candidate` | 6 / 7 | 2 in the enumeration method | 0 |

The candidate passes both writer controls and all four journal-barrier methods.
Both snapshots reach the injected directory-listing failure on each enumeration
retry. The first retry nevertheless exits 0 claiming completion while the real
extraction staging file remains; the second retry returns the already-unowned
refusal without disclosing the listing fault. After the fault is removed, the
healed retry removes the residue and canonical-loader acceptance succeeds with
exactly one transition witness. Its exit 1 is the already-unowned precondition
result, not a remaining cleanup failure. Results are recorded separately in the
original and candidate JSON/log files; they make no claim about later live edits.

## Assumptions and proof limits

- The source of the assertions is the current plan's durable-journal-absence rule
  and complete extraction-file-family cleanup, summarized as A14/A15 in
  `contract-assessment.md`. Neither an inode's existence nor a successful unrelated
  directory fsync proves the required barrier.
- The initial settled state is produced by the actual CLI while cleanup alone is
  paused through the existing `_clear_recovery_state` test seam. The already-absent
  state removes the real journal entry without a durability barrier. These are
  explicit retry-state fixtures, not claims that a power interruption occurred.
- Extraction residue is produced by the existing `_crash_at_replace` helper:
  production chooses its staging filename, then replacement and staging cleanup
  receive injected errors. No arbitrary `.gzkit` payload or handcrafted staging
  filename supplies the failure.
- Enumeration errors are injected at directory-listing calls: `os.scandir`,
  `os.listdir`, and Python 3.13's already-bound
  `Path._globber.scandir = staticmethod(faulting_scandir)` reference.
  **`Path.glob` and `Path.iterdir` remain real.** Every faulted retry asserts a
  positive listing-fault count and records the faulted API. This matters because
  stdlib glob itself suppresses `OSError`: merely deleting the application's
  `except OSError` cannot expose a listing fault hidden inside glob. This
  diagnostic runner deliberately targets the verified Python 3.13 runtime;
  another interpreter may require adapting the bound-scandir injection seam.
- The enumeration retry may enter with no journal after a prior deletion. Its
  second retry may warn under the current plan's orphan policy; the suite requires
  disclosure and later cleanup, without imposing a new orphan exit-code policy.
  Likewise a healed run may return the existing already-unowned precondition
  refusal after doing the required orphan cleanup. Canonical-loader acceptance,
  unchanged source and absence of residue prove its end state.
- These tests establish OS-fault handling and ordering, not actual storage-device
  persistence after power loss. The accepted ledger fsync and shared-ledger
  limitations (#952/#953) remain unchanged. No full-suite or Gate claim follows
  from these seven diagnostics.
