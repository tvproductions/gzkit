# AUDIT PLAN (Gate-5) — ADR-0.0.30 Complexity Authoring Guidance

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.30-complexity-authoring-guidance |
| ADR Title | Complexity Authoring Guidance |
| SemVer | 0.0.30 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ |
| Audit Date | 2026-05-10 |
| Auditor(s) | Agent (gz-adr-audit skill, opus-tier) under operator g0 |

## Purpose

Confirm ADR-0.0.30 implementation is complete by validating its claims with
reproducible CLI evidence. ADR-0.0.30 is the fourth and closing foundation in
the complexity-doctrine cluster (0.0.27 corpus → 0.0.28 thresholds → 0.0.29
trigger-time advisor → 0.0.30 upstream-prevention authoring guidance) and the
loop-closer with ADR-0.0.19's pre-execution reasoning-walkthrough doctrine.

**Audit Trigger:** Operator-invoked `/gz-adr-audit 0.0.30` after all five
linked OBPIs reached `attested_completed` status (2026-05-09 / 2026-05-10).
This is a heavy-lane / foundation-kind ADR; brief-level Gate 5 has stacked
across all five OBPIs (per ADR-0.0.18). The ADR-level validated receipt is
the final ceremony.

## Scope & Inputs

**Primary contract surfaces (delivered by this ADR):**

- `gz complexity guide <path>` — ad-hoc authoring-time review CLI verb
  (default in-line hint prose; `--json` emits canonical `AuthoringHint`)
- `gz complexity guide --server` — JSON-over-stdio LSP-style protocol
  server (initialize / analyze / shutdown envelopes, Content-Length framing)
- `complexity-guide` skill at `.gzkit/skills/complexity-guide/SKILL.md`
  with three vendor mirrors (`.claude/`, `.agents/`, `.github/skills/`)
- `gz justify <OBPI>` — augmented to emit `### Authoring-time complexity
  hints` section when the OBPI's allowed-paths include `.py` files
- `AuthoringHint` Pydantic model + projection from `AdvisorDiagnosis`
  (`src/gzkit/complexity/authoring/hint.py`, `engine.py`)
- JSON Schemas: `src/gzkit/schemas/authoring_hint.json`,
  `src/gzkit/schemas/authoring_guide_protocol.json`
- Editor-author specification: `docs/governance/complexity/authoring-guide-protocol.md`
- Manpage: `docs/user/manpages/complexity-guide.md`

**OBPI traceability (5/5 attested_completed; 33/33 REQs covered):**

| OBPI | Subject | REQs |
|------|---------|------|
| 01 | `gz complexity guide` CLI verb | 6/6 |
| 02 | `complexity-guide` skill (vendor-mirrored) | 6/6 |
| 03 | Authoring hint engine + AuthoringHint projection | 8/8 |
| 04 | Editor/IDE protocol contract (`--server` + spec doc) | 7/7 |
| 05 | `gz justify` integration | 6/6 |

**Cluster context (consumed, not edited):**

- ADR-0.0.27 corpus — distilled-characteristics document
- ADR-0.0.28 thresholds — `ThresholdTable` + `complexity-thresholds.json`
- ADR-0.0.29 advisor — `AdvisorDiagnosis` + `DiagnosisEngine`
- ADR-0.0.19 — pre-execution reasoning walkthrough (justify scaffold)

## Planned Checks

| # | Check | Command / Method | Expected Signal | Status |
|---|-------|------------------|-----------------|--------|
| C1 | Ledger proof complete | `uv run gz adr audit-check ADR-0.0.30` | PASS, all 5 OBPIs completed, 33/33 REQs covered | Pending |
| C2 | Demo: CLI help surface | `uv run gz complexity guide --help` | exit 0; help text documents flags + exit-code map (no exit 3) | Pending |
| C3 | Demo: CLI prose form on real source | `uv run gz complexity guide src/gzkit/commands/validate_cmd.py` | exit 0; one block per advise-band crossing with Archetype/Band/Guidance/Move | Pending |
| C4 | Demo: CLI `--json` mode | `uv run gz complexity guide src/gzkit/commands/validate_cmd.py --json` | exit 0; valid JSON array of AuthoringHint records with canonical fields | Pending |
| C5 | Demo: Skill vendor-mirror parity | `diff -q` of `.gzkit/`, `.claude/`, `.agents/`, `.github/` skill copies | byte-identical across mirrors | Pending |
| C6 | Demo: Editor protocol handshake | `gz complexity guide --server` driven by Content-Length-framed initialize + shutdown | initialize → version 1.0 + capabilities; shutdown → status ok | Pending |
| C7 | Demo: `gz justify` integration | `uv run gz justify OBPI-0.0.30-05` | exit 0; output contains `### Authoring-time complexity hints` section with hint blocks for the OBPI's `.py` allowed-paths | Pending |
| C8 | Spec + schema artifacts present | `ls` of `docs/governance/complexity/authoring-guide-protocol.md`, `src/gzkit/schemas/authoring_hint.json`, `src/gzkit/schemas/authoring_guide_protocol.json`, `docs/user/manpages/complexity-guide.md` | all four files exist | Pending |

## Layer 2 Trust Notes

Per `gz-adr-audit` SKILL.md § Layer 2 Trust Model, this audit consumes Layer 1
proof (ledger entries from `gz adr audit-check`). All five OBPIs report
`attested_completed`; the ledger entries are <2 days old (briefs completed
2026-05-09 and 2026-05-10, audit ran 2026-05-10) and well within the 7-day
freshness threshold. Re-running the full unittest / mkdocs / heavy-gate suite
would duplicate the receipts already booked into each brief's evidence section
(arb-step-unittest-d98f3e4f724e4ba6b3846a3c7e3acfb0 across 4648 tests, plus
the OBPI-scoped receipts named in each brief). **"Ledger proof verified."**

## Risk Focus

| Risk | Mitigation |
|------|------------|
| Authoring guidance silently broken — emits no hints when it should | Demo C3 + C4 against `validate_cmd.py` (a known advise-band-rich file per OBPI-01 demo block); confirms 7 hints emitted with canonical schema. |
| Vendor mirrors drift after sync | Demo C5 explicit `diff -q` against all three mirrors. |
| Protocol server doesn't honor Content-Length framing | Demo C6 drives the server with proper LSP-style framing and confirms initialize + shutdown round-trip. |
| Justify integration silent-skip path masks real failure | Verified at OBPI-05 brief level (4/4 BDD scenarios pass for hits + skip + engine-failure paths); demo C7 exercises the live "hits" path. |
| Cluster forward-reference (ADR-0.0.19 ↔ ADR-0.0.30) not closed | Demo C7 proves the integration emits the live section header; the additive amendment to `gz-justify` skill is checked at OBPI-05's REQ-05 (skill-version bump + structure preservation). |

## Findings Placeholder

Captured in `AUDIT.md` — no detailed findings here beyond structural notes.

## Acceptance Criteria

- All eight planned checks executed with proofs in `audit/proofs/`.
- Layer 1 verification skipped per Layer 2 trust model (ledger proof complete,
  fresh, and unsuspected).
- Feature Demonstration section in `AUDIT.md` covers all six capabilities
  with live command output and value summaries.
- No edits to ADR prose; any drift is filed as a follow-up GHI.
- Operator verbal `accept audit` / `verify audit` collected before the
  validated receipt is emitted (Step 8 ceremony).

## Attestation Placeholder

Operator's verbal ack will be collected in the audit-end turn; agent-relayed
emit-receipt will quote the operator verbatim with concrete enrichment, then
audit-end + `gz adr report ADR-0.0.30` will confirm `Lifecycle: Validated`.
