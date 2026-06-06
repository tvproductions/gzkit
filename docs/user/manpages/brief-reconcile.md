# gz brief reconcile

Reconcile an OBPI brief against current project state across the five drift
dimensions, and optionally write operator-attested amendments.

---

## NAME

`gz brief reconcile` — detect and (optionally) repair OBPI brief↔reality drift.

## SYNOPSIS

```bash
gz brief reconcile <OBPI-ID> [--apply] [--attestor "<name>"] [--dry-run] [--json]
```

`<OBPI-ID>` accepts the full canonical identifier or the short form
(`OBPI-0.0.37-06`). Resolution is ledger-first and follows rename chains via the
shared OBPI-id resolver.

## DESCRIPTION

`gz brief reconcile` is the operator-runnable surface over the OBPI-0.0.37-05
reconciliation engine (`reconcile_brief`). On every run it computes deltas across
five drift dimensions — **allowlist**, **discovery checklist**, **verification
verbs**, **REQ count**, and **citation tuples** — and emits a `brief_reconciled`
ledger event with the per-dimension counts. When any dimension drifts, it
additionally emits a `brief_reconcile_drift_detected` event carrying the full
per-dimension payload.

Exit code follows the `gz validate --*` convention: **0** when the brief is
clean, **3** when drift is detected (report mode). Under `--apply` the command
writes amendments and exits **0**.

The engine is consumed read-only; this command owns the CLI surface, ledger
emission, and the amendment-write path only.

## OPTIONS

- `--apply` — write operator-attested amendments back into the brief. Allowlist
  additions append under `## Allowed Paths`; unresolved-verb references are
  recorded under `## Tracked Defects` (never silently rewritten — that is an
  operator-judgment call); REQ-count drift is recorded as a tracked-defect note.
  **Requires `--attestor`.**
- `--attestor "<name>"` — full name of the attesting human. Required with
  `--apply`; without it, `--apply` fails with `--apply requires --attestor`.
- `--dry-run` — preview the would-be amendments without writing the brief or
  recording an applied event.
- `--json` — emit a machine-consumption payload (`brief_id`, `has_drift`,
  per-dimension `deltas`, `applied`, `dry_run`).

## EXAMPLES

Report mode (exits 3 on drift):

```bash
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli
```

```text
Brief reconcile: OBPI-0.0.37-06-brief-reconcile-cli — DRIFT
  deltas: allowlist=2 discovery=0 verification=0 req_count=-1 citation=0
```

Machine-readable output:

```bash
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli --json
```

```json
{
  "brief_id": "OBPI-0.0.37-06-brief-reconcile-cli",
  "has_drift": true,
  "deltas": {
    "allowlist": 2,
    "discovery": 0,
    "verification": 0,
    "req_count": -1,
    "citation": 0
  },
  "applied": false,
  "dry_run": false
}
```

Preview amendments without writing:

```bash
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli --apply --attestor "Jane Doe" --dry-run
```

Apply operator-attested amendments:

```bash
uv run gz brief reconcile OBPI-0.0.37-06-brief-reconcile-cli --apply --attestor "Jane Doe"
```

## SEE ALSO

- `gz obpi reconcile` — reconciles OBPI *runtime state* against ledger evidence
  (distinct from this command's brief-*content* reconciliation).
- ADR-0.0.37 — Constitutional Invariant Composition (invariant CIC-2:
  brief↔reality coherence).
