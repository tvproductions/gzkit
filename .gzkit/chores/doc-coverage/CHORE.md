# CHORE: Documentation Cross-Coverage Enforcement

**Version:** 1.0.0
**Lane:** Heavy
**Slug:** `doc-coverage`
**Frequency:** per-release

---

## Overview

Run the AST-driven documentation scanner against the documentation manifest
and produce an actionable gap report. Fails closed when any required
documentation surface is missing for a CLI command.

## Policy and Guardrails

- **Lane:** Heavy — changes operator-visible chore catalog
- The chore runner loads the manifest (`config/doc-coverage.json`) and invokes
  the scanner (`src/gzkit/doc_coverage/scanner.py`) — it does not duplicate logic
- The gap report lists every required surface that is missing, plus undeclared
  commands and orphaned documentation
- Exit 0 = all required surfaces present; exit 1 = gaps found

## Workflow

### 1. Run the chore

```bash
uv run gz chores run doc-coverage
```

### 2. Review gaps

If the chore fails, review the gap report. Each gap lists the command,
missing surface, and expected path.

For a detailed human-readable report:

```bash
uv run -m gzkit.doc_coverage.runner
```

For machine-readable JSON:

```bash
uv run -m gzkit.doc_coverage.runner --json
```

### 3. Fix gaps

Create the missing documentation surfaces (manpages, index entries,
runbook references, docstrings, COMMAND_DOCS mappings).

### 4. Re-validate

```bash
uv run gz chores run doc-coverage
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m gzkit.doc_coverage.runner` | 0 |

## Evidence Commands

```bash
uv run -m gzkit.doc_coverage.runner > ops/chores/doc-coverage/proofs/gap-report.txt
uv run -m gzkit.doc_coverage.runner --json > ops/chores/doc-coverage/proofs/gap-report.json
```

---

**End of CHORE: Documentation Cross-Coverage Enforcement**
