# Gate 5 Documentation Architecture

**Status:** Active
**Last reviewed:** 2026-01-29

---

## Overview

Gate 5 enforces **code-documentation-intent alignment** for Heavy lane work. This document
defines the three-layer documentation structure that proves robustness.

**Core Principle:** Documentation is the Gate 5 artifact. There is no separate "Gate 5 deliverable."
You organize existing docs to prove robustness.

---

## Three-Layer Documentation Structure

**Effective:** 2025-12-06

```text
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: Operator Runbook (docs/user/operator_runbook.md)          │
│  ─────────────────────────────────────────────────────────────────  │
│  Entry point and narrative index                                    │
│  High-level workflow (Librarian → Warehouse → Reporter)             │
│  Governance context (hot horizons, alignment, retention)            │
│  Troubleshooting and cross-dataset coordination                     │
│  Pointers to manpages for detailed references                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ references
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: Manpage Directory (docs/user/manpages/)                   │
│  ─────────────────────────────────────────────────────────────────  │
│  Unix-style command references (one per workflow step)              │
│  Structure: NAME, SYNOPSIS, DESCRIPTION, OPTIONS,                   │
│             IMPLEMENTATION TRACE, CONFIGURATION,                    │
│             ALGORITHM, EXAMPLES, EXIT STATUS, SEE ALSO, NOTES       │
│  Config-First: All settings from config/settings.json               │
│  Concrete, tested examples with expected output                     │
│  Exit codes with recovery procedures                                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ traces to
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: Docstrings (in source code .py files)                     │
│  ─────────────────────────────────────────────────────────────────  │
│  Pure PEP 257 style: One-liner + Args + Returns + Raises            │
│  PROHIBITED: Call Stack, Configuration, Algorithm, Examples         │
│  REQUIRED: One-liner summary, Args, Returns, Raises                 │
│  Optional Note pointing to manpage for implementation trace         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Layer 1: Operator Runbook

**File:** `docs/user/operator_runbook.md`

**Purpose:** Entry point for operators. Provides the "what" and "why" of workflows.

**Contents:**

- High-level workflow sequence
- Governance context (hot horizons, alignment, retention)
- Troubleshooting and cross-dataset coordination
- Pointers to manpages (never duplicates manpage content)

### Layer 2: Manpage Directory

**Directory:** `docs/user/manpages/`

**Purpose:** Unix-style command references. One file per workflow step.

**Required Sections:**

| Section | Content |
|---------|---------|
| NAME | Command name and one-line summary |
| SYNOPSIS | Command syntax with options |
| DESCRIPTION | What the command does |
| OPTIONS | All flags and arguments |
| IMPLEMENTATION TRACE | Call stack with docstring summaries |
| CONFIGURATION | Settings from config/settings.json |
| ALGORITHM | Step-by-step logic (numbered) |
| EXAMPLES | Concrete, tested examples with expected output |
| EXIT STATUS | Exit codes and recovery procedures |
| SEE ALSO | Related manpages and docs |
| NOTES | Edge cases, caveats, version notes |

**IMPLEMENTATION TRACE format:**

```text
module.py :: function_name() — One-liner from docstring
  ├── helper.py :: helper_func() — Helper one-liner
  └── utils.py :: utility_func() — Utility one-liner
```

### Layer 3: Docstrings

**Location:** Source code `.py` files

**Style:** Pure PEP 257

**Required:**

- One-liner summary (sacred first line — shared with manpage)
- Args section
- Returns section
- Raises section

**Prohibited (goes in manpages instead):**

- Call Stack
- Configuration
- Algorithm
- Examples
- Exit code tables

---

## Mirroring Strategy (No Duplication)

**Principle:** Single source of truth for each piece of information.

| Information | Source of Truth | Consumers |
|-------------|-----------------|-----------|
| Args/Returns/Raises | Docstring | Manpage abbreviates |
| One-liner summary | Docstring | Manpage copies verbatim |
| Algorithm | Manpage | Code implements |
| Configuration | config/settings.json | Manpage documents |
| Exit codes | Manpage | Code returns |

---

## Enforcement Hooks

| Hook | Purpose | Threshold |
|------|---------|-----------|
| `validate-manpages` | Every function in manpage IMPLEMENTATION TRACE exists in code | 100% |
| `sync-manpage-docstrings --check` | One-liners match between code and manpage | Exact match |
| `interrogate -f 85` | Docstring coverage | ≥85% |
| `test-manpage-examples` | Extract bash from EXAMPLES, execute, verify exit codes | All pass |

---

## Agent Workflow (Heavy Lane)

When implementing Heavy lane work:

1. **Update code** — implementation + tests
2. **Update docstrings** — pure PEP 257 (Args, Returns, Raises)
3. **Update manpage** — IMPLEMENTATION TRACE, CONFIGURATION, ALGORITHM, EXAMPLES, EXIT STATUS
4. **Update operator_runbook.md** — if workflow sequence or governance changes
5. **Run validation chores** — before commit

---

## Gate 5 Checklist

Every Heavy brief must satisfy:

- [ ] Operator runbook updated or confirmed current
- [ ] Manpage updated (IMPLEMENTATION TRACE, CONFIGURATION, ALGORITHM, EXAMPLES, EXIT STATUS)
- [ ] Docstrings updated (pure PEP 257: Args, Returns, Raises)
- [ ] Help text (argparse) reflects actual behavior
- [ ] Examples are concrete, accurate, executable
- [ ] Links/anchors validated (mkdocs build clean)
- [ ] Markdown lint clean
- [ ] Validation chores pass (validate-manpages, sync-manpage-docstrings --check, interrogate)

---

## See Also

- [GovZero Charter](charter.md) — Gate definitions
- [Audit Protocol](audit-protocol.md) — Closeout ceremony procedure
- [Runbook-Code Covenant](../../../.github/instructions/gate5_runbook_code_covenant.instructions.md) — Binding instructions
