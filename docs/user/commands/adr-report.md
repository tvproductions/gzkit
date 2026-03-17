# gz adr report

Deterministic tabular report — summary across all ADRs or focused detail for one ADR.

---

## Usage

```bash
# Summary table (all ADRs)
gz adr report

# Focused detail for one ADR
gz adr report <ADR-ID>
```

`<ADR-ID>` accepts full IDs (for example `ADR-0.5.0-skill-lifecycle-governance`) and
unique SemVer prefixes (for example `0.5.0` or `ADR-0.5.0`) when exactly one ADR ID
starts with that prefix.

---

## Runtime Behavior

### Summary Mode (no argument)

Renders the same ADR summary table as `gz status --table` — a deterministic ASCII table
showing lifecycle, lane, OBPI completion, unit status, QC readiness, and pending checks
for every registered ADR.

### Focused Mode (with ADR ID)

Renders three sections:

1. **ADR Overview** — single-row table with lifecycle, lane, OBPI completion, closeout
   readiness, and QC readiness.
2. **OBPIs** — one row per linked OBPI with runtime state, brief status, and completion
   flag.
3. **Issues** — per-OBPI issue and reflection lines when problems exist.

All output uses Rich ASCII-box tables for deterministic rendering.

---

## Example

```bash
# Summary of all ADRs
uv run gz adr report

# Focused report for ADR-0.14.0
uv run gz adr report ADR-0.14.0
uv run gz adr report 0.14.0
```
