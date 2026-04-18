# gz gates

> **Deprecated:** `gz gates` is deprecated and will be removed in a future
> release. Use [`gz closeout`](closeout.md) instead, which runs gates as part
> of the closeout pipeline.

Run applicable gates for the current lane and record results in the ledger.

---

## Usage

```bash
gz gates [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--gate` | integer | Run a specific gate (1-5) |
| `--adr` | string | ADR identifier to associate gate results with |

---

## What It Does

1. Resolves the target ADR (uses `--adr` or the single pending ADR)
2. Runs the gates required for the current lane
3. Appends a `gate_checked` event for each gate that runs
4. Exits non-zero if any required gate fails

Gate commands use `.gzkit/manifest.json` when available:

- Gate 2 (TDD): `verification.test`
- Gate 3 (Docs): `verification.docs` or `uv run mkdocs build --strict`
- Gate 4 (BDD): `verification.bdd` or `uv run -m behave features/`

For heavy-lane ADRs, Gate 4 is required and must pass before attestation.

### Gate 1 — ADR existence and frontmatter coherence

Gate 1 performs two checks:

1. Resolves the target ADR file on disk (ADR must exist under
   `docs/design/adr/`).
2. Validates frontmatter-ledger coherence across the four governed fields
   (`id`, `parent`, `lane`, `status`) via the same check surfaced by
   `gz validate --frontmatter`. Drift blocks Gate 1 with **exit code 3**
   (policy breach) and the operator sees a per-field listing naming an
   executable recovery command.

Status drift additionally displays the canonical ledger term via
`STATUS_VOCAB_MAPPING`; unmapped frontmatter terms surface on a distinct
"unmapped" line rather than silently falling back.

Example drift-block output:

```text
❌ Gate 1 (ADR): FAIL (frontmatter drift)
    Field status in docs/design/adr/.../ADR-0.1.0-test.md:
      ledger='Pending' frontmatter='Completed'
      canonical ledger term: completed
      → run: gz chores run frontmatter-ledger-coherence
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All required gates passed |
| 1 | One or more gates failed for reasons other than policy breach |
| 3 | Policy breach (e.g., Gate 1 frontmatter drift) |

There is no `--skip-frontmatter` bypass flag. Resolve drift via
`gz chores run frontmatter-ledger-coherence`, `gz register-adrs --all`, or
`gz adr promote <ADR-ID> --lane <canonical-lane>` — see the per-field
recovery line in the drift-block output.

---

## Example

```bash
# Run all required gates for the current lane
gz gates

# Run a specific gate
gz gates --gate 2

# Run gates for a specific ADR
gz gates --adr ADR-0.2.0
```
