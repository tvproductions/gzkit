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
clean, **3** when drift is detected. This is unconditional — `--apply` does not
suppress it. `--apply` writes its amendments, re-measures the brief as amended,
and reports that second measurement in the ledger receipt, the rendered deltas,
and the exit code. So `--apply` exits **0** only when the amendment actually
cleared every dimension, and **3** when drift survives it — `--apply` repairs
the allowlist dimension alone, and unresolved verbs, discovery paths, and stale
citations are recorded rather than repaired (GHI #677).

### Terminal-status briefs report but never gate

A brief whose `status:` is terminal — `Completed`, `attested_completed`,
`Validated`, `Superseded`, `archived`, or `Promoted` (matched
case-insensitively) — is a **sealed historical record**. Its Allowed Paths and
Discovery Checklist described the tree at implementation time, so resolving them
against a codebase that has since renamed or absorbed those files asks a question
the brief never claimed to answer.

Every delta is still computed and rendered for such a brief — the archaeology is
real and stays visible — but `has_drift` is always **false**, so the run exits
**0** and the emitted receipt does not block the Stage-1 pipeline gate. There is
no future work for that gate to hold, and the only `--apply` repair available
would rewrite a sealed governance artifact under an attestation no operator can
honestly give (GHI #707).

Read the deltas on a terminal brief as *"here is what moved since this shipped"*,
never as *"here is what you must fix"*. Drift that gates is drift on a live brief.

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
