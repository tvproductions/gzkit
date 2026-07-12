# gz permitted-entry

The airlock's third door — the ad-hoc/spurious entry: reconnaissance for
comprehension with light repair at most.

## Synopsis

<!-- gz-validate-skip: command-shape -->
```bash
gz permitted-entry --target TARGET [--recon] [--repair INTENT] [--dry-run]
```

## Description

`gz permitted-entry` crosses the airlock membrane for an ad-hoc entry that is
neither a planned pipeline implementation nor an mx/ghi defect repair — a
reconnaissance for comprehension, with light repair at most. It CONSUMES the
shared airlock primitive (`gzkit.airlock.enter.airlock_enter` /
`gzkit.airlock.exit.airlock_exit`), never forking a private variant
(ADR-0.33.0 Boundary Invariant #3), and closes the silent-bypass hole: an ad-hoc
entry that formerly crossed no membrane now leaves an `airlock_in` / `airlock_out`
L2 encounter record.

**The acknowledge-and-decide gate fires on EVERY transit.** The reason and door
select the ceremony *weight* (this door is permissive — the lightest profile),
never *whether* the gate fires (ADR-0.33.0 Boundary Invariant #2 — "a gate with a
hole is not a gate"). The gate is diagnostic-only at this door: a NO-GO is
surfaced (naming the un-accounted seam and a one-command re-sense), never a hard
block. The gate is an acknowledge-and-decide input, NEVER a Gate-5 completion
attestation — the sacred word stays reserved (Boundary Invariant #3).

**Reconnaissance is the default; light repair is the ceiling, not the default.**
The door never performs a repair itself — it is a membrane, not an editor. A
within-ceiling light-repair intent is *admitted* (it crosses the gate, logged); an
intent *beyond* the light-repair ceiling is REFUSED for inline execution and
trips a **fresh transit** through the pipeline door (intentional change) or the
mx door (defect repair) — the discovered correction is routed, never smuggled
into the reconnaissance (Boundary Invariant #5).

## Options

| Flag | Description |
|------|-------------|
| `--target TARGET` | The file or region the ad-hoc entry reconnoiters (required) |
| `--recon` | Reconnaissance-only (the default posture): inspect for comprehension, no change |
| `--repair INTENT` | A light-repair intent (at most); an intent beyond the ceiling trips a fresh transit |
| `--dry-run` | Preview the transit (fire the gate) without booking the L2 encounter events |

`--recon` and `--repair` are **mutually exclusive** — reconnaissance-only and a
repair intent are contradictory. Supplying both fails fast (the invocation is
rejected) rather than silently dropping the repair, so a beyond-ceiling repair can
never evade the ceiling and fresh-transit routing by adding `--recon`.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success — the transit crossed (the diagnostic gate never hard-blocks) |
| `1` | User/config error (e.g. missing `--target`) |

## Examples

### Reconnaissance-first (the default)

Enter to inspect a region for comprehension. The gate fires and yields a
seam/comprehension report; nothing is changed.

<!-- gz-validate-skip: command-shape -->
```bash
gz permitted-entry --target src/gzkit/quality.py --recon --dry-run
```

```text
permitted-entry recon: permitted-entry:src/gzkit/quality.py
  footprint (declared bodies): src/gzkit/quality.py
  push edges (reach): 0
  pull edges (invariants): 0
  un-accounted seams: 0
```

### Light repair (within the ceiling)

A one-line typo fix is under the light-repair ceiling — the intent is admitted
and crosses the gate.

<!-- gz-validate-skip: command-shape -->
```bash
gz permitted-entry --target README.md --repair "fix typo in badge line" --dry-run
```

```text
permitted-entry recon: permitted-entry:README.md
  footprint (declared bodies): README.md
  push edges (reach): 0
  pull edges (invariants): 0
  un-accounted seams: 0
permitted-entry: light repair admitted (within ceiling) — crosses the gate: fix typo in badge line
```

### Beyond the ceiling — trips a fresh transit

A structural change exceeds the light-repair ceiling. The door does not admit it
inline and presents **both** fresh-transit doors with their selection criteria —
`pipeline` for an intentional change, `mx` for a defect repair. The door does **not**
authoritatively guess the door: defect-vs-intentional cannot be reliably inferred
from free text, so the captain chooses. This satisfies the binding requirement —
route as a fresh transit, never smuggle inline — without a fragile heuristic that
would misroute some corrective phrasings.

<!-- gz-validate-skip: command-shape -->
```bash
gz permitted-entry --target src/gzkit/ledger.py --repair "refactor event schema" --dry-run
```

```text
permitted-entry recon: permitted-entry:src/gzkit/ledger.py
  footprint (declared bodies): src/gzkit/ledger.py
  push edges (reach): 0
  pull edges (invariants): 0
  un-accounted seams: 0
permitted-entry: intent exceeds the light-repair ceiling — not admitted inline (the door never edits). Route a fresh transit and choose the door — pipeline (intentional change) or mx (defect repair): refactor event schema
```

## Notes

- **Diagnostic-only calibration frontier.** The delivered primitive exposes no
  ceremony-profile parameter; per-door ceremony-weight calibration (permissive vs
  tight) and the brief-less DECLARE richness are the attested deferred frontier
  (ADR-0.33.0). The gate always *fires* now (the door always calls the primitive);
  the *weight* distinction matures with the frontier.
- **No new runtime dependency.** The door stands on the already-attested airlock
  primitive plus the declared target footprint.

## Related

- `gz mx` — the corrective-scoped door (defect repair).
- ADR-0.33.0-airlock-membrane — the airlock design and its Boundary Invariants.
