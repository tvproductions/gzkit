# Stage 4a — OBPI-0.35.0-07-content-land-orchestrator

## Value

Before this OBPI, `gz content commit` promoted a corpus change to its committed renditions one consumer at a time. Each write was non-atomic, and no shared record showed that a multi-consumer change was in progress. Now `gz content land <surface>` does five things in order. It generates the candidate for every routed consumer, verifies lineage, runs the OBPI-14 retention gate, and then publishes the whole set under ONE corpus attestation and a shared `landing_id`. A journal is written before the first byte and cleared last. `--status` classifies consumers by hash, and resume is non-destructive and never re-prompts. This round adds a per-file compare-and-swap in `_publish`: a target that was edited outside the landing after its checks ran is never overwritten. Publication stops at that file with exit 2, the journal is retained, and no completion event is recorded.

## Key proof

The CLI contract is registered with its required positional surface:

```text
$ uv run gz content land --help
usage: gz content land [-h] [--attestor ATTESTOR]
                       [--attestation-text ATTESTATION_TEXT]
                       [--retention-map RETENTION_MAPS] [--dry-run]
                       [--status LANDING_ID] [--quiet | --verbose] [--debug]
                       surface
```

The two concurrent-edit tests for this round's repair (REQ-02 during staging, REQ-07 after resume checks) pass:

```text
$ uv run -m unittest tests.content.test_landing.TestPublishLanding.test_edit_during_staging_is_never_overwritten tests.content.test_landing.TestResumeLanding.test_edit_after_resume_checks_is_never_overwritten
Ran 2 tests
OK
```

The full set of covering unit tests passes:

```text
$ uv run -m unittest tests.content.test_landing tests.commands.test_content_land
Ran 78 tests
OK
```

## Executed acceptance proofs (current)

All proofs are at input digest `9bfa895c…` (the amended contract below; code unchanged) and all are valid. All 27 of 27 mutation controls were killed on assertion.

| REQ | Kind | Proof | Controls |
|-----|------|-------|----------|
| REQ-0.35.0-07-01 | BEHAVIOR | proof-a10f1b3e786a41c49d7fa92b6959818d | 1/1 killed on assertion |
| REQ-0.35.0-07-02 | BEHAVIOR | proof-c8c8f9d5689f400a9704595f67a2fc21 | 6/6 |
| REQ-0.35.0-07-03 | BEHAVIOR | proof-5159f13a01c3430c8de1cf2df3cd17ec | 3/3 |
| REQ-0.35.0-07-04 | BEHAVIOR | proof-1dff311a157c4be09e00b07a28d7ac6d | 2/2 |
| REQ-0.35.0-07-05 | BEHAVIOR | proof-be5817d41e564351b42184a102495e61 | 3/3 |
| REQ-0.35.0-07-06 | BEHAVIOR | proof-2d86cc7779684b44963a54ea4572adc1 | 1/1 |
| REQ-0.35.0-07-07 | BEHAVIOR | proof-2e527176787c4bc4be4c127a86c7c687 | 4/4 |
| REQ-0.35.0-07-08 | BEHAVIOR | proof-92c6cba21e614d33a81e8c1e575dab70 | 3/3 |
| REQ-0.35.0-07-09 | SUPPORT | proof-40cd97defef345ce8f95ceb44855f985 | SUPPORT resolver pass |
| REQ-0.35.0-07-10 | BEHAVIOR | proof-3d3c1a47e7464225aacc3a744e2a0831 | 4/4 |

Stage-2 reviews imported on these proofs, at the amended contract:

- Spec review `arb-step-specreview-1aabd745d6d74abbace6760b17110cd4`: all ten approved; closed every mapped finding, including the two round-3 race findings.
- Quality review `arb-step-qualityreview-e1acaee0c71c4093a16f5b66ca8d341c`: all ten approved, same closures.

Stage-2 status is ready (true) with no open findings.

This round's repair closes the Step-4b round 2 findings (Codex, tier 1):

- `adv-07-publication-overwrites-concurrent-edit` (REQ-02) and `adv-07-resume-overwrites-concurrent-edit` (REQ-07) are repaired by the per-file compare-and-swap in `_publish` (`src/gzkit/content/landing.py`). The rule for each file: if its current SHA-256 equals `new_sha256`, it is skipped; if it equals `old_sha256`, it is replaced; any other value raises `_foreign_edit`, exit 2.
- `adv-07-manpage-edit-witness-absent` (REQ-09) is resolved by the operator-ruled amendment of REQ-09's witness clause to GHI #647 arm 2. The operator chose, verbatim: "Amend witness to arm 2 (Recommended)".
- The exit table in `docs/user/manpages/content.md` now names the exit-2 foreign-edit stop.

## Receipts (Stage 3; cited, not replayed)

All have exit_status 0:

```text
arb-ruff-ccb1590fae3f442f94530db0fd163909
arb-step-typecheck-09a88cde2f52428bbac00c1bdc20eacf
arb-step-unittest-f268bffbeadb405ab1c1441cfe73650b
arb-step-mkdocs-c806200f55bd4176a68519a0405a8fda
arb-step-behave-4a0f8b5ebcad4ea6bb814f71dddcdb13
```

- The unittest receipt records Ran 11078 tests, OK (skipped=7).
- The behave receipt records 13 scenarios and 96 steps passed.

These also exited 0: `gz validate --documents`, `--req-kind-discipline`, `--rendition-freshness`, `--cli-alignment`, and `gz cli audit`.

## Limits disclosed

- `landing.py` is about 1,690 lines, against the advisory 600-line guidance in `pythonic.md` (quality review observation `aux-landing-module-size`). The `gz check` module band and xenon pass.
- Step 4b round 3 (`arb-step-codexadversary-0264a78a0ba041878f39853b02548bf0`) approved 8 of 10 proofs and refuted REQ-02/07 with a writer racing the instant between `_publish`'s hash read and the replacement. The operator ruled, verbatim, "Accept as residual (Recommended)": the brief's Threat Model now names that check-to-replace window as an accepted residual, because the stdlib offers no compare-and-swap rename. Edits made at any earlier point stay in scope and are never overwritten.
- The Stage-2 arb red receipts for REQ-02 and REQ-07 are `failure_class=error` on a reconstructed base, so they are inconclusive. The RED evidence is the assertion failures observed before the fix, plus the killed publish-overwrites-foreign-edit controls.
- REQ-09's SUPPORT proof passes on the artifact-exists arm (GHI #647 arm 2), which the REQ itself now states.
- Step 4b round 4 (`arb-step-codexadversary-5186184340874c11a717355b77bc4b51`, tier 1, imported) was the focused confirmation against the amended Threat Model that the operator authorized past the follow-up bound. It returned CORROBORATED: 10 of 10 proofs approved, both race findings closed. It replayed `publish-overwrites-foreign-edit` for REQ-02 and REQ-07; the other controls were inspected, not re-run. Its weakest point is the accepted window itself, and its checks confirmed the exception does not extend back into staging or resume's checks.
