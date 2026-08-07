# ADR-0.35.0 — Substance Evaluation (judge-graded)

**ADR:** `ADR-0.35.0-canon-entry-corpus-landing`
**Evaluator:** agent judge, `gz-adr-evaluate` framework v1.0 Parts 1 and 3
**Date:** 2026-08-07
**ADR state at evaluation:** `Draft`, `feature`, `heavy`, 0/10 OBPIs landed

## Why this is a separate file from `EVALUATION_SCORECARD.md`

`gz adr evaluate` rewrites `EVALUATION_SCORECARD.md` wholesale on every run, so a
judged substance scorecard written there is destroyed by the next invocation —
even though `gz-adr-evaluate` SKILL.md § Step 7 instructs the judge to write it
exactly there. Filed as **GHI #769**; this file is that issue's candidate shape 2
(CLI owns the structural file, the judge owns the substance file) applied ahead of
the fix. It also honors GHI #624's rule, printed in the structural scorecard
itself: *"Do NOT composite these scores with a human substance review — they
measure different things."* **Nothing below is averaged with the structural score.**

## ⚠ Dispatch attestation: NOT PERFORMED — this is a single-driver evaluation

`gz-adr-evaluate` SKILL.md § Persona Dispatch mandates dispatching `spec-reviewer`,
`quality-reviewer`, and `narrator` to produce independent dimension scores, on the
stated ground that *"a single driver scoring its own scoring is the precise
optimistic-bias defect `spec-reviewer`'s anti-traits name."*

**No dispatch occurred.** A standing session instruction forbade spawning
subagents. Every score below was produced by one driver, so the optimistic-bias
mitigation the skill prescribes is absent and the scores should be read as one
reviewer's judgment, not a synthesized panel.

This disclosure is voluntary — no mechanism required it. `run_dispatch_attestation_audit`
in `gz check` checks only that `ADR-pool.obpi-pipeline-dispatch-attestation` still
carries the string `absorbed_into: ADR-0.0.73`; it records nothing about whether a
dispatch happened. Filed as **GHI #770**, whose minimum honest fix is precisely
this marker made mandatory rather than optional.

## Structural pre-screen (traceability only — NOT composited)

`uv run gz adr evaluate ADR-0.35.0-canon-entry-corpus-landing`
→ STRUCTURALLY COMPLETE, 3.55/4.0, 10 OBPIs scored, substance UNGRADED.

## Part 1 — Substance dimensions

<!-- gz-validate-skip: command-shape -->
| # | Dimension | Weight | CLI | Judge | Weighted | Reconciliation |
|---|-----------|--------|-----|-------|----------|----------------|
| 1 | Problem Clarity | 15% | 4 | **4** | 0.60 | Agree. Quantified throughout: 9,966 B of 31,990 B (31.2%), 7 duplicate groups, the 63x `ByteEvidence` inflation, `codex.md` at 13,606 B with no playback. Every claim carries a file:line. |
| 2 | Decision Justification | 15% | 4 | **4** | 0.60 | Agree. 9 decisions, 15 rejected alternatives (B–O), several citing in-repo precedent (`dc2bc605`, `d03ce98f`) and the cost of re-deciding (the 2026-07-19 session). Alternative B's analysis argues *against* the chosen path on attestation cost and says so. |
| 3 | Feature Checklist Completeness | 15% | **1** | **3** | 0.45 | **Override.** CLI heuristic misfired on *"items not prefixed with `OBPI-`"* — the items are prose mapping 1:1 to briefs 01–10, each quoted verbatim in its brief's § ADR Item. Its second finding, *"inconsistent granularity"*, has partial substance (item 5 bundles three deliverables, item 7 five), but § Decomposition Scorecard adjudicates it explicitly rather than by accident. Not 4: item 7's split contingency (10 → 11) is an acknowledged, unresolved sizing risk. |
| 4 | OBPI Decomposition Quality | 15% | 4 | **3** | 0.45 | **Override downward.** The CLI's own OBPI table scores Size = 2 on briefs 02, 05, and 07 — its dimension-4 score of 4 does not reconcile with its own per-OBPI data. Item 7 carries atomic multi-consumer write + resume + rollback + `--status`, and the ADR states it may split again. Dependency graph is acyclic, declared per brief, no numbering gaps. |
| 5 | Lane Assignment Correctness | 10% | 4 | **4** | 0.40 | Agree. All 10 Heavy; each touches a CLI, schema, or runtime contract. Gate 3/4/5 obligations acknowledged per brief. |
| 6 | Scope Discipline | 10% | 4 | **4** | 0.40 | Agree, and this is the ADR's strongest dimension. § 7 Scope Minimization gives cut lines *with pairing rules* ("04 and 06 together, never separately"), do-not-cut items with reasons, and 6 forced-onward follow-ons in § Closing. |
| 7 | Evidence Requirements | 10% | 4 | **3** | 0.30 | **Override downward.** Every OBPI carries verification verbs and REQ-level acceptance criteria, so the floor is met. But three of six Fidelity Assertion rows are the same command (`gz validate --rendition-lineage`) proving three different claims, and `gz content land --dry-run → 0` passes against a stub. Verification breadth is thinner than the row count implies. |
| 8 | Architectural Alignment | 10% | 4 | **4** | 0.40 | Agree. Exemplar files cited with line numbers throughout; analogues named (`gz obpi withdraw`/`repudiate`, ADR-0.0.71); anti-patterns named as rejected alternatives E, F, I. Append-only is honored rather than worked around. |

**Substance weighted total: 3.60 / 4.0 → GO** (threshold ≥ 3.0).
No dimension scores 1. Two dimensions were overridden downward against the CLI;
one upward.

## Part 2 — OBPI scores

The CLI's per-OBPI table is accepted as-is (all 10 average ≥ 3.6, none scores 1),
with one qualification: its Size = 2 marks on OBPIs **02**, **05**, and **07** are
judged accurate and are the evidence behind the dimension-4 override above. OBPI-07
is the sizing risk the parent ADR itself flags as possibly splitting 10 → 11.

## Part 3 — Red-team protocol (10 challenges, all engaged)

| # | Challenge | Result | Finding |
|---|-----------|--------|---------|
| 1 | So What? | **PASS** | § 7 Scope Minimization names the concrete capability lost per item; "do not cut 05 or 07 — without them 01–03 are schema with no consumer" is the model answer. |
| 2 | Scope | **PASS** | Both directions answered. Excluded-but-arguable: the CLAUDE.md seam and `.gzkit/rules/*.md`, both named with reasons and forced onward. |
| 3 | Alternative | **PASS** | Decomposition defended via explicit split adders; merge/split acknowledged rather than resisted (07 may split). |
| 4 | Dependency | **PASS** (qualified) | A single point of failure exists — 01 heads the chain, 05 needs 01+04, 07 needs 05 — so the graph is a diamond, not resilient. It passes because the ADR states this explicitly and orders around it, not because the graph is robust. |
| 5 | Gold Standard | **FAIL** | The ADR never compares itself structurally to a validated local exemplar (e.g. ADR-0.34.0, ADR-0.0.74). No such section exists. Cosmetic: costs a calibration check, not the design. |
| 6 | Timeline | **PASS** | Critical path derivable and stated per brief; parallel stages explicit (04 runs alongside 01–03). |
| 7 | Evidence | **PASS** | Every OBPI has at least one concrete verification command. See dimension 7 for the breadth qualification. |
| 8 | Consumer | **PASS** | § Consequences (Negative) answers the operator's real questions, including the ones that damage the ADR. |
| 9 | Regression | **FAIL** | **The material failure.** Pre-mortem #1 *is* the six-month silent-break scenario, and the ADR ships without a mitigation: *"Cadence, owner, and scheduled floor-raise are UNDECIDED and forced onward."* The failure *"requires nobody to do anything wrong"* — 18 months out the unowned total reads 22,100 B while "31.2% witnessed" has printed forty times. No monitoring or contract ensures the ADR's central value claim stays true. |
| 10 | Parity | **PASS** | The weakest claim is assumption a2 (the 8 corpus-addressed sections are the high-value ones); the ADR marks it **← SHAKIEST** itself and gives the accretion-curve reasoning. |

**2 failures → GO** (threshold: ≤ 2 GO, 3–4 CONDITIONAL GO, ≥ 5 NO GO).

## Defect found outside the rubric — fixed during evaluation

The § Boundary Invariants set carried **two `BI-04` entries** (8 invariants under 7
numbers), with `REQ-0.35.0-10-07` and `REQ-0.35.0-06-08` both citing "BI-04". A
Boundary Invariant is the *sole* proof channel for a STRUCTURAL-FENCE REQ and both
of these are cross-OBPI, auditable only at ADR closeout — so the collision would
have surfaced at the worst possible moment. Blast radius was zero (only `BI-01` is
cited by any brief), so the set was renumbered to BI-01…BI-08 and synced.

`gz validate --req-kind-discipline` passes over the duplicate: it checks that a REQ
*names* a Boundary Invariant, not that the name resolves uniquely.

## Verdict

**GO — with two conditions, and a recommendation to shrink the first commitment.**

The ADR is unusually well made. Its distinguishing quality is that it argues
against itself in writing: it names the scenario in which it becomes
*"retrospectively performative"*, marks its own shakiest assumption, and records
that a rejected alternative beats the chosen path on attestation cost.

That same honesty is why Challenge 9 is a genuine failure rather than a quibble.
An ADR that names its top-ranked failure and ships no mechanism against it has
converted a design risk into a *documented* design risk. Documentation is not
mitigation — and the ADR's central value claim (unwitnessed contract text becomes
*declining* debt) is precisely what pre-mortem #1 predicts will not happen.

### Conditions

1. **Resolve ratchet cadence, owner, and scheduled floor-raise before OBPI-04.**
   04 is where the ratchet lands; past that point pre-mortem #1 stops being a risk
   and becomes the architecture.
2. **Treat "04 and 06 together or not at all" as binding.** The ADR states that
   cutting 06 alone *is* pre-mortem #2 — the worst available combination — and it
   is the cut a mid-campaign schedule squeeze reaches for first.

### Recommendation on sizing

Commit only to the **01 → 03 slice** first, then re-decide. It discharges GHI #635,
removes a live double-render in AGENTS.md, and is a hard prerequisite for
everything downstream (§ Alternatives H). The full ADR is 10 OBPIs and 97 REQs — 66
of them BEHAVIOR, each requiring its own `@covers` test, none waivable — which is
the largest single unit on the Build-to-1.0 board, in a repo whose stated blocker
was accretion.

## Action items

| # | Item | Blocking? |
|---|------|-----------|
| 1 | Decide ratchet cadence / owner / floor-raise | Blocks OBPI-04, not 01–03 |
| 2 | Add a Gold Standard comparison against a validated local exemplar (Challenge 5) | No — cosmetic |
| 3 | Broaden Fidelity Assertions so distinct claims have distinct commands | No — but do it before closeout, when the assertions are run |
| 4 | Re-verify the 31.2% coverage figure at implementation time | No — Fidelity Assertions re-measure by design |
| 5 | Reconcile briefs 04–10 against the tree as 01–03 were | Recommended before each is opened; the reconciler cannot see pre-landed work (GHI #581) |
