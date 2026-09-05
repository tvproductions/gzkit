# The platform correction repeats the underlying contract defect

Assessment of the stable later snapshot `platform-candidate`, captured 2026-09-05. This update supersedes the earlier report's unqualified conclusion that only the listed lifecycle corrections remained.

**Correction prepared:** see [CORRECTION.md](CORRECTION.md) for the isolated,
tested patch and two passing reviews. It restores preservation/exit 2 for
unsupported required operations and has now been integrated into the live
checkout. It does not resolve Windows durability.

## Observed result

With the real CLI and real filesystem writes, inject `OSError(errno.EINVAL)` into every directory `fsync`, while allowing regular-file syncs to execute:

| Entry state | Actual result in new code | Consequence |
|---|---|---|
| Fresh unown, no journal | Warning at absence check; later snapshot writer refuses, exit 2; declaration/ledger unchanged; snapshot remains | The warning does not restore availability on this filesystem. The same primitive is required by another stage. |
| Transition already witnessed, awaiting cleanup | Warning; journal and measured snapshot removed; exit 0 | Cleanup discards dependents without the mandatory durability boundary. The new branch directly relaxes the binding rule. |

These are observations of error handling and deletion, not a claim that a power cut or an actual NFS host was exercised. The possible journal resurrection after power loss is the reason the existing ruling requires the barrier; it is not an observed power-loss result from this probe.

Reproduction: `probe_unsupported_barrier.py`. Full output: `unsupported-barrier-observations.json`. Snapshot hashes and patch are in `platform-candidate.json` and `platform-candidate-input.patch`:

- `unown.py`: `ab23a8eb5aef055a29db65ae2e38cef8e1c7e6ba0d29cbfeeae7ee3d0df54e18`.
- `ownership.py`: `9fc2d1dface2d0b848d07cff6d5f3e9c577bd454ac9a45cec5243df55a1c5a98`.

Run from `platform-candidate`:

```bash
UV_CACHE_DIR=/tmp/gzkit-health-uv-cache PYTHONPATH=/private/tmp/gzkit-obpi04-assessment-4dt92ti0/platform-candidate/src:/private/tmp/gzkit-obpi04-assessment-4dt92ti0/platform-candidate uv run --no-sync --project /Users/jeff/Documents/Code/gzkit python -B /private/tmp/gzkit-obpi04-assessment-4dt92ti0/probe_unsupported_barrier.py
```

## The conflicting statements

The current plan at lines 234–236 requires:

> Establish durable journal absence before deleting or reusing dependent recovery files, including when the journal is already absent on entry. Failure to establish that boundary preserves the files and exits non-zero.

The new `_establish_durable_journal_absence` documentation states:

> The unavailable case is DISCLOSED and the run proceeds; every other errno is a real fault and still refuses.

These are different contracts. Calling the latter a disclosure does not implement the former. The difference between an unsupported operation and a transient failure changes the remedy; both remain failures to establish the required boundary.

The platform policy at `.gzkit/rules/cross-platform.md:16` also states:

> Windows, macOS, Linux — co-equal. Max cross-platform; no platform is favored over another.

The Windows implementation of `commit_directory_entry` returns without a durability operation. The brief's disclosure of POSIX-only tests at lines 588–589 records an evidence limitation, not an explicit acceptance of weaker Windows durability. The ledger exceptions #952/#953 do not cover this ownership-cleanup issue. The brief already includes “an NFS mount that fails a directory fsync” in its failure model at line 1083; this is not a newly invented adversary.

## Execution direction

1. **Preserve the existing mandatory boundary.** Do not let the new unsupported-error warning branch authorize dependent deletion or reuse. The safe existing disposition is preservation plus non-success. Do not broaden suppression into every atomic writer to make this local workaround appear coherent.
2. **Give an honest capability error.** When the environment cannot supply a required operation, report that this location cannot establish the guarantee. Repeating the same command under unchanged conditions is not a repair. Do not universally diagnose every `EINVAL` as a specific network-filesystem property from the errno alone.
3. **Resolve Windows against the actual contract.** A platform-equivalent mechanism must be identified and verified on Windows before claiming equivalent durability. This assessment has not demonstrated one. If the intended product guarantee is weaker on a supported platform, that is an explicit contract decision; neither the old no-op nor newly added prose authorizes it. A Windows-wide refusal would preserve this safety boundary but would not by itself satisfy co-equal functional support.
4. **Keep the work finite.** Record one platform/capability table covering proven barrier support, failed/unavailable required operation, and the Windows mechanism/evidence. Bind writers and cleanup to the same stated contract. Then run the lifecycle matrix already prepared, update final-revision evidence, and perform the required review. Do not add another recovery state for each errno or use another adversarial round to decide platform semantics.

The immediate production correction is unambiguous: preserve rather than discard recovery material when the mandatory boundary is not established. Full Windows support under this durability promise remains an architectural/evidence gap. It would be misleading to call it only a documentation change or claim the OBPI is now one guaranteed review away from completion.

## Response to the subsequent Task-5 escalation

Keep the distinction in the diagnostic, while preserving both halves of the existing rule: files retained and non-success. A nonzero exit after continuing through cleanup would still violate the preservation requirement. Use the existing exit 2; a new exit code or new recovery state is not needed to express an unsupported required operation. Gate results do not establish this property if their tests omit the unsupported-error branch.

Changing six coupled diagnostics instead of four is not, by itself, evidence of expansion beyond the defect. Require semantic tests for the two newly changed branches: inspect declaration/ledger/artifact state and verify the message accounts for that state. A different sentence about unchanged bytes does not substitute for checking the actual bytes and witness rows. Keep any required message-contract assertion separately.
