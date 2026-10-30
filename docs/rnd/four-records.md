# R&D run — four-records

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-10-30T08:55Z.

**Challenge.** How the four records of the broader model (catalog item, feature/value bundle,
work package, release package; stand-in names, locked 2026-10-30) form a system, and which
well-known shapes from the literature fit them. Operator g0, verbatim:

> yes, those are the four, let's first try to map them to what we used to have. then, let's take
> ALL FOUR and re-enter rnd to find how they form a system. and, as you have already
> recommended/attempted, lets try to find good concepts from the literature that can help apply
> well-known shapes and concepts that might fit. If we can't find them, we stick to these first
> principles approaches and proceed with the generic designs.

---

## source · the operator's packaging model

Operator g0, current conversation (drydock RO-11 review) · read 2026-10-30.

> the release package is the current shopping cart for THIS ORDER. it will, alone, drive the next
> release (minor). that is clear. but what I am searching for is a feature package/bundle so that a
> set of REQs have a conhesive package (like my mADRs) that is used to describe why these belomg
> together. I might place that, and realted things, and whatver is needed to drive the relaese into
> that relaese shopping cart. sometimes I put prepared meals into the cart (the feature
> package/bundle (mADR), sometimes I put in raw ingrediens, etc. the release package is the shoppomg
> cart, the requirements catalog is the items and sone items come in packs/kits of the feature
> bundle items. I am struggling to find the containers for these things, which is why we are in
> drydock. the ADR + OBPI system was failing. The OBPI, was NOT failing, at all actually, but
> placing them in ADRS, and pegging a release to that ADR was. I am still wanting for a good
> comprehensive design that identifies all of these pieces and I still hope that
> common/best/well-known practices exist "out there" to address these. In the meantime, we seem to
> be working through a "first principles" way of doing this.

The operator's own account of the problem: four containers, one of them (the bundle) missing.

## source · why the mADRs were valuable, and how they broke

Operator g0, current conversation · read 2026-10-30.

> the strength of my old misused adrs is that they bounded the intentions and expected value of
> grouped/packaged requirements. by sitting together, the misused adrs would tell the story of why
> these features, together, advanced gzit (or an adopter's features) in a meaningful way. I really
> just needed a "bag" of a release plan/package that could keep all of the adr plus needed new
> items (corrections, scaffolds, shims, prerequisites, sidecars, twin/adjent adrs, etc. I started
> to frankenstein/morph these adrs to allow for that and it weakened the adr and became farcical.

And, earlier the same session:

> I was pre-registering releases in ADRs because I was naive about how linear I imagined the work
> would be. However, emergence and surprise taught me that I'd suddenly need other things (ADR
> bundles) to be in place PRIOR (as prerequisites) an ability to achieve that value.

The bundle's asset (bounded intent and value) and the two failure causes (release pegging,
emergence forced into the bundle).

## source · on framing the questions

Operator g0, current conversation · read 2026-10-30.

> I keep on giving you this context and background as your multiple choice questions sometimes
> reduce or shape the solution in ways that assume we fully understand (and have decomposed) the
> problem and that may not be the case.

Binds this run's interrogation: bounded choices only once the answer space is actually bounded.

## source · on the candidate shapes offered so far

Operator g0, current conversation · read 2026-10-30.

> I appreciate each of the alternatives you offered but do like any of them. I do like gherkin, but
> that is somewhat insufficient and is better as the BDD validation we already use/do. I do think
> agile's feature/epic is useful but plays too heavily into agile's "baggage" as well.
> feature/value bundle, for now, is our best stand in, and articulating our "four records," even
> with stand-in names, is the most import outcome of this "pause" I have created in out flow.

Gherkin stays BDD validation; SAFe-style Feature/Epic is judged to carry agile's baggage. The
research below must look past both.

## source · the four records, locked, and their mapping to the ADR/OBPI system

`docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Rulings of 2026-10-30, entries *The
four records, locked as the broader model, with stand-in names* and *The four mapped to what gzkit
had* · read 2026-10-30.

> They are: (1) the **catalog item**, an outcome and its REQs, filed by
> product responsibility, admitted on the operator's word, naming its source; (2) the
> **feature/value bundle**, a named set of requirements with the bounded story of why they belong
> together and the value they bring when realized together, with no version, release or order, able
> to wait in a pool; (3) the **work package**, the OBPI's essence carried forward, one outcome
> delivered against a frozen baseline through task cards and closed by Gate 5; (4) the **release
> package**, the shopping cart for one order, holding bundles whole or in part, loose items and
> whatever the release needs (corrections, scaffolds, shims, prerequisites), alone driving the next
> minor release and carrying the version. The ADR stays a decision record outside the four. Left
> open for R&D: the names; whether a bundle holds only admitted items; whether an item may sit in
> more than one bundle; how a bundle's promised value is checked against what landed; how
> prerequisites relate to the bundle that needs them; the pool's form for bundles.

> The ADR did five jobs, and
> only the decision stays with it [...] Exposed for the R&D: the checklist joined the bundle
> to its items, which nothing in the new model does yet; and emergence had no place but the ADR,
> where the new model puts prerequisites as loose items in the cart.

The locked model and its six open points are this run's starting frontier.

## source · the requirements model (gzkit canon side)

`docs/governance/ieee/requirements-model.md` · read 2026-10-30 (the records table, decisions 2,
4, 6, 7 and 9 read in full this session; the remainder to be read in full before any mapping onto
it is put to the operator).

> **Sources it composes.** The FDAU roadmap-and-backlog method (`tvproductions/xplane-fdau`, the
> retrospective specification *backlog-governance-model*), Superpowers Backplane
> (`docs/superpowers-backplane/governance.md` in that repository), and the operator's note *Bodies of
> Knowledge for Agentic Software Work* (2026-10-16: SWEBOK, PMBOK, SEBoK, BABOK, the ASQ CQE body of
> knowledge, and cybernetics as a lens).

> | Release Package | 1, with its events in 2 | the version | Which outcomes a version is planned to carry; mutable while a target | what is planned to ship |

The canon the four records amend. Its bodies of knowledge are the first places the literature
search looks.

## source · candidate shapes from the literature (UNREAD, hypotheses only)

Named from the agent's own knowledge in session on 2026-10-30, not yet read. Nothing below is a
decision and nothing commissions anything until a primary text is read.

- Denne and Cleland-Huang, *Software by Numbers* (2003), and the Incremental Funding Method:
  Minimum Marketable Features and architectural elements, sequenced by precedence.
- Shape Up (Basecamp): the pitch and the betting table.
- SAFe's Feature, Epic, Enabler and benefit hypothesis (the operator judges it to carry agile's
  baggage; read for mechanics only).
- Release-planning research: the Next Release Problem (Bagnall, Rayward-Smith and Whittley, 2001);
  requirement interdependencies in release planning (Carlshamre and others, 2001); Ruhe's release
  planning.
- PMBOK's work breakdown structure: work package, planning package, control account, WBS dictionary.
- Manufacturing bills of material: the kit and the phantom assembly.
- Feature models of software product lines (Kang and others, FODA, 1990).
- ISO/IEC/IEEE 29148 (held in the repository at
  `docs/rnd/renewing-vows/sources/std-iso-iec-ieee-29148.md`).

## source · the research pass, landed verbatim

`docs/rnd/four-records/sources/` · written by a research subagent 2026-10-30, every file read in
full by the run's agent the same day. Primary unless marked. Refusals were recorded and not worked
around. Each file carries its own URLs, access dates and verbatim quotations; the lines below cite,
they do not summarize.

- `fdau-backlog-model.md` (primary, the model's lineage): *"A **feature record** is the proposed
  local artifact name for a capability or reviewable outcome."*; *"A **release record** selects
  completed outcomes, checks compatibility and release gates, and receives a version."*;
  *"`candidate_release` is optional, mutable planning data. `released_in` is historical evidence
  added after publication."*; *"A pool idea without a chosen solution belongs in a capability pool,
  not in an accepted-decision register."*
- `backplane-governance.md` (primary, the model's lineage): *"A grouping capability is not an
  implementation leaf. A small feature may itself be the bounded outcome; do not create redundant
  layers."*; *"A milestone groups targets; it does not authorize publication."*
- `shape-up.md` (primary): *"There are five ingredients that we always want to include in a pitch:
  Problem [...] Appetite [...] Solution [...] Rabbit holes [...] No-gos"*; *"The pitch defines a
  specific payout that makes the bet worth making."*; *"Now that we've written a pitch, where does
  it go? It doesn't go onto a backlog."*
- `ifm-mmf.md` (primary texts NOT read, paywalled; definitions secondary): *"Minimum Marketable
  Features, or MMF for short, indicating that they contain strongly-related software features that
  can be quickly delivered and that are valued by customers"*; *"the architectural infrastructure,
  i.e. the set of basic features that offers no direct value to customers, but that are required by
  the MMFs"*.
- `release-planning.md` (EVOLVE primary; NRP abstract primary; Carlshamre and the theme papers
  secondary, one refused): *"The technical precedence constraints relate to situations where one
  requirement cannot be implemented until another is completed or where one requirement is
  implemented in the same increment as another one."*; theme, secondary: *"the requirements within
  a theme would be preferably delivered or postponed together"*.
- `wbs.md` (DoD EVMSIG and NASA primary; PMI not read, one refused): *"PLANNING PACKAGE (PP) — A
  logical aggregation of future work within a control account that cannot yet be planned in detail
  at the work package or task level."*; *"common elements of work must be included that are not
  necessarily product-oriented."*
- `bom-kits.md` (vendor documentation, primary as to Oracle only; APICS not read): *"A model bill
  [...] also specifies mandatory components or included items that are required for each
  configuration of that model. You do not order or build the model itself: you order and build
  configurations of the model."*; *"A configuration bill (a type of standard bill) is a set of
  option choices made from a model bill"*; *"As a subassembly, however, they lose their identity as
  distinct assemblies and are a collection of their components."*; *"The cost rollup treats phantom
  assemblies the same as regular assemblies. The phantom is treated as a distinct entity"*.
- `feature-models.md` (FODA primary, one copy refused): *"All optional and alternative features that
  must be selected when the named feature is selected must be defined using the "requires"
  statement."*
- `iso-29148-grouping.md` (sample clauses primary; 5.2.6, 5.2.8, 9.6.9 not read): the defined terms
  read include no named grouping of requirements by value, release or increment.
- `other-candidates.md` (DoD instructions and TOGAF refused or unread; one CRS report secondary).

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | ADR / OBPI | | | |
| 2 | GHI / direct fix | | | |
| 3 | chore | | | |
| 4 | control surface, rule, doc, skill, hook | | | |
| 5 | one-shot refactoring | | | |
| 6 | no action | | | |

## Close

**Challenge restated.** Not yet.

**Frontier.** The six open points of the locked model, and how the four records relate as one
system.

**Review.** Not yet written.

**Sign-off.** Not yet put.

## What this record does not license

No ADR, OBPI, chore, schema, verb or record type is started by this run. The four records'
stand-in names are not ruled names. Every row above awaits the operator's go.
