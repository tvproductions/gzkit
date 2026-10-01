# Audit A: OBPI-completion evidence gaps (#889, #942, #994, #1093)

Read-only diagnosis, 2026-09-30. Ledger `.gzkit/ledger.jsonl` (17909 lines; spacing is mixed, with early rows `"event": "x"` and later rows `"event":"x"`, so everything was parsed as JSON rather than grepped). "Completion" means `obpi_receipt_emitted` with `receipt_event: completed` (661 in total). Line numbers (Lnnnn) are 1-based ledger line numbers. Helper scripts and raw outputs are in this evidence directory (`a889.py`/`o889.json`, `c1093b.py`/`c1093b.txt`, `evhist.txt`).

The classifications are EXPLOITED (the gap let a completion through while the gate's intended condition failed, or a Demo mutated live state), EXPOSED-CLEAN (completed inside the window, and the evidence shows the intended condition held) and UNDETERMINABLE (the evidence needed is missing, with the missing evidence named).

---

## GHI #889: `obpi precomplete` arb_receipts never read exit_status

- **Gap:** `_check_arb_receipts_present` returned ok whenever any `arb-*.json` file existed. The fix (c9e296d8e) requires that, for each of lint, typecheck and unittest, the newest receipt at or after the OBPI lock claim records `exit_status` 0.
- **Introduced:** 31221c714, 2026-04-18T11:21Z (`git log -S _check_arb_receipts_present`). **Fixed:** c9e296d8e, 2026-09-14T08:28Z.
- **Population:** 284 completions in the window.
- **Method:** I applied the fixed predicate after the fact to every completion. The claim is the last `obpi_lock_claimed` for the OBPI before the completion. For each step I took the newest on-disk receipt between the claim and the completion. I also resolved every receipt ID cited in the completion evidence, and every `meta-receipt-bind` row (the separate `gz obpi complete` binding gate, live since b4f552151 on 2026-05-02, which checks that cited receipts record exit_status 0).
- **Evidence limits:** 1804 receipts are on disk and 1272 are tracked in git, against 3718 counted in the GHI on 2026-08-27. None survive from June or July and only 10 from August, so most completions in the window cannot be re-checked.
- **Caveats:**
  - precomplete writes no ledger event, so I cannot show that it actually ran for any particular completion.
  - The completion-time binding gate also has a lite-lane warn-and-proceed path (`obpi_complete.py`, the `_enforce_attestation_receipt_gate` matrix).

| Artifact | Completion ts | Classification | Evidence |
|---|---|---|---|
| OBPI-0.0.24-04-bdd-coverage (heavy, ADR-0.0.24) | 2026-05-02T18:56:39Z (L4524) | **EXPLOITED (undisclosed)** | Lock claimed 18:26:00Z. The only unittest receipt since the claim is `arb-step-unittest-e3b0f66d8d544457bae00c2386bc619e`: exit_status 1, 18:38:43Z, full suite, "FAILED (failures=4, errors=1)" (test_skill_manpage_coverage ×2, test_product_proof ×2, test_instruction_audit). The completion commit e5f011b08 adds exactly that one unittest receipt beside the green lint, typecheck, mkdocs and behave receipts. The attestation and meta-bind (L4523) cite no unittest receipt, and the red run is not disclosed. The fixed gate would refuse. |
| OBPI-0.0.22-05-gate5-walkthrough-arb-slot (heavy, ADR-0.0.22) | 2026-04-29T07:49:15Z (L4220) | **EXPLOITED (disclosed)** | Newest unittest since the claim is `arb-step-unittest-f0aba782c6654402ab7e2c6c1856a6ca`: exit 1, 07:44:13Z, full suite, "FAILED (failures=2)" on the gz-tech-debt-review index link. The attestation cites the scoped green `arb-step-unittest-3937164020cb426c8d2c79301f62f34c` (07:43:31Z, 15 tests) and says "Out-of-scope drift filed as GHI #359". #359 was created at 07:45:26Z for exactly that failure. The red receipt is tracked (c817a24a2). The fixed gate would refuse; the red run was routed rather than hidden. |
| 56 completions (2026-04-19 → 2026-09-12) | various | EXPOSED-CLEAN | The on-disk newest lint, typecheck and unittest receipts since the claim all record exit_status 0 (per-row detail in `o889.json`, where `cls` is EXPOSED-CLEAN). |
| 180 completions | various | UNDETERMINABLE, mitigated | The receipt files are gone. A `meta-receipt-bind` row shows that the cited lint, typecheck and unittest receipts resolved with exit_status 0 at completion, but "newest since claim" cannot be established. |
| 46 completions | various | UNDETERMINABLE | No surviving receipts for at least one step, and no meta-bind covering all three steps (pre-2026-05-02, lite-lane, or missing claim). This includes OBPI-0.0.23-03-sync-mirrors (L4277, lite, 2026-04-30): no unittest receipt on disk. It also cites a red `arb-step-validate-surfaces-7e27abd401f341b68b33e833f065e526` (exit 1), which was disclosed as carved out under GHI #368. |

Parent ADRs: ADR-0.0.24 and ADR-0.0.22 both recorded a Gate 2 pass at closeout (L4528 at 2026-05-02T20:47Z; L4229 at 2026-04-29T10:59Z). The red suite is therefore established at OBPI completion only, not at ADR closeout. I did not examine how faithful those Gate 2 rows are (three gates in the same second).

---

## GHI #942: Stage-4a packet's pasted command output unverified

- **Gap:** transcripts that an agent composed were believed on the agent's word. The fix (718b8f339) adds `gz obpi verify-packet`, which re-runs every `$` transcript.
- **Window:** from 2026-03-11 (b6c26750f, the first agent-composed Stage 4 presentation in the gz-obpi-pipeline skill; the "Step 4a" name dates from d1848af17, 2026-06-24) to 2026-09-06T10:49Z.
- **Population:** 606 completions.
- **Method:** before the fix, Step-4a packets were never persisted. The files under `.gzkit/evidence/` are tool-generated `present-evidence` JSON, and the only `.stage4a.md` files come after the fix. The closest persisted substitute is the agent-authored `key_proof` and `attestation_text` in each completion row; 145 of them contain `$` transcripts. On that text I checked:
  1. every `$ gz arb step --name X -- CMD` transcript that names a receipt, against the receipt's recorded `step.command` (8 checkable: 7 match, 1 mismatch, 2 receipts missing);
  2. test counts claimed next to a cited unittest receipt, against the receipt's `Ran N tests` (11 match; the mismatches were read by hand);
  3. invented `gz covers --json` keys (`obpi_id`, `coverage_pct`). There were none in `key_proof`.

| Artifact | Completion ts | Classification | Evidence |
|---|---|---|---|
| OBPI-0.0.28-03-threshold-validator (heavy, ADR-0.0.28) | 2026-05-06T00:46:08Z (L4887) | **EXPLOITED (packet-level; underlying claim held)** | The key_proof transcript `$ uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_complexity_thresholds_validator -v` shows "Ran 12 tests … receipt=arb-step-unittest-a7295197d4bd43249402cd2da1e47b09". That receipt's recorded command is `uv run -m unittest -q` (full suite, "Ran 4294 tests", exit 0, 00:34:39Z). No receipt on disk exists for the scoped command. The reporter at the time printed `receipt=<path>`, not a bare ID (`step_reporter.py:114` at cd5f4def4). The transcript is assembled, not captured; the tests were green regardless. |
| OBPI-0.35.0-04-section-ownership-and-ratchet | 2026-09-05T18:11:12Z (L15808) | EXPOSED-CLEAN | This is the GHI's own instance, caught before presentation ("the orchestrator re-ran the commands by hand before presenting", #942 body). The completion key_proof has none of the invented keys. |
| OBPI-0.0.17-01-schema-and-model | 2026-04-19T14:32:02Z (L3424) | UNDETERMINABLE | It claims "Full-suite regression green: Ran 3195 tests". The cited receipt `…40bab0bb…` is scoped (106 tests), and no receipt records 3195. The nearest full-suite receipts come after the completion (15:20Z red with 3172 tests, 15:46Z green with 3203). The claim is not witnessed; a run without a receipt cannot be excluded. |
| Remaining 603 completions | various | UNDETERMINABLE | The Step-4a packet the operator attested against was never persisted, and historical transcripts cannot be replayed against the historical tree. The count mismatches found under check 2 (L4447, L4751, L4206, L4653, L3613) are scoped-count prose placed next to full-suite receipts. They under-claim and do not fabricate. |

---

## GHI #994: a non-executing reviewer could record a confirmation it could not have made

- **Gap:** `gz obpi acceptance review` imported the review narrative without checking that its affirmative claims were grounded. The fix (3392c420d) adds `grounds` citations and refuses an approval that cites nothing when the reviewer cannot execute.
- **Window:** the importer shipped in 8436bfd8f (2026-09-08T10:32Z) and was fixed at 2026-09-14T11:52Z. Reviewers have had `tools: Read, Glob, Grep` since df9427434 (2026-03-20). No review receipt exists before 2026-09-08T11:21Z (the earliest of 80 `*review-*` receipts), so earlier Stage-2 reviews left no record.
- **Population:** 2 completions, and 28 review records in the window (22 from the non-executing spec and quality reviewers, 6 from the Codex adversary).
- **Method:** I scanned each review's `stdout_tail` for affirmative execution or ledger claims ("independently located", "ledger carries", "I ran", "Ran N tests", "exit 0", `artifact_edited`) and read every hit in context. I then compared the input_digest of each false claim with the digest the completion was attested at.

| Artifact | Completion ts | Classification | Evidence |
|---|---|---|---|
| OBPI-0.35.0-06-validate-rendition-lineage (heavy) | 2026-09-12T09:25:12Z (L16348) | EXPOSED-CLEAN (the gap was exercised twice and not relied on) | Two false confirmations were recorded. `arb-step-specreview-31f47107410b41ccaeecf5743b705a38` (L16254, digest 45cf01ca…) says "ledger carries 2 `artifact_edited` events citing `docs/user/manpages/validate.md`". `arb-step-specreview-3968ae54f65049a98cb8e48cc5b1461b` (L16266, digest 328501f4…) says "(independently located)". I re-checked the ledger: zero such rows. The Codex adversary refuted the claim (L16276), and later reviews retracted it (L16286, L16303, L16304). The completion was attested at digest 90807b7e… against spec 42ad26da (L16330), quality b9fd1be9 (L16332) and adversary 61d07ad4 (L16333). No affirmative false claim appears in those three. Both false rows remain durable in the acceptance ledger. |
| OBPI-0.35.0-05-corpus-candidate-generator (heavy) | 2026-09-11T00:07:23Z (L16171) | EXPOSED-CLEAN | The reviews behind the completion are spec 7eeca369 (L16160), quality 21166ae7 (L16159) and adversary 147e7e87 (L16161). Every execution gap is disclosed in `verification_gaps`. One citation defect: 7eeca369 cites "`.gzkit/ledger.jsonl:16050`" for the F11→REQ-01 and F13→REQ-04 mapping. L16050 is an `obpi_lock_ttl_warning`, and the mapping is actually at L16051 (off by one, and the substance holds). Review L16093 relies on a `/tmp/t2.log` that is outside the repo and gone now; this is disclosed. |

---

## GHI #1093: brief Demo ran in the live checkout

- **Gap:** `stage4_evidence._run_demo` ran with `cwd=project_root`. The fix (7a28ef98b) runs the Demo in a disposable copy.
- **Introduced:** d1848af17, 2026-06-24T11:44Z. **Fixed:** 2026-09-26T00:50Z.
- **Population:** 53 completions.
- **Method:**
  - I extracted each brief's `## Demo` using `extract_demo_commands`, from the brief as committed before the completion and from the current brief, and flagged the state-changing commands.
  - I read every committed version of every `.gzkit/evidence/*.evidence.json` packet: 81 demo runs, each with `ran`, `exit_status` and `stdout_tail`.
  - I matched the ledger rows emitted by flagged commands against packet `generated_at`.
- **Note:** `validate_stage4_evidence`, which is documented as re-running the Demo "at `gz obpi complete` time", has **no production caller** (`grep` over `src/`, and `git log -G` shows none ever existed). So in practice only `gz obpi present-evidence` executed Demos.

| Artifact | Completion ts | Classification | Evidence |
|---|---|---|---|
| OBPI-0.35.0-14-meaning-preserving-landing | 2026-09-25T09:44:45Z (L17495) | **EXPLOITED (the known instance)** | The Demo `gz content commit … --attestor g0 --attestation-text "demo"` overwrote `root.corpus.json` (restored from HEAD) and appended the false `rendition_committed` row L17415 (2026-09-25T01:28:45Z). This is disclosed in #1093 and in the OBPI Change Log. |
| OBPI-0.35.0-05-corpus-candidate-generator | 2026-09-11T00:07:23Z (L16171) | **EXPLOITED (non-attesting ledger row)** | The packet (generated_at 2026-09-08T11:30:39Z) records Demo `uv run gz content compose AGENTS.md --consumer root`, ran=true, exit 0, stdout "Candidate: …/.gzkit/renditions/AGENTS.md/root.candidate.md". Ledger L16055, `composition_candidate_emitted` at 11:30:36.25Z, is that run's row, 3 seconds earlier. It is tool-generated Layer-2 state and is not disclosed anywhere I found. There are 16 other candidate rows from 09-06 to 09-10 that I cannot attribute. |
| OBPI-0.0.65-03-gz-handoff-cli-verb | 2026-07-15T10:06:48Z (L13353) | **EXPLOITED (live write; no ledger row, no attestation)** | The packet (generated_at 2026-07-15T08:49:27Z) records Demo `gz handoff create --adr ADR-0.0.65 --slug demo-gz-handoff-create …`, exit 0, stdout `.gzkit/handoffs/20260715T084925Z-demo-gz-handoff-create.md`. That file never reached git, so it was removed or discarded. `handoff create` had no ledger write then: the first `handoff_resume_decided` row is 2026-08-05. |
| OBPI-0.35.0-09-codex-playback-wiring | 2026-08-21T08:23:56Z (L15246) | UNDETERMINABLE | The Demo includes `gz agent sync control-surfaces`, which writes `agent_sync_completed` and regenerates surfaces. No packet is persisted. L15242 and L15243 (07:04Z, 07:25Z) cannot be attributed to present-evidence rather than an ordinary sync. The rows are idempotent in kind. |
| OBPI-0.0.65-05-handoff-archive-retention | 2026-07-15T18:54:05Z (L13404) | UNDETERMINABLE | The Demo `gz handoff archive --older-than 30d` moves files. No packet is persisted. |
| OBPI-0.34.0-05-activate-standing-taxonomy-gate | 2026-07-31T08:32:02Z (L14462) | EXPOSED-CLEAN | The Demo `gz register-adrs` writes ledger rows only for unregistered artifacts. There are no `adr_created`, `obpi_created` or `artifact_renamed` rows from 07:30 to 08:33Z (the regenerated `adr-status.md` is a Layer-3 view). |
| OBPI-0.34.0-02 (L13612), OBPI-0.35.0-02 (L15505), OBPI-0.35.0-03 (L15855) | 07-20, 08-26, 09-05 | EXPOSED-CLEAN | Each writing Demo is a refusal probe: foundation `plan create 0.0.99`, `retire --attestor ""`, `--entry does-not-exist`, or a retire of an already-retired entry. There is no ADR-0.0.99 row, no `corpus_entry_retired` with reason "probe", and only one retirement of `corpus-prime-directive-ownership-2026-06-13…` (L13992, 2026-07-22, which predates the OBPI). |
| OBPI-0.44.0-01 (L12574) | 2026-07-10 | EXPOSED-CLEAN | No brief was found under `docs/design/adr`. Its packet shows the only Demo was `gz validate --surfaces`. |
| Remaining 43 completions | various | EXPOSED-CLEAN | By inspection, their Demo commands are read-only: `--help`, `--dry-run`, `validate`, `covers`, `list`, `python -c` read-only probes, `rg`, `cat`, and `unittest` or `behave` runs. |

### Sibling paths the #1093 fix does not close (untracked, operator to route)

1. **The ADR closeout ceremony walkthrough replays brief Demos live.** The agent runs them, following `gz-adr-closeout-ceremony` Step 4 and walkthrough discovery "extracted from OBPI briefs". This path is not isolated. Both instances below were committed:
   - ADR-0.0.65 closeout (2026-07-15T22:22Z, `.gzkit/ceremonies/ADR-0.0.65-…ceremony.json` walkthrough_index 5) created `.gzkit/handoffs/20260715T222217Z-demo-gz-handoff-create.md`, a hollow handoff that is still on disk. It also ran `gz handoff archive --older-than 30d` live, which archived 8 handoffs. Both were committed in c55c810e7.
   - ADR-0.0.72 closeout (2026-07-14T08:20–10:56Z) ran the Demo `gz insights remember … "InsightRecord required ts/type…(C4)"`. That wrote insight row 355 (2026-07-14T09:09:22Z) into the append-only insights register, committed in 97ea3d1d5.

   I found no GHI for this. The OBPIs and ADRs themselves were fine; these are durable Demo artifacts created during ADR completion.
2. **`gz obpi verify-packet`** (`stage4_packet._run`, `cwd=project_root`, currently at lines 252–255) still replays transcripts in the live checkout. It is tracked only as discovery insight line 837 (2026-09-26), not as a GHI.
3. **`validate_stage4_evidence`** says in its docstring that it runs at `gz obpi complete`, but nothing calls it. #1093's closure table claims a "`gz obpi complete` re-run" cause is covered. That path does not exist in production, so the coverage claim is only met by tests that call the function directly.

---

## What the release notes can truthfully say

While these four gates were open, most OBPI completions passed through them. The surviving evidence shows each gap was actually used only a handful of times, and in no case does the evidence show that shipped work was wrong.

- **#889:** two heavy-lane completions were attested while the newest full unittest run since their lock claim was red, and the fixed check would have refused both:
  - OBPI-0.0.24-04 (2026-05-02; receipt `arb-step-unittest-e3b0f66d…`, not disclosed);
  - OBPI-0.0.22-05 (2026-04-29; receipt `arb-step-unittest-f0aba782…`, disclosed and routed as GHI #359).

  The suite failures were outside those OBPIs' code, and both parent ADRs recorded a Gate 2 pass at closeout.
- **#942:** one persisted proof transcript (OBPI-0.0.28-03, 2026-05-06) pairs a scoped test command with a full-suite receipt it did not produce. The underlying run was green.
- **#994:** the only confirmations shown to be false (OBPI-0.35.0-06, two spec reviews) were refuted and superseded before the completion was attested.
- **#1093:**
  - Beyond the disclosed 2026-09-25 instance, one more Demo-generated ledger row exists: `composition_candidate_emitted` at 2026-09-08T11:30:36Z, from OBPI-0.35.0-05.
  - One live handoff file was written (OBPI-0.0.65-03).
  - Separately, ADR closeout walkthroughs replayed Demos live and committed a demo handoff and an insight row. That path is still open.

Most in-window completions (226 of 284 for #889, and 605 of 606 for #942) cannot be re-checked. Receipts from June to August were pruned, and pre-fix Step-4a packets were never persisted. The notes should say "no further instance found in surviving evidence", not "no other completion was affected".
