# Review — four-records

A readable account of the [four-records R&D run](../four-records.md), written for the operator to
read before sign-off. It is a view over the record and holds no authority: where the two differ,
the record governs. Written 2026-10-30.

## The problem

The ADR/OBPI system was failing, and the operator located the failure precisely: *"The OBPI, was
NOT failing, at all actually, but placing them in ADRS, and pegging a release to that ADR was."*
The ADR was doing five jobs at once (a decision, a story of value, a list of items, a version, a
release gate), and emergence (corrections, scaffolds, shims, prerequisites, sidecars, twin ADRs)
had nowhere to go but into it, which *"weakened the adr and became farcical"*. What was worth
keeping was the misused ADR's bounded story: *"by sitting together, the misused adrs would tell the
story of why these features, together, advanced gzit"*. The operator was *"struggling to find the
containers for these things"*.

## The model

Four records, a loosening and renaming of the old system, *"not abandonment or greenfield"*.

| Record | Holds | Successor to |
|---|---|---|
| **REQ catalog** | what must be true: outcomes filed `family.capability.outcome`, REQs beneath each outcome; admitted on the operator's word, naming its source | the ADR's checklist items and the OBPI briefs' REQs |
| **feature pack** | a list of outcomes already in the catalog, plus the story of why they belong together and the value they bring | the mADR (and the pool ADR, once brought down) |
| **work pack** | one outcome delivered, matching TASKs to REQs, closed by human sign-off | the OBPI, renamed |
| **release pack** | the cart for one order: feature packs whole or in part, loose items, whatever the release needs; it alone drives the next minor release and carries the version | the ADR's semver and closeout |

How they form a system:

- **Admission.** A requirement enters the catalog on the operator's word, as an outcome naming its
  source. Nothing else enters.
- **Telling the story.** A feature pack lists catalog outcomes and says why they belong together.
  An outcome sits in **at most one** feature pack, or none (revisit when a real outcome belongs to
  two stories).
- **Emergence.** An unforeseen prerequisite is admitted as its own outcome, usually in no feature
  pack, and joined by a `depends_on` edge to the outcome that needs it. The feature pack's story and
  list stay as written; it has no prerequisite field.
- **Work.** A work pack delivers one outcome, as an OBPI did one checklist item.
- **Release.** The release pack takes feature packs whole or in part and loose items. Readiness from
  `depends_on` shows which prerequisites travel with them, or go in an earlier release.
- **Value.** A human attests a feature pack's value delivered, *"JUST LIKE the obpi/madr
  pipelines"*, at the release pack's or the work pack's attestation, not in a ceremony of its own.
- **The pool.** Unchanged: intentions until brought down. Bringing one down is admitting its
  outcomes, then writing the feature pack that carries its story, motivation and why.
- **The ADR** stays a decision record outside the four.

## Names, and their standing

| Name | Standing |
|---|---|
| REQ catalog | **ruled** (operator, this run); the catalog is canon (requirements model) |
| `family.capability.outcome` | **ruled** (operator, this run); canon since 2026-10-29; the FDAU and Backplane term *outcome* is **sourced** |
| feature pack | **ruled** (operator, this run), over the candidates put; no source uses it |
| work pack | **ruled** (operator, this run); **contradicts** canon's *work package* (requirements model; RO-5, landed in code); *work package* is **sourced** (DoD EVMSIG, NASA WBS) |
| release pack | **ruled** (operator, this run); **contradicts** canon's *Release Package* (RO-4, rulings of 2026-10-25 and 2026-10-29) |
| pool, intentions | **ruled** (2026-10-25, reaffirmed this run) |
| the first-principles list put mid-run | **unratified**: drawn from the operator's words, put for correction, and passed over when the operator moved to naming; each principle stands only through the decisions that use it |

## What the literature contributed

Ten source files, read in full (`sources/`). gzkit's own lineage (FDAU, Backplane) has **no value
bundle**: both group by responsibility, which confirms the operator's gap. The nearest shapes
(Shape Up's pitch, the Minimum Marketable Feature, the release-planning theme, manufacturing's model
and configuration bill) were put and **not adopted**; several key primary texts (IFM, the theme
papers, PMI, APICS) could not be read and rest on secondary or vendor sources. They stay as sourced
vocabulary.

## What each disposition row would produce

| # | Row | Would produce |
|---|---|---|
| 1 | ADR / OBPI | nothing (not pursued: initiation is suspended; the feature pack is a loosening of the mADR, not a new decision) |
| 2 | GHI / direct fix | nothing (not pursued: no out-of-drydock defect) |
| 3 | chore | nothing (not pursued) |
| 4 | doc | the drydock contract's § The general arrangement and the requirements model amended to the four records as named, with the feature pack as a record; and the feature pack's store and value attestation put to the operator as a finding graded under the induction freeze, with its owning order |
| 5 | one-shot refactoring | a rename program, *work package* to *work pack* and *Release Package* to *release pack*, its route the operator's: prose only; prose and code identifiers (16 source files, the `release_package.md` template); or also the ledger event type `work_package_transitioned`, booked five times |
| 6 | no action | the literature's shapes recorded as not adopted, kept as vocabulary |

## What sign-off would and would not mean

Funding the run lets rows 4 and 5 proceed, each on its own go. It starts no ADR, OBPI, schema or
verb, and it does not grade the feature-pack finding: that grading is its own question under the
induction freeze.
