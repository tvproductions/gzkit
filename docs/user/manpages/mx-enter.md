# gz mx enter

Open the Maintenance Hangar (MX mode).

## Usage

<!-- gz-validate-skip: command-shape -->
```bash
gz mx enter --reason REASON --attestor ATTESTOR [--scope ADR_OR_OBPI ...] [--mode {mx,safe}] [--contract PATH]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--reason REASON` | Reason for entering MX mode (required; must be non-empty) |
| `--attestor ATTESTOR` | Operator identity (required; never an agent — only operators may open the hangar) |
| `--scope ADR_OR_OBPI ...` | ADRs/OBPIs under inspection (optional; 0 or more) |
| `--mode {mx,safe}` | `mx` (default): the Maintenance Hangar, most guards demote to advisory. `safe`: safe mode, the martial-law toggle (GHI #1244): OBPI initiation and brief ceremony are suspended under the contract, every guard runs at full strength |
| `--contract PATH` | Project-relative path of the safe-mode contract, the document that says what the mode suspends and what still binds. Required with `--mode safe`; refused with `--mode mx` |

## Runtime Behavior

- Validates that `--reason` and `--attestor` are non-empty; fails closed (exit 1) if either is empty
  or whitespace-only — no marker is written, no ledger event is emitted.
- Checks the hangar is not already open (`marker.is_active`). Fails closed (exit 1) if it is.
- Acquires a session lock on the `lock_manager` token rail (`mx-session` key) to serialize
  concurrent entry attempts (ADR-0.0.74 Decision #4 — token-rail/lock_manager).
- Fires the airlock-IN membrane **before** writing the hangar marker (ADR-0.33.0 — the mx door
  crosses the SAME airlock the pipeline door does). The gate fires on **every** entry regardless
  of `--reason` (the reason selects ceremony weight, never whether the gate fires) and books one
  `airlock_in` L2 event. It is **diagnostic-only** at this tracer increment: a NO-GO is surfaced
  as a refusal naming the un-accounted seam — it does **not** block the marker write. Fail-closing
  and real-entry seam accounting (the corrective ceremony weight, brief-less scopes) are the
  attested deferred calibration frontier.
- Resolves the mode. `--mode safe` requires `--contract` naming a readable file inside the
  project and fails closed (exit 1) without one; `--mode mx` refuses `--contract`. Under
  safe mode `gzkit.mx.checkpoint` demotes no guard: the marker suspends ceremony, not
  enforcement, and the awareness banner names the contract every turn.
- Writes the marker file (`.gzkit/mx.json`) with `session_id`, `opened_at`, `reason`,
  `attestor`, `inspection_scope`, `mode`, and `contract`.
- Writes one `mx_session_opened` ledger event carrying the same fields, binding the marker to
  the ledger (anti-contrivance: a hand-created marker with no matching ledger event is void).
- Emits a success message with `session_id` and `attestor`.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Hangar opened successfully |
| 1 | Validation failure: empty input, hangar already active, or concurrent entry |
| 2 | System/IO error |
| 3 | Policy breach |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# Open the hangar for ADR-0.0.74 repair work
gz mx enter --reason "re-true ledger-proof locks under ADR-0.0.74" --attestor g0

# Open with explicit inspection scope
gz mx enter --reason "repair marker binding" --attestor g0 --scope ADR-0.0.74 OBPI-0.0.74-04

# Multiple scope items
gz mx enter --reason "broad repair" --attestor g0 --scope ADR-0.0.74 ADR-0.0.73 OBPI-0.0.74-02

# Safe mode, the martial-law toggle, under a written contract
gz mx enter --mode safe --contract docs/governance/harbor-pilotage-candidate-2026-10-15.md --reason "harbor pilotage" --attestor g0
```

## Related

- [`gz mx`](mx.md) — MX mode command group overview
- ADR-0.0.74: MX Mode — Maintenance Hangar (design and decision record)
