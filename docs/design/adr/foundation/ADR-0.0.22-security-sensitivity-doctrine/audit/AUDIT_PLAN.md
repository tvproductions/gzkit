# AUDIT PLAN — ADR-0.0.22 Security Sensitivity Doctrine

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.22 |
| ADR Title | Security Sensitivity Doctrine |
| SemVer | 0.0.22 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine |
| Audit Date | 2026-04-29 |
| Auditor(s) | Jeffry Babb (operator), main-session agent (relayed) |

## Purpose

Confirm ADR-0.0.22 implementation is complete by validating its claims with reproducible CLI evidence and demonstrating the delivered capabilities working end-to-end.

**Audit Trigger:** Phase 2 (Validated) transition — ADR closeout-attested 2026-04-29; lifecycle currently `Completed`, target `Validated`.

## Scope & Inputs

**Primary contract surfaces introduced or modified:**

- `src/gzkit/schemas/adr.json`, `src/gzkit/schemas/obpi.json` — `sensitivity` enum field
- `data/security_surfaces.json` (new) — registered glob registry of security-sensitive surfaces
- `src/gzkit/schemas/security_surfaces.json` (new) — registry schema fragment
- `src/gzkit/governance/trust_audits.py` — `validate_sensitivity_binding` for `gz validate --sensitivity`
- `src/gzkit/commands/adr_audit.py` — `_requires_security_review_attestation` ORed into `_requires_human_obpi_attestation`
- `src/gzkit/arb/validator.py` — `CANONICAL_STEP_COMMANDS` reserved security-scan slot
- `src/gzkit/commands/obpi.py` — Gate 5 walkthrough extension for `sensitivity: security`
- `.gzkit/rules/security-sensitivity.md` — canonical rule file
- `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix — three-axis matrix
- `docs/governance/advisory-rules-audit.md` — Mechanical scorecard entry

**System health surfaces used:**

- `uv run gz adr audit-check ADR-0.0.22`
- `uv run gz adr report ADR-0.0.22`
- `uv run gz validate --sensitivity`
- `uv run gz validate --sensitivity --explain <paths>`
- `uv run gz cli audit`

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Ledger proof complete | `uv run gz adr audit-check ADR-0.0.22` | All 6 OBPIs PASS, 36/36 REQs | Pending |
| ADR lifecycle Completed | `uv run gz adr status ADR-0.0.22` | `Lifecycle=Completed`, `Closeout=attested`, 6/6 OBPIs `attested_completed` | Pending |
| Sensitivity validate scope | `uv run gz validate --sensitivity` | 587 briefs scanned, no escapes, registry healthy | Pending |
| `--explain` predictive subform | `uv run gz validate --sensitivity --explain "src/gzkit/credentials/**"` | Returns classification verdict | Pending |
| Schema field deployed | `python -c` import schemas, assert `sensitivity` enum present | Field present in both adr.json and obpi.json | Pending |
| Surface registry deployed | `test -f data/security_surfaces.json` + jq category count | ≥9 categories | Pending |
| Audit OR predicate present | grep `_requires_security_review_attestation` in adr_audit.py | Function defined and ORed | Pending |
| Walkthrough extension present | grep walkthrough in obpi.py | Walkthrough fires for `sensitivity: security` | Pending |
| ARB canonical slot reserved | grep `arb-step-security` in arb/validator.py | Slot reserved | Pending |
| Rule file canon | `test -f .gzkit/rules/security-sensitivity.md` | Exists, version-marked | Pending |
| AGENTS.md matrix present | grep "Lane & Kind & Sensitivity Attestation Matrix" AGENTS.md | Section exists | Pending |
| Scorecard entry present | grep security-sensitivity in advisory-rules-audit.md | Mechanical entry | Pending |
| Governance audit clean | `uv run gz cli audit` | passed | Pending |
| Docs build clean | `uv run mkdocs build -q` | exit 0 | Pending |

## Risk Focus

- **Registry-staleness risk** (negative consequence #2): registry must contain enough categories to provide true-positive signal. Verify ≥9 categories.
- **Schema migration burden** (negative consequence #3): ~150 existing briefs must validate as `sensitivity: null` — covered by `gz validate --sensitivity` reporting no false-positive escapes across 587 briefs.
- **Toolchain feature ADR forcing function** (negative consequence #5): the canonical security-scan slot must be reserved-but-empty until pool.agentic-security-review promotes; verify slot is named only.
- **Self-bootstrapping registry governance** (negative consequence #8): the registry's first commit cannot validate against its own rule. Verify the rule file documents this bootstrap exception.

## Findings Placeholder

Populated in `AUDIT.md`.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `AUDIT.md`.
- ADR lifecycle transitions to `Validated` after receipt emission.
- No edits to accepted ADR prose; hygiene via follow-up ADR if required.

## Attestation Placeholder

Operator's verbal `attest completed` ack relayed via agent under `gz adr audit-begin/audit-end` co-presence ceremony.
