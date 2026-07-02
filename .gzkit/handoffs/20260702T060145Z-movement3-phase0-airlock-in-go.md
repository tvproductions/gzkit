---
mode: CREATE
adr_id: ADR-0.0.9
branch: main
timestamp: "2026-07-02T06:01:45Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: 809f3f32
session_id:
continues_from: .gzkit/handoffs/20260701T004433Z-floor-cluster-ghi-burndown.md
---

<!-- Handoff document for ADR-0.0.9 — created by claude-code at 2026-07-02T06:01:45Z.
     Scope note: this is Magna Carta Movement III Phase 0 (airlock-in) campaign
     work, NOT ADR-0.0.9 OBPI work. It is homed under ADR-0.0.9 (state-doctrine)
     because the frontmatter model requires an ADR-X.Y.Z id (pool ids are
     rejected) and Phase 1's KEEL — promoting ADR-pool.obpi-state-machine — exists
     precisely to LOCK state doctrine (Arch-Boundary §12.3). No feature ADR exists
     yet: the first is authored in Phase 1. No OBPI lock was held this session
     (Phase 0 is pre-ADR, judgment-grade by hand), so the lock-coupling frontmatter
     keys are intentionally empty. last_commit_sha records the Phase 0 sync commit
     HEAD for traceability, not a lock conclusion. -->

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

## Current State Summary

Two operator-authorized fronts advanced this session, both landed clean on
`origin/main` (tree clean, 0 ahead / 0 behind at handoff time; HEAD `809f3f32`).

**Front 1 — GHI #519 (emergency) CLOSED as relieved.** The last `emergency`-labeled
GHI. Re-sensed against current repo truth: its acute cause (258K-window Codex
collapse / over-cap silent truncation of the shared root `AGENTS.md`) was already
relieved by prior sessions. Root `AGENTS.md` renders to 31,569 B, under Codex's
32,768 B `project_doc_max_bytes` cap; the budget in
`data/instructions_files_budget.json` is 31,800 (under cap), guarded by a
behavioral test with a live negative control
(`tests/governance/test_agents_md_map_doctrine.py::_budget_within_codex_cap`
rejects the old over-cap 33000). `gz validate --instructions-files-budget` is
exit 0. Posted an evidence-grounded closing comment and closed #519; the durable
<15k shrink residual is tracked under GHI #533 + ADR-0.0.37 (campaign §2a). No
code change — pure disposition.

**Front 2 — Magna Carta Movement III Phase 0 (airlock-in) EXECUTED.** Operator
authorized "take on Movement III Phase 0." The Phase 0 → Phase 1 gate is now
**OPEN**. The three pre-flight deliverables (seam-map, volume, falsifiers) were
authored 2026-06-30 and RE-SENSED current this session (no blast-radius shift);
the fourth deliverable — the go/no-go record — was written: GO (keel-up). Flipped
`docs/governance/airlock-in-constellation-2026-06-30.md` Status from
"work-start deferred / gate CLOSED" to "Phase 0 EXECUTED — GO attested; gate OPEN"
and appended a symmetric GO record to the insights channel (mirroring the
2026-06-30 NO-GO). **Boundary held: nothing authored or promoted.** Both changes
synced as commit `809f3f32` (`Task: TASK-gz-git-sync`).

## Important Context

- **Two-valued "go" (load-bearing).** In this constellation "go" means either
  (1) record the Phase 0 go/no-go and OPEN the gate, or (2) START Phase 1 (author
  or promote the KEEL ADR). The operator authorized (1). Their standing 2026-06-30
  distinction — *"if go means start work, I am not ready to"* — plus Behavior Rule
  Always #17 mean Phase 1 ADR authoring awaits an EXPLICIT go-to-work directive.
  Do not read "gate OPEN" as "Phase 1 authorized to begin now."
- **The campaign RULES pull order; it is Magna Carta.** Work the topmost unchecked
  item whose gate is met, through its governed path. Movement III is the topmost
  forward front; Phases 1-3 are sequential keel-up (corpus is the one
  parallel-early node). Handoffs advise; the campaign governs.
- **Arch-Boundary §12.3 is the sequence lock.** "Do not build the graph engine
  (HULL, Phase 2) without locking state doctrine first (KEEL, Phase 1)." The KEEL's
  runtime invariant monitor IS the lock. HULL before KEEL is a pre-registered
  sequence falsifier.
- **`foundation` enum is still live** at `src/gzkit/schemas/adr.json:36`. The KEEL
  and all constellation ADRs promote with `--kind feature` (mechanical abolition of
  `foundation` is Movement IV, not yet done). Do not assume the enum is gone.
- **STDLIB-FIRST departure owed.** `tree-sitter` + `networkx` (the HULL floor) is a
  named departure that MUST be attested in the HULL feature ADR (deterministic
  multi-surface extraction + topo-sort / cycle-detection stdlib cannot supply).
  `graspologic` is stripped (not 3.13-installable; parked as a future L3-advisory
  option in the airlock-in doc).
- **§5 enforcement-claim rule binds the HATCH.** The HATCH's "refuses GO on an
  un-accounted seam" claim REQUIRES a live negative control registered through
  Movement I's enforcement-claim surface (ADR-0.0.74) — no NC means facade means
  rejected.
- **Go/no-go channel resolution.** There is no `gz` go/no-go verb and Phase 0 is
  pre-ADR, so "record to the ledger" resolves for this by-hand gate to the insights
  provenance channel + the doc Status — the same channel the 2026-06-30 NO-GO used.
  Direct main-ledger writes remain forbidden (§ Never #2).

## Decisions Made

- **Decision:** Close GHI #519 as relieved rather than reopen remediation.
  **Rationale:** Re-sense proved the acute emergency is fixed and mechanically
  guarded (behavioral test + negative control + validator green); the residual is
  fully tracked under #533 / ADR-0.0.37 / §2a, so keeping #519 open duplicates a
  tracker. Operator approved the drafted closing comment.
  **Alternatives rejected:** (a) narrow-and-retitle #519 to its residual — risked
  duplicating #533; (b) start the deep <15k cure now — blocked by the #623
  derivation-spine facade and is Movement-III-scale, not a direct fix.
- **Decision:** Record Phase 0 GO and OPEN the gate, but STOP before Phase 1.
  **Rationale:** Operator authorized "Phase 0," not "start Phase 1"; the two-valued
  "go" distinction and Behavior Rule #17 forbid autonomously launching KEEL ADR
  authoring.
  **Alternatives rejected:** proceed straight into promoting
  `ADR-pool.obpi-state-machine` — would have violated the operator's explicit gate
  and the no-unrequested-implementation rule.
- **Decision:** Re-sense the 2026-06-30 seam-map before recording GO.
  **Rationale:** A ratified plan is a Layer-1 snapshot; recording GO against stale
  edges is the observation-completeness failure the airlock exists to prevent. The
  re-sense confirmed all edges current (five pool ADRs present, `foundation` enum
  live, subsumption + Plumb-coupling targets present).
  **Alternatives rejected:** rubber-stamp the two-day-old plan.
- **Decision:** Home this handoff under ADR-0.0.9 with a scope note.
  **Rationale:** Frontmatter requires an ADR-X.Y.Z id; Phase 1's KEEL locks state
  doctrine, of which ADR-0.0.9 is the foundation ADR.
  **Alternatives rejected:** ADR-0.0.74 (enforcement floor — binds only the HATCH's
  NC, less central to Phase 0/1 substance).

## Immediate Next Steps

ADVISORY ONLY — present these for operator review; do not execute without an
explicit go-to-work.

1. **Await the operator's explicit go-to-work for Phase 1.** The Phase 0 → 1 gate
   is OPEN, but Phase 1 start is a separate authorization (two-valued "go").
2. **On go-to-work, begin Phase 1 (KEEL) via the governed path** — promote
   `ADR-pool.obpi-state-machine` → feature (heavy) using `gz-adr-promote`
   (`gz adr promote --kind feature`, since `foundation` is still live). Decompose to
   OBPIs 1:1 against the ADR Feature Checklist.
3. **Scope Phase 1 to the airlock-critical tracer, not the full state machine:**
   Pydantic `State` / `Transition` models (thin `StrEnum` for the closed name-set),
   withdraw/supersede first-class transitions + CLI verbs (closes GHI #348), and the
   runtime invariant monitor. Defer choreography retirement, concurrency caps,
   failure-class taxonomy, event vocabulary to the ADR's later OBPIs.
4. **Enforce the Phase 1 landing falsifier before any Phase 2 (HULL) work:** the
   KEEL monitor MUST refuse a silent `status:` frontmatter drift (GHI #348 class) in
   PRODUCTION config. If it does not, the keystone is unbuilt — NO-GO on Phase 2.
5. **If a different front is chosen instead,** the direct-fixable GHI floor cluster
   remains available (e.g. #650 mx marker-path drift, #532 manpage path typo, #652
   oversized module) as the maintenance engine, no Movement III authorization needed.

## Pending Work / Open Loops

- **Phase 1 (KEEL) — not started.** Gate OPEN; awaits go-to-work. This is the
  topmost forward item.
- **Phase 2 (HULL graph substrate), Phase 3 (HATCH membrane), Phase 4 (RECALL,
  deferred/severable)** — all downstream of Phase 1; each is a new/promoted feature
  ADR. HULL supersedes `artifact-graph-navigation` + `execution-memory-graph` +
  `covers-source-anchors` (preservation falsifier: superseding must keep
  `gz validate --documents` / `--cli-alignment` green).
- **GHI #348** (silent node-drift class) — closes when KEEL withdraw/supersede
  transitions land.
- **#623** (ADR-0.0.37 derivation-spine facade, OBPIs 02/03/21/22 repudiated) —
  blocks the deep <15k AGENTS.md shrink (the #519 residual / §2a single-router
  bootstrap). Not on the Phase 1 critical path.
- **41 open GHIs, 0 emergency-labeled** after this session's #519 close.

## Verification Checklist

- [ ] Branch matches: `git branch --show-current` returns `main`
- [ ] Tree clean and synced: `git status -s` empty; `git rev-list --left-right --count origin/main...main` is `0	0`
- [ ] Phase 0 gate state: `docs/governance/airlock-in-constellation-2026-06-30.md` Status reads "Phase 0 EXECUTED — GO attested; gate OPEN"
- [ ] GO record present: `grep 'Phase 0' .gzkit/insights/agent-insights.jsonl` shows the 2026-07-02 GO record
- [ ] #519 closed: `gh issue view 519 --json state` returns CLOSED
- [ ] Budget guard green: `uv run gz validate --instructions-files-budget` exit 0
- [ ] `foundation` enum still live (promote --kind feature): `grep '"foundation"' src/gzkit/schemas/adr.json`
- [ ] Nothing authored/promoted for Phase 1: no new `docs/design/adr/**/ADR-0.*obpi-state-machine*` package exists

## Evidence / Artifacts

- `docs/governance/airlock-in-constellation-2026-06-30.md` — Phase 0 record; Status flipped to gate OPEN with the re-sense confirmation
- `.gzkit/insights/agent-insights.jsonl` — appended 2026-07-02 GO record (mirrors the 2026-06-30 NO-GO)
- `docs/governance/build-to-1.0-campaign-2026-06-30.md` — Magna Carta; Movement III §7 is the pull order
- `docs/design/adr/pool/ADR-pool.obpi-state-machine.md` — Phase 1 KEEL promotion target
- `src/gzkit/schemas/adr.json` — `foundation` enum still live at line 36
- `data/instructions_files_budget.json` — AGENTS.md budget 31,800, under Codex cap (the #519 guard)
- `tests/governance/test_agents_md_map_doctrine.py` — the Codex-cap behavioral test with negative control
- `.gzkit/handoffs/20260701T004433Z-floor-cluster-ghi-burndown.md` — predecessor handoff (this session resumed from its orientation)

## Environment State

Python 3.13 via uv; branch `main`; HEAD `809f3f32`. No OBPI lock held. No
in-progress pipeline. Codex/GPT-class agents read the shared root `AGENTS.md`
(31,569 B, under the 32,768 B cap) — a fresh-clone Codex run no longer collapses
on the governance surface at boot.
