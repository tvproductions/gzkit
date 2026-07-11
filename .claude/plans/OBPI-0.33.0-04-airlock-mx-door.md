# Plan: OBPI-0.33.0-04-airlock-mx-door

**OBPI:** OBPI-0.33.0-04-airlock-mx-door
**Parent ADR:** ADR-0.33.0-airlock-membrane (feature, heavy)
**Lane:** Heavy

## Context

Wire the mx/ghi door (`gz mx enter` / `gz mx exit`) into the SHARED airlock
primitive extracted by OBPI-02/03, so every mx transit crosses the SAME membrane
the pipeline door does. Per the parent ADR § Decision: "mx and permitted-entry
adapt to the airlock; the airlock is never forked per-door" and "ceremony scales
by door (pipeline tight; mx corrective; permitted-entry permissive), calibrated
to the pipeline." The mx/ghi door is the DEFECT-REPAIR door ("correction to a
desired state", § Intent).

**Booked decision — diagnostic-only tracer (option-c reconcile, attestor g0,
2026-07-11).** The delivered primitive is diagnostic-only at the door; per-door
ceremony calibration, real-entry seam accounting, and the brief-less DECLARE
input are the attested deferred WWHTBT-(a) calibration frontier — NOT this
increment. This increment wires the mx enter/exit seams to the airlock in the
SAME diagnostic-only, calibration-deferred posture the pipeline door shipped: the
acknowledge-and-decide gate LOGS its decision, it does not block the marker write.

**Gated-breadth precondition — CLEARED (verified from ledger):** OBPI-02's §5
live NC bites live (`gz validate --qc-binding` exit 0, facade=0); OBPI-01/02/03
attested complete (commits b786fb8 / c2156a0 / c543bb6); `src/gzkit/airlock/`
present with `airlock_enter` (enter.py:66) and `airlock_exit` (exit.py:233).

**Pattern this door mirrors (reference, READ-ONLY — Denied path):**
`pipeline_runtime.check_airlock_in_gate` / `check_airlock_out_gate` +
`obpi_cmd._run_airlock_in_diagnostic` / `obpi_stages._run_airlock_out_diagnostic`.
Those live in Denied modules, so the mx door CANNOT reuse them — it imports the
primitive DIRECTLY from `gzkit.airlock.enter` / `gzkit.airlock.exit` and calls it,
replicating only the diagnostic-only posture (call primitive → log a NO-GO/finding
→ never `raise SystemExit`).

## Files

- `src/gzkit/commands/mx_cmd.py` — ALLOWED. Additive call sites only:
  top-level `from gzkit.airlock.enter import airlock_enter` and
  `from gzkit.airlock.exit import airlock_exit`; two small diagnostic helpers;
  call sites in `mx_enter_cmd` (before the marker write) and `mx_exit_cmd`
  (after the hard guard-gate passes, before `mx_session_closed`). No local
  airlock logic; no `def airlock_enter`/`def airlock_exit`.
- `tests/test_mx_door_airlock.py` — ALLOWED (CREATE). `@covers` REQ tests.
- `docs/user/manpages/mx-enter.md` — ALLOWED. Additive: document the airlock-IN
  diagnostic membrane fires before the hangar opens.
- `docs/user/manpages/mx-exit.md` — ALLOWED. Additive: document the airlock-OUT
  diagnostic membrane fires (co-equal) at close.

**Denied (do not touch):** `src/gzkit/airlock/**`, `src/gzkit/schemas/airlock_*`,
`src/gzkit/pipeline_runtime.py`, pipeline Stage-1/Stage-5 wiring, the
permitted-entry surface (OBPI-05), the doctrine docs (OBPI-06),
`src/gzkit/cli/parser_governance.py` (UNTOUCHED NEIGHBOR — the `gz mx` subparser
already captures `--reason`/`--attestor`/`--scope`; no new parser surface).

## Steps (Red-Green-Refactor per behavior; one behavior per cycle)

Each step is one REQ = one RGR cycle. Watch each test fail on its OWN assertion
(not an import error) before implementing.

1. **REQ-04-04 first (import fence — the cheapest, grounds the others).**
   RED: test asserts `gzkit.commands.mx_cmd.airlock_enter is
   gzkit.airlock.enter.airlock_enter` and `mx_cmd.airlock_exit is
   gzkit.airlock.exit.airlock_exit`, and that `mx_cmd` source declares no local
   `def airlock_enter`/`def airlock_exit`. GREEN: add the two top-level imports
   plus their usage (steps 2–3) in the same edit (post-edit ruff strips unused
   imports — imports + usage land together).

2. **REQ-04-01 — `mx_enter_cmd` calls airlock-IN, diagnostic-only.**
   RED: test drives `mx_enter_cmd` across TWO distinct `--reason` values with an
   injected/fake `airlock_enter` (records calls) and a temp brief; asserts (a)
   the airlock-IN call is made on both reasons (gate fires regardless of reason,
   BI-2), BEFORE the marker exists; and (b) a NO-GO (`Decision.HOLD`) is surfaced
   as a logged refusal (via `build_refusal`) and does NOT block the marker write /
   exit non-zero (diagnostic-only; fail-closing is the deferred frontier).
   GREEN: add `_run_mx_airlock_in_diagnostic(...)` that calls `airlock_enter`,
   books the `airlock_in` L2 event via the primitive's `ledger=` param, and prints
   the refusal on a non-PROCEED decision; call it from `mx_enter_cmd` before
   `marker.write(...)`. Brief-less DECLARE deferred: the helper resolves the mx
   scope to an artifact file when one resolves, else logs a deferral note and
   skips — both paths diagnostic-only, never blocking.

3. **REQ-04-02 — `mx_exit_cmd` calls airlock-OUT, additive to the hard gate.**
   RED: test drives `mx_exit_cmd` with an all-green injected `_run_guards` and a
   fake `airlock_exit`; asserts the airlock-OUT call fires at close AND that the
   existing hard guard-gate still runs and still gates (a red `_run_guards` still
   exits 3 and writes no `mx_session_closed`; airlock-OUT is additive, never a
   replacement). GREEN: add `_run_mx_airlock_out_diagnostic(...)` calling
   `airlock_exit` (books `airlock_out` L2), invoked in `mx_exit_cmd` after the
   guard-gate passes and before `_mx_session_closed_event` is appended.

4. **REQ-04-03 — corrective door, calibration deferred (both seams reach the
   SAME shared primitive).** RED: test asserts both call sites (enter AND exit)
   reach the shared primitive the pipeline door consumes, in diagnostic-only
   posture, and that `mx_cmd` defines no local weight/profile branch — dropping
   either call site OR forking a locally-weighted variant fails. Does NOT assert
   a ceremony-profile parameter (none exists; the corrective-vs-tight distinction
   is the deferred frontier). GREEN: satisfied by steps 2–3 (no new profile code).

5. **Docs (Heavy Gate 3).** Additive edits to `mx-enter.md` / `mx-exit.md`
   documenting the diagnostic airlock membrane. `mkdocs build --strict` clean.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_mx_door_airlock -v
uv run gz covers OBPI-0.33.0-04-airlock-mx-door --json
uv run mkdocs build --strict
```

## Notes — Step 6a disclosures (Plan-Before-Exploration)

**Destination-in-mind.** Before writing this plan I had already formed the
approach: mirror the pipeline door's diagnostic-only seam by importing the
primitive directly (since `pipeline_runtime.py` is Denied) and adding two small
log-don't-block helpers. This came from reading `check_airlock_in_gate` /
`_run_airlock_in_diagnostic` and confirming the mx door cannot reuse them across
the Denied boundary.

**Rejected alternatives.**
- *Resolve `--scope` to a real brief and compute a meaningful seam-map now* —
  REJECTED: that is "real-entry accounting," which the option-c reconcile
  (attestor g0, 2026-07-11) explicitly deferred to the calibration frontier.
  Adopting it would contradict booked canon (REQ-01 rewritten to diagnostic-only).
- *Reuse `check_airlock_in_gate` from `pipeline_runtime.py`* — REJECTED: that
  module is a Denied path; reuse would violate the brief scope and couple the mx
  door to the pipeline door's wiring.
- *Thread a ceremony-profile / corrective-weight parameter* — REJECTED: the
  delivered primitive exposes no such parameter; REQ-03 forbids asserting a
  parameter that does not yet exist. Corrective-weight is a named residual.
- *Lazy imports inside the helpers* — REJECTED in favor of top-level imports
  (Pythonic rule: top-level imports unless a cycle forces lazy; `mx_cmd` is a
  leaf command module with no cycle back to `gzkit.airlock.*`).
