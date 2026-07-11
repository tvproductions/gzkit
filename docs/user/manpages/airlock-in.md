# gz airlock in

Operator surface over the airlock-IN membrane primitive (ADR-0.33.0).

---

## Overview

`gz airlock in` runs the airlock-IN three-beat preflight gate for a target
OBPI: **DECLARE** (read the target brief's declared intent + Allowed Paths) ->
**PING** (image the target's blast-radius via the read-only ontology sonar) ->
**RECONCILE** (measure the observed reach and declared parent invariants against
what the brief names) -> **decide** (`proceed | pause | hold | revert`).

The report carries the two-layer seam-map counts: `bodies` (the brief's declared
`## Allowed Paths` — seam-as-BODY), `push` (observed reach edges), `pull`
(declared parent-ADR invariants), and `unaccounted` (real push/pull edges the
brief text never names).

### Diagnostic-only tracer contract

`gz airlock in` is **not fail-closed at the CLI**. A NO-GO (any un-accounted
seam) prints a `build_refusal` diagnostic but the verb still **exits 0** — it
reports, it never hard-blocks. This mirrors the pipeline call site, which was
deliberately downgraded from `SystemExit(3)` to a warning (parent ADR
§ Consequences Negative #5). The only non-zero exit is a user error: an
unresolvable target brief exits 1.

For a real leaf OBPI target the ontology sonar returns no transitive dependents
and no parent invariants are supplied, so the seam-map push/pull layers are
empty and the decision is `proceed`. That is the tracer's documented calibration
frontier, not a defect.

The airlock only ever writes L2 — a booked `airlock_in` event — and never L1
canon; its verdict is never a Gate-5 completion attestation (parent ADR
§ Boundary Invariants #1, #3). In `--dry-run` no event is booked.

---

## Usage

```
gz airlock in --target OBPI [--phase PHASE] [--dry-run] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--target OBPI` | Target OBPI id to preflight (required). |
| `--phase PHASE` | Optional pipeline phase label (e.g. `build`). |
| `--dry-run` | Run the preflight without booking an `airlock_in` event. |
| `--json` | Emit a machine-readable preflight payload. |

---

## Example

```bash
uv run gz airlock in --target OBPI-0.33.0-01 --phase build --dry-run
```

Observed output:

```
airlock in (dry-run) — OBPI-0.33.0-01 @ build
  decision: proceed
  seams: bodies=12 push=0 pull=0 unaccounted=0
```

Machine-readable form:

```bash
uv run gz airlock in --target OBPI-0.33.0-01 --json
```

```json
{
  "target": "OBPI-0.33.0-01",
  "phase": null,
  "decision": "proceed",
  "authority": "captain",
  "blast_radius": 0,
  "seam_map": {
    "bodies": 12,
    "push": 0,
    "pull": 0,
    "unaccounted": 0
  },
  "unaccounted": []
}
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Preflight ran — decision reported (PROCEED **or** a diagnostic NO-GO). |
| 1 | User error — no OBPI brief could be resolved for `--target`. |
