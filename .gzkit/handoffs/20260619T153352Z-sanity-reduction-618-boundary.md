---
mode: CREATE
adr_id: ADR-0.0.73
branch: main
timestamp: "2026-06-19T15:33:52Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260619T112721Z-obpi-0.0.73-09-completion.md
last_commit_sha: 6a560e05
---

<!-- Handoff document for ADR-0.0.73 / Build-to-1.0 Magna Carta — created by claude-code at 2026-06-19T15:33:52Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a proposed plan and its
context. It is NOT clearance to unilaterally execute that plan. On resume, at
every freshness level: present the advised steps and current state, obtain
explicit operator authorization before any file mutation or `gz` ceremony, and
treat the campaign as the governing authority over what is pulled next. You
advise; the operator rules.

## Current State Summary

Floor is green (`uv run gz check` passing) and `main` is synced at commit
`6a560e05`. This session executed a defect sweep plus the opening cuts of the
Magna Carta Sanity-Reduction track:

- GHI #622 fixed (`lock_manager.list_locks` full-slug ADR filter), commit `92e979f4`; closed.
- GHI #627 verified already-resolved by OBPI-0.0.73-09's own implementation; closed (no code change).
- GHI #628 fidelity backfill: all 101 grandfathered ADR Decisions now carry runnable `## Fidelity Assertions`; `gz adr fidelity` is 102/102 green; the grandfather population is 0 and the waiver-ratchet baseline ratcheted 101 to 0; commit `08320022`; closed.
- Four formerly-RED validators repaired: `check-config-paths` (commit `daeddfef`), `--sensitivity` on OBPI-0.0.73-05/-09 (commit `0c605efd`), `--evaluation-justify-binding` via 8 gz-justify artifacts (commit `fe9c3c78`), and `--tautological-test-audit` (fence regression fixed in `7da9d680`).
- `qc_binding.py` split 832 to 274 + 576 lines (commit `a06cf138`).
- Magna Carta amendments committed: the heap reckoning incorporation and the Sanity-Reduction track ratification (operator "do what it takes to achieve sanity").
- Sanity-Reduction cut #618 step 1 LANDED: the dispatch consistency fence `tests/cli/test_validate_dispatch_consistency.py` (commit `7da9d680`).

## Important Context

- The Magna Carta `docs/governance/build-to-1.0-campaign-2026-06-10.md` GOVERNS; this handoff only advises. The 2026-06-19 Sanity-Reduction amendment plus its Progress note are the authoritative resume record; read them first.
- The Sanity-Reduction track is a bounded override of completion-before-reduction: only named, parity-proven, green-gated, one-at-a-time cuts. It runs alongside the topmost spine (Phase 0 / B.1 / ADR-0.0.73) and does not preempt it; it is not itself a 1.0 gate.
- The `gz validate` dispatch is the floor's spine. A silently-dropped scope would pass `gz check` green while checking nothing — the governance facade ADR-0.0.73 exists to kill. The step-1 fence exists precisely so the next collapse cut cannot do this undetected: any collapse MUST keep the fence green.
- Two drainage GHIs were filed to Magna Carta Phase E.5 this session: #631 (eval scorer manufactures false-RED 1.0 scores) and #632 (tautological-test-audit brittleness). Both are root-cause homes; the in-session workarounds (8 justify artifacts; the fence's module-scope source read) hold the gates green meanwhile.

## Decisions Made

- **Decision:** Declare `sensitivity: security` on OBPI-0.0.73-05/-09 rather than grandfather them.
  **Rationale:** Both genuinely modified subprocess-spawning surfaces; the rule mandates the declaration for new overlapping briefs.
  **Alternatives rejected:** Grandfathering (would breach the ratcheted baseline 87 and fail `--waiver-ratchet`); narrowing Allowed Paths (would falsify what the work touched).
- **Decision:** The ~29 WEAK fidelity rows are left as honest proxies, not "fixed."
  **Rationale:** Their ADRs' own enforcers are unbuilt (Draft/stub/collapsed); sharpening requires building those ADRs, which is their forward work, not a backfill defect.
  **Alternatives rejected:** Building 29 unbuilt validators now (out of scope; not a defect).
- **Decision:** Stage #618 as step-1 fence first, then the collapse — do not slam the six-surface spine in one shot.
  **Rationale:** A botched collapse silently dropping a scope is the worst failure class; the parity net must exist first.
  **Alternatives rejected:** One-shot registry collapse without a parity net.

## Immediate Next Steps

ADVISORY ONLY — present these and await operator authorization before acting.

1. Resume Sanity-Reduction cut **#618 step 2**: fold `validate()`'s 78-param signature, the `_other_scopes_active = any([...])` predicate, `_collect_errors`, and the `p_validate.set_defaults` forwarding lambda into one `VALIDATOR_REGISTRY` in `src/gzkit/commands/validate_cmd.py`. Verify green against the step-1 fence `tests/cli/test_validate_dispatch_consistency.py` with its own per-cut parity proof (toggle each scope, assert dispatch identical before/after). Green-gate via `uv run gz check`.
2. Then cut **#617**: collapse the 92 `_lazy()` CLI handler refs across the 3 byte-identical manifests to one source.
3. Then cut **#631**: fix `_score_architectural_alignment` in `src/gzkit/adr_eval_scoring.py` so it stops manufacturing false-RED 1.0 scores; this removes the need for the 8 justify band-aids on future evals.
4. Then the waiver/grandfather/baseline stack review (collapse what proves redundant; keep what each mechanism uniquely earns).

## Pending Work / Open Loops

- GHI #631 and #632 are open, homed to Magna Carta Phase E.5 (true root-cause fixes sequenced by the track above).
- GHI #632 symptom 3 (wrong-file reporting in the tautological audit) carries a hypothesis (count/positional baseline matching) that the fixer should confirm against `src/gzkit/tautological_tests.py`.
- The `evaluation-justify-binding` gate is held green by force-committed justify artifacts under `artifacts/justify/`; #631's real fix should re-score the stale evals and make those artifacts unnecessary.
- A stale `.pipeline-active` marker for the completed OBPI-0.0.73-09 was purged via `gz preflight --apply` this session; if it recurs, the marker-not-purged-on-completion path is worth a look.

## Verification Checklist

- [ ] `git branch --show-current` is `main`; HEAD at or ahead of `6a560e05`, synced.
- [ ] `uv run gz check` is green before opening the next cut (green-first).
- [ ] `uv run -m unittest tests.cli.test_validate_dispatch_consistency` passes (the #618 step-1 fence).
- [ ] Re-read `docs/governance/build-to-1.0-campaign-2026-06-10.md` 2026-06-19 Sanity-Reduction amendment + Progress note before pulling the next cut.
- [ ] Confirm GHI #631 and #632 are still open and homed to E.5.

## Evidence / Artifacts

- `tests/cli/test_validate_dispatch_consistency.py` (the #618 step-1 dispatch consistency fence)
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` (Magna Carta — Sanity-Reduction amendment + Progress note)
- `src/gzkit/commands/validate_cmd.py` (the dispatch spine the #618 collapse targets)
- `src/gzkit/governance/trust_audits/qc_binding.py` and `src/gzkit/governance/trust_audits/_qc_negative_controls.py` (the 832 to 274 + 576 split)
- `src/gzkit/commands/config_paths.py` (the path-literal exemption fix)
- `src/gzkit/tautological_tests.py` (GHI #632 root surface)
- `src/gzkit/adr_eval_scoring.py` (GHI #631 root surface)
- `artifacts/justify/adr-0-0-73-verification-layer-binding-audit-20260619.md` (one of the 8 justify artifacts)
- `data/fidelity_presence_grandfather.json` (emptied) and `data/waiver_ratchet_registry.json` (baseline 101 to 0)
- `.gzkit/insights/agent-insights.jsonl` (course-correction + defect-resolution + disposition records)
