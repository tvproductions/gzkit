<a id="amendments-2026-10-02"></a>

### 2026-10-02 — DRAFT r2, NOT RATIFIED — why repair displaced feature work, and what to change

**Operator (`g0`), verbatim:**

> yes, I think we really need to rethink why the last 4 months has greatly expanded fixes with
> far fewer features being completed

then *"measure #3 first, then draft the amendment (maybe we invite codex in occassionally to
take a 'sanity pass' to ensure that gaps and blindspots are identified?)"*, then *"1, then 2"*
(revise this draft against the Codex review, then GHI #1161).

**This is a draft for ruling.** P1–P6 are separable. The figures are a **dated record measured
2026-10-02**, not thresholds. The measurement scripts and their re-run commands are in
this directory (`README.md`), so later readers re-run them instead of trusting the numbers
transcribed here. **Revision 2** follows the read-only Codex
sanity pass of r1; § Review record lists what that pass changed.

#### What was measured (2026-10-02)

**Repair grew.** `fix` commits per month, April to September:

| Apr | May | Jun | Jul | Aug | Sep |
|---|---|---|---|---|---|
| 170 | 148 | 149 | 178 | 289 | 302 |

`feat` commits stayed between 5 and 25 a month. GHIs opened against closed: Aug 183/176,
Sep 228/197. **Issues are closed nearly as fast as they open. Repair took over the hours;
the queue is not rotting.**

**Completions, split by stream:**

| Month | Foundation | Feature |
|---|---|---|
| Apr | 72 | 35 |
| May | 117 | 17 |
| Jun | 65 | 6 |
| Jul | 6 | 22 |
| Aug | 0 | 3 |
| Sep | 0 | 6 |

Three things follow:

- **The headline fall from about 100 a month to single digits is mostly the Foundation Sunset
  running out.** Before 2026-05-17 (ADR-0.0.36), lite-lane OBPIs could also close themselves
  without attestation.
- **Feature completions were never high.** They fell from July's 22 back to June's level.
- **All nine August–September completions belong to one ADR**, `ADR-0.35.0`, a heavy one.

**Feature work is single-threaded by ruling.** This plan carries the standing ruling *"only one
feature at a time, feature, finish, draw from…"*, and ADR order is absolute (amended 2026-09-29
for corrections to a `Validated` ADR only). When the one ADR in flight is hard, feature output
is that ADR's pace. Repair is the only other work a session may draw (next point), so it fills
the rest. **This is an effect of an operator ruling. It is recorded, not proposed for change.**

**Agents can start repair on their own; feature work needs the operator to start it.**

- Under the IRON LAW only the operator initiates OBPI work, while GHIs are authorized for
  direct repair at any time.
- A session with no initiated pipeline has one kind of work it may draw: repair.
- September's commits cite a GHI 332 times and an OBPI 32 times.
- This plan's 2026-09-02 entry ranked a box high *"because it is drawable without the
  operator"*, which is the same asymmetry put to deliberate use.

**Retries per completion rose.** Only signals instrumented the same way across July–September
are counted, so new instrumentation does not inflate them:

| Feature completions | Median re-claimed locks | Median relaunched pipelines |
|---|---|---|
| July | 0 | 0 |
| August–September | 1 | 3 |

**Wall-clock is not attributable.** Median lock-to-receipt hours were 3.8 (Jul), 24.3 (Aug)
and 51.1 (Sep), but they include idle time, implementation and operator waits.

**At least one competing cause is documented.** OBPI-0.35.0-04 spent about nine hours
hardening against attacks beyond an accepted boundary, while adversary compute was about 7% of
its window. That is review-scope non-convergence, which the 2026-09-03 ruling ("bound the claim
BEFORE the first round, or the gate cannot converge") addressed. **The data does not show that
the added gates caused the decline.** It shows that the completion path grew and retries rose.

**The completion path grew.** Snapshots below use the counting rule of
`src/gzkit/governance/trust_audits/gate_population.py`:

| | Apr 15 | Jun 15 | Aug 15 | HEAD |
|---|---|---|---|---|
| `gz obpi precomplete` checks | none | 8 | 9 | 11 |
| `gz obpi complete` refusals | 3 | 10 | 11 | 12 |
| `gz-obpi-pipeline` SKILL.md lines | 598 | 872 | 1056 | 1717 |
| mandatory dispatch roles | 4 | 5 | 6 | 6 |
| default `gz check` steps | 10 | 31 | 55 | 65 |

38 `gz check` steps were added after 2026-06-15. The pre-push hook runs `gz check` with
`--reuse-verified` and without Behave or Preflight, so a push does not always re-run the full
sweep.

**Old and current adversary enforcement.**

- **Two completions passed with a refuted adversary verdict:** OBPI-0.34.0-02 (07-20) and
  OBPI-0.35.0-09 (08-21). Both were later repudiated.
- **Both predate the move of review enforcement into the acceptance reducer** (GHI #985,
  `8436bfd8f`, 2026-09-08). Completion now refuses through `_current_adversarial_event` →
  `completion_review`, and precomplete through `acceptance_blockers`.
- **What is dead:** the old helpers (`_enforce_adversarial_validation`,
  `_check_adversarial_validation`) and the five `--adversary-*` flags they read. That is
  obsolete code. **It is not a missing gate.**

#### Proposed changes (each separable)

- **P1 — Completion-path additions come to the operator (advisory).**
  - **Rule:** while this entry stands, a fix that would add a check, pipeline step, dispatch
    role, hook or `gz check` step to the completion path states three things before it lands:
    the obligation it protects, the defect it answers, and its expected false-refusal cost.
    The operator rules.
  - **Exempt:** removing a false refusal, and deleting obsolete code.
  - **Why advisory:** **no mechanical witness is claimed.** The gate-population inventory admits
    new gates and does not count dispatch roles, pipeline steps or hooks, so it cannot enforce
    this. Building an enforcer would be the kind of mechanism this entry is trying to slow.
  - **Widens the 2026-06-08 freeze,** which covered scorecard promotion only, to additions that
    arrive through GHI fixes, which is how most post-June additions came.
- **P2 — Review the post-June completion path against the scorecard's own bar.**
  - **Scope:** each completion-path check and `gz check` step added after 2026-06-15.
  - **Assessed for:** the obligation it protects, its exposure, recorded false refusals,
    independent coverage of the same obligation, and its run cost.
  - **The bar is canon's:** removal needs *"named steering-failure evidence"*
    (`docs/governance/advisory-rules-audit.md`). Having caught nothing is **not** evidence of
    uselessness, since rare hazards and deterrence produce zero catches.
  - **What it produces:** recommendations only. Each removal is the operator's ruling.
  - **First item:** the obsolete Step-4b helpers and the `--adversary-*` flags, already
    awaiting routing.
- **P3 — Make feature work drawable.**
  - **Batch initiation:** the operator initiates the next N OBPIs of the in-flight ADR in one
    act. This is consistent with the IRON LAW and with one-feature-at-a-time, since the batch
    stays within one ADR.
  - **Draw order for sessions:** an initiated OBPI first. A GHI is drawn only when it blocks
    in-flight feature work, a gate or a release. Every other GHI is tracked and batched.
  - **Prime Directive #6 is unchanged** (ruled closed 2026-09-15). It already says *"In-scope →
    fix immediately. Out-of-scope → file GHI"*. This proposal changes which planned work a
    session draws, as 2026-09-15 and 2026-09-27 (3) did, not whether a defect is tracked.
- **P4 — Record where a defect came from, when it can be known.**
  - **Change:** `ghi-author` adds an `Introduced by:` line, with `unknown` and `multiple` as
    first-class answers.
  - **Kept separate from discovery:** a defect found by checking a mechanism is not thereby
    introduced by that mechanism.
  - **Reading:** monthly. It measures what r1 assumed, whether gzkit's own mechanisms and fixes
    are a leading source of defects, and fills this plan's admitted gap that the f1
    measurement *"cannot separate enumeration from creation"*.
  - **Cost:** a skill-text change and forensic effort per GHI, not a validator. The effort is
    bounded by allowing `unknown`.
- **P5 — Define §5's backlog gate as a bounded check.** §5 says *"Each gate is bounded; none is
  a standing obligation"*, and *"GHI backlog at steady-state triage scale"* is undefined.
  - **Proposed (a check at 1.0 closeout, not a monthly floor):**
    - every open GHI carries a disposition, either routed or open with a named blocker;
    - no open `defect` GHI is older than an operator-set age without a blocker comment.
  - **Withdrawn from r1:** the zero-net-GHI rule, which rewards finding less; the monthly
    completion floor, which is a standing obligation; and the equal-size scope rule, which
    conflicts with the carried ruling *"Nothing comes out of 1.0 … the calendar is"*.
  - **Still open:** what makes the ≈2027-08 date bind. As the 2026-09-20 entry says, *"It is the
    operator's to rule on."*
- **P6 — Periodic outside sanity pass (Codex).**
  - **What:** a read-only Codex review of this plan's latest amendment and its evidence, asked
    *what gaps, blind spots or self-confirming reasoning does this miss?*
  - **When:** at each campaign amendment, and monthly, with the operator's go-ahead.
  - **Record:** the findings, and what changed because of them, are kept in the amendment they
    reviewed, as § Review record below does. They advise and never gate.
  - **Not ADR-0.36.0:** that ADR's cross-family critic is an automatic second opinion at each
    structured choice, still unbuilt and staged dark. P6 is a manual, campaign-level practice
    that uses the installed Codex plugin and adds no hook or gate.

#### What does not change

- **Doctrine:** Prime Directive #6, the IRON LAW and one-feature-at-a-time.
- **Gates:** Gate 5 stays universal.
- **ADR order:** ascending order, as amended 2026-09-29.
- **Defects in hand:** a defect found in the work being done is still fixed immediately.
- **1.0 standard:** nothing comes out of 1.0.

#### Review record (P6 applied to this draft)

A read-only Codex pass reviewed r1 on 2026-10-02. What it changed:

| Finding | Change in r2 |
|---|---|
| r1 compared mixed populations | Measurement re-cut by foundation and feature streams; the "collapse" is now attributed mostly to the Foundation Sunset ending |
| r1's cost composite mixed instrumentation dates | Composite replaced by signals instrumented the same way across July–September; wall-clock marked not attributable; competing review-scope cause added |
| r1 read dead helpers as a missing gate | Dead code and current enforcement are now distinguished |
| P1 claimed a witness that cannot enforce it | P1 is advisory and claims no witness |
| P2 defaulted to retire on zero catches, against canon | P2 now uses the scorecard's evidence bar |
| P5 created standing obligations and conflicted with the carried 1.0 ruling | P5 is a bounded closeout check; the conflicting parts are withdrawn |
| P4 forced a unique origin | P4 allows `unknown` and `multiple` and separates discovery from introduction |
| Push wording was stale | Push wording corrected to `--reuse-verified` |

Codex agreed with three parts of r1: the initiation asymmetry, separating work selection from
defect tracking, and an advisory-only P6. One correction came from the ledger measurement, not
Codex: the agent had attributed the "paused at step 4b" handoff to OBPI-0.36.0-07; it is
OBPI-0.35.0-07.
