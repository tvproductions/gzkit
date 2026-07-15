# ADR Closeout Form: ADR-0.0.65-handoff-system-consolidation

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.65-handoff-system-consolidation` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.65-01-canonical-location-migration](OBPI-0.0.65-01-canonical-location-migration.md) | **canonical-location-migration** — Canonize `.gzkit/handoffs/` as the single handoff write location per ADR-0.0.41. Migrate the 24 per-ADR handoff files (across 10 ADR packages) into `.gzkit/handoffs/`, preserving `continues_from:` chains and frontmatter timestamps. Amend `gz-session-handoff/SKILL.md` output-path doctrine from `{ADR-package}/handoffs/` to `.gzkit/handoffs/`. Bump `skill-version` and `last_reviewed`; run `gz agent sync control-surfaces`. | Completed |
| [OBPI-0.0.65-02-programmatic-api-implementation](OBPI-0.0.65-02-programmatic-api-implementation.md) | Real handoff authoring API (wraps the validation gate; grounded scaffolding) | Completed |
| [OBPI-0.0.65-03-gz-handoff-cli-verb](OBPI-0.0.65-03-gz-handoff-cli-verb.md) | **gz-handoff-cli-verb** — Add `handoff` CLI verb with `create`, `resume`, `list` subcommands routing authoring through the validation gate. Add manpage under `docs/user/manpages/`. Add behave coverage for create/resume/list flows. | Completed |
| [OBPI-0.0.65-04-orientation-single-location-scan](OBPI-0.0.65-04-orientation-single-location-scan.md) | **orientation-single-location-scan** — Collapse `_candidate_handoff_dirs()` in `scripts/session_orientation.py` to a single-surface scan of `.gzkit/handoffs/`. Delete the GHI #529 dual-scan workaround. Update orientation tests. (Depends on OBPI-01 completion: cannot collapse the scan until the per-ADR sources are empty.) | Completed |
| [OBPI-0.0.65-05-handoff-archive-retention](OBPI-0.0.65-05-handoff-archive-retention.md) | Handoff Archive Retention | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.65-01-canonical-location-migration | governance_artifact | FOUND |
| OBPI-0.0.65-02-programmatic-api-implementation | docstring | FOUND |
| OBPI-0.0.65-03-gz-handoff-cli-verb | runbook | FOUND |
| OBPI-0.0.65-04-orientation-single-location-scan | test_evidence | FOUND |
| OBPI-0.0.65-05-handoff-archive-retention | runbook | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `Completed — attest completed (g0): 5/5 OBPIs attested; 6 live demos verified (archive dry-run/live parity, list --json/--adr, resume, gated create); ARB green — arb-ruff-d510f84, arb-step-typecheck-c615ea4, arb-step-unittest-ab54fac6, arb-step-mkdocs-5447c487; bound fidelity gate passed; validate --documents clean.`

**Attested by**: g0
**Timestamp (UTC)**: 2026-07-15T22:35:27Z
