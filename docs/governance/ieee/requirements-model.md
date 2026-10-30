<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# The requirements model — families, outcomes, REQs, work and release

**2026-10-18. Status: decisions ruled, including the family legend (decision 8.3).**
Operator: **g0**. This document replaces
[`design-candidates.md` § The joined requirements model](design-candidates.md#the-joined-requirements-model),
which recorded the model of 2026-10-17 for ratification with five open points
([`OPEN-QUESTIONS.md` Q-19](OPEN-QUESTIONS.md#q-19-what-joins-requirements-features-bdd-and-the-ladder)).
On 2026-10-18 the operator ruled the model one decision at a time; each ruling is booked verbatim as
an insight record (scope `harbor-pilotage-wp4`) in `.gzkit/insights/agent-insights.jsonl`. This is
civil-rule design input for the catalog's first voyage: it realigns structure on paper, populates
nothing, changes no identifier, parser, schema or proof binding, and authorizes no migration. The
id-resolution seam (harbor pilotage RO-2) and the empty catalog schema (RO-3) are the work that would
make it executable.

**Sources it composes.** The FDAU roadmap-and-backlog method (`tvproductions/xplane-fdau`, the
retrospective specification *backlog-governance-model*), Superpowers Backplane
(`docs/superpowers-backplane/governance.md` in that repository), and the operator's note *Bodies of
Knowledge for Agentic Software Work* (2026-10-16: SWEBOK, PMBOK, SEBoK, BABOK, the ASQ CQE body of
knowledge, and cybernetics as a lens). External content is grounding, never authority; the authority
is the operator's rulings below.

## The records

| Record | Layer | Identity | Holds | Answers |
|---|---|---|---|---|
| PRD | 1 | `PRD-…` | Functional (`FR-nnn`) and non-functional (§7) requirements: the parent obligation set | why the product exists |
| Family | 1 (catalog) | mnemonic letter, `H` | One responsibility area, with a one-sentence scope in the legend | where an obligation belongs |
| Capability | 1 (catalog) | family + number, `H1` | A named grouping of outcomes with a scope; never carries work (ruled 2026-10-29) | which outcomes belong together |
| Outcome | 1 (catalog) | capability + dotted number, `H1.4` | One reviewable deliverable: statement, owner, `user_facing`, `governed_by`, `depends_on` | what is delivered |
| REQ | 1 (catalog) | sequential, area-free, `REQ-1207` | One atomic obligation: statement, kind (BEHAVIOR, SUPPORT, STRUCTURAL-FENCE), revision, `member_of`, `applies_to` for an NFR | what must be true |
| Feature file and steps | 1 | the outcome's code as a tag, `@H1.4` | The executable behaviour of one user-facing outcome; each scenario tagged with the REQ it proves | proof of user-facing behaviour |
| ADR | 1 | `ADR-<n>` (decision record) | One architecture decision: context, alternatives, consequences, decision status, supersession links | which choice was made |
| Work package | 1, with its events in 2 | sequential, `WP-<NN>-<slug>` | One dated attempt to deliver one outcome: the frozen REQ baseline, the closing test, the task cards | how one outcome is delivered |
| Task card | 1, with its events in 2 | `TASK-…` | One slice sized to an agent's context: one commit, one trailer, the REQ ids it drives | the increment |
| Release Package | 1, with its events in 2 | the version | Which outcomes a version is planned to carry; mutable while a target | what is planned to ship |
| Ledger | 2 | event ids | Every status transition, proof result, freeze, attestation and release record | what happened |
| Backlog board | 3 | none | A view composed from the catalog and the ledger; never edited | where everything stands |

Architecture decisions are peers of the catalog, never its parents (decision 9). The PRD is the
parent of the families: every FR and every §7 attribute has a disposition (see § Family schemes).

## The decisions, as ruled

### 2. Identity

Families and outcomes take FDAU mnemonic codes with a recorded legend: `H` is a family, `H1` a
capability, `H1.4` an outcome, exactly three levels, and a work package always delivers an outcome
(operator ruling 2026-10-29, *"A"*, recorded in the drydock contract's § Rulings of 2026-10-29).
REQs keep sequential ids that do not depend on their area, and membership is a field
(`member_of`), so moving a REQ between outcomes keeps its id, its `@covers` tags and its proof
history (the 2026-10-17 ruling stands). Codes are never derived into parentage: the catalog holds
the relationships, and a code's spelling proves nothing (Backplane: "Do not derive live parentage
from the spelling of a code"). A retired code is never reused. Legacy `ADR-`, `OBPI-`, `REQ-<semver>-NN-MM`
and `TASK-` identifiers are frozen and resolve through the ledger's `artifact_renamed` alias layer,
which `gz migrate-semver` already writes; old attestation evidence is never rewritten.

*Why positional codes stop at the outcome.* A WBS code such as `1.2.3` is safe on a baselined node.
REQs are added, removed and shifted before a freeze, so a code that spelled a REQ's position would
break on exactly the moves the catalog exists to allow.

### 3. Authority

Structure (families, outcomes, REQ membership, dependencies, gates) is Layer-1 canon under
`data/catalog/`, edited only through `gz` verbs that also book a ledger event, so every move has a
history. Delivery status and proof live only in the Layer-2 ledger. The backlog board is a Layer-3
view generated from both ([state doctrine](../state-doctrine.md)). FDAU's two authorities map onto
this split: its ROADMAP is the catalog, its BACKLOG is the ledger.

### 4. Lifecycle and proof

**The outcome carries the lifecycle** (FDAU's local child):

`queued → designing → specified → planned → in_progress → implemented → reviewed → verified → validated → released`,
with the side states `blocked` and `deferred`. Each transition needs a named ledger event as its
evidence. `verified` means every member REQ is SATISFIED at its current revision and review findings
are resolved. Only a Gate 5 human attestation on the outcome, made after reading the inspector's
report, moves `verified` to `validated`. It is one act, recorded at the close of the outcome's work
package, and that close moves the outcome (operator ruling 2026-10-29, *"A"*; the drydock
contract's § Rulings of 2026-10-29). `released` comes from the ledger release record.

**Each REQ carries proof only** (amended from "binary" after the operator's direction to learn from
Backplane): `SATISFIED`, `UNSATISFIED` or `UNKNOWN`. Missing evidence is `UNKNOWN`, never a pass and
never a fabricated failure. Evidence is bound to the REQ's revision and the commit it was taken at:
a behaviour-changing revision resets the affected claims to `UNKNOWN` until revalidated ("a prior
pass at commit B does not prove commit C"). A deferral or exclusion is a scope disposition with an
approver and a revisit condition, never a satisfaction result.

### 5. Dependencies

Explicit predecessor edges (`depends_on`) between outcomes, gates and external boundaries live in
the catalog, validated to exist and to be acyclic. Readiness derives only from those edges, never
from codes or list order. Pull order is a separate operator ruling recorded with the work or
Release Package. The standing ruling that feature ADRs are worked "in ascending semver order" stays
binding on legacy (m)ADR work until the operator retires it explicitly; nothing here retires it by
inference.

### 6. Work package

A work package delivers exactly one outcome. It freezes that outcome's REQ set as its baseline,
carries the task cards that execute it, and closes by the 100% rule: every REQ in the baseline
SATISFIED at its current revision or moved out by a recorded disposition, and nothing landed that no
REQ asked for. The outcome outlives its work packages: a reopened outcome takes a new work package,
with a ledger record naming the REQs that changed and why, and the first package's record stays
intact. A small feature is itself the outcome; no redundant layer is created to hold it. This
replaces the general arrangement's "a work package selects the REQs sharing one contract": an
outcome's REQs are the REQs that share its contract.

### 7. Release

No version appears in any outcome, work package or REQ id. This re-rules the 2026-10-05 grammar
`WP-<semver>-<NN>-<slug>` to `WP-<NN>-<slug>`
([identifier migration program](../../rnd/renewing-vows/identifier-migration-program.md)). The
release target is Release Package membership, mutable through a `gz` verb that books a ledger event;
a slip changes membership and nothing else. `released_in` derives from the ledger release record and
never changes. FDAU's `candidate_release` is therefore not a field on the outcome; the Release
Package holds it once. The Release Package says which **outcomes** advance in a version, replacing
the earlier "which REQ states advance".

### 8. The Q-19 open points

1. **Cross-cutting NFRs.** An NFR belongs to one owning outcome in the quality-attribute family and
   carries `applies_to` (outcomes, commands or configurations). Proof is recorded per target, and the
   NFR is SATISFIED only when every target is; the owner accepts the combined result (Backplane's
   shared coverage with a named combined-result owner).
2. **Starting families.** Drawn from the behaviour gzkit actually has, not from the PRD's FR list;
   every PRD FR and §7 attribute receives a disposition (mapped, split, retired), the operator picks
   a scheme, and the PRD is then amended to match. The candidates are in § Family schemes; the
   selection is decision 8.3 below.
3. **Registry form.** Settled by decisions 2 and 3: the family legend and the catalog live under
   `data/catalog/`; mnemonic codes replace a slug grammar.
4. **How a feature file declares its area.** Settled by decisions 2 and 4: a feature file belongs to
   one outcome and carries the outcome's code as a tag; the catalog holds the mapping.
5. **Areas and bounded contexts.** Kept apart, as the 2026-09-25 design review ruled.

### 9. ADR links

An outcome links to zero or more governing ADRs (`governed_by`); not every outcome needs one
(operator, 2026-10-17: *"I don't think that every requirements or feature necessitates an
architectural design or decision record"*). An ADR carries only a decision status (proposed,
accepted, superseded, with supersedes links): no checklist, no work packages, no release. Either the
catalog or an ADR may originate a work package. Legacy ADR checklists and OBPIs stay as frozen
history behind the aliases.

### 10. BDD on user-facing outcomes

This carries gzkit's standing rationale (BDD for user-facing surfaces and interfaces, the heavy-lane
test of `AGENTS.md` § Gate Covenant) onto the new records; only the anchor moves, from the ADR's lane
to the outcome. An outcome declares `user_facing` by that test: a CLI, API, schema or runtime contract
used by humans or external systems. Every BEHAVIOR REQ under a user-facing outcome needs a passing
scenario tagged with its REQ id in the outcome's feature file, in addition to its `@covers` unit test,
before it can be SATISFIED; SUPPORT and STRUCTURAL-FENCE REQs keep their declared proof channels. A
user-facing outcome is `verified` only with its feature file green under behave. The 415 existing
`@REQ-` tag occurrences (343 distinct REQs, across 79 feature files; measured 2026-10-18) keep
resolving through the aliases; regrouping the files by outcome is later drydock work.

**Two axes stay separate**, as before: a REQ's family type (functional or quality attribute) says
what kind of need it is; its kind (ADR-0.0.59) says which proof channel binds it.

### 8.3. The family legend — MIL-STD-881's compromise

Ruled 2026-10-18. Torn between Schemes A and B (operator, verbatim: *"torn here, there are reasons for
A and B"*, then *"so, perhaps MIL-STD-881 had the best compromise?"*), the operator selected one tree
on the model of MIL-STD-881F: a product-oriented hierarchy whose cross-cutting work sits in a fixed
set of **common elements** at the second level, siblings of the product, rather than in a second
hierarchy (Appendix K lists integration, assembly, test and checkout; systems engineering; program
management; system test and evaluation; data; and others). Scheme A's families are kept and banded:

| Band | Families | The 881 analogue |
|---|---|---|
| Product elements, the responsibilities gzkit delivers | X airlock and entry · H session continuity · C control surfaces and corpus · M maintenance · P packaging and release · D decision records | the prime mission product and its subsystems |
| Common elements, serving every product family | R requirements and work · G gates and verification · A attestation and closeout · L ledger and state · Q quality attributes | R ≈ systems engineering and program management · G ≈ system test and evaluation, and integration and test · L ≈ data · A ≈ acceptance within test and evaluation · Q has no direct analogue: it carries the cross-cutting NFRs (decision 8.1) |

**The placement rule for checks**, as 881 places test: a gate or validator that spans families
belongs to G; a unit's own `@covers` tests stay with its outcome. A product outcome that relies on a
common element says so with `depends_on` (the hangar's exit gate depends on G's guard re-run). No
`loop_stage` facet is kept: "every verification gzkit has" is the G family.

### 11. Grounding against the Bodies of Knowledge note

Ruled 2026-10-18, one decision at a time, after the operator asked that the whole note be reviewed
"so we can see how it can help gzkit while it is in drydock". Each selection is booked verbatim as an
insight record. Maxims and concepts are the note's numbering.

| Item | The note | Ruled |
|---|---|---|
| Rulings in the ledger | maxim 15 | Every `gz insights remember` also appends an `insight_recorded` ledger event: the insight's `ts`, a content hash, whose words they are (operator or agent), an optional `supersedes` reference. Insights stay the store (operator: *"what is the harm that the ledger notes that an insight was recorded and references it?"*) |
| The REQ as trace key | maxim 5 | Baseline and forward rule: RO-2 records the before-figures (361 of 736 test files carry `@covers`; 731 REQs have no test; 1,340 of 19,241 ledger events name a REQ); every new delivery event names its REQ or outcome; nothing legacy is backfilled |
| The safe-mode entry record | maxim 14 | The safe-mode entry event records the contract's content hash, its suspended list and its exit conditions; a contract edit while a session is open books a contract-amended event |
| Tampering | maxim 13 | RO-1 and RO-7 classify each cut candidate as common or special cause from its recorded provenance; special-cause clauses move to rationale records. A single failure is recorded as an insight and becomes a rule only on recurrence: a proposal cites at least the threshold of insight or GHI records of one class (3, in `data/recurrence_threshold.json`; operator: *"3 occurrences (Rec.)"*, *"Cited records (Rec.)"*), every pair at least one session lease apart by full timestamp (*"One lease apart (Rec.)"*), checked by `gz insights recurrence` |
| The operator's variety | maxim 17 | The operator initiates a work package, not each slice; Gate 5 sits per outcome, attested once at its work package's close; the passage log carries the baseline of human acts per delivered outcome |
| Acceptance criteria | maxim 8 | A REQ carries a statement (effect and rationale) and one or more pass/fail criteria (state or input → required outcome → evidence), on the `ghi-close` closure-contract precedent; proof binds to the criteria |
| Done drift | maxim 2 | Agents may draft REQs before freeze; after freeze the catalog verb refuses an edit to a baselined REQ except a reopening carrying the operator's words and attestor, which opens a new work package and resets that REQ's proof |
| REQ quality | protocol step 1 | Before freeze, the independent reviewer checks each baselined REQ against BABOK's nine criteria and returns failures by name, never rewriting; the validator checks only *testable* and *atomic*; *prioritized* is met at package level |
| Risk | maxim 12 | A short note at freeze (how the evidence could be green and still wrong) and the residual at validation, read at Gate 5; no scored register |
| Gate outcomes | protocol step 8 | Gate 5 on an outcome records one of proceed (→ `validated`), redirect (→ reopening, new work package), pause (→ `deferred` with a revisit condition) or terminate (→ withdrawal, never delivered); PRD FR-009's Completed, Partial and Dropped map to proceed, redirect and terminate |
| Derive | concept 3 | A REQ names the PRD FR or § 7 attributes it refines (`derives_from`); an FR with no deriving REQ is reported, and a PRD change lists the REQs it touches |
| Needs and requirements | concept 1 | The PRD FR or § 7 attribute is the stakeholder need, written by the operator; the catalog REQ is the system requirement derived from it, drafted by an agent and frozen by the operator. Solution wording in FRs is flagged for later rewording |

**The note's terms, mapped.** The note is grounding, not canon; where its glossary and this model
differ, this model governs and the mapping is:

| The note's term | The ruled records |
|---|---|
| work package, "a release-sequencing group of REQs, frozen for a release" | an outcome (the deliverable and its REQs), its work package (one dated, frozen attempt to deliver it) and its Release Package membership (the sequencing) |
| REQ, "an atomic statement of intent or needed effect" | intent is the PRD FR or § 7 attribute; the REQ is the system requirement derived from it, with pass/fail criteria |
| safe mode, "named governance rules are turned off" | every guard outside the `gate5_invariants` floor goes advisory; the contract names the suspensions, and the ledger pins the contract by hash at entry |

## Family schemes — the candidates, as drafted for selection

Selected: Scheme A, banded as decision 8.3 records. Schemes B and C are kept as the alternatives
considered.

FDAU's adoption checklist asks which labels "describe stable domain areas, and which currently
describe a release, team, or temporary campaign", and asks for each family's one-sentence scope.
Three schemes follow, drawn from the `gz` verb surface and `src/gzkit` as of 2026-10-18. The letters
are this project's legend, not FDAU's.

### Scheme A — product responsibility (selected, banded by decision 8.3)

| Letter | Family scope | Belongs | Does not belong |
|---|---|---|---|
| R | Requirements and work: intent, the catalog and the labor that delivers it | PRD, constitution, catalog, work packages, task cards, Release Packages; today's `prd`, `constitute`, `specify`, `plan`, `obpi`, `task` verbs | decision records |
| D | Decision records | ADR authoring, decision status, supersession, pool and promotion, evaluation | delivery state of any kind |
| L | Ledger and state | the append-only ledger and its schema, state and status views, frontmatter coherence, the alias layer, the backlog board, bulletins | the evidence producers themselves |
| G | Gates and verification | `check`, tests, smoke, behave, `covers`, drift, test shape, every validator that spans families (the corpus lineage and shape validators among them), ARB receipts, canaries | human attestation; a unit's own tests, which stay with its outcome |
| A | Attestation and closeout | Gate 5, attestation, closeout, audit, completion reversal | automated verification |
| X | Airlock and entry | the airlock, permitted entry, ontology imaging, the focused context loader | session memory |
| H | Session continuity | handoffs, the ruling store, session orientation, insights | ecosystem transit (X) |
| C | Control surfaces and corpus | AGENTS.md composition, the content corpus, vendor sync, skills, rules, personas, roles, readiness, the knowledge bundle | product verification |
| M | Maintenance | the MX hangar, safe mode, chores, tidy, preflight, GHI repair routing, cross-repo issue filing | feature or requirements work (GHIs carry repair only) |
| P | Packaging and release | init, upgrade, patch release, git-sync, parity, distribution, feature flags | release planning (R) |
| Q | Quality attributes | the PRD §7 attributes and every cross-cutting NFR (decision 8.1) | functional behaviour |

*Tradeoff.* Each family is a responsibility that stays put when the delivery method changes, which is
the property FDAU's slip test needs. The cost is eleven families, and R must hold both intent and
labor, so its families need care (R1 intent, R2 catalog, R3 work, R4 release planning, for example).

### Scheme B — governance loop stage

I intent (PRD, constitution, catalog, ADR) · L plan (work packages, Release Packages, task cards) ·
E execute (airlock, context, pipeline runtime, token blocks) · V verify (gates, tests, behave, ARB,
validators, canaries) · T attest (Gate 5, closeout, audit) · S ship (patch, git-sync, distribution,
init, upgrade) · K keep (ledger, state, handoffs, insights, corpus, control surfaces) · M maintain
(MX, chores, tidy, GHI) · Q quality attributes.

*Tradeoff.* It reads like the workflow, but the workflow is what this drydock is redesigning, so
outcomes would change family whenever the loop changes, which is FDAU's "temporary campaign" warning.
K becomes a grab-bag, and the ledger, used by every stage, has no natural home.

### Scheme C — audience

O operator surfaces (verbs humans run) · G agent surfaces (skills, rules, AGENTS.md, hooks, corpus,
airlock) · R the record (ledger, state, receipts, insights) · V the verification engine · A adopter
distribution · Q quality attributes.

*Tradeoff.* Six families, easy to hold in the head, but one feature splits across families
(`gz mx enter` is an operator surface while the MX checkpoint is an agent surface), and audience is
already carried by the `user_facing` flag (decision 10), so the family would repeat a field.

### PRD dispositions

Every PRD item receives one disposition. The PRD was amended to match on 2026-10-18
([PRD § 19](../../design/prd/PRD-GZKIT-1.0.0.md#19-amendments)).

| PRD item | A | B | C | Disposition |
|---|---|---|---|---|
| FR-001 Project Initialization | P | S | A | mapped; the wording names `docs/briefs/`, `docs/adr/` and `docs/audit/`, but `gz init` creates `design/adr/`, `design/constitutions/` and `design/prd/` (observed in a scratch repository 2026-10-18), so the FR is amended against the verb |
| FR-002 PRD Management | R | I | O | mapped |
| FR-003 Constitution Management | R | I | O | mapped |
| FR-004 Brief Creation | R | L | O | retired: `gz specify` now creates an OBPI and no standalone brief exists; its intent, a scoped statement before work, is absorbed by work package authoring |
| FR-005 ADR Creation | D, R | I, L | O | split: the decision record → D; the checklist, the `obpis/` directory and lane-from-interview retire (decisions 6, 9, 10) |
| FR-005a OBPI Brief Creation | R | L | O | split: work package authoring → R; the OBPI numbering is frozen behind aliases (decisions 2, 7) |
| FR-005b Closeout Ceremony | A | T | O | split: evidence presentation and attestation → A; "all OBPIs complete" becomes per-outcome validation (decision 4) |
| FR-006 Gate Verification | G | V | V | mapped; "(Heavy only)" becomes "for user-facing outcomes" (decision 10) |
| FR-007 State Management | L | K | R | mapped; the PRD → Brief → ADR graph becomes the catalog graph |
| FR-008 Status Display | L | K | O | mapped; "Display current lane" retires with the ADR lane |
| FR-009 Attestation Recording | A | T | O | mapped |
| FR-010 Audit Generation | A | T | R | mapped |
| FR-011 Ledger System | L | K | R | mapped |
| FR-012 Claude Hooks Integration | C | K | G | mapped; amended for the multi-vendor hook set |
| §7 Performance | Q | Q | Q | mapped; its budget moves to JSON (a value in Markdown is illustrative) and it takes `applies_to` |
| §7 Determinism | Q | Q | Q | mapped |
| §7 Explainability | Q | Q | Q | mapped |
| §7 Accessibility | Q | Q | Q | mapped |

**Behaviour the PRD does not name** received new FRs on 2026-10-18 (FR-013 to FR-031, with the
requirements catalog itself added as FR-015 and work package and outcome validation as FR-013 and
FR-014): the airlock (A: X),
handoffs and the ruling store (H), insights (H), the MX hangar and safe mode (M), chores (M),
cross-repo issue filing (M), the content corpus and AGENTS.md composition (C), skills and vendor sync
(C), ARB receipts and canaries (G), task cards and Release Packages (R), patch release, git-sync and
feature flags (P), and the operator bulletin (L, pooled).

## Paper migration test

FDAU's five-step test, run on paper on 2026-10-18 over the four kinds of item it names. Codes below
use Scheme A, which the operator then selected (decision 8.3); no catalog entry, alias or event was
written.

### Step 1 — freeze and alias

| Item | FDAU's kind | Legacy identity | Under the model |
|---|---|---|---|
| ADR-0.0.74 MX hangar | foundation-like ADR | 1 ADR, 20 OBPIs, 77 distinct REQs, 23 test files, 0 tagged scenarios | decision record `ADR-0.0.74` (accepted); family M1 "maintenance hangar" with one outcome per delivered mechanism (marker, checkpoint, floor, enter, exit, MX log, awareness hook, skill binding, lease); item 10 is a withdrawal record, not an outcome; 77 REQs keep their ids as aliases with `member_of` set |
| ADR-0.35.0 canon-entry corpus landing | feature ADR with a real decision | 1 ADR, 20 OBPIs (11 complete), 169 REQs, 17 feature files, 47 tagged REQs | decision record `ADR-0.35.0` holds the tombstone algebra; items 1–14 become outcomes in C, except the rendition-lineage validator (item 6) and the corpus shape witness (item 11), which go to G under decision 8.3; items 15–20 (pipeline run position, next command, served procedure, dispatch recording, lock continuity, skill cutover) become outcomes in R3, not governed by the tombstone decision |
| ADR-0.28.0 focused context loader | feature with no new architectural choice | 1 ADR, 2 OBPIs, 13 REQs, lite lane | one outcome in X with `governed_by: []`; its five numbered "decisions" (a verb, Markdown output, `@covers`-first discovery, two OBPIs, lite lane) are local design choices that belong in the outcome's design, not an ADR |
| ADR-pool.operator-bulletin | pooled idea | 1 pool file, no OBPIs | outcomes `queued` in L with `depends_on` the token-block and hangar occupancy outcomes; the pool file becomes a decision record with status `proposed` for its four selections |

### Step 2 — consumers of version-shaped ids

Measured 2026-10-18: 91 ADR packages and 221 pool entries; 1372 ledger rows carrying an `adr_id`;
371 Python files under `src/gzkit` naming `ADR-` or `OBPI-`; 358 test files carrying `@covers` REQ
bindings; 415 scenario REQ tags; the id grammar pinned by `src/gzkit/schemas/adr.json` and
`src/gzkit/schemas/obpi.json`. Commands, in order: `ls docs/design/adr/pre-release docs/design/adr/foundation | wc -l`,
`ls docs/design/adr/pool | wc -l`, `grep -c '"adr_id"' .gzkit/ledger.jsonl`,
`grep -rlE 'ADR-|OBPI-' src/gzkit --include='*.py' | wc -l`,
`grep -rlE '@covers\(.REQ-|covers\("REQ-' tests | wc -l`,
`grep -rhoE '@REQ-[0-9.]+-[0-9]+-[0-9]+' features | wc -l`. (The identifier program's 105 of
2026-10-10 used a narrower expression; the two figures are not comparable.) Every one of these reads
through the alias layer before any authoring rule changes: that is RO-2.

### Step 3 — separate views

| View | ADR-0.0.74 | ADR-0.35.0 | ADR-0.28.0 | operator-bulletin |
|---|---|---|---|---|
| Decision | accepted | accepted (tombstone algebra) | none | proposed |
| Outcome | M1.x validated (completed and attested) | C outcomes 1–14 mixed; R3 outcomes 15–20 queued or in progress | X outcome validated | L outcomes queued |
| Release | `released_in` from the ledger release records | C and R3 outcomes in separate Release Packages if they slip apart | `released_in` from the ledger | no Release Package |

### Step 4 — simulations

- **A slip.** The bulletin's outcomes move from a Release Package targeting 0.36 to one targeting
  0.37: only the membership changes; codes, dependencies and evidence are untouched. Today the same
  move for ADR-0.35.0 items 15–20 would leave them named `OBPI-0.35.0-15…20` in a release they no
  longer target, or force a re-cut.
- **One decision governing two features.** ADR-0.0.41 (token blocks) governs both the pipeline's lock
  continuity (ADR-0.35.0 item 19, in R3) and the MX hangar's lease, which reads the session lock's TTL
  (`src/gzkit/mx/hardening.py`, commit `d5fcd5c3f`). Both outcomes carry `governed_by: [ADR-0.0.41]`;
  neither belongs to the other's ADR.
- **Supersession.** The operator's 2026-10-18 ruling that expiry "is booked and announced, never
  evicted" supersedes TTL reaping for the hangar. Under the model a new decision record supersedes the
  reaping clause of ADR-0.0.41, the affected REQs take a new revision, and their proof resets to
  `UNKNOWN` until revalidated, while the shipped evidence stays attached to the earlier revision. The
  surface amendment of REQ-0.0.74-05-01 in `d5fcd5c3f` is that pattern, done by hand today.

**Verdict on paper: pass.** Only membership changes on a slip, evidence stays linked through the
aliases, and supersession moves decision authority without erasing shipped history.

### What the test surfaced

1. **A reused version slot.** `ADR-0.28.0` first named *chores-system-maturity-absorption*
   (`adr_created` 2026-03-22), was demoted to the pool on 2026-05-23, and was reassigned to
   *focused-context-loader* the next day. `OBPI-0.28.0-01` names both `chores-cli` (parked 2026-07-22)
   and `context-core`, separated only by slug. A version-coded identity reused for an unrelated
   feature is the hazard FDAU's method exists to remove; under decision 2 a retired code is never
   reused.
2. **User-facing items with no scenarios.** ADR-0.0.74 adds `gz mx enter` and `gz mx exit` and
   ADR-0.28.0 adds `gz context`, yet no feature file carries their REQ tags. Under decision 10 their
   outcomes would report BDD gaps.
3. **A lane that disagrees with the heavy-lane test.** ADR-0.28.0 chose the lite lane because "the
   verb adds no schema, ledger event, or runtime contract", but `AGENTS.md` § Gate Covenant lists a
   CLI used by humans among the heavy-lane surfaces. Decision 10's `user_facing` test, applied to the
   outcome, removes the per-ADR judgment.

### Step 5 — approval

Half reached. The operator chose the family legend (decision 8.3). The compatibility path (RO-2's
resolver, RO-3's schema) still needs approval before any creation, audit, promotion or release
tooling changes. The
current gates stay in force until then.

## What adopting the model changes elsewhere

Nothing below is changed by this document; each is a coupled surface the adoption must amend.

- `AGENTS.md` § Gate Covenant: lane wording moves from the ADR to the outcome (decision 10).
- [The general arrangement](../harbor-pilotage-candidate-2026-10-15.md#the-general-arrangement): its
  work-package and Release Package cells (amended there 2026-10-18 by pointer to this document).
- The identifier migration program's work-package row (amended there 2026-10-18).
- `docs/governance/GovZero/adr-lifecycle.md`, its own identifier scheme (already flagged by the
  identifier program's phase 0).
- ~~The PRD~~ — amended 2026-10-18 (FR-004 retired, FR-005/005a/005b split, FR-013 to FR-031 added).
- The `gz-design`, `gz-obpi-pipeline` and `gz-adr-create` skills, which assume an ADR parents its
  work.
