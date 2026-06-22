---
mode: CREATE
adr_id: ADR-0.0.74
obpi_id: OBPI-0.0.74-03-mx-gate5-invariants
branch: main
timestamp: "2026-06-22T12:15:12Z"
agent: claude-code
session_id: main-2026-06-22
continues_from: .gzkit/handoffs/20260622T094318Z-adr-0-0-74-post-obpi-12-next-mx-kernel.md
last_commit_sha: f2b1f2a7128a9fa733723fc88ccf358028c658f0
---

# Session Handoff — OBPI-0.0.74-03 complete + central-config refinement

## Current State Summary

Two units of work landed this session, both synced to `main` (tree clean, even
with origin):

1. **OBPI-0.0.74-03-mx-gate5-invariants** ran the full gz-obpi-pipeline
   (Stages 1-5) and is operator-attested complete. The never-relax floor now
   lives as a five-member `GATE5_INVARIANTS` frozenset at
   `src/gzkit/mx/invariants.py` (grader-gaming the fifth member);
   `src/gzkit/mx/checkpoint.py` imports the canonical constant instead of
   defining a local four-member set; `tests/mx/test_gate5_invariants.py` adds
   8 tests proving the leveled checkpoint pins every member to CRITICAL
   (`Route.AOG_MX_HANGAR`) in or out of the hangar. Lock released, markers
   cleared, completion handoff authored.

2. **Central-config pool ADR refinement.** Off an operator design observation
   (the `GATE5_INVARIANTS` constant as evidence for needing strong central
   config like airlineops), the two-tier distinction was captured into
   `docs/design/adr/pool/ADR-pool.central-config-airlineops-pattern.md` and a
   fourth promotion trigger was added.

## Important Context

- ADR-0.0.74 § Decision item 3 deliberately makes the never-relax floor "a code
  constant (NOT config)" for tamper-resistance (§ Risks #5 skeleton-key
  containment). This is the key tension behind the central-config refinement:
  airlineops central config is mutable (layered `defaults to settings to local`
  deep-merge, no programmatic immutability), so relocating an invariant-tier
  value into it naively would re-open the surface ADR-0.0.74 closed.
- The central-config gap is already tracked: the pool ADR plus the operator
  insight from 2026-05-11. The ADR-0.0.32 closeout gate (the named park gate)
  is complete, so the pool ADR is promotable on operator word — but the active
  Build-to-1.0 campaign currently lists GHI #615 (vocabulary config-first
  exorcism) as topmost, so promotion would be a campaign resequencing the
  operator ratifies, not an agent decision.
- Pipeline friction worth remembering for the next MX OBPI: the completion
  handoff `timestamp:` frontmatter must be a quoted string, or YAML parses it
  as a datetime whose `str()` uses a space separator and the lock-release
  matcher's string comparison rejects it. Insight records in
  `.gzkit/insights/agent-insights.jsonl` require a `ts` field and a list-typed
  `evidence` field.

## Decisions Made

- Authored `GATE5_INVARIANTS` in a dedicated `invariants.py` rather than
  extending the local definition in `checkpoint.py` — the brief required a
  single canonical home for the never-relax list. Rejected alternative: add
  grader-gaming in place inside `checkpoint.py` (would keep two would-be homes).
- Stage-5 allowlist drift (REQ tests import `gzkit.mx.marker` and the
  `gzkit.mx` package for the active-hangar fixture) was resolved by amending
  the brief allowlist to declare `src/gzkit/mx/__init__.py` and
  `src/gzkit/mx/marker.py` as test-fixture reads — matching the identical
  OBPI-0.0.74-02 precedent. Rejected alternative: an `--accept-*` override
  (the brief, not the code, was the artifact to adjust).
- Central-config refinement captured as a pool-ADR edit (not a promotion, not a
  new GHI) per operator routing choice — sharpens the tracked artifact without
  jumping the campaign queue.

## Immediate Next Steps

1. Confirm green floor: run `uv run gz check` and verify it passes before
   pulling the next campaign item.
2. Consult the Build-to-1.0 campaign
   (`docs/governance/build-to-1.0-campaign-2026-06-20.md`) for the topmost
   unchecked item whose gate is met; the campaign governs the pull order.
3. Likely next MX work under ADR-0.0.74: OBPI-0.0.74-09 (gates-as-sensors —
   migrate live guards to emit `GZ_<LEVEL>` through `checkpoint.resolve`, retire
   the two hand-set staging flags) and OBPI-0.0.74-13 (proxy-reality detector
   that makes grader-gaming's floor membership live).
4. Present advised steps to the operator and obtain authorization before
   executing any of them.

## Pending Work / Open Loops

- ADR-0.0.74 (MX Mode Maintenance Hangar) remains in progress; OBPI-03 is one
  of 13 OBPIs. Remaining MX kernel + hardening work targets release 0.29.0.
- `ADR-pool.central-config-airlineops-pattern` is promotable but parked behind
  the campaign queue; promotion is an operator-ratified resequencing decision.
- Standing rendition-floor warning observed during the run: committed
  `AGENTS.md/claude` rendition omits the `corpus-tty` invariant-tier entry
  (staged-warn, not blocking). Not addressed this session; flagged for whoever
  owns the next rendition recompose.

## Verification Checklist

- `uv run gz check` — full quality gate (lint, format, test, typecheck).
- `uv run gz obpi status OBPI-0.0.74-03-mx-gate5-invariants` — confirm
  `ATTESTED COMPLETED` against the ledger (Layer-2), not the brief frontmatter.
- `uv run gz obpi lock list` — confirm no stale lock for OBPI-0.0.74-03.
- `uv run -m unittest tests.mx.test_gate5_invariants -v` — 8 tests pass.
- `git status -sb` — confirm tree clean and even with origin/main.

## Evidence / Artifacts

- `src/gzkit/mx/invariants.py` (new — the five-member `GATE5_INVARIANTS` constant)
- `src/gzkit/mx/checkpoint.py` (modified — imports the canonical constant)
- `tests/mx/test_gate5_invariants.py` (new — 8 tests)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-03-mx-gate5-invariants.md` (completed brief)
- `docs/design/adr/pool/ADR-pool.central-config-airlineops-pattern.md` (two-tier refinement + fourth promotion trigger)
- `.gzkit/handoffs/OBPI-0.0.74-03-mx-gate5-invariants-complete.md` (OBPI completion handoff)
- `.gzkit/insights/agent-insights.jsonl` (improvement insight for the allowlist correction)
