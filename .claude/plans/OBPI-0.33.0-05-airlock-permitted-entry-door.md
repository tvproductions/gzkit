# Plan: OBPI-0.33.0-05 — Airlock Permitted-Entry Door

**OBPI:** OBPI-0.33.0-05-airlock-permitted-entry-door
**Parent ADR:** ADR-0.33.0-airlock-membrane (feature / heavy)
**Lane:** Heavy (net-new operator CLI verb `permitted-entry` = runtime contract surface)

## Context

The third airlock door. The pipeline door (OBPI-02/03) and the mx door (OBPI-04)
already CONSUME the shared `gzkit.airlock.enter.airlock_enter` /
`gzkit.airlock.exit.airlock_exit` primitive as diagnostic-only tracers. This OBPI
adds the `permitted-entry` verb for the ad-hoc/spurious entry — reconnaissance for
comprehension, light repair at most — closing the silent-bypass hole (parent ADR
Consequences #2): an ad-hoc entry that formerly crossed NO membrane now crosses the
airlock and leaves an `airlock_in`/`airlock_out` L2 record.

Parent ADR § Intent contract (the three-doors line this OBPI implements):
> "Three entry-reasons, three doors: pipeline (design implementation — intentional
> change), mx/ghi (defect repair — correction to a desired state), and
> permitted-entry (ad-hoc/spurious — reconnaissance for comprehension with light
> repair at most, bracketing action: upstream of planning and downstream of action)."

Parent ADR § Decision ceremony line:
> "ceremony scales by door (pipeline tight; mx corrective; permitted-entry
> permissive), calibrated to the pipeline."

Fail-closed anchors: BI-2 (gate fires on every entry; the reason/door selects
ceremony weight, never *whether* the gate fires — "a gate with a hole is not a
gate"); BI-3 (one extracted primitive; never fork); BI-5 (discovered correction
routes as a fresh transit).

### Design (destination-in-mind, Step 6a disclosure)

**Conclusion formed before authoring:** mirror the mx-door tracer pattern
(`src/gzkit/commands/mx_cmd.py`) — a thin adapter that CALLS the shared primitive
diagnostic-only, books L2, surfaces a NO-GO as a diagnostic refusal (never a block).
The one departure the mx door does NOT need: mx defers when no brief-bearing scope
resolves, but REQ-01 forbids that skip for permitted-entry (the gate must ALWAYS
fire). Resolution: the door **always synthesizes a minimal DECLARE** (a temp brief
naming `--target` as the sole declared Allowed Path + the repair intent text) when
`--target` does not resolve to an on-disk ADR/OBPI artifact — so `airlock_enter` /
`airlock_exit` are ALWAYS invoked. The seam-map is minimal (production reach empty =
the deferred calibration frontier); tests inject a `reach_fn` to exercise the NO-GO
path.

**Light-repair ceiling (REQ-03/04):** the door's OWN logic layered atop the shared
primitive. `classify_repair(repair: str | None) -> RepairScope` returns
`NONE` (recon-only) | `LIGHT` (within ceiling — crosses inline) | `BEYOND` (exceeds
ceiling — trips a fresh transit). Beyond-ceiling is a heuristic tripwire keyed on
structural-work verbs (refactor / redesign / rewrite / migrate / schema); it is
diagnostic (recommends, refuses inline execution) — never a hard block on operator
judgment, consistent with the diagnostic-only door posture. `route_door(repair) ->
Door` routes defect-repair language → `Door.MX`, otherwise intentional change →
`Door.PIPELINE`. Both `Door` and `FreshTransit` are REUSED from
`gzkit.airlock.exit` (never forked — BI-3).

**Rejected alternatives (Step 6a disclosure):**
- *Defer the gate when brief-less* (mirror mx exactly) — REJECTED: violates REQ-01
  (the gate would not always fire). The synthetic-DECLARE realization is what makes
  "gate always fires" true now.
- *A ceremony-profile parameter on the shared primitive (permissive vs tight)* —
  REJECTED: the delivered primitive exposes no such parameter; per-door ceremony
  WEIGHT calibration is the attested deferred frontier (parent ADR Objective NOTE).
  This door wires the diagnostic-only tracer at permissive intent; the weight
  distinction is a NAMED RESIDUAL, never asserted as already-built.
- *Fork a private enter/exit/gate for the permissive door* — REJECTED by BI-3 (one
  extracted primitive the doors CALL, never fork).
- *Semantic NLP classification of repair intent* — REJECTED: stochastic; the ceiling
  is an explicit, documented keyword tripwire, framed as a heuristic, diagnostic-only.

## Files

| Path | Action | Purpose |
|------|--------|---------|
| `src/gzkit/commands/permitted_entry.py` | CREATE | The `permitted-entry` handler: synthesize/resolve DECLARE, CALL shared `airlock_enter`/`airlock_exit` diagnostic-only, classify repair scope, trip fresh transit beyond ceiling |
| `src/gzkit/cli/parser_governance.py` | EDIT (additive) | Register the `permitted-entry` verb + `--target`/`--recon`/`--repair`/`--dry-run` args + `_permitted_entry_dispatch` lazy-import (mirrors `gz mx` registration ~L758–843) |
| `tests/test_permitted_entry.py` | CREATE | `@covers`-decorated REQ tests for all 6 door behaviors |
| `docs/user/manpages/permitted-entry.md` | CREATE | Command manpage (Gate 3 docs; contract + EXAMPLES with real CLI output) |

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **REQ-05 (no private fork) + skeleton** — create `permitted_entry.py` importing the
   shared `airlock_enter`/`airlock_exit`/`Door`/`FreshTransit`. RED: test asserts the
   handler routes through the shared primitives (patch `airlock_enter`/`airlock_exit`,
   observe the call) and that the module defines no parallel enter/exit/gate/SeamMap.
2. **REQ-01 (gate always fires)** — the door ALWAYS synthesizes/resolves a DECLARE and
   CALLS `airlock_enter`. RED: test drives a bare `--recon` entry, asserts a gate
   decision is produced (primitive invoked) and no exit path skips it.
3. **REQ-02 (recon default, no mutation)** — RED: recon-only invocation completes with
   NO file mutation and a non-empty seam/comprehension report.
4. **REQ-03 (light-repair ceiling)** — RED: a within-ceiling light repair is accepted
   and crosses; a beyond-ceiling intent is REFUSED for inline execution (enforced, not
   advisory).
5. **REQ-04 (trip to fresh transit)** — RED: a beyond-ceiling intent emits a
   `FreshTransit` naming the routed door (pipeline for intentional change / mx for
   defect repair) and performs NO inline mutation.
6. **REQ-06 (silent-bypass closure)** — RED: the ad-hoc entry path books an
   `airlock_in` (and on exit `airlock_out`) L2 ledger event — the previously
   membrane-less surface now leaves an accountable transit record.
7. **CLI registration** — add the `permitted-entry` verb to `parser_governance.py`
   (additive; mirrors `gz mx`). Smoke-verify `gz permitted-entry --help` exit 0.
8. **Manpage** — author `docs/user/manpages/permitted-entry.md` with real CLI-output
   EXAMPLES harvested from the four Demo invocations.
9. **REQ-07 [STRUCTURAL-FENCE] (never a completion attestation)** — proven by the parent
   ADR `## Boundary Invariants` #3 anchor, audited at ADR closeout; NO `@covers` test
   (ADR-0.0.59 proof channel). The door books `airlock_in`/`airlock_out` L2 events only,
   never a completion-attestation event — reinforced structurally by REQ-06's event-type
   assertion.

## Verification

```bash
uv run gz validate --documents
uv run gz obpi validate --adr ADR-0.33.0-airlock-membrane --authored
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --qc-binding
uv run -m unittest tests.test_permitted_entry -v
uv run gz covers OBPI-0.33.0-05-airlock-permitted-entry-door --json
uv run mkdocs build --strict
```

## Notes

- REQ-01..06 are `[BEHAVIOR]` → `@covers` test proof channel; REQ-07 is
  `[STRUCTURAL-FENCE]` → parent-ADR `## Boundary Invariants` #3 anchor (no `@covers`
  test). The brief declares `req_atomic:` for all seven, so no TASK subdivision is
  required (Stage 5 task-envelope gate satisfied).
- REQ-count drift RESOLVED (operator-ratified 2026-07-11): the former 7-declared-vs-6-
  acceptance drift is fixed by adding REQ-07 [STRUCTURAL-FENCE], restoring the 1:1
  requirements↔acceptance convention held by sibling OBPI-02/03/04. Brief reconcile now
  reports `req_count=0`.
- Production `reach_fn` stays empty (deferred calibration frontier); the seam-map is
  minimal-but-real. Diagnostic-only: a NO-GO logs `build_refusal`, never `SystemExit`.
- No new runtime dependency; the door stands on the already-attested airlock primitive.
