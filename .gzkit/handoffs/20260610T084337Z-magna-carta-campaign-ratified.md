---
mode: CREATE
adr_id: ADR-0.0.69
branch: main
timestamp: "2026-06-10T08:43:37Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260609T232527Z-0.0.68-validated-ln-sunset-ratified.md
---

<!-- Handoff document for ADR-0.0.69 — created by claude-code at 2026-06-10T08:43:37Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

**Magna Carta subordination (new, this session):** this handoff is CONTINUITY
ONLY. The authority on what gets pulled next is the Build-to-1.0 Campaign
(`docs/governance/build-to-1.0-campaign-2026-06-10.md`, Status: ACTIVE — Magna
Carta), surfaced as the first section of every session-orientation digest. If
this handoff and the campaign ever disagree on sequencing, **the campaign
wins** — note the variance and reconcile the campaign, not this file.

## Current State Summary

This session ran the "Fabled" evaluation of gzkit and ended with a ratified
constitutional plan. In order:

1. **Evaluation delivered** (in-chat): four-dimension sweep (architecture,
   governance corpus, tests, product surface), validator load-bearing audit
   (67 scopes ranked by ledger/git evidence), pool ranking (139 live items).
2. **Operator redirected to completion-before-reduction**: build gzkit out
   fully as found, as 1.0; reductive decisions wait for working proof. The
   audits became frozen baselines (campaign Appendices A/B), not action lists.
3. **Build-to-1.0 Campaign authored, ratified, elevated to Magna Carta** —
   it subsumes ALL prior plans (restore-health, ultraplan-brief, convergence
   roadmap — each carries a supersession banner), homes all 37 open GHIs,
   defines GHI-emergence discipline, and carries four operator rulings
   verbatim (ratification, elevation, propellants refinement, CMS amendment).
4. **CMS moved to near-top (Phase B)** by operator amendment; phases
   renumbered A–I with full cross-reference sweep.
5. **Campaign reconciled against the runtime**: A.1 (OBPI-0.0.69-02)
   checked off as `attested_completed`; B.1 baseline corrected to 13/19;
   ADR-0.0.65 seam named (deliberately NOT closed in Phase A; disposition
   lands with C.4 MOTD absorption).
6. All work committed and pushed; `gz git-sync --apply` clean
   (ahead=0 behind=0, HEAD `0faab2f8`).

Campaign burn-down at handoff time: **1/26 items done; topmost unchecked is
A.2 (OBPI-0.0.69-03, closeout-proof derived view + gate repoint).**

## Important Context

- **A concurrent session was active in this same working directory all
  session** — it landed OBPI-0.0.69-01/-02 and raced this session on two
  pushes (ref-lock) and one commit (forbid-pytest "files modified" was its
  concurrent ledger writes, not a real finding). Until the locks→branches
  migration lands, expect shared-worktree races; never bypass the hooks over
  them (Never #6) — queued commits ride the next green push automatically.
- **AGENTS.md is never direct-edited.** Two invariant-tier Magna Carta
  entries sit in `.gzkit/corpus/AGENTS.md.jsonl` awaiting Phase B.3
  deterministic playback (render them as ONE coherent steering-vs-propulsion
  rule). The Architectural Boundaries 1–2 amendment (full-pool override)
  lands the same way — also B.3.
- **The Magna Carta steers; the spine propels** (operator refinement,
  verbatim in the campaign header): ADR, OBPI, and GHI repair remain the
  primary propellants; the campaign only governs what is pulled next.
- The campaign checklist IS the workplan until MOTD ships (Phase C).
  Checklist updates with observed evidence are routine; amendments (scope or
  phase changes) require operator ratification recorded verbatim in place.
- Orientation (`scripts/session_orientation.py`) now renders the campaign as
  the FIRST section of every SessionStart digest (`collect_campaign`, tested
  in `tests/scripts/test_session_orientation.py`, 26/26 OK).

## Decisions Made

- **Decision:** Completion before reduction — build gzkit as found to 1.0,
  THEN cull/optimize.
  **Rationale (operator verbatim):** "where it is redundant, I want to know
  after it is proven; where it is dead/hollow, let an implementation show
  that; where it works, let working proof speak."
  **Alternatives rejected:** governance plateau/freeze; validator probation;
  pool culling to ~20 (all proposed by the evaluation, all deferred to
  Phase I with today's audits as baselines).
- **Decision:** Campaign = Magna Carta; subsumes all prior plans; addresses
  all GHIs; emergence discipline for new GHIs.
  **Rationale:** one canonical plan kills the partial-course-correction seam
  problem ("a model never fully co-owns the project").
  **Alternatives rejected:** keeping restore-health active alongside the
  campaign (violates Operating Rule 1: one active plan).
- **Decision:** CMS (ADR-0.0.37) to near-top — Phase B, before MOTD.
  **Rationale (operator verbatim):** "we don't direct edit AGENTS.md. the
  CMS system must be prioritized as a near-top priority."
  **Alternatives rejected:** original sequencing (CMS inside the Phase D/E
  burn-down).
- **Decision:** Scope rulings — full pool build-out (139 items to terminal
  disposition); Canon Foundation booked into 1.0; done-bar = Validated or
  operator-parked; in-flight first, then (amended) CMS, then MOTD.
- **Decision:** ADR-0.0.65 is deliberately NOT closed in Phase A; its
  terminal disposition lands with C.4 (MOTD absorbs handoff system).
  **Rationale:** completing it standalone would fork the system C.4
  consolidates.

## Immediate Next Steps

ADVISORY ONLY — and subordinate to the Magna Carta: these simply restate the
campaign's topmost unchecked items. Present to the operator; execute only on
authorization, through the governed path (OBPI pipeline; ceremony formula:
runtime `--from` stage state + narrator dispatch + verbatim template render).

1. **A.2 — OBPI-0.0.69-03** (closeout-proof derived view + gate repoint) via
   `uv run gz obpi pipeline OBPI-0.0.69-03` after plan approval.
2. **A.3 — OBPI-0.0.69-04** (retire `ln:` surface; supersedes #599).
3. **A.4 — ADR-0.0.69 closeout ceremony → Validated** (gz-adr-closeout-
   ceremony; unblocks A.5).
4. **A.5 — ADR-0.0.41 closeout** (2/5 → terminal, or operator-parks citing
   the 0.0.67 precedent).
5. Then **Phase B.1 — ADR-0.0.37 build-out** (13/19 → terminal; the CMS
   marquee; closes #519 via B.2).

## Pending Work / Open Loops

- **#519** remains the sole open `emergency` — cured by Phase B.2 (registry-
  projected <15k surface, GHI #533).
- **Phase B.3 playback**: two queued Magna Carta corpus entries + the
  Architectural Boundaries 1–2 amendment must land in rendered AGENTS.md via
  deterministic playback (never direct edit).
- **Pool-hygiene defects** (from the Appendix B baseline): status-drift on
  `ADR-pool.obpi-req-taxonomy-scope-fence`, 11 pool files missing `status:`
  frontmatter, 4 empty Intent sections — homed at G.3.
- **Locks→branches migration** (restore-health §13.7, carried into campaign
  Cadence): two shared-worktree races today are live evidence of need.
- GHI register snapshot (37 open, homed) regenerates at next triage; never
  hand-curate counts.

## Verification Checklist

- [ ] `git branch --show-current` → `main`; `git log -1` at or past `0faab2f8`
- [ ] `uv run gz git-sync` (dry-run) → ahead=0 behind=0, dirty=False
- [ ] `uv run python scripts/session_orientation.py` → first section is
      "## Active campaign — Magna Carta" with current burn-down
- [ ] `uv run gz adr report ADR-0.0.69` → 02 `attested_completed`; check
      whether 03/04 advanced since this handoff (concurrent session!)
- [ ] `uv run gz validate --insights-shape` → green
- [ ] `uv run -m unittest tests.scripts.test_session_orientation -q` → OK

## Evidence / Artifacts

- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — the Magna Carta
  (ACTIVE; rulings verbatim; phases A–I; GHI register; Appendices A/B
  baselines)
- `docs/governance/return-to-health-plan-2026-05-30.md` — superseded banner
- `ultraplan-brief.md`, `docs/design/restore-health-convergence-roadmap.md`
  — superseded banners
- `scripts/session_orientation.py` + `tests/scripts/test_session_orientation.py`
  — campaign-first orientation (TDD RED→GREEN, 26 tests)
- `.gzkit/corpus/AGENTS.md.jsonl` — two queued Magna Carta entries
- `.gzkit/insights/agent-insights.jsonl` — three Rule-11 records this session
  (completion-before-reduction; propellants refinement; CMS amendment)
- Commits: `ae304962` (ratification), `766201b5` (elevation), `e5e027ec`
  (refinement), `3525c603` (CMS amendment), `0faab2f8` (runtime reconcile)
