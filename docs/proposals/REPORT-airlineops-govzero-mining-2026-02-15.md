# REPORT: AirlineOps GovZero Mining

## Metadata

- Date: 2026-02-15
- Scanner: Human + Agent
- Canonical Source: `/Users/jeff/Documents/Code/airlineops`
- Identity rule: `GovZero = AirlineOps - (AirlineOps product capabilities)`
- Scope: GovZero process-habit extraction across control surfaces

---

## Mining Surfaces

- [x] `AGENTS.md`
- [ ] `CLAUDE.md`
- [x] `.github/**`
- [x] `.claude/**`
- [x] `.codex/**`
- [x] `.gzkit/**`
- [x] `docs/governance/GovZero/**`

---

## Mined Norms

| Norm ID | Mined Habit / Rule | Canonical Source Path | Product Capability? (Y/N) | Included in GovZero Scope? | gzkit Extraction Path(s) | Status (Parity/Partial/Missing/Divergent) | Notes |
|---|---|---|---|---|---|---|---|
| N-001 | Instruction surfaces are canonical and must be read before work | `.github/instructions/*.instructions.md` | N | Y | n/a | Missing | gzkit lacks `.github/instructions/` |
| N-002 | Skills must be mirrored across control surfaces | `.codex/skills/*` + `.claude/skills/*` | N | Y | `.claude/skills/*` only | Partial | `.codex/skills` mirror missing |
| N-003 | GovZero docs are a proof surface | `docs/governance/GovZero/**` | N | Y | `docs/governance/GovZero/**` | Parity | File set matches (incl. `audits/`, `releases/`) |
| N-004 | ADR tooling layer skill naming must match | `.github/skills/gz-adr-manager` | N | Y | `.github/skills/gz-adr-create` | Divergent | Rename/backport required |
| N-005 | Governance insights + lessons stored under `.gzkit/` | `.gzkit/governance`, `.gzkit/insights`, `.gzkit/lessons` | N | Y | `.gzkit/ledger.jsonl`, `.gzkit/manifest.json` | Partial | Surface gap in gzkit |

## NOT GovZero Exclusion Log

| Candidate Item | Canonical Source Path | Why NOT GovZero | Product Capability Evidence | Reviewer |
|---|---|---|---|---|
| Forecasting/warehouse/product ops skills | `.github/skills/*` (non-gz) | Product capability | Domain scope in skill names | Agent |

---

## Procedure Parity Checks

| Procedure Class | Canonical Source(s) | gzkit Runtime/Docs Surface(s) | Executable Check | Result | Evidence |
|---|---|---|---|---|---|
| Pre-tool orientation | `AGENTS.md`, instruction files | `AGENTS.md` | n/a | Partial | instruction files missing |
| Tool-use control | `gz-*` skills + instructions | `.github/skills/gz-*` | n/a | Divergent | `gz-adr-manager` vs `gz-adr-create` |
| Post-tool accounting | audit protocol | `uv run gz cli audit` | PASS | CLI audit passed |
| Validation | gate rules | `uv run gz check-config-paths` | FAIL | missing `docs/design/obpis` path |
| Verification | ADR audit-check | `uv run gz adr audit-check ADR-0.3.0` | PASS | all linked OBPIs completed |
| Human attestation boundary | Gate 5 doctrine | docs + attestation commands | Partial | missing instruction surfaces |

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
   - Severity: P1
   - Why it matters: Instruction surfaces missing in gzkit.
   - ADR/OBPI linkage: ADR-0.3.0 / new OBPI (instruction-surface parity)
   - Next action: Mirror canonical `.github/instructions/**`.

2. Finding:
   - Severity: P1
   - Why it matters: Skill naming divergence (`gz-adr-manager` vs `gz-adr-create`).
   - ADR/OBPI linkage: ADR-0.3.0 / OBPI-0.3.0-02 (backport execution)
   - Next action: Backport rename to AirlineOps or align gzkit.

3. Finding:
   - Severity: P2
   - Why it matters: `.codex/skills` mirror missing.
   - ADR/OBPI linkage: ADR-0.3.0 / new OBPI (control-surface mirror parity)
   - Next action: Add `.codex/skills` mirror + sync ritual.

4. Finding:
   - Severity: P2
   - Why it matters: Validation proof surfaces failing.
   - ADR/OBPI linkage: ADR-0.3.0 / new OBPI (proof-surface validation fixes)
   - Next action: Fix `gz check-config-paths` and mkdocs theme dependency.
