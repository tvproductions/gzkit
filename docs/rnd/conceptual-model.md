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
