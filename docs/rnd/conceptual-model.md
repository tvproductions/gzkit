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
