# First correction prepared and verified

The [platform finding](PLATFORM-FINDING.md) is now backed by a reviewable
[patch](unsupported-barrier-correction.patch). It restores the existing rule:
an unsupported required directory barrier preserves dependent recovery material
and exits 2 before deletion or reuse. Its diagnostic explains that an unchanged
retry cannot supply the missing operation.

The patch was prepared in `correction/` and has now been **integrated into the live
checkout**. It changes four files: the unown command, the shared helper's
documentation, the covering tests, and the manpage. It adds no exit code,
recovery state, or platform exception.

Verification:

- Before the correction, the new tests produced 24 preservation assertions that
  failed, with no setup/runtime errors.
- After correction, all 183 scoped ownership/unown/validation tests passed.
  Ruff, formatting, and scoped type checks passed.
- An independent rerun of the original EINVAL reproducer now observes fresh
  entry refusing before a snapshot is created, and pending cleanup refusing
  with the measured snapshot retained. Both return 2 and preserve the declaration
  and ledger.
- Independent specification and quality reviews both passed for this correction.
- `correction-manifest.json` records the exact patch/file hashes and read-only
  applicability checks from before integration. The existing implementation stage
  continues under the transferred Codex lock; the three actual dispatches were
  recorded. Live integration verification passed 183 scoped tests, receipt
  `arb-step-ownershipunown-0b99a378bc45413d84b5828b58720270`. No commit or OBPI
  completion was performed by Codex.

Evidence: [implementation and tests](correction-evidence.md),
[specification review](correction-spec-review.md),
[quality review](correction-quality-review.md), and
[independent reproduction](correction-validation/unsupported-barrier-observations.json).

This closes the specific unsupported-error regression in the proposed code.
It does not close OBPI-0.35.0-04. Windows durability and the other already-recorded
findings remain in the [consolidated execution path](EXECUTION.md). They must not
be represented as fixed by this patch.
