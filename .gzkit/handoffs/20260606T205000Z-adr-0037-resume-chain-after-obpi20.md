---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-06T20:50:00Z"
agent: claude-code
obpi_id: OBPI-0.0.37-23
session_id: finish-adr0037-obpi20-done
continues_from: .gzkit/handoffs/20260606T123000Z-finish-adr-0037-cms-durable-519.md
---

<!-- Handoff document for ADR-0.0.37 — created by claude-code at 2026-06-06T20:50:00Z -->

## This handoff ADVISES next moves — it is NOT authorization to execute them

On resume you MUST (1) present the advised steps to the operator, (2) obtain
explicit authorization before any file mutation, `gz` ceremony, or pipeline run,
and (3) treat human-as-final-witness as binding. You advise; the operator rules.
Every remaining OBPI below is foundation/heavy — Gate 5 human attestation is
mandatory and cannot be self-closed.

## Current State Summary

This session resumed the prior handoff (finish ADR-0.0.37) and landed **two durable
commits**, both pushed to `origin/main` (HEAD = `a8517518`, tree clean, synced 0/0):

1. **`a4519e4f` — `fix(reconcile): honor brief creates-declarations in Stage-2 gate`.**
   A governance **deadlock** was discovered and fixed: the Stage-2 reconcile-receipt
   gate (`check_reconcile_receipt_gate` in `src/gzkit/pipeline_runtime.py`) fails closed
   when an Allowed Path is missing on disk (`is_receipt_fresh`) or when `missing_on_disk`
   drives `has_drift` (`_compute_allowlist_delta` in `src/gzkit/governance/brief_reconcile.py`),
   yet the `pipeline-gate.py` PreToolUse hook blocks creating those files until a pipeline
   marker exists, and the marker is only written *after* the gate passes
   (`obpi_cmd.py:434` before `:449`). Closed loop — it blocked **every net-new-file OBPI**.
   The fix teaches `is_receipt_fresh`, `_compute_allowlist_delta`/`reconcile_brief`, and
   `check_reconcile_receipt_gate`/`_find_drifted_path` to honor the brief's
   `## Creates These Files` declarations via `extract_brief_creates_paths` — mirroring the
   GHI #419 exemption `brief_path_validity` already applies. TDD RED→GREEN; 3 new tests;
   full suite 5927 OK. `Task: TASK-reconcile-gate-honor-creates`.

2. **`a8517518` — OBPI-0.0.37-20 (setpoint declaration + coherence validator).**
   Foundation/heavy, **Gate-5 attested-complete** (attestor g0,
   operator-verbatim conversational attestation). Delivered: fail-closed
   `gz validate --setpoint-coherence` scope, `SETPOINT_TOKENS` constant + pinned
   `temperature_for` accessor, CLI wiring, manpage, BDD, and **7 `heavy`-sentinel
   setpoints** in `data/vendor-manifest.json` (decision A, ratified). `gz obpi reconcile`
   PASS (runtime state ATTESTED COMPLETED, proof + attestation recorded).

`uv run gz adr status ADR-0.0.37` confirms OBPI-20 dropped off the closeout-blocker
list; **7 OBPIs remain unbuilt** (10, 21, 22, 23, 24, 25, 27). ADR-0.0.37 stays open.

## Important Context

**The deadlock fix is load-bearing for the rest of the chain.** Items 21/22/23/24/25/27
all create net-new files; before `a4519e4f` they could not have run the pipeline at all.
The now-working net-new-file pattern is: list NEW files in `## Allowed Paths` **and** in a
`## Creates These Files` section (the GHI #419 marker), so both the `--authored` gate and
the reconcile gate exempt them until they exist; the `pipeline-gate.py` hook then permits
the writes once `gz obpi pipeline` creates the marker.

**The behave-coverage waiver pattern (learned this session).** The `behave_req_coverage`
precomplete gate is REQ-kind-agnostic: it flags BEHAVIOR REQs with no CLI surface and
SUPPORT REQs as "lacking scenario tags." The sanctioned fix is an OBPI-level entry in
`data/behave_coverage_waivers.json` (`waivers[OBPI-id] = {rationale: <code>, status_at_landing,
waived_reqs: [...]}` + a `default_rationale[code]` text). OBPI-20 waived REQ-04 (pure
accessor, no CLI surface → unit-proven) and REQ-05 (SUPPORT → ledger+validator). Add this
file to the brief's Allowed Paths when an OBPI needs a waiver.

**The substrate is still hollow** (unchanged from the prior handoff): the append-only corpus
`.gzkit/corpus/AGENTS.md.jsonl` is ~895 B; `.gzkit/invariants/` has 4 entries. Items **18
(corpus model)** and **19 (corpus capture)** build that substrate, and the composer (21) +
playback (22) have little to compress until the corpus migration runs. The prior handoff's
build order (`20 → 23 → 21 → 22 → 24 → 25 → 27 → 10`) does not list 18/19/26 explicitly —
reconcile the true dependency graph with the operator before picking the next item: the
composer/playback chain (21/22) realistically depends on the corpus model/capture (18/19).

**Setpoint decision-A precedent.** Non-`AgentContract` routed surfaces carry a `heavy`
(no-compression) sentinel. If a later OBPI makes another surface a real compression target,
its setpoint changes from the sentinel to a leaner tier — the coherence gate already enforces
that every routed pair stays declared.

## Decisions Made

- **Decision:** Direct-fix the reconcile-gate deadlock now (not a new OBPI/GHI).
  **Rationale:** operator-selected ("Direct-fix the gate now"); in-flight defect, one coherent
  commit, TDD, mirrors the existing GHI #419 exemption. **Rejected:** new OBPI under ADR-0.0.37
  (heavier, no separability gain); file-a-GHI-and-pause (would strand the whole chain).
- **Decision:** OBPI-20 declares a `heavy` sentinel setpoint for all 7 non-`AgentContract`
  routed pairs (decision A). **Rationale:** matches the checklist's "every (surface×consumer)
  has a declared setpoint" + the captured operator spec; operator ratified at Gate 5.
  **Rejected:** decision B (narrow the coherence domain to compression targets only) — recorded
  in the brief's § Open Implementation Decision should it ever be revisited.
- **Decision:** Waive REQ-04/REQ-05 behave coverage rather than author artificial scenarios.
  **Rationale:** ADR-0.0.59 names BDD-ing pure functions / SUPPORT REQs as the anti-pattern;
  unit + ledger+validator are the correct proof channels. **Rejected:** contrived behave
  scenarios for a non-CLI accessor and a SUPPORT doc REQ.
- **Decision:** Commit the deadlock fix separately from OBPI-20 (own `Task:` trailer), then let
  the pipeline Stage-5 git-sync commit the OBPI-20 work. **Rationale:** two distinct concerns;
  clean audit trail.

## Immediate Next Steps

Advisory only — present and obtain authorization before acting.

1. **Reconcile the true build order with the operator** before authoring the next brief: the
   prior handoff says `23` is next, but `18` (append-only corpus model) and `19` (corpus
   capture tool + skill) build the substrate the composer (21) and playback (22) consume.
   Decide whether 18/19 precede the composer chain. Read the parent ADR Checklist
   (`docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/...md` lines
   286–314) for the canonical item descriptions.
2. **Author the chosen next OBPI's brief** from its scaffold under
   `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/`, using
   the net-new-file pattern (Allowed Paths + `## Creates These Files`); run
   `uv run gz obpi validate --adr ADR-0.0.37 --authored` until it passes.
3. **Plan-audit → pipeline:** `uv run gz plan audit <OBPI-ID>` (via plan mode + ExitPlanMode so
   a `.claude/plans/` plan file exists), then `uv run gz obpi pipeline <OBPI-ID>`. The deadlock
   fix means net-new-file briefs now pass Stage-2; expect to `gz brief reconcile` once after
   each edit batch (the receipt goes stale when you touch an existing allowlist file).
4. **Add a behave waiver** if the OBPI has non-CLI-BEHAVIOR or SUPPORT REQs (see Important
   Context); declare `data/behave_coverage_waivers.json` in the brief's Allowed Paths.
5. **Continue the chain** through the remaining heavy/foundation OBPIs, one Gate-5 attestation
   each. Plan the corpus migration (the hidden content work) when 18/19/21/22 are in scope.

## Pending Work / Open Loops

- **7 OBPIs unbuilt:** 10 (doctrine refresh), 21 (composer), 22 (rendition store + playback),
  23 (invariant tier), 24 (advisor-QC loop), 25 (bullet-retention tier-scoped), 27
  (migration/disposition). Each foundation/heavy + Gate 5. ADR-0.0.37 cannot close until all
  are attested.
- **Hollow substrate:** corpus ~895 B, registry 4 entries; the migration that populates them
  has not run. Composer/playback have little to compress until then.
- **CMS scope gap (from prior handoff, still open):** ADR-0.0.37 targets AGENTS.md (~22% of the
  always-loaded surface); the `.claude/rules/*.md` surface (~73%) needs its own CMS ADR —
  operator-acknowledged future work.
- **Handoff retention (from prior handoff, still open):** no `gz handoff archive` verb exists;
  the store grows freely (floor-guarded at 34). Recommended as its own GHI/OBPI; do not
  bulk-delete.
- **`gz validate --setpoint-coherence` is NOT in the default `gz check` scope** (deliberate;
  adding it is a separate operator decision — see the OBPI-20 brief Denied Paths).

## Verification Checklist

- [ ] Branch is `main`: `git branch --show-current`
- [ ] Tree clean + synced 0/0: `git status --short --branch`
- [ ] HEAD is `a8517518` (or later): `git log --oneline -3`
- [ ] OBPI-20 attested: `uv run gz adr status ADR-0.0.37` shows it off the closeout-blocker list
- [ ] New scope works: `uv run gz validate --setpoint-coherence` exits 0
- [ ] Deadlock fix holds: `uv run -m unittest tests.governance.test_reconcile_freshness tests.governance.test_brief_reconcile` passes
- [ ] Substrate still hollow: `wc -c .gzkit/corpus/AGENTS.md.jsonl` (~895 B); `ls .gzkit/invariants/*.json` (4)

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/setpoint_coherence.py` — the OBPI-20 validator scope
- `src/gzkit/content/vendors.py` — `SETPOINT_TOKENS` + fail-closed `temperature_for` accessor
- `data/vendor-manifest.json` — `content_type_temperatures` now declares all 8 routed surfaces (decision A)
- `docs/user/manpages/validate.md` — `--setpoint-coherence` scope docs (REQ-05)
- `data/behave_coverage_waivers.json` — OBPI-20 REQ-04/05 waiver (the reusable waiver pattern)
- `src/gzkit/governance/reconcile_freshness.py` — `is_receipt_fresh` creates-exemption (deadlock fix)
- `src/gzkit/governance/brief_reconcile.py` — `_compute_allowlist_delta` creates-exemption (deadlock fix)
- `src/gzkit/pipeline_runtime.py` — `check_reconcile_receipt_gate` passes creates (deadlock fix)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-20-setpoint-declaration-coherence-validator.md` — the completed brief (status Completed)
- `.gzkit/handoffs/20260606T123000Z-finish-adr-0037-cms-durable-519.md` — predecessor handoff (build order + bill)

## Environment State

Windows + Python 3.13 via `uv`. Last commit SHA `a8517518217f4c15e6d83a8bbbf530be71ecbfb9`;
branch `main`, 0/0 synced with `origin/main`; tree clean. No active OBPI lock (OBPI-20 released
on completion). `uv run gz check` / git-sync pre-commit is multi-minute (unittest ~4.5 min
over 5927 tests). Operator attribution: use the name `g0` only; never the personal email.
