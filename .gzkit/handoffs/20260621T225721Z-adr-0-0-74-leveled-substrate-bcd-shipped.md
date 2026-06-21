---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-21T22:57:21Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260621T205805Z-adr-0-0-74-leveled-substrate-phase-a.md
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-21T22:57:21Z -->

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

ADR-0.0.74 (MX Mode — Maintenance Hangar; Draft, foundation, heavy) — the leveled
`GZ_<LEVEL>` substrate amendment is **fully DESIGNED, DECOMPOSED, evaluated, committed,
and pushed**. This session took the Phase-A predecessor handoff through Phases B, C,
and D and synced. HEAD is `b56077d3` on `origin/main`; ahead=0 behind=0; working tree
clean.

What landed this session (commit `b56077d3`, 13 files, +1454/-191):
- **Phase B (OBPI decomposition):** authored 4 new briefs — OBPI-11 `mx-gz-level-vocabulary`,
  OBPI-12 `mx-gates-as-sensors`, OBPI-13 `mx-proxy-reality-detector`, OBPI-14 `mx-hardening`;
  reshaped 3 DRAFT briefs to leveled framing — OBPI-03 (grader-gaming as 5th gate5_invariants
  member), OBPI-05 (re-emit levels + live exit negative-control), OBPI-09 (effective
  `GZ_<LEVEL>`, not hand-set bool). Checklist↔brief **1:1 restored**; `gz adr status ADR-0.0.74`
  shows **2/13** (OBPI-01/02 attested_completed; 03-09 and 11-14 DRAFT/pending; item 10
  withdrawn-hidden).
- **Phase C (Magna Carta amendment):** `docs/governance/build-to-1.0-campaign-2026-06-20.md`
  §3b ladder amended kernel/syslog 0-7 to Python `logging` + NOTICE=25 (STDLIB-FIRST);
  operator ratified verbatim ("ratified"), recorded in the campaign's § Archive.
- **Phase D (quality gate):** evaluation verdict **GO** — structural 3.85/4.0 (CLI),
  substance 3.35/4.0 (independent persona-dispatched review), every Phase-B OBPI avg >= 3.4,
  no dimension scored 1. Three review findings were FIXED before commit (see Decisions Made).
  Scorecard at `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/EVALUATION_SCORECARD.md`.

Validation green at handoff time: `uv run gz validate` passes all 11 scopes; `gz lint` and
`gz test` passed in the git-sync gate before push.

**The substrate is designed and decomposed, NOT implemented.** No `src/gzkit/mx/levels.py`,
`disposition.py`, `proxy_reality.py`, or `hardening.py` exists yet — those are the briefs'
deliverables. Building them is the next campaign pull.

## Important Context

- **Implementation is the next work, not more design.** Campaign Movement I item 1
  ("ADR-0.0.74 BI#2 built for real") is now decomposed into authored-ready briefs; the
  remaining work is implementing OBPI-03/05/09 (reshaped) and 11-14 (new) as real code under
  `src/gzkit/mx/`. These are contract-bearing heavy OBPIs, so the **`uv run gz obpi pipeline`**
  runtime owns their stage sequencing (verify -> ceremony -> guarded git-sync -> completion),
  not freeform implementation.
- **Implementation dependency order** (read the briefs' Prerequisites/Context for the
  declared edges): OBPI-11 (levels vocabulary) is the foundation; OBPI-12 (disposition
  handler) and OBPI-03 (gate5 floor + grader-gaming) consume it; OBPI-13 (proxy-reality
  detector) makes OBPI-03's grader-gaming membership live (BI#5); OBPI-14 (hardening) consumes
  the leveled checkpoint; OBPI-05 (exit) consumes OBPI-04 (enter, also still DRAFT) plus 11/12.
  OBPI-01 (marker) and OBPI-02 (checkpoint) are the landed honest base.
- **OBPI-01/02 `--authored` FAIL is a known non-defect.** `uv run gz obpi validate --adr
  ADR-0.0.74 --authored` reports 2/14 FAIL — OBPI-01 and 02 only, with "Changed-files audit
  found no modified paths." They are attested_completed; their work is committed (not in the
  working tree), so the live-scope re-audit finds nothing. This is the `--authored` gate
  re-auditing completed briefs, not a brief defect. Do NOT "fix" the completed briefs.
- **The "surface drift" episode resolved itself.** Mid-session, `gz validate` flagged
  `.claude/rules/tests.md`, `.github/instructions/tests.instructions.md`, and `tests/AGENTS.md`
  out of sync. Diagnosis: NOT committed drift at HEAD — transient working-tree corruption from
  an external `.claude/rules` regeneration this session. `uv run gz agent sync control-surfaces`
  repaired the tree back to HEAD's already-correct content (`git diff HEAD` empty after);
  nothing was committed for surfaces. HEAD was always correct. No action needed on resume.
- **REQ-kind tags are lowercase** (`[behavior]`/`[support]`/`[structural-fence]`) across all
  ADR-0.0.74 briefs — matches the sibling convention; the validator regex is case-insensitive
  (`re.IGNORECASE`, `src/gzkit/commands/validate_req_kind.py`). Do not "normalize" to uppercase.
- **The Q&A Transcript section of the ADR is preserved history** (the 2026-06-20 interview,
  still reads 10 binary items). The live Decision/Checklist/BI/Consequences are current. The
  Phase-D pass cleaned the live Consequences of the withdrawn item-10 leak; the Q&A copy is
  intentionally untouched.

## Decisions Made

- **Decision:** Bundle Phase A + B + C + D into one commit (HOLD on committing Phase A alone).
  **Rationale:** committing Phase A alone left a transient 13-listed/9-brief 1:1 gap that count
  validators flag every run; bundling keeps every committed HEAD 1:1-coherent.
  **Alternatives rejected:** commit Phase A immediately (operator chose HOLD).

- **Decision:** Apply the three Phase-D review findings before commit (not defer).
  **Rationale:** the contract's "complete all work fully / coupled-surface coherence" duty
  binds beyond the gate's dim-1 revision trigger; all three were unambiguous misalignments in
  artifacts about to be committed. Findings + fixes: (1) ADR Consequences leaked the withdrawn
  item-10 doc-type taxonomy — Positive #6 rewritten to the leveled-substrate benefit, Negative
  #3's lexical-alignment clauses removed; (2) OBPI-14 REQ-14-02 "blocks a normal release" was
  unwired — added `src/gzkit/commands/patch_release.py` + `closeout.py` to Allowed Paths and
  rewrote the REQ to consult `hardening.normal_release_blocked()` at the real `gz patch release`
  / `gz closeout` site (also fixed a `gz patch-release` -> `gz patch release` verb error); (3)
  OBPI-05 reshape left Discovery as scaffold — declared predecessors OBPI-04/01/02/11/12.
  **Alternatives rejected:** report GO and defer the score-2 polish (gate only mandates dim-1).

- **Decision:** OBPI-13's proxy-reality detector reads the existing ledger repudiation signal
  (`gz obpi repudiate --cause model-induced-fabrication`) rather than adding a new ledger event
  type. **Rationale:** keeps the brief stdlib-first and avoids touching ledger internals (a
  registered security surface that would force `sensitivity: security`). **Alternatives
  rejected:** a new `proxy_reality_*` ledger event type.

- **Decision:** The mid-session surface-drift was handled as repair-back-to-HEAD, no commit.
  **Rationale:** it was transient working-tree corruption, not committed drift; the sync
  restored HEAD's correct content. **Alternatives rejected:** a separate `fix(surfaces)` commit
  (became moot — there was no surface change to commit).

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator, await authorization before acting. -->

1. **Begin implementing the leveled substrate** (the campaign Movement I item 1 build). Start
   with **OBPI-11** (`src/gzkit/mx/levels.py` — the `GZ_<LEVEL>` vocabulary) since 12/03/14 all
   consume it. Run `uv run gz obpi pipeline OBPI-0.0.74-11` (contract-bearing heavy OBPI; the
   runtime owns stage sequencing). Claim the OBPI lock first (`gz-obpi-lock`).
2. **Then implement in dependency order:** OBPI-12 (disposition handler), OBPI-03 (gate5 floor
   + grader-gaming), OBPI-13 (proxy-reality live NC, after 03), OBPI-04 (enter) + OBPI-05 (exit,
   after 04/11/12), OBPI-06/07/08 (log/hook/skill), OBPI-09 (retire staging flags), OBPI-14
   (hardening). Each is heavy → pipeline path, brief-level Gate-5 attestation at completion.
3. **Optional quick win first:** the tracked `obpi_precomplete.py` REQ-kind-awareness defect
   (Movement II item 3) is a clean GHI-direct-fix (`fix(<scope>): <summary> (GHI #N)`); discharge it
   before resuming the heavier build if the operator prefers momentum.
4. **Release bookkeeping (downstream):** drop `ADR-0.29.0-precise-auth` to pool to free the
   `0.29.0` number for the MX release (per the campaign's versioning plan).

## Pending Work / Open Loops

- **ADR-0.0.74 is 2/13 complete.** OBPI-01/02 attested; 03-09 and 11-14 are authored-ready but
  UNIMPLEMENTED. The substrate build is the bulk of remaining work.
- **Tracked defect (Movement II item 3):** `gz obpi precomplete`'s behave-coverage check in
  `src/gzkit/commands/obpi_precomplete.py` (around lines 324-396) is not REQ-kind-aware, unlike
  `obpi_complete.py` (fixed under GHI #636). Clean GHI-tracked direct fix; awaiting operator go.
- **`ADR-0.29.0-precise-auth`** still in the feature list, not yet dropped to pool — release
  bookkeeping, downstream of building the substrate.
- **The enforcement-claim meta-validator** (Movement I item 3 — the general §5 mechanism) is
  its own work, not in this ADR. OBPI-13 ships only grader-gaming's specific live negative
  control, which must comply with §5.
- **`--authored` re-audits completed briefs** (OBPI-01/02 FAIL on changed-files). Consider
  whether the `--authored` gate should skip attested_completed briefs — possible GHI, low
  priority, not blocking.

## Verification Checklist

- [ ] `git rev-parse --short HEAD` is `b56077d3` and `origin/main` equals it (ahead=0 behind=0)
- [ ] `git branch --show-current` is `main`; working tree clean
- [ ] `uv run gz validate` passes all 11 scopes
- [ ] `uv run gz adr status ADR-0.0.74` shows 2/13; OBPI-01/02 attested_completed, 03-09 + 11-14 draft
- [ ] `uv run gz obpi validate --adr ADR-0.0.74 --authored` shows 12/14 PASS (OBPI-01/02 FAIL on the known completed-brief changed-files quirk — expected, not a defect)
- [ ] `EVALUATION_SCORECARD.md` is present in the ADR package directory

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — the amended ADR (Consequences coherence fixed this session)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-11-mx-gz-level-vocabulary.md` — new brief (the vocabulary foundation; implement first)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-12-mx-gates-as-sensors.md` — new brief (disposition handler / matrix)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-13-mx-proxy-reality-detector.md` — new brief (grader-gaming live §5 NC)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-14-mx-hardening.md` — new brief (TTL/release-lock/debt-aging/dangling-state; release wiring fixed this session)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-03-mx-gate5-invariants.md` — reshaped (grader-gaming = 5th floor member)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-05-mx-exit-hard-gate.md` — reshaped (re-emit levels + live exit NC; predecessors declared this session)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-09-mx-retire-staging-flags.md` — reshaped (leveled checkpoint)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/EVALUATION_SCORECARD.md` — Phase-D verdict GO (structural + substance channels)
- `docs/governance/build-to-1.0-campaign-2026-06-20.md` — Magna Carta; §3b amended + § Archive amendment record (Phase C)
- `.gzkit/handoffs/20260621T205805Z-adr-0-0-74-leveled-substrate-phase-a.md` — predecessor handoff (Phase A; this session's continues_from)
- `src/gzkit/commands/obpi_precomplete.py` — site of the tracked stale-behave-check defect (around lines 324-396)

## Environment State

Platform win32; Python 3.13; `uv run` throughout. Branch `main` (operator directive: no feature
branches). HEAD `b56077d3`, ahead=0 behind=0, working tree clean. Last commit SHA at handoff:
`b56077d3`. No OBPI lock was claimed this session — the work was governance authoring (briefs +
campaign + evaluation) and a guarded git-sync, not lock-based implementation; this is a
context-continuity handoff, not a lock-release register entry. No last lock-event timestamp
applies (no `obpi_lock_claimed` this session).
