# Isolated correction quality review

**PASS — no actionable scoped concerns found.** This is approval of the isolated unsupported-directory-barrier correction, not OBPI completion, full platform parity, or acceptance of the remaining protocol work.

Reviewed the four-file delta in `/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction` against `/private/tmp/gzkit-obpi04-assessment-4dt92ti0/correction-baseline.index`, its immediate caller/writer paths, the changed tests and manpage, and `PLATFORM-FINDING.md`. No source, governance, ledger, or pipeline state was edited by this reviewer.

## Findings

- `unown.py:1803–1809` removes the unsupported-error continuation. Every `OSError` now reaches an existing exit-2 refusal. The after-unlink path retains dependents before the sweep (`2133–2137`); the absent-on-entry path refuses before sweeping or starting a new transaction (`2087–2088`, caller `2495–2496`). This repairs the demonstrated policy violation without a new state, exit code, or journal schema.
- `_barrier_next_step` (`1812–1824`) limits errno classification to the remedy. Unsupported/invalid operation guidance names the attempted directory and avoids claiming that `EINVAL` proves a particular filesystem. Other errors retain repair-and-retry guidance. The two existing refusal paths still distinguish a witnessed transition whose journal was unlinked from an entry that started no transaction.
- The shared writer continues to propagate directory-sync failures (`ownership.py:927–928`, `970–978`). The patch does not suppress errors deeper in publication to make the warning path appear viable.
- The new helper faults actual directory descriptors at `os.fsync`, while regular-file syncs call the real function (`tests/commands/test_content_unown.py:5541` onward). The preparation-only cleanup suppression creates a witnessed pending transaction; it does not bypass the shared writer during the tested fault. The extract is generated through the ordinary changed-source recovery path.
- Fresh entry, after-unlink cleanup, and already-absent retry each exercise all four errno names and two consecutive refusals. Assertions compare retained snapshot/extract bytes, declaration bytes, and ledger records; healed retry checks cleanup, exactly one witness, source preservation and canonical loader acceptance. The healed exit 1 for an already-unowned section is correctly distinguished from fresh successful unown.
- The manpage change accurately describes preservation plus exit 2 and identifies the Windows guarantee as unproved. It does not claim that this correction resolves the existing Windows no-op.

## Verification

Ran the two focused test classes from the correction snapshot with its source first on `PYTHONPATH`:

```text
python -B -m unittest
  tests.commands.test_content_unown.TestUnavailableBarrierPreservesRecoveryMaterial
  tests.commands.test_content_unown.TestRetryProseMatchesWhatTheRetryDoes

Ran 5 tests in 0.042s
OK
```

Execution used `uv run --no-sync --project /Users/jeff/Documents/Code/gzkit`; tests used isolated temporary fixture files. No full suite or new adversarial research was run. These are simulated directory-sync errors against real descriptor and filesystem operations, not a physical power-loss or actual unsupported-filesystem demonstration.

Previously recorded enumeration-failure, Windows durability, and other recovery-documentation issues remain recorded. They were not introduced by this delta and are not re-raised as new blockers to this isolated correction.
