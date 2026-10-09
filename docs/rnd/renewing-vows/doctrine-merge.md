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

> **Note, 2026-10-08, after `docs/governance/GovZero/` was read in full.** Parts II and III
> were drafted before that read and need re-basing before you draw on them. Part III writes
> procedures beside canonical ones it does not name: the five-stage pipeline runbook, the
> OBPI transaction contract, the audit protocol and the charter. Part II's "Enforced today
> by" column does by hand what `docs/governance/advisory-rules-audit.md` already does with a
> cited witness per row. Policy 9's "System and collateral: **nothing**" is wrong: completed
> receipts carried a scope audit until 2026-06-19. Part I and the RATIFIED parts are
> unaffected. Detail: run record, source entry *gzkit's own doctrine layer*.

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

# Part II — Policies (DRAFT)

The June text names four policies in a sentence: "the five gates exist; a human attests
before work ships; autonomy span is bounded; evidence means artifacts." This part states
them, and the others that your rulings and canon already hold, one to a row.

**Who is bound.** Policies 1, 16 and 17 bind you. The rest bind the agents, which under
Article 2 means they bind the harness.

| # | Policy | Traces to | Where it comes from | Enforced today by |
|---|---|---|---|---|
| 1 | **One human commands and signs.** Only the operator initiates a work package, and only the operator attests that it is complete. | Art. 1 | Canon: `AGENTS.md` § OBPI Acceptance Protocol and § Gate Covenant (ADR-0.0.36). | Attestation: `gz obpi complete` refuses without it. Initiation: **nothing**; prose only. |
| 2 | **Control is centralized and execution is delegated.** One session plans and tasks, and is told of every change. Small, focused agents do the work. | Art. 2, 3 | You, 2026-10-05: "a series of much smaller, and much more focused agents, being orchestrated". JP 3-30 (2019) ch. I § 3. | Partly. A dispatch is recorded; its outcome and the run's position are not (ADR-0.35.0 briefs 15 to 18, unbuilt). |
| 3 | **An agent is a crew resource.** It drafts, flags, challenges and proposes. It decides nothing that ships. | Art. 3 | The article itself. | Gate 5. |
| 4 | **Every run is commanded in writing before it starts.** A tasking order states scope, constraints, stop conditions, expected artifacts and the reasoning. | Art. 2, 4 | June worklist: the captain's brief. You, 2026-10-05: the tasking order is a ledger event. JP 3-60 (2018) phase 4. | **Nothing.** A brief's allowed paths and a plan receipt exist; no tasking record does. Not yet binding. |
| 5 | **Constraints are worked out before execution and travel in the order.** | Art. 2, 4 | You, 2026-10-05 (the constraints sortie is "a Design act") and 2026-10-08. JP 3-30: special instructions "located in the air tasking order". | **Nothing.** Not yet binding. |
| 6 | **What is protected and what is restricted is declared.** A protected surface is not touched; a restricted one is touched only within its stated limits. | Art. 4 | Canon: a brief's allowed and denied paths. JP 3-60 (2018): the no-strike list and the restricted target. | Partly: `gz validate --brief-reconcile`. `consequence-bands.md` (2026-09-22) records that the path hook continues past a path outside the allowlist. |
| 7 | **The means are fixed by rule, never by the planner.** The kind of requirement fixes which sorties fly. Green and assessment are never waived. | Art. 2, 8 | You, 2026-10-05 ("A with evidence-cited subtraction and free addition"). JP 3-60 (2018): weaponeering. | **Nothing.** Not yet binding. |
| 8 | **Whoever does the work does not assess it.** | Art. 3, 7 | Canon: implementer, spec reviewer, quality reviewer; Step 4b by another vendor's model. 14 CFR § 121.369(b)(7), as AC 120-16G § 7-1c states it. | Partly: Step 4b is required before Gate 5 on a work package. Nothing checks who reviewed. |
| 9 | **Assessment is specified before execution and has five outputs.** Did it hit; does it work; what did it do to the system around it; did the means perform as estimated; is another pass needed. | Art. 4, 7 | JP 3-60 (2018) phase 6 and Appendix D. You, 2026-10-05: chase and damage assessment are two roles. | Hit: ARB receipts. Works: the requirement-coverage gate and Step 4b. System and collateral: **nothing** (Article 4's scope-conformance report, "Partial"). Means: **nothing**. |
| 10 | **Evidence is an artifact, with its source and its confidence. A crew's own report is an input.** | Art. 7 | Canon: "A subagent's claim is not evidence." JP 3-60 (2018) Appendix D. | ARB receipts; the ledger. Confidence is not recorded. |
| 11 | **Rigour scales on two independent axes.** Lane: does an external contract change. Integrity level: how silently and how irrecoverably the surface fails. | Art. 6, 8 | You, 2026-09-23 and 2026-09-25 (lane); 2026-09-22 (the bands); 2026-10-07 (the axis and its name). IEEE 1012-2024 clause 5. | Lane: a required field. Integrity level: **nothing**, and its scores are PROVISIONAL. |
| 12 | **A defect is a problem report: recorded, classified, resolved, closed.** Resolved is not closed. One left open at a release is assessed and reported. | Art. 7, 10 | Canon: the GHI, `ghi-triage`, `ghi-close`. FAA AC 20-189 and AC 00-71. | By skill, not by harness. The four states and classes are not gzkit's today. |
| 13 | **Maintenance is scheduled or unscheduled.** A scheduled task must be applicable and effective, and each run of one is recorded on the ledger. | Art. 10 | Your chore design, ratified 2026-09-12; you, 2026-10-07. FAA AC 121-22D and AC 120-16G. | `gz chores status` announces. The run record is a line in a Markdown log; the ledger event is unbuilt. |
| 14 | **A transfer of responsibility is briefed, and a briefing gates nothing.** Preview, briefing, assumption, review. | *no article; see Open questions* | You, 2026-08-17. FAA JO 7110.65BB Appendix A. | The handoff system; `gz handoff decide`. |
| 15 | **The rhythm.** Each session: how we work, what we are working on, what we were doing last, the transit, the marker on leaving. Two slower beats, a plan republish and a maintenance visit, come due on a signal and never on a calendar. Neither gates. | Art. 9, 10 | You, 2026-07-18 and 2026-10-07. | The session beat: hooks and orientation. The two slower beats: **nothing**. |
| 16 | **The span of a run is capped by what one attestation can honestly cover.** | Art. 6 | The article and the June worklist. | **Nothing.** The doctrine's own appendix: "Gap". Not yet binding. |
| 17 | **Unassisted work is scheduled and logged.** | Art. 9 | The article and the June worklist. | **Nothing.** "Gap". Not yet binding. |
| 18 | **The model that did the work is recorded, and a model and an effort are assigned by role.** | Art. 5, 8 | The article. You, 2026-10-05 ("so model + effort"). | **Nothing.** "Gap"; and effort can be set only on an agent's definition. Not yet binding. |

**The count.** Of eighteen policies, two are enforced in full (3 and 14), nine in part,
and seven by nothing in the harness (4, 5, 7, 12, 16, 17, 18). By Article 2 those seven are
not yet in the doctrine. That is the honest measure
of how far gzkit can hold anyone to account today.

Not policy, and left where it lives: the order of work and the IOC waypoint belong to the
campaign plan, which "rules sequencing".

---

# Part III — Procedures (DRAFT)

The June text: "Procedures are model-generation-specific and expected to change." This part
is the one most likely to be revised.

## 1. How one work package is flown

You ruled the shape on 2026-10-08: the six phases are the process and your eight roles are
the crew. The phases are those of the joint targeting cycle (JP 3-60, 28 September 2018),
which the publication calls "a six-phase iterative process that is not time-constrained nor
rigidly sequential". The staffing is a draft.

| Phase | Who | What they hand on | Policy |
|---|---|---|---|
| 1. Commander's objectives, guidance and intent | you, and the author of the order | intent, requirements, the measures of success | 1, 9 |
| 2. Target development | **target planning** | what is to change; what is protected; what is restricted | 6 |
| 3. Capabilities analysis | **mission constraints**; the runtime applies the rule for means | contracts (interfaces, invariants, stubs); the collateral estimate; the sortie set | 5, 7 |
| 4. Commander's decision | you initiate | the tasking order | 1, 4 |
| 5. Mission planning and execution | **mission planning**, **infiltration**, **ordnance delivery**, **exfiltration**, **decontamination** | the unit's plan; entry accounted; red then green; exit accounted; what the transit disturbed, cleaned and reported | 2, 3 |
| 6. Combat assessment | **BDA** | the five outputs of policy 9 | 8, 9, 10 |

Three of the eight roles (infiltration, exfiltration, decontamination) are the airlock's and
are gzkit's own words. No text read carries them.

## 2. The tasking order

It is the June doctrine's captain's brief: "scope manifest, stop conditions, expected
artifacts, explicit prohibitions on out-of-scope change". From JP 3-60 it also carries the
reasoning, because "The work of unit mission planners is significantly enhanced when they
are furnished with detailed insights into the reasoning that resulted in their unit
tasking."

## 3. Assessment

Made after the work, by someone who did not do it, from several sources, each finding with
its confidence. The publication's order: physical, then functional, then the system the
target belongs to. A confirmed miss may be re-flown at once; other judgments wait for the
fuller picture.

## 4. Transfer of responsibility

Four parts in order, from FAA JO 7110.65BB Appendix A: preview the position; verbal
briefing; assumption of position responsibility; review the position. The one arriving
previews alone, first, from the status displays. The one leaving stays to check for "known
omissions, updates, or inaccuracies".

## 5. Problem reports

Four states: recorded, classified, resolved, closed. Four classes, one to a report, the
highest that could apply: significant, functional, process, life cycle data (FAA AC 20-189).

## 6. Maintenance

A schedule of tasks, each with what, how and when. Tasks may be grouped into scheduled work
packages. "More maintenance is not always a good idea" (FAA AC 120-16G § 6-3b): adding a
task needs the same justification as any other change.

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

**DRAFT additions**, each a proposal from the run and none started:

- **Tasking event** (policy 4). The ledger record of what was commanded.
- **Crew split** (policies 5, 7). Constraints, red and green as separate sorties, with the
  rule for means checked by the runtime.
- **Combat assessment** (policy 9). An owner for the two outputs nothing produces. One of
  them is the June worklist's scope-conformance report.
- **Integrity level** (policy 11). A second axis beside lane, conditional on you lifting
  PROVISIONAL on the bands.
- **Maintenance record entry** (policy 13). One ledger event per chore run.
- **Reach** (Article 10). The doctrine is named by nothing an agent loads each turn; the
  line that carried it into `AGENTS.md` was dropped (compression sweep 2026-09-24, row S31).

## A note on the standing argument

The throughput position and this doctrine will keep colliding, and the collision is healthy when it is framed correctly. The throughput position answers "how much per token." The doctrine answers "who is in charge here, and who is liable." Both questions are real. Only one of them has an answer that survives a deposition. When a technique from the throughput world improves output per token without moving the signature, adopt it gratefully. When it improves output per token by moving the signature, the doctrine already says what happens, in twenty-three words it borrowed from Part 91.

*(RATIFIED, unchanged.)*

---

## Open questions for the operator

Each is yours. None is decided in this draft.

1. **Is this document the constitution?** Your 2026-06-14 ruling makes a constitution the
   root; none was ever written. You ruled one file on 2026-10-08.
2. **Article 3 and the role names.** The article says the model is not a crew member. The
   run's name table called the implementer the "pilot flying". This draft uses your eight
   role names and calls no agent a pilot. Is that right?
3. **Policy 14 has no article.** Nothing in the ten speaks to handing work from one session
   to the next. Trace it to an existing article, or write an eleventh?
4. **The seven policies nothing enforces.** For each: build the enforcement, or strike it.
5. **Who owns the two assessment outputs nothing produces?**
6. **Two kinds of planning.** The texts call the plan for the whole "operational planning"
   and the unit's own "mission planning". Do those names stand?
7. **Do the military names enter the doctrine's text**, or sit in a glossary beside it?
8. **Are the three policies that bind you (1, 16, 17) stated the way you want to be held?**

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
