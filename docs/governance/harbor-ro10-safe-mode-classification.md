<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-10 specification — safe-mode guard classification and A/B/C/D scheduling

**2026-10-25. Status: PARKED.** Drafted from the design session of 2026-10-25 and parked by the operator's word (*"yes, draft RO-10 and park it"*). It is not worked during this drydock. Its home is the new requirements, work and release system (RO-3 to RO-5): this design is meant to be one of that system's first entries, which is why it waits for it. Operator: **g0**. Repair order RO-10 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders).

## Why this order exists

The drydock's § Records clause, agent-drafted in `17d80ef7a` and ratified with the whole contract, required `gz arb red --commit` and a failing test on every act. Wide RO-9 commits made each witness run take half an hour or more, and the witness itself became repair work (GHIs #1260, #1268, #1269). The operator stopped it (*"this is all backwards"*). The session that followed designed what safe mode should switch off and why. It found that the design needs care, and that MX's A/B/C/D checks have no timed trigger.

## Rulings

Operator, verbatim, 2026-10-25, each also recorded as an insight:

- *"i don't want any long check at all - this is a remodel, things are going to be broken, disarray, and messy. it is time to leave things partially broken until the reconfiguration is complete, then we adjust tests and turn the "security alarms" back on. this is all backwards."*
- *"now, the renovation contractor must reattach all safeguards and reconfigurethem if they've been altered/rerouted/changed, etc. that is part of the repair order. It is the RO's obligation to restore the system either to prior operations or the repaired/renovated new operational status, which why it is important to disconnect all guards and alarms. The RO (or a sequence of ROs) are obligated to return the system to a prior, or new, stable system state."*
- *"never, ever, ever turn this off: "the pytest ban""*; *"ruff and ty are reasonable too - this is why I offered to review this to create a reasonable safe mode with you"*.
- On the three kinds of protection: *"1. yes; 2. yes; 3. yes, off"*.
- *"tripwires for the cheap ones, long ones fully off. however length is not necessarily an indicator of importance. we need a metric/rubric to reason about tgis distinction."*
- On the rubric: *"yes, write it into the doctrine, but how will tthese be established and periodically reviewed? at creation, of course, but, how about over time? particularly as the system evolves? also, your consequence observation is a matter of carefully planning and scoping the RO."*
- On scope: *"this entire mechanism needs to be designed, reveiwed, and carefully implemented. I am okay with this being a new RO, but we need to record this entire design session to come up with a spec."*; *"We need a bit of both - a leaner version now to get by, and heavier finishing verison."*
- *"yes, freeze lean, park the spec, two contractors - also, the A/B/C/D system, which is evidently in-place via the mx system, does NOT have a timed system of review that the chores does. I know that we have gates/tripwires to require/force chores review, take note that the A/B/C/D system is meaningless if it also doesn't have a timed component to enforce it."*

## The lean version, in force now (frozen)

Landed 2026-10-25 and frozen for the rest of this drydock (`757ddea7e`, `62e4041d6`, `fbd1c376c`):

- `gzkit.mx.alarms` switches off six pre-commit and pre-push hooks and the verifier pipe gate while the marker carries `mode: safe`; the `gz mx exit` re-run sounds them at full strength.
- On throughout: the secret scan, the authorship check, the guards sweep (the pytest ban pinned `CRITICAL`, the ledger and Gate-5 guards), ruff and ty.
- No per-act check; a § List of discrepancies (formerly § Punch list) in the contract; each repair order restores what it disconnected, rerouted or changed before it closes.

Amended 2026-10-27 (a record of that day's change; the freeze above is otherwise kept): two of the six hooks, the complexity ceiling and the cheap surface-fidelity subset, no longer route through `gzkit.mx.alarms`, and a whole-tree `gz lint` runs at every push; all are pinned `CRITICAL`. Operator, verbatim: *i think, even during repairs or contruction, somebody sweeps up the shop floor every night. The point is, it is too strivt to disable linting during safemode drydock/mx hangar. We are writing/changing code and that deserves*

## The heavy version, to design

### 1. Three kinds of protection

| Kind | What it guards | Disposition in safe mode |
|---|---|---|
| 1 | Damage that cannot be undone: secrets, operator PII, the ledger, attestation | Alarm, always |
| 2 | Rules that define what gzkit is: unittest only, ruff, ty | Alarm, always; a misfire is a defect fixed at once |
| 3 | Checks that measure the old structure: budgets, ratchets, pinned tests, the full suite, `gz check`, the commit witness | Off, or a tripwire; restored by the order that changed it |

### 2. Alarm versus tripwire

An **alarm** stops the work. A **tripwire** does not stop the work and does not ring; it records that an order touched something it guards, as a list-of-discrepancies line, so the contractor finds it at closing. A tripwire must run its check to know it tripped, so it suits checks cheap enough to run per commit.

### 3. The rubric

Read top to bottom; the first rule that applies decides.

| Step | Question about the check | If yes |
|---|---|---|
| 1 | Does it guard damage that cannot be undone? | Alarm |
| 2 | Does it enforce a rule the new structure must meet anyway? | Alarm; a misfire is fixed at once |
| 3 | Does it measure the surface this order is deliberately rebuilding? | Off: it trips on every intended change |
| 4 | Does it measure something nearby the order could disturb by accident? | Tripwire: it catches collateral, not intended change |
| 5 | Can it run within a commit's time budget? | If not, a would-be tripwire becomes an off item with a named restoration check |

Cost decides how a check runs, never whether it matters (step 5 is last). Steps 3 and 4 are answered by the order's own planning and scoping: its specification names its subject and its surroundings, and the dispositions follow.

### 4. Establishment and review over time

- Classifications are data, read by the switch, not prose: each guard's kind and cost class.
- A guard with no classification is an alarm, as an unregistered guard resolves `CRITICAL` today, so drift runs toward more protection, never less.
- Evidence for reclassification comes from use: a tripwire that trips on every order measures intended change; one that never trips is guarding something stable, or is dead; an alarm that misfires is a defect.

### 5. A/B/C/D checks need a timed trigger

ADR-0.0.74 (line 114) deferred *"the full MEL dispatch-with-limitation binder ((O)/(M) procedures + A/B/C/D repair intervals)"* to "Phase 2", and no registered artifact carries Phase 2. The checks exist in name with no interval behind them. By the correction-versus-enhancement doctrine this is a correction owed to ADR-0.0.74, carried here. In aviation every check level runs on a schedule (cycles, hours or calendar, whichever comes first), and only accident repair is unscheduled; this drydock is accident repair. The chores system already has timed triggers and gates that force review, and is the precedent.

## Open questions

1. **The pipe gate's kind.** Kind 2 (honest exit codes) or kind 3 (process friction). It misfires on heredocs; if kind 2, that misfire is fixed at once. Not yet ruled.
2. **When classifications are reviewed:** at each safe-mode entry, on a timed schedule, or both. Ruling 5 above requires a timed component for the A/B/C/D checks; whether the same applies to classifications is not yet ruled.
3. **gzkit's cycles and hours.** What an A/B/C/D interval counts: commits, releases, sessions, work packages, or calendar time.
4. **Where classifications live,** and how RO-5's repair-order template carries each order's subject and surroundings.

## Leads, not in scope

The A/B/C/D finding has a searchable shape: a scope deferred to "Phase 2" or "a later ADR" with no registered destination. Other instances likely exist; a sweep for that shape is a candidate for the follow-up contractor or a chore.
