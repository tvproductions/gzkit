<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Disagreements — Agent 0 and Agent 1

> **Meaningful disagreement is preserved here, not resolved into consensus.** A
> disagreement that is merely unresolved is more useful to a future investigator
> than an agreement that was manufactured.
>
> Agent 1 is **not epistemically subordinate** to Agent 0. Agent 0 leads
> reconciliation; that is a procedural role, not the authority to win an
> argument. Where Agent 1's challenge is stronger, the corresponding row in
> [`FINDINGS.md`](FINDINGS.md) moves to `QUALIFIED` or `REJECTED` and says so.

---

## Status: reconciled 2026-09-22 — eight entries

**Astra's Phase 2 report** is at
[`gzkit-engineering-assessment-adversarial-review.md`](gzkit-engineering-assessment-adversarial-review.md).
**The full reconciliation pass ran 2026-09-22**, after the operator lifted the
deferral. All 25 rows of its § 2 challenge table were mapped onto
[`FINDINGS.md`](FINDINGS.md) and dispositioned.

Counted directly from § 2: **25 data rows — 11 CONFIRM WITH QUALIFICATION,
9 REJECT, 3 DOWNGRADE TO HYPOTHESIS, 1 CONFIRM, 1 NEEDS MORE EVIDENCE.**

Where the pass landed, by status: **2 `CONFIRMED`** (F-032, F-033), **15
`QUALIFIED`**, **2 `DISPUTED`** (F-006, F-021), **14 `OPEN`**, **2 `REJECTED`**
(F-034, F-035, both pre-existing) — 35 rows in total. **Nineteen rows received a
Phase 2 challenge block and seventeen statuses moved**; F-001 and F-018 were
already `QUALIFIED` before the pass and carry their challenge without a status
change.

**Fourteen rows remain `OPEN`, and that is a deliberate classification, not an
oversight.** *(Ruled a settled disposition by the operator at `Q-14` on
2026-09-23, after the reasoning below was written.)* Astra reviewed pieces 01 and 02, not this register, and states its
own scope limit: *"This is not an exhaustive conformity audit"*, and the report's
subjective classifications, receipt population and historical gate events *"were
not independently reclassified."* **A row Astra did not reach was not exposed to
challenge, so it did not survive one.** Promoting such a row to `CONFIRMED` would
make the status word mean what the seeding note already refuses to let it mean.
**This pass could not meet Phase 3's stop condition on its own.** The operator
closed it at `Q-14` by ruling `OPEN` settled for an unchallenged row, rather than
by commissioning a second adversarial pass — which would have required a fourth
role the binding composition model does not have.

**Two `REJECTED` verdicts were not adopted**, and the reasons are recorded at
`D-01` and `D-05` rather than resolved by the lead's procedural role.

**Three rows of F-020's twenty-two-point disagreement register are themselves
rejected on counterevidence** and are no longer live disagreements; they are
recorded on that finding.

**One challenge row has no `F-###` to land on.** *"§3/§8: BDD gate largely
duplicates unit tests; retain only unique REQs"* — verdict **NEEDS MORE
EVIDENCE** — challenges a piece 01 claim that was never carried into this
register. Recorded at `D-08`. **A challenge with no row is a gap in the
register, not in the challenge.** *(Amended 2026-09-23: the claim does have a
measurement home — `M-F` — summarised in `README.md` § The measurement program.
It has no **finding**, which is the gap.)*

---

## Entries

### D-01 — Does a persistent system model exist, or only fragments of one?

- Findings touched:   F-006, and by inference F-013
- Agent 0 position:   Six intake surfaces each hold part of the project's durable knowledge, and none holds the model itself, so no surface is a backlog *against* a model. Risk and research-question have no home at all
- Agent 1 challenge:  *"Absence claim not sustained."* State/trust doctrine, CLI specification, architectural identity, source ontology and the OKF knowledge bundle exist [E7,E9,E10]; ADR consequences and research records hold risk and research content [E9,E10]. The claim *"Conflates full 42010 AD conformity with possession of useful system knowledge"*, and *"A concept need not have its own object"*
- Evidence for A0:    `01 § 2` object inventory, `01 § 4.4`, `01 § 8.2`; the three-session rediscovery loop recorded in the repository
- Evidence for A1:    E7, E9, E10 — named artifacts, each verifiable in the tree
- Disposition:        UNRESOLVED
- To resolve:         The two positions use *model* differently: A0 means a queryable object with coverage over concerns, A1 means possession of system knowledge in retrievable form. **The observation that settles it is whether any existing surface can answer "which decisions bear on this surface" without reconstruction** — `M-C` and `M-E` between them ask it. Neither agent can settle it by argument, and the rediscovery loop is evidence for A0 that A1's inventory does not address

### D-02 — Can a hierarchical REQ identifier outlive its work package?

- Findings touched:   F-002
- Agent 0 position:   `REQ-<adr-semver>-<obpi-NN>-<req-NN>` encodes parentage in identity, so the requirement cannot outlive the package that introduced it
- Agent 1 challenge:  *"Logical assertion, not observed property of the grammar."* The parser accepts an ID independently; storage lookup and deletion govern discoverability [E6]. 29148 permits relational identity [S2]
- Evidence for A0:    `src/gzkit/triangle.py:24-31`, the consolidated grammar
- Evidence for A1:    E6 — parser behaviour, independent of storage
- Disposition:        A0 CONCEDES
- To resolve:         Already resolved. **F-002's own Interpretation conceded this before the challenge arrived** — *"The identifier grammar is sound and globally unique. What is wrong is ownership, not syntax."* The Observation overstated what the Interpretation claimed, and the row is narrowed rather than defended. Recorded because a future investigator reading the original wording would re-derive the rejected form

### D-03 — What was destroyed when demoted briefs were deleted?

- Findings touched:   F-003, and F-001 which depends on it
- Agent 0 position:   A large fraction of all REQ acceptance criteria and FAIL-CLOSED constraints ever authored has been deleted by `gz adr demote`, demonstrating loss of enduring requirements
- Agent 1 challenge:  *"Deletion count is real; durability and causal attribution are unclassified."* 364 of 384 deletion events cluster in two deliberate demotion campaigns, largely unstarted work [E1]; the 16326 inference is invalid. Alternative: backlog retirement, with a smaller consequential retention problem underneath
- Evidence for A0:    `adr_demote.py:475`; `git log --diff-filter=D` over brief paths; `obpi_lifecycle.py:256-260` (*"A hollow exit 0"*); live behave tags pointing at deleted briefs
- Evidence for A1:    E1 — the clustering of deletion events into two campaigns
- Disposition:        MISSING EVIDENCE
- To resolve:         **Neither side has classified the deleted population.** The question is what share of the deleted REQs and constraints were durable engineering knowledge rather than retired backlog — `M-B` exactly. Recorded as `MISSING EVIDENCE` and not as `UNRESOLVED`, because the argument is premature rather than the evidence divided. The operator's `Q-01` ruling that the delete is collateral rather than designed is unaffected either way, and the dangling behave tags are a defect on their own terms

### D-04 — Does knowledge placement explain work-package duration?

- Findings touched:   F-001, F-025
- Agent 0 position:   Persistent knowledge carried inside transient work packages explains long OBPI duration — the investigation's central causal claim, asserted in piece 01 §§ 4, 6 and 8
- Agent 1 challenge:  *"No causal test; created-to-completed mixes queue and execution."* One OBPI open more than 33 days completed **3.25 hours after its first lock** [E2]. Alternatives: authorization and sequence waiting, scope coupling, churn
- Evidence for A0:    `01 § 4.4`, `01 § 6`; the duration distribution in `01 § 6`
- Evidence for A1:    E2 — lock-to-completion elapsed time against created-to-completed elapsed time
- Disposition:        MISSING EVIDENCE
- To resolve:         `M-G`, baselining duration as repeated measures against the eleven candidate causes F-025 lists. **F-025 already refuses to attribute duration to any cause, and its candidate list already contains Astra's alternatives** — so on this point the register and the challenge agree, and the disagreement is with piece 01's §§ 4, 6 and 8, which the operator had independently flagged for using unsettled findings as settled inputs. A0 concedes the causal claim; the placement observation underneath it is not conceded and is not challenged

### D-05 — Can the system retire what it detects?

- Findings touched:   F-021
- Agent 0 position:   The error-detecting loop works and is honest; what is missing is a mechanism to *retire* what it finds, so findings accumulate alongside the defects they describe. The grandfather ratchets are declared undeveloped arguments in 15026-2 § 3.1.7 terms
- Agent 1 challenge:  *"Historical audit and backlog sizes do not establish current failure"*, and *"A baseline is not automatically an undeveloped assurance argument."* July NC defects have subsequent repair commits; withdrawal, repudiation and demotion were exercised [E1,E5]. On the companion row: *"Too absolute"* — the rubric reads references from content and 36 `defect-resolution` records exist [E3]
- Evidence for A0:    `enforcement-claim-nc-audit-2026-07-18.md`; `evidence-record-contract.md`; `data/mechanical_witness_grandfather.json`; `Ledger.get_post_validation_failed_gates`
- Evidence for A1:    E1, E3, E5 — repair commits following the audit, retirement verbs exercised, 36 defect-resolution records
- Disposition:        UNRESOLVED
- To resolve:         The positions talk past each other and both are supported: A1 shows individual defects were repaired and retirement verbs exist; A0 claims no mechanism *links* a finding to its retirement, so the standing inventory cannot be reduced. **Astra's own alternative concedes the narrower form** — *"No adequate linked current-state reduction, despite useful archival signals."* The settling observation is whether any query returns the set of enforcement-claim non-conformances still live today. `M-D` asks it, and carries its own method problem: the prior audit disqualified itself as *"a stochastic surface auditing a stochastic surface"*

### D-06 — Do gzkit's gates decide anything?

- Findings touched:   F-019
- Agent 0 position:   The large majority of `gate_checked` events carry no observation of what was verified; `_run_gate_5()` prints and returns `True`; these are checks, not decision gates, in 24748-1 § 4.3.2 terms
- Agent 1 challenge:  *"Good historical payload concern; false generalization."* The claim *"Confuses a check, a gate condition, and the authorization consuming it."* Closeout blocks failures; completion emits human-attestation receipts [E4]. Alternative: a deprecated interface plus dispersed evidence, not universally absent gating
- Evidence for A0:    `src/gzkit/commands/gates.py:153-160`, `:261-263`; `governance/deprecations.py:41`
- Evidence for A1:    E4 — `completion_review` and closeout behaviour
- Disposition:        A0 CONCEDES
- To resolve:         Already resolved, in the challenge's favour on the general claim and A0's on the specific one. The surviving finding is about the deprecated `gz gates` interface and the historical payloads, not about the system's ability to gate. **The operator's `Q-07` ruling — re-point the covenant at `gz closeout` and `gz obpi complete`, keeping the five-gate vocabulary — was reached independently and lands in the same place.** Recorded because the original wording is the kind a later reader would cite as evidence that gzkit gates nothing

### D-07 — Is the anti-tautology stack ahead of the testing standard?

- Findings touched:   F-028
- Agent 0 position:   29119 has no vocabulary for RED-witness or mutation-witness classification — *"test oracle"* appears zero times in Parts 2–4 — and a `none` classification records a test that demonstrably cannot fail
- Agent 1 challenge:  *"Mechanisms useful; superiority and universal inference unsupported."* **Part 1 explicitly defines oracle and oracle problem** [S8]. And *"A passing selected baseline does not establish incapacity to fail on all relevant faults"*
- Evidence for A0:    `red_witness.py`, `mutation_witness.py` (GHI #963); the zero-occurrence count over Parts 2–4
- Evidence for A1:    S8 — ISO/IEC/IEEE 29119-1's own definitions
- Disposition:        A0 CONCEDES
- To resolve:         Already resolved. The zero-occurrence count over Parts 2–4 stands as stated and the mechanisms keep their KEEP class, but **the corpus does have the vocabulary and the finding searched the wrong parts of it.** A `none` witness is a local adequacy result over a selected baseline, not a proof of incapacity. **This is the clearest instance in the challenge table of a standards claim made from a partial read of the corpus, and it is a caution for Phase 4**

### D-08 — BDD duplication: a challenge with no finding to land on

- Findings touched:   none — this is the gap
- Agent 0 position:   Piece 01 held that the BDD gate largely duplicates unit tests and that only scenarios covering unique REQs should be retained. **This claim was never carried into `FINDINGS.md`**
- Agent 1 challenge:  **NEEDS MORE EVIDENCE.** *"ID/function overlap is insufficient"*; the 1012 note is *"misapplied to suite architecture"* [S6]; *"Same lines/REQs can be exercised under different conditions and assertions."* Alternative: some redundant tests amid useful boundary and acceptance checks
- Evidence for A0:    `01 § 3`, `01 § 8` — not re-derived by this pass
- Evidence for A1:    S6 — IEEE 1012's note read in its own scope
- Disposition:        MISSING EVIDENCE
- To resolve:         **`M-F` is this claim's measurement home, and it already exists** — *"Measure the real duplication between Gate 4 and Gate 2 before proposing removal"*, independent and cheap, with a method (run behave under coverage instrumentation, compare against the unit suite, verify the behave-only REQ count) and a note that `@wip` scenarios which never execute must be counted separately. **So the claim is not homeless in the investigation; it is homeless in the register.** Both Astra's verdict and `M-F` say the same thing in different vocabularies: measure before proposing removal. What remains for the operator is whether a finding should be authored so the claim carries a status, or whether `M-F` alone is a sufficient home for a REMOVE-class proposal that no finding asserts. **Either way the seeding of `FINDINGS.md` from pieces 01 and 02 was not exhaustive**, which is worth knowing before the register is treated as complete

---

**Phase 3's stop condition was met on 2026-09-23** — every row carries a settled
status, and the disagreements are recorded. Standing conditions:

- **`D-01` and `D-05` are live disagreements on load-bearing findings** (F-006,
  F-021) and must not be read as settled in either direction. A disagreement
  recorded is not a disagreement resolved, and this file exists to keep that
  distinction;
- the fourteen `OPEN` rows are settled under `Q-14`, **not confirmed** — nothing
  challenged them, and they may not be cited as having survived challenge;
- **Phase 4 remains unauthorised, and nothing in this file authorises it.**

---

## Entry schema

Each disagreement is recorded as:

```text
### D-NN — <the issue, stated neutrally>

- Findings touched:   F-0xx, F-0yy
- Agent 0 position:   what Phase 1 concluded, and on what basis
- Agent 1 challenge:  what Phase 2 asserts against it, in Agent 1's terms
- Evidence for A0:    repository references
- Evidence for A1:    repository references
- Disposition:        A0 CONCEDES | A1 CONCEDES | UNRESOLVED | MISSING EVIDENCE
- To resolve:         the specific observation that would settle it, and who can make it
```

**`MISSING EVIDENCE` is distinct from `UNRESOLVED`**, and the distinction is the
point of this file. `UNRESOLVED` means both positions are supported and the
evidence does not choose between them — a real disagreement. `MISSING EVIDENCE`
means neither is yet supported and the argument is premature. Recording the
second as the first would manufacture a dispute where there is only an unmeasured
question; those belong in `OPEN-QUESTIONS.md` or the measurement program.

Where a challenge lands, the disposition is recorded here **and** the status is
changed on the finding itself. The two must not drift.

---

## Amendments

- **2026-09-23 — stop condition met (`Q-14`).** § Status updated and the closing
  conditions rewritten. **No entry changed and no disposition moved.** `D-01` and
  `D-05` remain `UNRESOLVED` and are restated as standing conditions, because the
  moment a phase closes is the moment a live disagreement is most likely to be
  read as settled.
- **2026-09-23 — `D-08` given its measurement home.** Tracing `M-A` … `M-H` out
  of `01 § 12` showed that **`M-F` exists and is exactly this claim's measurement
  item.** The claim is homeless in the register, not in the investigation, and
  `D-08`'s *To resolve* is narrowed accordingly: the open question is whether a
  finding should be authored so the claim carries a status, or whether `M-F`
  alone suffices for a REMOVE-class proposal no finding asserts.
- **2026-09-22 — Phase 3 reconciliation pass run.** The operator lifted the
  deferral; all 25 rows of Astra's § 2 challenge table were mapped onto
  `FINDINGS.md` and dispositioned. **Nineteen rows received a Phase 2 challenge
  block; seventeen statuses moved** — 2 to `CONFIRMED`, 13 to `QUALIFIED`, 2 to
  `DISPUTED`, with F-001 and F-018 already `QUALIFIED`; 14 rows were left `OPEN`
  because Astra's non-exhaustive review never reached them, and silence is not
  survival. Eight disagreement entries recorded: `D-01` and `D-05` `UNRESOLVED`,
  `D-02`, `D-06` and `D-07` `A0 CONCEDES`, `D-03`, `D-04` and `D-08`
  `MISSING EVIDENCE`. **Phase 3's stop condition is not met by this pass** and
  cannot be — see § Status. **Two items for the operator:** `D-08` shows the
  seeding of `FINDINGS.md` from the pieces was not exhaustive; and F-014's
  qualification is Astra reaching, independently, the `Q-02` narrowing that is
  still awaiting a ruling.
- **2026-09-22 — Act 1 cold-read repair pass; challenge tally corrected.** The
  un-reconciled tally read *"roughly 26 rows, 8 REJECT"*. Counted directly from
  § 2 of the report: **25 data rows — 11 CONFIRM WITH QUALIFICATION, 9 REJECT,
  3 DOWNGRADE TO HYPOTHESIS, 1 CONFIRM, 1 NEEDS MORE EVIDENCE.** The contested
  share is **9/25**, not 8/26, and the prior enumeration summed to 24 against a
  stated 26. The "Created empty" entry below records the Phase 2 report as
  awaited; it is left standing as the dated record it is, and the report's
  arrival is stated in § Status above. **Unresolved:** the nine `REJECT` rows are
  still not mapped to `F-###` ids — that mapping is what the reconciliation pass
  produces, and until it exists a reader can tell that roughly a third of the
  register is contested but not which third. Separately, this file gates
  promotion to `CONFIRMED` on *"until this file is populated"* while
  `README.md` § Currently prohibited gates it on the Phase 2 report *"being
  read"*; two conditions on one act, for the operator to settle.
- **2026-09-22 — Created empty (Phase 3).** Schema fixed; no entries. Awaiting
  the Phase 2 report.
