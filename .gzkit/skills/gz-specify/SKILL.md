---
name: gz-specify
description: Create OBPI briefs linked to parent ADR items. Use when decomposing implementation into OBPI increments.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-30
---

# gz specify

Decompose an ADR's Feature Checklist into implementable OBPI briefs. Each brief
inherits lane, objective, and scope from the parent ADR's WBS table — not from
hardcoded defaults.

---

## When to Use

- After an ADR is authored and its Decomposition Scorecard is valid
- When the Feature Checklist and WBS table are aligned (same count, same ordering)
- To create one OBPI brief per checklist item

## When NOT to Use

- For pool ADRs (they cannot receive OBPIs until promoted)
- If the ADR has no Feature Checklist or Decomposition Scorecard
- If the WBS table and Feature Checklist are misaligned (fix the ADR first)

---

## Invocation

```bash
# Create one OBPI brief (lane and objective from WBS table)
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3

# Override lane explicitly
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3 --lane heavy

# Dry run (show what would be created)
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3 --dry-run

# Create all OBPIs for an ADR (run once per checklist item)
for i in $(seq 1 6); do
  uv run gz specify slug-$i --parent ADR-0.0.11 --item $i
done
```

---

## What the Command Does

1. **Reads the parent ADR** — resolves file, parses Feature Checklist and Decomposition Scorecard
2. **Validates alignment** — checklist item count must match scorecard target
3. **Parses the WBS table** — extracts lane, specification summary, and status per row
4. **Resolves lane** — priority: explicit `--lane` CLI arg > WBS table row > fallback `lite`
5. **Resolves objective** — from WBS specification summary column (not "TBD")
6. **Creates the brief** — renders the OBPI template with populated frontmatter
7. **Records the ledger event** — appends `obpi_created` to the project ledger

---

## Lane Resolution

| Source | When Used |
|--------|-----------|
| `--lane heavy` (CLI) | Always wins when explicitly passed |
| WBS table row | Used when `--lane` is not passed and WBS table has a row for this item |
| Fallback `lite` | Used when neither CLI nor WBS provides a lane |

The command prints the lane source so the operator can verify:
```
Lane: heavy (source: WBS table)
```

---

## What the Brief Still Needs After Creation

The command populates frontmatter (id, parent, item, lane, status) and objective
from the WBS table. The following sections still contain template defaults and
**must be authored** before pipeline execution:

- **Allowed Paths** — specific files/directories in scope
- **Denied Paths** — what's explicitly out of scope
- **Requirements (FAIL-CLOSED)** — numbered constraints with NEVER/ALWAYS language
- **Acceptance Criteria** — REQ-prefixed Given/When/Then criteria
- **Verification commands** — real commands that prove the work is done
- **Discovery Checklist** — prerequisite files to read

---

## Pre-Conditions

- Parent ADR must have a valid Decomposition Scorecard
- Feature Checklist item count must match scorecard `Final Target OBPI Count`
- Parent ADR must not be a pool ADR

## Post-Conditions

- OBPI brief file created at `{adr-dir}/obpis/OBPI-{version}-{NN}-{slug}.md`
- Lane matches WBS table (or CLI override)
- Objective derived from WBS specification summary
- `obpi_created` ledger event recorded

---

## Validation

After creating all briefs:

```bash
# Verify count matches
ls docs/design/adr/foundation/ADR-0.0.11-*/obpis/ | wc -l

# Verify lanes match WBS
grep "^lane:" docs/design/adr/foundation/ADR-0.0.11-*/obpis/*.md

# Register any unregistered OBPIs
uv run gz register-adrs ADR-0.0.11 --all
```

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-adr-create` | Creates the parent ADR that specify decomposes |
| `gz-obpi-brief` | Alternative manual brief creation |
| `gz-obpi-pipeline` | Executes briefs created by specify |
| `gz-adr-eval` | Evaluates ADR+OBPI quality (run after specify) |
