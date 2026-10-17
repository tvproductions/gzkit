<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Safe-Mode Doctrine — the Drydock and the Repair Order

**Authority:** operator rulings of 2026-10-15, 2026-10-16 and 2026-10-17, verbatim where quoted below; the ratified glossary in `docs/rnd/renewing-vows/doctrine-merge.md` Part 0 § Terms carries the terms.

**Companion rule:** `.gzkit/rules/mx-mode.md` § Safe mode. **Mechanism:** `gz mx enter --mode safe --contract <path>` and `gz mx exit`, operated through the `gz-mx` skill (ADR-0.0.74 extended under GHI #1244). **Template:** `.gzkit/templates/safe_mode_contract.md`. **First instance:** `docs/governance/harbor-pilotage-candidate-2026-10-15.md`, amended 2026-10-17 to this doctrine.

**Purpose:** keep the approach reusable. Operator, 2026-10-16, verbatim: *"keep these metaphor entrenched in canon, this won't be the last time we need to reach for this approach."*

---

## What safe mode is

Maintenance mode is standing: the Maintenance Hangar, the chores, the patch releases, and the GitHub issues that carry repair, refactor and address work (never feature or requirements work; operator, 2026-10-17: *"I'd like maintenance mode and GitHub issues to be very tightly coupled"*). Safe mode is an occasional flip inside it. Operator, 2026-10-17, verbatim:

> Safe mode has to be a way to quickly, without all the uh, constraints of the ceremony and all those other safeguards, which are important, to be able to just lower all that, to be able to make the re-rigging, reconfiguring, retooling, restructuring, and all that. But once we do that, we then want to turn off safe mode and return to normal operations under the new structures.

It is declared when the ordinary ceremony cannot govern its own repair: the control plane has grown past what a session can carry, or the structure the work runs on has to be re-rigged. The declaration is the operator's word; the mechanism records it (`.gzkit/mx.json` with `mode: safe`, bound to its `mx_session_opened` event) and the banner repeats it every turn. It is not taken for ordinary maintenance, and it is turned off as soon as the re-rigging is done (operator, 2026-10-17: *"we're not always going to go to safe mode... I just am able to go to safe mode occasionally"*).

Safe mode is a mode of the Maintenance Hangar (ruled 2026-10-16: *"A, extend gz mx with a safe mode"*). Like the hangar it lowers every guard to advisory while the marker is open, except the four that hold in every mode (§ What safe mode never suspends), and its exit is the hangar's hard gate. Unlike the hangar it carries a contract, and it suspends the initiation clause for repair orders and the brief ceremony.

## The metaphor, and why it holds

The regime is nautical because the nautical record already separates what a crisis confuses: who has the conn, where the ship is, and when it may sail again.

- **The harbor pilot.** The strongest model available, booked by the operator, takes the conn to get the ship out of the mess it is in and plan the drydock's order of work. It appraises the whole project, plans, measures, diagnoses and takes rulings with the operator; it executes a cut itself only when the cut is the measurement's own finding and small enough to read in one sitting. Operator, 2026-10-15: *"I wanted to PLAN in Fable, but not do all the work in fable."* The captain remains the operator.
- **Drydock.** The ship is out of the water so the structure can be repaired and realigned: re-rigged, reconfigured, retooled, restructured. The drydock designs and lands the new structures; it does not populate them (operator, 2026-10-17: *"repair and realign the structure, don't populate it"*). It does not load cargo and it does not chart the next voyage.
- **Repair orders.** A drydock session holds repair orders. A repair order is the maintenance mirror of the work package: one bounded repair with a scope, a witness and an owner, recorded to the ledger, and held as a GitHub issue under the repair tagging scheme. The term "work order" is retired (2026-10-16) and the repair order mirrors the work package directly (ruled 2026-10-17, R1).
- **Seaworthy.** The structure is repaired and its witnesses read true; the ship can sail under normal ceremony without choking. The sea trial, a fresh project on the released wheel running one work package end to end, is the first voyage's act under civil rule, not a condition of leaving the drydock.
- **Handback.** The amendment the operator ratifies at seaworthiness: every drydock commit listed, kept or reverted; the passage log carried; the suspended rules restored. Civil rule resumes on the ratification.
- **Normal voyages.** Ordinary operations under the new structures: work packages cut from the catalog, releases planned through Release Packages, the feature and requirement backlog maintained, repairs through GitHub issues.

## The instruments

1. **The contract.** Written before entry, from the template. Its sections: Authority (the operator's words, verbatim), Purpose (what the flip is for and what it does not do), The general arrangement (the target structure, drawn and verified), What is suspended and what is not, Division of labor, Mandate, Records, Repair orders, Exit, Rulings, Passage log. The `gz-mx` skill refuses entry when a required section is missing.
2. **The general arrangement.** The drawing of the target structure, saved beside the contract and ratified by the operator. Every repair order names the band it serves; a change that serves no band is not a repair order.
3. **The repair-order register.** One row per order: what it serves, what it lands, its witness, its owner. A repair order's state moves only by an act in the passage log. Once the repair tagging scheme lands, the register is the set of repair-order issues and the contract carries the pointer.
4. **The passage log.** One row per act: what changed, the measurement before and after, the commit, the witness. It is the record the handback carries.
5. **Records per act.** One commit per act with its `Task:` trailer naming the repair order, `gz arb red --commit` run after a code change with its verdict recorded, and an `undriven` verdict repaired in the same commit before it counts. The ledger is written only through `gz` verbs. No control is removed; lowered to advisory is not removed.

## The standard shape of a drydock

A contract instantiates the shape below. An instance adds orders as its appraisal finds them and marks a standard order "not applicable" with its reason rather than deleting it. The sequence is by dependency; orders that touch disjoint surfaces run in parallel on cheaper sessions.

| Order | Serves | What it lands |
|---|---|---|
| RO-0 | the drydock itself | the contract and the drawing ratified; the toggle's suspension in force; prior drift disposed |
| RO-1 | control plane | the bleeding stopped: whatever an agent loads cut to its budget first, measured for effect |
| RO-2 | identity | the seam that gives every artifact its own identity by alias and resolver, renaming nothing |
| RO-3 | catalog | the requirements store and the feature-area registry as empty structure, with their validators |
| RO-4 | version | the release detached from whatever carried it, one release shape, closeout keyed to it |
| RO-5 | labor, maintenance | the work-package, task-card and repair-order structure, with the repair tagging scheme |
| RO-6 | every band | the canon the general arrangement contradicts, retired with retention maps |
| RO-7 | control plane | the rest of the cut, staged, with an effectiveness report per stage |
| RO-8 | the in-flight work | disposition of what was open when the drydock began, and the handback |

**Standing exit measures.** The load of every surface an agent reads (the root contract, the rules in total and the largest, the skill descriptions and the skill bodies, the agent definitions, the nested `AGENTS.md`, the personas, the text the hooks inject each turn), each within a witnessed budget with an effectiveness report; the count of controls with no named contract, at zero; every reader resolving identity through the seam. The instance sets the values.

## The Release Package

The release management document type, the rung the ADR wrongly carried until 2026-10-16 (operator, verbatim: *"adrs are not releases"*; *"i must have a release management document type too"*; named the same day: *"Release Package it is"*). The vocabulary runs in one line: the work package is the labor on one contract, the Release Package is the set of work packages and the entry states a version ships, the release record in the ledger is what actually shipped (Q-10), and the release is the captain's signature on it. One document type carries the lifecycle in its `status`: `planned` while it is filled, `in-flight` while its packages land, `released` when the operator signs. One document per version under `docs/design/releases/`, named by the version it governs, from `.gzkit/templates/release_package.md`:

- frontmatter: the version; `status` (`planned`, `in-flight`, `released`); the catalog entries whose state advances, each with its from and to state; the work packages shipped; the lane and its gates; the operator's attestation;
- body: the intent of the version for the operator and for adopters, and the one-open-defect assessment the constitution's policy 12 requires.

`gz closeout` keys to it once RO-4 lands; the ADR stops carrying a version then. Gate 5 stays per work package, and a release carries its own attestation on top (ruled 2026-10-17, R2). The campaign sequences releases; a Release Package says what one release contains. A patch release uses the same document with a short list.

## What safe mode never suspends

Gate 5 attestation; the ledger through verbs; operator PII; the PRIME DIRECTIVE; and no control is removed. These are the hangar's `gate5_invariants` and the contract's standing list, and they hold in every mode. Every other guard runs at advisory while the marker is open and at full strength at the exit.

## Entry and exit, mechanically

- Entry: the operator invokes the `gz-mx` skill, which confirms the contract's sections and runs `gz mx enter --mode safe --contract <path> --reason "<why>" --attestor g0`. The marker, the event and the banner record the mode.
- Exit: the skill reads the contract's exit, stops on an unmet condition, and runs `gz mx exit --attestor g0`, the hard gate that re-runs every guard at full strength and renders the enter-to-exit log. The handback amendment follows the exit and precedes civil rule.

## Lineage

The harbor pilot and the drydock come from maritime practice: a licensed local pilot takes the conn for a passage the master cannot know, and a vessel is surveyed and repaired out of the water before a return to service. The hangar came first in gzkit (ADR-0.0.74, 2026-06), from aviation maintenance: return to service after a hard gate. Safe mode joins the two: the hangar's marker, demotion and gate, the pilotage's contract and passage log. The first instance ran from 2026-10-15; its first two days ran as one long exceptional period with harbor legs and a sea trial as the exit, which the operator corrected on 2026-10-17 to the shape above (verbatim: *"your whole dry dock plan was ill conceived - can we get the purpose of safe mode and dry dock clear please?"*). Its contract and passage log are the worked example this doctrine generalizes.
