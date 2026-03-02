---
applyTo: "**/*"
---

# ARB (Agent Self-Reporting) Middleware

**Version:** 1.0
**Status:** Active
**Last reviewed:** 2026-01-19

ARB is a QA middleware layer that wraps real verification steps (lint, type check, tests, etc.) and emits structured JSON receipts for deterministic validation and governance auditing.

---

## Core Concept

ARB intercepts QA command execution and records:

- **Execution metadata** (timestamp, duration, environment)
- **Input/output** (command, arguments, exit code, stderr/stdout)
- **Structured findings** (linting violations, type errors, test failures)
- **Receipt artifacts** (JSON schema-validated, persistent)

This allows agents and humans to:

1. Validate QA step outcomes programmatically
2. Aggregate recurring patterns across runs
3. File issues with deterministic evidence
4. Audit compliance and enforcement

---

## When to Use ARB

**Use ARB when:**

- Debugging a failing QA step and you need a deterministic receipt artifact for validation
- Updating enforcement flows and you want receipts produced as part of the normal run
- Summarizing recurring advice from recent lint/test/coverage runs
- Filing issues with structured evidence (lint violations, test failures, etc.)
- Auditing QA compliance across an ADR or release cycle

**Do NOT use ARB for:**

- One-off interactive command execution (use the tool directly)
- Time-sensitive operations (ARB adds receipt overhead; ~5-10% slower)
- Steps where receipt artifacts would clutter the workspace unnecessarily

---

## Available Commands

### Wrap a QA Tool (Generic)

```bash
# Run ruff via ARB (emits a lint receipt)
uv run -m opsdev arb ruff

# Run ruff with auto-fix via ARB
uv run -m opsdev arb ruff --fix

# Wrap any command as a step receipt
uv run -m opsdev arb step --name unittest -- uv run -m unittest -q

# Run type check via ARB
uv run -m opsdev arb ty check . --exclude 'features/**'

# Run coverage via ARB
uv run -m opsdev arb coverage run -m unittest discover -s tests -t .
```

### Validate & Analyze Receipts

```bash
# Validate recent receipts against JSON schemas (default: last 20 runs)
uv run -m opsdev arb validate

# Validate only the last N receipts
uv run -m opsdev arb validate --limit 50

# Summarize recurring advice from recent lint receipts
uv run -m opsdev arb advise

# Summarize advice from a specific category (lint, test, type, coverage)
uv run -m opsdev arb advise --category lint
```

### File Issues (Opt-In)

```bash
# File an issue from a failing ARB ruff run
uv run -m opsdev arb ruff --file-issue

# File an issue from a failing test run
uv run -m opsdev arb step --name unittest -- uv run -m unittest -q --file-issue
```

**Label:** Issues filed by ARB receive the `arb:auto-filed` label for easy tracking and filtering.

---

## Receipt Schema & Storage

### Schema Location

- **Authoritative schema:** `data/schemas/arb_lint_receipt.schema.json`
- **Schema ID:** `airlineops.arb.lint_receipt.v1`

### Receipt Storage

Receipts are persisted to `artifacts/receipts/` as JSON files with metadata:

```
artifacts/receipts/
  arb-ruff-2026-01-19T14-30-45Z.json
  arb-unittest-2026-01-19T14-31-20Z.json
  arb-tycheck-2026-01-19T14-32-05Z.json
```

Each receipt is timestamped and validated against the schema on creation.

### Cross-Machine Sync (Optional)

ARB receipts can be synced across development machines via Supabase Postgres integration:

- **Enabled in config:** `settings.json` → `supabase.arb_receipt_sync.enabled`
- **Docs:** See `.github/instructions/arb.instructions.md` § "Cross-Machine Sync"

---

## Workflow Examples

### Example 1: Debug a Failing Lint Run

You run `uv run ruff check .` and it fails. You want to examine violations programmatically:

```bash
# Run via ARB to generate a receipt
uv run -m opsdev arb ruff

# Validate the receipt
uv run -m opsdev arb validate --limit 1

# Summarize advice
uv run -m opsdev arb advise --category lint
```

The receipt shows exactly which files/lines violated which rules, with severity and context.

### Example 2: Wrap a Custom Step

You have a custom validation script that doesn't integrate with ARB natively:

```bash
# Wrap it as a generic step receipt
uv run -m opsdev arb step --name custom-validation -- python scripts/validate_custom.py

# Validate the step receipt
uv run -m opsdev arb validate --limit 1
```

### Example 3: File an Issue from a Failing Ruff Run

Ruff found violations that require discussion:

```bash
# Run ruff via ARB and auto-file an issue
uv run -m opsdev arb ruff --file-issue

# Result: GitHub issue created with title like "ARB: ruff violations (6 files, 12 lines)"
# Labels: [arb:auto-filed]
# Body: structured receipt data + recommended fixes
```

---

## Exit Codes & Error Handling

ARB preserves the exit code of the wrapped command:

- **Exit 0:** Command succeeded; receipt created successfully
- **Exit 1:** Command failed (e.g., ruff found violations, tests failed); receipt created with error/warning status
- **Exit 2:** ARB internal error (receipt creation failed); check logs in `artifacts/logs/arb/`

---

## Configuration

ARB behavior is controlled via `config/settings.json`:

```json
{
  "arb": {
    "enabled": true,
    "receipt_store": "artifacts/receipts",
    "schema_validate_on_write": true,
    "supabase": {
      "enabled": false,
      "api_url": "...",
      "api_key": "..."
    }
  }
}
```

---

## Limitations & Caveats

1. **Receipt overhead:** ARB adds ~5-10% runtime; not suitable for time-critical operations
2. **Schema validation:** Receipts are validated against the JSON schema; non-conformant receipts are logged and rejected
3. **Receipt retention:** Receipts older than 30 days are archived to `artifacts/receipts/archive/` automatically
4. **Cross-machine sync:** Requires Supabase credentials; disabled by default; opt-in only

---

## References

- **Schema:** `data/schemas/arb_lint_receipt.schema.json`
- **Config:** `config/settings.json` → `arb.*`
- **Receipts directory:** `artifacts/receipts/`
- **Logs:** `artifacts/logs/arb/`
- **Skill:** `.github/skills/arb/SKILL.md` (workflow & ceremonies)
