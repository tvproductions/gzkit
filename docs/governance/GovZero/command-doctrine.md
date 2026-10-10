# GovZero command doctrine

*A back-port of the aircrew accountability framing into the philosophy layer of GovZero and gzkit*

Status: Canonical doctrine (philosophy layer). Part I of this file, the statement of command and the ten articles, is the constitution: the root (operator rulings 2026-06-14, 2026-10-08 and 2026-10-10, frontier item 15 of R&D run `renewing-vows`).
Ratified: 2026-06-10 (operator-ratified relocation from working draft). Amended 2026-10-10 by the operator's ratification of Part 0 of `docs/rnd/renewing-vows/doctrine-merge.md`, verbatim: "ratify Part 0"; the run record `docs/rnd/renewing-vows.md` carries each ruling the amendment rests on, with the operator's words.
Authority: Philosophy layer of the Four P's stack — policies, procedures, and practices trace upward to these articles (Article 10). The [GovZero Charter](charter.md) remains the sole authority for gate definitions; this doctrine is what those definitions trace to.
Companion: the Sprint and Drift essay "The left seat." The implementation worklist is carried by the campaign (`docs/governance/build-to-1.0-campaign-2026-09-20.md` § Amendments 2026-10-10) through `ADR-pool.command-doctrine-internalization`; doctrine sets no dates and carries no worklist (statement of command, line 5).

## Why this document exists

GovZero has always had procedures (the five gates) and practices (gzkit, the session discipline, the attestation records). What it has had only implicitly is the layer Degani and Wiener (1997) put first in their Four P's model of cockpit operations: an explicit operating philosophy from which policies derive, from which procedures derive, from which practices follow. Their field finding is the reason the gap matters. Procedures that no longer trace visibly to a philosophy are the procedures operators stop complying with, and the operator most likely to stop complying with GovZero under deadline pressure is me.

The gap has a second cost that is newly urgent. Each model release arrives with vendor guidance about what the model prefers, and without an explicit philosophy there is no principled way to decide which of those preferences to accommodate and which to refuse. The scaffolding audit becomes vibes. With the philosophy written down, the audit becomes mechanical: anything in the apparatus that exists to compensate for model weakness is negotiable and retires as models improve; anything that exists to implement the philosophy is not negotiable and survives every release. The aviation record supplies the philosophy almost ready-made, because aviation spent fifty years deciding what survives improvement in the automation. This document writes it down.

## The Four P's, applied

**Philosophy** is the command doctrine below: ten articles stating what GovZero believes about authority, accountability, and automation, independent of any model, vendor, or tool.

**Policies** are the standing decisions that implement the doctrine in this practice: the five gates exist; a human attests before work ships; autonomy span is bounded; evidence means artifacts.

**Procedures** are the gate definitions, the briefing template, the attestation record schema, the substitution rules. Procedures are model-generation-specific and expected to change.

**Practices** are what actually happens in gzkit sessions, including the drift between procedure as written and procedure as flown. The drift is data. When practice diverges from procedure persistently, either the procedure has stopped tracing to the philosophy and should be fixed, or the practice is a compliance failure and should be named as one. The Four P's give the diagnostic: trace the divergent item upward and see where the chain breaks.

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

## The command doctrine

### Article 1. Accountability is non-transferable

One human signs for the work. The signature does not move to the model, the harness, the vendor, or the gate that passed. This is the GovZero analogue of 14 C.F.R. § 91.3, and the welding matters as much as the assignment: direct responsibility and final authority are one clause, not two. Whoever holds the signature holds override authority over every other element of the pipeline, and whoever holds override authority holds the signature. Any proposal that separates them, in either direction, is rejected on its face.

### Article 2. Authority must be instrumented, not asserted

A captain's authority over a human crew rests on shared consequences and a common operating manual. The model shares neither. It follows that command over a model is exactly as real as the harness that enforces it, and no more. Authority asserted in the context window is a briefing: necessary, and unenforceable. Authority implemented in the harness, in CI rules, file checks, diff gates, and halt conditions, is the only kind the model actually answers to. Every article below that imposes an obligation on the model is therefore really an obligation on the harness. If the harness does not enforce it, the doctrine does not contain it.

### Article 3. The model is crew, never in command

Crew resource management never promoted the first officer to command; it obligated the whole crew to keep the commander informed and made silence a violation (Helmreich et al., 1999). The same allocation applies here, in both directions. The model is used fully: it drafts, flags, surfaces, challenges, and proposes, and a practice that underuses a capable model is leaving crew resources idle, which CRM treats as a failure. And the model decides nothing that ships. Its challenges are inputs to judgment, never substitutes for it. Designing the harness so the model can effectively surface concern is part of the doctrine; treating surfaced concern as approval is a violation of it. An agent is crew: it fills a position, an obligation with a role to fulfil it, within the role's bounds and under its auspices. (Title and this sentence amended 2026-10-10; the article's allocation is unchanged.)

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

Every gate, check, and template in gzkit must trace upward through a policy to an article of this doctrine. Anything that cannot be traced is either workaround scaffolding for a past model generation, which retires on its own schedule, or accumulated ritual, which is retired when the campaign times it (amended 2026-10-10: doctrine sets no dates). This is Degani and Wiener's finding turned into a maintenance rule: incoherent procedure is what breeds noncompliance, so coherence is audited, not assumed. The audit is a task of the maintenance visit, due on the signal of a major model transition (the rhythm, below), and its two questions are fixed. Does this item implement the doctrine? Then it stays, whatever the vendor guidance prefers, and any output-quality cost is paid knowingly and measured. Does it compensate for a model weakness? Then it is benchmarked against the current release and retired the day it stops earning its place. The cure for procedural drift is not fewer procedures. It is procedures that visibly mean something.

## What changes in gzkit

The doctrine implied a worklist here from 2026-06-10 to 2026-10-10. By line 5 of the statement of command, doctrine sets no dates and carries no worklist, so the six items are carried by the campaign (§ Amendments 2026-10-10) through `ADR-pool.command-doctrine-internalization`, each keeping the article it implements: the briefing template (Articles 2, 4, 10); refusal and substitution handling (Article 5); the scope-conformance report (Article 4; restored on completion receipts under GHI #1181, 2026-10-09); the autonomy span parameter (Article 6); the proficiency log (Article 9); the coherence audit (Article 10, now a task of the maintenance visit). The item texts of 2026-06-10 are in the file's history at commit `251df874e` and in the pool ADR.

## The reconciliation of June (ratified 2026-10-10)

Three acts of 2026-06-09 and 2026-06-10 disagree in seven places and were never reconciled
(run record, decision *the work of 2026-06-08 to 2026-06-10 is discrepancy*). The operator
has ruled three readings: the freeze is a statement about assets; a doctrine is not a plan,
so the campaign did not subsume the doctrine; "retires now" is the campaign's to time. Each
pair below is settled by one of the seven lines or by one of those readings, or was marked
as the agent's proposal; the four proposals so marked were ratified with this Part on 2026-10-10.

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

## The rhythm (ratified 2026-10-10)

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

## The glossary

The names this doctrine uses for gzkit's surfaces (commander, captain, crew, position, role, force, campaign, order, release, and the registers beneath them) are ratified in `docs/rnd/renewing-vows/doctrine-merge.md` Part 0 and are held there until the glossary's home is named by the DDD-discipline R&D run. The statement of command and the terms above are the part of that glossary this file carries.

## A note on the standing argument

The throughput position and this doctrine will keep colliding, and the collision is healthy when it is framed correctly. The throughput position answers "how much per token." The doctrine answers "who is in charge here, and who is liable." Both questions are real. Only one of them has an answer that survives a deposition. When a technique from the throughput world improves output per token without moving the signature, adopt it gratefully. When it improves output per token by moving the signature, the doctrine already says what happens, in twenty-three words it borrowed from Part 91.

## Appendix A — Article-to-surface trace

Seed of the Article 10 coherence audit. Each row traces an article to the gzkit surfaces that implement it today; gaps are tracked in `ADR-pool.command-doctrine-internalization`. This table is the audit's working baseline and is re-walked by the maintenance visit due on a major model transition. Article 3's row reads its former title; the table is the June baseline and was not re-walked on 2026-10-10.

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

## References

Armstrong, B., & Shah, J. (2026). *Humans in the loop: The evolution of work in early experiments with generative AI*. MIT Industrial Performance Center. https://ipc.mit.edu/wp-content/uploads/2026/04/Humans_in_the_Loop_full_r01M.pdf

Degani, A., & Wiener, E. L. (1997). Procedures in complex systems: The airline cockpit. *IEEE Transactions on Systems, Man, and Cybernetics, Part A: Systems and Humans*, *27*(3), 302–312. https://doi.org/10.1109/3468.568739

Federal Aviation Administration. (2013). *Manual flight operations* (Safety Alert for Operators 13002). U.S. Department of Transportation.

Helmreich, R. L., Merritt, A. C., & Wilhelm, J. A. (1999). The evolution of crew resource management training in commercial aviation. *International Journal of Aviation Psychology*, *9*(1), 19–32. https://doi.org/10.1207/s15327108ijap0901_2

Responsibility and authority of the pilot in command, 14 C.F.R. § 91.3 (2026). https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-91/subpart-A/section-91.3

Salim, M., Latendresse, J., Khatoonabadi, S., & Shihab, E. (2026). *Tokenomics: Quantifying where tokens are used in agentic software engineering* (arXiv:2601.14470). arXiv. https://arxiv.org/abs/2601.14470

Sarter, N. B., & Woods, D. D. (1995). How in the world did we ever get into that mode? Mode error and awareness in supervisory control. *Human Factors*, *37*(1), 5–19. https://doi.org/10.1518/001872095779049516
