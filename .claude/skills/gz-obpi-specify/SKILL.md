---
name: gz-obpi-specify
description: Create and semantically author OBPI briefs linked to parent ADR items. Use when decomposing implementation into OBPI increments.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-obpi-specify

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

# Create and author one OBPI brief in one pass
uv run gz specify my-feature-slug --parent ADR-0.0.11 --item 3 --author

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

## Authored-Readiness Contract

`gz specify` is the ADR-to-OBPI decomposition command, not a pseudo-authoring
shortcut. It fills the brief with deterministic ADR-derived content, but the
brief is only ready for pipeline execution when it passes authored validation:

```bash
uv run gz obpi validate --adr ADR-0.0.11 --authored
```

That gate requires each brief to have substantive:

- Objective
- Allowed Paths
- Denied Paths
- Requirements (FAIL-CLOSED)
- Discovery Checklist prerequisites and existing-code entries
- OBPI-specific verification commands
- REQ-backed acceptance criteria

## Skill Responsibility

The skill does not stop at `uv run gz specify`.

The intended workflow is:

1. Run `gz specify --author` to materialize the OBPI from the ADR/WBS contract and execute the authored pass.
2. Read the parent ADR sections that govern the item: Feature Checklist, WBS row,
   Intent, Decision, Interfaces, Evidence, and adjacent OBPIs when needed.
3. Author the brief semantically:
   - narrow Allowed Paths and Denied Paths to the real execution boundary
   - rewrite Requirements into OBPI-specific fail-closed rules
   - populate Discovery Checklist with real prerequisite and existing-code reads
   - replace generic verification with commands that prove this item specifically
   - ensure Acceptance Criteria are concrete and mapped to REQ IDs
   - **every REQ-ID becomes a mandatory `@covers("REQ-X.Y.Z-NN-MM")` test traceability target** — this is enforced at implementation (Stage 2) and verification (Stage 3) by `gz adr audit-check`
4. Run `uv run gz obpi validate --authored <path>` and keep authoring until it passes.

The CLI owns deterministic decomposition. The skill owns the semantic authoring
pass that turns the generated brief into an execution contract.

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
# Fail closed if any brief is still thin or pseudo-authored
uv run gz obpi validate --adr ADR-0.0.11 --authored

# Verify count matches
ls docs/design/adr/foundation/ADR-0.0.11-*/obpis/ | wc -l

# Verify lanes match WBS
grep "^lane:" docs/design/adr/foundation/ADR-0.0.11-*/obpis/*.md

# Register any unregistered OBPIs
uv run gz register-adrs ADR-0.0.11 --all
```

---

## Heavy Lane Requirements

When a brief's lane is Heavy (from WBS or CLI override):

1. **Read `assets/HEAVY_LANE_PLAN_TEMPLATE.md`** before authoring — this is mandatory
2. Gate 5 attestation is required before OBPI closure
3. Human must execute CLI commands and provide explicit attestation
4. BDD scenarios + docs/manpage updates are additional acceptance criteria

**Heavy lane failure modes:**
- Marking OBPI closed before human attestation
- Skipping Gate 5 attestation step
- Not presenting CLI commands for human verification

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `gz-adr-create` | Creates the parent ADR that specify decomposes |
| `gz-obpi-pipeline` | Executes briefs created by specify |
| `gz-adr-evaluate` | Evaluates ADR+OBPI quality (run after specify) |
