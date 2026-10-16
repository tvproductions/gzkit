<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Safe-Mode Doctrine — Martial Law, the Harbor Pilot, Drydock and Seaworthiness

**Authority:** operator rulings of 2026-10-15 and 2026-10-16, verbatim where quoted below; the ratified glossary in `docs/rnd/renewing-vows/doctrine-merge.md` Part 0 § Terms carries the terms.

**Companion rule:** `.gzkit/rules/mx-mode.md` § Safe mode. **Mechanism:** `gz mx enter --mode safe --contract <path>` and `gz mx exit`, operated through the `gz-mx` skill (ADR-0.0.74 extended under GHI #1244). **Template:** `.gzkit/templates/safe_mode_contract.md`. **First instance:** `docs/governance/harbor-pilotage-candidate-2026-10-15.md`.

**Purpose:** keep the approach reusable. Operator, 2026-10-16, verbatim: *"keep these metaphor entrenched in canon, this won't be the last time we need to reach for this approach."*

---

## When safe mode is declared

Safe mode is declared when the ordinary ceremony cannot govern its own repair: the control plane has grown past what a session can carry, the work-design units no longer bound the work, and each turn under civil rule adds ceremony faster than it removes it. The operator named that state on 2026-10-16: *"I am in a 'kernel panic' mode here - gzkit has become untenable."* The declaration is the operator's word; the mechanism records it (`.gzkit/mx.json` with `mode: safe`, bound to its `mx_session_opened` event) and the banner repeats it every turn.

Safe mode is the Maintenance Hangar's sibling, not its extension. The hangar demotes guards so governance can be repaired in place. Safe mode suspends initiation and brief ceremony under a contract and demotes no guard: everything mechanical still binds, and the operator's word at entry is the initiation.

## The metaphor, and why it holds

The regime is nautical because the nautical record already separates the three things a crisis confuses: who has the conn, where the ship is, and when it may sail again.

- **The harbor pilot.** The strongest model available, booked by the operator, takes the conn for the passage into port. The pilot plans, measures, diagnoses and takes rulings with the operator; it executes a cut itself only when the cut is the measurement's own finding and small enough to read in one sitting. Operator, 2026-10-15: *"I wanted to PLAN in Fable, but not do all the work in fable."* The captain remains the operator: the pilot advises the helm and carries no signature.
- **Martial law.** The temporary arrangement under which the pilot acts: *"this is a TEMPORARY ARRANGEMENT until we get to port and dry dock."* It is entered by the operator's word and a written contract, and it yields back to the Magna Carta, gzkit's campaign under civil rule.
- **The harbor.** The passage in: the load cuts and the instruments that make the ship steerable again, measured leg by leg.
- **Drydock.** The structural rebuild that cannot be done under way: the ladder, the catalog, the release plan, the control plane subtracted. The ship is out of the water; it is not on a normal voyage, so the exceptional regime continues.
- **The sea trial.** The proof that the rebuilt ship sails: a fresh project on the released wheel runs one work package end to end. The constitution's governor rule is the ground: doctrine under construction is proven on another project before it binds its own making.
- **Seaworthy.** The one condition on which safe mode ends. Not the harbor's quay, not the drydock's gate: the trial passed and recorded.
- **Handback.** The amendment the operator ratifies at seaworthiness: every pilot commit listed, kept or reverted; the passage log carried; the suspended rules restored. Civil rule resumes on the ratification. Operator, 2026-10-15: *"martial law to get us on the diagram's plan including control plane and work/design modularization, then a return to magna carta (civilian rule)."*
- **The voyage.** Ordinary operations under the Magna Carta: releases planned, packaged, witnessed, attested.

## The regime, as one period

| Phase | Regime | Produces | Done when |
|---|---|---|---|
| Harbor | safe mode | the instruments and the load cuts | every harbor leg met |
| Drydock | safe mode | the structural rebuild and its first release | the release published through a release plan; the drydock exit numbers met |
| Sea trial | safe mode | one work package run on a fresh install of the release | the trial recorded in the passage log |
| Handback | ratification | the amendment | the operator's word; the exit through the hard gate |
| Voyage | civil rule | ordinary operations | — |

Safe mode is left once, at seaworthiness. Operator, 2026-10-16: *"my expectation is the we leave martial law | safe mode | dry dock with a return to seaworthiness so that I can return to a normal voyage."*

## The instruments

1. **The contract.** Written before entry, from the template. Its sections: Authority (the operator's words, verbatim), Entry (the purpose in one sentence and the target shape), What is suspended and what is not, On the ledger, Division of labor, Mandate, Records, Exit (the chart), Work orders, Passage log. The `gz-mx` skill refuses entry when a required section is missing.
2. **The pilotage chart.** One row per leg with its witness and its last reading; a reading moves only by an act in the passage log. Legs are grouped by phase. Drydock carries exit numbers. The orientation prints the readings while safe mode is open (GHI #1245).
3. **The passage log.** One row per act: what changed, the measurement before and after, the commit, the witness. It is the record the handback carries.
4. **Work orders.** Each a GHI with a closure contract, written by the pilot, executed by a cheaper session under § Records. A work order is a pilotage instrument and leaves with the contract; it is not the civil-rule work package.
5. **Executive decisions.** Under safe mode the pilot decides where canon permits a decision, records it in the chart with the reason, and the operator may overrule any by a word. Operator, 2026-10-16: *"in safemode/martial law, you need to lean in and make executive decisions to achieve outcomes as we are in crisis mode here."* A decision that is the operator's by canon (Gate 5, corpus attestation, the glossary) stays the operator's.
6. **Records per act.** One commit per act with its `Task:` trailer, `gz arb red --commit` run after it with its verdict recorded, and an `undriven` verdict repaired in the same commit before it counts. The ledger is written only through `gz` verbs. No control is removed.

## The standard chart

A contract instantiates the chart below. Legs and repairs keep their letters across instances so
passage logs read alike; an instance may add legs, and marks a standard leg "not applicable" with
its reason rather than deleting it. Operator, 2026-10-16, naming these as what is entrenched.

**Harbor legs** (every leg has a mechanical witness; the owner is the pilot, a cheaper session or
the operator):

| Leg | What it means | Witness |
|---|---|---|
| H1 | Session start bounded | the orientation under its cap; the campaign block's bound test |
| H2 | The root contract within budget | `gz validate --instructions-files-budget`, no advisory |
| H3 | Pipeline invoke bounded | `gz skill audit`; bytes at invoke in the passage log |
| H4 | Per-turn rules and skill descriptions cut | the two sizes in the passage log before and after |
| H5 | The catalog exists and is used | the catalog loads through the registry seam; live briefs carry `assignments:` |
| H6 | The TASK is the increment on one package | one package's TASKs each with a `red_commit_receipt_emitted`, in one session |
| H7 | Every control names its contract | the scorecard's obligation column read by `gz validate --advisory-scorecard` |
| H8 | The toggle is on the record | `.gzkit/mx.json` with `mode: safe`, bound to its event |
| H9 | Executed briefs attested | `gz obpi status` shows `attested_completed` |

**Drydock repairs** (under safe mode; the pilot specifies and cuts, cheaper sessions execute):

| Repair | What is rebuilt | Witness |
|---|---|---|
| D1 | The ladder: ADR records decisions and lands contracts; the release plan governs a version; the work package is the labor unit; the TASK is the increment | one release planned and closed through a release plan, `gz closeout` keyed to it |
| D2 | The catalog as the product's truth | a validator that fails on a brief assignment naming no entry |
| D3 | GHIs and MX visits classified by the contract they repair | `ghi-triage` reports the contract per issue |
| D4 | The control plane subtracted: every control names its contract or retires; no rule body carries a dated narrative | the obligation column full; the exit measures |
| D5 | The airlock derives the slice from the contract's modules | a transit beyond the modules is refused |
| D6 | Eval checks module design against module code | one eval run on one package, reported |

**Drydock exit measures.** The instance sets the values; the measures are standing: per-turn load
(the root contract, the skill descriptions, the rules in total and the largest), the count of
controls with no named contract (exit at zero, each named or retired by a logged act), and the
operator's attestations per release (one per release and the sea trial, never one per brief).
The first instance's values are in its contract.

## The release plan

The release management document type, the rung the ADR wrongly carried until 2026-10-16 (operator,
verbatim: *"adrs are not releases"*; *"i must have a release management document type too"*).
One document per version under `docs/design/releases/`, named by the version it governs, from
`.gzkit/templates/release_plan.md`:

- frontmatter: the version; `status` (`planned`, `in-flight`, `released`); the catalog entries
  whose state advances, each with its from and to state; the work packages shipped; the lane and
  its gates; the operator's attestation;
- body: the intent of the version for the operator and for adopters, and the one-open-defect
  assessment the constitution's policy 12 requires.

`gz closeout` keys to it at the D1 migration; until then it is the planning document the first
drydock release is built through. The campaign sequences releases; a release plan says what one
release contains. ADRs stop carrying a version at the migration; a patch release uses the same
document with a short list.

## The sea trial, as procedure

1. The drydock's release is built and published through a release plan.
2. A fresh project installs that release from the wheel; `gz init` scaffolds it. gzkit's own
   tree is never the substrate: doctrine under construction is proven on another project before
   it binds its own making (the constitution's governor rule).
3. A cheaper session takes one work package from the catalog, cuts its TASKs per increment, and
   lands each as one commit with its trailer and its `red_commit_receipt` on the pipeline route.
4. The operator attests the package from two artifacts only: its entries' states and its TASK
   receipts.
5. The trial is recorded in the passage log; the ship is seaworthy; the handback follows.
   A second substrate, if the operator names one, flies as a flight-test sortie.

## What safe mode never suspends

Gate 5 attestation; the ledger through verbs; operator PII; the removal of a control; the PRIME DIRECTIVE. These are the hangar's `gate5_invariants` and the contract's standing list, and they hold in every mode.

## Entry and exit, mechanically

- Entry: the operator invokes the `gz-mx` skill, which confirms the contract's sections and runs `gz mx enter --mode safe --contract <path> --reason "<why>" --attestor g0`. The marker, the event and the banner record the mode.
- Exit: the skill reads the chart, stops on an unmet leg, and runs `gz mx exit --attestor g0`, the hard gate that re-runs every guard at full strength and renders the enter-to-exit log. The handback amendment follows the exit and precedes civil rule.

## Lineage

The harbor pilot and the drydock come from maritime practice: a licensed local pilot takes the conn for a passage the master cannot know, and a vessel is surveyed and repaired out of the water before a return to service. The hangar came first in gzkit (ADR-0.0.74, 2026-06), from aviation maintenance: return to service after a hard gate. Safe mode joins the two: the hangar's marker and gate, the pilotage's contract and chart. The first instance ran from 2026-10-15; its contract and passage log are the worked example this doctrine generalizes.
