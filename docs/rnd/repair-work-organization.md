# R&D run — repair-work-organization

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-11-02T09:20Z.

**Challenge.** Operator g0, 2026-11-02, verbatim, in order, while RO-12's open point 2 was being
put:

> why would we treat repairs like work orders in a work package? we are also mixing and matching
> language - are these work packages? work orders? repair packages? repair orders?

> unless there is value in hierarchy? work package: bound container for a set of related work
> orders. work order: a set a goal-oriented tasks meant to achieve a defined outcome. task: a
> measurable/observable action that can be recorded and associated as outcome evidence. If there
> is value in that, then we can pursue it (what is old is new again, we used this language in
> summer 2025). If there is organizational value in this strata, then should discuss that.
> Otherwise, we'll want to drift. Order is attractive by its very name and concept - an order is
> an imperative and license to take the prescribed steps towards the outcome and an obligation to
> commit to the measure and assurance of those outcomes. Not too different than OBPI's REQ/TASK.
> The Work Order could bind/associate this REQ/TASK pairing.

> However, Repairs are sometimes more ad hoc and exploratory whereas we assume a Work Package and
> Work Order are proceeding according to the Feature Package's intent. However, this
> "normalization" around these concepts gives us the flexibility we needed.

> So, my point is that these may not all be sloppy synonyms, but rather "hidden" patterns or
> natural affinities in the language I am trying to fit to the work.

> that language is in AirlineOps...

> first, the drydock has vibed and improvised structure that was likely made up by the agent during
> a turn.

> feature packages group REQs. Work packages organize task responses to these feature pack. A work
> order is where we purposefully match REQ to TASK. A task has measured outcomes that allow for
> observability that leads to REQ fulfillment. A repair order has TASKs as well, but the outcomes
> are simply a part of the intent of the repair and not Feature/REQ bundle. However, your reasoning
> in the table suggests: Repair Packages - overall intent (responses to broader issues and needs -
> why are we doing these repairs (not the same as chores). Then a repair order provides task
> ordering to meet the needs/reasons for being in the mx/drydock. thus, the tasks (card language is
> superfluous but perhaps useful for measurement/tracking) become the unit of action, outcome, and
> measurement.

> I think this is where we have arrived in the evolution of this work.

> If we are not formal about this, we end up with your table; or worse, carrying OBPI around for
> over a year when it was a response to issues crafted in a session much like this one and then
> persisted far longer that warranted.

> We can rnd this, yes, but I think I have presented the structure. If rnd would be useful to
> formalize it, then let's. Relationship to feature pack and release pack is a welcome discussion.
> I am not trying to change anything about the catalog | feature | work | release arrangements
> we've already agreed to, but the "vibed" work organization of repairs|mx|drydock indicates that
> if I don't do this, the model will "vibe code" any arbitrary organizational structure and then,
> eventually, even drift from that.

The table the operator names, the agent's own, from the same exchange:

| Your level | Delivery today | Drydock in practice |
|---|---|---|
| Work package: bound container | Feature package, which holds a story but no labor | Repair order, such as RO-14 |
| Work order: goal-oriented tasks for a defined outcome | Work package | Tranche, such as RO-14 tranche 1 |
| Task: recorded, observable action | Task card: one commit, one trailer | Act |

---

## source · the terms as ruled today

Read 2026-11-02. `docs/governance/ieee/requirements-model.md` § The records:

> | Work package | 1, with its events in 2 | sequential, `WP-<NN>-<slug>` | One dated attempt to deliver one outcome: the frozen REQ baseline, the closing test, the task cards; the OBPI's successor, matching TASKs to REQs (ruled 2026-10-30) | how one outcome is delivered |

> | Task card | 1, with its events in 2 | `TASK-…` | One slice sized to an agent's context: one commit, one trailer, the REQ ids it drives | the increment |

> | Feature package | 1 | to be named when its store lands | A list of outcomes already in the catalog, each in at most one feature package, plus the story of why they belong together and the value they bring together; no version, release or order; its value delivered attested by a human at the release or work package attestation (ruled 2026-10-30, [the four-records R&D](../../rnd/four-records.md)); the successor to the mADR | why these outcomes belong together |

`docs/governance/harbor-ro5-work-packages.md`, ruling 1:

> **A repair order is a work package** (selection *"A"*): one work-package record with `kind: delivery | repair`. A delivery package names its outcome; a repair package names its GitHub issues in the outcome's place. One set of verbs, one freeze-and-close lifecycle.

Ruling 6: *"the drydock's `RO-n` names stay as aliases resolved through RO-2's identity seam."*

`docs/governance/safe-mode-doctrine.md` § Maintenance mode:

> A repair order is the maintenance mirror of the work package: one bounded repair with a scope, a witness and an owner, recorded to the ledger, and held as a repair work package (`kind: repair`) naming one or more GitHub issues under the repair tagging scheme (RO-5 rulings 1 and 2, 2026-10-25). [...] The term "work order" is retired (2026-10-16) and the repair order mirrors the work package directly (ruled 2026-10-17, R1).

`docs/rnd/renewing-vows/doctrine-merge.md` Part 0 § Terms:

> **Order.** How command reaches the work: a standing order binds every position; a tasking order binds one work package and carries the role's auspices.

> the term "work order" was retired on 2026-10-16 (verbatim: 'retire it, work package everywhere')

The contract's § The general arrangement, the Release Package row: *"the cart for one order, carrying the version: feature packages whole or in part, loose outcomes and repair packages, and whatever the release needs"*.

## source · AirlineOps, August 2025

`../airlineops` at commit `44049daf5` (2025-08-25), `docs/di/DI-027-di-revision-taxonomy.md`, read 2026-11-02:

> We need a unified umbrella concept "Work Order (WO)" to answer the governance question: *to what end is this change performed, and how does it support approved architecture (ADR) or user value (Feature)?*

> | FEAT (Feature Epic) | Cross-cutting user/business capability container for ACs, spawns child WOs | Minimal (WO_STARTED, optional updates) | ADR(s) |

> | REFACTOR | Internal structural change preserving external contracts | TESTS_PASSED, DOCS_UPDATED, invariants list | ADR(s) (architecture consistency) |

> | SPIKE | Exploratory investigation producing decision artifact or abandonment note | WO_STARTED + FINDINGS (future) + WO_COMPLETED | ADR(s) (investigation scope) |

At the same commit, `governance/README.md`: *"Guarantee every change traces to an ADR (architecture alignment) and/or Feature (user value) and is executed via a bounded Work Order (WO) with an explicit Checklist sized to its subtype."* At `57a3546c0` (2025-08-30), `src/airlineops/governance/wo_model.py`: a `WorkOrder` with `wo_id`, `type`, `status`, `adr_refs`, `checklist[]`; *"Cannot complete WO with unchecked checklist items"*. The tree search finds *work package* in only two AirlineOps Markdown files, neither a definition, and these two were not read. OBPI first appears in its commit messages on 2025-10-04.

**What it shows.** AirlineOps held a work order with a purpose and a checklist, and a feature container that spawned work orders. It held no *work package* stratum in what was read. The work order carried a type, so exploratory work (SPIKE) and repair-like work (REFACTOR, AMEND) were subtypes of one record. It had no REQ-to-TASK pairing: checklist items are text.

## source · where the drydock's structure came from

Measured 2026-11-02.

- *Act* enters the contract at `8984ba022` (2026-10-16), the pilotage chart, agent-drafted. No ruling defines it.
- *Tranche* enters the contract at `e89b30089` (2026-10-18), specifying RO-2. Its one ruling is a selection on one order's shape: *"One RO, tranches (Rec.)"*.
- `safe-mode-doctrine.md` item 5: *"One commit per act with its `Task:` trailer naming the repair order."* Git, since 2026-10-31: `TASK-ro14-wp-airlock-#1185`, `-wp-fence-#1206`, `-wp-acceptance-#1028` and `-wp-run-bound-#1200` carry three commits each, and 40 of the commits carry no `Task:` trailer. The one-commit rule does not describe the practice.
- `data/catalog/work_packages.json` is the store; RO-14's specification measures one record, RO-9's. Seventeen `RO-n` rows stand in the contract. Fifteen orders are not held as packages, so *"held as a repair work package"* is not yet true of them.

Bears on the challenge: the operator's *"likely made up by the agent during a turn"* holds for both words. Neither has a definition, a record or a witness.

## decision · the operator has presented the structure; the run formalizes it

Operator: *"I think I have presented the structure"*; *"I am not trying to change anything about the catalog | feature | work | release arrangements we've already agreed to"*. The run takes the structure as the input, tests it against the sources, and does not re-derive it. RO-12's open points wait on it (ruling 1 stands at either level).

Noted for the frontier, not decided: the operator's delivery wording places REQ-to-TASK matching in a *work order*, where the requirements model ruled it to the work package on 2026-10-30, and the operator rules out changing that arrangement. The two statements need reconciling.

## decision · the repair strata: the repair package at RO level, the repair order at tranche level, the task at act level

Ruled. Question: at which level does each repair term sit? Both sides were read in full (the sources above). Options put: **A** repair package is what RO-14 is today, the reason and scope; repair order is what a tranche is today, an ordered set of tasks toward that reason; task is what an act is today; the existing `kind: repair` record stays the repair package and the release rule stays true; cost, `RO-n` becomes a misnomer and *tranche* and *act* retire. **B** repair package is the whole visit, repair order is RO-14, task is the act, tranche dropped; cost, a release would carry a whole drydock, and a one-squawk hangar visit has no contract to sit under. **C** something else. Recommended A. Operator selected **"Package at RO level (Recommended)"**.

This corrects the sentence in RO-5 ruling 1, *"A repair order is a work package"*: the record that ruling built is the repair package.

**commissions:** 4 — the terms in the doctrine, the contract and RO-5's specification, on the operator's go on that row; the words and any rename wait on the later questions.

## source · the operator: the inputs differ, the execution does not

Question 2 was put (what *work order* means on the delivery side). Operator, 2026-11-02, verbatim, before choosing:

> it is clear we need symmetry: work/reapi package: broader strategic purposing for either construction planning or repair/remodel/refactoring; with "work" it doesn't yet exist, with repair it does. However, this may be flawed... work is work regardless of build or repair. we are uncovering a more importaant question: what drives req <-> work pairing? new construction/fabrication or repair/remodel/refactoring? features are implementation of design, repair/remodel/refactoring are responses to realized design after construction and/or use. there is higher philosophy here. the inputs are different, but execuation patterns are not:

> req/task pairing are the same whether we build or repair - new construction or repair/remodel/refactoring. the moves become more similar than not downstream.

> discuss.

(*"reapi"* is kept as typed; read as *repair*.)

## decision · the agent's reading, put for discussion and not ruled

Read against what canon holds, each cited above or in `docs/rnd/contractor-kit.md`:

- The REQ is where the two inputs meet. Construction reaches a REQ from design. Repair reaches one from a realized condition. Today a repair package has no REQ: RO-14 act 5 gives it *"one obligation per carried issue"*, and the list of discrepancies records that a docs or chore issue therefore has no honest proof. That limit is what the missing REQ costs.
- The agent proposes that the input sets the REQ's relationship to the work, and nothing downstream of it: construction states a **new** REQ; repair answers an **existing** REQ the realized system does not meet; remodel **changes** a REQ; refactor **preserves** one (AirlineOps's REFACTOR: *"invariants list"*). The correction-versus-enhancement doctrine is this test already: *"does the shipped surface fulfill its original declared intent?"*
- Exploratory repair fits as an earlier step, not another shape. The ruled documentation-first rule (*"an act's change cannot land until its encounter record exists as data"*) makes the encounter record repair's counterpart of design: the finding that yields the REQ. A freeze then falls on the order, once its REQ is known.
- `kind` on the record may be the input and not a kind of work, which would make RO-5's one record and one set of verbs right at the level it built them. The texts lean the same way: TUM App B's repair activity is *"involved in the construction, testing, repair, overhaul, refueling, or maintenance of the ship"*, one actor under one tag-out; decision B9 holds alteration and departure *"for repair and delivery packages alike"*.
- Symmetry at the top has a tension. A delivery work package delivers one outcome and is not strategic; the feature package holds the why. The parallel may be feature package to repair package, and work package to repair order, which is not what question 1's *"stays the repair package"* implies for the record.

## source · the operator: one requirement, and four levels on both sides

Operator, 2026-11-02, verbatim (dictated):

> Do we really think we can match every repair back to original requirement? I'm not arguing it. I'm just sort of suggesting that you're saying all requirements were originally about design. I'm speaking to your table, which I think is strong. But a repair has its own type of requirement. And do we really want to create two concepts of requirement when they're both going in and modifying the structure of the artifact? One of them, presumably in new construction, new fabrication. Although sometimes you have to rearrange and refactor to do that new construction as well. So that's a type of remodel. But we're trying to realize new features, right? That's what drives the product forward. But we also have a repair requirement. And I could see how the repair requirement can align to an original requirement of design. But I think that there's more similarity to the requirement across build and repair. And I think that's the conundrum. I do like the input requirements relationship table, though. That's very strong. Now, in where you see the flaw of the other table where you have the Y and feature package and Y and repair package, but clearly I'm making the argument that we have a layer in between that allows for grouping of sort of task matching, requirements to task matching down at something called a repair package. So I guess the problem is you're equating feature package and repair package, and I was, I guess, making a different argument. So I had seen a relationship from a feature package, which is just a way to put requirements together, but then a work package is a broader opportunity to have different groupings of requirements as are going to be put to tasks, so that I am then having a work order that actually then marries them. So in construction, I see four levels. You're making the case that in repair, there's three levels. But I guess the feature package equivalent in repair would be, you know, why we're in the hangar, why we're in dry dock, right? Is it from aviation an A, B, C, or D level check? Or is it, you know, an ad hoc or, I don't want to say catastrophic, but incidental reason for being in the hangar. So I suppose that's what would press down on the repair column in terms of shifting everything down by one. I still see a package, comma, order, comma, task type of arrangement. Anyway, I'm kind of meandering. Let's refocus.

(*"the Y"* is read as *the why*, the agent's row label.)

## decision · the agent's reading corrected on two points

Both from the operator's words above. The earlier reading's row *"answers an existing REQ"* assumed every requirement began in design; a repair has a requirement of its own, which may align to a design requirement and need not. And its *why* row equated the feature package with the repair package, three levels against the operator's four. The proposal to move the `kind: repair` record to the order level is withdrawn: question 1's ruling stands, and the repair column shifts down by one under a level above it.

Hypotheses for the operator, not ruled:

- One requirement concept. The `Req` model (`src/gzkit/models/catalog.py`, read 2026-11-02) has no field naming another REQ: `derives_from` holds *"PRD FR ids or section 7 attributes"*, and `member_of` requires an outcome. So one concept across build and repair needs a home for a repair REQ with no outcome, and a way to name a design REQ when it aligns.
- The level above the repair package is already in canon. `safe-mode-doctrine.md` § Maintenance mode, line 15, read in full 2026-11-02: *"It has three kinds. The scheduled checks are the aeronautical A, B, C and D program: the chores on their cadences and the hangar visits taken on cadence"*; *"The squawk is the on-demand repair of one reported discrepancy"*; *"The drydock is the third kind: on-demand and drastic"*.
- Four levels fit the ruled *one outcome* rule: a work package's REQs are one outcome's, and the work order sits inside it.

## decision · four levels on both sides: package, order, task beneath a why

Ruled. Question: is this four-level table the structure, with *package, order, task* running the same on both sides? Recommended yes. Operator: *"yes, that's the structure"*.

| Level | Construction | Repair |
|---|---|---|
| Why | Feature package: requirements put together | The reason for the visit |
| Grouping | Work package | Repair package |
| Marriage of REQ to task | Work order | Repair order |
| Action | Task | Task |

The word *work order* returns at this level, reversing its retirement of 2026-10-16 on the operator's structure. Whether a work package may group more than one outcome's requirements stays to be read: the ruled rule is one outcome, and the operator rules out changing that arrangement.

**commissions:** 4 — the structure in the doctrine, the requirements model, the contract and RO-5's and RO-12's specifications, on the operator's go on that row.

## source · the operator: the out-of-service package, and the gate against the hangar

Operator, 2026-11-02, verbatim (dictated), in the same message:

> And since we're struggling to have the equivalent of a feature package, and this is a provisional suggestion, but we could call it an out-of-service package on that right column as well, because regardless, that's what's happening, right? We're taking the vessel, whether it be an aircraft or a ship, out of service for a time, right? So sometimes, I think this also makes it clear sometimes what these GHIs are. The GHIs don't necessarily take the vessel into the hangar, right? Sometimes these checks can be done at the gate or while parked on the apron, right? So taking the aircraft to the hangar is definitely taking it out of service. And, you know, there are different ways to see that, but I think the metaphor is pretty strong. So it's a mouthful. I don't know if we'll do it hyphen separated or do it as a acronym, but I think that's the parity at the top row.

**The term against the texts, read 2026-11-02.** A text search of the aviation, TUM, JFMM and MEL sources finds no *out of service*, *line maintenance* or *heavy maintenance*. That is a search and not a read, so the absence is unproven. What stands: *return to service* is ruled (Part 0: *"Gate 5 attestation, which is return to service"*), so *out of service* is its natural pair. The Navy's working word is *availability*, which Volume V uses and never defines, read and not taken at C13. *Out-of-service package* is held as the operator's own term, provisional.

## decision · out of service means the MX marker is open; gate work stays below the package levels

Ruled. Question: does *out of service* mean exactly while the MX marker is open, with gate work staying below the package levels? Recommended yes. Operator, verbatim (dictated):

> yes, out of service means the marker is open is also very strong, because that tells us when our normal GHI system is adequate, right? We don't mean to take the vessel out of service. We just mean to temporarily act on it with every intention that it'll remain underway or out on the line, as they might say in aviation. But pulling into the hangar or dry dock definitely it takes the vessel out of service, right? And I wanted that to better manage alarms and tripwires and all that sort of thing.

A GHI fixed at the gate needs no package. `AGENTS.md` § Defect-fix routing stands, and *on the line* is the operator's word for that state. The MX marker's open and closed are *out of service* and *return to service*.

## source · the operator: the out-of-service package is the plan for return to service

Operator, 2026-11-02, verbatim (dictated), in the same message:

> kind of the out of service package, almost like a feature package, is it's the culmination of diagnosis and appraisal and prognosis. So I wouldn't call it design, except that it is a design for return to service. It is a plan, I should say, for return to service, not as much as a design. So that plan for return to service broadly characterizes what's going on, because then it gives us a clearer sense of goals and objectives. And then that's a good way to measure the outcomes, to know that, is this seaworthy, right? So we do sea trials, or we probably do test flights, right? Can we return this vessel to service? So out of service and return to service are good correspondents to MX hangar open, MX hangar closed, and all that sort of stuff. So I think we have a better taxonomy and hierarchy here. And the one we had was getting pretty drifty, to be honest.

## source · the operator: the hangar and the drydock are one place

The agent put whether the drydock contract is the out-of-service package, with a lean version for a hangar visit. Operator, 2026-11-02, verbatim (dictated), before choosing:

> Here's the thing. I've been mixing the metaphors, and it may not be necessary, although we could call them synonyms. Going into dry dock and going into the maintenance hangar are roughly the same thing. We either have, and this is where aviation's more useful, the A, B, C, and D level checks, or, you know, an incident. And maybe vessels have the same, that is, seagoing vessels have the same correspondent, but being in the hangar or being in dry dock, it's the same thing. You're neither sailing nor flying when you're in both of these places. So I think we're trying to distinguish their expression, and that's my fault. I just reach for metaphors all the time, but I would say they're equivalent. The MX language predates this dry dock stuff, and I don't mind the culmination of aviation and maritime. I like it, but we could treat them as synonyms, and that might be for the best, but treating them as distinct is problematic. is not a refutation of what you just shared. This out of service, return to service metaphor is strong. And if you want to tighten up around decisions we've made ever since the maintenance hangar entered in earlier in the year, then this is the right time to do it.

**Canon this meets, quoted.** `docs/rnd/contractor-kit.md`, decision *one condition with a standby level commanded at entry*: *"**Hangar** is the standing-maintenance level, for a hangar visit that answers one squawk. **Drydock** is the drastic level, taken under a contract."* (operator: *"A"*). `safe-mode-doctrine.md`, operator 2026-10-17: *"drydock is an extreme measure. the A,B,C,D system is aeronautical, but scheduled checks. the drydock metaphor, although nautical, is more - for me - an on-demand and drastic"*. `gz mx enter --level {hangar,drydock}`, and `gzkit.mx.alarms.alarms_off`, which turns the slow alarms off only at the drydock level.

**The agent's reading.** The two rulings agree on one condition and use place names for a difference of depth. What differs in the code is how much is lowered, not where the vessel is.

## decision · hangar and drydock are synonyms; the commands stay `gz mx`; one depth, not two

Ruled. Question: should hangar and drydock become synonyms, with two depths of visit under new names (A); one depth for every visit (B); or synonyms in prose only (C)? Recommended A. Operator, verbatim (dictated):

> These are synonyms for sure, so option A, but I'm not really convinced about two depths, to be honest, because your two depths are really actually GHI hanger, sorry, GHI gate apron doc level work versus, you know, like you said, what did you, I forget what you had, scheduled maintenance, that's A, B, C, and D. Frankly, the chore system has a good match for some of that, if not all of it. Or incident response, which then requires the hangar or the dry dock. So I'm not convinced about the two levels, to be honest. We can talk about it and you could convince me. I'm not sure if you're preserving prior decisions we made or arguing for it, but if you're still at the gate apron or dock, normal GHI direct repair is what we're doing. If we're at something that is either scheduled maintenance or incident response, then we're in dry dock in the hangar, right? Keeping them as synonyms is fine. I would keep the GZ commands at MX since that predates. But this is a good session. I think it's bringing in some order that we need.

**The agent withdrew the two depths.** It had been preserving the prior ruling, not arguing from the work. The ledger, read 2026-11-02: four `mx_session_opened` events, one without `mode: safe` (`d3c16ae0`, 2026-08-21, one defect, closed the next day), and three `safe` spans of this drydock. The shallow depth existed for *"a hangar visit that answers one squawk"*, and under the ruling above a squawk is answered on the line. Its one use is the only evidence for it.

- *Hangar* and *drydock* are synonyms for the out-of-service place. `gz mx` keeps its name.
- Out of service has one depth: the guards demoted, the slow alarms off, ceremony suspended, and lint, the fast static checks and the floor still on.
- This reverses *one condition with a standby level commanded at entry: hangar or drydock* (2026-10-27) on its two values. RO-13's *level per standby level* and every mode-contract paragraph naming *both standby levels* read one level.

**commissions:** 4 — the doctrine, `gz-mx`, `mx-mode.md`, the RO-13 and RO-14 specifications and the contract, on the operator's go on that row. 2 — `--level`, the marker's level field and every reader, by GHI, on the same go.

## decision · the alarm test decides between the line and out of service

Ruled. Question: can the work be done with every alarm on? Then it is on the line; if the alarms must come down, it is out of service. Options put: **A** that test decides, scheduled or incident being only the reason; **B** every scheduled check goes out of service; **C** chores stay outside the model. Recommended A. Operator, verbatim (dictated): *"the alarm test decides, and I like it, but the one squawk or not, I still think we just have to decide, are we in the hangar or not, right? Because that's what actually unhooks the alarms and tripwires."*

## source · the operator: chores are the checks; everything else is incident response

Operator, 2026-11-02, verbatim (dictated), in the same message:

> And that's what was my real motivation. I was getting tangled in my own shoelaces, metaphorically speaking. overriding something that we decided on October 27th, but this is why we do R&D. The hangar and dry dock values of standby level might have made sense at the time, but this planning discussion has made it clear that these things are synonyms. your system, look carefully at what A, B, C, and D checks actually are and how many of them require going to the hangar, possibly all. Does this mean that some chores probably should have been done in the hangar all along? Perhaps. I do like that the chores have a obligation recorded in their staleness. And I think we haven't been careful enough to check to see if some chores should have been done in the hangar anyway. I think some of these chores might have been done in flight, if I'm going to be honest, which is really bad, or in nautical terms, while underway. But again, I do like the idea of the operator's manual will tell you what you need to unhook to do any level of repair if it's normal routine. Now, if it's incident response, then the overall damage assessment and appraisal will tell us what systems need to actually be worked on. And then you're back to the operator's manual will tell you. So this assumes that the whole thing's not a write-off, right? So they're both kind of true, except for a scheduled check is not incident-based. It's routine scheduled maintenance-based. So this is the argument in favor of all chores are A, B, C, and D checks, to be honest. In fact, it might be smart to refactor those to impute that and then obviously make a gov0 equivalent of what A, B, C, and D mean. So I think the chore system and those level checks are arguably one and the same. So everything else is incident response, you know, which is on demand. And that's where we need the proper diagnosis, appraisal, evaluation, prognosis, plan for return to service, right? And that's probably what I would call it. It's a return to service plan. Whereas there's a definite structure and organization to A, B, C, and D checks that tell you exactly why you're going in there. Now, any one of these checks could reveal defects, but that's okay. I still think that's part and parcel to the chore system. So I think we're getting this pretty well delineated, to be honest.

(*"your system"* is kept as dictated; read as *you should*.)

Held for the operator's word once the sources are read, not yet ruled: all chores are the A, B, C and D checks; everything else out of service is incident response; *return to service plan* as the name of the incident's package.

## source · the operator: classify the chores by check level; rot; the return to service package

Operator, 2026-11-02, verbatim (dictated):

> I say letter check, I just mean those AC120, A check, B check, C check, D check. I'm not sure what they're correctly called, right? You help me. that we need to find a gzkit equivalent to those levels of check and actually start to classify the chores accordingly. I think that that's smart because I keep on appealing to that metaphor, and I think that they happen on different intervals, but I know the longer I work with a model and a code base, the worse the code base is likely to become. So we need to be aggressive on these chores because I think projects rot the longer you work with models, but the models save so much manual toil that we introduce new toils that are worth, you know, abiding by. But I think these level checks matter. So that's actually the next thing we want. How do we align chores for that? And then you're right. The other ruling I had about what while under review might cause further maintenance return to service planning matters. And I know we said an out of service package, but honestly, it should be called a return to service package. Being in the maintenance hangar already makes it clear that we're out of service, right? So out of service is a flag. The plan is return to service. So I might call it feature package on the build side and return to service package on the repair side.

## decision · the top row is the feature package and the return to service package; out of service is a flag

Ruled from the operator's words above. *Out of service* names the state the MX marker flags. The plan held while in that state is the **return to service package**, the repair side's peer of the feature package. *Out-of-service package* is withdrawn.

| Level | Construction | Repair |
|---|---|---|
| Why | Feature package | Return to service package |
| Grouping | Work package | Repair package |
| Marriage of REQ to task | Work order | Repair order |
| Action | Task | Task |

Next on the frontier, by the operator's word: a gzkit equivalent of the check levels, and the chores classified by it. Two research tracks were dispatched for its sources on 2026-11-02; no level is put until they are read.

## source · the census of chores against the alarm test

`docs/rnd/repair-work-organization/sources/census-chores.md`, written by a research subagent 2026-11-02, 41 of 41 `CHORE.md` read in full; read by the agent in full the same day. Its verdict rule is its own inference and is stated in the file. Verdicts: line 21, unclear 13, out of service 7.

> Read literally, the test therefore puts every chore on the line by default, because nothing states a need to lower an alarm.

> *Inference:* the hangar lowers the guard on the write it would be sheltering.

> `gz chores run` executes criteria, never a Workflow step

What bears on the frontier: the alarm test as ruled does not separate the population, because no procedure names a control it must lower, so the census added a second reading, a step that re-authors a control or the standard one judges by. A verdict falls on a step more often than a chore: of the seven, five are out of service at one step and on the line for the scan. All 253 run blocks fall outside every MX span, and no chore has recorded a run since 2026-10-17. Five written statements disagree with their mechanism (its § Population findings, 5), among them *"Each run of a chore is a ledger event"*, which no code does. Those five are defects to route, held here until the row 2 question.

## source · the letter checks

`docs/rnd/repair-work-organization/sources/letter-checks.md`, written by a research subagent 2026-11-02 and read by the agent in full the same day. Every quotation below is from it. faa.gov refused automated retrieval and fsims.faa.gov did not resolve, so Order 8900.1, the OpSpec text and the AMT handbook are unread; whether FSIMS defines a letter check is open.

> We cannot specify a letter check for mandatory inspection intervals because letter checks vary among different operators and can be escalated.

72 FR 46576, at 46577.

> (d) Line maintenance means— (1) Any unscheduled maintenance resulting from unforeseen events; or (2) Scheduled checks that contain servicing and/or inspections that do not require specialized training, equipment, or facilities.

14 CFR § 145.3(d).

> Organisations maintaining aircraft should have a procedure to determine whether the tasks or groups of tasks to be carried out fall under the line maintenance or base maintenance scope of the organisation

EASA AMC1 145.A.10(c).

> Task intervals are specified in terms of a frequency and usage parameter such as flight hours, cycles, and calendar time. Letter checks are not used.

Ackert, secondary, describing the MPD.

> Each letter check generally incorporates all the work covered by preceding checks, plus the tasks assigned at that letter-check interval.

Ackert § 4.2, secondary.

What it settles: the FAA governs the program, the MRB process sets tasks and intervals, and the operator packages them into visits, so the letters are the operator's design. Legacy MRB documents did once carry letter intervals (NTSB p. 26), so this corrects the agent's flat statement of the chain. No regulation read ties a letter to a hangar. In described practice C and D are hangar work, A is disputed, B has largely been folded into A and C, and pre-flight, transit and daily are not hangar matters. *"Possibly all"* is not supported. § 145.3(d) makes line maintenance a test of what the work needs, the same kind of test as the alarm test.

## decision · the agent's draft of gzkit's check levels, put and not ruled

From the two sources above. Intervals stay on each chore, as task intervals do in an MPD, and the letters are gzkit's own packaging, by what the work needs, each including those below. The chores' per-change and per-push gates stand below the letters, as pre-flight and transit do.

| Check | The work | Where | Census population |
|---|---|---|---|
| A | Inspect and report | Line | the 17 `propose` chores |
| B | Repair that touches no control | Line | the 4 line `repair` chores |
| C | Repair that may reach a control | Hangar | the 13 unclear |
| D | Re-author a control or its standard | Hangar | the 7 out of service |

Open beyond this draft: the census's second clause on the alarm test; a chore whose verdict falls on one step; and the operator's *"the operator's manual will tell you what you need to unhook"*, which reads as a per-chore list, against one depth and against the census's finding that the hangar lowers the ratchet guarding these writes.

## source · FAA Order 8900.1, as placed by the operator

Placed 2026-11-02 in `docs/rnd/repair-work-organization/sources/`, kept out of git by its `.gitignore`. `20_000_000.pdf`, Volume 20 Introduction (15 pages), read in full; `8900_1_Contents_11012026.accdb`, a contents index of titles and `drs.faa.gov` links, holding no section text, whose strings were searched; `Order-8900-1-Volume-16-Change-468-08292016.pdf`, unmanned aircraft, not relevant.

> A CAMP is a Federal Aviation Administration (FAA) authorization of a comprehensive inspection program and a program covering other maintenance, preventive maintenance, and alteration that a person designs to maintain a specific make, model, and series (M/M/S) aircraft and ensure each aircraft is airworthy.

> Nearly all CAMP-related regulations are performance-based regulations. Performance-based regulations focus on measurable outcomes and relies on the person to produce the prescriptive processes, techniques, or procedures in a document or manual.

The Introduction uses no letter check, hangar, line or base maintenance. The index's strings hold no title with *letter check*. Its nearest titles: *Chapter 5. Maintenance Schedule/Time Limitations*, with *Maintenance Schedule/Time Limitations: Foundational Information*, *Evaluate and Authorize the Maintenance Schedule/Time Limitations of a CAMP* and *Evaluate Proposed Adjustments to Task Intervals/Time Limitations*. Those sections are unread.

## source · FAA Order 8900.1 Volume 20: the four levels

`docs/rnd/repair-work-organization/sources/faa-8900-1-vol20-extract.md`, from the PDFs the operator placed 2026-11-02; the 18 sections searched for check terms and the passages read in context. Vol. 20, Ch. 8, Sec. 1 (CHG 912, 6/17/25):

> There are four levels of inspections, usually termed "A," "B," "C," and "D" checks. Line maintenance includes "A" and "B" checks while "C" and "D" checks are heavy maintenance.

> Line maintenance consists of three primary activity categories: transit checks, daily and weekly checks, and "A" and "B" checks.

Ch. 5, Sec. 1: intervals are *"expressed as hours of time in service, cycles, and calendar-time, or some other identifiable increment"*.

**What this corrects.** The source entry above and the agent's report to the operator said the FAA does not define the checks. For regulation that stands; for FAA guidance it was wrong, and the gap the research track named is answered. The operator's *"pretty sure it's the FAA"* holds. The FAA's line runs between B and C, which the agent's draft reached from the census independently. *"Possibly all"* in a hangar is answered no: A and B are line by the FAA's own text. The same order keeps a hangar and heavy maintenance apart: *"Maintenance providers may perform maintenance in locations such as a hangar, a line maintenance environment, or in a shop."* The Navy equivalent was not sought further.

## decision · gzkit adopts four check levels, by what the work needs

Ruled. Question: adopt the four levels, set by what the work needs, with intervals staying on each chore and each level including those below? Options as drafted above, the FAA's text read on both sides. Recommended yes. Operator: *"yes, adopt the four levels - use the rich detail we found"*.

| Check | FAA's category | The work in gzkit | Where |
|---|---|---|---|
| Transit, daily, weekly | Line | `gz check`, the commit and push hooks; not chores | Line |
| A | Line | Inspect and report | Line |
| B | Line | Repair that touches no control | Line |
| C | Heavy maintenance | Repair that may reach a control | Out of service |
| D | Heavy maintenance | Re-author a control or the standard one judges by | Out of service |

The rich detail the operator names carries forward: gzkit classifies its own work (*"The CH, not the FAA, is responsible for classifying their work"*); an interval is *"hours of time in service, cycles, and calendar-time, or some other identifiable increment"*, whichever is reached first, so agent work can age a chore; each check includes those below; and a check may be phased into smaller visits. The census's counts are the auditor's reading and move as each chore is classified. This also settles the alarm test's second clause: a step that changes a control or the standard one judges by is C or D, whether or not it names an alarm to lower. Heavy maintenance and the hangar stay distinct words in the FAA's text; in gzkit, heavy work is out of service by this table.

**commissions:** 4 — the levels defined in canon and the chore registry carrying each chore's level. 5 — every chore classified, a program, on the operator's go; a chore whose steps span levels is the next questions'.

## decision · the marker opens the state; each level means more disassembly and disconnection, by a named list

Put: **A** the marker opens the state, and each check level and return to service package names what comes down as tag-out line items, the blanket staying as RO-13 ruling 4's temporary group entry; **B** keep the blanket; **C** keep it and pin more guards. Recommended A. Operator: *"each level means more disassembly and disconnection"*. The agent read that as A, with the list growing by level, and said so. The texts agree: EASA's line work needs no *"extensive disassembly"* (AMC1 145.A.10), and a D check *"involves extensive disassembly to gain access for inspection"* (Hessburg, secondary).

- A and B disconnect nothing, by the alarm test. They may take code apart with every alarm on.
- C disconnects what its list names. D's list is the widest.
- *One depth* now reads: out of service is one state, and what is lowered within it varies by what the work needs.

**commissions:** 4 — each level's standard disconnection list, in the kit's tag-out log. 5 — the checkpoint read through tag-out lines, carried by RO-13's retiring of the group entry.

## decision · a finding above a chore's level leaves the run as a problem report

Ruled. Question: when a chore's steps span levels, where does the level sit? Options put: **A** a chore's level is the level of its inspection and the repairs that level allows, and a finding that needs more leaves the run as a problem report, for the next check at that level or a return to service package; **B** a chore's level is its highest step; **C** each step carries its own level. Recommended A. Operator: *"A"*. AC 120-16G § 5-4b supports it: unscheduled maintenance arises from *"scheduled maintenance tasks, pilot reports, or unforeseen events"*.

**commissions:** 5 — chores whose procedures carry a step above their level are cut to their level, in the classification program.

## decision · one requirement concept, specialized by inheritance

Ruled. Question: one requirement across build and repair, and where does a repair REQ live? Facts put: `Req.member_of` requires an outcome; exit item 3 has the catalog *"landed, empty"*; today an issue stands in for a REQ, always `BEHAVIOR`. Options put: **A** one shape, a repair REQ held on its repair package; **B** every requirement in the catalog; **C** every repair REQ under an outcome. Recommended A. Operator: *"sounds an opportunity for classic inheritance - they likely have some specialization"*.

Taken as A, refined: a base requirement carries what is common (statement, criteria, kind, revision, proof), and two specializations carry what differs. The catalog requirement keeps `member_of` an outcome, `derives_from` and `applies_to`. The repair requirement is held on its repair package, names its problem report, and may name a design REQ it aligns to. Which fields and how it is declared are diamond 2. Proof runs one path, so a docs issue gains an honest `SUPPORT` kind, which clears the discrepancy recorded under RO-14 act 5.

**commissions:** 4 — the requirements model and the RO-5 specification carry the base and its two specializations. 5 — RO-12 lands the repair requirement on the repair package.

## decision · an order is a real record; Gate 5 stays at the package

Ruled. Question: how much weight does an order carry? Options put: **A** a real record with an id, an ordered task list, its REQ bindings, and its own freeze and inspection, Gate 5 staying at the package; **B** a section of the package; **C** a full record with its own Gate 5. Recommended A. Operator: *"a"*.

| Level | Decides | Who |
|---|---|---|
| Feature or return to service package | Why, and the measure of success | Operator |
| Work or repair package | Scope and footprint; initiation; Gate 5 at close | Operator |
| Work or repair order | Which REQs marry which tasks, in what order; the freeze; inspection and buy-back | Coordinator and inspector |
| Task | One recorded action, with its measure and its (V) mark | Craftsman |

This answers exploratory repair: a repair package stays open while each repair order freezes once its REQ is known. A delivery package keeps its frozen baseline as ruled, and its work orders sit inside it.

**commissions:** 4 — the RO-5 and RO-12 specifications carry the order record and the level table. 5 — RO-12 lands it.

## decision · `RP-n` replaces `RO-n` in live text

Ruled. Question: what becomes of the `RO-n` names, now that RO-14 is a repair package? Options put: **A** `RP-n` replaces `RO-n` in the contract and specifications by contract amendment, keeping the numbers, `RO-n` staying an alias through the identity seam, ledger rows, commits and handoffs staying as written, the record id staying `WP-<NN>-<slug>`; **B** keep `RO-n` as a historical label; **C** drop the short names. Recommended A. Operator: *"A"*.

**commissions:** 4 — the contract, its specifications, the doctrine and the contractor brief, by contract amendment (B1). 2 — the `RP-n` alias in the identity seam, by GHI.

## decision · every opening of the marker has a return to service package

Ruled. Question: does a C or D check need a return to service package? Options put: **A** every opening of the marker has one, written from diagnosis for an incident, where the contract is that package, and generated from the level for a scheduled check, with the check as its reason, the level's standard list as its disconnections and the chores' acceptance as its measure; **B** only incidents have one. Recommended A. Operator: *"a"*.

**commissions:** 4 — `gz-mx`, the doctrine and the contract template carry it. 2 — `gz mx enter` requires the package, by GHI.

## decision · the questions checked; the unit is the task, and *card* is dropped

The operator had taken the recommended option four times running with no amendment, so the agent said so, named where its own framing carried the most weight, and asked whether the questions were the right ones. It listed what remained: whether *card* stays on *task*; how the return to service package relates to the feature and Release Packages; the close. Operator: *"1. no 2. let's discuss 3. ask it"*.

- Ruled: the unit of action is the **task**. *Task card* is dropped, as the operator said earlier: *"card language is superfluous but perhaps useful for measurement/tracking"*.
- The relationships are put for discussion, then the close is asked.

**commissions:** 4 — *task card* becomes *task* in the requirements model and the specifications.

## decision · the relationships: a seaworthy vessel serves users; a release only bumps the patch

The agent put three tensions for discussion: the two top rows answer to different parties; return to service and release are separate axes that touch; a remodel touches both columns. Operator, verbatim: *"1. no, a seaworthy vessel benefits users. 2. release package is N/A for return to service other than bumping patch. 3. a repair restores, but yes, some are remodels. we"* (the message ends there).

- Ruled, 1: the parity holds by audience too. Both top rows serve users, one by delivering value and one by restoring a seaworthy vessel.
- Ruled, 2: the Release Package has no part in return to service, except the patch bump a return yields.
- 3 is open: a repair restores, and some repairs are remodels. The operator's sentence was cut off.

Held for the operator, not put yet: the Release Package's members include *"repair packages"* (rulings of 2026-10-29), and the sea trial's best form is *"a fresh project on the released wheel"*. Whether a repair package's patch bump goes through the Release Package or the patch release route is how ruling 2 reads against those.

---

## decision · a restoring repair yields a patch; a remodel yields a minor release

Completes the open point above. Operator, verbatim, in the next message: *"we'd do a minor release"*, read as the end of *"a repair restores, but yes, some are remodels. we"*.

- A repair package that restores yields a patch bump, outside the Release Package.
- A repair package that remodels changes an obligation, so it rides a Release Package to a minor release, as the Release Package *"alone drives the next minor release"* (rulings of 2026-10-29). This is how *"repair packages"* among its members reads.
- The input table now sets the release too: restore, patch; remodel, minor.

## decision · a work package keeps one outcome

Not put: the operator ruled it out of change (*"I am not trying to change anything about the catalog | feature | work | release arrangements we've already agreed to"*). The four-level structure fits it, the work orders sitting inside one outcome's package. Revisit if a work order is found needing the REQs of two outcomes.

## source · the operator at the review: the work order is the OBPI

The agent walked the review with the operator in four parts, each with its weak points. Operator, 2026-11-03, verbatim:

> 1. I'm saying that the WO IS the OBPI, which is a correction, we use these package as a way of grouping for cohesion. discuss. 2. refactor advances patch. 3. marker means flag? but, yes to the point

> "The generated package relies on each level having a standard disconnection list, and none exists. Until RO-13 lands, any heavy check still lowers the whole blanket, so the waiver-ratchet problem stays open in the meantime." ==> yes, we need a standard disconnect list, which is what I meant by "the manual would indicate." what waiver ratchet?

> " We're out of service now under that blanket. Applying this model mid-drydock means renaming RO-n to RP-n while the work is under way." ==> this is the best time to pivot, this is exactly why we are in dry dock. sometimes we need to dispense with ceremony and controls to get the job done. we note the changes in the manual (like an airworthiness directive) and return to service as amended/adjusted

> 4. A + B: GHIs (repair at gate/apron/dock); C+D, bring to mx hangar. we do these at date intervals and/or at minor version advance. we need a better design discussion that looks to fit to gzkit and less to the metaphor. howver, A/B being GHI and C/D being mx is a start.

## decision · the review's rulings: refactor is a patch; the standard disconnect list is the manual; pivot now

- Ruled: a refactor advances the patch.
- Ruled: each level carries a standard disconnect list, the manual the operator meant by *"the operator's manual will tell you"*. A return to service package generated for a check reads it.
- Ruled: the pivot happens in this drydock, `RP-n` among it. Each change is noted in the manual as an airworthiness directive would be, and the vessel returns to service as amended.
- Ruled as a start: A and B are line work, answered by GHIs and direct repair; C and D take the vessel into the MX hangar; checks are due by date and/or at a minor version advance. The operator asks for a design that fits gzkit before the metaphor, so the level definitions are reopened on the frontier.
- The marker is the flag: `.gzkit/mx.json`, bound to its ledger event.

## decision · the correction: the work order is the OBPI's successor; packages group for cohesion

The operator names it a correction under the correction-versus-enhancement doctrine. It meets ruled canon: the requirements model's work package is *"the OBPI's successor, matching TASKs to REQs (ruled 2026-10-30)"*, and the agent's row 6 held *"a work package keeps one outcome"* without putting it. Under the correction the work order is the OBPI's successor, and the work package groups orders for cohesion, the job the ADR's checklist once did. Row 6's entry is withdrawn. Its consequences are put to the operator one at a time.

## source · the operator: care with the governors off; the successions; Gate 5

Operator, 2026-11-03, verbatim:

> do we have a commitment to draw down that list eventually? [the waiver ratchet, quoted]

> also, just because a guard is down is not a reason for the mx plan to exercise care and respect; while the "governors" are disabled don't overrev the engine, so to speak. or, do it, but note that is part of the diagnostic/testing process and is done with care.

> the obpi to work package alignment is right on. exactly ==> "RO-14's migration really runs from OBPI to work order." work package is the mADR successor, the WO is the OBPI successor.

> we just (correctly) revised this: "Where Gate 5 sits. [...] If the order is the OBPI, those two collide."

**The drawdown, measured 2026-11-03.** `data/waiver_ratchet_registry.json`: 35 shrink-ratchets and 2 closed-set locks, about 6,796 entries by baseline count, and no dated cutover. ADR-0.0.73's mechanism refuses growth and requires no shrink. No commitment to draw the lists down was found in the registry or that ADR's matched lines; the chores that shrink a baseline do so when run.

**Canon this meets.** `docs/rnd/four-records.md`, operator 2026-10-30, verbatim: *"yes, at most one for now - this the successor to the madr and the work pack is the successor to the obpi"*; the record: *"The feature pack is the mADR's successor, as the work pack is the OBPI's."*

## decision · care with the governors off; Gate 5 at the order

- Ruled: with a guard down, the work still takes care (*"don't overrev the engine"*). Running past a disabled limit is allowed only as a deliberate part of diagnosis or test, noted as such.
- Ruled: Gate 5 sits at the order, as on every OBPI. Question put: **A** Gate 5 at the order, the package closing when its orders do and its why is answered, with a value or seaworthiness attestation at the top; **B** at the package, as ruled earlier; **C** at both. Recommended A. Operator, confirming: *"answer was A"*. The earlier *"Gate 5 stays at the package"* is superseded.
- Ruled: RO-14's migration runs from OBPI to work order.
- Open: the operator's *"work package is the mADR successor"* against the ruling of 2026-10-30 that the feature pack is.

**commissions:** 4 — the care rule in the maintenance discipline the kit's personas carry.

## source · the operator: draws from features into work packages, completions into releases

The agent asked whether the mADR's jobs split, the story to the feature package and the grouping of OBPIs to the work package. Operator, 2026-11-03, verbatim:

> ask madr question again. the feature pack might be fulfilled by multiple combinations of work efforts. you can see that I am trying to retain the madr/obpi without tying to releases or feature bundles restrictively. variable assignments to/draws from features ==> work packages; variable completions or work packages / mx ==> release packages. this means that we might complete two work packages or all of a work order but not all of the work package and decide to place them in a release package and then ship a minor release. we can then evaluate what to do with partially completed work package; likely, we'll rebundle its remainder. we achieve the flexibility and decoupling i sought using these approaches.

**Canon this meets, quoted.** Requirements model: a work package is *"One dated attempt to deliver one outcome"* and *"closes by the 100% rule"*. The contract's Release Package row: it carries *"feature packages whole or in part, loose outcomes and repair packages"* (rulings of 2026-10-29).

## decision · the work package inherits the mADR as the story; the feature package is the epic; MX work advances patches

Ruled. Question: which mADR job does the work package inherit? Options put: **A** its planning job, a cohesive grouping of work orders drawing REQs from any feature packages and bound to no feature or release, the feature package keeping the story and value; **B** the whole mADR; **C** work packages within one feature package. Recommended A. Operator, verbatim:

> no. mx work should advance patches but neccesarily on a one to one basis, we already do with with the "patch release skill" that we have. that is operator judgement on A/B GHI work and perhap mandatory when leaving the mx hangar.

> aren't those the same thing retstated? [the Release Package's members, quoted]

> A is good, but B was good too. A wins because you elevate the feature pack to "epic" and keep the WP (mADR) as a story.

- **A is taken, with the operator's framing:** the feature package is the **epic**, and the work package, the mADR's successor, is the **story**. A feature package may be fulfilled by many combinations of work packages, and a work package draws from any feature packages. Neither binds a release.
- **MX work advances patches** through the patch release skill, not one patch per item: on the operator's judgment for A and B work, and perhaps mandatory at `gz mx exit`. The agent's *"or MX work"* among the Release Package's members is withdrawn. A remodel still rides a minor release.
- **The Release Package's members are unchanged.** The agent's restatement said the same as the ruling of 2026-10-29, and its proposed amendment is withdrawn.
- The requirements model's *"One dated attempt to deliver one outcome"* and *"closes by the 100% rule"* are amended: a work package draws from several outcomes, may ship part of its work, and its remainder is rebundled.

**commissions:** 4 — the requirements model's work package row and the four-records succession, amended. 2 — whether the patch release is mandatory at `gz mx exit`, put with the `gz mx enter` GHI.

## decision · the checks: dates for now; A and B GHI-driven, C and D MX-driven

Ruled. Question: how the levels run in gzkit. Options put: **A** C at each minor version advance or by date, D at each major version or every few C checks, A and B by date, B meaning a change to no control's behavior; **B** dates only for every level; **C** version only. Recommended A. Operator, verbatim: *"B for now until we have more maturity, recommend C + D on minor release + timed. the real dictiction: A + B are GHI driven and we should also recommend on GHI drawdown. C + D are mx driven and recommend on mx exit + timed."*

- Every level is due by date for now. Version and event triggers wait for more maturity.
- **A and B are GHI-driven.** They are recommended at a GHI drawdown.
- **C and D are MX-driven.** They are recommended at a minor release and at `gz mx exit`, and also run by date.
- Recommended means advised, not gated.
- Carried into the classification program, not put: whether B means a change to no control's behavior or no control file touched. It sorts the census's 13 unclear chores and moves no disposition.
- The waiver lists have no drawdown commitment (measured above). The agent's draft placed their drawdown in C. That placement is carried to row 3 as advice, not ruled.

## decision · the review's level table is the canon form of the model

Ruled at the sign-off walk-through, 2026-11-03. Question: does the two-column model in the review's § The model stand, and does its blank *Succeeds* cell on the epic row read *none (new)*? Operator, verbatim: *"yes, it stands; use "none (new)" the table needs to kept and associated as canon - it captures the design very well."*

- The review's table (level, construction, repair, succeeds, decides, who) is kept as the canon form of the model, its epic row reading *none (new)*: neither the feature package nor the return to service package succeeds an earlier record.
- Row 4 carries that table whole into canon, not the three-column level table above it.

## source · the operator at the sign-off walk-through: a remodel supersedes

At the review's input table, whose remodel row read *"changes one"*. Operator, 2026-11-03, verbatim:

> we don't change a req with a model as much as we supersede it - we remodel to refocus, refurbish, and redescribe. we transcend the prior req in the remodel. this precerves the value of prior work that was realized in the prior req

**Canon this meets, quoted.** `src/gzkit/models/catalog.py`, `Req.revision`: *"Only rises."*; the model has no field naming another REQ. `docs/governance/ieee/requirements-model.md`: *"Evidence is bound to the REQ's revision and the commit it was taken at"*, and its worked example, *"the affected REQs take a new revision, and their proof resets to `UNKNOWN` until revalidated, while the shipped evidence stays attached to the earlier revision."* Canon keeps prior value by revision in place; the operator's words keep it by a new REQ.

## decision · a remodel revises forward into a new REQ that supersedes the prior

Ruled. Question: when a remodel supersedes a REQ, is the result **A** a new REQ with a `supersedes` link, the prior kept whole with its evidence, or **B** a new revision of the same REQ, as canon has it? Recommended A. Operator, verbatim: *"yes, A and it is cleaner and addresses the discussion of revision - we revise forward into a new req."*

- A remodel states a new REQ that supersedes the prior. The prior REQ stays whole, with its evidence, as the record of value realized; it is not edited.
- The input table's remodel row reads *supersedes one*. The agent's proposal above (*"remodel **changes** a REQ"*) and the restore-and-remodel decision's *"changes an obligation"* are corrected by this entry, not rewritten.
- Commissions to row 4: the requirements model's revision rule and worked example amended to revise forward; a `supersedes` link on the base requirement. Carried as advice, not put: what `revision` still counts once an obligation's change makes a new REQ.
- Commissions to row 5: RP-12's repair requirement carries the `supersedes` link.

## decision · return to service is the package's close, apart from each order's Gate 5

Ruled at the sign-off walk-through, 2026-11-03. The review read *"returning it is Gate 5's return to service"*, from Part 0's *Release* term (*"in gzkit, Gate 5 attestation, which is return to service"*, `docs/rnd/renewing-vows/doctrine-merge.md`), while placing Gate 5 at the order and the return to service package at the epic. Question: is return to service **A** a separate operator act at the return to service package's close, certifying the vessel seaworthy after every order's Gate 5, or **B** the last order's Gate 5? Recommended A, on 14 CFR § 43.9's separation of approving the work from returning the aircraft to service. Operator, verbatim: *"Option A"*.

- Each order's Gate 5 attests that order's work. Return to service is the operator's act at the return to service package's close, and the flag closes on it.
- Commissions to row 4: Part 0's *Release* term amended so Gate 5 is not itself the return to service.

## source · the operator at the sign-off walk-through: components built for service

At the review's alarm test and standard disconnect list. Operator, 2026-11-03, verbatim:

> the parts we build are going to need their own mx awareness moving forward. All complex machines are build with service and mx in mind. So, BITS, safeguards, alarms, flags, safe mode compliance, and switched feature/caps flagging would become normals parts of component design. I think any complex machine/component is designed and engineered with these in mind. I realize that this would become a significant retrofit to current gzkit, but this was design immaturity on my part from the get go. I feel this mx/service awareness is a natural design expectation that we've missed.

Read against the run: the alarm test and the standard disconnect list both presume that each component already declares what can be lowered, tested and switched. Today the disconnect list is RO-13's temporary group entry, a blanket, because no component declares its own. The operator names that missing declaration as a design expectation, which under the correction-versus-enhancement doctrine reads as a correction. Its disposition is put to the operator below.

## decision · design for service gets its own R&D run

Ruled. Question: does designed-in MX awareness take **A** a decision inside this run, row 4 a component design standard and row 5 the retrofit; **B** its own R&D run, this run recording the source and pointing to it; or **C** this run's frontier reopened? Recommended B: this run organizes the work, the source is about how components are designed. Operator, verbatim:

> B, its own R&D run - we are building an integrated system and the requirements of integration are part of the spec that constrains design and integration. For instance: Eventually, in the case of AirlineOps, I grew tired of having the entire test suite run and asked if we could group tests by the subsystems they taught. Full test runs should come with releases, but not the daily git sync work. By tracking what systems are touched by each construction or repair, we can test for only planned direct effects. This is a design with subsystem awareness for modularity and purpose. That would be the case with everything - alarms, tripwires, access panels, mx procedures, safeguards. Like unittesting, these are all a normal part of fulfilling the contract and why things like keeping the hexagonal architecture in mind aslo helps.

- A separate R&D run takes design for service: integration requirements as part of the spec that constrains design; subsystem awareness, so each construction or repair tracks the subsystems it touches and tests its planned direct effects, the full suite riding releases; and alarms, tripwires, access panels, MX procedures and safeguards as normal parts of fulfilling the contract, as unit tests are, with the hexagonal architecture in mind.
- Ground it starts from, named and not read in full here: `gz check` already runs *"the tests the change touches"*, and the full suite runs under `gz check --full` at CI, release and the `quality-check` chore (root `AGENTS.md`); AirlineOps's subsystem test grouping, the operator's precedent.
- This run's standard disconnect list waits on that run: a level's list is drawn from what each component declares, and until components declare, RO-13's group entry stands.
- The run is commissioned, not opened. It opens on the operator's word through `gz-rnd`.

## decision · further research is a seventh disposition

Ruled at the sign-off walk-through, 2026-11-03, on the R&D discipline itself. The agent asked whether the design-for-service run should be tracked by a GHI under row 2 or recorded under row 6. Operator, verbatim: *"six dispositions of what?"*, then *"we are missing reframing/further research option? one outcome of rnd is expository: we have a better understanding that now opens up the need/opportunity for further research."* Options put: **A** a seventh row, *further research*; **B** further research routed to row 2 as a GHI; **C** row 6's reason field. Recommended A: the Design Council source already holds that findings *"can send them back to the beginning of their diamond work"*, and the map had no row for it. Operator, verbatim: *"A, add row 7 further research"*.

- Amended in the same act: `docs/governance/rnd-discipline.md` § Amended 2026-11-03, the `gz-rnd` skill (0.8.0) and its record template. This run's map gains row 7.

**commissions:** 7 — the design-for-service run.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | not pursued | — | Every outcome has a governed home in the drydock's canon and repair packages; the structure is reversible, so it fails the admission question. Revisit at civil rule if the structure outgrows the drydock |
| 2 | GHI / direct fix | commissioned | the `RP-n` alias in the identity seam; `gz mx enter` requiring a return to service package, and whether a patch release is mandatory at `gz mx exit`; `--level` and the marker's level field retired, every reader keyed to one state; the census's five statements that disagree with their mechanism (`census-chores.md` § Population findings, 5) | filed 2026-11-03 on the operator's go (*"yes, go for row 2"*), by `ghi-author`: #1302 the alias, #1303 `gz mx enter`, #1304 `--level`, #1305 the five statements |
| 3 | chore | commissioned | the chore registry carries each chore's check level and a date interval; the checks packaged by level, each including those below; A and B recommended at a GHI drawdown, C and D at a minor release and `gz mx exit`; the waiver lists' drawdown as C work, which has no commitment today | advise only; the operator directs admission (the operator: *"we need to be aggressive on these chores"*). Advice written 2026-11-03 on the operator's go (*"row 3 is a go"*): `repair-work-organization/row3-chore-levels.md`. Admitted 2026-11-03, operator verbatim *"A, admit as advised, marked provisional"*: every chore declares `check: {level, provisional: true}` and a `periodDays`, due at whichever comes first; `gz chores status --check <A-D>` reads one check's package |
| 4 | control surface, rule, doc, skill, hook | commissioned | the work order as the OBPI's successor and the work package as the mADR's, the feature package as the epic, Gate 5 at the order, the care rule with the governors off; return to service as the package's close and Part 0's *Release* term amended to match; the four levels, the two columns and the review's level table, whole, into the requirements model, with its revision rule amended so a remodel revises forward into a new REQ carrying `supersedes` and the four-records succession, the doctrine and the contract (by amendment, `RP-n` among it); the RO-5, RO-12, RO-13 and RO-14 specifications; `gz-mx`, `mx-mode.md` and the contract template; the chore class system and the chores README; *task card* to *task* | drafted and landed 2026-11-03 on the operator's go (*"row 4 is go"*), one commit per surface: requirements model `62fa1a52a` (outcome `validated` derived, operator *"c"*), doctrine `4f43398d6`, contract `c415267da` (`RP-n` in live text only, operator *"A"*), Part 0 and four records `9a7f2486c`, `gz-mx`, `mx-mode.md` and the template `236cbd5bd`, the specifications and brief `fdff604e9`, the chore class system and the care rule `1da1fde51`. Open in canon, not ruled: what `revision` still counts; how Gate 5's four outcomes apply to an order; how RP-13 re-reads its standby levels |
| 5 | one-shot refactoring | commissioned | every chore classified A to D and cut to its level, with findings above it leaving as problem reports; the checkpoint read through tag-out lines as RO-13 retires its group entry; RP-12 lands the order record, Gate 5 at the order and the repair requirement with its `supersedes` link; RP-14 migrates OBPI to work order | a program; the operator selects its route. Go given and route selected 2026-11-03, operator verbatim *"A"*: RP-12 first (the order record, Gate 5 at the order, the repair requirement with `supersedes`), then RP-14, then the chore classification and RP-13, since the order record is what RP-14 and the cut-to-level findings land on |
| 6 | no action | commissioned | the Navy's counterpart left unsought; the hyphen or acronym for the package names | each recorded in its entry |
| 7 | further research | commissioned | design for service: components built with their own tests, alarms, tripwires, access panels, MX procedures, safeguards and switches; integration requirements in the spec; each construction or repair tracking the subsystems it touches | opened on the operator's word through `gz-rnd`; the standard disconnect list waits on it |

## Close

**Challenge restated** (2026-11-03, deliberately, at the close). gzkit's maintenance work was organized by structure the agent improvised: *act* and *tranche* with no definition, record or witness; *a repair order is a work package* at the wrong level; a requirement that excluded repair; and *hangar* and *drydock* spelling a depth as a place. The model would keep improvising such structure and then drift from it. The run defines one structure for build and repair, four levels on each side; ties *out of service* to the open MX marker and the alarm test; adopts the FAA's four check levels for the chores; and answers what each level decides.

**Frontier.** Empty again, 2026-11-03, after the review's reopening was ruled.

**Review.** Written at `docs/rnd/repair-work-organization/review.md`, 2026-11-03; walked with the operator the same day, whose corrections reopened the frontier; rewritten after them. Walked again section by section at sign-off, 2026-11-03, where five rulings landed (the level table as canon, a remodel supersedes, return to service at the package's close, design for service as its own run, further research as a seventh disposition) and the review was corrected to them. Operator, verbatim: *"yes, read in full"*.

**Sign-off.** *"yes, read in full - fund"* — **fund**, 2026-11-03. Rows 2 to 5 and row 7 each still await the operator's go on that row.

## What this record does not license

No record, verb, rename or canon change is authorized by this run; funding authorizes none. Rows 2 to 5 await the operator's go on each row, and row 7's run opens on the operator's word. The one canon change made during the run, the seventh disposition row, was the operator's ruling on the R&D discipline itself, not a row of this run. The RP-12 specification draft (`docs/governance/harbor-ro12-contractor-kit.md`) stays paused, its ruling 1 standing.
