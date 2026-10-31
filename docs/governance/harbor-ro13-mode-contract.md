<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-13 specification — the two-way mode contract

**2026-10-31. Status: specified; its open points ruled one at a time, drafted by the agent at the operator's request (*"I want a RO-13 tranche page"*), and the page and its tranches accepted by the operator the same day (*"i accept"*).** Operator: **g0**. Repair order RO-13 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving every band and the control plane. Split around RO-4 to RO-8 (operator: *"c"*): the foundation tranches land after RO-11 and RO-5's tranche 6 (operator: *"A"*, 2026-10-31), the retrofit tranches after RO-8. The rulings are quoted with the options put in the contract's § Rulings of 2026-10-31. The design is the [contractor-kit record](../rnd/contractor-kit.md), whose counts are dated measurements.

## Scope

Every control gets a declared contract, in both directions. **Inbound:** the control's level under the central condition signal, applied at its place of call, never by the declaration. **Outbound:** a built-in self-test reporting its suitability for function. The record's reason stands: gzkit could not be modified with all its features on (*"We were causing tampering in places where dampening was happening, and vice versa."*).

`GATE5_INVARIANTS` is never listed. Its members hold no MEL entry, are never demoted, and are outside the baseline's count.

This order does not repair the MX system itself. GHI #1273 is an RO-12 precondition, and F2 builds on what it leaves.

## Rulings

1. **Split** (operator: *"c"*). The foundation goes after RO-11 and RO-5's tranche 6, before RO-4, so RO-4 to RO-8 declare in the real shape from their first commit. The retrofit goes after RO-8, against the final structure.
2. **One control per distinct check, wherever it is reached** (operator: *"A"*). The entry sits at the implementation. A step, hook line or twin that only dispatches to it inherits that entry.
3. **A control's CLI refusal goes through one named call carrying its control identity** (operator: *"a"*). A plain `GzCliError` stays a usage error.
4. **The checkpoint is one temporary group entry** (operator: *"a"*). Its members keep today's demotion and leave as each gets its own entry. The baseline counts them as having none, and the MEL view shows them not yet contracted.
5. **The operator rules a default level per role** (operator: *"a"*). An entry at its default is written by the craftsman and inspected by the QAI, role label included. An entry below default, any level of off in particular, stops for the operator.
6. **A modification is profound when any fact in the entry stops being true** (operator: *"a"*): what the control refuses, when it fires, its level, bypass, limitation, placard or self-test. The craftsman amends the entry, and the control drops to *not yet accepted*.
7. **The retrofit runs code by role, then skills, then rules and the other surfaces** (operator: *"a"*).
8. **Self-test intervals are defaults per role and kind, in JSON** (operator: *"a"*). An entry shortens its own freely; lengthening past the default is on the operator's word.
9. **The self-test chore is admitted, and `gz check` re-proves what a change touches** (operator: *"a"*).
10. **Lockout is dropped as a mode signal** (operator: *"A"*). The tag-out log carries isolating one surface. An entry declares no lockout level, and the doctrine's one condition with a standby level, hangar or drydock, stands.
11. **The operator and a working session land F1 to F5; the drydock contractor lands R1 to R3 under the kit** (operator: *"A"*), a tranche at a time, stopping on an entry below default.

Carried from the record, not re-ruled: one MEL entry per control (level per standby level, (M) bypass, (O) limitation, placard, restore condition and deadline, self-test interval, accepted state); two decorators joined by reference, `@enforces` unchanged; three declaration shapes against one schema (decorator, Markdown MEL block, `gzkit.mx.alarms` arguments); suitable when the latest self-test passed within the interval; accepted only on a passing self-test and an inspected red witness.

## Tranches (for the contractor)

The contractor stops and waits on every structural question; the names of new verbs, decorators, events and data files are among them. Every surface these tranches add carries the contract from its first commit.

### Foundation, after RO-11 and RO-5's tranche 6

- **F1, the declaration.** The shared Pydantic MEL model and its schema. The MEL decorator, metadata-only at import, with a self-test reference that names no registered claim or arm failing at decoration, on the precedent of `enforces` in `src/gzkit/enforcement.py`. The Markdown MEL block and its validator. The MEL arguments on the `gzkit.mx.alarms` wrapper.
- **F2, the place of call.** The reader that takes declaration and signal through one function, widening `resolve` in `src/gzkit/mx/checkpoint.py` from one marker reading to the doctrine's condition and standby level. The group entry of ruling 4. No control changes behavior in this tranche.
- **F3, the refusal call.** The named call of ruling 3 beside `GzCliError` in `src/gzkit/commands/common.py`. It lands used by no existing site; the sort of those sites is R1's.
- **F4, the enumerator and the baseline.** The enumerator resolves what dispatches to what across the census's dispatchers (`docs/rnd/contractor-kit/sources/census-code-controls.md` § 10b) and the model-surface kinds, and produces the real population, replacing the census's 421 and 206 as a measure. The MEL view is the derived join of the declarations and the registries, Layer 3, and never blocks a gate. The shrink-only baseline counts controls with no entry, group members included, and refuses a new unlisted control.
- **F5, the self-test channel.** A receipt writer for the chore `--self-test` arms, as `run_meta_validator` writes `enforcement_claim_verified` for claims. The arms' exit statuses made uniform, so a failed self-test cannot meet the step seam's demotion on exit code 3, and the `assert`-based arm in `check_cross_reference_staleness.py` rewritten so it runs under `python -O`. The self-test chore admitted, and `gz check` re-running the self-tests of each control a change touches.

### Before the retrofit

- **T0, the tables.** The agent drafts the default level per role and the default interval per role and kind; the operator rules each. Nothing in R1 to R3 starts without them.

### Retrofit, after RO-8

- **R1, code controls by role.** Alarms, gates, then safeguards, monitors and tripwires. Every `raise` site is read and sorted once, and each control's refusal moves to the named call. Twins collapse to one entry (GHI #1274's class).
- **R2, skills.** The contract carried through prompts and skill routing, by the Markdown block; the self-test reference may name `gz-skill-review`.
- **R3, rules and the other surfaces.** Rules, personas, agent definitions, chores, templates and the text-injecting hooks, by the Markdown block.

Each control leaves the group entry when it has its own entry, a passing self-test and an inspected red witness. A control an earlier order retired is not retrofitted; the enumerator stops finding it.

## Restoration (RO-13's list-of-discrepancies lines)

The lines are in the contract's § List of discrepancies under RO-13.

## Witness

The shrink-only baseline of controls with no MEL entry, closed at zero, read from the enumerator. The foundation's unit tests, run against a temporary tree holding one declared control, one unlisted control and one group member. Each restored control's inspected red witness (the contract's RO-12 row, refusal 8).
