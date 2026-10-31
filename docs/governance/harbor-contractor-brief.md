<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Drydock contractor brief

**Last updated: 2026-10-31.** Operator: **g0**. The instructions for the two contractors of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md) (operator, 2026-10-25: *"freeze lean, park the spec, two contractors"*). Ruled the same day: *"specify all six first and launch the contractor once on everything"*; on a structural question the contractor stops and waits (*"A"*). **Amended 2026-10-28** with the contract (its Status line) on the operator's sign-off of the contractor-kit R&D, verbatim *"fund, yes to 2 and 4"* ([`docs/rnd/contractor-kit.md`](../rnd/contractor-kit.md)): the launch now runs RO-5, then RO-12, then the rest under the kit (operator: *"A"*; record decision *the kit is RO-12, placed immediately after RO-5*), and the compliance register is three records, the tag-out log, the maintenance record and the list of discrepancies (contract § Records).

## The drydock contractor

**Goal.** Land the repair work of every open repair order, in register order, as its specification states, with the alarms off, recording everything each act unplugs, dismantles or modifies in the three records (until RO-12 lands them, as lines in the contract's § List of discrepancies). Leave each order open for the restoration contractor.

**Order of work** (the register's order, which is dependency order):

1. [RO-5](harbor-ro5-work-packages.md) — work packages, repair orders, GitHub coupling (five tranches).
2. RO-12 — the contractor kit. **Not worked by this contractor**: the operator and a working session build it (the bootstrap, the contract's § Division of labor), after #1200, #1206, #1208, #1028 and #1273 and the other reused-part defects the contract's RO-12 row lists are repaired as direct fixes. Stop and wait. Every order below then runs under the kit as its first flight.
3. [RO-11](harbor-ro11-intake.md) — intake: the capability records, the three-letter legend and the entry verb (three tranches; placed before RO-4, amended 2026-10-30, operator: *"A"*).
4. [RO-13](harbor-ro13-mode-contract.md), foundation tranches F1 to F5 — the two-way mode contract's shared parts (operator: *"c"*). **Not worked by this contractor**: the operator and a working session land them (operator: *"A"*). Stop and wait.
5. [RO-4](harbor-ro4-release.md) — release detached from the ADR (four tranches).
6. [RO-6](harbor-ro6-canon-retirement.md) — superseded canon corrected (three tranches).
7. [RO-7](harbor-ro7-context-cut.md) — the context cut (seven stages, each measured by [RO-1's protocol](harbor-ro1-cut-measurement.md); RO-1's baseline report is written first).
8. [RO-8](harbor-ro8-in-flight-work.md) — the in-flight work absorbed (four acts; act 3 waits for the operator's review).
9. [RO-13](harbor-ro13-mode-contract.md), retrofit tranches R1 to R3 — code controls by role, then skills, then rules and the other surfaces, after the operator rules the tables (T0).

RO-10 is parked and not worked. RO-9 closed through Gate 5 on 2026-10-29.
**Each act:**

- One commit: `fix(<scope>): … (GHI #N)` or `feat(<scope>): …` or `docs(drydock): …`, with a `Task: TASK-ro<n>-<slug>` trailer.
- One passage-log row in the contract: what changed, the measurement before and after, the commit.
- One line in the contract's § List of discrepancies (formerly § Punch list, the compliance register) for each item the act unplugs, dismantles or modifies: its disposition (restored, reconnected, retired, or replaced by a named successor), its authority, and `open`; a discrepancy is graded *blocks return to service* or *due by a named event*, and takes root cause and corrective action only when it blocks return to service or recurs (the contract's § List of discrepancies).
- No long check: no `gz arb red --commit`, no `gz check`, no failing test required first. Tests may stay red; what is left broken goes on the list of discrepancies.
- Commit through the hooks, never `--no-verify`. Push after each act.

**Always on, never worked around:** the pytest ban (unittest only), ruff, ty, the secret scan, the authorship check (operator authorship is `g0`; never the operator's personal email), the ledger written only through `gz` verbs, Gate 5 (no OBPI is initiated or completed).

**Stop and wait for the operator, one question at a time, with a recommendation:**

- every structural question a specification does not answer, including the names of new `gz` verbs and ledger events;
- every binding loss a cut stage finds (RO-1 step 4);
- the skill demotion list (RO-7 ruling 3) and the catalogue merge plan (RO-7 stage 6), each as one batch;
- RO-8 act 3;
- RO-12 and RO-13 (above);
- any repair order that needs the contract changed: the contract changes only by its own amendment, never through a repair order (contract § Records, B1);
- anything that would delete data, rewrite history or force-push.

A stop is not a failure: record where the work stands in a handoff (`gz handoff create`) and wait.

## The restoration contractor

**Goal.** Return the system to a stable state: clear every line of the three records (the contract's § List of discrepancies until RO-12 lands them) with the alarms on, so each repair order can close through the operator's Gate 5.

**Work:**

1. For each order, in register order, clear its lines: reattach and reconfigure each item to its disposition, adjust the tests to the new structure, and mark the line `cleared` with its commit.
2. Run RO-1's restoration flight (GHI #1252) and the commit witness's restoration (GHI #1268, the #1269 rerun on `7b7ea83cd`).
3. Bring each order to the operator for Gate 5: proceed, redirect, pause or terminate.
4. When every line is cleared and every order closed, the sea trial (§ Exit 10) is done by the normal crew rather than the contractors; on its pass the handback (§ Exit 9) goes to the operator for ratification, then `gz mx exit` through the `gz-mx` skill.

## Launching

The operator launches each contractor in a fresh session. The goal is the **Goal** paragraph of its section above; the loop prompt is: *"Read `docs/governance/harbor-contractor-brief.md` and the latest handoff; take the next act of the next open repair order in its order of work; stop and ask where the brief says to."*
