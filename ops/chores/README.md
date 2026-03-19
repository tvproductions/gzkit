# Chores Directory

This directory contains **self-contained chore packages** — recurring maintenance tasks with
definitions, acceptance criteria, and tracked evidence.

## What is a Chore?

A chore is a repeatable maintenance activity with:

- **Clear scope:** Specific area of the codebase or process
- **Measurable acceptance:** Machine-readable criteria for completion
- **Tracked evidence:** Proof artifacts committed to git

Chores are **not features**. They maintain code quality, enforce policy, and reduce technical debt.

## Directory Structure

Each chore is a self-contained directory:

```text
ops/chores/{slug}/
├── CHORE.md          # Definition, procedure, acceptance criteria
├── acceptance.json   # Machine-readable acceptance criteria
├── README.md         # Human-readable summary
└── proofs/           # Execution evidence
    └── CHORE-LOG.md  # Auto-appended by gz chores run
```

## Chore Registry

The file `config/gzkit.chores.json` serves as the **central registry** for chore discovery.
It points to chore directories here but does not contain the definitions.

## How to Execute a Chore

```bash
# 1. Discover
uv run gz chores list

# 2. Inspect
uv run gz chores show <slug>

# 3. Assess
uv run gz chores advise <slug>

# 4. Fix (if criteria fail)
# Read ops/chores/<slug>/CHORE.md for remediation workflow

# 5. Execute and log
uv run gz chores run <slug>

# 6. Audit
uv run gz chores audit --slug <slug>
```

## How to Add a New Chore

1. Create a new directory: `ops/chores/{slug}/`
2. Add `CHORE.md` following the template pattern
3. Add `acceptance.json` with machine-readable criteria
4. Add `README.md` with a human summary
5. Create `proofs/` directory with `.gitkeep`
6. Add the chore pointer to `config/gzkit.chores.json`

## Lane Classification

| Lane | Timeout | Description |
|------|---------|-------------|
| **lite** | 120s | Internal changes only, no external contract changes |
| **medium** | 300s | Expanded checks, full test runs |
| **heavy** | 900s | External contracts, docs, full gates |
