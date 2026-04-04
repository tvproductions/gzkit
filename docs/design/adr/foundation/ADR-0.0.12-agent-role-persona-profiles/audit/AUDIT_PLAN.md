# AUDIT PLAN (Gate-5) — ADR-0.0.12

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.12 |
| ADR Title | Agent Role Persona Profiles |
| SemVer | 0.0.12 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles |
| Audit Date | 2026-04-04 |
| Auditor(s) | Claude Opus 4.6 (agent), jeff (human attestor) |

## Purpose

Confirm ADR-0.0.12 implementation is complete by validating that all six agent
roles have persona frames loaded at dispatch time, AGENTS.md references the
persona control surface, and all evidence is reproducible.

**Audit Trigger:** Post-implementation Gate-5 validation. ADR is Completed with
all 7 OBPIs attested. Moving to Validated.

## Scope & Inputs

**Primary contract surfaces:**

- `.gzkit/personas/*.md` — 6 persona files (main-session, implementer, spec-reviewer, quality-reviewer, narrator, pipeline-orchestrator)
- `uv run gz personas list` / `uv run gz personas list --json` — persona discovery CLI
- `src/gzkit/pipeline_runtime.py` — dispatch persona loading (`load_persona_for_dispatch`, `prepend_persona_to_prompt`)
- `AGENTS.md` — main session persona reference section

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| All 6 persona files exist | `uv run gz personas list` | 6 personas in table | Pending |
| JSON mode works | `uv run gz personas list --json` | Valid JSON, 6 entries | Pending |
| Schema validation | `uv run -m unittest tests.test_persona_schema -v` | 52 tests OK | Pending |
| Model validation | `uv run -m unittest tests.test_persona_model -v` | 10 tests OK | Pending |
| Dispatch integration | `uv run -m unittest tests.test_pipeline_runtime.TestPersonaPipelineIntegration -v` | 11 tests OK | Pending |
| AGENTS.md persona section | `uv run -m unittest tests.test_sync_surfaces -v` | 12 tests OK | Pending |
| BDD persona scenarios | `uv run -m behave features/persona.feature` | 6 scenarios, 30 steps pass | Pending |
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.12` | PASS, 21/22 REQs | Pending |

## Risk Focus

- **REQ-0.0.12-07-03 uncovered** — BDD requirement (persona.feature scenarios pass). Covered by behave but not by `@covers` decorator since BDD steps don't use Python decorators. Tooling coverage gap, not implementation gap.
- **Test file naming drift** — ADR Evidence section references `tests/test_persona_profiles.py` but actual files are `tests/test_persona_schema.py` and `tests/test_persona_model.py`. Non-blocking documentation drift.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with checkmarks.
- Proof logs saved under `audit/proofs/` and referenced.
- No edits to accepted ADR prose.
- Feature demonstration showing persona loading in action.

## Attestation Placeholder

Human will complete in `AUDIT.md` with final summary.
