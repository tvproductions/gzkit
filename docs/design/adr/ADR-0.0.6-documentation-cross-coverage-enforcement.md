---
id: ADR-0.0.6-documentation-cross-coverage-enforcement
status: Draft
semver: 0.0.6
lane: heavy
parent:
date: 2026-03-23
---

# ADR-0.0.6: Documentation Cross-Coverage Enforcement

## Intent

1. **AST-scanning chore** — Discover all CLI subcommands from argparse registrations and verify each has a manpage, command index entry, runbook reference, docstring, and manpage mapping
2. **Documentation manifest** — Declare the documentation contract (`config/doc-coverage.json`) so obligations are explicit and auditable
3. **Bidirectional coverage** — Detect both undocumented commands and stale documentation references to removed commands
4. **Chore integration** — Register as a `gz chores` item so doc coverage runs as part of regular maintenance

## Decision

### Three-Layer Model

```
Layer B: AST Scanner (discovers what exists, verifies surfaces)
  ├── Scans cli.py for add_parser() calls
  ├── Verifies: manpage, index entry, runbook ref, docstring, mapping
  └── Detects: orphaned docs referencing removed commands

Layer C: Documentation Manifest (declares what should exist)
  ├── config/doc-coverage.json
  ├── Maps command → required surfaces
  └── Governance-relevant flag per command

Layer B+C: Chore Runner (enforcement surface)
  ├── gz chores run doc-coverage
  ├── Produces pass/fail report
  └── Actionable gap list
```

### Required Surfaces Per Command

| Surface | Verification Method |
|---------|-------------------|
| Manpage | `docs/user/commands/<slug>.md` exists |
| Command index | Listed in `docs/user/commands/index.md` |
| Operator runbook | Referenced in `docs/user/runbook.md` |
| Governance runbook | Referenced in `docs/governance/governance_runbook.md` (if governance-relevant) |
| Docstring | CLI handler function has non-empty docstring |
| Manpage mapping | Registered in `src/gzkit/commands/common.py` |

### Chore Registration

```json
{
  "slug": "doc-coverage",
  "description": "Audit documentation cross-coverage for CLI commands and skills",
  "frequency": "per-release",
  "command": "uv run gz chores run doc-coverage"
}
```

## Consequences

### Positive

Automated detection of documentation gaps at the point of change, not after manual audit.

### Negative

New maintenance surface (manifest). Mitigated by the scanner catching drift automatically.

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 6
- Baseline Range: 3-4
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

- [ ] OBPI-0.0.6-01: AST Scanner — Discover CLI commands and verify documentation surfaces
- [ ] OBPI-0.0.6-02: Documentation Manifest — Declare per-command documentation obligations
- [ ] OBPI-0.0.6-03: Chore Registration and Enforcement — Register as chore, produce actionable report

## Q&A Transcript

Discovered 2026-03-23 when four QC capabilities (#29-#32) were merged without runbook or manpage coverage. Manual audit caught the gap (#33). Prior art: `gz cli audit` (manpage/index parity), `interrogate` (docstring coverage), OBPI-0.0.3-09 (AST policy tests).

## Evidence

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

Single-layer scanner without manifest. Rejected because the manifest makes obligations explicit — the scanner alone can only detect what exists, not what should exist.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.6 | Pending | | | |
