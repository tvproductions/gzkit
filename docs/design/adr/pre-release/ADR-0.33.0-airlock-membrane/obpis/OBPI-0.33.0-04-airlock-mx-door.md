---
id: OBPI-0.33.0-04-airlock-mx-door
parent: ADR-0.33.0-airlock-membrane
item: 4
lane: Heavy
status: Draft
req_atomic:
  # Each REQ is one indivisible unit of labor — a single Red-Green-Refactor
  # cycle each: 01 the mx-enter -> airlock-IN call site, 02 the mx-exit ->
  # airlock-OUT call site, 03 the corrective (medium) ceremony-weight profile
  # threaded to the shared primitive, 04 the consume-only / no-private-fork
  # fence. No labor is subdivided below any REQ. This is a GATED-BREADTH OBPI:
  # no REQ begins until OBPI-02's section-5 live NC bites live.
  - REQ-0.33.0-04-01
  - REQ-0.33.0-04-02
  - REQ-0.33.0-04-03
  - REQ-0.33.0-04-04
---

# OBPI-0.33.0-04-airlock-mx-door: Airlock Mx Door

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`
- **Checklist Item:** #4 - "mx door: wire airlock enter/exit into gz mx enter/exit (corrective-scoped ceremony). [BEHAVIOR; gated-breadth]"

**Status:** Draft

## Objective

Wire the mx/ghi door — `gz mx enter` / `gz mx exit` — into the SHARED airlock
primitive extracted by OBPI-02/03: `mx_enter_cmd` CALLS airlock-IN
(`gzkit.airlock.airlock_in`) and `mx_exit_cmd` CALLS airlock-OUT
(`gzkit.airlock.airlock_out`), at CORRECTIVE (medium) ceremony weight — so
every mx transit crosses the SAME membrane the pipeline door does, calibrated
between the pipeline's tight bar and permitted-entry's permissive bar. The mx
door ADAPTS to the airlock; it NEVER forks a private airlock variant (parent
ADR § Decision: "the airlock is never forked per-door" — one extracted
primitive the doors CALL). **GATED-BREADTH:** this OBPI does not begin until
OBPI-02's section-5 live negative control (un-accounted seam → GO structurally
unreachable, un-forced production) bites live (parent ADR § Decision + BI-4).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it changes the runtime behavior of two operator-facing CLI
verbs humans invoke — `gz mx enter` and `gz mx exit` — inserting the airlock
membrane (an acknowledge-and-decide gate) into the enter/exit path. That is a
runtime-contract change to the mx door surface, not a documentation- or
process-only edit.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new
     files (existence-gate exempt, GHI #419). Disjoint from siblings: the
     airlock primitive itself (src/gzkit/airlock/*) is OBPI-01/02/03;
     pipeline_runtime.py is OBPI-02/03; the permitted-entry surface is OBPI-05;
     doctrine docs are OBPI-06. This brief touches the mx command module only. -->

- `src/gzkit/commands/mx_cmd.py` — additive call sites ONLY: `mx_enter_cmd` invokes `gzkit.airlock.airlock_in` before the marker write; `mx_exit_cmd` invokes `gzkit.airlock.airlock_out` at the co-equal exit. The door CALLS the shared primitive; it defines no local airlock logic.
- `tests/test_mx_door_airlock.py` — **CREATE**: `@covers`-decorated REQ tests for the mx-door airlock wiring (enter→airlock-IN, exit→airlock-OUT, corrective ceremony weight, consume-only/no-fork).
- `docs/user/manpages/mx-enter.md` — additive: document that `gz mx enter` now fires the airlock-IN membrane (corrective ceremony) before opening the hangar.
- `docs/user/manpages/mx-exit.md` — additive: document that `gz mx exit` now fires the airlock-OUT membrane (co-equal) at close.
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` — parent ADR for intent, § Decision, and Boundary Invariants (READ-ONLY reference; no edit).
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-04-airlock-mx-door.md` — this brief (evidence).

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/airlock/**`, `src/gzkit/schemas/airlock_*.json` — OBPI-01/02/03 OWN the extracted primitive + its ledger-event schemas; this door CONSUMES only, never modifies.
- `src/gzkit/pipeline_runtime.py`, any pipeline Stage-1/Stage-5 wiring — the pipeline door is OBPI-02/03, the calibration reference this door adapts to.
- The permitted-entry surface (any new ad-hoc/spurious entry command module) — OBPI-05.
- `docs/governance/work-phases-and-airlock.md`, `docs/governance/four-phases-of-work.md` — the doctrine-lawful promotion is OBPI-06.
- `src/gzkit/cli/parser_governance.py` — UNTOUCHED NEIGHBOR: the `gz mx` subparser already captures `--reason`/`--attestor`/`--scope`; the airlock call sites need no new parser surface.
- Any path not listed in Allowed Paths; new runtime dependencies; CI files; lockfiles.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: `mx_enter_cmd` MUST call the SHARED airlock-IN primitive (`gzkit.airlock.airlock_in`) and `mx_exit_cmd` MUST call the SHARED airlock-OUT primitive (`gzkit.airlock.airlock_out`) extracted by OBPI-02/03 — consume-only.
2. NEVER: fork, copy, or reimplement a private airlock variant inside the mx door. One extracted primitive the doors CALL, never fork (parent ADR § Decision; BI-3; Negative #3 "Door drift").
3. ALWAYS: the airlock gate fires on EVERY mx entry regardless of the repair `--reason` — the reason selects ceremony WEIGHT only, never whether the gate fires (parent ADR BI-2).
4. ALWAYS: the mx door invokes the airlock at CORRECTIVE (medium) ceremony weight — calibrated BETWEEN the pipeline door's tight bar and permitted-entry's permissive bar, calibrated to the pipeline (parent ADR § Decision: "pipeline tight; mx corrective; permitted-entry permissive").
5. NEVER: emit or record the airlock's acknowledge-and-decide gate as a completion attestation — it is a DIFFERENT sort of operator input; the sacred word stays reserved (parent ADR BI-3). The airlock gate is ADDITIVE to `mx exit`'s existing hard guard-gate, never a replacement for it.
6. NEVER: mutate `src/gzkit/airlock/*` or the pipeline Stage-1/Stage-5 wiring — this door adapts to the primitive; it does not reshape it. The airlock never writes L1 canon (BI-1) — the mx door's call sites propose/log to L2 only.
7. NEVER: begin implementation until OBPI-02's section-5 live NC bites live. This is the gated-breadth precondition (parent ADR § Decision + BI-4); a BLOCKERS halt fires if the NC is not yet biting.

> STOP-on-BLOCKERS: if prerequisites are missing (notably the OBPI-02 live-NC
> precondition or the `gzkit.airlock` primitive), print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the three-doors / mx=corrective line** verbatim into `### Implementation Summary`. The contract is: "mx and permitted-entry adapt to the airlock; the airlock is never forked per-door" and "ceremony scales by door (pipeline tight; mx corrective; permitted-entry permissive), calibrated to the pipeline." The mx/ghi door is the DEFECT-REPAIR door — "correction to a desired state" (§ Intent).
- [ ] Parent ADR § Intent — the three-entry-reasons / three-doors why-frame ("mx/ghi (defect repair -- correction to a desired state)").
- [ ] Parent ADR § Boundary Invariants — BI-2 (gate fires on every entry; reason/door selects ceremony weight only), BI-3 (acknowledge-and-decide, never completion attestation), BI-4 (un-accounted seam → GO structurally unreachable — the gated-breadth NC this door waits on).
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`

> **STOP:** If you cannot quote the parent ADR § Decision line that this OBPI
> implements — the "adapt to the airlock; never forked per-door" line and the
> "mx corrective" ceremony-calibration line — STOP and re-read. Do not proceed
> to Allowed Paths, Prerequisites, or implementation until the Decision quote
> is in hand. **AND STOP** if OBPI-02's section-5 live NC is not yet biting:
> this is a gated-breadth OBPI that does not begin before that keystone lands.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/mx-mode.md` — honor-the-marker + PRIME-DIRECTIVE doctrine for hangar sessions; the airlock gate is additive to, never a replacement for, the hard exit gate.
- [ ] `AGENTS.md` § "Every REQ … [kind]" (ADR-0.0.59) — the REQ-kind discipline the Acceptance Criteria below obey (all four are BEHAVIOR → each proven by a `@covers` test under `tests/`).

**Context:**

- [ ] Sibling OBPI-0.33.0-02 (airlock-IN) and OBPI-0.33.0-03 (airlock-OUT) briefs — the extracted primitive's shape (`airlock_in`/`airlock_out`, the door-ceremony profile parameter) this door CONSUMES.
- [ ] OBPI-0.33.0-05 (permitted-entry) — the permissive end of the ceremony scale; this door sits between it and the pipeline.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.33.0-02 landed AND its section-5 live NC bites live (`uv run gz validate --qc-binding` green) — the gated-breadth precondition. STOP here if the NC is not yet biting.
- [ ] `src/gzkit/airlock/` package present, exporting `airlock_in` / `airlock_out` with a door-ceremony profile parameter (OBPI-01/02/03) — the shared primitive this door CALLS.
- [ ] `src/gzkit/commands/mx_cmd.py` present with `mx_enter_cmd` and `mx_exit_cmd` — the additive call sites land inside these two functions.
- [ ] Parent ADR present, registered in `gz state`, carrying a `## Boundary Invariants` section (BI-2 / BI-3 anchors).

**Existing Code (read; do NOT modify — establishes the conventions this door mirrors):**

- [ ] `src/gzkit/commands/mx_cmd.py` — `mx_enter_cmd` (marker write + `mx_session_opened` ledger event) and `mx_exit_cmd` (hard-gate guard re-run + `mx_session_closed`) — the enter/exit seams the airlock call sites bracket; read how reason/attestor/scope are already captured.
- [ ] `src/gzkit/cli/parser_governance.py` `gz mx` subtree — the `--reason`/`--attestor`/`--scope` inputs already flow into `mx_enter_cmd`/`mx_exit_cmd`; confirm no new parser surface is needed (UNTOUCHED NEIGHBOR).
- [ ] `src/gzkit/mx/marker.py` + `src/gzkit/mx/log.py` — the marker/log seams around which airlock-IN (pre-marker) and airlock-OUT (pre-close) fire.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/mx-enter.md` + `mx-exit.md` updated for the airlock membrane

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- CONSTRUCTION HOUSEKEEPING (lint, type, test, mkdocs) proving the codebase
     is healthy. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects (GHI #415).
     One command per line. -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_mx_door_airlock -v
```

## Demo

<!-- THE YIELDED PRODUCT: a corrective mx transit that crosses the airlock
     membrane on the way IN and the way OUT. Concrete, runnable invocations
     (not --help). Harvested by the closeout walkthrough. -->

```bash
# A corrective mx transit — the mx/ghi door is for DEFECT REPAIR (correct the
# environment to a desired state). airlock-IN fires FIRST, at CORRECTIVE (medium)
# ceremony: it declares the repair intent, pings the shape via the HULL sonar,
# reconciles the seam-map, and reaches the acknowledge-and-decide gate BEFORE the
# hangar marker is written. The gate fires regardless of the --reason (BI-2).
gz mx enter --reason "repair drifted OBPI brief allowlist" --attestor g0 --scope ADR-0.0.74

# ... perform the governance repair ...

# airlock-OUT fires (co-equal, same corrective weight): drift-diff of what the
# repair disturbed, findings + decision menu, routing any discovered correction
# as a FRESH transit, logging to L2 — additive to the existing hard exit gate.
gz mx exit --attestor g0
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59). All four are BEHAVIOR:
     each is proven by a @covers test in tests/test_mx_door_airlock.py. The
     BEHAVIOR proof channel requires tests/** in Allowed Paths (declared above). -->

- [ ] REQ-0.33.0-04-01 [BEHAVIOR]: `gz mx enter` calls airlock-IN — `mx_enter_cmd` invokes the SHARED `gzkit.airlock.airlock_in` primitive BEFORE writing the hangar marker, and the call fires for ANY `--reason` value (BI-2: the reason selects ceremony weight, never whether the gate fires); a `@covers(REQ-0.33.0-04-01)` test in `tests/test_mx_door_airlock.py` asserts (a) the airlock-IN call is made on enter across two distinct `--reason` values, and (b) a refused (NO-GO) airlock-IN blocks the marker write and exits non-zero.
- [ ] REQ-0.33.0-04-02 [BEHAVIOR]: `gz mx exit` calls airlock-OUT (co-equal) — `mx_exit_cmd` invokes the SHARED `gzkit.airlock.airlock_out` primitive at close; a `@covers(REQ-0.33.0-04-02)` test asserts the airlock-OUT call fires on exit and is additive to (does not bypass or replace) the existing hard guard-gate that must still pass before `mx_session_closed` is written.
- [ ] REQ-0.33.0-04-03 [BEHAVIOR]: corrective-scoped ceremony — the mx door invokes the airlock at CORRECTIVE (medium) ceremony weight, calibrated between the pipeline's tight bar and permitted-entry's permissive bar; a `@covers(REQ-0.33.0-04-03)` test asserts both call sites pass the mx/corrective door-ceremony profile to the shared primitive (NOT the pipeline's tight profile and NOT permitted-entry's permissive profile), so a drift to another door's weight fails the test.
- [ ] REQ-0.33.0-04-04 [BEHAVIOR]: no private fork — the mx door CONSUMES the shared primitive only and defines no local airlock reimplementation; a `@covers(REQ-0.33.0-04-04)` test asserts `gzkit.commands.mx_cmd` imports `airlock_in`/`airlock_out` from `gzkit.airlock` (the single extracted source) and that the module declares no local `def airlock_in`/`def airlock_out` or private seam-map/gate logic (parent ADR BI-3; Negative #3 "Door drift").

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
