# PLAN: AirlineOps Backport for OBPI-0.3.0-02

## Purpose

Apply the gzkit OBPI-0.3.0-02 parity outcomes back into AirlineOps to preserve bidirectional parity for ADR create/audit behavior.

## Required Backport Changes

1. Rename skill surface:
- `gz-adr-manager` -> `gz-adr-create`
- Update skill directory names in `.github/skills/` and `.claude/skills/`
- Update references in `AGENTS.md`, `CLAUDE.md`, GovZero docs, and skill cross-links

2. Preserve full-depth skill behavior:
- Keep canonical `gz-adr-audit` procedure depth and assets
- Keep canonical create workflow under renamed `gz-adr-create`

3. Runtime/doc alignment:
- Ensure command references in skills map to active AirlineOps runtime command surface
- Update command manpages/runbook links to renamed skill

## Suggested Sequencing

1. Rename skill directories and internal references
2. Regenerate control surfaces
3. Run command/docs parity checks
4. Re-run parity scan from gzkit against updated AirlineOps

## Blast Radius Checklist

- [ ] `.github/skills/**` references updated
- [ ] `.claude/skills/**` mirrors updated
- [ ] `AGENTS.md` skill catalog updated
- [ ] `CLAUDE.md` skill catalog updated
- [ ] GovZero docs references updated
- [ ] Any ADR/OBPI templates referencing `gz-adr-manager` updated

## Verification Commands

```bash
# in airlineops
uv run -m unittest discover tests
uv run -m opsdev md-docs
uv run -m opsdev check-config-paths

# from gzkit parity side
uv run gz cli audit
uv run gz check-config-paths
```

## Completion Signal

Backport is complete when both repositories report `gz-adr-create` and no active `gz-adr-manager` references remain in operator control surfaces.
