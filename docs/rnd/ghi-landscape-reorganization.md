# R&D run — ghi-landscape-reorganization

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-09-20T09:52Z.

**Challenge.** Operator g0, current conversation · read 2026-09-20, verbatim:

> we are not going to start 0.37.0 now. I want to try rnd out where a ghi cleanup/triage
> spree happens. since the last rnd found issues with gzkit broadly, we can go beyond (but
> also augment) the current ghi-triage. rnd on big picture outcomes should be a way to take
> a macro perspective on what big picture sees in terms of organizing/reorganizing the
> ghi/fix landscape.

Two things are named. First, a **ruling**: `ADR-0.37.0` is not started now, so the airlock
findings surfaced by the 2026-09-20 report stay tracked and unselected. Second, the
**subject**: the GHI/fix landscape as a population, viewed from the altitude a big-picture
report takes, with `ghi-triage` augmented rather than replaced.

This run is the first exercise of `gz-rnd` v0.3.0's second subject — a population the
project already carries — which was added on the operator's direction earlier in this same
conversation.

---

## source · gz-rnd v0.3.0, the second subject

`.gzkit/skills/gz-rnd/SKILL.md` · read 2026-09-20

> **Two subjects, one frame.** A run studies either something new — pasted material, an
> unexplored capability — or **a population the project already carries**: a recurring
> defect class, a queue that grows faster than it drains, a family of issues that close
> individually and keep producing. The second is as legitimate a subject as the first and
> was added on the operator's direction, 2026-09-20. Ranking what is in the queue belongs
> to `ghi-triage`; asking *why this class keeps producing, and how these issues should be
> framed, consolidated or sequenced* is design work, and it belongs here.

The boundary this run must respect and test: `ghi-triage` ranks; this run asks why the
class produces and how the landscape should be shaped.

## source · what ghi-triage already does

`.gzkit/skills/ghi-triage/SKILL.md` (skill-version 5.2.1) · read 2026-09-20

> Real triage — read each issue, classify severity, recommend an order. The bundled script
> does the deterministic work (fetch, route, render the deliverable). The agent does the
> cognitive work (read each body, compose a short WHY per issue). Determinism is enforced at
> the rendering boundary; cognitive freedom lives only on the input edge.

> The deliverable is the rank-ordered list from Step 3, full stop.

Triage is **per-issue and ordinal**. It answers *what should I pull next*. It does not ask
whether two issues are the same finding, whether a family wants one artifact instead of
nineteen, or whether an issue is well-formed as an issue. That is the gap this run occupies.

## source · the measured residue

`docs/reports/big-picture/2026-09-19.md` and `2026-09-20.md`, re-measured 2026-09-20

1,001 closed issues at a **median age of 3.7 hours**, 71.2% closed within 24 hours — against
an open queue that has grown 9 → 32 → 55 → 57 since mid-August, 52 of 56 labelled `defect`.

The open queue is therefore not a backlog of the same kind of work as the closed one. It is
the **residue that the fast path does not absorb**. Characterising that residue — what makes
an issue stay open when the median issue closes the same session — is the run's first factual
question.

---

## decision · the run is scoped to one question

The operator narrowed the deliverable, 2026-09-20, selecting *"Study why the residue
exists"* over the offered design-then-apply option: narrow the run to one question — what
makes an issue stay open when the median closes in 3.7 hours — and let the answer determine
whether any reorganization is warranted at all.

This is the stricter reading of diamond 1 and it overrides the recommendation given. A
reorganizing structure proposed before the residue is characterised would be a design
answering a problem nobody has yet defined, which is the failure this diamond exists to
prevent. Whether the landscape wants reorganizing is now an **output** of the run, not a
premise of it.

Consequence for the disposition map: rows 2–5 cannot be filled until the residue question
is answered. Row 6 (`no action`) is a live possible outcome, not a formality — if the
residue turns out to be well-formed work correctly waiting on sequence, the correct
disposition is to leave it alone.

---

## source · the residue is size-sorted, and size gates on permission

Measured 2026-09-20 over every open issue body and the last 400 closed, parsing the
`Scope hint -> Estimated diff` field the `ghi-author` template requires. 54 of 57 open and
369 of 400 closed carry the field. Restricted to the three structured values:

| Estimated diff | Closed (n=231) | Open (n=42) |
|---|---:|---:|
| `<=10 lines` | 28% (64) | **2% (1)** |
| `<=100 lines` | 43% (99) | 45% (19) |
| `larger` | 29% (68) | **52% (22)** |

`<=10 lines` is **14x enriched in the closed population**. The open queue is not a random
sample of filed work held up by attention — it is size-sorted, and what sorts it is canon.

`AGENTS.md` § Defect-fix routing, verbatim:

> Without a GHI, fix directly when the change is small (about ten source lines or two
> files), sits in one surface, surfaced in flight, and a unit test covers it. Work that
> crosses briefs, changes a CLI, schema or runtime contract, or is new feature work is OBPI
> work, which the operator initiates.

The threshold in that rule and the discontinuity in the data are the same boundary. Below
it an agent may repair and close within the session; above it the only route is OBPI, and
`AGENTS.md` § OBPI Acceptance Protocol reserves initiation to the operator. **The residue is
therefore the accumulation of work no agent is permitted to start**, which is a different
claim from work nobody has got to.

A second, smaller category appears only in the open set: roughly four issues whose
`Estimated diff` is not a size but a sentence beginning *"unknown"* — *"unknown — this is a
design question"*, *"unknown until measured"*. These are not sized because they are not yet
decisions. They have no route because no route exists for an unanswered question.

**Limitation, stated because it bounds the claim.** This compares the current open residue
against everything ever closed — survivorship, not a cohort followed from filing. A cohort
study would measure whether a `larger` issue filed today is still open in 30 days. The
direction is strong enough to carry a hypothesis; it is not proof of a rate.

---

## source · the label signature inverts between the two populations

Measured 2026-09-20, 57 open against the 30 most recently closed:

| Label | Open (n=57) | Closed, last 30 |
|---|---:|---:|
| `eval-feedback` | 5% (3) | **47% (14)** |
| `investigation` | 2% (1) | **13% (4)** |
| `tech-debt` | 32% (18) | 20% (6) |
| `defect` | 93% (53) | 77% (23) |

`eval-feedback` marks a finding produced by a run that also specified its repair. It is
nearly half of what closes and a twentieth of what stays. A delegated pass that read all 57
open bodies in full reports the corresponding mechanic on the closed side: **30 of 30 closed
citing a commit SHA, 0 superseded into an ADR or OBPI, 0 closed as duplicate**, and 15 of
the 30 discharged on just **three** commits. The fast path is not thirty repairs; it is a
few sweeps each discharging a batch of findings that arrived with their fix already
specified.

## decision · the residue is defined by what an issue needs in order to end

This answers the run's question, and it **corrects the hypothesis recorded above**.

The earlier entry found the residue size-sorted — `<=10 lines` at 28% of closed against 2%
of open — and read size as the mechanism. Size is a **proxy, not the cause**. The
discriminator is whether an issue arrives with a commit-shaped answer. Small findings
usually do, which is why size correlates; but the open queue is not held up by bigness.

Counting from the 57 bodies: **8 are explicitly blocked on sequence** (ADR order, an
unpromoted pool ADR, an operator-held campaign box); **at least 14 name an unresolved design
question or an operator ruling as their next concrete action**; **19 are class-members whose
remedy is a class-level witness that does not exist**. The categories overlap, but their
union is most of the queue. What they share is that **none of them can be ended by writing
code** — and the fast path only knows how to end things by writing code.

Two structural producers keep the residue topped up, and both are canon colliding with
canon rather than work going undone:

- **The pool-ADR fence.** `AGENTS.md` § Architectural Boundaries 1 and 2 forbid promoting
  pool ADRs into the runtime track pre-1.0. #611, #766 and #767 are each parked behind a
  pool ADR. The fence has no expiry and no exception path, so anything routed there is
  parked until 1.0 by construction.
- **The homeless-corrective collision.** A correction against a `Validated` ADR must re-home
  to a feature ADR, while ascending-semver order withholds every feature slot above the one
  in flight. #871's own words: *"the collision is the steady state, not an edge case."*

A third producer is quieter and is a defect about the queue itself: **its cross-references
decay**. Eleven open bodies cite sibling issues as "(open)" that are now closed. #969's
argument rests on #889 being open; #889 is closed. Two issues (#815, #943) have had their
premises materially falsified by later work and neither was updated. Nothing observes the
queue's own staleness — which is an instance of the very family the campaign names.

**Consequence for the challenge.** A triage spree would not drain this queue, because
ranking does not supply a closure route. The queue is not disorganised; it is an accurate
record of decisions that only the operator can make, plus a thin layer of genuine decay.
That is a finding against reorganisation, not for it.

**A surprise worth recording.** The campaign's dated measurement has the
`doctrine-declared-without-mechanism` family at 19 of 32 open issues (59%) on 2026-09-02.
The pass that read every body today classifies 14 of 57 (~25%). Both are judgments by
different readers, so the comparison is suggestive rather than measured — but if the
direction holds, the family the campaign ranks as its dominant producer is **shrinking in
share while the queue grows**, and the growth is arriving from the chore estate, the ADR
lifecycle machinery and the pipe-gate instead. That is worth a live re-measure before the
campaign's sequencing is trusted on it.

---

## source · family taxonomy of the open queue

Delegated read-only pass, 2026-09-20: **57 of 57 open bodies read in full** (322,747
characters; median body 5,283). Folded into this record at operator direction *after* the
close. Stating that plainly, because this file's own convention forbids composing a record
afterwards: the taxonomy **was** available during the run and informed the closing decision
— specifically the "19 class-members awaiting a class-level witness" count — but it was not
transcribed at the time. This entry completes the record; it revises nothing.

**Epistemic status.** Family membership is a *reading*, not a measurement. The pass's own
caveat is carried: it self-reported a hand-transcription error in the two youngest age
buckets and said to trust computed counts over its listings. The same caution applies here.
Of its 14 F1 assignments, **9 are self-declared in the issue bodies and 5 are the pass's own
reading of the mechanism**.

| Family | Members | Shared mechanism |
|---|---|---|
| F1 doctrine-declared-without-mechanism | 14 — #799, #804, #807, #810, #907, #922, #926, #939, #950, #956, #1017, #1030, #1034, #1063 | A binding claim in one layer; the witness is absent, narrower than the claim, or never invoked |
| F2 a gate reports green over a state it cannot see | 6 — #808, #919, #969, #983, #998, #1032 | The control passes, but the question it answers is not the one its consumers read it for |
| F3 a forward edge with no governed reversal | 3 — #611, #930, #973 | A transition that cannot be taken back, leaving only a hand-edit canon forbids |
| F4 a declared state machine the runtime does not walk | 3 — #930, #1014, #1015 | `*_TRANSITIONS` enforced only on paths opting into `LifecycleStateMachine.transition()` |
| F5 handoff and session provenance is thin | 4 — #766, #767, #813, #1003 | Documents produced without the Layer-2 facts that establish authorship or derivation |
| F6 chore declaration diverges from chore behavior | 5 — #808, #997, #1009, #1011, #1044 | CHORE.md prose, `acceptance.json` and the actual subject are three uncoupled surfaces |
| F7 verifier-pipe-gate shell-recognition residue | 2 — #1012, #1013 | Command resolved by head over a tokenization blind to reserved words and heredocs |
| F8 content model richer than the verbs that write it | 6 — #799, #894, #921, #978, #983, #1018 | The CMS declares sections, tiers, ownership and attestor identity the verbs cannot each express |
| F9 homeless corrective residual | 3 — #804, #818, #871 | Canon selects a destination another rule forbids, or names none |
| F10 a delivery boundary nothing observes | 4 — #802, #815, #1034, #1062 | An artifact crosses out of the governed tree and nothing reports its state back |
| F11 vendor-doctrine currency | 2 — #943, #1019 | Each vendor's doctrine sole-sourced to one registry entry, so one release stales all of it |
| F12 adversary/acceptance machinery residue | 3 — #927, #993, #1028 | The falsifiability apparatus is keyed to REQs inside Heavy briefs, so direct-fix has no witness |

Cross-family members where the pass said so: #808 (F2, F6), #799 (F1, F8), #930 (F3, F4),
#983 (F2, F8), #804 (F1, F9). Singletons: #594, #832, #837, #968, #1039.

**Why this supports the closing decision.** Nineteen issues were classified `class-member` —
their remedy is a class-level witness that does not exist. Twelve families across 57 issues
means the queue is not an undifferentiated pile, but it is also not reducible: most families
have 2–6 members and each wants a different mechanism. There is no consolidation that
collapses the queue, which is what a reorganisation would have had to deliver.

**Overlap candidates, flagged with evidence and acted on by nothing.** #1014/#1015 (filed 44
seconds apart, identical probe output verbatim, one ruling asked twice); #1012/#1013 (51
seconds apart, same three surfaces and ancestor, both arguing they are distinct mechanisms);
**#1039/#1051** (same import-cycle mechanism, #1051 closed 14 minutes after #1039 was filed,
**neither cites the other**); #611/#930/#973 (each body carries a section pre-arguing it is
not a duplicate of #611 — the volume of that prose is itself the signal); #799/#939 (identical
blocker cited: `bullet_retention.py:49-59`).

**The F1 figure is a hypothesis and the campaign's sequencing rests on the older one.** The
campaign records 19 of 32 (59%) on 2026-09-02; this pass counts 14 of 57 (~25%). Different
readers, different dates, no shared method. Named in § Close as the one measurement this run
did not take.

---

## Disposition map

<!-- All six rows always present. State is `commissioned` or `not pursued`. -->

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | **commissioned** | Nothing. The two structural producers are architectural, but the pool-ADR fence is exactly what forbids routing them to a pool ADR. | Naming the collision rather than resolving it: the disposition the finding calls for is the one the finding says is unavailable. Operator ruling required; agents cannot initiate either way. |
| 2 | GHI / direct fix | **commissioned** | Re-measure and close the two stale-premise issues (#815, #943 control-surface half); apply #1051's landed fix as the template for #1039. | Genuine reductions on evidence, not queue-tidying. Each needs the operator's go on this row. |
| 3 | chore | **commissioned** | A queue-staleness chore: detect open bodies citing closed issues, and premises falsified by later landings. | 11 decayed cross-references measured today. Recurring, mechanical, measurable — chore-shaped by the class system's own criteria. |
| 4 | control surface, rule, doc, skill, hook | **commissioned** | Two: give `ghi-triage` a family and staleness pass beside its ranking; harden `ghi-author` Step 0's sibling-cut defense. | The Step 0 defense failed inside this very session — #1017 was in the recent-by-date skim and was not recognised as a member of #1063's class. |
| 5 | one-shot refactoring | **not pursued** | — | The pair-merge candidates (#1014/#1015, #1012/#1013) are work units, not refactoring. They belong to whoever pulls them. |
| 6 | no action | **commissioned** | Do not reorganise the queue. | The run's answer: the residue is an accurate record of decisions only the operator can make. Reorganising it would relabel a correct state. Revisit if the decay layer grows past the stale-cross-reference count measured today. |

## Close

**Challenge restated.** The challenge asked for a macro perspective on organising or
reorganising the GHI/fix landscape, with a cleanup spree in view. Deliberately restated at
the close: **the landscape does not need reorganising, and the run's value was establishing
that rather than doing it.** The queue is size-sorted only incidentally; what actually sorts
it is whether an issue can be ended by a commit. Most of the residue cannot, and is
correctly parked on operator decisions, on campaign sequence, or on class-level witnesses
that do not exist. What the landscape does carry is a thin, real decay layer — eleven stale
cross-references and two falsified premises — and that is a maintenance subject, not a
reorganisation.

**Frontier.** Empty. The run's single question is answered and its consequence for
reorganisation is recorded. One measurement is named as worth taking live but does not block
a disposition: whether the `doctrine-declared-without-mechanism` family is genuinely
shrinking in share.

**Sign-off.** Operator g0, 2026-09-20, at the disposition beat: **funded rows 1, 2, 3 and
4**; rows 5 (`not pursued`) and 6 (`commissioned`) stood as drafted. All six rows carry a
state and the frontier is empty, so diamond 1 is closed — **fund**.

Row 1 is funded as *propose only*. The IRON LAW is unchanged: an agent may draft the ADR
route for the pool-ADR fence and the homeless-corrective collision and put it in front of
the operator; only the operator initiates it, or does not.

## What this record does not license

No ADR, OBPI or chore is **started** by this run. Funding row 1 licenses a *proposal* and
nothing more — `AGENTS.md` § OBPI Acceptance Protocol reserves initiation to the operator,
and a funded disposition row does not move that line. `ADR-0.37.0` remains unstarted by the
operator ruling recorded in the challenge.

The four funded rows are diamond-2 work and carry their own machinery and gates: row 2
through `ghi-close`, row 3 through the chore class system, row 4 through the skill authoring
and sync rules, row 1 through a drafted proposal the operator rules on. This record
authorises none of them to skip those gates.

The one measurement this run names but did not take: whether the
`doctrine-declared-without-mechanism` family is genuinely shrinking in share. Two judgments
by different readers are not a measurement, and the campaign's sequencing currently rests on
the older one.
