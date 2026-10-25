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

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | | | |
| 2 | GHI / direct fix | | | |
| 3 | chore | commissioned | the vibe-coded and underbaked audit chore | operator directed it, 2026-10-25 |
| 4 | control surface, rule, doc, skill, hook | commissioned | the contractor kit, shape open | operator ruled "A" |
| 5 | one-shot refactoring | | | |
| 6 | no action | | | |

## Close

**Challenge restated.** Open.

**Frontier.** Open.

**Review.** Not yet written.

**Sign-off.** Not yet put.

## What this record does not license

No repair order, persona, skill, verb or chore is authored by this run. Rows 3 and 4 await the
operator's go on the row once their shape is defined here.
