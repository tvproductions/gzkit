# Population read: 15 GHIs and the F2 landscape record

Research subagent report, read-only, returned 2026-11-22 to the session that opened this run
(`e870dccc-bfdb-48be-baa8-a327a1e81cb8`), landed verbatim as delivered. A subagent's claim is
not evidence until re-derived (`.gzkit/rules/model-selection.md` claim 5); the claims this run
relies on are re-read in the record's `source` entries.

---

# Primary source: check-outcome-reporting population read (15 GHIs + F2 landscape record)

Read 2026-11-22, read-only. Each issue was fetched with `gh issue view <N> -R tvproductions/gzkit --json number,title,state,stateReason,closedAt,body,comments`, and every body and every comment was read in full. **Issues read: 15 of 15 listed.** Text inside quotation marks or block quotes is verbatim. Text outside quotes is the reader's classification.

---

## Part A: what `docs/rnd/ghi-landscape-reorganization.md` says about F2

I read the whole file (304 lines). F2 appears in two places: the family table row (line 215) and the cross-family line (lines 227–228). No other section names F2.

**Definition and members (line 215), verbatim:**

> | F2 a gate reports green over a state it cannot see | 6 — #808, #919, #969, #983, #998, #1032 | The control passes, but the question it answers is not the one its consumers read it for |

**Cross-family membership (lines 227–228), verbatim:**

> Cross-family members where the pass said so: #808 (F2, F6), #799 (F1, F8), #930 (F3, F4),
> #983 (F2, F8), #804 (F1, F9). Singletons: #594, #832, #837, #968, #1039.

**Epistemic status of the whole taxonomy (lines 206–210), verbatim:**

> **Epistemic status.** Family membership is a *reading*, not a measurement. The pass's own
> caveat is carried: it self-reported a hand-transcription error in the two youngest age
> buckets and said to trust computed counts over its listings. The same caution applies here.

**A passage that touches one F2 member (line 176–177), verbatim:**

> Eleven open bodies cite sibling issues as "(open)" that are now closed. #969's
> argument rests on #889 being open; #889 is closed.

`gh` confirms #889 is closed: closedAt 2026-09-14T08:30:39Z.

**Disposition ruled for F2: none.** None of the six disposition rows (lines 255–262) names F2 or any F2 member. The ruling closest to the family is row 6, verbatim: "Do not reorganise the queue." with reason "The run's answer: the residue is an accurate record of decisions only the operator can make. Reorganising it would relabel a correct state." The one taxonomy-wide judgment (lines 230–234) is verbatim: "There is no consolidation that collapses the queue, which is what a reorganisation would have had to deliver."

---

## Part B: per-issue records

Shape key:
- **(R)**: a check that ran, or was skipped or demoted, whose REPORT says pass.
- **(P)**: a check that PASSES without having read what it guards: a fail-open input, a vacuous empty population, or a proxy for the subject.

### #808 decommission-tautological-tests: criteria gate the ratchet, not the debt

1. **State:** CLOSED · stateReason COMPLETED · closedAt 2026-09-28T23:58:58Z
2. **Mechanism (verbatim):**
   > `decommission-tautological-tests` reports every criterion green while 274 tautological operations stand outstanding across 93 test files

   > **No criterion reads the outstanding operation count.** Criterion 1 is the closest and is still the wrong measurement: a ratchet is a *non-regression invariant*, and this chore's purpose is *reduction*.

   > the **drift ratchet holding** — fail-closes on growth *above baseline*. Green at 274 ops and green at 0 ops alike.

   **Class of failure (verbatim):**
   > **Ratchet-shaped acceptance criteria on a reduction-shaped chore.** When a chore's goal is to drive a population toward zero but its criteria assert only that the population has not grown, the chore is **complete-by-construction on the day it is authored** and stays complete for every value of the debt. Its green signal carries no information about whether any work has occurred.
3. **Resolution (verbatim, close comment):**
   > **Disposition:** fixed
   > **Resolved by:** 53d6b2ba0 — `fix(chores): gate tautological-test debt against a declining target (GHI #808)`

   A follow-up comment corrects the SHA, verbatim: "SHA correction to the close comment above: the fix landed on origin/main as **7b88dab0a**, not 53d6b2ba0." The operator ruling cited, verbatim: "Add declining target (Recommended)".
4. **Shape: P.** The deciding sentence: "No criterion reads the outstanding operation count." The check reads a proxy (non-growth) in place of its subject (reduction).

### #919 qc-binding: a control that could not run is reported as theater

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > **The accusation is false. The check is not theater — it never ran.** `uvx radon` could not resolve PyPI, so `check_module_size.py` never obtained a measurement to judge.

   > `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py:119-123` — the verdict is binary, and both failure modes collapse to the same `0`

   > Distinguishing a bail-out from a verdict and then returning `0` for both means the discrimination is computed and discarded.

   **Class of failure (verbatim):**
   > **A two-valued verdict over a three-valued world: `caught` / `did not catch` / `could not observe`.** Any environmental fault that changes a control child's exit code away from `expected_exit` — unreachable package index, missing interpreter, sandbox denial, disk-full, a tool removed from PATH — is reported as an enforcement claim adopted by nothing.
3. **What blocks it (verbatim):**
   > Open design question for the operator: whether an inconclusive control should **fail** the gate (safe, but a network blip blocks every push) or **warn and abstain** (push proceeds; an unobserved control is not evidence of enforcement). These have opposite failure modes and the choice is a ruling, not a detail.

   No comment records a ruling. The two comments are cross-links to #941 and #986.
4. **Shape: neither as defined.** It has R's mechanism with the opposite polarity: a check that did not run reports a verdict, but the verdict is FAIL ("FACADE"), not pass. The deciding sentence: "The accusation is false. The check is not theater — it never ran." A cross-link comment states the shared root, verbatim: "Common root: no channel separates "the thing under test is wrong" from "I could not test the thing", so the second is reported in the vocabulary of the first."

### #969 attestation evidence: a harness aggregate status can report success over a red verifier

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > The verifier exited **1**. The command exited **0**. Any consumer reading only the aggregate — most sharply a backgrounded harness call, whose notification is the sole reported signal — announces success over a red suite.

   **Class of failure (verbatim):**
   > Any consumer that reads a compound command's aggregate exit status as the verifier's verdict. The shell-side predicate (#940) can require the status be *surfaced*; nothing requires a *reader* to prefer the surfaced status over the aggregate, and nothing requires attestation evidence to come from the receipt channel the declaration names as the only sound one.

   The body names a consumer-side partner, verbatim: "#889 (open) reports that `_check_arb_receipts_present` counts receipts and never opens `exit_status`, so the one channel declared to carry the verifier's own result out of the shell is consumed by a presence check." #889 has since closed (2026-09-14), so this "(open)" is stale.
3. **What blocks it (verbatim):**
   > Estimated diff: unknown — this is a design question (which surface must refuse an aggregate-derived claim), not a located fix

   Two later comments record live instances, both on 2026-09-14. One, verbatim: "The notification reported the aggregate (the trailing `echo`) and was green over a red gate. It was caught only because the output file was read, not the summary line — which is exactly the reader-side obligation this issue says nothing currently requires."
4. **Shape: R.** The deciding sentence: "The verifier exited **1**. The command exited **0**."

### #983 section ownership: 10 of 12 corpus-owned sections carry no covering corpus content

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > The predicate exists and is correct. Nothing applies it to the declaration as it stands — `load_declaration` cross-checks the closed enum, the section roster, the ratchet floor and the witness chain, but never asks whether a section claimed as `corpus-owned` is actually covered.

   **Class of failure (verbatim):**
   > **A gate that governs a transition, but never the resting state it produces.** `gz content own` (GHI #974) applies `section_coverage` at the moment of transition. Every section declared `corpus-owned` by any other route — the day-one genesis declaration, a hand-authored map, a transition predating the gate — is admitted permanently without ever meeting the bar, and `load_declaration` re-admits it on every load. This is the presence-check family AGENTS.md § DO IT RIGHT names: the loader answers *"is a valid ownership value declared"*, never *"does the corpus actually carry this section"*.
3. **What blocks it (verbatim):**
   > whether the correct remedy is a loader arm, a `gz validate` scope, or a corpus-population campaign is an open design question — this issue does not prescribe it.

   Its exit condition also includes, verbatim: "the disposition of the 10 live sections (populate the corpus, or un-own them through the attested path) is operator-ruled and recorded." The issue has no comments.
4. **Shape: P.** The deciding sentence: "the loader answers *"is a valid ownership value declared"*, never *"does the corpus actually carry this section"*."

### #998 waiver-ratchet: honesty mechanisms gate debt volume, never coverage

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > Nothing in that refusal concerns what the waived entry was watching. The gate objected to the list getting longer. Had two stale entries been removed first, the same waiver would have landed with the gate green, and the sole witness over `.claude/agents` ↔ `.gzkit/agents` coherence would have gone quiet while the suite stayed green.

   > All three quantify the debt list over time. None asks what coverage a waived entry was providing, so none can distinguish silencing one of five redundant checks from silencing the last one standing.

   **Class of failure (verbatim):**
   > Any waiver, on any registered surface, whose volume mechanism currently has headroom — a shrink-ratchet with slack, a dated cutover before its date, a closed-set lock at authoring time — can silence the last remaining witness over a surface while `gz validate --waiver-ratchet` reports green. The volume mechanisms are orthogonal to coverage, so satisfying one says nothing about the other.
3. **What blocks it (verbatim):**
   > Which arm is right is a design question this GHI does not settle.

   The issue has no comments.
4. **Shape: both.**
   - P (the gate reads volume, a proxy, never coverage), verbatim: "None asks what coverage a waived entry was providing".
   - R (a waived check, in effect skipped, with the suite reporting green), verbatim: "the sole witness ... would have gone quiet while the suite stayed green."

### #1032 agent sync: exits 0 while printing 'Recovery required' for stale mirror paths

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > The non-destructive design is deliberate and is not the finding. The finding is the status: the message says recovery is REQUIRED, ~90 lines of "Updated …" precede it, the last line is "Sync complete.", and the exit is 0.

   **Class of failure (verbatim):**
   > A command that detects a condition it declares REQUIRED to fix, and reports success.
3. **What blocks it:** the issue states no blocker. Its scope hint is "Estimated diff: ≤100 lines". Its open question, verbatim: "whether a non-zero exit would break callers that tolerate stale paths today (the pre-commit sync hook, `gz git-sync`) is for the fixer to measure." The comments add family members and a sibling but no ruling.
4. **Shape: R.** The deciding sentence: "A command that detects a condition it declares REQUIRED to fix, and reports success."

### #843 gz mx: hangar demotes gz validate guards but never reaches pre-commit hooks

1. **State:** CLOSED · stateReason COMPLETED · closedAt 2026-08-22T11:30:11Z
2. **Mechanism (verbatim):**
   > The demotion is implemented against the **`gz validate` scope resolver** [...] Pre-commit hooks are a **separate enforcement surface** that never consults the MX marker.

   **Class of failure (verbatim):**
   > Every governance repair whose guard lives in a pre-commit hook rather than a `gz validate` scope. The ledger is the instance observed; the same gap applies to any pre-commit-guarded canonical surface. The failure is not that a specific guard is too strict — it is that the maintenance mode advertised for repairing governance has no authority over one of the two enforcement surfaces governance uses.

   The 2026-08-21 comment, kept unchanged by the 2026-08-21 correction comment, verbatim: "ordinary `gz validate` scopes genuinely do resolve `advisory` under the hangar and their findings are collected and discarded at `validate_cmd.py:917`. That is this issue's actual subject and it still holds. So the practical note for #844/#845/#846 stands as written — their `gz check` greens are honest about test/lint/typecheck/behave/docs and advisory about validate scopes."
3. **Resolution (verbatim, close comment):**
   > **Disposition:** fixed
   > **Resolved by:** `92667fe5` (the `gzkit.hooks.guards` seam) + `7af1a54b` (the rest of the surface, and two defects in the first commit's own tests)

   Also verbatim: "Third recurrence of one class — **#638** (`gz check` step layer, closed 2026-06-24) and **#651** (enforcement floor demoting in the hangar, closed 2026-07-01) were the first two."

   The close table includes two rows relevant to this class:
   - "A demoted finding is silently discarded | `…::test_demotion_is_announced_rather_than_silent`"
   - "An unresolvable checkpoint fails open | `…::test_unreadable_checkpoint_fails_closed`"
4. **Shape: neither in the body.** The body's defect is a guard that failed to demote, which made it too strict. **R appears in the comments.** The 2026-08-21 comment: "advisory about every `gz validate` scope while the hangar is open". The close table: "A demoted finding is silently discarded".

### #917 behave shards: non-recursive glob would drop nested feature files

1. **State:** CLOSED · stateReason COMPLETED · closedAt 2026-08-29T09:09:26Z
2. **Mechanism (verbatim):**
   > So any feature file below `features/` that is not directly in it is planned into no shard and passed to no behave process.

   > A file that lands in **zero** shards violates that, and the violation is silent: the gate reports `✓ Behave` over a scenario set it never ran.

   > The conservation test cannot detect this, because it enumerates the expected set using the **same non-recursive glob the planner uses**

   **Class of failure (verbatim):**
   > **A partition validated by an enumeration that shares the partitioner's blind spot.** Any future divergence between how the planner discovers work and how the runner would discover it is invisible to the test, because the test asks the planner's question.

   Also verbatim: "**Not currently firing:** `find features -name '*.feature' -mindepth 2` returns 0".
3. **Resolution (verbatim, close comment):**
   > **Disposition:** fixed
   > **Resolved by:** `fa098fc0` — `fix(check): shard what behave would run, and witness it independently (GHI #917)`
4. **Shape: both.**
   - R (scenarios skipped while the report says pass), verbatim: "the gate reports `✓ Behave` over a scenario set it never ran."
   - P (a test that compares the planner with itself), verbatim: "the assertion compares the planner against its own assumption and passes."

### #1154 gate tests: negatives feed only absence; stand-in inputs pass

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > What they lacked was the one input that distinguishes the claimed check from its stand-in: an artifact **present but false**, such as a receipt that exists and records a failure, or a walkthrough that exists and is unfilled.

   **Class of failure (verbatim):**
   > A gate's test set feeds the "violated" pole only as absence, and the "satisfied" pole as a minimal stand-in, so the test passes identically whether the gate checks the claimed state or only presence.

   Item 1 of the 2026-10-01 progress comment, verbatim: "`unittest-parallel -t . -s tests --buffer` exits 0 for a suite that collects zero tests and for one whose every test is skipped [...] `quality.run_tests` took `returncode == 0` as the claim "Tests pass", so a run that tested nothing was green."

   Item 2, verbatim: "`complete` counted a covering test as proof on exit 0 alone. A skipped or empty `unittest` run and a `behave --tags @REQ` that selects no scenario both exit 0."
3. **What blocks it:** all five contract items are reported landed: 572314835, 86465500b, 21ca3f404, 06c2883ce, a267eed2b and following, and 55e5b47af and a425a4c65. The 2026-10-02 comment leaves two rulings open, verbatim:
   > **Needs an operator ruling — the designated per-REQ discriminator.**

   > **Needs an operator ruling — canary scale.**

   The 2026-10-03 comment adds a design question, verbatim: "`guard_canary.binding_hash` hashes the guard source, the claim id and the designated test id, but **not the mutation** (`find`/`replace`)."
4. **Shape: both.**
   - P in the body (a test that cannot tell the claimed check from presence), verbatim: "the test passes identically whether the gate checks the claimed state or only presence."
   - R in the comments (vacuous runs reported as passing), verbatim: "so a run that tested nothing was green."

### #1263 mx: CI inherits the committed marker; demoted guards never run full

1. **State:** CLOSED · stateReason COMPLETED · closedAt 2026-10-31T09:10:24Z
2. **Mechanism (verbatim):**
   > `.gzkit/mx.json` is committed, so every CI checkout carries an open safe-mode marker, and `checkpoint.hangar_demotes` (`src/gzkit/mx/checkpoint.py`) demotes every guard outside `gate5_invariants` to advisory in CI as it does locally. The demoted guards run at full strength nowhere until `gz mx exit`. Both drydock exits met red guards no push had reported

   **Class of failure (verbatim):**
   > A local operating mode carried into a shared verifier by a committed marker, so the verifier inherits the relaxed severity meant only for the operator's session.
3. **Resolution (verbatim, close comment):**
   > **Disposition:** fixed
   > **Resolved by:** 2b79d26aa (`GZKIT_MX_FULL_STRENGTH`, the `full-strength-report` job), absorbed by #1273 (closed today).

   Contract amendment, verbatim: "the operator ruled "report only, decide within #1273", and that the marker stays committed. So the switch sits on a second CI job with `continue-on-error: true`, beside the unchanged blocking job, rather than on `check` as this issue first said."

   Verification, verbatim: "CI 41186366297 on ca318dab2: `check` green on both platforms; `full-strength-report` red on the tautological audit alone, reporting without failing the run."
4. **Shape: R.** The deciding sentence: "Both drydock exits met red guards no push had reported". The resolution keeps the blocking job green while a report-only job is red. That is a ruled, disclosed form of the same reporting split.

### #1271 gz mx exit: re-runs the change scope, not every guard at full strength

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > `gz mx exit` re-runs only the change scope of `gz check`, not `--full`.

   > So the exit gate never runs these: the full unit suite, Behave, the docs build, Preflight, and the guard-canary sweep

   **Class of failure (verbatim):**
   > An exit gate claims "every guard" but runs a narrower scope than the set the session demoted. So guards outside the change scope that were held advisory are never re-checked before the hangar closes.
3. **What blocks it:** no blocker is stated, and the issue has no comments. The operator has ruled it a defect, verbatim: "*"3. that too needs fixing"*". The open weighing, verbatim: "`--full` is far slower than the change scope, which the operator may weigh."
4. **Shape: R.** The deciding sentence: "An exit gate claims "every guard" but runs a narrower scope than the set the session demoted."

### #1272 safe mode: step demotion acts only on exit code 3

1. **State:** OPEN · stateReason none · closedAt null
2. **Mechanism (verbatim):**
   > The `gz check` step seam demotes a failing step under an open marker only when the step exits with code 3.

   > These steps fail with a code other than 3, so they still block while the hangar or safe mode is open

   **Class of failure (verbatim):**
   > Demotion is keyed to the exit code a step happens to return, not to a declared property of the guard. So which guards relax in safe mode is an accident of each step's implementation.
3. **What blocks it (verbatim):**
   > whether some rc-1 steps (lint, typecheck) are meant to stay on in safe mode is the operator's ruling to make.

   Comment of 2026-10-28, verbatim: "If this issue's fix demotes steps whatever their failing code, the rc-1 self-test failures (validator-reachability, ledger-inertness) would be demoted too. The two fixes need to be read together." The #1273 close records, verbatim: "#1272 and #1289 open, owned by RO-13's F5."
4. **Shape: neither.** The defect makes steps too strict, not falsely green. Its sibling #1289 (the comment) is R, and so is #1330 in the 2026-11-19 comment, verbatim: "a clone with no hook files passed `gz check --full` green and a commit landed unhooked."

### #1273 mx signal: each reader interprets the marker its own way

1. **State:** CLOSED · stateReason COMPLETED · closedAt 2026-10-31T09:10:22Z
2. **Mechanism (verbatim, findings 2–4):**
   > `checkpoint.hangar_demotes` (`src/gzkit/mx/checkpoint.py`) demotes in both `mx` and `safe` mode, and also when the marker is unreadable: *"An unreadable marker keeps the hangar's original presence-only reading."*

   > **Neither reading checks the ledger binding.**

   > **In safe mode no `gz check` runs at push.** The pre-push entry is `uv run python -m gzkit.mx.alarms gz-check-pre-push -- gz check --reuse-verified`, and `alarms.main` returns 0 when `alarms_off()`.

   **Class of failure (verbatim):**
   > The single truth-source marker (*"Every surface — code guards and agents — reads MX state from here and nowhere else"*) is interpreted by each reader in its own way. That covers modes, an unreadable file, the ledger binding, and which hooks are alarms. So "is the hangar open?" has several answers at once.
3. **Resolution (verbatim, close comment):**
   > **Disposition:** fixed
   > **Resolved by:** da18330d5, f0033aecd, 0af0ab891, 8bac12097, 2b79d26aa, 0fc222ae0, 9f862c390, e77d1fe81, 090800d4a; written review 5066b9c44 and 62c55dde0, `docs/governance/harbor-1273-mx-signal-review.md`.

   The operator ruled the reading of *on*, verbatim: "the condition is on only when the marker is present, readable, ledger-bound and not exiting" (Operator: *"A"*). Verification, verbatim: "`gz arb red --commit` not run: the commit witness is off in safe mode (contract, § List of discrepancies, RO-0)."
4. **Shape: R, with a P-like reader defect.**
   - R (a skipped check exits 0), verbatim: "`alarms.main` returns 0 when `alarms_off()`."
   - The demotion decision itself reads a fail-open proxy, verbatim: "An unreadable marker keeps the hangar's original presence-only reading."

   The second is a demotion decision, not a pass, so it fits P only loosely.

### #1339 ledger guard: a git failure or colored diff passes a staged ledger edit

1. **State:** CLOSED · stateReason COMPLETED · closedAt 2026-11-22T18:57:23Z
2. **Mechanism (verbatim):**
   > With `GIT_DIR=/nonexistent-git-dir`, `git diff --cached .gzkit/ledger.jsonl` prints its usage text and exits 129. The guard reads its empty stdout as nothing staged and passes.

   > `_run_git` (184-200) returns `""` on `FileNotFoundError, OSError` and never reads `result.returncode`.

   **Class of failure (verbatim):**
   > A guard reads an input it failed to obtain, or obtained in a form it cannot parse, as a clean input, and passes. Here the input is git's output, and it fails through a git error, a missing executable, or a user's diff configuration.
3. **Resolution (verbatim, close comment):**
   > **Disposition:** fixed
   > **Resolved by:** 4fda55e8b, 88a650164, 0b32c54f1

   Review comment, verbatim: "**Review verdict: CONFIRMED** (spec-reviewer subagent, which did not do the fix)." Booked onward, verbatim: "the wider class, a check passing without checking, across validators, runners and receipts, is booked under insight scope `check-reporting` and goes to the R&D session next."
4. **Shape: P (fail-open input).** The deciding sentence: "The guard reads its empty stdout as nothing staged and passes."

### #1340 authorship: guard reads git config, not the identity a commit stamps

1. **State:** CLOSED · stateReason COMPLETED · closedAt 2026-11-22T19:03:57Z
2. **Mechanism (verbatim):**
   > `_effective_email` (`src/gzkit/governance/trust_audits/authorship.py:83-97`) runs `git config --get user.email`. That is the configured address, not the one git stamps.

   **Class of failure (verbatim):**
   > A witness reads a proxy for its subject, the configured address, rather than the subject, the identity git stamps. Every route that sets the identity without changing config passes.
3. **Resolution (verbatim, close comment):**
   > **Disposition:** fixed
   > **Resolved by:** ea16c67a0, 4e8a9fba3

   Recorded limit, verbatim: "The out-of-hook question is settled as commit-time only: a commit made without the hook (cherry-pick, rebase, a hand-pushed ref) is not judged." Booked onward, verbatim: "the out-of-hook gap, and the pre-push `Authorship policy` step judging config rather than pushed commits, are booked under insight scope `check-reporting` for the R&D."
4. **Shape: P (proxy for the subject).** The deciding sentence: "A witness reads a proxy for its subject".

---

## Part C: table of all 15

| # | Title (short) | State · reason · closedAt | Shape | Resolution / blocker |
|---|---|---|---|---|
| 808 | decommission chore gates ratchet, not debt | CLOSED · COMPLETED · 2026-09-28 | P | fixed, 7b88dab0a (close comment said 53d6b2ba0, corrected) |
| 919 | unrun control reported as theater | OPEN | neither (R mechanism, FAIL polarity) | operator ruling: fail vs warn-and-abstain |
| 969 | aggregate status green over red verifier | OPEN | R | design question: which surface refuses an aggregate-derived claim |
| 983 | corpus-owned sections lack coverage | OPEN | P | design question (loader arm / validate scope / corpus population) plus an operator ruling on 10 sections |
| 998 | waiver ratchet gates volume, not coverage | OPEN | both | design question: per-entry field vs sole-witness detector |
| 1032 | agent sync exits 0 over "Recovery required" | OPEN | R | no blocker stated; ≤100 lines |
| 843 | hangar demotion misses pre-commit hooks | CLOSED · COMPLETED · 2026-08-22 | neither (body); R in comments | fixed, 92667fe5 + 7af1a54b |
| 917 | behave shards drop nested features | CLOSED · COMPLETED · 2026-08-29 | both | fixed, fa098fc0 |
| 1154 | gate tests feed only absence | OPEN | both (P body, R comments) | 5 items landed; rulings open on per-REQ discriminator and canary scale |
| 1263 | CI inherits the committed MX marker | CLOSED · COMPLETED · 2026-10-31 | R | fixed, 2b79d26aa, absorbed by #1273 (report-only job) |
| 1271 | mx exit re-runs change scope only | OPEN | R | none stated; operator ruled it a defect |
| 1272 | step demotion acts only on rc 3 | OPEN | neither | operator ruling on the stay-on set; read with #1289; owned by RO-13 F5 |
| 1273 | each reader interprets the MX marker its own way | CLOSED · COMPLETED · 2026-10-31 | R (P-like reader defect) | fixed, 9 commits + review doc |
| 1339 | ledger guard passes on a git failure | CLOSED · COMPLETED · 2026-11-22 | P | fixed, 4fda55e8b, 88a650164, 0b32c54f1 |
| 1340 | authorship reads config, not stamped identity | CLOSED · COMPLETED · 2026-11-22 | P | fixed, ea16c67a0, 4e8a9fba3 |

Tallies: R 5 (969, 1032, 1263, 1271, 1273). P 5 (808, 983, 1339, 1340, plus 1154 counted under both). Both 3 (998, 917, 1154). Neither 3 (919, 843, 1272), where 843 and 1272 carry R in their comments or siblings. Open 8, closed 7.

On what F2 holds: of the six F2 members, #919 is "neither" as defined. Its unrun check reports FAIL, not pass. The F2 definition ("The control passes, but the question it answers is not the one its consumers read it for") therefore fits #919 less well than the other five.

---

## Part D: further OPEN issues met in comments or `## Related` sections that look like the same class

For each one, only its state was checked (`gh issue view --json number,state,closedAt,title`). Its body was not read. Each line below is quoted from where it was met.

- **#1135** (OPEN), from the #1032 comment of 2026-09-27: "#1135 (`gz init` prints 'Registered git merge driver' when `git config` failed, and 'Repaired N' on a dry run)." Looks like R.
- **#1155** (OPEN), from the #1154 comment of 2026-10-01: "9 of the 12 gates listed here had no registered enforcement claim on the function that was hollow, measured at each fix commit's parent".
- **#1224** (OPEN), from the #1154 comment of 2026-10-14: "Five validators return their passing value when the file they audit is missing." Looks like P (fail-open input).
- **#1266** (OPEN), from the #1154 comment of 2026-10-23: "The canary coverage check counts a claim as covered by one canary, so the complexity-ceiling claim's cognitive leg (added under #1183) has no reviewed mutant". Looks like P (proxy).
- **#1289** (OPEN), from the #1272 comment of 2026-10-28: "a chore self-test that fails with exit 3 (module-size, tautological-debt) is demoted under an open marker, so a gate that has lost its teeth is reported as advisory." Looks like R (demoted).
- **#907** (OPEN), from #1340 § Related: "#907: same family. That issue owns the rule's file-content clause; this one owns the email clause's commit identity." Looks like P.
- **#1262** (OPEN), from #1271 § Related: "#1262 (debt aging reads hours, not what the guards refuse)". Possibly P (proxy). Weaker fit.

Met but CLOSED, so not listed above: #1124 ("`gz tidy` exits 0 over 456 findings"), #781, #730, #743, #853, #793, #852, #889, #941, #986, #942, #1159, #1161 and #1330. Met, open, but not this class: #1316 (removal propagation), #611 (corrective primitive) and #1275 (mode reaching the model).

The insight scope `check-reporting`, booked 2026-11-22 by #1339 and #1340, is the canonical record of this class per both close comments. I did not read it.
