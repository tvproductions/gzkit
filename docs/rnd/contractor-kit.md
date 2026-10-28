# R&D run — contractor-kit

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-10-25T15:50Z.

**Challenge.** Operator g0, 2026-10-25, verbatim, in order:

> if the contractor for repairs and the contractor for restoration are just prompts, then this
> is extreme vibe coding... we'll need a skill, we'll need personas, we'll need tools. What in
> the wide world of vibe coding is going on?

> How many other poorly-handled functions and processes of MAJOR consequent, like safe mode for
> repair/remodeling/renovation in dry dock, do we have in gzkit. You were just about to go out
> and majorly vibecode this whole thing.

> A and we had better talk about it THOROUGHLY. Did we ever adopt our own local appropriation of
> pocock's grill-me? I think it is our rnd skill. Don't you think that would be appropriate
> right about now?

> I just saved myself from a vibe-coding disaster.

The "A" answers the agent's question of 2026-10-25, which put three options: **A** a full
contractor kit (two personas, a `gz-drydock` skill with drydock and restoration modes, `gz`
verbs that serve the next act and record passage-log and register lines as validated data)
specified as its own repair order and worked before any contractor launches; **B** personas and
skill now, tools with RO-5; **C** no contractor for RO-5, the session works it with the operator.

---

## source · the contractor brief

`docs/governance/harbor-contractor-brief.md` · read 2026-10-25

> **Goal.** Land the repair work of every open repair order, in register order, as its
> specification states, with the alarms off, recording everything each act unplugs, dismantles
> or modifies in the compliance register.

> The operator launches each contractor in a fresh session. The goal is the **Goal** paragraph
> of its section above; the loop prompt is: *"Read `docs/governance/harbor-contractor-brief.md`
> and the latest handoff; take the next act of the next open repair order in its order of work;
> stop and ask where the brief says to."*

The whole of each contractor today: a Goal paragraph, a loop prompt, and stop rules in prose. No
persona, no skill, no verb; every record it keeps (passage-log row, register line) is hand-edited
Markdown in the contract file.

## source · the contract's division of labor

`docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Division of labor · read 2026-10-25

> - **The session** appraises, plans, measures, drafts and rules with the operator, and executes
>   a repair order itself only when it is the measurement's own finding and small enough to read
>   in one sitting (operator, 2026-10-16: *"fable extra is expensive if you have a deterministic
>   plan you are now executing"*).
> - **Cheaper sessions** execute the deterministic repair orders under § Records.

## source · the OBPI pipeline, the nearest prior art

`.gzkit/skills/gz-obpi-pipeline/SKILL.md` (v6.69.3) · read 2026-10-25

> **Each stage's procedure is served by the runtime at stage entry.** `uv run gz obpi pipeline
> <OBPI-ID>` prints `Stage N procedure: <path> (sha256 <digest>)` for Stage 1 and again for every
> stage it enters; read that file before acting in the stage. [...] A stage file that is
> missing, empty or altered refuses the launch before any marker is written

> The pipeline dispatches four subagent personas across its stages. [...] Runtime mapping:
> `src/gzkit/pipeline_dispatch.py` (`ROLE_PERSONA_MAP`).

A persona, a skill, a runtime verb that serves each stage's procedure and refuses on a missing
one, and dispatched implementer and reviewer subagents: the shape the challenge names, already
built for OBPIs, which safe mode suspends.

## source · the pipeline-orchestrator persona

`.gzkit/personas/pipeline-orchestrator.md` · read 2026-10-25

> I see each ceremony step as a promise to the next. When I begin a step, I am committing to
> finish it and hand a clean state to what follows — not to pause, summarize, or ask whether the
> work so far is "enough."

Persona inventory, observed 2026-10-25 (`ls .gzkit/personas/`): flight-test-engineer,
implementer, main-session, narrator, pipeline-orchestrator, quality-reviewer, spec-reviewer. No
contractor persona.

## source · the starting rule changed before this run opened

commit `3c32d8f07` · 2026-10-25

`gz-rnd` lost `disable-model-invocation` after the harness refused the agent's start. Operator,
verbatim: *"On rnd, BULLSHIT, if I say we need it, then we need it and you start it."*; *"then
change that skill description, if you start rnd, and I don't wan it, I can always politely
decline. I want that shit changed."*; *"maybe the skill offers... do you want to start an rnd
session for that?"*; *"OR, when I call for it"*.

## decision · the contractor kit is specified before any contractor launches

Ruled. Question: A, B or C above. Operator: *"A and we had better talk about it THOROUGHLY."*
RO-5 tranche 1 is paused with nothing written.

**commissions:** 4 — the kit (personas, skill, verbs) as a repair order of the drydock; its shape
is what this run defines.

## decision · a chore hunts the other vibe-coded and underbaked processes

Ruled. Operator, verbatim: *"We had better get a "vibe coded" and underbaked bullshit chore soon
- to find the other places where my kindness and understanding were translated by the agent into
weakness and an opportunity to vibe code instead of behave in discipline"*, citing the agent's
reply that deferred the population audit into two options. Booked as an insight (2026-10-25T15:35:05Z,
scope `vibe-coding-audit`).

**commissions:** 3 — the audit chore; the operator has directed admission.

## decision · a contractor is a runtime-driven session that dispatches each act

Ruled. Question: what is a contractor? Options put: **A** a session whose loop a `gz` verb drives,
serving each act and its pinned procedure and refusing to advance until the act's records exist
as data; **B** a controller session dispatching each act to an implementer subagent with spec and
quality reviewers, no runtime verb; **C** both, A's runtime with B's dispatch inside each act, the
OBPI pipeline's shape applied to repair orders. Recommended C. Operator: *"c"*.

Tension carried, not resolved: per-act reviewer dispatch costs against the contract's *"Cheaper
sessions execute the deterministic repair orders"*.

## source · the operator on the pipeline

Operator, 2026-10-25, verbatim, answering the question of where the contractor runtime comes
from (A new drydock-only runtime; B the OBPI pipeline generalized now; C the pipeline's parts
reused under a thin act runner keyed on the work-package id; recommended C):

> I am VERY, VERY fond of, and protective of, the pipeline as a premier feature of gzkit. As
> such, it had regressed a little lately. Assuming we are in rnd mode, this requires careful
> discussion and attention. I am inclined to your "C" but we need to talk, at length. I think
> these two contractors in repair/restore mode in the hangar/drydock are distinct new personas.
> Discuss

Question 2 stays open: "inclined to C" is not a ruling. What regressed is unread; a research
report is commissioned (`docs/rnd/contractor-kit/sources/pipeline-regressions-2026-10-25.md`), and
the maintenance texts the contractor names may borrow from (14 CFR Part 43, § 121.371) are being
fetched verbatim into `docs/rnd/contractor-kit/sources/`. Until read, every aviation or shipyard
mapping below is a hypothesis.

## decision · the two contractors are distinct new personas

Ruled. Operator: *"I think these two contractors in repair/restore mode in the hangar/drydock are
distinct new personas."* Neither is the pipeline-orchestrator, whose grounding (*"not to pause,
summarize, or ask whether the work so far is 'enough'"*) contradicts a drydock contractor that
must stop on every structural gap.

## decision · each persona is anchored on the failure it resists

Ruled. Question: is each persona defined by the failure it resists — the drydock contractor's
*invention* (filling a gap the spec leaves, tidying, restoring as it goes), the restoration
contractor's *green by the wrong route* (a test loosened until it passes, the old shape
reconnected instead of the register's disposition, a cleared line taken as proof) — with traits,
anti-traits and grounding written outward from it; or by mode or product with failures beneath?
Recommended yes. Operator: *"yes, to MRO, good use of our prior planning"*.

## source · the MRO texts the renewing-vows run landed

Read 2026-10-25 in the landed files, each line confirmed in place:

`docs/rnd/renewing-vows/sources/us-gov-faa-ac-120-16g-maintenance-programs.md` (AC 120-16G, 1/4/16):

> A primary concept of the RII function is to prevent any person who performs any item of work
> from performing any required inspection of that work (§§ 121.369(b)(7) and 135.427(b)(7)).
> (§ 7-1c)

> The regulations are broad enough to permit you to organize all of these individual tasks into
> a series of integrated scheduled work packages of your own design (§ 6-1)

`docs/rnd/renewing-vows/sources/us-gov-14cfr-43-9.md` (eCFR as of 2026-10-02):

> The signature constitutes the approval for return to service only for the work performed.
> (14 CFR § 43.9(a)(4))

And the caution from that run's corrections of 2026-10-08 (`docs/rnd/renewing-vows.md`):
*"implementer, reviewers, narrator → pilot flying, pilot monitoring, assessor, briefer: the
mapping is wrong (AC 120-71B: the monitor works at the same time as the flyer)"*. Roles are
mapped from the text, not the sound.

## decision · MRO is the frame the contractor kit borrows from

Ruled with the decision above (*"yes, to MRO"*). The RII independence principle and
return-to-service-for-the-work-performed are read text; any further MRO name waits for its source.

## source · the operator's regard for the pipeline skill

Operator, 2026-10-25, verbatim: *"I am MOST FOND OF, and have the HIGHEST REGARD FOR, the pipeline
skill"*. Every design choice here is weighed against it: the contractor kit takes the pipeline as
its model and must leave the pipeline skill, its personas and its runtime no worse.

## source · the operator on what the two contractors are

Operator, 2026-10-25, verbatim, answering the question of who inspects an act (A one new inspector
persona for both contractors, the pipeline's reviewers untouched; B the pipeline's reviewers with a
contractor checklist; C two inspector personas; recommended A):

> yes, A, but are they the same thing? one wants to find solutions, get fixes in, see how to
> untangle bullshit after having documented what is encountered, the other wants to restore and
> realign back to gzkit's norms. One is pull away, forward, and improvig (not biased that gzkit is
> right), the other is restorative and is mindful of gzkit's big picture and purpose.

Two consequences, both against the agent's framing:

1. **The drydock contractor was mis-anchored.** The agent named its defining failure *invention*
   and its virtue spec-literalism. The operator's contractor finds solutions and gets fixes in,
   pulling forward, *"not biased that gzkit is right"*, after documenting what it encounters.
   Solving is its job, so invention is not its failure; the decision *each persona is anchored on
   the failure it resists* stands, but the drydock contractor's failure is re-opened.
2. **One inspector for both is suspect.** The two contractors face opposite ways: one away from
   gzkit's present shape, one back to its norms. An inspector holding gzkit's norms would drag the
   forward contractor back, which is the bias the operator excludes. "A" is held, not booked,
   until that is ruled.

## source · the MRO and ship-repair texts fetched for this run

Fetched verbatim 2026-10-25 by a research subagent from eCFR and FAA; read 2026-10-25 at the lines
quoted. Files under `docs/rnd/contractor-kit/sources/`: `14cfr43.md`, `14cfr121-371.md`,
`faa-rii-return-to-service.md`, `ship-repair.md`. Sections read so far are the ones quoted; the
rest is held unread.

`14cfr121-371.md`, 14 CFR § 121.371(c):

> No person may perform a required inspection if he performed the item of work required to be
> inspected.

`ship-repair.md`, 29 CFR 1915.89(c)(7)(iv), OSHA shipyard lockout/tags-plus:

> The employer shall ensure that the lockout/tags-plus coordinator maintains and administers a
> continuous log of each lockout and tags-plus system. The log shall contain: (A) Location of
> machinery, equipment, or system to be serviced; (B) Type of machinery, equipment, or system to be
> serviced; (C) Name of the authorized employee applying the lockout/tags-plus system; (D) Date that
> the lockout/tags-plus system is applied; (E) Name of authorized employee removing the lock or
> tags-plus system; and (F) Date that lockout/tags-plus system is removed.

`ship-repair.md`, 29 CFR 1915.89(i)(1):

> Before removing any lockout/tags-plus system and restoring the machinery, equipment, or system to
> use, the employer shall ensure that the authorized employee does the following:

`ship-repair.md`, DFARS 252.217-7010(d):

> The job order will state whether dock and sea trials are required to determine whether or not
> the Contractor has satisfactorily performed the work.

Hypotheses these raise, none decided: the compliance register is a lockout log (what was isolated,
by whom, when; who removed it, when), with the drydock contractor applying and the restoration
contractor removing; the repair order's spec is a job order stating its own trials; § 121.371(c)
restates the RII independence principle in the regulation itself.

## source · the pipeline regressions report

`docs/rnd/contractor-kit/sources/pipeline-regressions-2026-10-25.md` · written by a research
subagent 2026-10-25 (121 of 748 insights in the window read in summary, 19 in full; 57 of 86 GHIs
read in full, the search capped at 100; 84 commit messages, 9 diffs) · read 2026-10-25 at its
method, ledger fact and summary table; the per-item sections are held unread.

> **Ledger fact that bounds every "repaired" claim below.** The last `pipeline_launched` is
> OBPI-0.35.0-15 on 2026-10-11T18:06Z. The last `obpi_receipt_emitted` is the same OBPI on
> 2026-10-13T08:39Z. No pipeline event of any kind has been recorded since 2026-10-14.

Checked in the ledger 2026-10-25: last `pipeline_launched` 2026-10-11T18:06:16Z; last `pipeline_*`
event 2026-10-13T08:39:55Z.

Its summary against the four parts option C would reuse:

> | Dispatch composer (`pipeline_dispatch.py`, review composers) | The prompt-growth and
> double-envelope regressions are repaired (#1096, #1095). The fix-cycle cap is dead code (#1200,
> open). Dispatch refusals exit 0 (#1198, open). A marker-cache fault drops a ledger row (#1208,
> open). |
> | Persona frames (`.claude/agents`, `.gzkit/agents`, `.gzkit/personas`) | Two hand-authored
> copies with no writer (insight dated 2026-09-12). Read-only is enforced only as "no Bash" (#968).
> No guard against implementer cwd escape was found (B10, inferred). |
> | Procedure pinning (`pipeline_procedure.py`, the served stage files) | Landed 2026-10-15 without
> OBPI Gate 5; its obligations are carried to the catalog by the RO-8 ruling. One control (S2-080)
> has been reworded since the attestation. **Never run on a real OBPI.** |
> | Reviewer protocol (Stage 2 two-stage review, Step 4b, acceptance import) | Whole-tree proof
> currency kept by ruling (#1029), so the 4a/4b loop now stops and asks but is not gone (#1028).
> The finding-identity import refusal is unresolved in what was read. The verifier pipe gate that
> protects its evidence is switched off under safe mode (A3). |

States checked with `gh` 2026-10-25: #1200, #1206, #1208, #1028 OPEN.

Bearing on question 2: every part option C would reuse carries an open regression, and the newest
(procedure pinning) has never run on a real OBPI. Reuse would import them; the drydock contractor
would be the first real run of code the pipeline itself has not flown.

## decision · the drydock contractor resists bias toward the present shape; the runtime holds documentation-first

Ruled. Question: the drydock contractor's defining failure — A bias toward the present shape
(treating gzkit as right, patching around the old structure); B changing before documenting what
was encountered; C both, the persona anchored on A and B held by the runtime (an act's change
cannot land until its encounter record exists as data). Recommended C. Operator: *"C. both, and
your evidence suggest why we need at least two personas, perhaps even a third (the inspector).
repairer, inspector, restorer"*. This replaces the agent's earlier anchor, *invention*.

## decision · the performer of the repair never performs the restoration

Ruled. Operator, citing § 121.371(c): *"that's why I don't want the same agent/persona for the two
sides of the work"*. Read text: *"No person may perform a required inspection if he performed the
item of work required to be inspected."* The operator extends the independence principle from
inspection to the two sides of the work.

## decision · three personas: repairer, inspector, restorer

Ruled with the decision above (*"repairer, inspector, restorer"*). Terms, held here until the
glossary has a home: **repairer** (the drydock contractor), **inspector**, **restorer** (the
restoration contractor) — the operator's words. The texts' own terms differ: 14 CFR Part 43 speaks
of the person performing the work and the person approving it for return to service; 29 CFR
1915.89 of the *authorized employee* and the *lockout/tags-plus coordinator*. Whether one inspector
serves both sides is open: the operator's list names one, and the agent's concern that an inspector
holding gzkit's norms drags the repairer back is unresolved.

## decision · the compliance register takes the lockout/tags-plus log as its model

Ruled. Operator on the 1915.89 log and its removal procedure: *"this is PERFECT"*, with the
agent's mapping — the repairer applies lockouts, the restorer removes them — and the job order
stating its own dock and sea trials (DFARS 252.217-7010(d)).

**commissions:** 4 — part of the kit's shape; the record's fields are diamond 2.

## source · the lockout removal rule, read after the ruling

`docs/rnd/contractor-kit/sources/ship-repair.md`, 29 CFR 1915.89(i), read 2026-10-25:

> (2) The employer shall ensure that each lock or tags-plus system is removed by the authorized
> employee who applied it.

> (3) When the authorized employee who applied the lockout/tags-plus system is not available to
> remove it, the employer may direct removal by another authorized employee, provided the employer
> developed and incorporated into the lockout/tags-plus program the specific procedures and
> training that address such removal, and demonstrates that the specific procedures used provide a
> level of employee safety that is at least as effective in protecting employees as removal of the
> system by the authorized employee who applied it.

> (iii) Ensure that the authorized employee who applied the lock or tags-plus system has knowledge
> of the removal before resuming work on the affected machinery, equipment, or system.

And (i)(1)(iii), before any removal: *"Inspects the work area to ensure that nonessential items
have been removed and machinery, equipment, or system components are operationally intact."*

**Contradicted in part.** The ruled mapping (the restorer removes what the repairer applied) is the
text's *exception*, (i)(3), not its default, (i)(2). The text allows it only with a specific
removal procedure shown to be as safe as removal by the applier. Put to the operator.

## decision · removal by another under (i)(3) is the norm, carried by a removal procedure written at application

Ruled. Question: how is a lockout removed by someone other than its applier? A follow (i)(3) as the
norm — the repairer writes each line's removal procedure (what was disconnected, its disposition,
how to restore and test it) when it applies the lockout, a lockout without one is refused at
application, the restorer removes only under it and records the removal, the inspector checks
*"operationally intact"* before the line clears; B follow (i)(2), the repairer removes its own,
breaking the separation ruling; C keep the log as a record format only. Recommended A. Operator:
*"I love how you are showing adopting those regs, it DEEPLY strengthens our design and
implementation. For your Q: A. However, see my three roles."*

The operator's qualifier, *"see my three roles"*, is read as: the lockout's life is divided among
repairer, inspector and restorer, not between two contractors. The agent's reading, put to the
operator with the next question.

## decision · one inspector, whose standard is the job order and the lockout log

Ruled. The agent laid the lockout's life across the three roles — encounter (repairer documents;
the runtime refuses a change without the record), apply (repairer logs the lockout and writes its
removal procedure; inspector checks the record, the log line and that the procedure makes removal
by another *"at least as effective"*), remove (restorer removes under the procedure and records it;
inspector checks it was done under the procedure, *"operationally intact"*, tests kept semantic;
the repairer informed per (i)(3)(iii)), return to service (restorer brings the order to Gate 5).
Question: one inspector or two? A one inspector whose standard is the job order and the lockout
log, never gzkit's present shape, inspecting at application and removal, always a separate
subagent from the performer and never either contractor's session; B two inspectors, each sharing
its contractor's orientation. Recommended A. Operator: *"A"*.

This resolves the concern held since the operator's *"are they the same thing?"*: an inspector
judging against the record, not a direction, drags neither contractor.

## decision · repair the pipeline first, then reuse its parts unchanged

Ruled; this settles question 2. Facts put: every part option C would reuse carries an open
regression (#1200, #1206, #1208, #1028 OPEN); procedure pinning has never run and no OBPI can run
in safe mode (R4); procedure pinning's obligations ride RO-8 into the 0.35.0 Release Package, while
the four GHIs are direct repairs under § Defect-fix routing. Question: how does the kit relate to
the pipeline? A repair first, then reuse unchanged — the four GHIs repaired before the kit is built,
the kit imports the repaired parts unchanged keyed on the work-package id, its first runs are the
parts' first flight under the inspector, anything a run finds returns to the pipeline as a GHI and
is never patched inside the kit, procedure pinning stays with RO-8; B reuse as-is with the
regressions on the register as known hazards; C build the kit separately and leave the pipeline
untouched until civil rule. Recommended A. Operator: *"A"*.

The kit leaves the pipeline better, never forked — the bar the operator's regard for the pipeline
sets.

**commissions:** 2 — direct repair of #1200, #1206, #1208 and #1028 under their own GHIs, before
the kit is built.

## source · the job order and the changes clause

`docs/rnd/contractor-kit/sources/ship-repair.md`, DFARS 252.217-7005 (Inspection and Manner of
Doing Work), read 2026-10-25:

> (a) The Contractor shall perform work in accordance with the job order, any drawings and
> specifications made a part of the job order, and any change or modification issued under the
> Changes clause of the Master Agreement.

> (c) The Government may inspect and test all material and workmanship at any time during the
> Contractor's performance of the work.

> (4) The Contractor shall maintain complete records of all inspection work

`docs/rnd/contractor-kit/sources/dfars-252-217-7003-changes.md`, DFARS 252.217-7003 Changes (DEC
1991), fetched from the eCFR API and read 2026-10-25:

> (a) The Contracting Officer may, at any time and without notice to the sureties, by written
> change order, make changes within the general scope of any job order issued under the Master
> Agreement in— (1) Drawings, designs, plans, and specifications; (2) Work itemized; (3) Place of
> performance of the work; (4) Time of commencement or completion of the work; and (5) Any other
> requirement of the job order.

> (e) Nothing in this clause shall excuse the Contractor from proceeding with the job order as
> changed.

The change order is issued by the Contracting Officer, in writing, and only *"within the general
scope"* of the job order; work outside that scope is a new job order.

## decision · the repair order's specification is a job order, changed only by the operator's change order

Ruled. Question: what does the repairer work from? A the RO spec is a job order — goal, scope (what
may be disconnected), trials that show the work done, structural stops; the tranches a starting
plan the repairer may reorder or rework within scope, recording each revision; a solution beyond
scope is proposed as a change order the operator issues in writing (a recorded amendment to the
spec) or declines; work wholly outside scope is a new job order, a new RO; B the spec is a script,
every departure a stop; C free within the RO's goal, departures recorded after. Recommended A.
Operator: *"A"*.

This replaces the contractor brief's *"as its specification states"*, written for the literal
executor the operator rejected.

## decision · the remaining frontier, put to the operator

The agent reported that the operator had taken the recommended option on questions 6 to 9 in a row,
asked whether the questions were the right ones, and laid out the remaining frontier in order: the
bootstrap (who builds RO-5's store and the kit before any contractor exists); the log keeper (the
lockout/tags-plus coordinator); the persona budget against compress-before-growth; models and cost
per role; trials against the doctrine's sea trial and Gate 5 as return to service; the kit's RO
number and place; the audit chore's shape and rows 1, 5, 6. Operator: *"continue with your
questions"*.

## source · the contract on who executes a repair order

`docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Division of labor (quoted above): *"The
session ... executes a repair order itself only when it is the measurement's own finding and small
enough to read in one sitting"*; *"Cheaper sessions execute the deterministic repair orders under
§ Records."*

## decision · the operator and a working session build the bootstrap under the kit's own discipline

Ruled. Facts put: the kit is keyed on the work-package id from day one (question 8), so RO-5
tranche 1 must exist first; the four pipeline GHIs are repaired before reuse; no repairer exists
until the kit does; the bootstrap is neither small nor deterministic, so both division-of-labor
clauses refuse it. Question: who builds it? A the operator and a working session, each act one
commit with an independent reviewer subagent that never did the work, each disconnection on a
hand-kept lockout log (the last hand-kept records, for the restorer to clear), every structural
question a stop, and a recorded amendment naming the bootstrap as the division-of-labor exception;
B a cheaper session from a job order under the prose brief; C key the kit on RO ids, re-key at
RO-5. Recommended A. Operator: *"yes, we'll need the WP to exist and we're stuck, as you say. In
the true drydock/mx hangar fashion, we'll improvise and innovate until we have a pattern to build
from. A."*

**commissions:** 4 — the contract's § Division of labor amended to name the bootstrap as its
exception, with the operator's words.

## source · the lockout coordinator's duties

`docs/rnd/contractor-kit/sources/ship-repair.md`, 29 CFR 1915.89(c)(7), read 2026-10-25:

> (i) The employer shall establish and implement lockout/tags-plus coordination when: (A)
> Employees on vessels and in vessel sections are servicing multiple machinery, equipment, or
> systems at the same time; [...]

> (iii) The employer shall designate a lockout/tags-plus coordinator who is responsible for
> overseeing and approving: (A) The application of each lockout and tags-plus system; (B) The
> verification of hazardous-energy isolation before the servicing of any machinery, equipment, or
> system begins; and (C) The removal of each lockout and tags-plus system.

## decision · the coordinator is a new role; the runtime keeps the log; the operator attests

Ruled, amending the agent's option C. Question: who is the lockout/tags-plus coordinator? A the
runtime; B the operator at every lockout; C split by duty — the runtime keeps the log, the
inspector approves each application, isolation check and removal, the operator approves at order
level. Recommended C. Operator:

> Yes, C, the runtime, my attestation, and perhaps, an "orchestrator" that we haven't spoken of yet
> - that "orchestrator" can spawn multiple contractors for repair. Then, bring in an inspector,
> then, on the backside, bringing multiple restorers/integrators. So, the coordinator is a new
> orchestration role. That is a change but make sense from the regulatory guidance. inspectors
> shouldn't decide other than for compliance. A coordinator is a tactical, operational, and
> strategic chaperone for the entire affair. Let's discuss. Does that fit the regulatory guidance?

The runtime keeps the log; the operator attests; a new coordinator role oversees and approves
application, isolation verification and removal, dispatching repairers in parallel, the inspector,
then restorers. The inspector decides compliance only — the agent's C had given it the
coordinator's approvals, which mixed inspection with running the work. Four roles now: coordinator,
repairer, inspector, restorer.

## source · the person directly in charge, and the separation of inspection

`docs/rnd/contractor-kit/sources/14cfr121-371.md`, read 2026-10-25:

> (b) For the purposes of this section, a person directly in charge is each person assigned to a
> position in which he is responsible for the work of a shop or station that performs maintenance,
> preventive maintenance, alterations, or other functions affecting aircraft airworthiness. A person
> who is directly in charge need not physically observe and direct each worker constantly but must
> be available for consultation and decision on matters requiring instruction or decision from
> higher authority than that of the persons performing the work. (§ 121.378(b))

> (c) Each person performing required inspections in addition to other maintenance, preventive
> maintenance, or alterations, shall organize the performance of those functions so as to separate
> the required inspection functions from the other maintenance, preventive maintenance, and
> alteration functions. The separation shall be below the level of administrative control at which
> overall responsibility for the required inspection functions and other maintenance, preventive
> maintenance, and alteration functions are exercised. (§ 121.365(c))

Answering *"Does that fit the regulatory guidance?"*: it fits — concurrent servicing is the text's
trigger for a coordinator, and the person directly in charge is the role. Two parts are corrected by
the text: the coordinator may dispatch the inspector but not direct, override or filter it
(§ 121.365(c): the two lines meet only at the top, the operator); and "strategic" exceeds it — scope
belongs to the Contracting Officer's change order (DFARS 252.217-7003) and return to service to the
approving signature (§ 43.9(a)(4)), both the operator's. Put to the operator. Term held: the texts
say *coordinator* and *person directly in charge*; "orchestrator" collides with the
`pipeline-orchestrator` persona.

## decision · the coordinator's authority — provisional

Question: A tactical and operational, the operator keeping strategy (the coordinator dispatches,
sequences, deconflicts concurrent lockouts, approves application, isolation and removal against
procedure, proposes change orders and re-sequencing but never issues them, cannot direct, override
or filter the inspector); B tactical, operational and strategic, the inspector reporting through it.
Recommended A. Operator: *"Provisionally, I accept A, but let's delve."* Held provisional; not
booked as ruled.

## source · the role terms across the aviation and maritime texts

Read 2026-10-25 in `docs/rnd/contractor-kit/sources/` (and the renewing-vows AC 120-16G file):

- 14 CFR § 43.3(b): *"The holder of a mechanic certificate may perform maintenance, preventive
  maintenance, and alterations"*. § 43.7(a): *"no person, other than the Administrator, may approve
  an aircraft [...] for return to service after it has undergone maintenance, preventive
  maintenance, rebuilding, or alteration"* except as the section provides.
- AC 120-16G (in `faa-rii-return-to-service.md`): *"Your Director of Maintenance (DOM) and chief
  inspector must hold an airman's certificate"*; *"You must formally notify each of these
  individuals of their RII authorization as well as its scope (§§ 121.371(d) and 135.429(e))"*;
  *"You should also clearly state RII buy-back procedures"*; *"You must set procedures, standards,
  and limits necessary for required inspections, and acceptance or rejection of the RII"*; RII
  requirements identified *"on work forms, job cards, engineering orders"*.
- 46 CFR § 71.55-1: *"(a) No repairs or alterations affecting the safety of the vessel [...] shall be
  made without the knowledge of the Officer in Charge, Marine Inspection. (b) Drawings of alterations
  shall be approved before work is started"*; § 71.55-5(a): *"An inspection, either general or
  partial depending upon the circumstances, shall be made whenever any important repairs or
  alterations are undertaken."*
- 29 CFR 1915.89(o)(3): affected employees are trained *"(ii) That affected employees are not to
  apply or remove any lockout/tags-plus system; and (iii) That affected employees are not to bypass,
  ignore, or otherwise defeat any lockout/tags-plus system."* (o)(4)(iv) names *"a group's primary
  authorized employee"*. The section's definitions (§ 1915.80) were not fetched; unread.
- DFARS 252.217-7003, -7005, -7010: *Contractor*, *Contracting Officer*, *job order*, *change
  order*, *dock and sea trials*, the Government's right to *"inspect and test all material and
  workmanship at any time"*.

The crosswalk the agent draws from them, every row a proposal until ruled:

| gzkit role or record | Aviation (14 CFR, AC 120-16G) | Maritime (46 CFR, DFARS, 29 CFR 1915) | Proposed term |
|---|---|---|---|
| the operator, on scope | the certificate holder | Contracting Officer (change order); OCMI (knowledge of repairs, drawings approved before work) | Contracting Officer, for scope |
| the operator, at Gate 5 | approval for return to service (§ 43.7); airworthiness release (§ 121.709) | the Government accepts delivery; dock and sea trials | approval for return to service |
| coordinator | person directly in charge (§ 121.378(b)) | lockout/tags-plus coordinator (§ 1915.89(c)(7)) | coordinator |
| repairer | mechanic or repairman performing maintenance and *alterations* (§ 43.3) | Contractor; authorized employee who applies a lockout | repairer (no text term; the work is *alteration*) |
| inspector | RII inspector; acceptance or rejection, *buy-back* | marine inspector (§ 71.55-5); the Government inspects (DFARS -7005(c)) | inspector |
| restorer | the person completing work before approval | authorized employee removing a lockout and starting up (§ 1915.89(i), (j)) | restorer (no text term) |
| every other agent or session | — | *affected employee*: never applies, removes or bypasses a lockout | affected party |
| the compliance register | maintenance record entry (§ 43.9) | lockout/tags-plus log | lockout log |
| the RO specification | engineering order; job cards; work forms | job order, changed by change order | job order |
| an act's unit of work | task card, work card (AC 120-16G) | job order item | task card |
| a persona's assignment | RII authorization *"as well as its scope"* | — | authorization and scope |
| trials | — | dock and sea trials (DFARS -7010(d)) | dock trial, sea trial |

Collision found: `docs/governance/safe-mode-doctrine.md` already uses *sea trial* for one voyage
after exit, under civil rule (*"a fresh project on the released wheel running one work package end
to end"*), where DFARS states trials per job order. Held for the trials question.

## decision · the text's own term wherever one exists

Ruled. Question: A the text's term wherever one exists, the operator's words kept only where the
texts have none (*repairer*, *restorer*), each departure recorded with its rejected synonym,
contested terms ruled singly; B keep gzkit's current terms, the regulatory ones as glossary notes;
C every term on its own. Recommended A. Operator: *"A"*. Earlier: *"if we need to adopt terminology
closer to that regulatory guidance, lets do it."*

Terms held by this rule until the glossary has a home: **coordinator** (rejected: *orchestrator*,
which collides with `pipeline-orchestrator`); **inspector**; **repairer** and **restorer** (no text
term; *integrator* offered by the operator for the restorer, not taken); **affected party**;
**lockout log** (proposed by the rule over *compliance register*; the contract's ruling *"the punch
list is the compliance register"* is renamed only on the operator's word); **job order** and **change
order**; **task card**; **authorization and scope**; **approval for return to service**;
**Contracting Officer** for the operator on scope. *Sea trial* stays contested.

## decision · the coordinator is the operator-facing session; the inspector routes around it through the runtime

Ruled. Question: what is the coordinator mechanically, and how is the inspector kept from it (§
121.365(c))? A the coordinator is the operator-facing session and performs no work itself, it
dispatches repairers and restorers as subagents, it may request an inspection but the runtime
composes the inspector's dispatch from the job order, task card and lockout-log line, the runtime
writes the findings to the log and the operator sees them unedited, acceptance or rejection (the
buy-back) is the inspector's alone and only the operator overrides it; B the coordinator composes
every dispatch, independence by persona discipline; C the coordinator a subagent under a thin
session. Recommended A. Operator:

> A. yes, I did recommend an inspector before you started, rightfully, digging into the guiding
> text. I like an independent inspector and the pipeline does this with the adversarial reviewer.
> However, this system we are adopting will likely end up being even stonger - I am sure we can
> backport lessons from here back to the pipeline (and vice versa).

The coordinator's authority (question 12) was provisional pending this delve; this answer settles
its mechanics, and the provisional A stands until the operator books it.

## decision · lessons cross between the kit and the pipeline in both directions

Ruled with the decision above: *"I am sure we can backport lessons from here back to the pipeline
(and vice versa)."* The pipeline's adversarial reviewer (Step 4b) is the precedent for the
independent inspector. Consistent with question 8: a lesson crossing either way travels as a GHI on
the receiving side, never as a local patch.

**commissions:** 2 — each lesson that crosses, as a GHI on the side that receives it.

## decision · a dock trial per job order; the sea trial is an increment of real work before exit

Ruled, with the operator's amendment. Facts put: DFARS 252.217-7010(d) — *"The job order will state
whether dock and sea trials are required [...] (1) If dock and sea trials are required, the vessel
shall be under the control of the vessel's commander and crew. (2) The Contractor shall not conduct
dock and sea trials not specified in the job order without advance approval"*; the doctrine's sea
trial, *"a fresh project on the released wheel running one work package end to end, is the first
voyage's act under civil rule, not a condition of leaving the drydock"*. Question: A each job order
states its dock trial (its own witness, its alarms reconnected, run by the restorer, inspected,
before return to service) and the doctrine's single sea trial is kept; B dock and sea trials per
job order; C the sea trial only. Recommended A. Operator:

> Yes, I like A's compromise - we simply need to complete some work still under the mx mode. If we
> like it, the mx mode work gets booked and we leave mx and back to duty. So, we just do an
> increment of work with the repair work.

Taken: the dock trial per job order. **Amended:** the sea trial is an increment of real work done
while the hangar is still open; if the operator likes it, the mx work is booked and the hangar
exits. That makes the sea trial a condition of leaving, against the doctrine's *"not a condition of
leaving the drydock"*. DFARS sides with the operator: its trials *"determine whether or not the
Contractor has satisfactorily performed the work"*, so they come before the Government accepts
delivery. Doctrine change put to the operator before booking.

Put as A (amend: the sea trial before exit) or B (keep the doctrine). Operator, before choosing:

> I don't have a "fresh project" laying around and that, at the moment, is impractical. Make the two
> an OR - we'll do the better approach at a time where we can, but, the alternative approved
> approachis the one I suggest, better/best sort of thing. Before we go 'A' or 'B' consider what I
> just said.

Reformulated as two approved forms of one sea trial, best and better, and put again.

## decision · the sea trial gates exit, in either of two approved forms

Ruled. Draft put: *"The ship leaves the drydock only after a sea trial, done by the normal crew rather
than the contractors, in one of two approved forms. Best: a fresh project on the released wheel
running one work package end to end. Better: an increment of real work in gzkit itself, done through
the restored structures while the hangar is still open. The best form is used when it's practical;
otherwise the better form is the approved alternative. If the operator likes the trial, the mx work
is recorded and the hangar exits; if not, the ship goes back to the drydock."* Question: A either form
satisfies exit — today the better; the best when a fresh project and released wheel exist, run as the
first voyage and recorded as the best-form trial if it can only follow exit; B only the better form
gates exit. Recommended A. Operator: *"A"*.

**commissions:** 4 — `docs/governance/safe-mode-doctrine.md` § Seaworthy amended (superseding *"not a
condition of leaving the drydock"*) and the contract's exit conditions gaining the sea trial, each
with the operator's words.

## source · how personas reach an agent's context, and what their budget measures

Read 2026-10-25, after the operator declined to rule on the persona budget: *"first, we discuss this
personas budget and what it is meant to accomplish... is it that the personas are all loaded into
context together at once? I can't discuss this budget until we explore that more."*

Readers of `.gzkit/personas/`, traced in the code: `pipeline_dispatch._persona_frame` loads one
persona body into one dispatched subagent's prompt (`load_persona(project_root, stem)` over
`ROLE_PERSONA_MAP`); a skill's `persona:` frontmatter tells the main session to read one file;
`AGENTS.md` § Persona: *"Read the applicable definition in `.gzkit/personas/` when assigning a
role."* No hook and no orientation injects a persona (`.claude/hooks`, `src/gzkit/hooks`,
`scripts/session_orientation.py`: no mention). Per-file sizes 2,538 B (`main-session`) to 4,695 B
(`flight-test-engineer`).

GHI #1251, the budget's authority: *"aggressively trim all control plane artifacts (agents, rules,
skills and any other items that an agent loads and saturates context)"*; its observation reads
*"`.gzkit/personas/*.md` 24,879 B"*, naming no loading mode, beside *"5 agent definitions [...]
loaded on every dispatch"*. `data/instructions_files_budget.json`: `"surface": "personas", "pattern":
".gzkit/personas/*.md", "max_bytes": 12000` — a total across every file.

**Finding.** The persona budget's purpose is context saturation; its measure is a total no agent
loads. It prices a new, narrow persona the same as an existing one grown by the same bytes, and
only the latter saturates anyone's context. A witness measuring something other than its purpose is
a defect; it must become a GHI or a change order to RO-7's exit numbers on the operator's ruling.

## decision · each persona file is capped; the total is retired

Ruled. Question: A a cap per persona file, what one dispatch or role assignment carries, its value in
`data/instructions_files_budget.json` set by measurement under RO-1's protocol, the change carried to
RO-7 as a change order with the operator's words, the witness defect recorded as a GHI; B keep the
total, relabelled a catalogue-sprawl limit; C both. Recommended A. Operator: *"so, yes, caping each
personal file directly is the best approach. ==> "A""*.

The four new personas are judged by whether each stays lean, not by the size of the catalogue.

**commissions:** 2 — a GHI on the persona witness measuring a total no agent loads; 4 — RO-7's exit
number changed from a personas total to a per-file cap by change order.

Class, held as a hypothesis for the audit chore (row 3): other budgets may total a surface that is
loaded per item — agent definitions (descriptions every session, bodies per dispatch), path-scoped
rules, nested `AGENTS.md` by subtree. Unread; not decided.

## source · the pipeline's model routing

`src/gzkit/pipeline_dispatch.py`, read 2026-10-25: `DISPATCH_MODEL_MAP` routes a task by complexity
(simple → haiku, standard → sonnet, complex → opus); `REVIEW_MODEL_MAP` routes review (simple →
sonnet, standard → sonnet, complex → opus) under *"Reviews always require judgment -- never route to
haiku."* Every `.claude/agents/*.md` reads `model: inherit`. By construction the reviewer is never
below the performer it checks.

## decision · roles reuse the pipeline's routing, kept current by the model-card chore

Ruled with provisos. Question: A reuse the pipeline's routing unchanged — performers by each task
card's complexity, the inspector by `REVIEW_MODEL_MAP`, the coordinator on the session's model, the
contract's *"Cheaper sessions"* clause amended so cheapness is per task card; B a fixed model per
role; C the inspector always one tier above the performer. Recommended A. Operator:

> yes, and these models, and their model cards, which I think I have a chore for, must be
> periodically examined. A is good, but only if the model system card chore keeps these up. ALSO,
> the chore should look at these model level assignments as a part of that chore's task. So, "A" is
> fine, but with those provisos.

Checked: the chore is `frontier-model-card-currency` (`uv run gz chores show
frontier-model-card-currency`, read 2026-10-25). It keeps `data/frontier_model_cards.json` and the
doctrine sourced to cards current; it does not examine model-level assignments
(`DISPATCH_MODEL_MAP`, `REVIEW_MODEL_MAP`, skill `model:` frontmatter, agent `model:`). The proviso is
a gap in it.

**commissions:** 3 — `frontier-model-card-currency` widened to examine every model-level assignment
(the routing maps, skill and agent `model:` fields, the kit's roles) against the current cards each
run; the operator has directed it. 4 — the contract's *"Cheaper sessions execute the deterministic
repair orders"* amended to per-task-card routing.

Operator, on that row: *"that chore must be udpated with this expanded scope."* The go on row 3's
chore widening.

## source · group lockout

`docs/rnd/contractor-kit/sources/ship-repair.md`, 29 CFR 1915.89(k), read 2026-10-25: *"When more
than one authorized employee services the same machinery, equipment, or system at the same time [...]
(i) Assign responsibility to one primary authorized employee for each group [...] (iii) Ensure that
the primary authorized employee obtains approval from the lockout/tags-plus coordinator to apply and
remove [...] (A) Sign a group tag [...] before servicing is started; and (B) Sign off the group tag
[...] when servicing is finished."*

## decision · one lockout per surface; the coordinator sequences overlaps

Ruled. Canon already places concurrent repairers: *"local worktrees are fine"* (operator, 2026-09-27)
— each subagent in an ephemeral local worktree, never pushed, landing on main *"through the single
writer"*, the coordinator. Question: A the runtime refuses a second lockout on a surface another job
order holds; repairers run in parallel only on disjoint surfaces; overlapping job orders run in
sequence; B group lockout under a primary repairer; C no deconfliction. Recommended A, with B
recorded as the text's route to more parallelism. Operator: *"A. yes, there is no point in spawing
multiple workers if the work can't be subdivided. Don"*, completed in the next message: *"don't do
multiples for the sake of it"*. The coordinator dispatches more than one repairer only when the work
subdivides into disjoint surfaces; parallelism is never a goal.

## source · what the contract's punch list holds, and what the texts' records hold

Put to the operator: rename the compliance register the lockout log (A) or keep it (B). Operator,
before choosing: *"are we sure that punchlist, compliance register, and lockout log are the same
thing? it seems that the log is for the inspector <-> worker compliance alignment whereas the
punchlist might match to that but would be for work rather than inspection. Elaborate."*

`docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Punch list — the compliance register,
read 2026-10-25 in full: dispositions *restored* (*"returned to its prior state"*), *reconnected*
(*"returned in a new form"*), *retired* (*"removed for good"*), *replaced* (*"removed, with its named
successor"*); each line `open` until the restorer clears it. Its lines: RO-0 the alarm hooks and
verifier pipe gate switched off, the commit witness off; RO-1 GHI #1252's effectiveness flight not
yet run; RO-5 the brief-lane validators to be reconnected, OBPI briefs replaced; RO-4 `version_sync`
and `closeout` reconnected, `patch_release_event` and `gz-patch-release` replaced, a template
retired; RO-6 replaced text retired; RO-7 nested `AGENTS.md` retired, skills replaced; RO-8 briefs
retired, obligations replaced. The contractor brief adds: *"Tests may stay red; what is left broken
goes on the register."*

`docs/rnd/contractor-kit/sources/14cfr43.md`, 14 CFR § 43.9(a), read 2026-10-25: *"each person who
maintains, performs preventive maintenance, rebuilds, or alters [...] shall make an entry in the
maintenance record [...] (1) A description [...] of work performed. (2) The date of completion of the
work performed. (3) The name of the person performing the work [...] (4) [...] the signature [...] of
the person approving the work."*

"Punch list" occurs in no source this run or `renewing-vows` holds; it is the operator's term, from
construction practice, unsourced.

**Finding: the register is three records in one.** Against the texts:

- **Lockout log** (29 CFR 1915.89(c)(7)(iv)) — a *temporary* isolation, applied and removed, kept
  by the coordinator for coordinating concurrent servicing. Not an inspector-worker record: the
  inspector's acceptance or rejection is the RII's own record. Register lines of this kind: the
  alarms and pipe gate off, the commit witness off, the brief-lane validators disconnected until
  reconnected. Every line must be removed before return to service.
- **Maintenance record** (14 CFR § 43.9(a)) — *permanent* work: what was done, when, by whom,
  approved by whom. Register lines of this kind: every *retired* and *replaced* line, and the new
  form of a *reconnected* one. The contract's passage log (*"what changed, the measurement before
  and after, the commit"*) already carries part of it.
- **Punch list** (the operator's term) — *outstanding work*: deficiencies and work not yet done,
  worked before acceptance. Register lines of this kind: GHI #1252's flight not yet run; the brief's
  *"what is left broken"*; and, by this run's design, the inspector's rejections.

A *reconnected* line spans two: a lockout while the old connection is off, a maintenance-record entry
for the new form. The agent's earlier mapping, register = lockout log, was wrong.

## decision · three records: the lockout log, the maintenance record, the punch list

Ruled. Question: A three records — the lockout log (temporary isolations with their removal
procedures; kept by the runtime, approved by the coordinator; empty at return to service), the
maintenance record (permanent work under § 43.9(a), absorbing the passage log's per-act role, closed
by the operator's Gate 5 signature per order), the punch list (outstanding deficiencies, what is left
broken and the inspector's rejections; cleared before return to service); B two, outstanding work as
lockout lines; C one register with a kind column. Recommended A. Operator:

> A. and that matters because mx/drydock (with the alarms and tripwire concepts) DOES require that
> lockout concept. It seems that if I don't push back, I am liable for accepting summarized (partially
> vibed) reads from you of the foundational documents.

Corrects two earlier entries: *the compliance register takes the lockout/tags-plus log as its model*
(the register is three records, of which the lockout log is one) and the inspector's findings in
*the coordinator is the operator-facing session* (a rejection is a punch-list item, an acceptance the
inspection record's, not the lockout log's). The contract's § Punch list is renamed and split on the
operator's word, carried in the review.

**commissions:** 4 — the contract, the contractor brief and the doctrine's § Handback carry the three
records in place of the single compliance register.

## decision · every mapping put to the operator reads both sides in full first

From the operator's words above. The agent put *"register = lockout log"* to the operator after
reading the OSHA log in full and the contract's register not at all; the operator ruled on it
(*"this is PERFECT"*), and only the operator's push-back caught it. That is this skill's own rule
broken — *"Read the source before anything drawn from it becomes a decision"* — on the gzkit side of
a mapping rather than the text side. From here, a question that maps a text onto gzkit canon cites
both sides, each read in full, and says so. Before the review, the agent re-reads every source a
decision in this record rests on that was read only in part, and marks what moves. Insight
2026-10-25T21:14:15Z, scope `gz-rnd:both-sides-read`.

**commissions:** 4 — `gz-rnd` § Sources before decisions gains the both-sides rule.

## source · the re-read of every source read only in part

Read in full 2026-10-25, under the decision above: the pipeline regressions report (all 201 lines);
`.gzkit/skills/gz-obpi-pipeline/SKILL.md` (all 251 lines); `docs/governance/safe-mode-doctrine.md`
(all 80 lines); the contract's § Exit — seaworthiness; the ratified glossary,
`docs/rnd/renewing-vows/doctrine-merge.md` Part 0 § Terms (*"Ratified 2026-10-10 (operator, verbatim:
'ratify Part 0')"*), which the doctrine names as the carrier of its terms; and
`.claude/rules/model-selection.md` (loaded this session). What moves:

1. **Question 8's repair set was drawn from the report's summary table.** The full report names more
   open defects in the parts the kit reuses: #1198 (dispatch refusals exit 0), #1203 (a recorded
   position has no reader without a marker), #1205 (stale-marker crash, in a registered security
   surface), #1194, #1209, #1204; implementer containment #1185 (open until one real completion) and
   B10 (*"No mechanical guard against a cwd escape was found"*, inferred); Part C's latent defects
   #1207, #1199, #1202, #1225, #1145, #1193, #993. Of the four booked, #1028's root (*"currency is
   whole-tree, not per-obligation"*) stands by ruling (#1029, won't-fix). Two constraints bear on the
   kit: *"writes made through Bash are invisible to every Write/Edit-matched hook"* — only the
   commit-side fence sees them; and #968, *"real read-only enforcement for reviewer subagents is not
   possible in Claude Code"*.
2. **Question 13's terms meet a ratified glossary.** Part 0 § Terms: *"Commander. The one human, as
   the shaper of intent and the decider of what the force is tasked to do. Captain. The same human, as
   the holder of the signature and the override."*; *"Order. How command reaches the work: a standing
   order binds every position; a tasking order binds one work package and carries the role's
   auspices."*; *"Position. An obligation and a role to fulfil it. [...] Every agent is crew, the
   orchestrating session included."*; *"Release. The captain's signature on what ships; in gzkit, Gate
   5 attestation, which is return to service."* The run's *Contracting Officer* duplicates
   *commander*, and *job order* duplicates *tasking order*: ratified canon held the terms first.
3. **Question 16 amends ratified text in three places.** Part 0: *"Sea trial. One work package run on
   a fresh install of the released wheel."*; the contract's exit: *"The sea trial [...] is civil rule's
   first act, in Movement E of the campaign where it already lives; it is not an exit condition"*; and
   the doctrine. The campaign plan's Movement E is a fourth surface; campaign amendments need the
   operator's ratification.
4. **Question 18 rested on the pipeline's maps; a binding rule allocates further.**
   `model-selection.md` § Subagent effort levels, operator ruling 2026-10-05 (*"A (so model +
   effort)"*): execution sorties mid-tier at `low` effort; assessment strong at `high`; *"Cross-vendor
   IV&V; security-sensitive assessment"* strongest at `max`; headquarters synthesis strongest at
   `high`; effort set on the agent definition, never the dispatch.
5. **Question 20 is consistent with the doctrine**, which already says *"What an act leaves broken
   goes on the contract's punch list, which the exit empties"*; its passage log (*"One row per act:
   what changed, the measurement before and after, the commit, the witness"*) is the doctrine's, so the
   maintenance record absorbing it amends the doctrine too.

The pipeline skill's full body adds nothing against question 1; its *"Use one writer per governed
checkout"* and *"Never stash, pop, reset, revert, or sync another active run's work"* agree with
question 19.

## decision · every open defect in a part the kit reuses is repaired before reuse

Ruled; widens question 8's repair set. Question: A every open defect in the parts the kit reuses —
dispatch, markers and position, persona frames and implementer containment, procedure pinning, the
reviewer protocol: #1200, #1206, #1208, #1198, #1203, #1205, #1194, #1209, #1185, a cwd-escape guard,
and #1028's stop-and-ask boundary (its cause stands by #1029); latent defects outside those parts
(#1207, #1199, #1202, #1225, #1145, #1193, #993) stay pipeline GHIs on their own schedule; B only the
original four; C everything the report names. Recommended A. Operator: *"A for sure."*

States checked with `gh` 2026-10-25: #1198, #1203, #1205, #1194, #1209, #1185 OPEN (and #1200,
#1206, #1208, #1028 earlier). #1204 is OPEN but concerns a brief's scope, RO-8's ground, not a reused
part.

**commissions:** 2 — direct repair of the eleven under their own GHIs before the kit is built,
replacing question 8's four; a GHI filed for the cwd-escape guard, which has none.

## source · the operator on vocabulary for maintenance work

Put: A ratified Part 0 wins and the texts fill gaps (Commander, Captain, tasking order, positions and
crew; *Contracting Officer* and *job order* rejected); B amend Part 0 to the regulatory terms; C keep
both as synonyms. Recommended A. Operator, before choosing:

> for mx work, I think the regulatory language is stronger, give me a new rundown - hopefully we span
> naval and aviation terms well. I am leaning B (or even C), but show me

The sources held span civil aviation (14 CFR), the Coast Guard (46 CFR), Navy ship-repair contracts
(DFARS 252.217) and shipyard safety (29 CFR 1915.89), not the Navy's own maintenance manuals, where
naval and aviation maintenance meet. Commissioned 2026-10-25, verbatim into
`docs/rnd/contractor-kit/sources/`: COMNAVAIRFORINST 4790.2 (NAMP), COMUSFLTFORCOMINST 4790.3 (JFMM),
NAVSEA S0400-AD-URM-010 (Tag-Out User's Manual). Until they land, any Navy term is unread.

## source · the Navy manuals: refused by every host

Research subagent, 2026-10-25; files `navy-namp.md`, `navy-jfmm.md`, `navy-tagout.md` under
`docs/rnd/contractor-kit/sources/`, read 2026-10-25. Every navy.mil host refused automated retrieval
(403 challenges, a TLS reset); the refusals are recorded and were not worked around. Editions
identified: COMNAVAIRFORINST 4790.2E (28 Oct 2024; definitions in Appendix A, QA in Chapter 7,
Maintenance Control in Chapter 5, *"Impromptu CDI evaluations"* named in its highlights); JFMM Rev D
Change 5 (13 Jun 2025, from search snippets); Tag-Out User's Manual Rev 08 (28 Oct 2020). None of the
requested definitions was read from current text.

Secondary and superseded, cited as such: an FAS-hosted extract of the original JFMM (c. 2000–2002),
`navy-jfmm.md`: *"Dock Trials are those ship trials conducted at the Industrial Activity to determine
the ability of the ship, from a material standpoint, to conduct Sea Trials safely."*; *"Restoration
Level Maintenance [...] The minimum planned inspection, maintenance and testing criteria to be applied
to ensure a component will function satisfactorily until the next planned accomplishment of the
maintenance requirement."*; *"Supervising Authority The officer designated by NAVSEA to represent the
Navy Department at an industrial activity"*. It verifies nothing about the current manuals.

Per the skill: *"When a host refuses automated retrieval, ask the operator for the file; do not work
around the refusal."* Asked.

## source · the Navy manuals, placed by the operator

Operator: *"all placed"*. Read 2026-10-25 from the operator's PDFs, text extracted with `pdftotext`,
verbatim extracts saved as `docs/rnd/contractor-kit/sources/navy-tum-rev08.md` (the Tag-Out User's
Manual's Appendix B glossary in full, §§ 1.6.1 g–h, 1.6.2, 1.6.3) and `navy-jfmm-vol5-glossary.md`
(JFMM Rev D Chg 5 Volume V Part I Appendix A, 13 JUN 2025, in full). The NAMP file placed, `CNAF
4790.2E release LTR.PDF`, is the eight-page release letter, an image with no extractable text; the
NAMP's Appendix A, Chapter 5 and Chapter 7 remain unread.

Tag-Out User's Manual, Rev 08:

> **Authorizing Officer** The person with the authority to sign for issuing or clearing tags and
> labels. Department Heads shall designate Authorizing Officers by billet or watchstation.

> **Tag-out** a. A process of hanging danger or caution tags to isolate a system or equipment to
> protect personnel or equipment.

> **Tag-out Log** [...] this control document is used for administering tag-out procedures and a
> record of authorization for each active tag-out action.

> **Line Item** An individual entry in a tag-out that details the isolation, hazards, and work
> required for completion of a specific job.

> **Cleared** This is an Authorizing Officer function. When the line item is "cleared", the hanging
> tags are no longer referenced by that line item.

> **Repair Activity** A RA is any activity other than Ship's Force involved in the construction,
> testing, repair, overhaul, refueling, or maintenance of the ship. **Ship's Force** Personnel
> assigned to the ship who are responsible for maintenance and operation of ship's systems and
> equipment.

> **Lead Maintenance Activity (LMA)** The single activity responsible for integrating all
> maintenance and modernization on U.S. Naval ships during any type of availability.

> 1.6.2 [...] A second qualified person shall independently determine the adequacy and accuracy of
> the line item and isolation.

> **Danger Tag** A red tag prohibiting operation or removal of equipment that could jeopardize safety
> of personnel or endanger equipment, systems, or components. **Caution Tag** A yellow tag used as a
> precautionary measure to provide temporary special instruction or to indicate that unusual action
> must be exercised to operate equipment.

JFMM Volume V, Appendix A:

> **Quality Assurance Inspector** The designated individual(s) in FMA and ship work centers who
> inspect the work of other individuals, not their own work.

> **Inspection** A certification conducted by a separate individual qualified as an inspector [...]
> **Verification** Certification required to be performed by the craftsman.

> **Craftsman** A mechanic or other individual trained in QA methods and procedures [...] to perform
> maintenance on ship's systems or components.

> **Formal Work Package** Written instructions [...] delineating all the essential elements and
> guidance necessary to produce acceptable and reliable products. **Controlled Work Package** The
> records that provide the Objective Quality Evidence (OQE) necessary to certify that the completed
> maintenance was authorized, required tests were completed and work was certified. This consists of
> the Formal Work Package (FWP) and OQE.

> **Objective Quality Evidence** Any statement of fact, either quantitative or qualitative, pertaining
> to the quality of a product or service based on observations, measurements, or tests which can be
> verified.

> **Departure From Specification** A lack of compliance with any authoritative document, plan,
> procedure, instruction, etc.

> **Dock Trial** Dock Trials are those ship trials conducted at the Industrial Activity to determine
> the ability of the ship, from a material standpoint, to conduct Sea Trials safely.

> **Re-Entry** Includes any and all work and testing in a SUBSAFE certified system [...] from the
> first breaching through final grooming, testing and return to final operation [...] **Re-Entry
> Control** The controls used to document the re-entry and re-certification of SUBSAFE systems

> **Valve Repair, Restoration, Overhaul** a. Repair. Any work done to improve the material condition
> or operation of the valve correcting deficient conditions such that the component may be returned
> to service, but which, in total does not meet the full intent of the applicable restoration or
> overhaul technical standard [...] b. Restoration or Overhaul. All valve parts replaced or restored to
> the requirements of the applicable technical standard

> **In-Process Surveillance** The review of work in progress by personnel not directly involved with
> the work [...] **Rework** The unplanned repetition of a step or a series of steps in a Formal Work
> Package. **Defect** An imperfection that impairs completeness or quality or does not meet required
> specification.

> **Naval Supervisory Authority** The officer designated to represent the Navy Department at an
> industrial activity [...] **Maintenance Manager** Those persons, such as Port Engineers, Ship
> Superintendents, Ship's Coordinators [...] assigned to assist Ship's Force in the tracking of work
> candidates, development of work packages

## decision · a scoped register: maintenance vocabulary inside the hangar, Part 0 for the force

Ruled. Four-column crosswalk put (Part 0, aviation, Navy, maritime). Question: B amend Part 0
force-wide; C synonyms everywhere; D inside the hangar and drydock the maintenance vocabulary governs,
Part 0 governs the force, one recorded crosswalk binds them row by row and is canon. Recommended D.
Operator: *"D, yes."* Rows where the four columns disagree are ruled one at a time.

**commissions:** 4 — the crosswalk as canon beside Part 0 (its home is the glossary's, unsettled until
the DDD-discipline run names it; held in this record until then).

## source · the Navy's tag-out clearing rule

`docs/rnd/contractor-kit/sources/TUM_REV_8_28Oct20.pdf` § 1.8 Clearing Tag-outs, read in full
2026-10-25:

> 1.8.1 General. Remove danger and caution tags immediately when the operation/work line item(s)
> requiring the tag(s) has been corrected and clearing of tags has been authorized by the Authorizing
> Officer and RA Representative (when applicable).

> 1.8.4 a. [...] In situations where the RA Representative is no longer available (i.e., RA has
> completed work and left the geographical area or the ship has departed) the Authorizing Officer may
> authorize clearing the tag by marking the Clearance Authorized Repair Activity block on the TRS as
> "RA Not Available".

> 1.8.5 b. The person assigned shall remove the tag. [...] (2) If upon removal of a tag the item is
> found out of its expected position, all tag removal/restoration efforts for the items shall be
> stopped. The discrepancy shall be reported immediately to the Authorizing Officer and RA
> Representative.

> 1.8.3 [...] Repositioning of a component with multiple danger tags is never authorized until all
> danger tags have been cleared.

Against OSHA's § 1915.89(i)(2) default (removal *"by the authorized employee who applied it"*), the
Navy's default is removal by *"The person assigned"* under the Authorizing Officer's clearance, with
the departed repair activity marked *"RA Not Available"* — the ruled design (question 6) as the norm,
not the exception.

## decision · the isolation is the Navy's tag-out

Ruled. Question: A the Navy's tag-out — **Danger** and **Caution** tags (an alarm off and locked; a
tripwire that records), the **tag-out log** of **line items** replacing question 20's "lockout log",
the coordinator holding the **Authorizing Officer** duty to issue and clear, the restorer *"the person
assigned"* with the departed repairer marked *not available*, question 6's removal procedure carried
in each line item, OSHA kept as a cited source; B OSHA's lockout as recorded. Recommended A. Operator:
*"A"*.

Amends the names in questions 6, 19 and 20 (lockout → tag-out; lockout log → tag-out log); their
substance stands. Adds the restorer's stop rule (§ 1.8.5 b(2): found out of its expected position →
stop and report) and the multiple-danger-tag rule (§ 1.8.3). The Danger/Caution pair names the
alarm/tripwire classification RO-10 parked; RO-10's rubric is not decided here.

## source · the operator on the work package, and the JFMM's formal and controlled work packages

Put: A job order, change order, departure from specification, maintenance record with OQE, avoiding
the Navy's "work package" as colliding with RO-5's; B the Navy's FWP/CWP pair; C tasking order.
Recommended A. Operator, before choosing:

> I am not sure they are misaligned and we have an odd exception with agents/llms. The Formal Work
> Package IS good terminology, it is the strict shape and guidance. In fact, the instructions and
> criteria are a formal work package (sort of plan and spec) and the work package is the entire
> bundle; which is an affordance for our llm context. therefor, we can retain gzkit's work package
> and they can bundle repair orders, work orders, release package. etc. Let's expand here. The matrix
> of all of this language is VERY useful. I LIKE that a work package contains formal work package and
> controlled work. It is strong. I also think change order from dfars is worth mixing in. mx record
> and change order could be synonyms too. lots to untangle

JFMM Rev D Chg 5 Volume V Part I Chapter 2, read 2026-10-25 (§§ 2.2, 2.2.3, 2.2.4, 2.3.7 in full):

> 2.2 TECHNICAL WORK DOCUMENTS. Technical Work Documents (TWD) consist of three general types:
> Maintenance Procedures (MP), Formal Work Packages (FWP) and Controlled Work Packages (CWP).

> 2.2.3 Formal Work Package. An FWP coordinates in a single document materials required, initial
> conditions, MP, test and inspections, and system restoration for the selected maintenance task.
> [...] FWPs should be only as detailed as required by the complexity of the work, craftsman
> knowledge, technical requirements, extent of tests, and level of worker supervision required

> 2.2.4 Controlled Work Package. A CWP is required when higher authority requires a record (Objective
> Quality Evidence (OQE)) of repairs [...] In its simplest form a CWP will consist of, as a minimum, a
> MP and the required QA forms.

§ 2.3.7, the graded changes: *"Pen and ink changes [...] for minor administrative changes that do not
change the scope or intent of the FWP"*; a *"Rework addendum [...] may be used in lieu of a revision
when rework is required and the scope of the original work will not be changed"*; *"Revisions are
any change to a CWP, FWP or TWD that meets the criteria"* — *"(1) Scope of the work changes [...] (2)
Boundary of the work changes [...] (3) Change in test requirements unless authorized by a Departure
from Specification"* — where *"Work must stop immediately"* and *"A revision, as a minimum, must be
approved by the same level of personnel who approved the original FWP"*; an *attachment* for
unexpected added work within the boundary; a *supplement*, *"another stand-alone FWP"*; *voiding*
with *"traceability to the replacement"*. Closeout verifies, among seven attributes, *"Equipment and
systems were restored to normal conditions and configurations."* Revisions *"will be entered into the
body of the original FWP"* and pages with signatures or recorded data are never removed.

Against gzkit canon, read: RO-5 ruling 1, *"A repair order is a work package (selection "A"): one
work-package record with `kind: delivery | repair`"*; Part 0, *"the term "work order" was retired on
2026-10-16 (verbatim: 'retire it, work package everywhere')"*; the doctrine, *"the Release Package
is the set of work packages"*.

## decision · the vocabulary matrix is rebuilt from a deep read before any further term is ruled

Ruled. After question 24 was put (work package = formal work package + controlled record), the
operator stopped the run: *"hold on, if you are not carefully reading this stuff, then we are flying
in circles. I think you need to take some time, do a deep dive, and come up with a matrix that favors
the more formal naval/aviation terms - the literature on them, even if we are taking liberties here,
would be richer than our vibing."* Question 24 is withdrawn, not answered; it is put again from the
matrix.

Four research tracks commissioned 2026-10-25, each a verbatim inventory (every role, document,
record, state and act, with its defining sentence quoted and its section cited), landing under
`docs/rnd/contractor-kit/sources/`: `inventory-navy-tum.md` (the Tag-Out User's Manual, whole),
`inventory-navy-jfmm-v5.md` (JFMM Volume V Part I chapters 1–3, 8–10), `inventory-aviation-civil.md`
(14 CFR 43, 121; AC 120-16G; AC 43-9D; the problem-report circulars), `inventory-maritime.md`
(46 CFR 71; DFARS 252.217; 29 CFR 1915.89 and § 1915.80). The agent verifies every quote against its
source before it enters the matrix, and reads the gzkit side in full (the requirements model, RO-5,
Part 0, the doctrine, the contract). The NAMP (COMNAVAIRFORINST 4790.2E) is still missing: the file
placed is its release letter, an image without text; the operator is asked for Appendix A and
Chapters 5 and 7. The PDFs the operator placed are kept out of git by
`docs/rnd/contractor-kit/sources/.gitignore` (12 MB of binaries); their verbatim extracts are
committed. Operator, while the tracks ran: *"if you only extracted text from limited aspects,
consider a wider read."* The JFMM track was widened to all of Volume V, Parts I to III; the TUM track
already reads the whole manual; the next session checks each inventory's read/skipped header against
this instruction and widens any track that read narrowly. Session handoff written at this point for a fresh context window (operator: *"set this to a
handoff, so we can get a fresh ctx window"*; *"handoff + git sync"*).

## decision · the run resumes: verify the inventories, then build the matrix

Ruled, on resuming `.gzkit/handoffs/20261025T220051Z-rnd-contractor-kit-deep-dive.md`. Facts put:
all four inventories landed and are committed (`cec73faf8` to `affa8fb25`), and none of their quotes
had been checked. Question: proceed with the handoff's steps 2 (verify every inventory quote against
its source, then read the gzkit side in full) and 3 (build the matrix)? Operator: *"proceed with 2,
then 3"*. Booked with `gz handoff decide` (session `7e48b285`). The first step, re-run any track that
did not land, was set aside because there was nothing left to do. Four independent verifiers, one per
inventory, check every quote against the PDF extractions (`pdftotext -layout`) and the repository
sources. Their reports are inputs, and the agent checks their failure tables itself before any row
enters the matrix.

## source · the operator on the pipeline and the GHI system, while the verifiers ran

Operator, 2026-10-25, verbatim:

> btw, with that matrix, and all you've read, we should be able to put together a modified pipeline
> process WITH EASE. I think the GHI system could benefit more from this mx-oriented too.

Two subjects, neither ruled yet. The first is a modified pipeline process built from the matrix. It
bears on question 8, which ruled *"repair first, then reuse unchanged"*, and on the decision that
*lessons cross between the kit and the pipeline in both directions*, each as a GHI on the receiving
side. The second is the GHI system made maintenance-oriented. Part 0's candidate glossary already
maps GHI → *problem report* (sourced: AC 00-71, AC 20-189, four states and four classes) and keeps
*squawk* as the operator's own word. The doctrine already couples GitHub issues to maintenance mode
(*"I'd like maintenance mode and GitHub issues to be very tightly coupled"*). Both subjects join the
frontier after the matrix. Neither is put as a question before the matrix is presented.

## source · the four inventories, verified

Four independent verifier subagents each checked every quoted string in one inventory against its
source: `pdftotext -layout` extractions of the TUM and JFMM PDFs, and the repository files for the
aviation and maritime texts. The maritime verifier also re-fetched the six eCFR files from the
versioner API. The reports are saved verbatim, with host paths made relative:
`docs/rnd/contractor-kit/sources/verify-inventory-tum.md`, `verify-inventory-jfmm5.md`,
`verify-inventory-aviation.md` and `verify-inventory-maritime.md`. Read 2026-10-25.

| Inventory | Quotes | Verbatim | Misquote | Cut that changes meaning | Misstated `[reading]` |
|---|---|---|---|---|---|
| TUM | 419 | 419 | 0 | 10 (6 material) | 0 |
| JFMM Vol V | 626 | 623 | 3 | 36 (14 high) | 3 |
| Civil aviation | 205 | 205 (41 second-hand) | 0 | 6 | 4 |
| Maritime | 179 | 179 | 0 | 3 | 2 |

No quote sits in the wrong section, and the six eCFR files match a fresh fetch word for word. Against
the source text, the agent checked § 43.9(a), § 121.378(a), § 91.407(b), § 121.369(b)(8),
§ 1915.80(b)(15), TUM 1.5.1.c, 1.8.4.a and LIRS block 7, and JFMM I-FWD 1.2.a and I-2.3.7.4. Each
finding held. **What moves:** the cuts are condition and scope. An inventory row is not quoted into
the matrix as-is: each matrix cell is checked again against the source by the agent, and the
condition is restored where a cut dropped it. Two readings bear on the design. § 121.369(b)(8) lets
two classes, not one, countermand an inspector. JFMM I-5.4.3 uses *verification* for the inspector's
act as well, so the (V)/(I) split is a margin convention, not a definition.

## source · the vocabulary matrix

`docs/rnd/contractor-kit/vocabulary-matrix.md` · drafted by the agent 2026-10-25 from the four
verified inventories and the gzkit side read in full. The gzkit side is the requirements model,
the RO-5 specification, Part 0's statement of command, terms and candidate glossary, the
safe-mode doctrine, and the contract's binding sections and punch list. The contract's passage log
was read in preview only, and its superseded record was not read. The matrix is a view and holds no
authority. It has 34 rows in three bands: positions, documents and records, states and acts. Every
cell quote was checked by the agent: 172 strings, 166 matched by script and 6 confirmed by hand.
Rows marked *contested* are put to the operator one at a time under the scoped-register ruling.
Four findings move earlier entries, each as a proposal until ruled:

1. The Navy text has a term for the repairer, *Repair Activity* (TUM App B), which corrects the
   run's *"no text term"*.
2. The Navy gives restoration to Ship's Force (TUM 1.3.1.d), not to a repair activity. JFMM I-13.2.c
   grounds the restorer's separation: reconnection by *"a worker who was not involved in the
   disconnection"*.
3. JFMM's Formal Work Package carries an initial-conditions section (tag-outs), a test and
   inspection section, and a system restoration section. *Job order* (DFARS) is a priced contract.
4. JFMM's change ladder keeps a revision, which changes the work, apart from a Departure from
   Specification, which accepts a result. Both are apart from the record of the work.

## decision · a work package bundles its formal work package and its objective quality evidence

Ruled; question 24, put again from the matrix (rows B2 to B5). Both sides were read in full:

- gzkit: RO-5 ruling 1, *"A repair order is a work package"*; the requirements model, *"the frozen
  REQ baseline, the closing test, the task cards"*.
- JFMM I-2.2.3: an FWP *"coordinates in a single document materials required, initial conditions,
  MP, test and inspections, and system restoration"*. JFMM I-2.2.4: a CWP is required *"when higher
  authority requires a record (Objective Quality Evidence (OQE))"*.

The options put:

- **A.** The work package is the bundle, for both kinds. It holds its formal work package (initial
  conditions as tag-out line items, the procedure as task cards, test and inspection holding the
  baseline, the closing test and the dock trial, and system restoration) and its objective quality
  evidence. Sections that do not apply are marked NA.
- **B.** RO-5's record as specified, with the JFMM terms as crosswalk notes.
- **C.** Job order plus maintenance record.

Recommended A. Operator: *"okay, A. Looking at the matrix, that appears to be the strongest?"*

**Variance found after the ruling, put to the operator.** Option A said that a package closed with
its OQE *"is a controlled work package"*. That misreads JFMM. There the CWP is one of three TWD
types, chosen at planning (I-2 App. B: *"Is a CWP Required per PARA 2.2.4"*), not a state a package
reaches at close. Because gzkit requires the record for every package, the faithful reading is that
every gzkit work package is a controlled work package from the moment it is opened. That is the
liberty already marked at B4. The ruling stands on the bundle. The CWP clause waits for the
operator's word on the correction.

**commissions:** 4 — the RO-5 specification amended so the work-package record carries initial
conditions, procedure (task cards), test and inspection, system restoration and its OQE, on the
operator's go for that row.

## decision · every work package is a controlled work package from opening

Ruled; corrects the clause held in the decision above. Operator: *"yes to your correction"*. Every
gzkit work package is planned and opened as a controlled work package (*"CWP = FWP + OQE"*, JFMM
I-2 App. B), because gzkit requires the record for every package. It does not become one at close.
This is the liberty marked at matrix row B4: JFMM requires a CWP only *"when higher authority
requires a record"*.

The operator corrected the agent's red flag in the same message: *"I have provided commentary and
even extension in times where I took your suggestions."* The record bears it out. The coordinator
began as the operator's extension (*"an 'orchestrator' that we haven't spoken of yet"*). The two
forms of the sea trial are the operator's (*"Make the two an OR"*). The model-card chore proviso
is the operator's. The flag described the answers as bare acceptances when they were amended
acceptances.

## decision · the change ladder: pen and ink, change order, attachment, supplement

Ruled; matrix row B10. Both sides were read in full:

- gzkit: question 10 (*"changed only by the operator's change order"*; the tranches reordered
  within scope, each revision recorded). The operator: *"change order from dfars is worth mixing
  in"*. The requirements model already uses *revision* for a REQ.
- JFMM I-2.3.7.1 to .6.
- FAR 2.101 and DFARS 252.217-7003(a).

The options put:

- **A.** JFMM's ladder as written.
- **B.** JFMM's ladder, with the rung needing the operator's approval named **change order**:
  - **pen and ink** — administrative changes and resequencing, approved by the coordinator and
    recorded in the package;
  - **change order** — a scope, boundary or test change; work stops; issued only by the operator,
    who approved the original;
  - **attachment** — added work inside the boundary with no new tag-outs, approved by the operator;
  - **supplement** — a new formal work package within the package.

  Under B, work outside the *"general scope"* is a new work package; a change order never changes
  the contract (DFARS 217.7103-6(b)); superseded pages are kept (JFMM I-2.3.7.3.c(2)).
- **C.** Every change a change order.

Recommended B. Operator: *"B avoids collision and fits"*.

Consequences:

- The ladder is the Navy's and one rung's name is DFARS's, a marked liberty. *Revision* stays the
  REQ's word.
- It amends question 10 in name only: the repairer's in-scope reordering is a pen-and-ink change
  recorded in the package.
- It settles matrix row B3 by construction. Question 24 (A) names the package's instructions its
  formal work package, so *job order*, held since question 10, is superseded as gzkit's name and
  stays only as DFARS's term in the crosswalk.

**commissions:** 4 — the ladder in the contractor kit's runtime and in the RO-5 amendment, each rung
a recorded event on the package.

## source · the operator on departure from specification, and JFMM on approved and unapproved change

Matrix row B9 was put (A: adopt the DFS; B: an open problem report; C: no new record). Operator,
before choosing, verbatim:

> in drydock and mx, we are there to modify/remodel as much as return to spec, does dfs feel like
> it fits? is it a repair spec? I suppose these could work in either repair or design/feature work.
> discuss

JFMM Rev D Chg 5 Volume V, read 2026-10-25 in `jfmm5.txt`:

> 8.1.1 Background. Specifications are engineered requirements such as type of materials,
> dimensional clearances, vibration levels, flow rates, and physical arrangement to which ship
> components are purchased, installed, tested, and maintained. [...] There are occasions when the
> applicable specifications cannot be met. In these cases, the nonconformance to specifications is
> controlled with a DFS. (I-8.1.1)

> System Restoration (required element). This section contains those steps necessary to restore the
> system to normal operating status. If the FWP resulted in an approved change to the equipment or
> component configuration (such as the performance of an approved Alteration and Improvement), this
> section must direct the ship to submit a Ship's Configuration Change Report (OPNAV 4790/CK) [...]
> Ensure the requirements contained within Part I Chapter 8 of this volume are followed if the FWP
> resulted in an unapproved change to the equipment or component configuration. (I-2.3.3.1.l)

> Those DFSs for a change in configuration, which NAVSEA accepts as a permanent repair, will be
> maintained in an auditable file by the ship and the ISIC until reflected in ship's selected record
> drawings, data or technical variance documentation. (I-8.3.4.a)

The text answers the question. JFMM separates an **approved change** to the configuration (an
alteration, accounted for by a configuration change report) from an **unapproved change** (a DFS).
A DFS is always measured against the specification the work was approved to meet. It is never
measured against the configuration the work set out to change. 14 CFR draws the same line between
repair and alteration (§ 1.1, *major alteration* and *major repair*). 46 CFR 71.55-1(b) puts the
approval first: *"Drawings of alterations shall be approved before work is started"*.

## decision · alteration and departure from specification, both against the package's own spec

Ruled; matrix row B9, re-put from the source entry above. The options put:

- **A.** Two records, both measured against the package's own approved specification, for repair
  and delivery packages alike:
  - the **alteration** — the planned remodel, approved in the formal work package before work and
    accounted for at close as a **configuration change**: the maintenance record's *reconnected*,
    *replaced* and *retired* lines, with canon and docs updated;
  - the **departure from specification (DFS)** — only where the work cannot meet its own approved
    specification. It is a deviation (before) or a waiver (after), temporary (with a clear-by
    condition) or permanent, approved by the operator alone, and it never changes the work.
- **B.** A DFS for every difference from the prior shape.
- **C.** No DFS.

Recommended A. Operator: *"okay, A is it - make sure the agents/personas/skills are well-versed in
these details"*.

The operator's rider binds the kit's shape: every position and its procedure must carry this
vocabulary. Persona files are capped one by one (question 14). So the vocabulary lives once, in the
crosswalk the scoped-register ruling made canon. Each persona carries only its own position's terms
and stop rules, and the kit's skill points to the crosswalk. Copying the whole matrix into every
persona would breach the cap and create five copies to drift.

**commissions:** 4 — the alteration and DFS records in the contractor kit and the RO-5 amendment;
the crosswalk as the single home of the vocabulary; each kit persona and the kit skill carrying
their position's terms by reference to it, with a witness that each term a persona or skill uses
resolves to a crosswalk row (the operator's rider, verbatim above). Executed in diamond 2, on the
row's go, once the kit is specified.

## source · the operator on persona obligations, the two sides, and the aviation separation

Matrix row A4 was put (A: repair activity for the position, craftsman per session; B: craftsman;
C: keep repairer). Operator, verbatim:

> no, the persona/agent doesn't need the whole matrix, but they need to be clear on their
> expectations and obligations.

> On navy... I guess craftsman could also be the persona? repair activity and restoration/resolution
> activity? it seems like the aviation part doesn't want the person who did the fix to evaluate the
> fix, but that is the inspector. I am not sure.

The first refines the rider. A persona carries its position's expectations and obligations, which
is Part 0's *"Position. An obligation and a role to fulfil it."* It does not carry the vocabulary at
large.

On the second, the sources separate three pairs, each from a different text:

1. **Doer and inspector:** § 121.371(c), *"No person may perform a required inspection if he
   performed the item of work required to be inspected."*; JFMM gl., the QAI inspects *"the work of
   other individuals, not their own work"*. This is the aviation rule, and it binds the inspector,
   as the operator says.
2. **Repair side and restoring side.** No aviation text requires it; the operator ruled it,
   extending the independence principle. The Navy builds it into the organization: the repair
   activity works under tags that Ship's Force issues and clears (TUM 1.3.2.b, *"Is Ship's Force
   except for RA tag-outs per Appendix C"*). *"Ship's Force is responsible for system restoration
   (e.g., valve/switch lineups) after tags are cleared."* (TUM 1.3.1.d). The repair activity may
   be gone by then (*"RA Not Available"*, TUM 1.8.4.a). JFMM I-13.2.c requires a disconnection
   identifiable enough that *"a worker who was not involved in the disconnection will be able to
   reconnect the wires without the need for further information sources"*.
3. **Inspection line and coordinating line:** § 121.365(c), separation *"below the level of
   administrative control"*.

*Restoration activity* and *resolution activity* occur in no source read. The Navy's restoring side
is Ship's Force: *"Ship's Force is ultimately responsible for all work accomplished on board their
ship."* (JFMM I-1.8.a).

## source · the operator: repair and restore as two activities of one craftsman

Rows A4 and A6 were put together (A: repair activity and Ship's Force, two craftsman personas;
B: repair activity and restoration activity; C: keep repairer and restorer). Operator, verbatim,
quoting the agent's line on JFMM I-13.2.c:

> this holds promise - repair and restore are just two activities the craftsman can do (or crew):
> "- JFMM I-13.2.c requires every disconnection to be clear enough that "a worker who was not
> involved in the disconnection" can reconnect it."

This reading conflicts with two booked rulings, quoted here verbatim:

- *"I think these two contractors in repair/restore mode in the hangar/drydock are distinct new
  personas."* (decision · the two contractors are distinct new personas)
- *"that's why I don't want the same agent/persona for the two sides of the work"* (decision · the
  performer of the repair never performs the restoration)

A third ruling rests on them: *each persona is anchored on the failure it resists*, under which the
repairer resists bias toward the present shape and the restorer resists green by the wrong route.
Part 0 carries the shape the operator now reaches for. Crew fill positions (*"Crew. The actor
implementing within the role's bounds and under its auspices."*), and the position carries the
obligation. JFMM I-13.2.c is a legibility requirement whose test case is a worker who did not
disconnect (*"e.g."*). It does not on its own forbid the same worker reconnecting. Separation would
then need a mechanism of its own. Put to the operator.

## decision · one craftsman persona fills two positions: repair and restoration

Ruled; matrix rows A4 and A6. Both rulings in conflict were quoted verbatim before the question was
put (source entry above). The options put:

- **A.** One **craftsman** persona carrying the trade: work to the formal work package, document
  before changing, stop when guidance is *"incorrect, incomplete or unclear"*, mark its own steps
  (V). Two **positions**, **repair** and **restoration**, each with a procedure the runtime serves at
  act entry carrying its obligations and the failure it resists. Repair resists bias toward the
  present shape; restoration resists green by the wrong route. Separation by mechanism: the
  runtime refuses a session that applied a tag-out line item from clearing it, and every line item
  meets the JFMM I-13.2.c standard. The sides keep the Navy's names, **repair activity** and
  **Ship's Force**.
- **B.** Two craftsman personas.
- **C.** One persona and no mechanism.

Recommended A. Operator: *"A"*.

This amends three booked decisions, with the operator's word:

- *the two contractors are distinct new personas* and *three personas* now read three positions
  (repair, restoration, inspection) plus the coordinator, filled by two personas (craftsman,
  inspector) and the coordinator's own.
- *each persona is anchored on the failure it resists* now reads *each position*.
- *the performer of the repair never performs the restoration* stands. It is held at instance
  level by the runtime, as § 121.371(c) holds the inspector at person level.

*Repairer* and *restorer* are retired as role names. *Restoration activity* is not adopted, and
*Ship's Force* is the restoring side.

**commissions:** 4 — the craftsman persona and the two position procedures in the kit; the
runtime's refusal of same-session clearance; the I-13.2.c legibility standard as a line-item check
at application.

## decision · the inspector is the Quality Assurance Inspector

Ruled; matrix row A5. Both sides were read in full:

- gzkit: questions 9 and 13.
- JFMM gl., the QAI inspects *"the work of other individuals, not their own work"*; I-1.6.15 places
  QAIs *"within their respective work centers"*; I-12.4.9 makes coating inspectors *"independent of
  the group, shop or code"*.
- §§ 121.371(c), 121.369(b)(8) and 121.365(c).

The options put:

- **A.** *Quality Assurance Inspector (QAI)*, with the liberty marked: gzkit's QAI is separated from
  the coordinator line under § 121.365(c), not placed in the work center.
- **B.** Plain *inspector*.
- **C.** *Required inspection inspector*.

Recommended A. Operator: *"A"*.

The independence rule is cited from aviation, and the title is the Navy's. With the craftsman and
the Authorizing Officer, the positions now read in one naval register.

## decision · the human is the operator, and always the commander

Ruled; matrix row A1. The options put:

- **A.** *Commanding Officer* inside the hangar.
- **B.** Part 0's captain and commander inside the hangar, with *Commanding Officer* in the
  crosswalk.
- **C.** *Contracting Officer*.

The agent recommended B, having withdrawn its own earlier proposal of A. Operator, verbatim:

> actually, everywhere else, I am the operator and I am assumed to be gov zero (the human). The
> human, in gzkit, is always the commander

Inside the hangar and drydock the human is **the operator**, `g0`, and is always the
**commander**. No maintenance title is adopted for the human. *Commanding Officer* (JFMM, TUM),
*operational commander* (JFMM I-FWD 1.2.c) and *Contracting Officer* (FAR 2.101) are recorded in
the crosswalk as other texts' names for that standing. *Contracting Officer*, held since question
13, is withdrawn. Part 0's *captain* (the signature and the override, *"It is one standing and
does not divide"*) is untouched by this ruling. Matrix row A2's approval for return to service is
the operator's signature.

## decision · the punch list becomes the list of discrepancies

Ruled; matrix row B8. Both sides were read in full:

- gzkit: the contract's § Punch list and question 20; the DFS ruling now takes accepted shortfalls
  off the list.
- § 43.11(b); JFMM QA form 14 and Part III survey-card categories; DFARS 252.217-7013(c).

The options put were A (keep *punch list*), B (*list of discrepancies*) and C (JFMM's discrepancy
record). Operator: *"B and C seem pretty identical"*. The agent named the one difference — whether
every item carries a causal analysis — and the JFMM text that grades it (I-9.3.1.a: minor
deficiencies *"corrected without causal analysis or long-term corrective action unless recurring
in nature"*; I-9.4.1.b(1): certification-affecting deficiencies *"IMMEDIATE CORRECTIVE ACTION"*).
It then put:

- **B′.** A **list of discrepancies**: one line per discrepancy, graded *blocks return to service*
  or *due by a named event*, cleared with its evidence. A line takes the fuller record (root cause
  and corrective action) only when it blocks return to service or recurs, by the threshold in
  `data/recurrence_threshold.json` checked by `gz insights recurrence`. The contract's § Punch list
  is renamed on the operator's word.
- **A.** *Punch list* with the same grading.

Operator: *"B′"*.

**commissions:** 4 — the contract's § Punch list, the contractor brief and the doctrine's references
renamed to the list of discrepancies, with the grading and the causal-analysis rule; the three
records of question 20 now read the tag-out log, the maintenance record and the list of
discrepancies.

## decision · the run resumes a second time: the record checked, the frontier recomputed

Ruled, on resuming `.gzkit/handoffs/20261026T001040Z-rnd-contractor-kit-matrix-ruled.md`. The
handoff advised five steps. Operator: *"step 1"*. Booked with `gz handoff decide` (session
`15ccb03e`), and steps 2 to 5 were set aside for now. Step 1 is three acts: this entry, the check
against git, and a fresh frontier.

**Record against git, 2026-10-26.** The record and `docs/rnd/contractor-kit/` have no uncommitted
changes, and HEAD (`69fb6e879`) is the handoff's own landing. `git cat-file` resolves every
nine-character commit hash this record cites, among them `cec73faf8` to `affa8fb25`, `5661474e3` and
`9649d0eb0`. Every source file named in the record exists. The matrix's § Rows the operator rules
singly shows all eight rows struck through, and each matches a `decision` entry above.

**One carried order is still open.** The deep-dive handoff entry ordered: *"the next session checks
each inventory's read/skipped header against this instruction and widens any track that read
narrowly."* No entry records that check. The TUM inventory names Appendices E, G and L as skipped,
with reasons. The JFMM inventory names Part I Ch. 4 as skipped, with a reason. The maritime
inventory has no skipped header. The aviation inventory's § Not read lists texts that no
repository file holds, and the rows that depend on them are marked as gaps: Part 65, Part 145
(U.S.), § 119.65, § 121.628, § 91.213, § 121.363, § 121.368, § 121.375, § 121.377, § 121.380a,
§ 91.405, § 91.409, § 91.417, and Part 43 Appendices A, B and D. This is fact work, so the
operator is not asked to rule on it. It goes on the frontier because no matrix row may lean on a
gap row until the gap is read or the row says it is a gap.

**Frontier, recomputed from the subject** (the core model first; placement waits):

1. **The coordinator's authority** (A3, held provisional) together with **A8, a stop requested
   from outside the work chain**. Every position is now ruled, so every prerequisite is settled.
   The rest of C4 (stop work) and the scope of C6 depend on this ruling.
2. **A7, the affected party.** Held and sourced, but not yet ruled.
3. **The rows still proposed:** B1 (the contract as the rule), B11 (the register as a Layer 3
   view), C1 (commencement), C3 (self-check and independent check: a margin convention, per the
   JFMM I-5.4.3 reading), C5 (rework and buy-back), C10 (package closeout, which collides with
   `gz closeout`), C11 (handing a position to the next session), C12 (the form of the handback),
   and C13 (the drydock session has no definition).
4. **The two subjects the operator opened.** B12 (GHI → *problem report*) carries the GHI system.
   The modified pipeline process is bounded by question 8 and by the both-directions lessons
   decision. Each comes after the rows it builds on.
5. **The widening check** above, done as fact work before any gap row is cited.
6. **Placement and close:** the kit's RO number and its place in the register, the shape of the
   vibe-coded audit chore, disposition rows 1, 5 and 6, the restated challenge, `review.md`, and
   sign-off.

The earlier handoff's list of open items was an input to this, not the frontier. The new items it
missed are A7, the still-proposed rows (3) and the widening check (5).

## source · surveillance: who watches work from outside the chain, and what a stop request binds

Read in full on 2026-10-26 for matrix row A8. The JFMM and TUM text comes from fresh
`pdftotext -layout` extractions of `Volume_V_D5.pdf` and `TUM_REV_8_28Oct20.pdf`.

JFMM Vol V Part I, Chapter 9 and Appendix C:

> 9.2.2 Surveillance. Surveillance involves observation of actual work in progress or specific
> areas of concern. (I-9.2.2)

> In-Process Surveillance — The review of work in progress by personnel not directly involved with
> the work to assess such attributes as tagging and installation of controlled material, compliance
> with technical procedures, and recording of required data. (I-FWD App. A)

> Ship's Force personnel will conduct internal QA Audit and Surveillance as scheduled by the
> Quality Assurance Officer (QAO) as part of the ship's overall monitoring program. (I-9.3.1.a)

> (2) Position yourself so the job can be monitored but not to interfere with individual(s)
> performing the work. (3) [...] In those instances, where a safety issue, incorrect assembly, or
> violation of a technical requirement critical to the job is noted, identify this to the
> individuals performing the job and request they stop until the problem can be resolved.
> (I-9 App. C ¶ 2.d(2)–(3))

> (5) Once the surveillance is completed, inform the individuals performing the job of any
> violations or comments noted during the surveillance. Findings will also be discussed with
> appropriate supervisor. (6) Write up surveillance findings and provide them to the QAO with copy
> to the division officer in charge of the work surveyed. (I-9 App. C ¶ 2.d(5)–(6))

TUM 1.7.6: *"The Shipyard/RMC will establish a process that reviews the tag-out log and ensures
proper posted tag checks. The goal of the monitoring is to provide timely data on tag-out
performance so emerging adverse trends can be quickly addressed. Any deficiencies found during the
monitoring shall be recorded by date, description, and signature entry in a formal Shipyard/RMC
document per local guidance."*

29 CFR 1915.89(q)(2): the audit is performed by *"(i) An authorized employee other than the one(s)
currently using the energy-control procedure being reviewed; or (ii) Individuals other than an
authorized employee who are knowledgeable about the employer's lockout/tags-plus program"*.
§ 121.373(a) (CASS) asks for *"a system for the continuing analysis and surveillance of the
performance and effectiveness of its inspection program"*. That is program-level surveillance, not
watching a job while it is under way.

**What the texts agree on.** The surveillant is not part of the work, and is scheduled by the
quality side (the QAO), not by the person running the work. It observes without interfering. It
**requests** a stop, and only on three named triggers. Its findings go up the quality line, with a
copy to the person in charge of the work. No text gives it the power to order a stop.

**The gzkit side, read 2026-10-26.** No position watches work in progress from outside the chain.
The inspector is dispatched by the runtime at set points (the decision above, *the coordinator is
the operator-facing session*). Its job is acceptance, not watching the work as it happens. The
nearest built design is the cross-family critic (`ADR-0.36.0`, `Proposed`, nothing landed; campaign
§ Movement A item 2). It is a skill with three doors (operator, agent, gate), and its verdict
reaches the operator unedited. It challenges decisions and scope, not work in progress. The
contractor brief's stops are all self-stops: *"Stop and wait for the operator"*. Under the
provisional A, the coordinator *"cannot direct, override or filter the inspector"*, and nothing is
said about a surveillant.

## decision · surveillance: a stop request from outside the chain becomes a runtime hold

Ruled; matrix row A8. Both sides were read in full (the source entry above). Question: who may
stop work from outside the work chain? Options put:

- **A.** A surveillance position, filled by any session outside the work chain and dispatched by
  the operator, never by the coordinator; the cross-family critic is a later candidate. On one of
  JFMM's three triggers (a safety issue, incorrect assembly, a violation of a technical requirement
  critical to the job), it writes a stop request to the tag-out log. The runtime then holds that
  surface (no further application, landing or clearing) until the coordinator records a resolution
  with evidence. The finding reaches the operator unedited. The coordinator cannot dismiss it
  without a resolution; only the operator lifts it without one.
- **B.** The same position, reporting only: no hold, and the operator decides.
- **C.** No surveillance position, recorded as not pursued.

Recommended A. Operator selected **"A: request becomes hold (Recommended)"**.

**Liberty, recorded.** In JFMM the surveillant *requests* a stop (I-9 App. C ¶ 2.d(3)), and here
the runtime makes it a hold. In gzkit, a request kept only by persona discipline would be honored,
if at all, by the coordinator, and the coordinator is the session being watched. The three
triggers are JFMM's own and keep the hold narrow. Dispatch by the operator, not the coordinator,
follows I-9.3.1.a (*"as scheduled by the Quality Assurance Officer"*): the quality line, not the
work line, schedules surveillance. The term is the text's own: **surveillance**, and the one who
performs it is the **surveillant**.

**commissions:** 4 — the kit gains the surveillance position: its persona obligations, the
operator-only dispatch, the stop request as a tag-out log line, the runtime hold and its two lifts
(the coordinator's resolution with evidence, or the operator).

## decision · the coordinator's authority, booked

Ruled; matrix row A3. This closes the provisional entry *the coordinator's authority — provisional*
(*"Provisionally, I accept A, but let's delve."*). The delve settled three things:

- the mechanics (*the coordinator is the operator-facing session; the inspector routes around it
  through the runtime*);
- overlapping work (*one lockout per surface; the coordinator sequences overlaps*);
- surveillance (the A8 decision above).

The change ladder had already given the coordinator pen-and-ink approval. Question: book A as the
rulings since have filled it in, or keep it provisional and name what still needs delving? The A
put:

- **The coordinator holds:** dispatching repairers (more than one only on disjoint surfaces) and
  restorers; sequencing overlapping work packages; the Authorizing Officer duty on the tag-out log
  (approving application, the isolation check and removal against the written procedure); approving
  pen-and-ink changes; requesting an inspection, whose dispatch the runtime composes; and being the
  single writer that lands work on main.
- **The coordinator may not:** issue a change order (it may propose one); direct, override or
  filter the inspector; dispatch surveillance, or dismiss a surveillance hold without a recorded
  resolution; or approve return to service.
- **The operator keeps the strategic level:** change orders, return to service (Gate 5),
  countermanding the inspector, dispatching surveillance, and lifting a hold without a resolution.

Recommended booking A. Operator selected **"Book A as stated (Recommended)"**. The liberty stays as
matrix row A3 records it: the coordinator joins the Navy's two sides, Ship's Force issuing tags and
the repair activity working under them.

**commissions:** 4 — the coordinator's persona obligations and the runtime's refusals, as listed
above.

## source · every stop-work trigger in the texts

Read on 2026-10-26 for matrix row C4, from fresh extractions. JFMM Vol V was searched for
*stop*, *cease* and *halt*, and every hit was read in context. TUM was searched the same way.

- JFMM I-1.6.11.a, the craftsman: *"Perform all maintenance actions following the approved
  procedure. If that guidance is either incorrect, incomplete or unclear, stop and seek
  clarification from the work center or shift supervisor."*
- JFMM I-2.3.7.2.a, rework: *"The craftsman doing the work must stop the work and notify the LPO or
  Work Center Supervisor (WCS) that rework is required."* Under I-2.3.7.2.d a rework addendum is
  *"approved by the Division Officer"*, and *"Any additional actions that were not included in
  the originally approved CWP or FWP constitute a change in scope or work boundaries and must be
  issued as a revision"*.
- JFMM I-2.3.7.3.b(1), revision (a change of scope, boundary or test, I-2.3.7.3.a): *"Work must
  stop immediately and the LPO or WCS must be notified when the need for a revision is
  identified."*
- JFMM Part I Ch. 2 QA form instructions, the electroplating block: *"IF THE APPLIED PLATING
  THICKNESS IS BEYOND THE MAXIMUM ALLOWED OR NOT WITHIN THE SPECIFIED RANGE, STOP WORK AND OBTAIN
  FURTHER TECHNICAL DIRECTION."* This is the one instance in the text of a measured result outside
  its specification.
- JFMM I-9 App. C ¶ 2.d(3), surveillance: quoted in the source entry above, and ruled as a hold.
- JFMM I-1.6.15.k, the QAI: *"Ensure the deficiency is resolved before work continues."*
- TUM 1.8.5.b(1) and (2): when clearing would reposition an item with more than one tag, or the item
  is found out of its expected position, *"all efforts to remove the tag shall be stopped"* /
  *"all tag removal/restoration efforts for the items shall be stopped. The discrepancy shall be
  reported immediately to the Authorizing Officer and RA Representative."*

**What the texts agree on.** The person doing the work stops. The stop goes to whoever holds the
authority to resolve that kind of trigger: the supervisor for an unclear procedure or rework, the
revision chain for scope, boundary or test, technical direction for a result outside its
specification, and the Authorizing Officer for a tag discrepancy. The work stays stopped until
that authority resolves it.

**The gzkit side.** The contractor brief lists self-stops to the operator, *"one question at a
time, with a recommendation"*: every structural question a specification does not answer, every
binding loss, the named batch rulings, and *"anything that would delete data, rewrite history or
force-push."* The run has already ruled: tag-out clearing (TUM 1.8.5.b(2), the restorer's rule);
change orders as the operator's alone, with work stopping (the change ladder); departure from
specification (B9); a surveillance hold (A8); and acceptance or rejection as the inspector's alone,
countermanded only by the operator (C6).

## decision · a stop is a recorded event, routed by its trigger to the one who can resolve it

Ruled; matrix row C4. Both sides were read in full (the source entry above). Options put:

- **A.** A stop is a recorded event on the work package, carrying a trigger from a closed list.
  The runtime refuses to land anything on that package until the named resolver records a
  resolution. Routing:
  - to the **coordinator**: an incorrect, incomplete or unclear procedure (I-1.6.11.a), cleared as
    a pen-and-ink change or escalated; rework inside scope (I-2.3.7.2); a tag discrepancy, as
    Authorizing Officer (TUM 1.8.5.b);
  - to the **operator**: a change of scope, boundary or test (I-2.3.7.3, a change order); a result
    outside its specification (a departure from specification or a change order); and the
    contractor brief's deletion, history-rewrite and force-push stops;
  - a surveillance hold (A8) and an inspector's deficiency (I-1.6.15.k, C6) follow their own
    rulings.
- **B.** The same record and hold, with every trigger going to the operator.
- **C.** Triggers and routing as persona obligations only.

Recommended A. Operator selected **"A: routed by trigger (Recommended)"**.

The routing follows the texts' own split: the supervisor clears clarification and rework, the
revision chain handles scope, and the Authorizing Officer handles tags. Each text authority maps to
the gzkit position the run has already ruled. The term is the text's own: **stop work**.

**commissions:** 4 — the closed trigger list, the stop as a package event, the runtime's refusal
to land on a stopped package, and each trigger's resolver, in the kit's runtime and the persona
obligations.

## decision · the questions are the right ones

The operator took the recommended option on every question this session (A8, A3, C4). As this
skill's red flags require, the agent said so and asked whether the questions are the right ones.
Operator: *"questions are fine"*.

## source · the affected employee

Read in full on 2026-10-26 for matrix row A7.

29 CFR 1915.80(b)(2), `docs/rnd/contractor-kit/sources/osha-1915-80-definitions.md`:

> Affected employee. An employee who normally operates or uses the machinery, equipment, or system
> that is going to be serviced under lockout/tags-plus or who is working in the area where servicing
> is being performed under lockout/tags-plus. An affected employee becomes an authorized employee
> when the employer assigns the employee to service any machine, equipment, or system under a
> lockout/tags-plus application.

29 CFR 1915.89, `docs/rnd/contractor-kit/sources/ship-repair.md`:

- before shutdown, *"(ii) Notify each affected employee that the machinery, equipment, or system
  will be shut down and deenergized prior to servicing, and that a lockout/tags-plus system will be
  implemented."*;
- before removal, the authorized employee *"(i) Notifies all other authorized and affected employees
  that the lockout/tags-plus system will be removed"* (§ 1915.89(i)(1));
- training, (o)(3): *"(ii) That affected employees are not to apply or remove any lockout/tags-plus
  system; and (iii) That affected employees are not to bypass, ignore, or otherwise defeat any
  lockout/tags-plus system."*

The Navy has the rule but no role name. TUM 1.7.3.a: *"Never remove or operate a danger-tagged
component."* TUM 1.3.3.c(1)(f), to a contractor: *"does not remove existing tags or take any action
that changes the position of tagged components"*.

**A defect in the matrix, found on this read.** Row A7 calls *affected party* *"OSHA's term"*.
OSHA's term is ***affected employee***. *Affected party* departs from the text, and the
departure was never recorded. The *text's own term* decision requires that record. The role-terms
source entry says *"The section's definitions (§ 1915.80) were not fetched; unread"*. They were
fetched later (`osha-1915-80-definitions.md`), so that statement is out of date, and this entry
supersedes it.

**The gzkit side.** No position or rule covers a session that is not dispatched to a work package.
The nearest mechanisms are OBPI locks and the session orientation's *Active OBPI claims*, which
announce a claim but refuse nothing to another session. The coordinator is the single writer that
lands work on main (A3).

## decision · the affected parties, named by the operator

Ruled; matrix row A7, the *who*. The agent drafted a question that defined the affected party as
every session not dispatched to a line item, with the operator excluded. The operator stopped the
question to clarify, and stated the definition:

> affected parties aee: the operator, plus all gzkit (or adopting system's) agents, control surfaces
> and rules designed to enforce system behavior, and, when applicable, all end users of an adopting
> system.

(*"aee"* is kept as typed; read as *are*.)

This takes OSHA's own test, not the agent's. In 1915.80(b)(2) an affected employee is one who
*"normally operates or uses"* the system under service. That is a party affected by the servicing,
not a party shut out of the work. The agent's draft had confused the two. Four classes:

1. **the operator**: affected as well as commander;
2. **every agent** of gzkit or of an adopting system;
3. **the control surfaces and rules designed to enforce system behavior**, which are exactly what a
   drydock unplugs, dismantles or modifies;
4. **when applicable, every end user of an adopting system**, reached through what gzkit ships.

What each class is owed (notification, the bar on applying, removing or bypassing) is the next
question. The term *affected party* is held; recording its departure from OSHA's *affected
employee* is part of that question.

## source · the operator: the controls carry their own contract for the mode signals

The agent put the next question: what each class is owed. Option A was notice by channel (the
tag-out log, the orientation, a demoted guard announcing itself, the handback's release notes)
plus the bar on applying, removing or bypassing. Option B was notice to people only. The operator
stopped it to clarify, 2026-10-26, verbatim:

> this is reaaly design by contract - the controls, monitors, alarms, and safeguards each needs to
> understsnd what a safemode, standby, lockout singal is and adjust internal behavior, knowing how to
> bypass and how to restore. the reparing craftsman must adjust these in cases of profound
> modification.

(Spelling kept as typed.) This is the operator's earlier doctrine, now applied to the controls.
`docs/rnd/renewing-vows.md` § *the constraints sortie is a Design act* quotes it: *"these are the
prior contracts and understandings of the system (Design by Contract) - these are invariants and
other constraints that the model must obey"*.

**The gzkit side, read 2026-10-26.** Today no guard understands a mode signal. One external
checkpoint (`gzkit.mx.checkpoint`, wired for the pre-commit guards in `src/gzkit/hooks/guards.py`)
resolves each registered guard's level. While the hangar is open it demotes the guard to advisory
and prints `demote_notice`. It cannot demote anything in the `GATE5_INVARIANTS` floor
(`src/gzkit/mx/invariants.py`). The guard does not know it has been demoted. A guard the checkpoint
does not wrap does not change at all. There is one signal (the hangar open, with safe mode as a
mode of it), no *standby*, and no lockout scoped to a surface. The nearest declared fragment of a
contract is `@enforces(..., exempts=...)` (`src/gzkit/enforcement.py`): each enforcement claim
declares its exemption surface, *"DECLARED, not inferred"* (GHI #728, #797). That covers the
exemption half and nothing about a mode.

**Sources this principle calls for, not yet read.** Each is a hypothesis until read, and none
commissions anything.

- **The Minimum Equipment List**, 14 CFR § 91.213 and § 121.628. It is the aviation text's model
  of a system operated with an item inoperative, with a maintenance procedure to deactivate the
  item and an operations procedure to run without it. Both sections are on the aviation
  inventory's § Not read list, so the widening check above now carries weight.
- **Design by Contract's primary text** (Meyer). Gzkit holds only secondary citations
  (`ADR-pool.agent-reliability-framework.md` links a Wikipedia article).
- ***Standby*** is the operator's word. No source read so far uses it as a mode signal.

## decision · every control carries a mode contract; the repairing craftsman amends it

Ruled in principle by the operator's words above; matrix row A7 (the *what is owed*). This
replaces the agent's notice-by-channel option: notice is not enough. Each control, monitor, alarm
and safeguard (affected-party class 3) carries its own contract for the mode signals: **safe mode,
standby, lockout**. On each signal it adjusts its own behavior. Its contract states how it is
bypassed and how it is restored. Where a repair modifies a control profoundly, the **repairing
craftsman** amends that control's contract as part of the repair.

What this departs from in gzkit: the external checkpoint that demotes guards that do not know they
are demoted. What stays open until the sources above are read: the contract's shape (its clauses,
and whether it maps to the MEL's deactivate-and-operate pair), what each signal means, the
threshold for *profound modification*, and what classes 1, 2 and 4 are owed.

Two background research tracks were dispatched on 2026-10-26 to land the sources verbatim under
`docs/rnd/contractor-kit/sources/`: the aviation gap texts with the MEL (the carried widening
check), and Meyer's primary text on Design by Contract. Their reports are inputs, read by the
agent before any mapping.

## decision · the mode contract is a massive refactor, and the operator judges it the best way

Operator, 2026-10-26, verbatim, on the principle above:

> yes, that will be a MASSIVE refactor, but it is the best way that I can see.

This places the mode contract in **disposition 5, one-shot refactoring**. Every control, monitor,
alarm and safeguard gzkit carries would gain its own contract, and the external demotion checkpoint
would give way to controls that read the signal themselves. That is the one entry row 5 has had.
Row 5 is still open: this skill lets the agent propose a program and leaves the route to the
operator. The program can be proposed only after the contract's shape is decided from the sources.
The operator's words settle that the refactor is wanted. They do not settle its route.

## source · the operator: the mode is honored at the place of call

Operator, 2026-10-26, verbatim (dictated):

> Here's the thing. If we are clever about it, we really just perhaps have an on-off switch for a
> lot of these. So this really depends on how these are called. And this is an architectural
> matter. If we really did have better hexagonal architecture, then how these things are called
> would have been through ports and adapters. But nonetheless, this is probably a very significant
> refactor, but I don't see how else we would have affected parties and notification. They're not
> intelligent where they can stop what they're doing. So we have to bake in safe mode at the places
> of call, right? Where the behaviors need to be suspended or modified.

**The gzkit side, read in full 2026-10-26.**

- `.gzkit/rules/hexagonal-architecture.md` (canon: `docs/governance/hexagonal-architecture.md`)
  makes ports and adapters gzkit's *"primary code-architecture directive"*. Its operative rules
  are about **external technology**: *"Every external dependency is confined to an adapter behind
  a port"*. Rule 5: *"formalize the port when the SECOND adapter is real"*. Rule 7: *"do NOT add
  `domain/`/`application/`/`adapters/`/`contexts/` folder partitions"*, because hexagonal *"governs
  the boundary, not internal layout"*. No rule governs how a control (a guard, hook or validator) is
  called.
- `src/gzkit/mx/checkpoint.py` is already a switch at the place of call, for one signal: *"the
  single place code reads the marker and resolves guard severity [...] A new guard inherits the
  checkpoint for free; nobody can forget to wire it, and the never-relax list lives in exactly one
  place"* (ADR-0.0.74 Decision item #2). `resolve(guard_name, emitted_level)` pins
  `GATE5_INVARIANTS` to CRITICAL and otherwise demotes to ADVISORY while the marker is open. It is
  imported from the pre-commit guards (`hooks/guards.py`), the routing hook, `validate_cmd`,
  `quality` and three rendition trust audits. Not yet measured: how many of gzkit's controls are
  called through it, against how many exist.

## decision · the mode contract is honored at the place of call, not inside the control

Ruled in principle; this **corrects** the entry *every control carries a mode contract; the
repairing craftsman amends it*. That entry said each control *"adjusts its own behavior"*. The
operator: *"They're not intelligent where they can stop what they're doing. So we have to bake in
safe mode at the places of call"*. Restated:

- Each control's **contract is declared**: what it does under safe mode, standby and lockout, how
  it is bypassed and how it is restored. For many controls the contract is just an **on-off
  switch**: *"we really just perhaps have an on-off switch for a lot of these"*.
- The contract is **honored at the place of call**, where the behavior is suspended or modified.
  The control itself does not read the signal.
- In a strong hexagonal shape, that place of call is a **port**. Today the one such switch is the
  MX checkpoint, which knows one signal (the marker open) and one adjustment (demote to advisory).
- The repairing craftsman still amends a control's declared contract on profound modification.

The refactor in disposition 5 is therefore the place-of-call work. It finds every place a control
is called, routes each through a port that reads the mode signal, and widens the signal from one
marker to safe mode, standby and a lockout scoped to a surface. This is the operator's reason
it is the only route to the affected parties and their notification (*"I don't see how else we would
have affected parties and notification"*). The census of places of call is fact work, owed before
the program is proposed. The airlock's seam map (`gz airlock in`) is a candidate instrument for it.
That is a hypothesis, not yet checked against what the seam map holds.

## source · the Minimum Equipment List, Meyer on assertion monitoring, and the aviation widening

Landed on 2026-10-26 by two background research tracks. Each file is saved verbatim under
`docs/rnd/contractor-kit/sources/` with its provenance header. The agent checked a sample of each
against the source before reading it in full:

- `14cfr91-213-121-628-mel.md`: §§ 91.213 and 121.628 in full. The agent re-fetched § 91.213 from the
  eCFR versioner API, and three quotes matched.
- `faa-mel-guidance-ac91-67-n8900-748.md`: AC 91-67 (6/28/91) ¶¶ 1–8, 13–14, 19–23, and N 8900.748
  ¶¶ 1–7 with Appendices A and E. The research track typed AC 91-67 from page images, because its
  OCR layer is unreliable. The agent re-downloaded the PDF (SHA-256 matches the header), rendered
  page 10, and found ¶ 7b(1), 7b(2) and 7c word for word. **Not retrieved:** FAA Order 8900.1
  Vol. 4 Ch. 4 and MMEL policy letters PL-25, PL-34 and PL-36 (`fsims.faa.gov` no longer resolves;
  `drs.faa.gov` serves only a JavaScript shell). The repair categories A–D are therefore unread.
- `meyer-design-by-contract.md`: about 35 quoted passages from eiffel.org and eiffel.com, excerpts
  and not full text. Only I2E names Meyer as author. The others are attributed to Eiffel Software.
  The agent re-fetched ET and I2E, and four quotes matched. An earlier attempt failed on a
  content-filter error while transcribing the 1992 IEEE paper from page images, and it wrote
  nothing.
- **The widening check is discharged.** `14cfr91-119-121-maintenance-gaps.md`,
  `14cfr-part65-145-gaps.md` and `14cfr43-appendices.md` land every text that the aviation
  inventory's § Not read listed, except the Part 135 counterparts, § 119.67 and Part 43 Appendices C,
  E and F. The matrix rows marked as gaps on these texts must be re-checked against them before the
  review.

The passages the mode contract rests on:

- § 91.213(a)(3): the approved MEL must *"(ii) Provide for the operation of the aircraft with the
  instruments and equipment in an inoperable condition."* § 91.213(b): items that *"may not be
  included in a Minimum Equipment List"*, among them those *"essential for safe operations under
  all operating conditions"*.
- AC 91-67 ¶ 20f(2)(v): *"all items related to the airworthiness of the aircraft that are not
  included on the MMEL must be operative."* ¶ 20f(3): *"If the operator has not yet developed a
  procedure for an item, that item must be operative."*
- AC 91-67 ¶ 6r: (O) and (M) procedures are *"the specific maintenance procedures the operator uses
  to disable or render items of equipment inoperative and to specific operating conditions and
  limitations"*. Under ¶ 6r(2), (M) is *"accomplished before beginning operation with the listed
  item of equipment inoperative"*. Under ¶ 6r(1), (O) is *"accomplished before or during operation"*.
- AC 91-67 ¶ 6g: *"Deactivation means to make a piece of equipment or an instrument unusable to the
  pilot/crew by preventing its operation."* ¶ 6t, the placard: *"visible to the pilot or flightcrew
  and alerts them to the inoperative equipment."* ¶ 7c: *"It also ensures that future flightcrews and
  maintenance personnel are aware of the discrepancy."*
- AC 91-67 ¶ 23d: *"The MEL permits operations with inoperative items of equipment for the minimum
  period of time necessary until the equipment is repaired."* Under ¶ 23d(3), the item is
  inspected or repaired *"at the next 100-hour, annual, progressive, or unscheduled inspection. However,
  if FAR § 91.213 requires that an item be repaired, the item cannot be deferred."*
- AC 91-67 ¶ 20f(2)(i): *"The operator's procedures document may not be less restrictive than the
  MMEL."* ¶ 20f(2)(ix): the procedures document is *"a single procedural reference document"*.
- Meyer (ET, § Run-time assertion monitoring): checking levels set *"separately for each class, with
  defaults at the system and cluster levels"*: *no*, *require*, *ensure*, *invariant*, *all*.
  Enabling or disabling is legitimate because *"for a correct system [...] the compilation option
  makes no difference to the semantics of the system"*. And *"you should always assume -- to avoid
  loosening your guard -- that in the end monitoring will be turned off."* Under SETLVL the level
  takes effect on recompile, and once set it does not change during execution (BLOG reply,
  community material).

**What the two sources agree on, as the agent reads them (to be put, not decided).** The MEL is a
mode contract for a whole aircraft. It is one list of the items that may be inoperative, each with
a procedure to deactivate it (M), a limitation to operate under (O), a placard that tells everyone
who comes after, and a deadline for repair. Anything off the list stays operative, and some items
may never be listed at all. Meyer gives the switch itself: a declared checking level per component,
with defaults at the system and group level, fixed for the length of a run. In gzkit, § 91.213(b)
already has a counterpart: the `GATE5_INVARIANTS` floor.

## decision · the mode contract is a Minimum Equipment List with Meyer's levels

Ruled; matrix row A7 (the *what is owed*), and the shape of the disposition 5 refactor. Both sides
were read in full (the source entry above and the place-of-call entry). Options put:

- **A.** gzkit keeps **one list of controls, its Minimum Equipment List**. Each entry declares:
  - its **level under each signal** (safe mode, standby, lockout), such as on, advisory or off,
    with defaults by mode and by surface (Meyer: *"separately for each class, with defaults at the
    system and cluster levels"*);
  - its **(M) bypass procedure**, performed by the repairing craftsman and recorded on the tag-out
    log;
  - its **(O) limitation**, the condition the system runs under without it;
  - its **placard**, the notice the port gives every affected party at the place of call
    (AC 91-67 ¶ 7c);
  - its **restore condition and deadline**, at the latest the exit re-run (¶ 23d).

  A control not on the list cannot be relaxed (¶ 20f(2)(v), 20f(3)). The floor can never be listed
  (§ 91.213(b), `GATE5_INVARIANTS`). A level is fixed for the length of an act (Meyer; the BLOG
  reply).
- **B.** Meyer's levels only: an on-off switch with defaults, and no procedures, placard or deadline.
- **C.** B for every control, and A only where a repair modifies a control profoundly.

Recommended A. Operator selected **"A: MEL with Meyer levels (Recommended)"**.

**Terms.** *Minimum Equipment List* is the text's term, and gzkit's list takes it. *(M) procedure*,
*(O) procedure*, *placard*, *deactivation* and *inoperative* are AC 91-67's (¶ 6g, 6k, 6r, 6t).
*Level* is Meyer's word for the setting. **Liberties, recorded:** the MEL's items are equipment
and gzkit's are controls. The MEL covers only the takeoff (¶ 23b, *"An MEL applies only to the
takeoff"*), while gzkit's list holds for the length of an act. gzkit's signals are three, safe
mode, standby and lockout, where the MEL has one condition, inoperative. *Standby* is still
unsourced.

**Still open:** where an entry is declared (in a central list, or at the control as `@enforces`
declares `exempts`, with the list a derived view); what *standby* means; the threshold for
*profound modification*; who determines that an inoperative control *"does not constitute a
hazard"* (§ 91.213(d)(4)); and the census of places of call.

**commissions:** 5 — the refactor gives every control an MEL entry and routes each call through a
port that reads it. 4 — the placard as the port's notice to the affected parties, and the (M)
procedure in the craftsman's obligations.

## source · the operator: each surface onboards the contract; only the signal is central

The agent put the next question: where an MEL entry is declared. The options were one JSON list
in `data/`, a decorator at the control, or the JSON list bound by the control. The operator stopped
it to clarify, 2026-10-26, verbatim:

> one json file isn't each surface or actor onboarding the contract - the contract becomes a
> compliance obligation for the surface/actor. these are external signal that require internal
> management - reading a single file for guidance is too brittle or would create a single failure
> point. now, a central file could be the signal itself, but at that stage this could be handled in
> config (which already is a known single point limitation that accepted). config files themselves
> are design by contract. or, a flag at invocation, but that still requires retraining everywhere.
> still, this overarching 'standby' mode seems to be the best comprehensive solution.

**The gzkit side, read 2026-10-26.** The signal is already central. `src/gzkit/mx/marker.py`: *"the
single filesystem truth-source for Maintenance Hangar mode"*, at `.gzkit/mx.json`. It is *"valid only
when bound to a real `mx_session_opened` ledger event"* and imports no gzkit subsystem, so that
*"it opens even when gz's own subsystems are the patient"*. The marker says: *"Every surface — code
guards and agents — reads MX state from here and nowhere else."* Config is `.gzkit.json` and
`.gzkit/manifest.json`.

## decision · the contract is each surface's compliance obligation; the signal alone is central

Ruled in principle from the operator's words above. This **amends** the MEL decision's *"gzkit
keeps one list of controls"*. The entry's contents stand: levels per signal, (M), (O), placard,
restore and deadline. The single authoritative list does not.

- **The contract is onboarded by each surface or actor** as its own compliance obligation. The
  surface manages the external signal internally. No surface reads its guidance from one shared
  file, because that file would be *"too brittle"* and *"a single failure point"*.
- **Only the signal is central.** It lives in config, an already-accepted single point (*"config
  files themselves are design by contract"*). The MX marker is that pattern today, bound to the
  ledger so a hand-made signal is void.
- **A flag at invocation was considered and not taken**: it *"still requires retraining
  everywhere"*.
- **Any list of controls is a derived view** (Layer 3), assembled from what the surfaces declare. By
  the state doctrine's Rule 5, it can never block a gate.

This fits the place-of-call ruling: the place of call is the surface's own entry point, where it
reads the signal and applies its own contract. The operator names an **overarching *standby*
mode** as *"the best comprehensive solution"*. What *standby* is, relative to safe mode and
lockout, is the next question.

## source · the plant condition: the Navy's overarching mode, and each component's contract keyed to it

Read on 2026-10-26 from the fresh TUM and JFMM extractions. Both were searched for *standby*,
*stand by*, *inactivation*, *lay-up*, *cold iron*, *plant condition*, *inport* and *out of
commission*, and every hit was read in context. Neither text uses *standby* as a mode.

- TUM 1.3.2(3): *"The Authorizing Officer shall sign the Authorizing Officer Issued block of the line
  item signifying agreement that any associated system status changes and installation of tags are
  compatible with ship and plant conditions."* 1.3.3.a(3), the repair activity: *"The RA
  Representative authorizing the line item remains responsible for ensuring the tag-out is
  compatible with system status and ship/plant conditions."*
- TUM App. D, Figure 6, the **Tag Guide List** (NAVSEA 4790/12): for each piece of equipment, the
  *"NUMBER OF TAGS PER EQUIP"* under each of three conditions: *"COLD IRON"*, *"INPORT"* and
  *"UNDERWAY STEAMING"*.
- TUM App. (Master tag-out): *"Tag Roll. An isolation boundary change that occurs when plant
  conditions or scope of work changes, etc. warrant a line item to have its isolation changed or
  "rolled" from one set of boundaries to another."* *"Master tag-out. A concept used to provide for
  the isolation of multiple work items within a common boundary"*.
- TUM App. L: *"When an entire system is placed OOC, it is not necessary to put OOC labels on all
  instruments associated with the system."* An instrument with a *"small and consistent"* error
  takes a CAL label *"so instrument operations may continue"*. A large or inconsistent error takes
  an OOC label, and the instrument *"shall not be used"*.
- JFMM I-2 FWP initial conditions: *"this section should identify work boundaries and plant or system
  conditions (e.g., Pressure or Temperature Band, cold iron). The duty officer or tagout authorizing
  officer will determine and set the isolation boundaries."*

**What the texts show.** There is one ship-wide **plant condition**, set centrally. Each component
carries its own requirement for each condition: the Tag Guide List column. Every tag-out is checked
for compatibility with the current condition. A change of condition rolls each item's isolation to
the new boundary. A whole system can be marked out of commission at once, with no label on each part.
CAL against OOC is a two-level per-instrument status: *degraded but usable*, or *not to be used*.
This is the operator's model in the Navy's terms: a central signal, and a per-surface contract
keyed to it. *Standby* has no text term. The nearest is the plant condition as a whole, of which
the TUM names three values.

## source · the operator: the out-of-service indication runs both ways

The agent put the question of what *standby* is. Option A was standby as the overarching
condition, safe mode one of its values, and lockout checked as compatible with it. The operator
stopped it to clarify, 2026-10-26, verbatim (dictated):

> So this is smart. This tells us that the labeling that you showed briefly, that's an internal
> responsibility the module takes, right? So an out-of-service indication is a part of this design
> by contract, but it actually happens externally and internally. It's able for an external signal
> to let out-of-service notifications or service-level notifications happen. But it's also based on
> perhaps a diagnostic, a way for a module itself to signal externally that it's also unavailable.
> So this is actually a two-way street, and it's very smart. Of course, because we didn't design
> this way, because I just didn't have the wherewithal to see this maintenance mode coming, this is a
> pretty extensive refactor, unless you can help me see it differently.

## decision · the mode contract runs both ways: the module labels itself, and reports itself out of service

Ruled in principle from the operator's words above; this adds to the MEL and onboarding decisions.

- **Inbound.** An external signal (the condition) reaches the module. The module adjusts its level
  and **labels itself**, so the out-of-service or service-level indication is the module's own
  internal responsibility. This is the placard, carried by the module (TUM App. L: the CAL or OOC
  label).
- **Outbound.** The module can **signal externally that it is unavailable**, from its own
  diagnostic. This is the Navy's OOC label raised from inside: a CAL status for *degraded but
  usable*, an OOC status for *not to be used*. The nearest existing mechanism is the guard canary
  and enforcement-claim runner (`src/gzkit/guard_canary.py`). It detects from outside that a guard
  no longer fires, *"the claim still reads green"*. It is not a module reporting on itself.

The operator asked whether the refactor can be seen differently. The agent's answer is in the next
entry, as a proposal, not yet ruled.

## decision · the agent's reframe of the refactor, recorded as considered and not adopted as the route

The agent proposed, in conversation on 2026-10-26, that AC 91-67 ¶ 20f(3) (*"If the operator has not
yet developed a procedure for an item, that item must be operative"*) makes the refactor a migration
rather than a single rewrite:

1. Today's MX checkpoint is declared as a group default (Meyer's *"defaults at the system and
   cluster levels"*; TUM App. L, an entire system OOC). This keeps the 2026-10-17 ruling (*"Safe mode
   lowers every guard outside GATE5_INVARIANTS to advisory while its marker is open"*).
2. The craftsman peels controls out into their own contracts as repairs touch them.
3. Ports go at the few places of call: the pre-commit config (18 hooks), the Claude hook events
   (10 entries across 7 events), the `gz check` step list, and the CLI validators.
4. The outbound self-report is the new build.

The operator's answer is in the next two entries. It accepts that degrees of rewrite exist, and it
rules that the route is not chosen to save effort. The reframe is kept as one input to row 5's
program, not as the route.

## source · the operator: built-in self-test, standby defined, and the design done the right way

Operator, 2026-10-26, verbatim (dictated):

> Sure, I get it, but even in the diagnostic built-in testing that a module really should have had
> all along, there's two things going on here, but they are all still designed by contract. One thing
> is that modules occasionally, perhaps as a part of maintenance or as a part of normal checks, maybe
> through the chore system, need to be able to built-in tests, you know, built-in self-test. So they
> can participate in this MEL process by indicating their suitability for function, which is not safe
> mode at all, but still can actually interact with safe mode. And that safe mode, on the other hand,
> could tell modules to reduce their level of operational compliance. You know, this is what I meant
> by a standby mode. So really, we have this two-way street, and you're right, there's different
> degrees of rewrite, but I also caution us to not be so parsimonious or urgent to get back underway
> that we don't do this design the right way.

## decision · built-in self-test reports suitability for function; standby is safe mode's command to reduce compliance

Ruled in principle from the operator's words above. This settles the open question of what
*standby* means, and names both channels of the two-way contract. Both are Design by Contract.

- **Outbound: built-in self-test.** Each module carries a **built-in self-test**. It runs as part of
  maintenance or of normal checks, possibly scheduled through the chore system. It reports the
  module's **suitability for function** into the MEL. This is **not safe mode**: it runs in normal
  operation as well. It can interact with safe mode, though: a module that reports itself unsuitable
  enters the MEL as inoperative, and an (O) limitation then governs the system around it.
- **Inbound: standby.** **Standby** is safe mode's command to modules to **reduce their level of
  operational compliance**: the Meyer level, lowered on the signal. Safe mode is the condition.
  Standby is what it tells each module to do. The question of what *standby* is, as put to the
  operator, is answered by this, and option A (standby as the condition itself) is not taken.
- **The design is done the right way, not the fast way.** Operator: *"I also caution us to not be so
  parsimonious or urgent to get back underway that we don't do this design the right way."* This
  binds row 5's program: its route is chosen for the design, and saving effort or returning to
  service sooner are not reasons for a route. This is the operator applying `AGENTS.md` § DO IT
  RIGHT #3 (*"'Smaller diff' / 'faster to land' are not concrete downsides"*) to this run.

**Terms.** *Built-in self-test* is the operator's term. Avionics uses *built-in test equipment*
(BITE), but no text the run holds defines it. That is unsourced, and the run does not rely on it.
*Suitability for function* is the operator's phrase. AC 91-67's nearest is *inoperative* (¶ 6k:
*"does not accomplish its intended purpose and/or is not consistently functioning normally within
its approved operating limits or tolerances"*), and TUM's is the CAL/OOC split.

**commissions:** 5 — each module's built-in self-test and its report into the MEL; standby as the
inbound level command. 3 (advise only) — a chore that runs the self-tests, if the operator admits
one.

## source · the operator on the census: every control, by kind, with priorities ordered

Operator, 2026-10-26, verbatim (dictated), approving the census:

> Yeah, the syntax is going to matter quite a bit. And this is really widespread and pervasive, but
> I don't see a way around it. This is also probably going to be a massive refactor, so you are
> right, though. The priorities have to be ordered, right? We can't just redo everything at once.
> So in your inventory and census, you know, not everything's going to be tripwire or alarm. So we
> also have to look at the actual controls we have in place. But this design by contract means that
> we really should have had this in there all along. And that's a different matter. And there are
> different development strategies if it's code versus props more skills routing, if it's skills,
> and obviously some conditional logic if it's different rules and other more model-oriented control
> surfaces.

(*"props more skills routing"* is kept as dictated; read as *prompts or skills routing*.)

## decision · the census covers every control in place, by kind; the refactor's priorities are ordered

Ruled from the operator's words above.

- **The census inventories every control in place**, not only the places a tripwire or alarm is
  called. It records each control's role, since *"not everything's going to be tripwire or
  alarm"*.
- **Controls are sorted by kind, because each kind has its own development strategy:**
  - **code**: a port and the contract at the place of call;
  - **skills**: the contract carried through prompts and skill routing;
  - **rules and other model-oriented control surfaces**: conditional logic in the surface's text.
- **The contract's syntax matters.** It must serve all three kinds. That is a design question owed
  after the census.
- **Priorities are ordered.** The refactor is not done all at once. This does not conflict with the
  caution against parsimony: the order is chosen for the design, and the whole design is still
  done.
- **Not having designed this from the start is a separate matter.** Operator: *"we really should
  have had this in there all along. And that's a different matter."* It is recorded here, and not
  pursued inside this run.

Two background research tracks were dispatched for the census on 2026-10-26, one for code controls
and one for model-oriented surfaces. Each lands its inventory under
`docs/rnd/contractor-kit/sources/`.

## decision · the mode contract is a permanent design requirement for everything gzkit builds

Operator, 2026-10-26, verbatim (dictated):

> Don't forget though, moving forward, this design by contract is there when we design new things,
> which means that this is an overarching design requirement permanently and always with everything
> we build in terms of its built-in self-testing, but also in terms of its ability to comply with
> these different modes of operation, right? Having a safer maintenance mode is something we'd
> expect out of anything that's built moving forward.

Ruled. The refactor in disposition 5 retrofits what exists. This ruling covers everything not yet
built. **Every new control, module, skill, rule or surface gzkit builds carries the two-way mode
contract from the start:**

- a built-in self-test that reports its suitability for function;
- compliance with each mode of operation (its level under safe mode and standby, its bypass, its
  restore).

A design that lacks either is incomplete. It is a standing requirement, the same kind as
ports-and-adapters is today (`.gzkit/rules/hexagonal-architecture.md`: *"primary code-architecture
directive"*).

**commissions:** 4 — the requirement written into canon as a rule, and into the ADR, OBPI and skill
templates as a required section, drafted for the operator's go on the row. 1 (proposal only) — the
admission question is owed: is this hard to reverse, surprising without context, and the result
of a real trade-off? If all three hold, it is an ADR the operator may initiate. If not, it stays at
row 4.

## source · the operator: why the drydock exists, and the factory floor mode gzkit never had

Operator, 2026-10-26, verbatim (dictated):

> Yeah, I get it with C3, and I like how the Navy, you know, has some distinction there. So I
> obviously need to review and verify the majority of this with you. And we don't have to onboard
> all the costs immediately, but this need for maintenance mode or dry dock really came about from
> the reality that we couldn't keep on modifying gzkit while all features of gzkit were on. We were
> causing tampering in places where dampening was happening, and vice versa. So we needed this mode,
> and we needed it all along. We should have had a factory floor mode where we would build these
> provisions, but then obviously keep them disabled while we were assembling and modifying parts.
> So this was long overdue.

## decision · a factory floor condition: provisions built in, held disabled during assembly

Ruled in principle from the operator's words above.

- **Why the drydock exists, in the operator's words.** gzkit could not be modified with all its
  features on: *"We were causing tampering in places where dampening was happening, and vice
  versa."* The controls and the work interfered with each other. That is the hazard the mode
  contract removes.
- **A factory floor condition.** It is a value of the central condition signal. A provision
  (control, self-test, alarm) is **built in** as part of assembly, but **held disabled** while parts
  are assembled and modified. It is enabled when the assembly is accepted. This is the build-time
  counterpart of standby: standby lowers a working control, and factory floor holds a new one off
  until it is accepted. With the permanent design requirement, it is how a new surface carries its
  contract from the first commit without interfering with the work that builds it.
- **Costs are not all paid at once.** *"we don't have to onboard all the costs immediately"* is
  consistent with the ordered priorities and the caution against parsimony.
- **The operator reviews and verifies most of this with the agent.** *"I obviously need to review
  and verify the majority of this with you."* The review before sign-off is where this happens.

**Hypothesis, unread as a mapping:** TUM 1.7.6 names *"ship's construction periods when the TUM is
invoked"*. The Navy's new-construction regime, building a ship whose systems are not yet in service,
is the likely text counterpart of the factory floor. Only 1.7.6's single sentence has been read.
*Factory floor* stays the operator's term until a construction-period source is read.

## source · self-check, second person and inspection, in the texts and in the pipeline

Read in full 2026-10-26 for matrix row C3, from fresh extractions and the repository.

JFMM I-2.3.3.1.j(3), the margin symbols of an FWP: *"(V) = Steps requiring verification by a
craftsman."*; *"(I) = Steps requiring inspection by a QAI or NDT Inspector."*; *"(Q) = Critical
Quality Control Points (Q-Point)."*; *"(S) = Steps in an FMA procedure requiring verification by a
member of Ship's Force."*; *"(G) = Government notification required."*. JFMM I-5.4.3: *"Critical
Inspections. An inspection on any system or component, which by its nature is so critical to the
successful completion of the task, that the inspection requires verification by a separate
individual, other than the craftsman, qualified as an inspector. These inspections will be annotated
in the written work procedure by the presence of an (I)"*.

TUM 1.6.2: *"In addition to the Second Person verification, which is always mandatory, independent
reviews may be required by cross checkers and/or the Assistant Authorizing Officer. [...] a. A second
qualified person shall independently determine the adequacy and accuracy of the line item and
isolation."* TUM 1.6.5.a: *"After tag posting is complete, a second person shall independently
ensure that the correct component is tagged, and check (verify) proper component positioning and
tag attachment. This checker shall not accompany the person(s) posting the tag."* TUM App. D,
LIRS block 12: *"SECOND PERSON — An independent review is done to ensure the adequacy of tag-out
isolation and to ensure the correctness of the line item and tags."*

14 CFR § 121.369(b)(7): *"Instructions to prevent any person who performs any item of work from
performing any required inspection of that work."*

**The texts have three tiers.** The **craftsman's own verification** (V) is the performer's check.
The **second person** is an independent check by someone who does not accompany the work, and the
TUM makes it *"always mandatory"* for tag-outs. **Inspection** (I) is by a qualified inspector at the
critical points the procedure marks. The performer never inspects its own work (§ 121.369(b)(7)).

**The gzkit side.** The implementer (`.claude/agents/implementer.md`) checks its own work:
Red-Green-Refactor, with the red witnessed by `gz arb red`, a `red_receipt_emitted` event. The
spec-reviewer (`.claude/agents/spec-reviewer.md`) is *"Independent review by reading; cannot
execute commands"*, and must *"Re-read all changed files independently — do NOT trust the
implementer's summary"*. The quality reviewer is the same kind of check. The run's inspector, the
QAI ruled at A5, is dispatched by the runtime at set points. The built-in self-test, just ruled, is
a module checking itself.

## decision · three tiers of check: craftsman verification, second person, inspection

Ruled; matrix row C3. Both sides were read in full (the source entry above). Options put:

- **A.** Three marks on each task card step:
  - **(V) craftsman verification**: the performer's own check, which covers the implementer's
    witnessed red and green and a module's built-in self-test;
  - **second person**: an independent check by someone who neither did nor accompanied the work,
    which covers the pipeline's spec and quality reviewers;
  - **(I) inspection**: by the QAI at the critical points, dispatched by the runtime.

  A lower tier never satisfies a higher mark. The runtime refuses a session that performed a step
  from signing its second-person or (I) mark.
- **B.** Two marks, (V) and (I), with the reviewers folded into (I).
- **C.** Keep the pipeline's names, and put the Navy's marks in the crosswalk only.

Recommended A. Operator selected **"A: three tiers (Recommended)"**.

The terms are the texts' own: *verification by a craftsman* (V), *Second Person* (TUM 1.6.2), and
*inspection* (I). This settles the matrix's recorded liberty: JFMM's use of *verification* for the
inspector's act as well (I-5.4.3) is no longer a gap. In gzkit, *verification* is the (V) tier and
*inspection* is the (I) tier. A built-in self-test is always (V), so it never stands in for an
independent check.

**commissions:** 4 — the three marks on task cards in the kit's runtime, the refusal of
self-signing, and the pipeline's reviewers named as the second person. 2 — a GHI on the pipeline
side for the second-person name, as a lesson crossing from the kit.

## source · the operator: assembly mode, and whether the non-operational modes are one

Operator, 2026-10-26, verbatim (dictated, sent while C3 was being put):

> I guess you'd call that assembly mode, right? The idea is that, you know, we're not fully
> operational, so it's just a non-operational mode where the logic and pathways are available, but I
> don't know if that's important enough as a distinction from safe mode and factory floor mode and
> maintenance mode ultimately become pretty indistinguishable. You're in non-assembled disrepair or
> disintegration,

**The agent's reading, for the question.** For the central signal, the operator's point holds:
safe mode, maintenance and factory floor are all *not fully operational*, and a module told to
stand by does the same thing in each. The difference lives in the **control's own state**, not in
the signal. A control lowered by standby was accepted before, and its restore returns it to a level
it has already held. A control never yet accepted, which is the assembly case, has nothing to return
to. Its first enabling is an **acceptance**, with its own self-test passing for the first time. The
Navy keeps the same split between a system restored after repair and one accepted out of
construction. The construction-period text is unread, so that remains a hypothesis.

## decision · one non-operational condition; each control carries accepted-and-lowered or not-yet-accepted

Ruled. Options put:

- **A.** One non-operational condition on the signal (today's safe mode and MX hangar). Factory
  floor and assembly are not separate modes. Each control's contract carries a state: **accepted
  and lowered**, which is restored at exit, or **not yet accepted**, which is enabled only by its
  first acceptance (its self-test passing and its mark signed).
- **B.** Assembly as its own value of the signal.
- **C.** One condition, with no state on the controls.

Recommended A. Operator selected **"A: one condition (Recommended)"**.

This **amends** the factory floor decision. The factory floor is no longer a value of the signal.
It survives as the *not yet accepted* state of a control under the one non-operational condition.
The operator's *"pretty indistinguishable"* holds for the signal, and the distinction is kept where
it matters: whether a control's restore returns it to a held level or is its first acceptance.

**commissions:** 5 — each control's contract carries its accepted state, and first acceptance is
recorded.

## source · the census of controls, code and model-oriented

Two background tracks landed on 2026-10-26: `docs/rnd/contractor-kit/sources/census-code-controls.md`
(870 lines) and `docs/rnd/contractor-kit/sources/census-model-surfaces.md` (550 lines). Their method
and gaps are in each header. The code census counted the registries by running the code. It took
CLI refusals as a sample of 37 out of 301 refusal sites. The model census read frontmatter and
headings in full, and read every hit for the mode terms in context. Its role labels are the
census's reading, because the repository declares no role field.

**Counts.**

- **Code: 421 controls.**
  - By kind: 25 git-hook, 23 Claude/Codex, 74 `gz check` steps, 108 validators, 134 `@enforces`
    claims, 8 CI, 37 CLI refusals (sampled), 4 MX-internal, 8 chore scripts.
  - By role: 116 tripwire, 12 alarm, 13 monitor, 218 safeguard, 52 gate, 7 other, 3 dispatcher.
  - 204 read the MX signal and 217 do not.
- **Model-oriented: 206 surfaces** (183 without the 23 generated nested `AGENTS.md`).
  - By kind: 73 skills, 26 rules, 2 contract files, 7 personas, 6 agent definitions, 40 chores,
    13 text-injecting hook entries, 14 templates, 2 loose prompts.
  - 8 are mode-aware today. No surface reports its own suitability for function.
- **Built-in self-test today:** only the `--self-test` arms of 7 chore scripts.

**Checked by the agent against the code, 2026-10-26:**

- `.gzkit/mx.json` is tracked in git (`git ls-files`). HEAD carries `"mode": "safe"` and
  `"exiting": false`. `hangar_demotes` (`src/gzkit/mx/checkpoint.py`) returns True whenever the
  marker is active and not exiting, so every clone, CI included, runs demoted.
- The step demotion acts only on exit code 3 (`src/gzkit/commands/quality.py`: `if
  getattr(result, "returncode", 0) != 3: ... return result`). Steps that fail any other way still
  block.
- `gz mx exit` re-runs `uv run gz check` (`src/gzkit/commands/mx_cmd.py:380`), the change scope, not
  `--full`.

**Correction to this record.** The entry *the agent's reframe of the refactor* says *"the Claude hook
events (10 entries across 7 events)"*. That counted matcher groups. The census counts **17
registered entries** across 7 events, running 15 scripts.

**Findings the census reports, not yet checked by the agent.** Each is a defect candidate,
tracked here until routed:

- the Claude and Codex safe-mode banners differ (`.claude/hooks/mx-awareness.py:44-51` against
  `src/gzkit/mx/awareness.py:20-24`), and Codex gets no per-turn banner;
- twin controls disagree: the Codex verifier pipe ignores safe mode where its Claude twin honors
  it, and the Claude pipeline gate demotes while its pre-commit twin is pinned CRITICAL;
- the checkpoint (both modes, unreadable marker included) and the alarms wrapper (safe only) read
  *open* differently, and neither checks the ledger binding `is_valid`;
- in the GATE5 floor, two members are unenforced, gitleaks runs outside the checkpoint with no
  claim, and `grader-gaming` has no production caller;
- 96 of 134 claims have no canary, and 55 leave `exempts` undeclared;
- hook drift: `ceremony-step-gate.py` and `control-surface-sync.py` are unwired, and the README
  lists a missing `session-start-advisement.py`;
- `AGENTS.md:167` says the post-edit ruff hook strips imports, while the hook says it only reports;
- `pipeline-router.py` routes to the OBPI pipeline without reading the marker;
- `mx-mode.md` loads only for MX code paths;
- subagents receive no safe-mode banner. The model census observed this of itself: it ran
  without a banner while the marker was open.

## source · the operator on the census findings

Operator, 2026-10-26, verbatim:

> these might need decorators or something similar (maybe there are other Python affordances I may
> be missing) ==> "218 safeguards, 116 tripwires, 52 gates, 13 monitors, 12 alarms"
>
> this seems promising ==> "--self-test"
>
> 1. on mx.json and its mode: safe, that likely pre-dates this drydock period. we need to review the
> entire mx system to make sure we get this right. 2. this needs fixing/address. 3. that too needs
> fixing
>
> on additonal defects... I KNEW IT, I knew we had hidden slop and misalignments. those all must be
> fixed.
>
> q1: see above, we need to review mx mode structures and design.
> q2: yes, but let's do one overall review before filing.

## decision · the census's findings: all fixed; one review before filing; the MX system reviewed whole

Ruled from the operator's words above.

- **Syntax direction for code controls.** The 411 code controls with a role (218 safeguards, 116
  tripwires, 52 gates, 13 monitors, 12 alarms) carry their mode contract by **decorators or a similar
  Python affordance**. The operator asks for other affordances too, so the syntax question puts the
  candidates: decorators (the `@enforces` precedent), `typing.Protocol` ports (the hexagonal rule's
  shape), context managers, class registration, and entry points.
- **The `--self-test` arms are the seed of the built-in self-test.** Seven chore scripts carry one
  today. Their shape is read before the self-test's syntax is put.
- **The MX system is reviewed whole.** That covers its structures and design: the marker, its
  tracking in git, its two readings of *open*, the ledger binding, the checkpoint and the alarms
  wrapper. The tracked `"mode": "safe"` marker likely predates this drydock period, and the review
  settles it. This review is a frontier item of the run, ahead of the port design.
- **Findings 2 and 3 are defects to fix:** the step demotion acting only on exit code 3, and
  `gz mx exit` re-running the change scope instead of `--full`.
- **Every defect the census found must be fixed.** Operator: *"I KNEW IT, I knew we had hidden slop
  and misalignments. those all must be fixed."*
- **One overall review before filing.** Row 2 has the operator's go to file GHIs (*"yes"*), but
  only after the agent verifies every finding against the code and presents the whole set as one
  review: real or not, its evidence, and how findings group. The GHIs are filed through
  `ghi-author` after that review.

**commissions:** 2 — every verified census defect as a GHI, after the overall review.

## decision · the defect review approved; ten GHIs to be filed

The agent wrote `docs/rnd/contractor-kit/defect-review.md`: 24 findings checked against the code
(17 verified or counted, 5 carried from the census with evidence, 2 not defects), grouped into ten
proposed GHIs, one defect class each. Question: approve this grouping for filing, or split or merge
any? Operator: *"yes, let's go with those"*.

The ten are filed through `ghi-author`. Its prior-art step runs on each, and a group an open issue
already carries joins that issue. Their numbers are recorded in the review as they land.

**Filed 2026-10-26: #1271 to #1280.** #1271 is the `gz mx exit` scope; #1272 is the exit-code-3 demotion; #1273 is the MX-system review, filed as an investigation, with #1263 (the committed marker in CI, already filed with the operator's env-switch ruling) as its sibling and a cross-link comment posted there; #1274 is the twin controls; #1275 is the mode not reaching the model; #1276 is the GATE5 floor; #1277 is enforcement coverage, naming the per-step witness family #1230 to #1241 and #1155 once; #1278 is the unregistered hooks; #1279 is the TODO check that cannot fail; #1280 is `AGENTS.md:167`. This invocation was authoring only, so nothing was implemented.

## decision · the run resumes a third time: the record checked, the frontier recomputed

Ruled, on resuming `.gzkit/handoffs/20261027T093232Z-bookmarks-folded-deps-lsp-rnd-committed.md`.
That handoff put a choice between this run and the subagent-folding run. Operator: *"b"*, which
picks this run. The other run had a writer active in another session.

**Record against git, 2026-10-27.** The record and `docs/rnd/contractor-kit/` have no uncommitted
changes. The last commit to touch the record is `0efea264d`. The one commit hash cited after the
second resume entry, `9649d0eb0`, resolves. So does every source file cited after it. The ten census
GHIs, #1271 to #1280, are all OPEN, and so is their sibling #1263. Of the rows the second resume
listed as still proposed, only C3 has been ruled since (*three tiers of check*). The coordinator's
authority (A3), the stop requested from outside the chain (A8) and the affected party (A7) are each
ruled in the entries above. The widening check is discharged (*the Minimum Equipment List, Meyer on
assertion monitoring, and the aviation widening*).

## source · the operator on the MX system, 2026-10-26 to 2026-10-27, in sessions outside this run

These rulings were given while repairs ran in safe mode, after the census entry above. They are
taken from the settled-ruling store (`uv run gz handoff rulings`) and
`.gzkit/insights/agent-insights.jsonl`, read 2026-10-27. Verbatim, in order:

> we are supposed to be in mx, that is way too many alarms and traps

> we are supposed to be freeing things up in mx, not hashing canaries

> report only, decide within #1273

> i think, even during repairs or contruction, somebody sweeps up the shop floor every night. The
> point is, it is too strivt to disable linting during safemode drydock/mx hangar. We are
> writing/changing code and that deserves

The third phrase rules that CI's full-strength run of demoted guards reports and does not fail while
a mode is open. The fourth keeps lint and the fast static checks armed in safe mode
(`docs/governance/safe-mode-doctrine.md` item 5). Together they are the operator's first rulings,
made in the field, on what the standby level command lowers and what it never lowers. They bear on
this run's MX-system review and on the MEL entries the mode contract gives each control.

## decision · the frontier, recomputed from the subject

The core model comes first, and placement waits.

1. **The MX system reviewed whole.** It was ruled ahead of the port design (*the census's findings*).
   GHI #1273 carries it as an investigation, and the operator has twice routed MX shape decisions
   into it (*"decide within #1273"*). The question still open: is the MX model (the condition
   signal, its marker and tracking, its readings of *open*, the ledger binding) defined here, with
   #1273 carrying the repair, or is the model itself defined in #1273? Nothing below can be ruled
   until this is settled.
2. **The syntax of the mode contract for code controls**: decorators, `typing.Protocol` ports,
   context managers, class registration or entry points. Before this is put, the seven chore
   `--self-test` arms are read as the seed of the built-in self-test. It depends on 1, because a
   control declares its MEL entry against a signal whose shape 1 settles.
3. **The rows still proposed:** B1, B11, C1, C5, C10, C11, C12 and C13.
4. **The two subjects the operator opened:** B12, which carries the GHI system, and the modified
   pipeline process.
5. **Placement and close:** the kit's RO number, the shape of the audit chore, disposition rows 1,
   5 and 6, the restated challenge, `review.md`, and sign-off.

The handoff's list of open steps was an input to this frontier, not the frontier. It led with the
syntax (2). That would put the syntax ahead of the review the operator ruled must come first.

## decision · the MX model is defined in this run; #1273 carries the repair

Ruled. Question: where is the MX model defined (the condition signal, its marker and its tracking,
its readings of *open*, the ledger binding)? Options put: **A** in this run, with #1273 auditing
the current code against it and owning the repairs, including the report-only CI shape already
routed there, recommended; **B** in #1273, with this run consuming its result. Operator: *"A"*.

#1273's repairs wait on the model questions below. The rulings already routed into #1273 stand as
inputs to the model and are not re-put.

## source · the MX system as built, read for the model

Read 2026-10-27, in full: `src/gzkit/mx/marker.py`, `levels.py`, `checkpoint.py`, `alarms.py` and
`lease.py`; `docs/governance/safe-mode-doctrine.md`; `.claude/rules/mx-mode.md` at `1.14.0`; GHI #1273's
body and its three comments. Read in part: `src/gzkit/mx/hardening.py`, at the dangling-state
detector only. Not read: `awareness.py`, `contract.py`, `disposition.py`, `invariants.py`, `log.py`
and `proxy_reality.py`.

- **The signal.** `marker.py`: *"a dumb filesystem truth-file whose *presence* means `MX==TRUE`"*,
  *"*valid only* when bound to a real `mx_session_opened` ledger event the tool wrote"*. The marker
  module imports no gzkit code, *"so it opens even when gz's own subsystems are the patient"*. It
  offers three readings: `is_active` (presence), `read` (a parsed payload, or `None`), and
  `is_valid` (present *and* bound to a still-open `mx_session_opened`).
- **Two values of `mode`.** `Marker.mode` is `Literal["mx", "safe"]`. The field's description still
  says *"safe: ... guards at full strength (GHI #1244)"*. `checkpoint.hangar_demotes` says the
  reverse: *"Safe mode lowers every guard outside `GATE5_INVARIANTS` to advisory ... that
  disposition was replaced by the ruling"*. So the description is stale.
- **The readers.** `hangar_demotes` is true when the marker is present and not `exiting`, and also
  when it is unreadable (*"An unreadable marker keeps the hangar's original presence-only
  reading"*). `alarms.alarms_off` is true only for `mode == "safe" and not exiting`. Neither calls
  `is_valid`.
- **Severity.** `levels.py` reuses `logging`'s ladder and adds `NOTICE = 25`. A level at or above
  `ERROR` grounds. `checkpoint.resolve` pins `GATE5_INVARIANTS` to `CRITICAL`, and under the marker it
  demotes any other level below `CRITICAL` to `ADVISORY`. That makes emitting `CRITICAL` the
  floor-pin *by LEVEL* that `mx-mode.md` describes.
- **The dangling state.** `hardening.dangling_state_status` grounds at `ERROR` when the ledger holds
  an open session and no marker is present (*"ledger open but marker missing"*).
- **The marker in git, measured.** `git log --name-status -- .gzkit/mx.json` shows three entries.
  `4a919af17` (2026-08-21) adds it while a hangar session is open, `00e3ef9b4` (2026-08-21, GHI
  #848) deletes it at exit, and `548594f97` (2026-10-17) adds it at safe-mode entry. It is not in
  `.gitignore`. **So the marker rides in git for the life of a session, and the one at HEAD is this
  drydock's own.** It does not predate this period, which corrects the hypothesis in the census
  ruling (*"likely pre-dates this drydock period"*). What has never been ruled is whether riding in
  git is intended.

## decision · the condition belongs to the repository

Ruled. Model question 1: does the non-operational condition belong to the repository or to one
working copy? Options put: **A** the repository, so the marker stays committed and every clone,
parallel session, worktree and CI is in the condition, with CI's full-strength run as #1263's
report-only second job (recommended); **B** one working copy, with the marker ignored by git;
**C** the ledger as the signal, with the marker as a cache. Operator: *"A"*.

- Riding in git for the life of a session, as measured, is now intended. #1273's question *"whether
  the marker belongs in git"* is answered **yes**.
- By #1273's own comment, this means the `GZKIT_MX_FULL_STRENGTH` switch is needed. It is built
  report-only, as a second CI job with `continue-on-error: true` beside the unchanged blocking job.
  That is the repair #1273 and #1263 carry.
- The dangling-state detector keeps its meaning: ledger open and marker absent is a defect in every
  clone.

**commissions:** 2 — #1263's report-only full-strength CI job, carried by #1273.

## decision · the condition is on only when the marker is present, readable, ledger-bound and not exiting

Ruled. Model question 2: one reading of *on* for every reader. Options put: **A** on only when the
marker is present, parses, is bound to a still-open `mx_session_opened`, and is not `exiting`, with
anything else read as normal operation at full strength and announced loudly (recommended); **B**
on whenever the file is present (today's checkpoint), with a bad binding or parse only reported;
**C** A's reading for demotion and B's for the alarm switch. Operator: *"A"*.

- `is_valid`'s anti-contrivance becomes the one reading. A hand-made or corrupted marker lowers
  nothing.
- This reverses `hangar_demotes`' *"An unreadable marker keeps the hangar's original presence-only
  reading"*. An unreadable or unbound marker now means full strength.
- The cost is accepted: a marker corrupted mid-drydock brings every guard back. The loud
  announcement names the cause and its one-command recovery.

**commissions:** 2 — `checkpoint.hangar_demotes`, `alarms.alarms_off` and every other reader conform
to this one reading, carried by #1273.

## decision · one condition with a standby level commanded at entry: hangar or drydock

Ruled. Model question 3: what becomes of `mode: mx | safe` under the one non-operational
condition? Options put: **A** one condition with a standby level commanded at entry, where the marker
names the level (hangar or drydock) in place of `mode`, and each control's MEL entry declares what it
does at each level (recommended); **B** one condition at one level, with `mode` retired and ceremony
suspension keyed to whether a contract is present; **C** the safe-mode contract carries the command,
and the marker holds only on/off plus the contract hash. Operator: *"A"*.

- **The two levels.** *Hangar* is the standing-maintenance level, for a hangar visit that answers one
  squawk. *Drydock* is the drastic level, taken under a contract. They are the doctrine's own words
  (`safe-mode-doctrine.md` § What safe mode is). *Safe mode* remains the name of the
  condition-at-drydock as the doctrine uses it. What it lowers is now a level default rather than a
  second mode.
- **What each level lowers is each control's own declaration**, with defaults by level (the MEL
  ruling: *"defaults by mode and by surface"*). Today's behavior is the starting default: at the
  hangar level guards demote and the slow alarms stay on. At the drydock level guards demote, the
  slow alarms are off and ceremony is suspended under the contract. Lint and the fast static checks
  are pinned at both levels.
- **The floor is never on the list at any level** (`GATE5_INVARIANTS`).

**A canon disagreement this settles, by canon.** #1273 observed that in safe mode no `gz check` runs
at push, while `gz-session-handoff` § Trust Model says *"the pre-push `gz check` ... are untouched"*.
`safe-mode-doctrine.md` item 5, the later and operator-ruled surface (2026-10-25: *"i don't want any
long check at all"*), rules for the drydock level: the slow alarms are off, and a whole-tree
`gz lint` runs at every push. The skill's sentence describes the operational condition and the
hangar level. It is stale for the drydock level, and the fix is its own.

**commissions:** 2 — the marker's `mode` becomes the commanded level, every reader keys to it, and
`gz-session-handoff` § Trust Model names the drydock-level exception, all carried by #1273. 5 — each
control's MEL entry declares its behavior at both levels.

## source · the seven `--self-test` arms and the `@enforces` declaration, read for the syntax

Read 2026-10-27: the self-test function and its dispatch in each of the seven chore scripts, the
callers in `src/gzkit/quality.py` (`run_module_size_audit`, `_run_project_local_ratchet`), and the
signature and docstring of `enforces` in `src/gzkit/enforcement.py`.

- **The shared shape.** Each arm is an argparse flag (or a bare `argv[0]` check, in
  `check_module_size.py`) that runs synthetic cases over the script's pure functions, *"no repo
  state, no network"*. The cases include the failure directions, which `check_module_size.py` calls
  *"TEETH"* (*"all five breach directions fire"*). The arm prints one line per case and returns an
  exit status. Nothing records the result.
- **Who calls them.** `gz check` runs four arms before their ratchet: module size, tautological
  debt, validator reachability and ledger inertness. Its docstring gives the reason: *"a gate with
  no automatic caller and a gate whose teeth are never verified are the same failure class"*. No
  automatic caller was found for the rule-conflicts, cross-reference-staleness and pattern-scan arms.
- **The exit statuses disagree.** `check_debt_target.py` and `check_module_size.py` return **3** on
  a failed self-test. `check_reachability.py` and `check_ledger_inertness.py` return **1**.
  `check_evidence.py` documents **2**. `check_cross_reference_staleness.py` uses `assert` and always
  returns 0, so under `python -O` its checks do not run.
- **Defect candidates, not yet put.** (a) A failed self-test that exits 3 meets the step seam's
  demotion code: under an open marker, a self-test that has lost its teeth is reported as
  advisory. (b) The `assert`-based arm can pass vacuously. Both are tracked here until routed.
- **`@enforces`, the decorator precedent.** *"Declare that a production callable enforces an
  enforcement claim. ... Returns the decorated callable unchanged — registration is metadata-only."*
  It takes `claim`, `fixture`, `entrypoint`, `expect`, `exempts`, `population` and `delegates_to`.
  It validates at decoration time and registers a record. A fixture with an entrypoint is already a
  self-test declared at the control. The registry it fills is the derived list that the onboarding
  ruling asks for.

## decision · a code control declares its mode contract by decorator, read at the place of call

Ruled. Model question 4: which Python affordance does a code control use to declare its mode
contract? Options put: **A** a decorator at the control, on the `@enforces` precedent. It records the
MEL entry (level per standby level, (M) procedure, (O) limitation, placard, restore condition) and
names the self-test. It is metadata-only at import, and the place of call reads declaration and
signal through one function, as `checkpoint.resolve` does today (recommended). **B** a
`typing.Protocol` port per control. **C** a context manager at the place of call. **D**
`pyproject.toml` entry points. Operator: *"A"*.

- The decorator declares and never changes behavior. Applying the level stays at the place of call
  (*the mode contract is honored at the place of call*).
- The list of controls is the decorator registry, a derived view (*the signal alone is central*).
- **Still open, and next:** whether the decorator shares `@enforces`'s registry or becomes one with
  it; how non-Python controls (git hooks, CI jobs, model-oriented surfaces) declare theirs; and how a
  self-test result reaches the MEL as *suitability for function*.

**commissions:** 5 — every code control carries the decorator, and the place-of-call function reads
it.

## decision · the questions are the right ones, a second time

After five recommended options in a row this session, the agent asked whether the questions were
the right ones (the red flag in `gz-rnd`). The three named as next were the decorator's registry,
the non-Python declarations, and the self-test's path into the MEL. Operator: *"they are the right
questions, continue"*.

## source · the `@enforces` registry and its runner

Read 2026-10-27: `src/gzkit/enforcement.py` lines 1 to 134 (the module docstring,
`EnforcementClaimRecord`) and `run_meta_validator`.

- **The unit is the claim, not the control.** Each record links one `claim_id` to a `fixture` (a
  *"Violation-builder callable"*) and an `entrypoint` (a *"Production callable; runner calls
  entrypoint(fixture())"*). So one callable can carry several claims.
- **The runner is an outside check of teeth.** `run_meta_validator` runs every claim and classes the
  result as PASS, FACADE (*"entrypoint did not catch the violation"*) or TEST_BUG. On a clean run with
  a root it *"emits one `enforcement_claim_verified` receipt per claim"*. So a self-test result
  already reaches the ledger as a receipt.
- **The runner is never demoted.** The census entry above: *"The runner is reached at CRITICAL from
  both of its gate callers"*. It is part of the floor's own machinery, and the floor *"can never be
  listed"* (the MEL ruling).

## decision · two decorators joined by reference: the MEL entry names its self-tests

Ruled. Model question 5: does the mode-contract decorator share `@enforces`'s registry? Options put:
**A** merge them into one decorator and one registry; **B** two decorators joined by reference, where
a new decorator carries the control's one MEL entry and its self-test field names `@enforces` claim
ids or a chore `--self-test` arm, `@enforces` is unchanged, and the MEL view is the join
(recommended); **C** `@enforces` grows MEL fields on each claim. Operator: *"B"*.

- **`@enforces` stays the floor's proof of teeth.** It is never demoted and holds no level. That
  keeps the MEL ruling's *"The floor can never be listed"* true by construction.
- **One MEL entry per control**, so a level is the control's own and is fixed for an act.
- **A reference that names no registered claim or arm fails at import**, on `@enforces`'s
  decoration-time precedent.
- **The runner's `enforcement_claim_verified` receipt is a self-test result.** A chore arm today
  prints and records nothing. How either result reads as *suitability for function* is the next
  question.

**commissions:** 5 — the MEL decorator with its self-test references and the decoration-time check;
the MEL view as the join of the two registries.

## decision · suitable for function: the latest self-test passed within the entry's declared interval

Ruled. Model question 6: when is a control *suitable for function*? Options put: **A** when its
latest self-test result passed and is younger than the interval its MEL entry declares; a failed or
stale result shows it inoperative in the MEL view, its (O) limitation then governs, and every
affected party gets the placard; chore arms write a receipt as the runner does (recommended).
**B** when its latest result passed, at any age. **C** when its self-test passes at the place of
call before every use. Operator: *"A"*.

- *Inoperative* takes AC 91-67 ¶ 6k's sense, and the CAL/OOC split stays available for *degraded but
  usable* against *not to be used*.
- An interval is declared in each entry. Choosing a value per control is diamond-2 work.

**commissions:** 5 — the interval field in the MEL entry; the inoperative reading in the MEL view;
a receipt writer for the chore `--self-test` arms. 3 (advise only) — the self-test chore already
recorded as a candidate, now the scheduler that keeps receipts fresh.

## decision · non-Python controls declare in their own slot, against one shared schema

Ruled. Model question 7: how do controls that are not Python callables declare their mode
contract? Options put: **A** each surface declares in its own slot against one shared schema
(recommended). The MEL entry becomes one Pydantic model. Python scripts, hook scripts included,
take the decorator. Markdown surfaces (skills, rules, personas, agent definitions, chores,
templates) carry an MEL block in frontmatter, validated against the model, and their self-test
reference may name an existing check such as `gz-skill-review`. Config-only controls (third-party
pre-commit hooks, CI steps) carry it as arguments to the `gzkit.mx.alarms` wrapper on their own
config line. **B** one sidecar file for every non-Python control. **C** Python only for now.
Operator: *"A"*.

- Three declaration shapes, one schema. The MEL view joins them with the two decorator registries.
- A third-party hook enters the MEL through the wrapper. A hook not wrapped is not listed, and by
  the MEL ruling an unlisted control cannot be relaxed.
- This closes the syntax item on the frontier: the decorator (question 4), the registry join
  (question 5), suitability (question 6) and the non-Python shapes (this one).

**commissions:** 5 — the shared MEL model; the frontmatter block and its validator; the wrapper's
MEL arguments.

## decision · B1: the contract changes only by its own amendment, never through a repair order

Ruled; matrix row B1. Question: adopt the master-agreement rule for the safe-mode contract? DFARS
217.7103-6(b): *"A master agreement shall be changed only by modifying the master agreement itself.
It shall not be changed through a job order."* Options put: **A** adopt it, with amendment booking
mechanical as today (`mx_contract_amended` per committing edit); a repair order needing a contract
change stops for a contract amendment first (recommended). **B** adopt it, and require the
operator's verbatim words on every amendment. **C** do not adopt it. Operator: *"A"*.

- **contract** stays the term (ratified 2026-10-15). The rule is added, and nothing is renamed.
- The pin (*"Hash at entry + amend event"*) is unchanged. The rule constrains what an amendment may
  come from, not how it is booked.

**commissions:** 4 — `safe-mode-doctrine.md` § The instruments item 1 and the contract template
carry the rule.

## decision · B11: the work package log, a Layer 3 view over the issues and the ledger

Ruled; matrix row B11. Question: what is the register of open orders? JFMM I-2.3.7.8.b(2)(b): *"All
open CWPs will be logged and tracked in the CWP REC log."* Options put: **A** name it the **work
package log**, a Layer 3 view assembled from the repair-order issues and the ledger and never
edited, with the contract's § Repair orders carrying the pointer (recommended); **B** keep
*register* as the name, as a view; **C** keep a hand-maintained table in the contract. Operator:
*"A"*.

- **register** is retired inside the hangar for this record. Part 0 is unaffected, under the
  scoped-register ruling.
- By the state doctrine's Rule 5, the log never blocks a gate. The issues and the ledger are its
  sources.

**commissions:** 4 — `safe-mode-doctrine.md` § The instruments item 3, the contract template's
§ Repair orders, and the crosswalk carry the term and the pointer. 5 — something renders the view;
its producer is diamond-2 work.

## decision · C1: initiation is the operator's; commencement of work is the coordinator's, once the tags hang

Ruled; matrix row C1. Question: is starting work an act separate from initiation? JFMM QA-9 Blk 15B:
*"granting permission for work to be conducted. No work can start prior to this signature."* DFARS
252.217-7010(a): *"The Contractor shall not start work until the job order has been awarded"*.
Options put: **A** two acts: the operator initiates, and the coordinator records **commencement of
work** once every surface the package works has its tag-out entry hung, with no work before both
(recommended). **B** one act, where initiation is also permission to start. **C** two acts, both the
operator's. Operator: *"A"*.

- The two preconditions of commencement are initiation and the tags hung. The tag-out log is the
  witness that isolation preceded the first change.
- **initiated** keeps its ruled sense (RO-5 ruling 5). **commencement of work** is added as the
  coordinator's term.

**commissions:** 4 — the kit's coordinator position carries the commencement act and its two
preconditions. 5 — the runtime refuses an act of work on a package with no commencement recorded.

## decision · C5: rework is the repair activity's repeat; buy-back is the inspector's reinspection

Ruled; matrix row C5. Question: does the fix cycle split into two recorded acts? JFMM I-2.3.7.2:
*"Rework is the unplanned repetition of a step, or a series of steps in a CWP or FWP."* 14 CFR
§ 121.369(b)(4): *"Procedures for the reinspection of work performed pursuant to previous required
inspection findings (buy-back procedures)."* Options put: **A** two terms for two acts: after a
QAI finding the craftsman does **rework**, and the inspector does a **buy-back** limited to that
finding; rework that reaches past the finding is unplanned work and goes back through the change
ladder (recommended). **B** rework only, with reinspection an unnamed second pass. **C** keep
*fix cycle*. Operator: *"A"*.

- **fix cycle** is retired for this record. The inspector, not the craftsman, closes a finding,
  which keeps the three ruled tiers distinct.
- A finding with no buy-back on record is open. Nothing else closes it.

**commissions:** 4 — the kit's craftsman and inspector positions carry rework and buy-back, and
the pipeline's fix-cycle wording is drafted to the two terms. 5 — the runtime records a buy-back
per finding and refuses to close a finding without one.

## decision · C10: final inspection and acceptance, then closed; closeout stays with the release

Ruled; matrix row C10. Question: what closes a work package, given that `gz closeout` keys to the
Release Package once RO-4 lands (`safe-mode-doctrine.md` § The Release Package)? DFARS
252.217-7007(e): *"Upon completion of the work under a job order and final inspection and
acceptance"*. 14 CFR § 121.709(b)(2)(ii): *"All items required to be inspected were inspected by an
authorized person who determined that the work was satisfactorily completed"*. JFMM I-2.3.7.7.f, a
closeout attribute: *"Equipment and systems were restored to normal conditions and
configurations."* Options put: **A** *closeout review*, then *closed*, qualified as package or
release closeout every time; **B** **final inspection and acceptance**, then *closed*: the
inspector's final inspection checks the record complete and every tag cleared, the operator's
acceptance is Gate 5 (recommended); **C** *closed* only, with no named review. Operator: *"b"*.

- **closeout** names the release-level act alone. The matrix's *closeout review* is not taken, so
  the package and the release share no word.
- The JFMM's closeout attributes, restore-to-normal among them, become the content of the final
  inspection. The source term departs from the JFMM's here, and this entry records that.
- **closed** keeps its ruled sense (RO-5 ruling 5): it carries the Gate 5 decision.

**commissions:** 4 — the kit's inspector position carries final inspection with the tag-clear
check, and the doctrine keeps *closeout* for the Release Package. 5 — the runtime refuses
acceptance on a package whose tag-out log has an entry still hung.

## decision · C11: shift turnover, a named act the handoff carries

Ruled; matrix row C11. Question: what act happens at session relief inside the hangar? The
handoff's name is not in question: the three-subjects ruling names it session memory
(ADR-0.0.65). TUM 1.3.1.c: *"Supervisory watchstanders shall review associated tag-out logs during
watch relief and shift turnover."* 14 CFR § 121.369(b)(9): *"Procedures to ensure that required
inspections, other maintenance, preventive maintenance, and alterations that are not completed as a
result of shift changes or similar work interruptions are properly completed before the aircraft is
released to service."* 29 CFR 1915.89(m)(2): *"The employer shall establish and implement
provisions for the orderly transfer of lockout/tags-plus systems between authorized employees when
they are starting and ending their workshifts"*. Options put: **A** **shift turnover** as a named
act: at every session relief in the hangar the relieving session reviews the tag-out log, the
findings awaiting buy-back and the commenced packages, the handoff records the review, and every
hung tag transfers by name (recommended); **B** no new term, the review one more check in the
handoff's resume step; **C** adopt *position relief briefing* beside the handoff. Operator: *"a"*.

- **handoff** keeps its name and subject. The Part 0 candidate *position relief briefing* is not
  taken.
- A tag hung by a session that has been relieved, with no turnover naming it, has no holder.
  1915.89(m)(2) makes the transfer itself the thing recorded.

**commissions:** 4 — the handoff skill carries a turnover section for hangar sessions, and the
kit's coordinator position carries the review. 5 — the handoff's authoring gate refuses a hangar
handoff whose turnover omits a tag the log shows hung.

## decision · C12: the handback takes the form of a transfer of custody

Ruled; matrix row C12. Question: what must the handback contain? The doctrine names the act, *"The
amendment the operator ratifies at seaworthiness"*, and **handback** is the held term. JFMM III-5
App. C: *"IF NO RECs ARE OPEN AT THE TIME OF CUSTODY TRANSFER, STATE THIS FACT."* JFMM
I-2.3.7.8.b(2)(b)2: *"The CWP must include documented transfer of responsibility for accomplishment
of deferred actions from the FMA to the tended ship"*. DFARS 252.217-7010(b): *"Upon completion of
the work, the Government shall accept delivery of the vessel at the time and location specified in
the job order."* Options put: **A** a **transfer of custody** enumerating every open line item (the
punch list), every departure from specification the hangar accepted, and each deferred action with
its new holder, an empty category stated as *none*, then the operator's ratification (recommended);
**B** the ratified amendment alone, pointing at the punch list and the work package log; **C** open
items only. Operator: *"A"*.

- **handback** keeps its name. **transfer of custody** names its form.
- Silence is not *none*. A category left out of the handback is a defect in it, not an empty
  category.
- The enumeration is checked against the punch list and the work package log, which are its
  sources. The handback is not a third copy.

**commissions:** 4 — `safe-mode-doctrine.md` and the gz-mx skill's exit carry the three categories
and the *none* rule. 5 — `gz mx exit` refuses a handback whose enumeration disagrees with the punch
list or the work package log.

## decision · C13: the drydock session is defined in canon; the matrix's gap is stale

Not put to the operator: canon answers it (AGENTS.md § Operator Economy, consult canon before
asking). Matrix row C13 recorded *"gap (no definition)"*. `safe-mode-doctrine.md` § Maintenance
mode, read 2026-10-27, defines it: *"A drydock session is one `mx_session_opened` to
`mx_session_closed` span with `mode: safe` and its contract; `gz mx exit` renders its enter-to-exit
log at the hard gate; its repair orders are the units inside it."* The same paragraph carries the
operator's verbatim ruling of 2026-10-17 that the drydock is *"an on-demand and drastic"* kind
beside the scheduled checks and the squawk. The run's own standby-level ruling (one condition,
hangar or drydock) agrees with it.

- **drydock** is kept (Part 0, ratified). *Availability* is not taken: Volume V never defines it.
- No source term is missing. The definition is gzkit's own, and the citation is to canon.

**commissions:** 6 — no action: the definition exists, and the matrix standing cell is corrected
in this commit.

## decision · B12: the GitHub issue's role is a problem report, with AC 00-71's states

Ruled; matrix row B12. Question: what is the GitHub issue, and when is it closed? Canon read:
`safe-mode-doctrine.md` § Maintenance mode, *"the GitHub issue is the write-up"*; AGENTS.md
§ Defect-fix routing, *"closed with the commit SHA"*. AC 00-71 § 3.1: *"Problem report (PR) – A
means to identify and record the resolution of anomalous behavior, process non-compliance with
development assurance plans and standards, and deficiencies in life cycle data (adapted from
DO-178C/ED-12C)."* § 3.2: *"Resolved – A problem report that has been corrected or fully
mitigated, for which resolution of the problem has been verified but not formally reviewed and
confirmed."* *"Closed – A resolved problem report that underwent a formal review and confirmation of
an effective resolution of the problem."* Options put: **A** **problem report** names the role, the
GitHub issue stays the carrier (*GHI* in the tooling, *write-up* the squawk's word), and the states
are **recorded, classified, resolved, closed**: the fix commit resolves, and only a review (the
buy-back of C5, the final inspection of C10) closes (recommended); **B** the states only, with no
name; **C** rename *GHI* to *problem report* everywhere; **D** keep open/closed. Operator: *"A"*.

- **GHI** and **write-up** are kept. The carrier is not renamed, as in B1 and C11.
- The fix commit's SHA now witnesses **resolved**, not closed. A problem report closed by its own
  author's commit with no review on record has skipped a state.

**commissions:** 4 — AGENTS.md § Defect-fix routing (the *closed with the commit SHA* clause),
the ghi-close and ghi-author skills, and the doctrine carry the four states; a canon change through
the content skills, on the operator's go. 5 — the review step before GitHub's close, and its
record, are diamond-2 work.

## decision · the modified pipeline process: a crosswalk, each difference crossing as a GHI

Ruled. Question: what shape does the modified pipeline process take (operator, 2026-10-25: *"we
should be able to put together a modified pipeline process WITH EASE"*), given question 8, *"repair
first, then reuse unchanged"*, and the both-directions ruling? Options put: **A** a crosswalk in
this record from each pipeline stage to the kit act it carries, each difference from a ruled act
crossing as one GHI on the pipeline side, sequenced after #1200, #1206, #1208 and #1028
(recommended); **B** a pool ADR for the modified pipeline, proposed only; **C** no change until
civil rule. Operator: *"A"*.

B fails the admission question: the change is reversible, and its trade-off was already made at
question 8. The canon routes it to rows 2 and 4.

**The crosswalk.** Read 2026-10-27: `.gzkit/skills/gz-obpi-pipeline/SKILL.md` § Pipeline Stages,
and `references/stage-1-load-context.md`, `stage-4-present-evidence.md` and
`stage-5-sync-and-account.md`.

| Kit act (ruling) | Pipeline today | Difference |
|---|---|---|
| initiation, the operator's (RO-5 ruling 5) | only the operator initiates (AGENTS.md § OBPI Acceptance Protocol) | none |
| commencement once the tags hang (C1) | Stage 1 step 9, `gz obpi lock claim` | the lock claim stands for commencement, and nothing is isolated before it: the brief's allowed and denied paths are declared but not hung as tags |
| self-check, independent check, inspection (three tiers, C3) | Stage 3 baseline checks; Stage 2 spec-reviewer and quality-reviewer; Step 4b adversarial validation | none in kind; Step 4b is the inspector's precedent |
| rework and buy-back (C5) | Step 4b follow-up: *"The adversary must verify each claimed closure"*, under the ruling *"Step 4b closes on independent confirmation of the corrected state"* (2026-09-05) | the act exists in substance and has no name; a Stage 2 reviewer finding has no recorded reinspection of its own |
| final inspection and acceptance, then closed (C10) | Step 4b's last verdict, the Stage 4 human gate, `gz obpi complete` | restore-to-normal comes after acceptance: Stage 5 cleans the markers after attestation, where the kit's final inspection checks every tag cleared before it |
| shift turnover (C11) | the abort path: *"Leave the lock held, name it in the handoff"* | partial: a held lock is named, but no review of what the relieved session held is recorded on a non-abort relief |
| problem report, resolved then closed (B12) | a finding returns as a GHI, closed with the commit SHA | the GHI closes on the fix with no review; row 4 of B12 already carries it |
| transfer of custody (C12) | none | none: the pipeline is not a hangar, so there is no custody to transfer |

Five rows differ. The B12 difference is commissioned already, so four cross as GHIs.

**commissions:** 2 — one GHI per difference on the pipeline side (commencement with no isolation,
the unnamed buy-back, restore-to-normal after acceptance, turnover on a non-abort relief), each
filed through ghi-author on the operator's go on that row and sequenced after #1200, #1206, #1208
and #1028.

## decision · the kit is RO-12, placed immediately after RO-5

Ruled. Fact: the contract's register (`harbor-pilotage-candidate-2026-10-15.md` § the order table,
read 2026-10-27) runs to RO-11, so the kit's order is RO-12. Question: where does RO-12 sit in the
register's order, which is dependency order? Facts put: the kit's acts work on RO-5's structures;
question 8 requires #1200, #1206, #1208 and #1028 repaired first, and with #1273 all five read
OPEN on 2026-10-27; the contractor brief's order is RO-5, RO-4, RO-11 (stop), RO-6, RO-7, RO-9,
RO-8. Options put: **A** immediately after RO-5, the five GHIs as its preconditions, every order
from RO-4 on then running under the kit as its first flight (recommended); **B** last, after RO-8,
built for the next drydock; **C** not a repair order, a work package at civil rule. Operator:
*"A"*.

- RO-4 waits on the five repairs and the kit. The contractor brief's *"launch the contractor once
  on everything"* (2026-10-25) is amended by this ruling: the launch now runs RO-5, then RO-12,
  then the rest under the kit.
- The orders after RO-12 are the parts' first flight under the inspector, as question 8 put it.

**commissions:** 4 — the contract's register gains the RO-12 row and the contractor brief its
order, as contract amendments (B1), on the operator's go on that row. 2 — #1200, #1206, #1208,
#1028 and #1273, repaired as direct fixes before RO-12 is landed.

## decision · the vibe-coded audit chore is a signature catalogue

Ruled. Question: what shape does the audit chore take (operator, 2026-10-25, admission directed)?
Read 2026-10-27, the neighbouring chores: `session-correction-mining` mines the operator's
corrections, `failure-class-index` the filed GHIs' declared classes, `evidence-integrity-audit` a
brief's claims against state; none reads shipped processes for the class the operator named, which
is defined by the corrections that were *not* made. Options put: **A** a signature catalogue: named
signatures, each anchored to an observed instance in this repository and carrying its own detector
or reading procedure; members read, never titles, with the count read against the count that
exist; each finding to ghi-author on the operator's go on that row; a signature joins only from an
observed instance (recommended); **B** widen `session-correction-mining`; **C** a one-shot
population audit under row 5. Operator: *"A"*.

The seed signatures, each from this run:

1. a self-test that passes vacuously (`assert load_baseline() is not None`, the
   `ghi-cross-reference-staleness` arm, read 2026-10-27);
2. a budget totalling a surface loaded per item (the persona witness; its siblings a hypothesis,
   unread);
3. a control with no named contract (the doctrine's standing exit measure);
4. a *deferred to X* claim that X does not carry (AGENTS.md § PRIME DIRECTIVE item 7);
5. work handed back as options (the agent's reply the operator cited on 2026-10-25).

Signatures 4 and 5 need a reader, not a pattern. The chore says so for each, and does not report a
pattern match as a reading.

**commissions:** 3 — the chore, in this shape; admission directed 2026-10-25.

## decision · row 1, ADR / OBPI: not pursued

Ruled. The admission question put: is the decision hard to reverse, surprising without context,
and the result of a real trade-off? Facts put: the kit's home is RO-12 (ruled 2026-10-27); the
two-way mode contract is hard to reverse and a real trade-off, but it is a refactoring program, row
5; no OBPI can run in safe mode (R4); the doctrine moves the ADR off the release rung, and pool
entries *"aren't ADRs any longer"* (RO-11). Options put: **A** not pursued, the kit's home RO-12
and the mode contract's row 5, revisited at civil rule through RO-11's process (recommended);
**B** propose a pool ADR for the two-way mode contract. Operator: *"A"*.

**commissions:** none. Row 1 is **not pursued**. Reason: every outcome of this run has a governed
home that is not an ADR. Revisit if, at civil rule, the kit or the mode-contract program outgrows
the drydock; it is then pulled as a work package under the catalog by RO-11's process.

## decision · row 5: the two-way mode contract program is RO-13, ratcheted to zero

Ruled. Question: by what route does the program run, which gives every control its MEL entry, its
standby level at the place of call and its built-in self-test, across the census's 421 code
controls and 206 model-oriented surfaces, kind by kind and with priorities ordered (ruled
2026-10-26)? Precedents put: RO-2 (*"Ratchet to zero (Rec.)"*) and RO-9, each a whole-tree program
in tranches with a shrink-only baseline. Options put: **A** its own repair order, **RO-13**, after
RO-12, in tranches by kind (code controls first, by role: alarms, gates, then safeguards, monitors
and tripwires; then skills; then rules and the other surfaces), witnessed by a shrink-only baseline
of controls with no MEL entry, closed at zero, the priority order set when RO-13 is specified with
the operator (recommended); **B** a tranche set inside RO-12; **C** at civil rule, as work packages
per kind. Operator: *"A"*.

- The witness turns the doctrine's standing exit measure, *"the count of controls with no named
  contract, at zero"*, into a check.
- The route was chosen for the design (*"not be so parsimonious or urgent to get back underway"*).
  The kit's first flight does not wait for the program.

**commissions:** 5 — the program, as RO-13 after RO-12; its specification and priority order with
the operator. 4 — the contract's register gains the RO-13 row, as a contract amendment (B1), on the
operator's go on that row.

## decision · correction: the C12 entry uses a retired term

The C12 entry says *punch list* three times, and so did the question put. Matrix row B8 retired
the term on 2026-10-25 (*"B′"*; *punch list* retired, unsourced) for **list of discrepancies**,
each line a **discrepancy**. Read the C12 ruling with that term: the handback enumerates every
open discrepancy on the list of discrepancies. The ruling's substance is unchanged, because the
operator ruled on the enumeration and not on the word. The entry stands as written, because the
record is never rewritten.

The contract's section is still headed § Punch list, and the contractor brief calls it *"§ Punch
list (the compliance register)"*. Renaming it is part of row 4's B8 commission and is not done here.

## decision · row 6, no action: the outcomes ruled to need none

Not a new question. Each item below was ruled earlier, and this entry collects them for row 6.

- **C13.** The drydock session needs no definition from this run. `safe-mode-doctrine.md`
  § Maintenance mode carries it.
- **The handoff's name.** *Position relief briefing* is not taken (C11, option C put and not chosen).
  The three-subjects ruling names the handoff.
- **The GHI's name.** *Problem report* is not adopted as a rename (B12, option C put and not
  chosen). Only the role and the states change.
- **The modified pipeline as its own design.** No separate design and no pool ADR (crosswalk, option
  B put and not chosen; row 1 not pursued). The pipeline changes only through the crosswalk's GHIs.
- **That the two-way mode contract was not designed in from the start.** Recorded and not pursued
  inside this run (operator, 2026-10-26: *"we really should have had this in there all along. And
  that's a different matter."*).

**commissions:** 6 — the five items above, each with its reason in place.

## decision · the questions are the right ones, a third time

The operator took the recommended option on all eleven questions since the second check (C5, C10,
C11, C12, B12, the pipeline crosswalk, RO-12, the chore's shape, row 1, row 5). As the red flags
require, the agent said so, named the three places its framing carried the most weight (C10
against the matrix's own proposal; RO-12 delaying RO-4; RO-13 lengthening the exit), and asked
whether the questions were the right ones. Operator: *"yes, your suggestions were good"*.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | not pursued | — | the kit's home is RO-12 and the mode contract's is row 5; revisit at civil rule, pulled as a work package by RO-11's process (ruled 2026-10-27) |
| 2 | GHI / direct fix | commissioned | the ten census defects filed as #1271 to #1280 (2026-10-26); direct repair of the eleven defects in the pipeline parts the kit reuses (#1200, #1206, #1208, #1198, #1203, #1205, #1194, #1209, #1185, a cwd-escape guard to be filed, #1028's stop-and-ask boundary); a GHI on the persona witness measuring a total; each lesson crossing kit and pipeline as a GHI, the four from the pipeline crosswalk among them (2026-10-27); #1273 before RO-12 | operator, questions 8, 14, 17, 21; crosswalk and RO-12 rulings |
| 3 | chore | commissioned | the vibe-coded and underbaked audit chore, as a signature catalogue (ruled 2026-10-27); `frontier-model-card-currency` widened to model-level assignments (landed `9649d0eb0`) | operator directed both, 2026-10-25 |
| 4 | control surface, rule, doc, skill, hook | commissioned | the contractor kit (four positions and the surveillant, runtime, tag-out log, maintenance record, list of discrepancies (B8), work package and change order (B3, B10)); the contract's division of labor, cheaper-sessions clause, exit conditions and § Punch list; the doctrine's § Seaworthy and § Handback; Part 0's sea-trial term and the campaign's Movement E (operator ratification); RO-7's persona exit number; `gz-rnd`'s both-sides rule; the vocabulary crosswalk; from 2026-10-27: the MX model and the two-way mode contract by decorator, the matrix rows ruled (B1, B11, B12, C1, C5, C10, C11, C12), the RO-12 row and the contractor brief's order | operator, questions 1–24; rulings of 2026-10-26/27 |
| 5 | one-shot refactoring | commissioned | the two-way mode contract across every control, monitor, alarm and safeguard: each module onboards its MEL entry, takes the standby level command from the central condition signal at its place of call, and reports suitability for function through its built-in self-test (operator: *"a MASSIVE refactor, but it is the best way that I can see"*) | RO-13 after RO-12, in tranches by kind, a shrink-only baseline of controls with no MEL entry closed at zero (ruled 2026-10-27); route chosen for the design (*"not be so parsimonious or urgent to get back underway"*); a self-test chore remains an advise-only candidate for row 3 |
| 6 | no action | commissioned | C13 (defined in canon); the handoff not renamed; the GHI not renamed; no separate pipeline design; the not-from-the-start question | each ruled in its own entry; collected 2026-10-27 |

## Close

**Challenge restated** (2026-10-27, deliberately, at the close). gzkit was about to run safe
mode's repair and restoration work as prose prompts. The problem is wider than the two contractors.
gzkit had no governed apparatus for maintenance work: no positions kept apart by mechanism, no
record of what was isolated, no inspection independent of the performer, and no closure a reviewer
witnesses. Its controls carried no contract for the condition they run under, so the drydock
demoted them from outside, and a control cannot know it has been demoted. The run defines three
things from the naval and aviation maintenance texts: the apparatus (the contractor kit, RO-12);
the two-way mode contract every control carries (RO-13 for what exists, and a standing design
requirement for what is built next); and a chore that hunts the same failure elsewhere. The
original question, *"How many other poorly-handled functions and processes of MAJOR consequent"*,
is answered by that chore, not by this run.

**Frontier.** Empty, 2026-10-27: every matrix row ruled, the two subjects the operator opened ruled, placement ruled, and all six disposition rows carry a decision.

**Review.** Written at `docs/rnd/contractor-kit/review.md` (2026-10-27); awaiting the operator's read before sign-off.

**Sign-off.** Not yet put.

## What this record does not license

No repair order, persona, skill, verb or chore is authored by this run. Rows 3 and 4 await the
operator's go on the row once their shape is defined here.
