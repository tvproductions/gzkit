# AUDIT PLAN (Gate-5) — ADR-0.0.65

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.65-handoff-system-consolidation |
| ADR Title | Handoff System Consolidation and CLI Surface |
| SemVer | 0.0.65 (foundation, heavy lane) |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation |
| Audit Date | 2026-07-15 |
| Auditor(s) | pipeline-orchestrator (driver) + spec-reviewer + quality-reviewer (independent) |

## Purpose

Confirm ADR-0.0.65 implementation is complete and its thesis holds against the
running system, moving the ADR COMPLETED → VALIDATED. The ADR was born from a
2026-05-29 audit (GHI #529) that found the handoff system "half-wired": the
documented surface, the code, and the runtime disagreed about where handoffs
live and whether an executable authoring API existed.

**Audit Trigger:** Gate-5 validation (post-closeout, pre-VALIDATED).

## Scope & Inputs — the ADR's claims

The Decision commits to consolidating the handoff system to a single source of
truth across doctrine, skill, code, and CLI. Extracted claims:

- **C1 — Canonical write location resolved.** `.gzkit/handoffs/` is the single
  write surface; 24 per-ADR handoffs migrated; `gz-session-handoff/SKILL.md`
  amended off `{ADR-package}/handoffs/`.
- **C2 — Real programmatic API.** `create_handoff` / `scaffold_handoff` /
  `list_handoffs` / `resume_handoff` / `load_handoff_chain` shipped as real
  importable code in `src/gzkit/handoff_api.py`, wrapping `handoff_validation.py`
  so CREATE runs the validation gate mechanically.
- **C3 — `gz handoff` CLI verb.** `create` / `resume` / `list` subcommands route
  authoring through the validation gate; manpage + behave coverage.
- **C4 — Orientation single-location scan.** `_candidate_handoff_dirs()`
  collapsed to a single `.gzkit/handoffs/` scan; GHI #529 dual-scan workaround
  deleted.
- **C5 — `gz handoff archive` retention.** Move-not-delete verb honoring three
  guards: migration-floor, `continues_from:`-chain integrity, lock-handoff
  coupling. Closes GHI #585.

## Planned Checks

| Check | Command / Method | Expected Signal | Status |
|-------|------------------|-----------------|--------|
| Ledger proof (L2) | `gz adr audit-check ADR-0.0.65` | All 5 OBPIs PASS | ✓ (proofs/audit-check.txt) |
| Gate status | `gz adr status ADR-0.0.65 --json` | Gates 1–5 pass | ✓ |
| Heavy gates | `gz gates --adr ADR-0.0.65` | pass | ✓ (proofs/gates.txt) |
| Bound fidelity gate (Step 3) | `gz adr fidelity ADR-0.0.65-...` | 2/2 pass, exit 0 | ✓ (proofs/fidelity.txt) |
| Governance CLI audit | `gz cli audit` | pass, 129/129 covered | ✓ |
| C2/C3 — verb + API exist | `gz handoff --help`; `ls src/gzkit/handoff_api.py` | 4 subcommands; module present | ✓ |
| C1/C4 — split-brain closed | quality-reviewer trace | write/read/API/CLI agree on `.gzkit/handoffs/` | (independent) |
| REQ coverage integrity | spec-reviewer trace | 6 advisory-uncovered REQs are SUPPORT/FENCE, not BEHAVIOR gaps | (independent) |

## Risk Focus

1. **Fidelity-assertion staleness.** The first assertion is self-labeled `WEAK`
   and its prose describes the `gz handoff` verb as "unbuilt (Proposed)" — but
   OBPI-03 shipped the verb. The assertion passes (it tests the lock-coupling
   guard) but does not exercise the now-built thesis. Non-blocking; flagged for
   remediation.
2. **Advisory-uncovered REQs (6).** Must confirm each is SUPPORT or
   STRUCTURAL-FENCE (proof-channel-exempt), not a silently-uncovered BEHAVIOR.
3. **Split-brain relocation risk.** The original defect was a read/write split.
   Confirm it is genuinely closed, not merely moved.
