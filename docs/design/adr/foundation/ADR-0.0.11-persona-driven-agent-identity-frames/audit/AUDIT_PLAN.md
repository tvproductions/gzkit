# AUDIT PLAN (Gate-5) — ADR-0.0.11

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.11 |
| ADR Title | Persona-Driven Agent Identity Frames |
| SemVer | 0.0.11 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames |
| Audit Date | 2026-04-02 |
| Auditor(s) | jeff (human), Claude (agent) |

## Purpose

Confirm ADR-0.0.11 implementation is complete by validating its claims with reproducible CLI evidence.

**Audit Trigger:** Gate-5 validation — ADR is Completed with all 6 OBPIs attested. Moving to Validated.

## Scope & Inputs

**Primary contract surfaces:**

- `.gzkit/personas/` control surface directory (persona storage)
- `uv run gz personas list` — persona enumeration CLI
- `uv run gz validate --personas` — schema validation integration
- `.gzkit/personas/implementer.md` — exemplar persona file
- AGENTS.md `## Persona` section — template integration
- `docs/design/research-persona-selection-agent-identity.md` — research synthesis

**Governance surfaces:**

- `uv run gz adr report ADR-0.0.11` — ADR lifecycle status
- `uv run gz adr audit-check ADR-0.0.11` — ledger proof completeness

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Persona list CLI | `uv run gz personas list` | Lists defined personas | Pending |
| Persona validation | `uv run gz validate --personas` | Schema validation passes | Pending |
| Persona file exists | `ls .gzkit/personas/implementer.md` | File present with YAML frontmatter | Pending |
| AGENTS.md persona section | `grep "## Persona" AGENTS.md` | Mandatory section present | Pending |
| Research doc exists | `ls docs/design/research-persona-selection-agent-identity.md` | Research synthesis present | Pending |
| Unit tests | `uv run -m unittest -q` | All tests pass | Pending |
| Docs build | `uv run mkdocs build -q` | Build clean | Pending |
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.11` | PASS (already verified) | Pending |
| Gates | `uv run gz gates --adr ADR-0.0.11` | All gates pass | Pending |
| REQ coverage | Audit-check advisory | >=60% coverage | Pending |

## Risk Focus

- **Uncovered REQs:** 7/20 REQs uncovered (OBPI-01 at 0%, OBPI-05 at 0%, OBPI-02 at 80%). Assess whether these are test-coverage gaps or genuine missing implementation.
- **Trait composition model:** Verify orthogonal composition is tested, not just documented.
- **Schema validation:** Confirm negative-case testing (malformed personas rejected).

## Findings Placeholder

Will be captured in `AUDIT.md` — do not populate here beyond structural notes.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- ADR present in index/status with correct state.
- No edits to accepted ADR prose.

## Attestation Placeholder

Human will complete in `AUDIT.md` with final ✓ summary.
