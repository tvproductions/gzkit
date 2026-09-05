# Final verification

Parent: [OBPI-0.35.0-04](../../../obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md).
This supplements the historical archive; it is not human attestation or a replacement verdict.

The production and test files are committed at `f89520331ea3ccf26b6e85fc48b8d3fd55b813d5`
and pushed. Their bytes match the [43-case mutation sweep](summary-v4.json), which
was captured from its preceding commit plus the three-line R16 fixture correction.
Every baseline passed without skips; all 43 mutations caused assertions, with no
invalid results or survivors. All restorations and module provenance checks passed.
See [the full mutation record](mutation-evidence.md) and
[retained execution bundle](final-mutation-evidence.zip).

The roster is reconstructed G1–G18 plus R01–R18 plus mocked-native W01–W07.
The historical additional four targets remain unavailable; none were invented.
The seven Windows mutations prove local error handling and call semantics, not
actual Windows operation. That operation is being verified separately by CI.

[Verification evidence](verification-evidence.zip) and its
[SHA-256 inventory](verification-manifest.json) retain:

- 9,421 full-suite tests passing, with three native-Windows skips on macOS:
  `arb-step-unittest-dbb1bff960f84ea89182aa9a92f5ba15`.
- Ruff: `arb-ruff-2ab9fc6904f844ca9237215a2885f75e`.
- Typecheck: `arb-step-typecheck-20e2cce3acb5415c9492401ad9557f59`.
- Strict docs: `arb-step-mkdocs-9e138df2a7a94953ade025734f2c8f8e`.
- Five BDD scenarios, 29 steps, no skips:
  `arb-step-behave-556144265c2446a0a6a99090bb23cf23`.
- Seven standalone recovery diagnostics passing against verified live imports.
- Tool-generated presentation: all three brief demos exit 0; all eight REQs
  satisfy their own proof channels (seven BEHAVIOR, one SUPPORT).
- Actual failing mutations and passing tests for the two final proof gaps:
  required Windows flush strength and the reused snapshot's cleanup obligation.

Independent bounded specification and quality reviews passed. The specification
review first identified the flush-strength test gap; the assertion now rejects
NO_SYNC and its re-review passed. Production already requested the correct flags.

Windows and Linux CI run [33976418620](https://github.com/tvproductions/gzkit/actions/runs/33976418620)
completed successfully on both platforms. The Windows full check, including its
native directory-handle tests, completed at 2026-09-05T16:07:04Z. See
[the exact job result](ci-result.json). The accepted ledger limitations and scope
remain those of the brief.

## Acceptance verdicts (round 12) and the post-acceptance fix

Both acceptance reviews completed against the identities above and returned
`not-refuted` with no in-scope critical or high finding — this is now the standing
Step-4b verdict; the round-11 refutation is overturned (brief § Round 12):

- Codex, tier 1 plugin runtime: `arb-step-codexadversary-1e432720be4046cfaee3197e27a82a1a`,
  exit 0 — "approve. CORROBORATED-WITH-CAVEATS / not-refuted ... No material findings."
- Claude, supplementary and separately attributable:
  `arb-step-claudeacceptance-3eae42a1cd9845d2900a25e28b595617`, exit 0 —
  "CORROBORATED-WITH-CAVEATS. Enum: not-refuted." One medium, two low, one cosmetic.

The medium (Windows failure paths read a stale `GetLastError` because `WinError()` was
called without the `use_last_error` slot's value), one low (manpage exit-code row) and
the cosmetic (event-type count in a comment) were fixed in a focused pass on the operator's
instruction; the other low (malformed declaration shapes reaching the generic error path,
inside the accepted hand-edit boundary) is disclosed in the brief's Tracked Defects. The
regression test for the medium was observed RED before the fix and again with the fix
block deleted after it; see [the retained witness](round12-fix-mutation-witness.log).
That fix moved two identities: `ownership.py` is now
`d9561d7f0df0ef195767f379f424be2ab1f10ca9a793dda5b781940edff4c091` and
`test_ownership.py` is now
`0eae3cbd04fcb9f7a95719e28dce61db0e7580cbfa9cc7ba03ac4260680e2be1`; `unown.py` and
`test_content_unown.py` are unchanged. The 43-case sweep above is bound to the reviewed identities; the correction batch
below reran the roster against these. Post-fix canonical receipts: ruff
`arb-ruff-063f6b5146794670802be9b89d8dc834`, typecheck
`arb-step-typecheck-0412215b64a240489b25720250014fb2`, full suite 9,422 OK with three
native-Windows skips `arb-step-unittest-8d80976da6fc4f7287bb60cb4d8c6610`, strict docs
`arb-step-mkdocs-755f4be854654807ad430bae802981df`. Human attestation remains pending.

## Completion preflight

[Observed preflight](precomplete-before-review.json): ten checks pass and only
`adversarial_validation` fails because round 11 remains the standing refutation.
There is no outstanding operator ruling. The fresh reviews have since completed (above); the check still fails closed because refutation tokens remain in the section as history, which is the GHI #879 presence-check design. Tracked separately as GHI #964 on the operator's ruling; completion proceeded on the chokepoint's own gate (`gz obpi complete` exit 0, `attested_completed`, 2026-09-05T18:11:12Z).
The preflight's remedy suggesting completion with a refuted verdict is obsolete
and conflicts with the current completion guard and pipeline skill (GHI #960);
that suggestion is not a valid completion route and was not followed. This records
the observed diagnostic defect without making it a new ownership-protocol requirement.

The required Codex-plugin review is supplemented by an actual Claude review.
Codex reviewing a Codex-authored correction is not cross-vendor merely because
the current provider-blind gate recognizes its executable. The two review identities
and outcomes must remain separately attributable in the final evidence.

## Correction batch `d2280608` — evidence chain

- Commit `d2280608` on `main` (pre-push `gz check` passed): the saved-error fix, its
  three-arm mocked regression, a deterministic native failure-path test (Windows-only),
  the manpage exit-row split, and the comment fix.
- Mutation roster rerun against the final bytes: [summary-v5.json](summary-v5.json),
  [postfix-mutation-evidence.zip](postfix-mutation-evidence.zip) with
  [its SHA inventory](postfix-mutation-archive-members.json) — 44 of 44 KILLED at
  `source_commit d2280608`, 43 rebound cases unchanged in edit and selector plus W08.
- Windows + Linux CI run 33981617383 at `d2280608`: [job result](postfix-ci-result.json),
  [full Windows job log](postfix-ci-windows.log). Both success; Windows 17:47:02Z.
- Focused tier-1 confirmation: receipt
  `arb-step-codexadversary-fe5cf406644b4a688924c12b89071450` (copied here),
  [log](postfix-codex-confirmation.log), [prompt](postfix-acceptance-focus.txt) —
  approve, CORROBORATED-WITH-CAVEATS / not-refuted, no material findings.
- Round 12's own provenance above is unchanged. Operator attestation received 2026-09-05 ("Attest completed for OBPI-0.35.0-04"); completion recorded by `gz obpi complete` with the correction-review receipt.
