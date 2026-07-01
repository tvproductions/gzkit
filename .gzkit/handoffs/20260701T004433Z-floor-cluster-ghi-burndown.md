---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-07-01T00:44:33Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: 9305497b
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-07-01T00:44:33Z.
     Scope note: this is a maintenance/MX GHI-burndown sweep, not ADR-0.0.74 OBPI
     work. It is homed under ADR-0.0.74 because #651 is directly an ADR-0.0.74
     surface and the whole sweep advances the campaign's Movement II "drain the
     facade" theme (ADR-0.0.74 §5 enforcement floor). The four GHIs span
     ADR-0.0.71 (#634/#610), ADR-0.0.74 (#651), and ADR-0.0.59 (#632). No OBPI
     lock was held this session (direct-fix path per AGENTS.md § Defect-fix
     routing), so the lock-coupling frontmatter keys are intentionally empty. -->

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

A facade-drain maintenance sweep over the Magna Carta campaign's floor cluster.
Started from `/ghi-triage` (58 open GHIs ranked; ranking cached at
`.gzkit/cache/triage/rank.json`), reconciled the triage against the active
campaign (`docs/governance/build-to-1.0-campaign-2026-06-30.md`), and drained the
direct-fixable floor-cluster GHIs as patch-line MX squawks. Four GHIs closed,
each via the governed `ghi-close` read→execute→verify→close protocol with
RED→GREEN TDD and a full `uv run gz check` (exit 0) after every fix. **All four
commits are on `origin/main`** (synced via guarded `gz git-sync --apply`; tree is
clean, 0 ahead / 0 behind).

Closed this session:
- **#634** (`5456b2f9`) — `gz obpi status` rendered a repudiated OBPI as green
  `ATTESTED COMPLETED`; the status semantics layer never consumed the
  `obpi_completion_repudiated` event. Added a `repudiated` short-circuit in
  `derive_obpi_semantics` + a `REPUDIATED` render branch. Verified live on
  OBPI-0.0.37-22.
- **#610** (`fbf52d6c`) — a repudiated OBPI could not be re-completed. Gap B
  (hard blocker): `gz obpi repudiate` never reset the brief frontmatter
  `status: Completed`, so `gz obpi complete` fail-closed — now reset to `Active`.
  Gap A: the precomplete changed-files audit switched to the live tree for a
  repudiated OBPI — now reuses sealed `scope_audit` via `_should_use_sealed_scope`.
- **#651** (`41b3edfb`) — the enforcement-floor `gz check` step demoted to
  advisory inside the MX hangar (it was absent from `_STEP_GUARD_META`). Pinned
  CRITICAL. Chose the emitted-level pin over GATE5_INVARIANTS membership because
  membership collides with REQ-0.0.74-03-01 (the floor is fixed at exactly five
  integrity-class guards).
- **#632** (`9305497b`) — the tautological-test audit's brittle count/position
  baseline. Switched `audit_drift` to stable-identity matching; added two NARROW
  scanner exemptions (`ast.parse`/`rglob('*.py')` source-fences;
  importlib-module-backed behavioral tests); converted the 2 genuine tautologies
  to behavioral assertions on production. Added anti-laundering pin tests.

## Important Context

- **Campaign reconciliation (load-bearing).** The Magna Carta rules *pull order*,
  not severity. The forward engine's topmost item — Movement III Phase 0
  (airlock-in the constellation) — is **operator-gated and NOT authorized**; do
  not open it without explicit authorization. GHI burndown is the *maintenance
  engine* (patch line, `MX = patch; GHIs are its squawks`) and runs in parallel —
  it needs no Movement III authorization. Draining the backlog to steady-state is
  itself a §8 1.0 gate.
- **`#519` is the only `emergency`-labeled GHI** — campaign-authorized to run
  outside sequence (its cure is the §2a single-router bootstrap).
- **Reading the code beat the triage estimate three times.** #634's tempting
  frontmatter-validator expansion would have turned `gz check` red (it is #610's
  Layer-1 scope); #651's "obvious" GATE5 membership route would have broken a
  foundation cardinality REQ; #632's "~100 line" estimate hid a shrink-ratchet
  fence + 4 scanner false-positives. DO IT RIGHT #5 (read before you change) is
  the operative lesson.
- **`data/tautological_test_baseline.json` is a shrink-ratchet surface**
  (ADR-0.0.73 BI#8, `baseline_count: 91`) — its `operations` list may only
  shrink. #632's identity-matching fix makes stale baseline entries harmless (a
  new tautology has a new identity → still flags), so the baseline was left
  untouched (no re-baseline, ratchet honored).
- **Repudiation-consumer cluster status:** #634 (render) + #610 (re-complete) are
  now coherent. The remaining coupled surfaces — `validate_frontmatter`,
  `closeout_form.auto_fix_obpi_brief_frontmatter` — are repudiation-blind by the
  same class and are tracked under #611 (the general append-only
  corrective-action primitive; architectural, pool-ADR scope).

## Decisions Made

- **Decision:** Run the burndown top-down by severity, starting with the floor
  cluster (#634 → #610 → #651 → #632).
  **Rationale:** Where my severity triage and the campaign's §5/§8 floor property
  coincide is the highest-leverage start; it pays down the named root cause
  ("enforcement must actually fire") rather than generic drift.
  **Alternatives rejected:** authorizing Movement III (not authorized; different
  engine); working #519 first (emergency interrupt, but architectural not
  patch-sized).
- **Decision:** #651 pinned via `_STEP_GUARD_META` CRITICAL, not GATE5_INVARIANTS
  membership.
  **Rationale:** GATE5_INVARIANTS is fixed at exactly five integrity-class guards
  by REQ-0.0.74-03-01; the enforcement-floor meta-validator *runner* is a
  different category. Emitted-level CRITICAL pins it without disturbing the
  floor's declared cardinality.
  **Alternatives rejected:** floor membership (breaks the cardinality REQ);
  `gz mx exit` re-run as sufficient backstop (leaves an in-hangar advisory window
  open — the "safe place to vibe" the ADR warns of).
- **Decision:** #632 fixed as scanner-correctness (narrow exemptions) + 2 real
  dispositions, NOT "refactor 6 tautologies."
  **Rationale:** 4 of the 6 flagged ops were scanner false-positives (legitimate
  behavioral/static-fence tests); refactoring them would have been scanner-gaming
  on a §5 sensor. The `ast.parse`/`rglob('*.py')` signals are deliberately narrow
  (a `"src"` path segment was rejected as too broad after it over-exempted 13
  ops); pin tests prove real doc-echo tautologies still flag.
  **Alternatives rejected:** re-baseline up (shrink-ratchet forbids growing
  `operations`); broad `"src"`-segment source-fence signal (over-exempts, launders
  real tautologies).

## Immediate Next Steps

<!-- ADVISORY ONLY — present for operator review; do not execute without authorization. -->

1. **Decide the next burndown target.** The direct-fixable floor cluster is
   exhausted. Recommended next pull is the degrading-severity tier —
   e.g. `#544` (covers grandfathering cache loaded as raw dict, no schema
   validation — clean ~30-60 line Pydantic fix), `#582` (subprocess text reads
   lack `errors=`; ~39-site sweep + validator), or `#558` (`gz adr demote
   --on-collision keep-pool` leaves stale `promoted_to`/`Superseded`).
2. **Do NOT pull #648, #643, or #623 as patch-line work** — they are
   forward-engine / AIRLOCK-routed / larger-correction, not direct fixes
   (verified this session).
3. **If Movement III is to be worked, obtain explicit operator authorization
   first** (Phase 0 airlock-in is operator-gated per the campaign).
4. **Optionally file a follow-up note on #611** — the repudiation-blind
   frontmatter surfaces (`validate_frontmatter`, `closeout_form`) are the next
   coupled cut once the general corrective-action primitive is designed.

## Pending Work / Open Loops

- **#611** (open) — general append-only corrective-action primitive; the
  architectural home for the repudiation-consumer class (#634/#610 are its
  point-fixes). Pool-ADR / design-conversation scope, not a direct fix.
- **#648** (open) — BI#9 enforcement-floor enrollment-completeness enumeration;
  operator-routed to the AIRLOCK system. #651 fixed the *demotion*; #648 is the
  *enumeration* (whether a missing floor member is detected at all).
- **#643** (open) — Stage-4 acceptance evidence is agent-fabricable; needs a new
  `gz obpi present-evidence` verb + validator scope (forward-engine).
- **#623** (open) — ADR-0.0.37 canon→AGENTS.md derivation-spine facade (larger
  correction).
- **Degrading-severity tier** (open): #544, #618, #538, #582, #558, #578, #573,
  #575, #563, #565, #536, #595, #641, #480, #516, #609 — see
  `.gzkit/cache/triage/rank.json` for the full ranked list.

## Verification Checklist

- [ ] `git rev-list --left-right --count origin/main...main` → `0	0` (synced)
- [ ] `git branch --show-current` → `main`
- [ ] `git status --short` → clean (no uncommitted changes)
- [ ] `uv run gz check` → "All checks passed" (exit 0)
- [ ] `uv run gz obpi status OBPI-0.0.37-22` → `Runtime State: REPUDIATED` (#634)
- [ ] `gh issue view 634 634 610 651 632` show state CLOSED (spot-check the four)
- [ ] `uv run python .claude/skills/ghi-triage/scripts/triage.py --format json`
      re-run if a fresh backlog count is needed

## Evidence / Artifacts

- `.gzkit/cache/triage/rank.json` — the 58-GHI severity ranking driving the sweep
- `src/gzkit/ledger_semantics.py` — #634 `_repudiated_obpi_semantics` short-circuit
- `src/gzkit/commands/status_obpi.py` — #634 REPUDIATED render branches
- `src/gzkit/commands/obpi_cmd.py` — #610 `_reset_brief_status_after_repudiation`
- `src/gzkit/hooks/obpi.py` — #610 `_should_use_sealed_scope`
- `src/gzkit/commands/quality.py` — #651 enforcement-floor CRITICAL pin
- `src/gzkit/tautological_tests.py` — #632 identity matching + narrow exemptions
- `tests/commands/test_status_obpi.py` — #634 regression tests
- `tests/test_obpi_repudiate_cli.py`, `tests/test_obpi_validator.py` — #610 tests
- `tests/mx/test_check_step_checkpoint_seam.py` — #651 `TestEnforcementFloorPin`
- `tests/governance/test_tautological_tests.py` — #632 pin tests
- `tests/governance/test_token_block_discipline.py` — #632 2 converted tautologies

## Environment State

Python 3.13; `uv` toolchain. No environment changes this session. All four fix
commits (`5456b2f9`, `fbf52d6c`, `41b3edfb`, `9305497b`) are on `origin/main`;
HEAD at handoff creation is `9305497b`.
