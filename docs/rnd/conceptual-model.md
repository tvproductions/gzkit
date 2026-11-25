# R&D run — conceptual-model

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-11-25T00:36Z.

**Challenge.** Opened from the drydock taxonomy walk, paused at W51
(`docs/governance/drydock-taxonomy.md`). Through T21 to T30 the agent kept putting A/B/C options
on concepts it had not separated, and each option carried a conflation forward. Operator g0,
verbatim:

> you keep offering easy solutions, but we are learning that there is a signifocant amount of
> conflation here

> record the T30 rulings first, then pause for the R&D (this is classic LLM drift: a vibe coded
> variant of whimsy and copycat convenience)

The subject is a population the project carries: why one term or one record keeps carrying two
or more concepts across gzkit's governance, and how the conceptual model is to be separated
before any further naming ruling.

---

## source · the taxonomy walk's pause

`docs/governance/drydock-taxonomy.md` § 9, W51 · read 2026-11-24

> The walk pauses here. T30's sub-ids, T37, W9's cardinality, a FIX's source, the GHI's kind and
> the construction reading of RP-12's rulings go to the conceptual-model R&D, which W15's
> documentation run follows or absorbs as that R&D rules. W44 to W50 were ruled in the same
> vocabulary and are open to that R&D's review. T31 to T36 and T39 stay unruled.

The walk's open rows are this run's inputs, and the rulings W44 to W50 are under review here.

## source · the commissioned DDD-discipline run, never opened

`docs/rnd/design-amendment.md`, decision *Q8 — DDD's language arm gets its own R&D run* · read
2026-11-25

> **commissions:** a separate R&D run on DDD discipline (why the language arm lapsed, where
> the glossary lives, how it stays current beside TDD and BDD, and how it fits the hexagonal
> rule and the ontology). Only the operator can open it.

> Operator, next turn, verbatim: *"you keep the need for a DDD run in both a h/o AND in the
> magna carta. I am NOT waiting for post 1.0 for that."*

Measured 2026-11-25: `docs/rnd/` holds no DDD run. The run commissioned on 2026-09-27 to find
*"why the language arm lapsed"* was never opened, and the subject of this run is that lapse's
effect.

## source · the glossary's unsettled home

`docs/governance/rnd-discipline.md` § `term` and `insight` are not entry kinds · read 2026-11-25

> **The glossary's home is unsettled.** The only glossary today is
> [`PRD-GZKIT-1.0.0.md` § 2.1 Ubiquitous Language](../design/prd/PRD-GZKIT-1.0.0.md). The
> 2026-09-17 ruling named `GLOSSARY.md` at the repo root, on the false premise that gzkit had
> no glossary; that file was never created. The DDD-discipline R&D run decides the home

`docs/design/prd/PRD-GZKIT-1.0.0.md` § 2.1 · read 2026-11-25

> gzkit-namespace glossary entries. Each entry conforms to UbiquitousLanguageTerm schema
> (ADR-0.0.43): term, scope (cross-cutting | <bc-slug>), definition (≥10 chars), provenance
> (list of ADR IDs).

## source · the cascade puts the language first

`.gzkit/rules/hexagonal-architecture.md` § The cascade & domain cohesion · read 2026-11-24

> 1. **DDD** — model the domain in governance's ubiquitous language (the drydock's
>    ruled record names), never framework-generic nouns. Subdomains are discovered in
>    admitted REQs and bounded contexts designed over them; **the ontology depicts that
>    model, it does not define it**.

## source · position, role and crew

`docs/governance/GovZero/command-doctrine.md:55-60` · read 2026-11-24

> - **Position.** An obligation and a role to fulfil it. **Role.** What the position gives its
>   holder to fulfil the obligation; it has bounds and auspices, and the holder has no
>   authority apart from it. **Crew.** The actor implementing within the role's bounds and
>   under its auspices. Every agent is crew, the orchestrating session included. *(Ruling of
>   2026-10-08: 'the position is an obligation and a role to fulfill the obligation, the crew
>   is the actor implementing within the bounds and auspices of that role'.)*

## source · the FIX

`docs/governance/drydock-taxonomy.md` § 9, W6 · read 2026-11-24

> the operator named a new concept. Verbatim: *"okay, then we need a new concept, how about
> FIX?"*, and, confirming the agent's reading (*FIX as the repair requirement, its own `FIX-<n>`
> series, living in the repair order, sharing the base requirement's shape and proof path*):
> *"yes, that's the concept ==> fix is the repair requirement, otherwise, we have a bad name and
> semantic collision."* This reverses RP-12 ruling 45's one shared `REQ-<n>` sequence.
> `REQ` names a catalog requirement only.

`docs/governance/ieee/requirements-model.md` § 12 still reads, 2026-11-24: *"both live in
`data/catalog/reqs.json`, one `REQ-<n>` sequence, each marked `"specialization": "catalog"` or
`"repair"`"*, the design W6 reversed.

## source · the problem report and its unratified scheme

`.gzkit/skills/ghi-close/references/problem-report-states.md`, decision B12, as quoted in
`docs/governance/drydock-taxonomy/sources/gather-F-rnd-ghi-chores-hex.md` § 10c · read 2026-11-24
(secondary: the gathering's quotation, not the reference file itself)

> | `classified` | "categorized in accordance with an established classification scheme" — its Step 1 class label |

`.gzkit/skills/ghi-author/SKILL.md` Step 1 · read 2026-11-24

> | Defect | `defect` | Something observable is wrong, drifted, or inconsistent with canonical intent |
> | Enhancement | `enhancement` | Surface works as designed; the design could be tighter |
> | Investigation | `investigation` | Unknown root cause; the GHI is to find it, not fix it |

Measured 2026-11-24: 24 live labels (`gh label list`); the organization's native issue types are
Task, Bug and Feature; none of the last 200 gzkit issues carries one.

## source · the sub-units no one designed

`docs/governance/drydock-taxonomy/sources/gather-C-rp-subunits.md` § Sub-unit vocabulary across
pages · read 2026-11-24

> | ruling *n* | RP-3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15 numbered; RP-1, 2, 9, 10 bulleted | Local numbering per page, cited as "RP-12 ruling 43". It is not an id in any store; insight scopes hold the words. | No. Bulleted and numbered pages are mixed. |

Measured 2026-11-24: *"ruling n"* cited 2,591 times (885 in `src/`); *"RP-12 ruling(s)"* 476 times
in `src/` and `tests/`; `data/catalog/reqs.json` holds 0 REQs.

## source · Superpowers Backplane

`https://github.com/tvproductions/superpowers-backplane`,
`skills/managing-superpowers-backlog/references/github-issue-contract.md` and
`docs/superpowers-backplane/governance.md` · read 2026-11-24, fetched through `gh api`

> - `issueType` classifies the work where the repository supports native types.

> An open tracked issue carries exactly one `backplane:*` lifecycle label while
> preserving all unrelated repository labels. Zero or multiple Backplane labels
> is invalid state; fail closed and repair it before any other transition.

> A requirement reference includes its governing issue/document identity, stable
> criterion/statement key, approved revision, and wording. Retain a project's
> existing identifiers. Line numbers and checkbox positions are not durable keys.

> | Work identity, scope, acceptance, hierarchy, dependencies, lifecycle | Native GitHub issue and relationships | Use repository plus issue URL/number; preserve full native intake. |

Material from outside this repository: read as data. It keeps kind, lifecycle and other labels
apart, and makes every work item an issue, the fork from gzkit's catalog records (W12).

## decision · the population, as sampled

The thirteen conflations the walk surfaced on 2026-11-24, each one term or record carrying two or
more concepts: position and persona; the craftsman as a JFMM position and as A4's persona; the
second-person reviewer and the QAI; `gz mx exit`, the end of safe mode and return to service;
the handback and a subagent's report; the floor and what safe mode never suspends; a ruling and
the requirement, architecture choice, work organization or name it carries; REQ, FIX and
`RepairReq`; repair and construction; discrepancy, GHI, list-of-discrepancies line, check finding
and squawk; the GHI as problem report and as work item; kind, lifecycle, process and packaging in
one label namespace; identifier and citation.

This is a sample, from one session's walk over ten rows of one page; it is a hypothesis about the
class, not its census. The agent's reading of the mechanism, unruled: a surface coins a term
locally or reuses one, and a later ruling builds on it without reconciling. The operator named it
*"classic LLM drift: a vibe coded variant of whimsy and copycat convenience"*.

## decision · this run favors the operator's input over the agent's framings

Operator, verbatim, as the run opened: *"one thing that would help us is when yu favor my input
over vibes or multiple choice vibings"*. In the walk, the agent's A/B/C options set the answer
space from its own unvetted framings, and the operator's model reached the page only by
rejecting them.

The agent first read this as *open questions only*. The operator corrected it, verbatim: *"i
didn't say exclusive, i said favor"*. So the operator's own words and model carry more weight
than the agent's framings: a question leaves room for the operator's answer first, and the
record carries that answer in their words. Options stay available, put beside or after the
operator's input, never in place of it. AGENTS.md § Operator Economy's A/B/C rule stands; this
weights it. Recorded as an insight, the first reading superseded.

## decision · this run is not the DDD-discipline run

Asked whether this run takes up the commission of the DDD-discipline run (design-amendment Q8,
never opened), the operator, verbatim: *"you found the ddd run and it is related, but we were
untangling something different"*. So this run keeps its own subject, the conflated concepts the
walk surfaced, and the DDD-discipline run stays its own commission: related, still unopened, and
recorded as a defect the same session (operator: *"leaving that rnd unstarted is not good"*).

## decision · the knot: the GHI and what a discrepancy is

Asked what was being untangled and where to start, the operator, verbatim: *"the GHI and what a
discrepancy is"*. The frontier is computed from that.

## source · the discrepancy, in the borrowed text

`docs/rnd/contractor-kit/sources/14cfr43.md`, 14 CFR § 43.11(b) · read 2026-11-25

> (b) Listing of discrepancies and placards. If the person performing any inspection required by
> part 91 or 125 or § 135.411(a)(1) of this chapter finds that the aircraft is unairworthy or does
> not meet the applicable type certificate data, airworthiness directives, or other approved data
> upon which its airworthiness depends, that persons must give the owner or lessee a signed and
> dated list of those discrepancies. For those items permitted to be inoperative under
> § 91.213(d)(2) of this chapter, that person shall place a placard, that meets the aircraft's
> airworthiness certification regulations, on each inoperative instrument and the cockpit control
> of each item of inoperative equipment, marking it "Inoperative," and shall add the items to the
> signed and dated list of discrepancies given to the owner or lessee.

`docs/rnd/contractor-kit/sources/14cfr91-119-121-maintenance-gaps.md`, 14 CFR § 91.405 · read
2026-11-25

> (a) Shall have that aircraft inspected as prescribed in subpart E of this part and shall between
> required inspections, except as provided in paragraph (c) of this section, have discrepancies
> repaired as prescribed in part 43 of this chapter;

In the text, a discrepancy is what an inspection finds against approved data, listed to the owner,
and repaired or placarded.

## source · the problem report, in the borrowed text

`docs/rnd/renewing-vows/sources/us-gov-faa-ac-00-71-open-problem-reports.md` (AC 00-71, read in
full 2026-10-08 from the operator's PDF) and its quotation in
`docs/rnd/contractor-kit/sources/inventory-aviation-civil.md` · read 2026-11-25

> **Problem report (PR); open problem report (OPR); OPR summary report** (aircraft certification /
> development assurance — not in-service maintenance)
> - "Problem report (PR) – A means to identify and record the resolution of anomalous behavior,
>   process non-compliance with development assurance plans and standards, and deficiencies in life
>   cycle data (adapted from DO-178C/ED-12C)." — AC 00-71 § 3.1 [S7]

> ### The four classifications (§ 3.3)
>
> Significant – assessed at the product, system, or equipment level, a PR that has an actual or
> potential effect on the product, system, or equipment function that may lead to a Catastrophic,
> Hazardous, or Major failure condition, or may affect compliance with the operating rules.
>
> Functional – a PR that has an actual or a potential effect on a function at the product, system,
> or equipment level.
>
> Process – a PR that records a process non-compliance or deficiency that cannot result in a
> potential safety nor a potential functional effect.
>
> Life Cycle Data – a PR that is linked to a deficiency in a life cycle data item but not linked to
> a process non-compliance or process deficiency.

> 4.2.1 The most important clarification when compared with the former classification scheme is to
> give each OPR a single classification using a given order of priority

The inventory itself marks the problem report as development assurance, not in-service
maintenance. Its classification scheme comes with it; B12 took the states and not the scheme.

## source · gzkit's GHI, squawk and list of discrepancies

`docs/governance/safe-mode-doctrine.md:15` · read 2026-11-25

> The squawk is the on-demand repair of one reported discrepancy: the GitHub issue is the write-up,
> and a hangar visit or a direct fix answers it

> In its role the GitHub issue is a problem report (AC 00-71 § 3.1), and its states are recorded,
> classified, resolved and closed

`.gzkit/skills/ghi-close/references/problem-report-states.md` · read 2026-11-25

> | **classified** | *"A problem report that has been categorized in accordance with an established classification scheme."* | carries its `ghi-author` Step 1 class label and its class of failure |

`docs/rnd/contractor-kit.md`, decision *the punch list becomes the list of discrepancies* · read
2026-11-25

> - **B′.** A **list of discrepancies**: one line per discrepancy, graded *blocks return to service*
>   or *due by a named event*, cleared with its evidence.

and decision *three records* · read 2026-11-25

> the punch list (outstanding deficiencies, what is left broken and the inspector's rejections;
> cleared before return to service)

gzkit's canon makes the GHI at once the write-up of one reported discrepancy (in-service
maintenance) and an AC 00-71 problem report (development assurance), with its *classified* state
pointing at ghi-author's unratified table; and it keeps a second home for discrepancies, the list,
holding what the work leaves broken and the inspector's rejections.

## decision · a discrepancy combines the in-service and the development-assurance senses

Asked what a discrepancy is in gzkit, after both texts above were quoted, the operator, verbatim:
*"do not be afraid to offer me options. it is a combination of both of these: 14 CFR § 43.11(b),
§ 91.405) and AC 00-71 § 3.1"*. So a gzkit discrepancy carries § 43.11(b)'s measure (a finding
against the approved data the article depends on, listed, then repaired or placarded) and
AC 00-71 § 3.1's objects (anomalous behavior, process non-compliance, deficiencies in life cycle
data). The method decision above stands with the operator's emphasis: options are welcome, put
with the operator's input favored.

## decision · a discrepancy is measured against declared intent of record

Question: what is the approved data a gzkit discrepancy is measured against? Options put: A,
declared intent of record, anything the operator approved (the catalog's REQs and FIXes, ADRs,
the PRD, ruled canon: rules, doctrine, AGENTS.md, the contract), the correction doctrine's
*"original declared intent"*, with behavior measured against requirements, process against
process canon and life-cycle data against its ruled standards, and unruled prose not approved
data; B, the requirement records only; C, anything documented, ruled or not. Recommended A.
Operator: *"A: Declared intent of record"*.

So a gzkit discrepancy is a finding that gzkit's behavior, process or life-cycle data does not
meet its declared intent of record.

## source · the discrepancy line as built

`src/gzkit/mx/discrepancies.py:1-14` · read 2026-11-25

> The list of discrepancies' writer and reducer (RP-12 O4 task 2).
>
> `docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the list of discrepancies
> is ledger events, rendered as a view (ruling 9). A `discrepancy_recorded` event books
> one line, graded *blocks return to service* or *due by a named event*, the event named
> in text (ruling 179), always on an order (ruling 178); a `discrepancy_cleared` event
> clears it with its evidence. [...] The coordinator alone
> clears a line, citing an entry or a cleared tag of its package, or an open GitHub
> issue the line was filed as (rulings 172 and 180)

`src/gzkit/events.py:2117-2123` · read 2026-11-25

> DiscrepancyGrade = Literal["blocks-return-to-service", "due-by-event"]
> [...]
> DiscrepancySource = Literal["left-broken", "inspector-rejection", "found-in-work"]

## decision · the GHI is the discrepancy's record

Question: what is the GHI to a discrepancy, given its two homes today (the GHI as the squawk's
write-up, and the `DSC-` line on an order)? Options put: A, every discrepancy however found is
one GHI, its write-up and its record, its route and grade properties of the GHI, the list of
discrepancies a view over GHIs, `DSC-` lines retired and a find in the work filing a GHI; B, a
`DSC-` line while its order can clear it, a GHI once it outlives the order; C, one GHI as
§ 43.11(b)'s signed list carrying several discrepancies. Recommended A. Operator: *"A: GHI is its
record"*.

So one discrepancy is one GHI. The list of discrepancies, the `DSC-` record and RP-12 rulings 9,
172, 178 to 181 meet this ruling on the separated model; their repair is diamond 2.

## source · the classifications a GHI already carries

Operator, as the agent put AC 00-71's scheme: *"be careful here, we have some classification of
ghi's. also, this: https://github.com/tvproductions/superpowers-backplane"*. Read in full
2026-11-25: `.gzkit/skills/ghi-triage/SKILL.md` (242 lines), `docs/rnd/ghi-landscape-reorganization.md`
(304), `docs/rnd/ghi-batch-closure.md` (396); `.gzkit/skills/ghi-author/SKILL.md` Step 1 and
`.gzkit/skills/ghi-close/SKILL.md` Phase 1 step 2 and Phase 4 step 8 read at those sections.

`ghi-author` Step 1:

> 1. **Classify the GHI** using the table below. Pick exactly one; a single GHI is one class.

with Defect, Enhancement, Investigation, and *"Secondary labels (binding — additive, not
exclusive)"*: `runtime`, `tech-debt`, `security`, `eval-feedback`.

`ghi-triage` Step 1 and Step 2:

> Each record contains: `number`, `title`, `labels`, `klass` (one of
> `defect`/`enhancement`/`investigation`/`chore`/`unlabeled`), [...] `route`, `urgency`

> | `severity` | one of `blocking` (current work fails), `degrading` (succeeds but produces drift), `latent` (deferrable) |
> | `readiness` | optional; one of `ready`, `ruling`, `sequence`, `design`; on every entry or on none (a partial set exits 1) |

`ghi-landscape-reorganization` § source · family taxonomy of the open queue:

> | F1 doctrine-declared-without-mechanism | 14 — [...] | A binding claim in one layer; the witness is absent, narrower than the claim, or never invoked |

(twelve families, F1 to F12, each a shared root-cause mechanism; *"Family membership is a
*reading*, not a measurement."*)

`ghi-close` Phase 1 step 2, *"Classify the GHI's prescriptive shape"*: single prescribed fix;
multiple options with a dominant choice; multiple options with none; investigation;
already-resolved; forward-reference tracker. Phase 4 step 8, the dispositions: `fixed`,
`superseded`, `withdrawn`, `duplicate`, `won't-fix`.

`ghi-batch-closure` § decision · this run's terms are held:

> - **readiness** — whether an open GHI can be ended by an agent now: R1 ready, R2 ruling,
>   R3 sequence, R4 design. _Avoid_: *route* (which `ghi-triage` already uses for authority).

Backplane, measured 2026-11-25 over its own last 24 issues: one carries a native type
(`Feature`); 23 carry none, most with `backplane:backlog`. Its contract keeps kind in the native
type and lifecycle in one label; its own queue exercises little of either.

So a GHI is classified today along at least nine axes by five surfaces: class (Defect,
Enhancement, Investigation), secondary properties (runtime, tech-debt, security, eval-feedback),
severity (blocking, degrading, latent), readiness (ready, ruling, sequence, design), route
(direct fix or OBPI), family (F1 to F12, a root-cause reading), prescriptive shape (six),
disposition at close (five) and problem-report state (B12's four), beside the packaging label
`repair` and the script's `chore` and `unlabeled` classes. Three of them are called *class*.

## decision · a GHI's axes fall in three groups, each axis with one name and one home

Question: how are the GHI's classifications organized, given that they answer what the
discrepancy is, where it stands and how it is ended? Options put: A, three groups by question:
*what it is* (set when the report is classified, B12's state, and fixed after: class, the
secondary properties, severity, family), *where it stands* (changing over its life: the
problem-report state as one exclusive lifecycle, Backplane's rule, and readiness), *how it is
ended* (route, prescriptive shape, disposition), each axis with one name and one home, *class*
naming one axis only, and `repair` and `chore` leaving the GHI's classification; B, one kind and
one lifecycle only, the rest working notes of triage and closing; C, the names untangled and
the structure kept. Recommended A. Operator: *"A: Three groups, one home each"*.

## decision · a discrepancy's class is behavior, process or life-cycle data

Question: what are the class values? Options put: A, the three objects of the ruled definition:
behavior (gzkit does not do what its intent of record says), process (the work did not follow
its process canon), life-cycle data (a record, doc, schema or requirement is deficient), effect
left to severity so the axes do not overlap, investigation read as the *recorded* state before
classification, and enhancement retired as no discrepancy; B, AC 00-71 § 3.3's four by priority,
Significant read for gzkit as touching the floor, what safe mode never suspends or an external
contract; C, A's three objects with a significant flag. Recommended A. Operator: *"A:
Behavior/process/data"*.

This takes AC 00-71 § 3.1's three objects and departs from its § 3.3 scheme, which splits
behavior by effect; gzkit carries effect on severity instead. *Enhancement* and *investigation*
leave the class axis: the first is no discrepancy, the second is a state.

## decision · the class lives in exactly one namespaced label

Question: where does the class live? Measured: native issue types are organization-wide, and
`tvproductions` holds about twenty repositories beside gzkit; its types are Task, Bug and
Feature. Options put: A, exactly one `class:behavior`, `class:process` or
`class:life-cycle-data` label on a classified GHI, Backplane's exactly-one rule on the class axis
(zero or two invalid, failing closed), no organization-wide change, and a GHI with no class label
in the *recorded* state; B, organization issue types; C, a `Class:` line in the body. Recommended
A. Operator: *"A: One namespaced label"*.

## decision · the lifecycle state is derived, never stored

Question: where does B12's state live? Options put: A, derived from facts that exist, with no
lifecycle label: *recorded*, open with no class label; *classified*, open with one; *resolved*,
open with a landed `(GHI #N)` commit; *closed*, closed on GitHub with the review comment on
record; B, exactly one `state:*` label on an open GHI, Backplane's rule; C, a ledger event per
transition with labels as display. Recommended A, under the state doctrine (a derived view traces
to Layer 1 or 2). Operator: *"A: Derived, not stored"*.

## decision · how a discrepancy surfaced is one of six, in one `found:*` label

Question: what is the surfacing route, given its scattered values (the `DSC-` sources
left-broken, inspector-rejection and found-in-work in `src/gzkit/events.py:2123`; the doctrine's
reported squawk and scheduled check finding; the `eval-feedback` label, which
`src/gzkit/commands/validate_commit_trailers.py:122` reads for the `Eval-feedback-source:`
trailer)? Options put: A, one closed set of six (reported, found-in-work, left-broken,
inspector-rejection, check-finding, eval-feedback) in exactly one `found:*` label, `eval-feedback`
becoming `found:eval-feedback` with the trailer validator repointed in the same commit and the
trailer kept; B, two values, reported or found; C, no route axis, provenance in the body.
Recommended A. Operator: *"A: Six values, one label"*. The route sits in the *what it is* group,
set once.

## source · the grades a finding can carry

`docs/rnd/contractor-kit/sources/inventory-navy-jfmm-v5.md:476, 478` · read 2026-11-25

> | Minor findings | "Minor deficiencies which do not affect certification of a component or system or the nature of the finding does not warrant specific follow up action, may be entered into a deficiency-tracking system for trend analysis or corrected without causal analysis or long-term corrective action unless recurring in nature." | I-9.3.1.a |

> | Certification-affecting findings | "All deficiencies which affect certification must be categorized as "IMMEDIATE CORRECTIVE ACTION"." | I-9.4.1.b(1) |

with ghi-triage's severity (*blocking*, *degrading*, *latent*, quoted above) and the `DSC-` grade
(`DiscrepancyGrade = Literal["blocks-return-to-service", "due-by-event"]`, quoted above).

## decision · no fixed severity axis; MX reads the hold on return to service

The agent put severity as a fixed grade of significance beside triage's urgency. The operator
asked, verbatim: *"why are these two dimensions needed, how will they help mx work?"*. Tested by
what reads each: the hold on return to service (*blocks-return-to-service* or *due-by-event*) is
read by `gz mx exit` and the handback, and B′ asks root cause and corrective action of a blocking
line; triage's blocking, degrading and latent order what to pull next, recomputed each run and
never stored; significance has no reader, since B′ ties causal analysis to blocking or recurrence
and recurrence is measured (`gz insights recurrence`), the nearest live consumer being the
`security` label's heightened Gate 5 walkthrough. Put to the operator: no fixed severity axis,
urgency left to triage, and the hold on return to service the grade MX uses. Operator, verbatim:
*"yes, record that and move to readiness"*.

So *severity* leaves the *what it is* group. The hold on return to service belongs to a GHI
carried by a return to service package and sits in *where it stands*. Triage's per-run grade is
urgency.

## decision · readiness stays triage's per-run reading, settled by canon

Canon rules it, so nothing was put: `docs/rnd/ghi-batch-closure.md` Q5 (2026-09-27, *"Enum in
input; rulings asked live (Recommended)"*) makes readiness (*ready*, *ruling*, *sequence*,
*design*) one enum in triage's rank input, never stored on the GHI. Under the reader test the
operator applied to severity, it has readers: triage's landing queue and ruling docket, and, in MX
terms, *ready* marks what a coordinator can draw into a repair order now. It changes with every
ruling and landing, and that run found stale blockers on nine issues, so it stays a per-run
reading in *where it stands*.

## decision · a GHI carries no stored route

Question: what is a GHI's route, given that Defect-fix routing's direct fix or OBPI reads every
issue *direct-fix* (*"authority, not readiness"*, ghi-batch-closure), that W10 puts all repair on
one discipline with the alarm test deciding line or out of service, and that construction never
comes through a GHI? Options put: A, route as the alarm test's answer, line or out of service,
Defect-fix routing's OBPI arm retired for GHIs; B, the size and surface test kept beside the
alarm test; C, no stored route, the coordinator deciding line or out of service under the alarm
test when drawing the GHI into work, the decision showing in which package carries it.
Recommended A. Operator: *"C: No stored route"*.

So route leaves the GHI's classification. Line or out of service is the coordinator's act under
the alarm test, recorded by the package that carries the GHI.

## source · GitHub's organization issue types

`https://docs.github.com/en/issues/tracking-your-work-with-issues/configuring-issues/managing-issue-types-in-an-organization`,
with the filtering pages it links, read 2026-11-25 through a `web-fetch` subagent; its report
quotes, held as the subagent's reading (secondary until re-read):

> "You can create up to 25 issue types that you can apply to issues."

> "Default issue types are included in every organization and user account... The default types
> are task, bug, and feature."

> "If you disable an issue type, it will not be shown and it won't be possible to set an issue to
> that type, but if you later decide to enable the issue type, it will be displayed again on any
> issues previously set to the issue type."

> "Filter for issues with a particular type: `is:open type:"Bug"`"

Not stated on the pages, per the report: whether a type can be scoped to some repositories, who
may manage types, what a deleted type does to issues carrying it, and whether an issue holds more
than one type. Measured locally 2026-11-25: `gh` 2.105.0 takes `--type` on `issue create`,
`issue edit` and `issue list`; gzkit's last 200 issues carry no type, and the sampled issues of
airlineops and flightops carry none.

## decision · per-issue native features first; class and found stay labels

The agent put prescriptive shape and disposition; the operator asked, verbatim: *"wouldn't we want
to use gh native features here?"*. Shown the native features (close reason with `--duplicate-of`;
timeline commit references; `blockedBy` and `blocking`; live relationships) and that
`.gzkit/rules/gh-cli.md` § Allowed commands permits none beyond `close --comment`, three options
were put: A, native first with labels only where no native feature exists, the rule widened;
B, native for closing only; C, A plus the class as an organization issue type. Asked *"tell me
more about option C"*, the agent read GitHub's documentation (source above) and reported its
gain (a native single-valued field, filtered in search and Projects) and its costs, chief among
them that types are organization settings an adopter's own administrator must add, while gzkit
ships to repositories it does not own through `gz init`. Operator, verbatim: *"ok, c is out
because of the adopter limitation, what was A?"*. A was restated with the adopter test applied:
a per-issue native feature needs no organization setting.

- **disposition**: the native close reason, *fixed* to completed, *duplicate* to duplicate with
  `--duplicate-of`, *superseded*, *withdrawn* and *won't-fix* to not planned; the close comment
  keeps the evidence and names which of the five;
- **resolved**: the timeline reference the `(GHI #N)` trailer leaves;
- **waits on another GHI**: native `blockedBy` and `blocking`, in place of blocker prose;
- **links between GHIs**: native relationships where one fits, comment prose only otherwise;
- **prescriptive shape**: not stored, ghi-close's working reading;
- **class and found**: one `class:*` and one `found:*` label each.

The agent corrected its own table: a package is a catalog record (W12), not an issue, so
parent and sub-issues do not carry a package's GHIs; the package record's `issues` field does.
The gh-cli rule's allowed list widens to the native verbs, each used only through `ghi-author`,
`ghi-close` or `gz wp`, which also brings `gz wp attach`'s `gh issue edit` (C11) inside it. Not
verified: blocked-by on GitHub Enterprise Server. Operator, verbatim: *"yes, A — record it and
move on"*.

**commissions:** 4 — `.gzkit/rules/gh-cli.md` § Allowed commands widened to the per-issue
native verbs; `ghi-author`, `ghi-close` and `ghi-triage` carry the fields as ruled. Defect-fix routing's OBPI arm has
no GHI destination under this run's rulings; its repair is diamond 2.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | catalog, packages, orders and decision records | | | |
| 2 | GHI / direct fix | | | |
| 3 | chore | | | |
| 4 | control surface, rule, doc, skill, hook | | | |
| 5 | one-shot refactoring | | | |
| 6 | no action | | | |
| 7 | further research | | | |

## Close

**Challenge restated.**

**Frontier.**

**Review.**

**Sign-off.**

## What this record does not license

No ADR, OBPI, package, chore, GHI or rename is started by this run. The taxonomy walk stays
paused at W51, and no row of the disposition map carries the operator's go.
