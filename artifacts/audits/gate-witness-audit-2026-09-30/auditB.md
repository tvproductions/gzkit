# Audit B: verdict and reasoning gates (GHI #959, #960, #985, #996)

Record date 2026-09-30. Read-only diagnosis against `.gzkit/ledger.jsonl` (17909 lines, `", "` JSON spacing; parsed with `json.loads`, not grep), git history, and `gh issue view`. Ledger line numbers are 1-based. No ledger, brief or issue was written.

## Cross-cutting correction: the "13 of 13 recorded no resolution" figure is false

GHI #959's body (repeated in #960) says: "refutation completions: 13; with adversary_resolution absent: 13". The ledger contradicts this. All 13 refutation `adversarial_validation` rows carry a non-empty `resolution` field. For each row, `git log -S<id> -- .gzkit/ledger.jsonl` returns exactly one commit (the one that added it), and that commit's version of the row already contains `"resolution"`. The key `adversary_resolution` (the CLI flag's name) appears 0 times in the ledger (`grep -c adversary_resolution` = 0). The measurement almost certainly looked up the wrong key. **Release notes must not repeat the "13 of 13 without resolution" claim.**

## GHI #959: refuted-with-caveats cleared the chokepoint with no resolution

- **Window:** opened by `e41a34c43` (committed 2026-07-09T10:32:09Z, GHI #676), where the chokepoint checked only `verdict == "refuted"`; closed by `ac57c15a8` (2026-09-04T11:57:19Z), which changed it to `verdict in REFUTATION_VERDICTS`.
- **Population:** 20 OBPI completions (`obpi_receipt_emitted`, `receipt_event: completed`) fall in the window. Each has exactly one `adversarial_validation` row, and 7 of those rows are `refuted-with-caveats`.
- **Method:** for each caveated row, check whether `resolution` is present and non-empty, and whether it was present when the row was first committed.
- **Result:** 7 EXPOSED-CLEAN, 0 EXPLOITED. The resolution that #959 required was recorded every time. Whether those caveats were really closed is a #960 question and is handled below.

| artifact | completion ts | classification | evidence |
|---|---|---|---|
| OBPI-0.33.0-02-airlock-in-pipeline-tracer | 2026-07-11T08:37:08Z | EXPOSED-CLEAN | ledger L12729 has a resolution; first commit 1b6e315cf |
| OBPI-0.33.0-06-airlock-doctrine-lawful | 2026-07-12T09:27:23Z | EXPOSED-CLEAN | L12917 has a resolution plus refuted_claim; 017d0ef9c |
| OBPI-0.0.72-03-insight-record-reconcile | 2026-07-13T12:29:32Z | EXPOSED-CLEAN | L13169; 5f3910e5b |
| OBPI-0.0.72-04-security-floor-overridden-event | 2026-07-14T00:42:56Z | EXPOSED-CLEAN | L13225; 0293aa132 |
| OBPI-0.0.65-04-orientation-single-location-scan | 2026-07-15T00:35:24Z | EXPOSED-CLEAN | L13290; 591a45367 |
| OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion | 2026-07-19T16:56:22Z | EXPOSED-CLEAN | L13548; 8e57a818f |
| OBPI-0.34.0-05-activate-standing-taxonomy-gate | 2026-07-31T08:32:02Z | EXPOSED-CLEAN | L14463; c3b644992 |

## GHI #960: a refutation plus a resolution string counted as a completing verdict

- **Window:** also opened by `e41a34c43` (2026-07-09T10:32:09Z): from the start, `refuted` passed as long as a resolution was attached. `refuted-with-caveats` passed with no resolution until #959, and with one after. Closed by `edbab5ae4` (2026-09-04T12:17:49Z), which refuses both refutation verdicts outright. The fix commit landed 20 minutes after #959's, and no completion falls between them.
- **Population:** the same 20 completions. 7 completed on `not-refuted`, so the intended condition held for them. 13 completed on `refuted` (6) or `refuted-with-caveats` (7). None of the 13 was later repudiated or withdrawn: I scanned every `obpi_completion_repudiated`, `obpi_withdrawn` and `ledger_event_corrected` row.
- **Method:** under the operator's #960 ruling, a clean completion needs the adversary to re-run and return a non-refuting verdict, or a re-run that comes back clean within a declared boundary. For each of the 13, I read the full `resolution` and `refuted_claim` in the ledger and the attestation text on the paired receipt.
  - **EXPLOITED:** the record itself says the refutation still stood at completion. Either the adversary was explicitly not re-run, or a finding against the OBPI's own deliverable or REQ proofs was knowingly left unfixed.
  - **UNDETERMINABLE:** the resolution says the findings were fixed, or bounded out of scope, but no non-refuting adversary re-run was recorded. That re-run is the missing evidence.
- **Qualifier:** every EXPLOITED row was attested by g0 with the standing refutation in view. These are not silent bypasses. The chokepoint let a refutation stand as terminal, which is exactly the gap, and the human gate accepted it on disclosed facts. Each routed residual was later fixed (GHI state checked on 2026-09-30).

| artifact | completion ts | classification | evidence |
|---|---|---|---|
| OBPI-0.35.0-02-content-withdraw-verb | 2026-08-26T02:01:49Z | EXPLOITED | L15504: "The adversary's own check was NOT re-run … this completion records the refutation as standing". Round-9 blocker (the two ledger readers disagree) routed to GHI #883, closed 2026-08-28. Attestation L15505: "including a STANDING REFUTED verdict … receipt arb-step-codexadversary-33c1b0ee…" |
| OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement | 2026-07-29T09:28:29Z | EXPLOITED | L14160, pass 3: "REQ-03/04 doc-content tests still bypassable …". The residual in the OBPI's own REQ proofs was homed on GHI #615 (closed 2026-08-04). The operator "ruled to attest holding the corrected caveat" (L14159) |
| OBPI-0.34.0-05-activate-standing-taxonomy-gate | 2026-07-31T08:32:02Z | EXPLOITED | L14463: "Unresolved and disclosed, not waived: Unicode line separators … and BOM-less UTF-16/32 still defeat detection at both ingresses". This is the gate the OBPI makes permanent. Tracked at GHI #736 (closed 2026-08-03) |
| OBPI-0.34.0-02-authoring-time-kind-rejection | 2026-07-20T10:54:32Z | UNDETERMINABLE | L13613: the round-3 refutation's new finding (register-adrs/init book a foundation ADR) was "NOT fixed here" and was routed by operator ruling to GHI #706, closed 2026-07-20T11:39Z. OBPI-0.34.0-05's attestation (L14462) says "#706 discharged". No clean re-run was recorded |
| OBPI-0.0.65-05-handoff-archive-retention | 2026-07-15T18:54:05Z | UNDETERMINABLE | L13405: two residual concurrency findings were "operator ruled … out-of-scope" and the boundary was documented. No re-run verdict was recorded |
| OBPI-0.0.72-04-security-floor-overridden-event | 2026-07-14T00:42:56Z | UNDETERMINABLE | L13225: the round-5 surviving caveat (Ledger.append non-atomic) was operator-ruled out of scope and tracked at GHI #687 (closed 2026-07-14). No re-run verdict |
| OBPI-0.33.0-06-airlock-doctrine-lawful | 2026-07-12T09:27:23Z | UNDETERMINABLE | L12917: in-scope fixes were made, a "residual caveat … deferred to ADR-0.33.0 closeout", and there was no re-run verdict |
| OBPI-0.0.65-02-programmatic-api-implementation | 2026-07-13T06:56:31Z | UNDETERMINABLE | L13085: "Re-dispatched Codex confirmed fixes 1-4-5 PASS", but the adversary's residual REQ-06 flag was rebutted by the implementer, not withdrawn by the adversary |
| OBPI-0.35.0-09-codex-playback-wiring | 2026-08-21T08:23:56Z | UNDETERMINABLE | L15247: pass-3 fixes with "all three probes re-run green". The recorded `adversary_receipt` is the refuting pass-3 receipt, and no pass-4 adversary verdict exists |
| OBPI-0.33.0-02-airlock-in-pipeline-tracer | 2026-07-11T08:37:08Z | UNDETERMINABLE | L12729: "Re-validated against the adversary's own attack", run by the implementer. No adversary re-run verdict |
| OBPI-0.0.72-03-insight-record-reconcile | 2026-07-13T12:29:32Z | UNDETERMINABLE | L13169: caveat 1 fixed; caveat 2 declared a "false positive" by the implementer |
| OBPI-0.0.65-04-orientation-single-location-scan | 2026-07-15T00:35:24Z | UNDETERMINABLE | L13290: three caveats fixed and re-witnessed with gz arb red. No adversary re-run verdict |
| OBPI-0.34.0-01-grandfather-manifest-and-closed-kind-assertion | 2026-07-19T16:56:22Z | UNDETERMINABLE | L13548: "The adversary's own checks were re-run after both fixes", with no adversary re-run verdict recorded |
| 7 not-refuted completions (0.44.0-01, 0.33.0-03, 0.33.0-04, 0.33.0-05, 0.0.65-03, 0.34.0-04, 0.35.0-01) | 2026-07-10 to 2026-08-24 | EXPOSED-CLEAN | ledger L12575, L12777, L12842, L12894, L13354, L14404, L15432: verdict `not-refuted` |

## GHI #985: acceptance could lose proof obligations or finding closure on re-edit or re-run

- **Window:** the fix sha in the brief (`8436bfd8f`, 2026-09-08T10:32Z) is not the final fix. #985 was reopened on 2026-09-09 on source-verified grounds (`_validate_new_review`, `_record_findings`, `assess_readiness`, `completion_review`) and closed again by `a83213b36` and `ed9c3485d` (2026-09-09T12:10:15Z). The gap has three arms with different openings:
  1. **Legacy review arm.** `pipeline_dispatch.handle_review_cycle` accepted later aggregate passing verdicts without keeping prior findings, `ReviewFinding` had no obligation or closure identity, and Step 4 relied on a verdict token (from #985's preserved original body). `handle_review_cycle` was introduced in `2ad08115e` (2026-03-21T07:10:31Z). Population: **458 completions**, from 2026-03-21T07:33:51Z to OBPI-0.35.0-03 at 2026-09-05T20:05:13Z.
  2. **Mutation-witness arm.** `_witness_one` accepted named unittest ERRORs as kills. It was added by `df0c23879` (2026-09-06T11:56Z). **0 completions** fall between then and 2026-09-09T12:10Z.
  3. **Acceptance-store arm.** Delayed findings were rejected, closures were erased by a repeated finding, and a fresh proof identity invalidated closure. The arm was introduced by `8436bfd8f` itself and closed by `a83213b36`. **0 completions** in its window. The first `acceptance_recorded` row is L16032 (2026-09-08T10:45:55Z), and OBPI-0.35.0-05 completed afterwards, on 2026-09-11 (L16170/16171), under the repaired machinery.
- **Method:** look for findings or proofs that vanished between runs. Before the fix, Layer 2 held no per-finding record: adversarial rounds left no ledger trace (the #960 operator comment measured 8 rounds and zero events for OBPI-0.35.0-04), and Stage-2 review outcomes lived in Layer-3 markers and transcripts. A per-completion determination is therefore possible only where a brief or receipt archive keeps the round history. I read `docs/governance/obpi-review-churn-2026-09-08.md` (the #984/#985 investigation) and the OBPI-0.35.0-04 brief.
- **Result:** 1 EXPOSED-CLEAN (OBPI-0.35.0-04) and 457 UNDETERMINABLE. OBPI-0.35.0-03 falls in the 457: its round history is in the resolution prose (L15854), but I did not read its brief rounds. 0 EXPLOITED found. The 7 June repudiations (L9758, L10112 to L10115, L10434, L10572) are fabrication or invalid-verification cases, not a lost obligation across a re-run, so I did not attribute them to #985.

| artifact | completion ts | classification | evidence |
|---|---|---|---|
| OBPI-0.35.0-04-section-ownership-and-ratchet | 2026-09-05T18:11:12Z | EXPOSED-CLEAN | The documented churn case: the round-3 durability obligation resurfaced at round 10 (churn doc § OBPI-04 item 1). The brief keeps it: round 10 finding 1 "OPEN — IN SCOPE" (brief L1038), then round 11 "Round 10's two high findings are discharged" (L1054). Final verdict `not-refuted` with receipt arb-step-codexadversary-fe5cf406… (L15807; the receipt file is present locally). The obligation was carried across rounds, not lost at completion |
| 457 other completions, 2026-03-21 to 2026-09-05 | — | UNDETERMINABLE | No durable per-finding or per-obligation record existed before the fix. Rebuilding one would require each brief's round prose and gitignored `artifacts/receipts/`, which were not read per OBPI |
| (none) | — | — | Arms 2 and 3 had no completion in their open windows |

## GHI #996: the justify binding was discharged by any file whose name matched

- **Window:** opened by `a6d52f661` (2026-05-03T19:29:35Z; the earliest commit `git log --follow` finds for `evaluation_justify_binding.py`, whose `_has_justify_artifact` checks only `startswith(slug) or id in name`). Closed by `eb91f20b6` (2026-09-14T10:02:13Z).
- **Consumers during the window:**
  - The `gz validate --evaluation-justify-binding` scope. It is registered as `_ScopeEntry("evaluation_justify_binding", "explicit", …)`, and `tier: "explicit"` means flag-gated, not part of a no-flag `gz check`. It does not appear in `_build_check_steps()` (`src/gzkit/commands/quality.py`) either before or after the fix.
  - `LifecycleStateMachine.transition`, which ran the gate only when `from_state in ("Pending", "Draft")`. Every recorded `lifecycle_transition` is `adr Proposed→Completed` (62) or `ADR Completed→Validated` (17), so the lifecycle gate never executed on any recorded transition.
- **Population:** 168 `adr-evaluation` events across 54 IDs, using the thresholds in `data/eval_feedback_thresholds.json` (unchanged across the fix). 8 triggered evaluations had a filename match in `artifacts/justify/`. No triggered OBPI evaluation exists. With the old predicate run against every file that ever existed there, I found no prefix collision onto a wrong subject.
- **Method:** I recovered each matching file from git: 4 were deleted in `58bbfa630`, so I restored them from `88fe4f6a3` into a temporary directory. I ran the post-fix reader `gzkit.justify.parser.parse_walkthrough` on each, checked the anchor subject and the section fill, and called the post-fix `validate_evaluation_justify_binding` read-only on the live IDs.
- **Result:** 8 EXPOSED-CLEAN, 0 EXPLOITED. None was empty or unfilled: all have 8 of 8 sections filled, a subject-naming anchor, and were authored on 2026-06-19, after the evaluations they answer. Each path has exactly one add in git history.

| artifact | completion ts | classification | evidence |
|---|---|---|---|
| ADR-0.0.73-verification-layer-binding-audit | eval L10574 (2026-06-19T10:19Z); walkthrough 88fe4f6a3 | EXPOSED-CLEAN | 8,375 B file; parses, 8/8 filled, draft_slug names the subject; the post-fix validator returns [] |
| ADR-0.47.0 (now ADR-pool.owasp-top10-2025-scan) | eval L5422 | EXPOSED-CLEAN | 8,897 B; parses and filled; post-fix [] |
| ADR-0.49.0 (now pool) | eval L6622 | EXPOSED-CLEAN | 9,680 B; parses and filled; post-fix [] |
| ADR-0.50.0 (now pool) | eval L6645 | EXPOSED-CLEAN | 9,653 B; parses and filled; post-fix [] |
| ADR-0.0.26 | eval L4709; file live 88fe4f6a3 to 58bbfa630 | EXPOSED-CLEAN | 10,938 B; parses and filled; superseded by the non-triggered re-eval L10755 |
| ADR-0.0.51 | eval L6641 | EXPOSED-CLEAN | 10,379 B; parses and filled; re-eval L10757 clean |
| ADR-0.0.56 | eval L7035 | EXPOSED-CLEAN | 13,094 B; parses and filled; re-eval L10759 clean |
| ADR-0.0.64 | eval L7907 | EXPOSED-CLEAN | 12,300 B; parses and filled; re-eval L10761 clean |

**Limit:** `artifacts/` is gitignored (`.gitignore:66`). A placeholder that was never force-added would leave no git trace. An explicit validate run over such a file cannot be enumerated from git or the ledger, so that residue is UNDETERMINABLE by construction and cannot be counted.

**Adjacent finding, not #996, needs routing:** two ADRs completed while their latest evaluation was triggered and no walkthrough existed. Filename discharge played no part: nothing matched. The gate simply had no consumer on the completion path.
- **ADR-0.0.73:** triggered eval L10574; `lifecycle_transition` Proposed→Completed at L10626 (2026-06-19T12:37:49Z). The walkthrough was committed at 14:26Z, and the #628 sweep message says the scope was exiting 3 for it.
- **ADR-0.33.0-airlock-membrane:** triggered eval L12477; completed at L12939 (2026-07-12T16:38:08Z). It has no walkthrough today, and the post-fix validator still reports it.

The current `lifecycle.py:117` still gates only `Pending` and `Draft`. `closeout.py:566` builds `LifecycleStateMachine(ledger)` without `project_root`, so closeout never injects the gate. The 2026-09-28 `work_start_transitions` routing (Draft→Proposed) makes the gate reachable at work start, but not at completion. Two `gh issue list --search` queries found only #1014 (closeout from_state, closed); that is not proof that no tracking issue exists.

## What the release notes can truthfully say

- **#959:** 7 completions during the window used `refuted-with-caveats`, and all 7 recorded a resolution, so this hole was never used.
- **#960:** 13 of the 20 heavy-lane completions between 2026-07-09 and 2026-09-04 completed on a refutation verdict with a resolution string, which the fixed gate now refuses. In 3 of them (OBPI-0.35.0-02, OBPI-0.34.0-03, OBPI-0.34.0-05), the ledger's own resolution text shows the refutation still stood at completion. All three were attested by the operator with that fact disclosed, and their routed defects (#883, #615, #736) have since been fixed. For the other 10, the resolution says the findings were fixed or bounded, but no clean adversary re-run was recorded, so whether the refutation was discharged cannot be shown.
- **#985:** the arms introduced in September (mutation witness, acceptance store) had no completion while they were open. Before the fix, Layer 2 held no per-finding record, so for the 458 earlier completions it cannot be shown either way whether a finding was dropped. The one documented churn case (OBPI-0.35.0-04) carried its obligation to a clean final verdict.
- **#996:** no completion was discharged by an empty or unfilled walkthrough. All 8 filename matches were complete, subject-bound walkthroughs that also pass the fixed check. The gate was not on any completion path during the window.
- **Do not state** that 13 refutations recorded no resolution. The ledger shows all 13 did.
