---
name: gz-arb
description: ARB (Agent Self-Reporting) middleware skill for wrapping QA steps, generating structured receipts, validating compliance, and filing issues with deterministic evidence. GovZero v6 skill.
compatibility: GovZero v6 framework; requires uv, opsdev CLI
metadata:
  skill-version: "1.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
  status: ACTIVE
  effective-date: "2026-01-19"
  tool-versions: "opsdev>=1.0.0"
opsdev_command: arb
invocation: uv run -m opsdev arb {subcommand} [--options]
---

# gz-arb (Agent Self-Reporting)

Wrap QA verification steps, generate JSON receipts, validate compliance, and file structured issues.

**Authoritative reference:** `.github/instructions/arb.instructions.md`

---

## Quick Start

Wrap a QA tool and generate a receipt:

```bash
# Run ruff and emit receipt
uv run -m opsdev arb ruff

# Run any command as a step receipt
uv run -m opsdev arb step --name unittest -- uv run -m unittest -q

# Validate recent receipts
uv run -m opsdev arb validate

# Summarize recurring advice
uv run -m opsdev arb advise
```

---

## When to Use

- **Debugging QA failures:** Wrap the step in ARB to get deterministic receipt artifacts
- **Auditing compliance:** Validate receipts against schema; track patterns over runs
- **Filing issues:** Use `--file-issue` to create GitHub issues with structured evidence
- **Analyzing QA trends:** Summarize advice from recent runs to identify systemic problems

---

## Procedure

### Step 1: Wrap a QA Step

Choose a tool (ruff, unittest, ty, coverage) or wrap a custom command:

```bash
# Wrap a built-in tool
uv run -m opsdev arb ruff
uv run -m opsdev arb ruff --fix

# Wrap a custom command
uv run -m opsdev arb step --name my_step -- python scripts/validate.py
```

ARB executes the command and emits a JSON receipt to `artifacts/receipts/`.

### Step 2: Review the Receipt (Optional)

Receipts are JSON files with full metadata, findings, and structured results:

```bash
# List recent receipts
ls -lrt artifacts/receipts/ | tail -5

# Inspect a receipt
cat artifacts/receipts/arb-ruff-2026-01-19T14-30-45Z.json | jq .
```

### Step 3: Validate Receipts (Optional)

Check that receipts conform to the ARB schema:

```bash
# Validate last 20 receipts
uv run -m opsdev arb validate

# Validate last N receipts
uv run -m opsdev arb validate --limit 10

# Stop on first validation error
uv run -m opsdev arb validate --strict
```

### Step 4: Analyze Patterns (Optional)

Summarize recurring advice from recent runs:

```bash
# Summarize advice from all recent runs
uv run -m opsdev arb advise

# Filter by category (lint, test, type, coverage)
uv run -m opsdev arb advise --category lint

# Show top N recurring items
uv run -m opsdev arb advise --limit 10
```

### Step 5: File an Issue (Optional, Opt-In)

Create a GitHub issue from a failing ARB run:

```bash
# Run ruff and file an issue if it fails
uv run -m opsdev arb ruff --file-issue

# Custom command with issue filing
uv run -m opsdev arb step --name mytest -- python test.py --file-issue
```

**Result:** GitHub issue with:

- **Title:** `ARB: {tool} failures ({count} items)`
- **Labels:** `arb:auto-filed`
- **Body:** Structured receipt data + context

---

## Common Workflows

### Workflow A: Single-Step Audit

Run a QA step once and get a receipt:

```bash
uv run -m opsdev arb ruff
uv run -m opsdev arb validate --limit 1
```

### Workflow B: Multi-Step Audit

Wrap multiple steps and validate all receipts:

```bash
uv run -m opsdev arb ruff
uv run -m opsdev arb step --name unittest -- uv run -m unittest -q
uv run -m opsdev arb ty check . --exclude 'features/**'

# Validate all three
uv run -m opsdev arb validate --limit 3
```

### Workflow C: Recurring Pattern Detection

Summarize advice from all recent runs to identify systemic problems:

```bash
# Run QA steps across multiple sessions/days
uv run -m opsdev arb ruff
uv run -m opsdev arb ruff  # next day
uv run -m opsdev arb ruff  # next day

# Analyze patterns
uv run -m opsdev arb advise --category lint --limit 20
```

Result: Identify top recurring violations (e.g., "Line length exceeds limit in 12 files").

### Workflow D: File Issues from Failing QA

Run QA steps and file GitHub issues for failures:

```bash
uv run -m opsdev arb ruff --file-issue
uv run -m opsdev arb step --name myvalidation -- python scripts/validate.py --file-issue
```

**Note:** Issues are filed only if the wrapped command exits with non-zero status.

---

## Receipt Anatomy

Each receipt is a JSON file containing:

```json
{
  "metadata": {
    "version": "airlineops.arb.lint_receipt.v1",
    "timestamp": "2026-01-19T14:30:45Z",
    "run_id": "abc123def456",
    "tool": "ruff",
    "duration_ms": 2345
  },
  "command": {
    "executable": "ruff",
    "args": ["check", "."],
    "cwd": "/Users/jeff/Documents/Code/airlineops"
  },
  "result": {
    "exit_code": 1,
    "status": "FAILURE",
    "stderr": "...",
    "stdout": "..."
  },
  "findings": [
    {
      "file": "src/module.py",
      "line": 42,
      "rule": "E501",
      "severity": "warning",
      "message": "Line too long"
    }
  ]
}
```

All receipts are schema-validated on creation.

---

## Configuration

ARB receipt paths are configured via the artifacts registry (`config/artifacts.json`).

### Supabase Sync (Optional)

For cross-machine receipt synchronization, configure Supabase in `config/settings.local.json`:

```json
{
  "supabase": {
    "enabled": true,
    "postgres_dsn": "postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
  }
}
```

**Setup steps:**

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the table schema: `config/schemas/arb_receipts.sql` in Supabase SQL Editor
3. Get connection string from Settings → Database → Connection string (URI)
4. Add to `config/settings.local.json` (gitignored, safe for credentials)
5. Test: `uv run -m opsdev arb ruff` — receipt should sync

**Note:** Supabase sync is opt-in. Without configuration, receipts are written locally only.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "ARB: command not found" | opsdev CLI too old | `uv sync --all-groups --frozen` |
| "Receipt validation failed" | Schema mismatch | Check receipt JSON against `data/schemas/arb_lint_receipt.schema.json` |
| "Issue filing failed" | GitHub token missing | Check `gh auth token` or set `GITHUB_TOKEN` env |
| "Supabase push failed" | Connection error | Verify `postgres_dsn` in `config/settings.local.json`; check Supabase dashboard |
| "arb_receipts table not found" | Table not created | Run `config/schemas/arb_receipts.sql` in Supabase SQL Editor |
| Receipts not syncing | Supabase disabled | Set `supabase.enabled: true` in `config/settings.local.json` |

---

## Exit Codes

- **0:** Step succeeded; receipt created
- **1:** Step failed (command exited with 1); receipt created with failure status
- **2:** ARB internal error (can't create receipt); check `artifacts/logs/arb/`

---

## References

- **Instructions:** `.github/instructions/arb.instructions.md`
- **Schema:** `data/schemas/arb_lint_receipt.schema.json`
- **Config:** `config/settings.local.json` → `supabase.*` (credentials)
- **Table Schema:** `config/schemas/arb_receipts.sql`
- **Receipts directory:** `artifacts/receipts/`
- **Logs:** `artifacts/logs/arb/`
