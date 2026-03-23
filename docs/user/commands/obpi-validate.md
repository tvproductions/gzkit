# gz obpi validate

Validate OBPI brief(s) for completion readiness and scaffold detection.

---

## Usage

```bash
gz obpi validate <path-to-obpi-brief>
gz obpi validate --adr ADR-X.Y.Z
```

Single-file mode takes a filesystem path to one OBPI brief. Relative paths resolve from the current workspace root.

Batch mode (`--adr`) discovers and validates all OBPI briefs in the ADR package's `obpis/` directory.

---

## Runtime Behavior

### Scaffold Detection (all statuses)

For any brief regardless of status, the validator detects template placeholders left by `gz specify` or other scaffolding:

- `src/module/` in Allowed Paths
- `First constraint` or `Second constraint` in Requirements
- `Given/When/Then behavior criterion` in Acceptance Criteria

Scaffold detection warns that the brief was auto-generated but never authored.

### Completion Readiness (status: Completed)

For completed briefs the validator additionally fails closed on:

- missing or empty `Allowed Paths`
- changed files outside the OBPI allowlist
- missing or placeholder `Implementation Summary`
- missing or placeholder `Key Proof`
- missing git-sync readiness prerequisites
- missing heavy/foundation human-attestation evidence

Text mode prints `BLOCKERS:` followed by one blocker per line and exits `1` when validation fails. Passing validation exits `0`.

---

## Options

| Option | Description |
|--------|-------------|
| `<path>` | Path to a single OBPI brief file |
| `--adr ADR-X.Y.Z` | Validate all OBPI briefs under an ADR package |

---

## Examples

```bash
# Single brief
uv run gz obpi validate docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-01-hexagonal-skeleton.md

# All briefs under an ADR
uv run gz obpi validate --adr ADR-0.0.3
```

```text
PASS OBPI-0.0.3-01-hexagonal-skeleton.md
PASS OBPI-0.0.3-02-domain-extraction.md
FAIL OBPI-0.0.3-03-exception-hierarchy.md
  - 'Requirements (FAIL-CLOSED)' contains template placeholder 'First constraint'

1/3 briefs failed validation
```
