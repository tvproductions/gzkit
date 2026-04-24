# Chores Directory — Agent Contract

**STOP. Read this entire file before modifying anything in this directory.**

---

## What This Directory Contains

Each subdirectory is a **self-contained chore package** with these files:

| File | Purpose | Required |
|------|---------|----------|
| `CHORE.md` | Definition, workflow, acceptance criteria | YES |
| `acceptance.json` | Machine-readable criteria for automation | YES |
| `README.md` | Human-readable summary | YES |
| `proofs/` | Directory for execution evidence | YES |

---

## MANDATORY: Consult Before Acting

Before executing or modifying ANY chore, read:

1. **The chore's `CHORE.md`** — Contains the authoritative procedure
2. **The registry** at `config/gzkit.chores.json` — For discovery

---

## Chore Execution Protocol

### Step 1: Read the CHORE.md

Every chore has a workflow section. Follow it exactly.

### Step 2: Dry-Run Criteria

```bash
uv run gz chores advise <chore_slug>
```

### Step 3: Run Evidence Commands

Execute the commands listed in the CHORE.md Evidence section. Save outputs to `proofs/`:

```bash
# Example: Save command output to proofs/
uvx ruff check . > ops/chores/pythonic-refactoring/proofs/ruff-report.txt
```

### Step 4: Execute and Log

```bash
uv run gz chores run <chore_slug>
```

This validates acceptance criteria and writes a dated log entry to `proofs/CHORE-LOG.md`.

---

## What You MUST NOT Do

1. **DO NOT skip the CHORE.md** — It contains the authoritative procedure
2. **DO NOT put proofs in `artifacts/`** — Proofs go in the chore's `proofs/` directory
3. **DO NOT modify acceptance criteria** without updating both `CHORE.md` and `acceptance.json`
4. **DO NOT create chores without all required files**

---

## What You SHOULD Do

1. **Follow the established pattern** — Study existing chores before creating new ones
2. **Keep proofs atomic** — One file per evidence artifact
3. **Use descriptive filenames** — `ruff-report-2026-03-19.txt` not `output.txt`
4. **Commit proofs** — They are tracked, not gitignored

---

## Adding a New Chore

Use an existing chore as a template. Required structure:

```text
ops/chores/{slug}/
├── CHORE.md          # Definition, workflow, acceptance criteria
├── acceptance.json   # Machine-readable criteria
├── README.md         # Brief human summary
└── proofs/           # Evidence directory
    └── .gitkeep      # Keep the directory tracked
```

After creating, add the chore pointer to `config/gzkit.chores.json`.

---

## Acceptance Criteria Format

The `acceptance.json` file uses this schema:

```json
{
  "criteria": [
    {
      "type": "exitCodeEquals",
      "command": "uv run -m unittest -q",
      "expected": 0
    },
    {
      "type": "outputNotContains",
      "command": "uvx ruff check src/gzkit --select E722",
      "notContains": "E722",
      "description": "No bare except clauses"
    }
  ]
}
```

Supported types:

- `exitCodeEquals` — Command must exit with specific code
- `outputContains` — Command output must contain string
- `outputNotContains` — Command output must not contain string
- `fileExists` — File must exist at path

Commands must not contain shell operators (`&&`, `||`, `|`, `<`, `>`).
Split compound commands into separate criteria.

---

## If You're Unsure

**ASK THE HUMAN:**

- "Should I create a new chore or add to an existing one?"
- "What lane should this chore be?"
- "Where should I store this proof artifact?"
