# gz obpi brief-drift

Reconcile an OBPI brief against current project state across the five drift
dimensions, and optionally write operator-attested amendments.

---

## NAME

`gz obpi brief-drift` — detect and (optionally) repair OBPI brief↔reality drift.

## SYNOPSIS

```bash
gz obpi brief-drift <OBPI-ID> [--apply] [--attestor "<name>"] [--dry-run] [--json]
```

`<OBPI-ID>` accepts the full canonical identifier or the short form
(`OBPI-0.0.37-06`). Resolution is ledger-first and follows rename chains via the
shared OBPI-id resolver.

## DESCRIPTION

`gz obpi brief-drift` is the operator-runnable surface over the OBPI-0.0.37-05
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
`Validated`, `Superseded`, `archived`, `Promoted`, `Abandoned`, or `Withdrawn`
(matched case-insensitively) — is a **sealed historical record**. Its Allowed Paths and
Discovery Checklist described the tree at implementation time, so resolving them
against a codebase that has since renamed or absorbed those files asks a question
the brief never claimed to answer.

Every delta is still computed and rendered for such a brief — the archaeology is
real and stays visible — but `has_drift` is always **false**, so the run exits
**0** and the emitted receipt does not block the Stage-1 pipeline gate. There is
no future work for that gate to hold, and the only `--apply` repair available
would rewrite a sealed governance artifact under an attestation no operator can
honestly give (GHI #707).

So `--apply` on a terminal brief is **refused**: it exits **3** (policy breach),
writes nothing to the brief, and records no ledger event. `--apply --dry-run`
is refused the same way, so the preview predicts the refusal the write would
hit (GHI #1115). Run the command without `--apply` to read the deltas.

Read the deltas on a terminal brief as *"here is what moved since this shipped"*,
never as *"here is what you must fix"*. Drift that gates is drift on a live brief.

The engine is consumed read-only; this command owns the CLI surface, ledger
emission, and the amendment-write path only.

## OPTIONS

- `--apply` — write operator-attested amendments back into the brief. Allowlist
  additions go to frontmatter `allowlist:` on a structured brief and under
  `## Allowed Paths` on a legacy one (GHI #825); unresolved-verb references are
  recorded under `## Tracked Defects` (never silently rewritten — that is an
  operator-judgment call); REQ identity drift is recorded as a tracked-defect note.
  **Requires `--attestor`.**
- `--attestor "<name>"` — attestor handle, never a real name. Required with
  `--apply`; Defaults to `authorship.attestor_handle` in `.gzkit.json` when set (GHI #1036). With neither, `--apply` fails with
  `--apply requires --attestor`.
- `--dry-run` — write nothing to the brief. With `--apply` it previews the
  amendment: every line `--apply` would add or remove, taken from the same
  function that performs the write, so the preview and the write cannot
  disagree (GHI #1116). It still records a `brief_reconciled` event with
  `applied` false.
- `--json` — ## EXAMPLES

Output below is from a live (`Active`) brief whose allowlist names a file that
does not exist and whose verification block names an unknown `gz` verb. Every
run shown exits 3 because the drift remains. A terminal brief (for example,
`Completed`) reports `sealed` instead and exits 0, and `--apply` on it is
refused.

Report mode (exits 3 on drift):

```bash
uv run gz obpi brief-drift OBPI-0.1.0-02-drift
```

```text
Brief reconcile: OBPI-0.1.0-02-drift — DRIFT
  deltas: allowlist=1 discovery=0 verification=1 req_count=0 citation=0
```

Machine-readable output:

```bash
uv run gz obpi brief-drift OBPI-0.1.0-02-drift --json
```

```json
{
  "brief_id": "OBPI-0.1.0-02-drift",
  "has_drift": true,
  "deltas": {
    "allowlist": 1,
    "discovery": 0,
    "verification": 1,
    "req_count": 0,
    "citation": 0
  },
  "applied": false,
  "dry_run": false,
  "planned_amendments": null
}
```

Preview amendments without writing:

```bash
uv run gz obpi brief-drift OBPI-0.1.0-02-drift --apply --attestor g0 --dry-run
```

```text
Brief reconcile: OBPI-0.1.0-02-drift — DRIFT
  deltas: allowlist=1 discovery=0 verification=1 req_count=0 citation=0
Planned amendments (what --apply would write):
  + ## Tracked Defects
  + - Unresolved verb `gz totally-not-a-real-verb-xyz` (obpi brief-drift, attestor g0)
Dry run: no amendments written.
```

The same preview as JSON (`--apply --attestor g0 --dry-run --json`) carries it
line for line:

```json
  "planned_amendments": {
    "allowlist_additions": [],
    "tracked_defects": [
      "Unresolved verb `gz totally-not-a-real-verb-xyz` (obpi brief-drift, attestor g0)"
    ],
    "added_lines": [
      "",
      "## Tracked Defects",
      "",
      "- Unresolved verb `gz totally-not-a-real-verb-xyz` (obpi brief-drift, attestor g0)"
    ],
    "removed_lines": []
  }
```

Apply operator-attested amendments:

```bash
uv run gz obpi brief-drift OBPI-0.1.0-02-drift --apply --attestor g0
```

 "citation": 0
  },
  "applied": false,
  "dry_run": false
}
```

Preview amendments without writing:

```bash
uv run gz obpi brief-drift OBPI-0.0.37-06-brief-reconcile-cli --apply --attestor g0 --dry-run
```

Apply operator-attested amendments:

```bash
uv run gz obpi brief-drift OBPI-0.0.37-06-brief-reconcile-cli --apply --attestor g0
```

## SEE ALSO

- `gz obpi sync` — reconciles OBPI *runtime state* against ledger evidence
  (distinct from this command's brief-*content* reconciliation).
- ADR-0.0.37 — Constitutional Invariant Composition (invariant CIC-2:
  brief↔reality coherence).
