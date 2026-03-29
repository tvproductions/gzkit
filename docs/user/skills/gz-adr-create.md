# /gz-adr-create

Create and book a GovZero ADR with its OBPI briefs, enforcing SemVer odometer
discipline and five-gate compliance.

---

## Purpose

`/gz-adr-create` is the entry point for recording a new architectural decision.
It scaffolds the full ADR package — the decision document, closeout form, OBPI
briefs (one per checklist item), and registry entries — in a single invocation.
The skill enforces GovZero v6 compliance: SemVer minor-version odometer, canonical
lifecycle states, OBPI co-creation, and the ADR-contained directory layout.

## When to Use

Invoke `/gz-adr-create` when you have a new capability, architectural change, or
design decision that needs formal governance tracking. Typical trigger points:

- **After design exploration** — once `/gz-design` dialogue has produced a clear
  decision, create the ADR to formalize it.
- **When starting a new feature** — before implementation begins, the ADR
  captures intent, scope, and the OBPI work breakdown.
- **When recording a retrospective decision** — if a decision was made informally
  and needs governance backing.

This skill sits at the beginning of the ADR lifecycle. After creation, OBPIs
are executed via `/gz-obpi-pipeline` and the ADR is closed via `/gz-closeout`.
See [Runbook: ADR Creation](../runbook.md) for the full workflow.

## What to Expect

The skill performs these operations:

1. **Reads the canonical ADR template** from its co-located assets.
2. **Creates the ADR directory** under `docs/design/adr/{series}/ADR-{id}-{slug}/`.
3. **Generates the ADR document** with all required sections populated from your
   inputs (intent, decision, checklist items, interfaces, rationale, consequences).
4. **Creates the OBPI briefs** — one per checklist item — in the `obpis/`
   subfolder. Each brief has YAML frontmatter linking it to its parent ADR and
   checklist item.
5. **Creates the closeout form** (`ADR-CLOSEOUT-FORM.md`).
6. **Updates three registries**: `adr_index.md`, `adr_status.md`, and the
   governance copy at `docs/governance/GovZero/adr-status.md`.
7. **Runs post-authoring QC** via `/gz-adr-eval` to score the ADR and OBPIs.
8. **Validates** with `uv run -m unittest -q` and `uv run mkdocs build --strict`.

Typical runtime is 1-3 minutes depending on the number of checklist items.
The ADR starts in `Proposed` status.

**Success** looks like: ADR directory with document, closeout form, and OBPI
briefs; all three registries updated; mkdocs build passes.

**Failure** looks like: duplicate ADR ID, template not found, or registry
validation errors.

## Invocation

```text
/gz-adr-create ADR-0.25.0 --title agent-capability-uplift
/gz-adr-create ADR-0.25.0 --title agent-capability-uplift --series adr-0.25.x
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `ADR-X.Y.Z` | yes | The ADR identifier (SemVer format) |
| `--title` | yes | Kebab-case slug for the ADR directory name |
| `--series` | no | Series folder (e.g., `adr-0.25.x`); inferred from version if omitted |
| `--brief-count` | no | Number of OBPI briefs; inferred from checklist if omitted |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/gz-adr-create/SKILL.md` | Agent execution instructions | Read |
| `.claude/skills/gz-adr-create/assets/ADR_TEMPLATE_SEMVER.md` | Canonical ADR template with all required sections | Read |
| `src/gzkit/templates/obpi.md` | OBPI brief template for generated briefs | Read |
| `docs/design/adr/adr_index.md` | ADR index registry | Read/Write |
| `docs/design/adr/adr_status.md` | ADR status table | Read/Write |
| `docs/governance/GovZero/adr-status.md` | Governance copy of ADR status | Read/Write |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-design`](gz-design.md) | Typically precedes ADR creation — produces the design decision |
| [`/gz-specify`](gz-specify.md) | Alternative for creating individual OBPI briefs after ADR exists |
| [`/gz-adr-eval`](gz-adr-eval.md) | Post-authoring QC evaluation run during creation |
| [`/gz-obpi-pipeline`](gz-obpi-pipeline.md) | Executes the OBPIs created by this skill |
| [`/gz-closeout`](gz-closeout.md) | Closes the ADR after all OBPIs complete |
| [`gz register-adrs`](../commands/register-adrs.md) | Registers ADR ledger events after creation |
