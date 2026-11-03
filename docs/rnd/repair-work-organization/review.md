# Repair work organization: the review before sign-off

> A view over [`docs/rnd/repair-work-organization.md`](../repair-work-organization.md), written 2026-11-03 and rewritten the same day after the operator's corrections at the first walk-through. It holds no authority: where it and the record disagree, the record governs. Every name below is marked **ruled**, **sourced**, **contradicted** or **unsourced**.

## The problem

gzkit's maintenance work was organized by structure the agent improvised. *Act* and *tranche* had no definition, record or witness. *"A repair order is a work package"* sat at the wrong level, and the work package had been named the OBPI's successor when it is the mADR's. The requirement concept excluded repair, so an issue stood in for a REQ and a docs issue had no honest proof. *Hangar* and *drydock* spelled a depth as a place. Left alone, the model would keep improvising such structure and then drift from it (operator: *"if I don't do this, the model will 'vibe code' any arbitrary organizational structure"*).

## The model

### Two columns, four levels each

| Level | Construction | Repair | Succeeds | Decides | Who |
|---|---|---|---|---|---|
| Epic | Feature package | Return to service package | | why, and the measure of success: value delivered, or seaworthiness | Operator |
| Story | Work package | Repair package | the mADR | the cohesive grouping of orders; scope and footprint; initiation | Operator |
| Order | Work order | Repair order | the OBPI | the REQ-to-task binding and order; the freeze; inspection and buy-back; **Gate 5** | Coordinator, inspector, operator |
| Action | Task | Task | the TASK | one recorded action, its measure, its (V) mark | Craftsman |

- A feature package may be fulfilled by many combinations of work packages, and a work package draws REQs from any feature packages. Neither binds a release.
- A work package may ship part of its work; its remainder is rebundled. The requirements model's *one outcome* and *100% rule* are amended.
- Gate 5 sits at the order, as on every OBPI. The package closes when its orders close and its why is answered.
- A repair order freezes once its REQ is known, so a repair package stays open through exploration.
- Both top rows serve users: one delivers value, the other restores a seaworthy vessel.

### One requirement, specialized

A base requirement carries statement, criteria, kind, revision and proof. The catalog requirement belongs to an outcome; the repair requirement is held on its repair package, names its problem report, and may name a design REQ it aligns to. Proof runs one path.

| Input | Relationship to a REQ | Release |
|---|---|---|
| New construction | states a new one | Release Package, minor |
| Repair (restore) | answers what must hold again | patch |
| Remodel | changes one | Release Package, minor |
| Refactor | preserves them as invariants | patch |

MX work advances patches through the patch release skill, not one patch per item: on the operator's judgment for A and B work, perhaps mandatory at `gz mx exit`. The Release Package's members are unchanged.

### Out of service

- The vessel is **out of service** exactly while the MX flag, `.gzkit/mx.json`, is open; returning it is Gate 5's **return to service**. Hangar and drydock are synonyms; the commands stay `gz mx`.
- **The alarm test** decides: work done with every alarm on is on the line, a GHI fixed directly included; work that must lower an alarm, or changes a control or the standard one judges by, is out of service.
- Out of service is one state. What comes down within it is each level's **standard disconnect list**, the manual; today's blanket is RO-13's temporary group entry.
- With the governors off the work still takes care. Running past a disabled limit is a deliberate act of diagnosis or test, noted as such.
- Every opening of the flag has a return to service package: written from diagnosis for an incident, where the drydock contract is that package; generated from the level for a scheduled check.
- The pivot happens in this drydock. Each change is noted in the manual as an airworthiness directive would be, and the vessel returns to service as amended.

### The check levels

| Check | FAA (Order 8900.1 Vol. 20 Ch. 8 Sec. 1) | gzkit | Driven by | Recommended at | Disconnection |
|---|---|---|---|---|---|
| Transit, daily, weekly | line | `gz check`, commit and push hooks | every change | — | none |
| A | line | inspect and report | GHIs | a GHI drawdown | none |
| B | line | repair that touches no control | GHIs | a GHI drawdown | none |
| C | heavy | repair that may reach a control | MX | a minor release, `gz mx exit` | its standard list |
| D | heavy | re-author a control or its standard | MX | a minor release, `gz mx exit` | the widest list |

- Every level is due by date for now; version and event triggers wait for more maturity. *Recommended* means advised, not gated.
- gzkit classifies its own work, as the FAA leaves classification to the carrier.
- Each check includes those below. A chore's level is its inspection's and the repairs that level allows; a finding above it leaves the run as a problem report.
- The census's reading today: A 17, B 4, C 13, D 7. No chore has recorded a run since 2026-10-17. B's exact boundary goes to the classification program.
- The 37 waiver and baseline lists, about 6,796 entries, can only shrink and carry no drawdown commitment. Their drawdown is advised as C work.

## Names, by standing

- **Ruled and sourced:** the four levels A to D, line and heavy maintenance (FAA Order 8900.1); return to service (14 CFR § 43.9, Part 0); problem report; task (AC 120-16G); tag-out; the airworthiness directive as the model for a manual change.
- **Ruled, the operator's own:** return to service package; repair package; work order and repair order; epic and story for the two upper levels; out of service as the flag's state; on the line; the standard disconnect list as the manual; `RP-n`.
- **Ruled, gzkit canon carried:** feature package; work package, re-scoped; `gz mx`; Gate 5 universal (ADR-0.0.36).
- **Contradicted and retired:** *act*, *tranche*; *task card*; *out-of-service package*; *hangar* and *drydock* as two standby levels; *repair order* for what RO-14 is; the work package as the OBPI's successor; *one outcome per work package*; *Gate 5 at the package*; *letter checks absent from FAA text*.
- **Unsourced:** none held as a decision. The Navy's counterpart was not sought further.

## What each disposition row would produce

| # | State | Produces |
|---|---|---|
| 1 ADR / OBPI | not pursued | nothing; the structure is reversible and has governed homes |
| 2 GHI / direct fix | commissioned | the `RP-n` alias; `gz mx enter` requiring the package, and whether a patch release is mandatory at exit; `--level` retired; the census's five statement-mechanism disagreements |
| 3 chore | commissioned | the registry carrying each chore's level and date interval; checks packaged by level; their recommendation points; the waiver drawdown as C work |
| 4 surfaces | commissioned | the model into the requirements model and the four-records succession, the doctrine, the contract, the RP-5, RP-12, RP-13 and RP-14 specifications, `gz-mx`, `mx-mode.md`, the chore class system; *task card* to *task*; the care rule |
| 5 refactoring | commissioned | every chore classified and cut to its level; the checkpoint read through the standard disconnect lists as RO-13 retires its group entry; RP-12 landing the order record, Gate 5 at the order and the repair requirement; RP-14 migrating OBPI to work order |
| 6 no action | commissioned | the Navy counterpart; the hyphen or acronym |

## What this run does not do

It executes no row. It specifies no field, verb or file; that is diamond 2. The RP-12 specification stays paused until sign-off, then takes this model as its ground.
