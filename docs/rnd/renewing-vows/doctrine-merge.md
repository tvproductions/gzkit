# GovZero command doctrine — the June doctrine and the October run, merged

> **DRAFT. Not canon.** The canonical doctrine is still
> [`docs/governance/GovZero/command-doctrine.md`](../../governance/GovZero/command-doctrine.md),
> ratified 2026-06-10. This file is the merge the operator directed on 2026-10-08, verbatim:
> *"merge them, they assist in creating my doctrine"* (sent first as *"merge them, the assist
> in creating my doctrine"*). It is material that assists. The doctrine is the operator's to
> create from it. Nothing here binds anyone until the operator ratifies a text and it
> replaces the canonical file with a recorded attestation.
>
> **How it was built.** Parts marked RATIFIED are copied byte for byte from the canonical
> file (SHA-256 `ad96345626d6d06a55dd0f10ef044531f04cbdfaf13b04f20da6ede9186c604b`), with no word changed. Parts marked DRAFT are new. Every new
> statement names the article it traces to, where it comes from (a ruling of yours with its
> date, existing canon, or a text that was read), and what enforces it today. Where nothing
> enforces it, it says so. Run record: [`../renewing-vows.md`](../renewing-vows.md).
>
> **What it is for**, in the operator's words, 2026-10-08: *"binding/bounding doctrine for
> gzkit to hold me and agents to account."*

> **Re-based 2026-10-10.** Parts II and III were rewritten once after the operator closed
> frontier item 22 ('C': gzkit is built with a released gzkit) and ruled the seven-line
> statement of command ('it stands, add the seventh'). Part II now opens with that statement
> and cites `docs/governance/advisory-rules-audit.md` as the witness authority instead of
> grading enforcement by hand. Part III names the canonical procedures it sits beside
> (`obpi-pipeline-runbook.md`, `obpi-transaction-contract.md`, `obpi-runtime-contract.md`,
> `audit-protocol.md`, `charter.md`, `session-handoff-obligations.md`) and maps the six phases
> onto them. Part I and every RATIFIED part are unchanged.

## How to read this draft

The June doctrine set four layers and wrote the first. This draft keeps the first as it is
and writes the next two.

| Part | Layer | State |
|---|---|---|
| I | Philosophy: the ten articles | RATIFIED 2026-06-10, unchanged |
| II | Policies: the standing decisions that implement the articles | DRAFT |
| III | Procedures: how one piece of work is flown | DRAFT |
| IV | Practices, and what is still to be built | RATIFIED worklist, with DRAFT additions |

The test this draft applies to itself is the doctrine's own, Article 2: *"If the harness
does not enforce it, the doctrine does not contain it."* So each policy in Part II carries a
column, **Enforced today by**, and a policy with nothing in that column is marked **not yet
binding**. You then decide, policy by policy: build the enforcement, or strike the policy.

---

## Why this document exists

GovZero has always had procedures (the five gates) and practices (gzkit, the session discipline, the attestation records). What it has had only implicitly is the layer Degani and Wiener (1997) put first in their Four P's model of cockpit operations: an explicit operating philosophy from which policies derive, from which procedures derive, from which practices follow. Their field finding is the reason the gap matters. Procedures that no longer trace visibly to a philosophy are the procedures operators stop complying with, and the operator most likely to stop complying with GovZero under deadline pressure is me.

The gap has a second cost that is newly urgent. Each model release arrives with vendor guidance about what the model prefers, and without an explicit philosophy there is no principled way to decide which of those preferences to accommodate and which to refuse. The scaffolding audit becomes vibes. With the philosophy written down, the audit becomes mechanical: anything in the apparatus that exists to compensate for model weakness is negotiable and retires as models improve; anything that exists to implement the philosophy is not negotiable and survives every release. The aviation record supplies the philosophy almost ready-made, because aviation spent fifty years deciding what survives improvement in the automation. This document writes it down.

*(RATIFIED, unchanged.)*

## The Four P's, applied

**Philosophy** is the command doctrine below: ten articles stating what GovZero believes about authority, accountability, and automation, independent of any model, vendor, or tool.

**Policies** are the standing decisions that implement the doctrine in this practice: the five gates exist; a human attests before work ships; autonomy span is bounded; evidence means artifacts.

**Procedures** are the gate definitions, the briefing template, the attestation record schema, the substitution rules. Procedures are model-generation-specific and expected to change.

**Practices** are what actually happens in gzkit sessions, including the drift between procedure as written and procedure as flown. The drift is data. When practice diverges from procedure persistently, either the procedure has stopped tracing to the philosophy and should be fixed, or the practice is a compliance failure and should be named as one. The Four P's give the diagnostic: trace the divergent item upward and see where the chain breaks.

*(RATIFIED, unchanged.)*

---

# Part 0 — Candidate text, drafted under the go on row 4 (2026-10-10)

> **Candidate, not canon.** The operator gave row 4 its go on 2026-10-10 ('go on row four')
> and named the statement of command and the terms as the first part. This part is the text
> proposed to stand at the head of the merged doctrine, in the doctrine's own voice. Each
> line names its source. It replaces nothing until the operator ratifies it with a recorded
> attestation; then it sits above the ten articles in
> `docs/governance/GovZero/command-doctrine.md`.

## Statement of command

1. One human commands. As commander that human shapes intent and decides what the force is
   tasked to do. As captain the same human signs for what ships and can override anything.
   It is one standing and does not divide. *(Article 1; rulings of 2026-10-08.)*
2. Command reaches the work only as orders the harness carries: standing orders for every
   position, a tasking order for one work package. The order is what carries a role's
   auspices. *(Articles 2 and 4; ruling of 2026-10-10.)*
3. Every obligation has a position, and every position leaves a record. Crew fill positions
   and command nothing. Every obligation has a position is the lapses' remedy. *(Article 7;
   rulings of 2026-10-08 and 2026-10-10.)*
4. The commander holds positions too, and is bound by doctrine and policy until changing
   them on the record. *(Article 1; ruling of 2026-10-08.)*
5. The campaign says what the force does next and when. Doctrine sets no dates and carries
   no worklist. *(Ruling of 2026-10-09 on the campaign; ruling of 2026-10-10.)*
6. Work is assessed from records by someone who did not do it. Release is the captain's.
   *(Article 7; Article 1; Gate 5.)*
7. The orders that bind construction are the last release's. Doctrine under construction is
   product until released, and is proven on another project before it binds its own making.
   *(Ruling of 2026-10-10, frontier item 22.)*

Ruled whole by the operator on 2026-10-10: 'it stands, add the seventh'.

## Terms

- **Commander.** The one human, as the shaper of intent and the decider of what the force is
  tasked to do. **Captain.** The same human, as the holder of the signature and the override.
  The operator is both and is not crew. *(Ruling of 2026-10-08: 'i am commander and shape
  intent, i am not crew, but i am captain, you are crew'.)*
- **Position.** An obligation and a role to fulfil it. **Role.** What the position gives its
  holder to fulfil the obligation; it has bounds and auspices, and the holder has no
  authority apart from it. **Crew.** The actor implementing within the role's bounds and
  under its auspices. Every agent is crew, the orchestrating session included. *(Ruling of
  2026-10-08: 'the position is an obligation and a role to fulfill the obligation, the crew
  is the actor implementing within the bounds and auspices of that role'.)*
- **Force.** What has doctrine, assets (its table of organization and equipment) and
  abilities. **Doctrine.** The force's: the ten articles and this statement. **Campaign.**
  What focuses the force's abilities for specified goals; the Magna Carta is gzkit's.
  *(Ruling of 2026-10-09: 'a force has doctrine, assets (ToE), and abilities. a campaign
  focuses these abilities for specified goals'.)*
- **Order.** How command reaches the work: a standing order binds every position; a tasking
  order binds one work package and carries the role's auspices. *(Line 2.)*
- **Release.** The captain's signature on what ships; in gzkit, Gate 5 attestation, which is
  return to service. *(Line 6; `AGENTS.md` § Gate Covenant; 14 CFR § 43.9 as landed.)*

## Article 3, title amended (body unchanged)

Ratified title: "The model is a crew resource, not a crew member". Ruled 2026-10-08 ('a'):
an agent is crew, and the title is amended; what the article allocates is unchanged, "the
model decides nothing that ships". Candidate title: **"The model is crew, never in
command."** The body is not touched by this candidate; whether it gains the position and
the role is an item travelling with row 4 (frontier item 15).

---

## The reconciliation of June (candidate, drafted under the go on row 4, 2026-10-10)

Three acts of 2026-06-09 and 2026-06-10 disagree in seven places and were never reconciled
(run record, decision *the work of 2026-06-08 to 2026-06-10 is discrepancy*). The operator
has ruled three readings: the freeze is a statement about assets; a doctrine is not a plan,
so the campaign did not subsume the doctrine; "retires now" is the campaign's to time. Each
pair below is settled by one of the seven lines or by one of those readings, or is marked
as the agent's proposal for the operator's correction.

| # | The disagreement | Settled by | Resolution (candidate) |
|---|---|---|---|
| 1 | Freeze: subtraction has equal standing. Campaign, a day later: every reductive move is deferred past 1.0. | Line 5; the operator's reading that the freeze is about assets | The freeze states how much mechanism the force carries; when any of it is retired is the campaign's to say. The campaign's deferral governs timing; the freeze's sentence is kept as a statement of assets and loses its standing as a schedule. |
| 2 | Campaign: reduction deferred. Article 10: accumulated ritual "retires now". | Line 5; the operator's reading | Article 10 keeps its criterion (ritual that stops earning its place is retired) and gives up its date. "Now" is struck from the doctrine's text and the retirement is timed by the campaign. *Agent's proposal: the amendment of Article 10's wording.* |
| 3 | Freeze: too much mechanism; a new check only on observed drift. Article 2: six new mechanisms, one a gate precondition. | Line 3; line 7 | Both hold at once once positions are distinguished from assets. Article 2's six items are obligations and each gets a position (line 3); whether a position is met by a new mechanism or by a briefing is the policy question put 2026-10-09 (what a policy is, lines 1 to 3, unanswered). Line 7 adds: a new mechanism binds construction only once released. |
| 4 | Campaign supersedes all prior plans. The doctrine's worklist landed after it and is named by no campaign edition. | Line 5; the operator's reading that a doctrine is not a plan | The doctrine carried a plan it should not carry. The six-item worklist leaves the doctrine's text and enters the campaign as items the operator sequences, each keeping the article it implements. The pool ADR `command-doctrine-internalization` is the vehicle the campaign names. *Agent's proposal: the campaign amendment that adopts the worklist.* |
| 5 | Freeze: cut, then "measure the residual". No measurement; no owner. | Line 3 | A measurement with no position is a lapse. It gets a position or it is struck. *Agent's proposal: struck, since the operator read the sequence as dead and the campaign deferred reduction.* |
| 6 | Freeze's text: "the third state is empty". The file's own table contradicts it. | Line 3; corrected 2026-10-09 | The scorecard's text was corrected on the operator's go for the lapses; the freeze block is a dated record and is cited as such. |
| 7 | Article 10: the coherence audit "runs at every major model transition". No run found. | Line 3 | The audit is an obligation with no position. It gets one, named in the campaign, with its trigger. *Agent's proposal: the position is the maintenance visit of the rhythm's slower tier, due on the signal of a model transition.* |

What this reconciliation does not do: it does not amend the campaign plan or the scorecard;
those are later parts of row 4. It does not decide what a policy is. It records that the
three acts are placed by the operator's five terms (the freeze about assets, the doctrine
the force's, the Magna Carta the campaign) and that under line 5 the doctrine carries no
worklist and sets no dates.

---

## The rhythm (candidate, drafted under the go on row 4, 2026-10-10)

Three tiers. The first is ratified; the two slower ones are advisory until each has a
signal, and this text says so of itself. *Avoid* "weekly" and "each week" for any tier;
*avoid* "the account" for the handoff.

**The session tier** (operator-ratified 2026-07-18, verbatim: "AGENTS.md -> how we work;
magna carta -> what we are working on. handoff -> what we were doing last. airlock -> a
sortie into the environment. handoff -> a market [marker] for when we leave the session.
That should be our rhythm."). Each session: `AGENTS.md` is how we work; the campaign plan is
what we are working on; the handoff is what we were doing last, checked against live state
before anything is acted on; the airlock is the sortie into the environment; the handoff on
leaving is the marker. The handoff is briefed as a transfer of position responsibility, in
four parts: preview from the status displays, verbal briefing, assumption, review (JO
7110.65BB Appendix A; JO 7210.3EE 2-2-4 for the checklist's content). The briefing gates
nothing; the relieving session owns the completeness of its own briefing as much as the one
leaving. *(Line 3; policy 14; ruling of 2026-08-17.)*

**The republish tier** (ruled 2026-10-07: 'Two slower tiers, signal-triggered'). A new
edition of the campaign plan folds its amendments into the body and the rulings register.
It comes due on accumulated amendments, announced, never on a calendar, and every ruling is
carried or withdrawn explicitly in the fold. Advisory until the signal is built; the signal
today is the count of amendments on the active edition, read by hand. *(Line 5: the campaign
sets dates, so the republish is the campaign's own beat.)*

**The maintenance tier** (same ruling). Due chores and issue triage are flown together as
one named maintenance visit, a scheduled work package of the operator's own design (AC
120-16G § 6-1). It comes due when the chore board announces it; the operator keeps the
frequency ('I maintain frequency', 2026-09-12). Each run of a chore is a ledger event; a
finding is not (ruled 2026-10-07). The coherence audit of Article 10 is a task of this
visit, due on the signal of a model transition. *(Line 3; policy 13; the agent's proposal
of the reconciliation, pair 7.)* Advisory until the board's signal is wired; the
accumulated-work signal reads `unmeasured` today (GHI #1009).

**What the rhythm is not.** It is not a calendar, and no tier gates: staleness announces.
The operation tier adds nothing, because closeout and then release are canon, and the first
flown sortie is a campaign gate behind `ADR-0.38.0`, not a beat.

---

## Campaign amendment of 2026-10-10 (candidate text, drafted under the go on row 4)

> The campaign plan is operator-ratified canon and is not edited ahead of ratification
> (precedent: handoff of 2026-10-07). The entry below is drafted in the plan's own amendment
> form, ready to be appended to `docs/governance/build-to-1.0-campaign-2026-09-20.md`
> § Amendments on the operator's word, with the operator's verbatim ratification in its
> first line. Until then it binds nothing.

### 2026-10-10 — the force's doctrine is named; the IOC waypoint; the governor is the last release (awaiting ratification)

**Operator (`g0`), verbatim (2026-10-10):** *[the operator's ratifying words go here]*.
Drafted under the go on row 4 of R&D run `renewing-vows` ('go on row four', 2026-10-10),
signed off *fund* the same day ('the restatement stands, fund').

**What changes.**

1. **The campaign names the force's doctrine.** A force has doctrine, assets and abilities;
   a campaign focuses those abilities for specified goals (operator, 2026-10-09). This plan
   is the campaign. The force's doctrine is `docs/governance/GovZero/command-doctrine.md`,
   ratified 2026-06-10, as it stands and as amended by the operator from the candidate text
   in `docs/rnd/renewing-vows/doctrine-merge.md` Part 0. No prior edition named it. Doctrine
   sets no dates and carries no worklist (statement of command, line 5): the doctrine's
   six-item worklist ("What changes in gzkit") is therefore carried here, each item keeping
   the article it implements, through `ADR-pool.command-doctrine-internalization`, which the
   operator sequences like any other pool item. *(Reconciliation pair 4; the agent's
   proposal, ratified or not by this entry's first line.)*
2. **The IOC waypoint** (ruled 2026-10-07: 'A waypoint before 1.0'). Initial operational
   capability is a named point on the route: `ADR-0.35.0` through `ADR-0.38.0` landed, S1
   flown on a non-gzkit substrate (§ 6 Movement E item 3), and the four theatre-canon
   staleness items repaired. Each condition is read from the ledger or a closed issue, never
   from prose. 1.0 is full operational capability; § 5's ten gates are untouched; nothing is
   post-anything by default. The waypoint sequences and excludes nothing. The identifier
   migration stays timed to 1.0.
3. **The governor is the last release** (ruled 2026-10-10, frontier item 22: 'C'). gzkit's
   construction is governed by the released gzkit, not the working tree; doctrine and
   positions under construction are product until released and proven on another project
   before they bind their own making. The operator's intended patch release is the first
   step. Pinning the surfaces a session loads from the tree to a release is unsized and is
   proposed only (row 1 of the run).
4. **The republish signal has fired.** This edition carries 46 dated amendments. Under the
   rhythm (session tier ratified 2026-07-18; two slower tiers ruled 2026-10-07), a new
   edition folds them into the body and the rulings register; the fold carries or withdraws
   every ruling explicitly. The operator cuts the edition; this entry announces and gates
   nothing.

**What does not change.** TOPMOST and the working order inside `ADR-0.35.0` (§ Amendments
2026-10-05). The IRON LAW. The three-pillars hold on GHI #1028. Rows 1, 2, 3 and 5 of the
run have no go; chores wait until the run's row-4 work is directed to a close ('let's do
chores after rnd', 2026-10-09). The freeze of 2026-06-09 stays a dated record; the
reconciliation of the three June acts is candidate text in the same Part 0 and is ratified
with the doctrine, not by this entry.

---

## The weaponeering rule (candidate rule file, drafted under the go on row 4, 2026-10-10)

> Proposed as `.gzkit/rules/weaponeering.md`, in the rules' own form (frontmatter, version
> marker, binding claims, named witness). It is not written into `.gzkit/rules/` ahead of the
> operator's word, because a rule file is loaded by agents on the paths it names and the
> scorecard carries a row per rule. Its witness, the runtime check, lands with the sortie
> layer after `ADR-0.35.0` briefs 15 to 20 (row 1, proposed); until then the rule says of
> itself that it is advisory, which is the one state canon allows a declared discipline
> without a mechanism. Ruled 2026-10-05 ('2. A (but what about C?)', then 'A with
> evidence-cited subtraction and free addition').

```markdown
---
id: weaponeering
paths:
  - "src/gzkit/pipeline_dispatch.py"
  - "src/gzkit/pipeline_runtime.py"
  - ".gzkit/skills/gz-obpi-pipeline/**"
  - "docs/design/adr/**/obpis/*.md"
description: The requirement's kind fixes the sorties a work package flies; subtraction cites evidence, addition is free
---

<!-- rule-version: 0.1.0 -->

# Weaponeering (gzkit)

> **Rule version:** `0.1.0` — first edition, from R&D run `renewing-vows` (operator ruling
> 2026-10-05, verbatim: "A with evidence-cited subtraction and free addition"; row 4 go
> 2026-10-10). **Advisory until its witness lands**: the runtime check is part of the sortie
> layer proposed after `ADR-0.35.0` briefs 15 to 20. Until then the planner reads this rule
> and the completion gate does not; a sortie set that departs from it is a finding for the
> operator, not a refusal.

## Operative claims

1. **The kind of a requirement fixes its standard sortie set.** A `[behavior]` REQ flies
   three sorties in order: constraints, red, green. A `[support]` REQ flies one documentary
   sortie. A `[structural-fence]` REQ flies none and is audited at closeout through its
   proof channel (ADR-0.0.59; `gz validate --req-kind-discipline`).
2. **The constraints sortie is a Design act.** It lands the contracts the work must obey
   (interfaces, invariants, stubs) before any failing test, so that red fails on an
   assertion and not on a missing symbol. Its product travels in the order.
3. **Subtraction cites evidence.** A standard sortie is skipped only when its product
   already exists on the ledger and the order cites it: red, when an assertion-class red
   receipt for the REQ exists on the base tree; constraints, when the contract exists and
   the brief names the symbol. No other ground skips a sortie.
4. **Addition is free.** An order may add sorties to the standard set without justification.
5. **Green and assessment are never waived.**
6. **The runtime checks the rule; the planner never decides it.** Planner discretion over
   the sortie set is refused. Until the runtime check exists, this claim is the advisory
   part of the rule.

## Witness

None yet. The check belongs to the sortie layer (row 1 of the run `renewing-vows`, proposed
after `ADR-0.35.0` briefs 15 to 20). Measured 2026-10-05 for claim 2: 207 of 282 red
receipts on the ledger failed on `error` (the symbol did not exist) rather than on an
assertion. Reclassify this rule from advisory when the runtime refuses a sortie set that
departs from claims 1, 3 and 5.

## Do Not

- Do not skip red because "the test would obviously fail"; cite the assertion-class receipt
  or fly it.
- Do not fold constraints into red; a red that fails on `error` has flown no constraints.
- Do not let a planner, a skill or a session choose the sortie set; the kind chooses it.
```

What this candidate does not do: it does not write the file, does not add the scorecard row
a new rule needs, and does not build the runtime check. On the operator's word the file is
written, the scorecard row is added with the "Advisory" grade and this witness note, and the
control surfaces are regenerated.

---

# Part I — Philosophy (RATIFIED, unchanged)

## The command doctrine

### Article 1. Accountability is non-transferable

One human signs for the work. The signature does not move to the model, the harness, the vendor, or the gate that passed. This is the GovZero analogue of 14 C.F.R. § 91.3, and the welding matters as much as the assignment: direct responsibility and final authority are one clause, not two. Whoever holds the signature holds override authority over every other element of the pipeline, and whoever holds override authority holds the signature. Any proposal that separates them, in either direction, is rejected on its face.

### Article 2. Authority must be instrumented, not asserted

A captain's authority over a human crew rests on shared consequences and a common operating manual. The model shares neither. It follows that command over a model is exactly as real as the harness that enforces it, and no more. Authority asserted in the context window is a briefing: necessary, and unenforceable. Authority implemented in the harness, in CI rules, file checks, diff gates, and halt conditions, is the only kind the model actually answers to. Every article below that imposes an obligation on the model is therefore really an obligation on the harness. If the harness does not enforce it, the doctrine does not contain it.

### Article 3. The model is a crew resource, not a crew member

Crew resource management never promoted the first officer to command; it obligated the whole crew to keep the commander informed and made silence a violation (Helmreich et al., 1999). The same allocation applies here, in both directions. The model is used fully: it drafts, flags, surfaces, challenges, and proposes, and a practice that underuses a capable model is leaving crew resources idle, which CRM treats as a failure. And the model decides nothing that ships. Its challenges are inputs to judgment, never substitutes for it. Designing the harness so the model can effectively surface concern is part of the doctrine; treating surfaced concern as approval is a violation of it.

### Article 4. Uncommanded change is an annunciation failure

The documented tendency of strong models to tidy beyond scope, draft unrequested artifacts, and create defensive backups is not enthusiasm. It is the software equivalent of uncommanded control inputs, and the mode-error literature says what unannunciated state divergence does to a supervisor's situation awareness (Sarter & Woods, 1995). The doctrine response: every run is preceded by a scope manifest, every run is followed by a diff of delivered work against commanded scope, and every artifact outside the manifest is annunciated before the run can pass any gate. The model is not asked to behave. The harness is built to notice.

### Article 5. Model identity is an attestable fact

Current releases can decline a request at the API layer and complete it on a different model, and routing, fallback, and substitution will only proliferate. An attestation that does not record which model produced the work attests less than it claims. The attestation record therefore carries the served-model identity for every gated artifact, and substitution is handled the way airline dispatch handles inoperative equipment: by explicit prior relief, not silent acceptance. A standing substitution policy states which fallbacks are acceptable for which classes of work. A substitution outside the policy fails the gate. A substitution inside the policy is recorded, not waved through.

### Article 6. Autonomy span is set by attestation capacity, not model endurance

Models can now run for hours. The attestor still reviews at human speed, and evidence accumulates faster than review capacity as run length grows. Letting the model's endurance set the checkpoint cadence is letting the autopilot decide when the pilot looks up. The doctrine sets it the other way: a run is capped at the volume of change one attestation can honestly cover, as a configured policy parameter, revisable deliberately and never by drift. When a model release extends what is possible, the parameter is re-decided, not silently inherited.

### Article 7. Evidence is artifacts, not narration

A model's account of its own reasoning is generated output, carrying the same verification burden as everything else it generates, and the current releases largely decline to provide it anyway. GovZero loses nothing, because the gates never properly rested on narration. Evidence is the ADR, the failing-then-passing test, the diff, the Gherkin scenario, the recorded model identity, the scope-conformance report: artifacts the model cannot retroactively edit and the attestor can independently check. Where self-narration was being used as comfort, retire it. Where its absence hurts, the hurt is diagnostic visibility, and the remedy is better artifacts, not pleas for testimony.

### Article 8. Efficiency is a constraint, not the objective

Token economics is fuel planning: a real discipline, practiced seriously, and never the reason the flight exists. The throughput frame optimizes output per token and carries no liability term in its objective function; the doctrine adopts its techniques and rejects its objective. Minimum fuel is a hazard, and a pipeline optimized to the edge of its verification budget is the software version of landing on fumes. The early empirical record points the same direction: in fully automated pipelines, verification, not generation, dominates token cost (Salim et al., 2026). Spending to verify is not overhead on the work. On the current evidence it is most of the work.

### Article 9. Proficiency is maintained deliberately

Automation that performs continuously degrades the supervisor's ability to perform when it stops, and the aviation regulator's remedy was scheduled manual operation in revenue service, not nostalgia for hand-flying (Federal Aviation Administration, 2013). The enterprise field record now shows the same erosion channel in knowledge work: workers using generative tools can complete tasks without retaining what the task would have taught, doing without learning (Armstrong & Shah, 2026). The drift phase is GovZero's equivalent, and this article makes it doctrine rather than temperament: deliberate intervals of unassisted work, scheduled and logged, scoped to the skills the practice cannot afford to lose. The schedule is reviewed like any other safety-critical maintenance. Skipping it under deadline pressure is exactly the failure mode the aviation record predicts, because deadline pressure is when the automation is leaned on hardest.

### Article 10. Procedures earn compliance through coherence

Every gate, check, and template in gzkit must trace upward through a policy to an article of this doctrine. Anything that cannot be traced is either workaround scaffolding for a past model generation, which retires on its own schedule, or accumulated ritual, which retires now. This is Degani and Wiener's finding turned into a maintenance rule: incoherent procedure is what breeds noncompliance, so coherence is audited, not assumed. The audit runs at every major model transition, and its two questions are fixed. Does this item implement the doctrine? Then it stays, whatever the vendor guidance prefers, and any output-quality cost is paid knowingly and measured. Does it compensate for a model weakness? Then it is benchmarked against the current release and retired the day it stops earning its place. The cure for procedural drift is not fewer procedures. It is procedures that visibly mean something.

---

# Part II — Policies (DRAFT, re-based 2026-10-10)

## The statement of command (ruled by the operator, 2026-10-10)

Seven lines. They are the operator's ('it stands, add the seventh'), and every policy below
hangs from one of them.

1. One human commands. As commander that human shapes intent and decides what the force is
   tasked to do. As captain the same human signs for what ships and can override anything.
   It is one standing and does not divide.
2. Command reaches the work only as orders the harness carries: standing orders for every
   position, a tasking order for one work package. The order is what carries a role's
   auspices.
3. Every obligation has a position, and every position leaves a record. Crew fill positions
   and command nothing. Every obligation has a position is the lapses' remedy.
4. The commander holds positions too, and is bound by doctrine and policy until changing
   them on the record.
5. The campaign says what the force does next and when. Doctrine sets no dates and carries
   no worklist.
6. Work is assessed from records by someone who did not do it. Release is the captain's.
7. The orders that bind construction are the last release's. Doctrine under construction is
   product until released, and is proven on another project before it binds its own making.

## Terms (ruled 2026-10-08 and 2026-10-09)

- **Position**: an obligation and a role to fulfil it. **Role**: what the position gives its
  holder, with bounds and auspices. **Crew**: the actor implementing within those bounds and
  under those auspices. Every agent is crew, the orchestrating session included; the operator
  is commander and captain and is not crew.
- **Force**: has doctrine, assets (ToE) and abilities. **Campaign**: focuses those abilities
  for specified goals. The ten articles are the force's doctrine; the Magna Carta is the
  campaign; the six-phase process is how the commander employs the force.

## Policies

Each policy names the line of the statement and the article it traces to. The witness column
names the canonical surface; whether that surface is mechanical or advisory is the
scorecard's to say (`docs/governance/advisory-rules-audit.md`), and this draft does not
re-grade it. "None" means the scorecard carries no row for it.

| # | Policy | Line / Article | Where it comes from | Witness |
|---|---|---|---|---|
| 1 | Only the operator initiates a work package and only the operator attests that it is complete. | 1, 6 / Art. 1 | `AGENTS.md` § OBPI Acceptance Protocol; § Gate Covenant (ADR-0.0.36) | `gz obpi complete` refuses without attestation; initiation is prose |
| 2 | Control is centralized and execution is delegated: one session tasks and is told of every change; small focused agents do the work. | 2 / Art. 2, 3 | Operator 2026-10-05; JP 3-30 ch. I § 3 | dispatch records; the run's position and outcome are `ADR-0.35.0` briefs 15 to 18, unbuilt |
| 3 | An agent is crew: it drafts, flags, challenges and proposes within its role, and decides nothing that ships. | 3 / Art. 3, title to be amended | Art. 3; rulings 2026-10-08 | Gate 5 |
| 4 | Every work package is commanded in writing before it starts: a tasking order with scope, constraints, stop conditions, expected artifacts and reasoning. | 2 / Art. 2, 4 | June worklist item 1 (the captain's brief); operator 2026-10-05; JP 3-60 phase 4 | none; the brief's Allowed Paths and the plan-audit receipt exist, no tasking record does |
| 5 | Constraints are worked out before execution and travel in the order. | 2 / Art. 2, 4 | Operator 2026-10-05 and 2026-10-08; JP 3-30 (special instructions in the order) | none |
| 6 | What is protected and what is restricted is declared, and a file touched outside it is found. | 3 / Art. 4 | Brief Allowed Paths; JP 3-60 no-strike list; **direct fix 2026-10-10** | `gz obpi complete` and `precomplete` refuse on out-of-scope files (GHI #1181, held local); airlock exit reports them (GHI #1185, held local) |
| 7 | The means are fixed by rule, never by the planner; green and assessment are never waived. | 2 / Art. 2, 8 | Operator 2026-10-05 (weaponeering) | none |
| 8 | Whoever does the work does not assess it. | 6 / Art. 3, 7 | spec and quality reviewers; Step 4b by another vendor's model | Step 4b required before Gate 5; nothing checks who reviewed |
| 9 | Assessment is specified before execution and has five outputs: hit, works, effect on the surrounding system, means as estimated, reattack. | 6 / Art. 4, 7 | JP 3-60 phase 6; operator 2026-10-05 | hit: ARB receipts; works: REQ coverage and Step 4b; system: the scope report, lapsed 2026-06-19 and restored under #1181; means: none |
| 10 | Evidence is an artifact with its source; a crew's own report is an input. | 6 / Art. 7 | `model-selection.md` claim 5; JP 3-60 App. D | ARB receipts; the ledger |
| 11 | Rigour scales on two axes: lane (does an external contract change) and integrity level (how silently and irrecoverably the surface fails). | 2 / Art. 6, 8 | Operator 2026-09-23, 2026-09-25, 2026-09-22, 2026-10-07; IEEE 1012-2024 cl. 5 | lane: a required field; integrity level: none, PROVISIONAL |
| 12 | A defect is a problem report: recorded, classified, resolved, closed; one left open at a release is assessed and reported. | 3 / Art. 7, 10 | the GHI; `ghi-triage`; `ghi-close`; FAA AC 00-71 § 3.1 and AC 20-189 § 4.1, read 2026-10-08 | by skill |
| 13 | Maintenance is scheduled or unscheduled; a scheduled task is applicable and effective, and each run is a ledger event. | 3 / Art. 10 | chore design 2026-09-12; operator 2026-10-07; AC 121-22D | `gz chores status` announces; the event is unbuilt |
| 14 | A transfer of position responsibility is briefed in four parts, from a facility checklist, and gates nothing. | 3 / no article (open, item 15) | Operator 2026-08-17; JO 7110.65BB App. A; JO 7210.3EE 2-2-4 | the handoff system; `gz handoff decide` |
| 15 | The rhythm: the session tier as ratified 2026-07-18; two slower beats, a republish and a maintenance visit, due on a signal, never a calendar. | 5 / Art. 9, 10 | Operator 2026-07-18 and 2026-10-07 | session beat: hooks and orientation; slower beats: none |
| 16 | The span of a run is capped by what one attestation can cover. | 4 / Art. 6 | Art. 6; June worklist item 4 | none ("Gap" in the article's own appendix) |
| 17 | Unassisted work is scheduled and logged. | 4 / Art. 9 | Art. 9; June worklist item 5 | none ("Gap") |
| 18 | The model that did the work is recorded; model and effort are assigned by role, on the agent definition. | 2 / Art. 5, 8 | Art. 5; operator 2026-10-05; documentation read 2026-10-06 | none ("Gap"); `model-selection.md` to be corrected |
| 19 | **The governor is the last release.** What binds construction is the released gzkit; the working tree is product until released and proven elsewhere. | 7 / Art. 2 | Operator 2026-10-10, 'C' | none; the first step is a release, and the pinning of session-loaded surfaces is unsized |
| 20 | The operator abides by doctrine and policy and encourages adherence, and may override and change policy on the record. | 4 / Art. 1 | Operator 2026-10-08 | the rulings store; `gz handoff decide`; what "encourage" consists of is open |

Policies 1, 16, 17, 19 and 20 bind the operator; the rest bind the crew, which under
Article 2 means they bind the harness. Not policy: the order of work and the IOC waypoint,
which belong to the campaign (line 5).

**What is not reconciled.** The freeze of 2026-06-09, the campaign's ratification and the
command doctrine disagree in seven places (run record, decision *the work of 2026-06-08 to
2026-06-10 is discrepancy*). None of the three is cited here to settle a question against
another. The operator's readings so far: the freeze is a statement about assets; "retires
now" is the campaign's to time; a doctrine is not a plan. The reconciliation is part of this
document's row-4 work and is not drafted ahead of the operator's direction.

---

# Part III — Procedures (DRAFT, re-based 2026-10-10)

"Procedures are model-generation-specific and expected to change" (June text). This part
does not write procedures beside canon's. It names the canonical ones and says where the
six phases and the positions sit in them.

## 1. The canonical procedures, as they stand

- `docs/governance/GovZero/obpi-pipeline-runbook.md`: the five stages (plan, implement,
  verify, present, sync) and the `gz-obpi-pipeline` skill that runs them.
- `docs/governance/GovZero/obpi-transaction-contract.md` and `obpi-runtime-contract.md`:
  what a work package's completion is a transaction over, and the runtime's anchor states
  (corrected 2026-10-10 to match the code).
- `docs/governance/GovZero/audit-protocol.md`: how a completed ADR is audited.
- `docs/governance/GovZero/charter.md`: the authority boundary.
- `docs/governance/GovZero/session-handoff-obligations.md`: what a session owes on leaving.

## 2. Phases, stages and positions (the statement of 2026-10-08, "a good start")

1. The six phases are the life of one work package, from the operator's intent to an
   assessed effect.
2. The five pipeline stages are the part of that life the pipeline runs: execution and
   assessment, then the operator's release, then recovery.
3. Everything before launch is the first four phases: the operator's intent, the target and
   its limits (the brief), the choice of means, and the operator's decision to task.
4. A stage is a span of the work with its witnesses. A position is an obligation and a role
   inside it, and one stage can hold several positions.
5. The stages and their witnesses stay as built. What changes is which crew fill the
   positions inside them. (The agent's choice, marked.)

| Phase (JP 3-60, 2018) | Canonical home today | Positions (the operator's eight roles) |
|---|---|---|
| 1. Objectives, guidance, intent | the engineering order and the brief's requirements | command (not a crew position) |
| 2. Target development | the brief: Allowed and denied paths | target planning |
| 3. Capabilities analysis | plan stage; `gz plan audit`; model tier by complexity | mission constraints; the runtime applies the weaponeering rule |
| 4. Commander's decision | the operator's initiation through `gz-obpi-pipeline` | command; the tasking order is the record to build |
| 5. Mission planning and execution | implement stage: lock, airlock in, implementer red then green, airlock out | mission planning, infiltration, ordnance delivery, exfiltration, decontamination |
| 6. Combat assessment | verify and present stages: receipts, spec and quality review, Step 4b, scope report; Gate 5 | BDA; the captain releases |

Open under item 14: where mission planning sits; how ordnance delivery and BDA divide; who
owns munitions effectiveness.

## 3. The tasking order

The June doctrine's captain's brief (worklist item 1: scope manifest, stop conditions,
expected artifacts, prohibitions on out-of-scope change), carrying also the reasoning (JP
3-60 phase 4). Ruled a ledger event on 2026-10-05; proposed after `ADR-0.35.0` briefs 15 and
18 land; not a new order but item 1 of `ADR-pool.command-doctrine-internalization`.

## 4. Assessment

By someone who did not do the work, from records, each finding with its source. The
publication's order: physical, functional, then the target's system. The scope report is the
system output, restored on completion receipts under GHI #1181 and refusing at `gz obpi
complete` when a changed file lies outside Allowed Paths (built 2026-10-10, held local). The
exempt list of gzkit's own records is the agent's draft and the operator's to correct.

## 5. Transfer of position responsibility

Four parts in order, from JO 7110.65BB Appendix A: preview the position; verbal briefing;
assumption of position responsibility; review the position. The checklist's content is the
facility's under JO 7210.3EE paragraph 2-2-4: tailored to the position, reviewed annually,
status information first, traffic last, and the briefing recorded. In gzkit the handoff
document is the briefing and `gz handoff decide` is the assumption; the preview from the
status displays is `gz status` and the orientation hook. "Watch" is in no text read.

## 6. Problem reports

Four states in order, recorded, classified, resolved, closed; resolved is not closed, which
needs "a formal review and confirmation of an effective resolution". Four classes, one per
report, the highest that could apply: significant, functional, process, life cycle data. An
open report may ship; an unmitigated significant one may not (FAA AC 00-71 § 3.1 and AC
20-189 § 4.1 and § 6, both read 2026-10-08, both "adapted from DO-178C/ED-12C"). gzkit's GHI
carries open and closed only.

## 7. Maintenance

A schedule of tasks, each applicable and effective (AC 121-22D), grouped into "integrated
scheduled work packages of your own design" (AC 120-16G § 6-1); each run a ledger event (ruled 2026-10-07, unbuilt); the maintenance planning
document is the reference beside the MRB report (EASA checklist). "Letter check" is operator
practice and is labelled so.

---

# Part IV — Practices, and what is still to be built

## What changes in gzkit

The doctrine implies a concrete worklist. Each item below names the article it implements.

**Briefing template (Articles 2, 4, 10).** Replace heavyweight in-prompt scaffolding with a captain's-brief structure: scope manifest, stop conditions, expected artifacts, explicit prohibitions on out-of-scope change. Brief and complete are compatible; the template enforces both. Everything removed from the prompt either moves into the harness or is retired by the Article 10 audit.

**Refusal and substitution handling (Article 5).** The harness branches explicitly on API-level refusals rather than treating any successful response as usable output. The attestation record gains a served-model field. A substitution policy file states acceptable fallbacks per gate class, and the gate runner enforces it.

**Scope-conformance report (Article 4).** A post-run check diffs delivered changes against the scope manifest and annunciates every unrequested artifact, backup, or tidy. The report is a gate precondition, not advice.

**Autonomy span parameter (Article 6).** A configured cap on change volume per attestation unit, with a documented re-decision procedure tied to model transitions. The cap appears in the attestation record so its observance is itself attestable. The cap's calibration can be empirical rather than intuitive: validated supervisory-control instruments measure the supervisor directly, with SAGAT estimating situation awareness and NASA TLX measuring mental workload, and Armstrong and Shah (2026) propose exactly this instrumentation for generative AI oversight roles. Measuring the attestor, not just the model, turns the doctrine's most judgment-dependent parameter into one that tracks observed review capacity.

**Proficiency log (Article 9).** Drift sessions get scheduled and recorded alongside the other governance artifacts, with the skill domains under maintenance named. The log makes skill retention auditable the same way the gates make work auditable.

**Coherence audit (Article 10).** A standing checklist run at each major model transition: trace every gzkit item to an article, benchmark every compensation item against the current release, record what was retired and what was retained at known cost. The audit record is the practice's own answer, in advance, to anyone arguing the apparatus is superstition.

*(RATIFIED, unchanged. Tracked in `ADR-pool.command-doctrine-internalization`.)*

**DRAFT additions**, each a proposal from the run (re-based 2026-10-10):

- **Tasking event** (policy 4): item 1 of `ADR-pool.command-doctrine-internalization`, a
  correction under its owning ADR, not a new order.
- **Crew split** (policies 5, 7): constraints, red and green as separate sorties, the rule
  for means checked by the runtime. Proposed, after briefs 15 to 20.
- **Scope report and refusal** (policy 9, Article 4): built as direct fixes under GHI #1181
  and GHI #1185 on 2026-10-10, held local for the operator's review.
- **An owner for munitions effectiveness** (policy 9): proposed, after item 14.
- **Integrity level** (policy 11): a second axis beside lane, conditional on lifting
  PROVISIONAL on the bands.
- **Maintenance record entry** (policy 13): one ledger event per chore run.
- **The governor as the last release** (policy 19): a release first, then the pinning of
  session-loaded surfaces, unsized.
- **Reach** (Article 10): the doctrine is named by nothing an agent loads each turn (row 2
  (d)); its worklist is named by no campaign edition.

## A note on the standing argument

The throughput position and this doctrine will keep colliding, and the collision is healthy when it is framed correctly. The throughput position answers "how much per token." The doctrine answers "who is in charge here, and who is liable." Both questions are real. Only one of them has an answer that survives a deposition. When a technique from the throughput world improves output per token without moving the signature, adopt it gratefully. When it improves output per token by moving the signature, the doctrine already says what happens, in twenty-three words it borrowed from Part 91.

*(RATIFIED, unchanged.)*

---

## Open questions for the operator

Each is yours. None is decided in this draft. Closed since the first draft: whether an agent
is crew (yes; Article 3's title to be amended); the operator's standing (commander and
captain, not crew); the governor (the last release, item 22); the statement of command.

1. **What the constitution is relative to this doctrine** (item 15). Your 2026-06-14 ruling
   makes a constitution the root; none was written; you ruled one file on 2026-10-08.
2. **Article 3's body**: does it gain the position and the role, or do policies beneath it
   carry them?
3. **Policy 14 has no article.** Trace it to one, or write an article for relief of position.
4. **Article 6's sizing** against the frame's two sizings of a run.
5. **Who owns munitions effectiveness**, and the other two seams of item 14.
6. **The two planning names** (operational planning for the whole, mission planning for the
   unit).
7. **Whether the military names enter the doctrine's text** or a glossary beside it.
8. **What a policy is** (lines 1 to 3 of the statement put 2026-10-09); whether changing an
   article differs from changing a policy; what "encourage" consists of.
9. **The policies nothing witnesses** (4, 5, 7, 15's slower beats, 16, 17, 18, 19): build the
   witness, or state them as advisory in their own text, no third state.

---

## Appendix A — Article-to-surface trace

Seed of the Article 10 coherence audit. Each row traces an article to the gzkit surfaces that implement it today; gaps are tracked in `ADR-pool.command-doctrine-internalization`. This table is the audit's working baseline and is re-walked at every major model transition.

| Article | Implementing gzkit surface | Status |
|---|---|---|
| 1 — Accountability is non-transferable | Universal OBPI attestation (ADR-0.0.36; `AGENTS.md` § Universal OBPI Attestation); canon-owner attestation directive (`AGENTS.md` § Attestation); Charter § Authority Boundary | Implemented |
| 2 — Authority must be instrumented, not asserted | Validator scopes (`gz validate`), pre-commit hooks, ARB middleware ([arb-middleware](../arb-middleware.md)), pipeline runtime; appraised in [harness-engineering-appraisal](../harness-engineering-appraisal.md) | Implemented — the operating thesis |
| 3 — The model is a crew resource, not a crew member | Personas (`.gzkit/personas/`); push-back rule (`AGENTS.md` § Behavior Rules — Always #10); subagent doctrine (Always #5, #6) | Largely implemented |
| 4 — Uncommanded change is an annunciation failure | OBPI brief Allowed Paths; `gz validate --brief-reconcile`; surgical-changes rule (`AGENTS.md` § DO IT RIGHT #11) | Partial — no post-run delivered-vs-commanded scope-conformance gate |
| 5 — Model identity is an attestable fact | (none — no served-model field in attestation or receipt schemas under `src/gzkit/schemas/`) | Gap |
| 6 — Autonomy span is set by attestation capacity | [OBPI Decomposition Matrix](obpi-decomposition-matrix.md) sizes by intrinsic complexity, not attestation capacity | Gap, with a named tension — the matrix must reconcile to this article |
| 7 — Evidence is artifacts, not narration | ARB receipts (`AGENTS.md` § Attestation canonical invocations); ledger Layer-2 truth ([state-doctrine](../state-doctrine.md), [trust-doctrine](../trust-doctrine.md)); `@covers` test discipline | Implemented — strongest alignment |
| 8 — Efficiency is a constraint, not the objective | Anti-vibing mantra (`AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT, operative claim 1: "lighter ceremony" is never the tradeoff axis) | Implemented |
| 9 — Proficiency is maintained deliberately | (none — no proficiency log, no scheduled drift sessions) | Gap |
| 10 — Procedures earn compliance through coherence | Advisory-rules scorecard ([advisory-rules-audit](../advisory-rules-audit.md); `gz validate --advisory-scorecard`); [model-regression taxonomy](../model-regression-taxonomy.md) F1–F10 | Partial — no trace-to-article column, no model-transition trigger |

*(RATIFIED, unchanged. It is the June baseline and has not been re-walked for this draft.)*

## References

Armstrong, B., & Shah, J. (2026). *Humans in the loop: The evolution of work in early experiments with generative AI*. MIT Industrial Performance Center. https://ipc.mit.edu/wp-content/uploads/2026/04/Humans_in_the_Loop_full_r01M.pdf

Degani, A., & Wiener, E. L. (1997). Procedures in complex systems: The airline cockpit. *IEEE Transactions on Systems, Man, and Cybernetics, Part A: Systems and Humans*, *27*(3), 302–312. https://doi.org/10.1109/3468.568739

Federal Aviation Administration. (2013). *Manual flight operations* (Safety Alert for Operators 13002). U.S. Department of Transportation.

Helmreich, R. L., Merritt, A. C., & Wilhelm, J. A. (1999). The evolution of crew resource management training in commercial aviation. *International Journal of Aviation Psychology*, *9*(1), 19–32. https://doi.org/10.1207/s15327108ijap0901_2

Responsibility and authority of the pilot in command, 14 C.F.R. § 91.3 (2026). https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-91/subpart-A/section-91.3

Salim, M., Latendresse, J., Khatoonabadi, S., & Shihab, E. (2026). *Tokenomics: Quantifying where tokens are used in agentic software engineering* (arXiv:2601.14470). arXiv. https://arxiv.org/abs/2601.14470

Sarter, N. B., & Woods, D. D. (1995). How in the world did we ever get into that mode? Mode error and awareness in supervisory control. *Human Factors*, *37*(1), 5–19. https://doi.org/10.1518/001872095779049516

**Added by this draft**, each read in the run and recorded under
`docs/rnd/renewing-vows/sources/`:

- Chairman of the Joint Chiefs of Staff. (2018). *Joint targeting* (Joint Publication 3-60).
- Chairman of the Joint Chiefs of Staff. (2019). *Joint air operations* (Joint Publication 3-30).
- Federal Aviation Administration. (2016). *Air carrier maintenance programs* (Advisory Circular 120-16G).
- Federal Aviation Administration. (2017). *Standard operating procedures and pilot monitoring duties for flight deck crewmembers* (Advisory Circular 120-71B).
- Federal Aviation Administration. (2022). *Management of open problem reports (OPRs)* (Advisory Circular 20-189).
- Federal Aviation Administration. (2022). *Best practices for management of open problem reports (OPRs)* (Advisory Circular 00-71).
- Federal Aviation Administration. (2024). *Maintenance review boards, maintenance type boards, and original equipment manufacturer/type certificate holder recommended maintenance procedures* (Advisory Circular 121-22D).
- Federal Aviation Administration. (2025, with changes through 2026). *Air traffic control* (Order JO 7110.65BB), Appendix A.
