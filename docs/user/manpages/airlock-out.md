# gz airlock out

Operator surface over the airlock-OUT membrane primitive (ADR-0.33.0).

---

## Overview

`gz airlock out` runs the airlock-OUT exit membrane for a completed transit's
target OBPI — co-equal with `gz airlock in` ("same shape both ways"). Where
airlock-IN gates ENTRY, airlock-OUT accounts for what the transit DISTURBED on
the way out: **DRIFT-DIFF** (push-minus-pull over the two-graph) -> **FINDINGS +
RECOMMENDATIONS** -> a closed **DECISION MENU** (`leave_it_be | modify | repair |
adjust_maps`) -> **FRESH-TRANSIT ROUTING** for any discovered correction -> **log
to L2**.

The drift-diff is the symmetric difference of two edge veins: **FACT** edges
(`OBSERVED` provenance, from the ontology reach) and **INTENT** edges (`LAW`
provenance, from the declared parent-ADR invariants). A FACT edge with no
matching INTENT edge is a *"you wrecked something"* finding (you touched what you
never declared); an INTENT edge with no matching FACT edge is a *"broken
contract"* finding (you declared what you never delivered).

### Diagnostic-only tracer contract

`gz airlock out` is **not fail-closed at the CLI**. Surfaced drift prints
findings but the verb still **exits 0** — it reports, it never hard-blocks. This
is co-equal with the Stage-1 airlock-IN seam and mirrors the pipeline Stage-5
exit call site (parent ADR § Consequences Negative #5). The only non-zero exit
is a user error: an unresolvable target brief exits 1.

For a real leaf OBPI target the ontology sonar returns no transitive dependents
and no parent invariants are supplied, so the two-graph FACT layer is empty, the
drift-diff is `clean`, and no findings surface. That is the tracer's documented
calibration frontier, not a defect.

A discovered correction is ROUTED as a FRESH transit through the right door
(`pipeline | mx | permitted-entry`) — never smuggled inline into the current
sortie (parent ADR § Boundary Invariants #5). The airlock only ever writes L2 —
a booked `airlock_out` event — and NEVER L1 canon: a canon-relevant finding is
returned as a **proposal** for governed attestation, never a write (parent ADR
§ Boundary Invariants #1). In `--dry-run` no event is booked.

---

## Usage

```
gz airlock out --target OBPI [--dry-run] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--target OBPI` | Target OBPI id to exit-account (required). |
| `--dry-run` | Run the drift-diff without booking an `airlock_out` event. |
| `--json` | Emit a machine-readable exit-report payload. |

---

## Example

```bash
uv run gz airlock out --target OBPI-0.33.0-01 --dry-run
```

Observed output:

```
airlock out (dry-run) — OBPI-0.33.0-01
  verdict: clean
  decision menu: leave_it_be, modify, repair, adjust_maps
```

Machine-readable form:

```bash
uv run gz airlock out --target OBPI-0.33.0-01 --json
```

```json
{
  "target": "OBPI-0.33.0-01",
  "verdict": "clean",
  "decision_menu": [
    "leave_it_be",
    "modify",
    "repair",
    "adjust_maps"
  ],
  "drift": [],
  "findings": [],
  "routing": [],
  "proposals": []
}
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Drift-diff ran — verdict reported (`clean` **or** surfaced findings). |
| 1 | User error — no OBPI brief could be resolved for `--target`. |
