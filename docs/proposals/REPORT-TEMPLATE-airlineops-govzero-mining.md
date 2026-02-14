# REPORT: AirlineOps GovZero Mining (Template)

## Metadata

- Date: YYYY-MM-DD
- Scanner: Human + Agent
- Canonical Source: `../airlineops`
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`
- Scope: GovZero process-habit extraction across control surfaces

---

## Mining Surfaces

- [ ] `AGENTS.md`
- [ ] `CLAUDE.md`
- [ ] `.github/**`
- [ ] `.claude/**`
- [ ] `.codex/**`
- [ ] `.gzkit/**`
- [ ] `docs/governance/GovZero/**`

---

## Mined Norms

| Norm ID | Mined Habit / Rule | Canonical Source Path | Product Capability? (Y/N) | Included in GovZero Scope? | gzkit Extraction Path(s) | Status (Parity/Partial/Missing/Divergent) | Notes |
|---|---|---|---|---|---|---|---|
| N-001 |  |  |  |  |  |  |  |

## NOT GovZero Exclusion Log

Exclusions are exceptional. Default is inclusion in GovZero scope unless product capability evidence is explicit.

| Candidate Item | Canonical Source Path | Why NOT GovZero | Product Capability Evidence | Reviewer |
|---|---|---|---|---|
|  |  |  |  |  |

---

## Procedure Parity Checks

| Procedure Class | Canonical Source(s) | gzkit Runtime/Docs Surface(s) | Executable Check | Result | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation |  |  |  |  |  |
| Tool-use control |  |  |  |  |  |
| Post-tool accounting |  |  |  |  |  |
| Validation |  |  |  |  |  |
| Verification |  |  |  |  |  |
| Human attestation boundary |  |  |  |  |  |

---

## Required Commands

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-<target>
uv run mkdocs build --strict
```

---

## Findings and Next Actions

1. Finding:
   - Severity:
   - Why it matters:
   - ADR/OBPI linkage:
   - Next action:

2. Finding:
   - Severity:
   - Why it matters:
   - ADR/OBPI linkage:
   - Next action:
