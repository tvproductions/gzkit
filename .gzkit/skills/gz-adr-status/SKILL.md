---
name: gz-adr-status
description: Generate ADR status table or display terminal summary. GovZero v6 skill.
compatibility: GovZero v6 framework; generates ADR lifecycle status tracking
metadata:
  skill-version: "1.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
opsdev_command: adr status
invocation: uv run -m opsdev adr status
---

# gz-adr-status

Generate ADR status table or display rich terminal summary.

**Command:** `uv run -m opsdev adr status`

**Layer:** Layer 1 — Evidence Gathering

---

## When to Use

- To check current status of all ADRs
- Before starting work on an ADR
- During governance reviews
- To identify ADRs needing attention (Draft, Proposed, Completed)

---

## Invocation

```text
/gz-adr-status
/gz-adr-status --summary
```

**CLI equivalent:**

```bash
# Write status table to docs/design/adr/adr_status.md
uv run -m opsdev adr status

# Display rich terminal summary (no file write)
uv run -m opsdev adr status --summary
```

---

## Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--summary` | `false` | Display rich terminal summary instead of writing file |

---

## Output

### File Mode (default)

Writes `docs/design/adr/adr_status.md` with:

- All ADRs grouped by series (0.0.x, 0.1.x, etc.)
- Current status for each ADR
- Last modified date
- OBPI completion counts

### Summary Mode (`--summary`)

Displays rich terminal table with:

- ADR ID and title
- Current status (color-coded)
- OBPI progress (e.g., "7/9 complete")
- Staleness indicators

---

## Status Values

Per [adr-lifecycle.md](docs/governance/GovZero/adr-lifecycle.md):

| Status | Meaning |
|--------|---------|
| Pool | Idea captured, not yet drafted |
| Draft | Being written, not ready for review |
| Proposed | Ready for review/approval |
| Accepted | Approved, work can begin |
| Completed | All work done, awaiting audit |
| Validated | Audited and attested |
| Superseded | Replaced by newer ADR |
| Abandoned | Work stopped, not proceeding |

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| gz-adr-sync | Regenerate index + status files |
| gz-adr-check | Blocking evidence audit |
| gz-adr-audit | Gate 5 verification procedure |

---

## References

- Command: `src/opsdev/commands/adr_subcommands.py`
- Output: `docs/design/adr/adr_status.md`
