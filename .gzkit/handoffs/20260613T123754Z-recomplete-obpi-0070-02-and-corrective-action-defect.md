---
mode: CREATE
adr_id: ADR-0.0.70
branch: main
timestamp: "2026-06-13T12:37:54Z"
agent: claude-code
obpi_id: OBPI-0.0.70-02-session-correction-mining
session_id:
continues_from:
last_lock_event_timestamp: "2026-06-13T12:08:50.829919+00:00"
last_commit_sha: f34c771b7ff76ddf8449510e10febbf758a31246
---

<!-- Handoff document for ADR-0.0.70 — created by claude-code at 2026-06-13T12:37:54Z -->

## This handoff ADVISES next moves — it is NOT authorization to execute them

A handoff records a proposed plan and its context. It is NOT clearance to
execute. On resume, present the advised steps and current state, obtain explicit
operator authorization before acting, and treat the human-as-final-witness
doctrine as binding. You advise; the operator rules.

## Current State Summary

OBPI-0.0.70-02-session-correction-mining was RE-COMPLETED this session with a
genuine operator Gate-5 attestation (completion receipt
`attestation_type: operator-verbatim-conversational`), replacing Fable's
repudiated fraudulent Gate-5 (GHI #608, repudiated 2026-06-13T12:00:50Z via
`gz obpi repudiate --cause model-induced-fabrication`). No code changed; the
prior-committed miner (commits ffdc3aaa, 863250d6) was re-verified green:
full suite `arb-step-unittest-e34f335785ec4c66bf7072d30e9a2d26` exit 0, OBPI
scope `arb-step-unittestscoped-1dc85aa04e524810aa683da8655f4d4e` 14/14, lint
`arb-ruff-b73b14918a7749ffabaa6892d73cf0b9`, typecheck
`arb-step-typecheck-569e4f3e9e084dd4ba7f335773ee68ed`, `gz validate
--chores-layout` exit 0, `gz covers` behavior_uncovered_reqs=0. The
`gz obpi complete` call returned exit 0. The OBPI lock is still held pending
this handoff (the lock-release register gate, ADR-0.0.41, is what required this
document). ADR-0.0.70 now reads with item 2 genuinely complete.

## Important Context

Re-completion of a repudiated OBPI is blocked by a two-part defect in the
repudiate verb (tracked: GHI #610, GHI #611). The repudiate verb writes only
the ledger event; it does NOT reset the brief frontmatter `status: Completed`,
and it severs the GHI #66 sealed-scope-evidence path. Consequence: `gz obpi
complete` refused with "Brief is already Completed", and `gz obpi precomplete`
brief_readiness flagged governance-churn paths (`.gzkit/ledger.jsonl`,
`.claude/plans/.pipeline-active*.json`) as out-of-allowlist because the live
changed-files audit had no committed-deliverable evidence to read. The
completion chokepoint `gz obpi complete` does NOT run the changed-files audit
(it lives only in the bypassable precomplete pre-flight), so the operator
ratified proceeding past the inapplicable precomplete block. The manual
workaround was a one-line correction: reset the brief frontmatter status
Completed to Active (correcting the Layer-1/Layer-2 divergence the repudiate
verb should have corrected automatically), then `gz brief reconcile` to refresh
the reconcile receipt, then `gz obpi complete`.

## Decisions Made

- **Decision:** Re-complete OBPI-0.0.70-02 via a manual brief-status reset
  (Completed to Active) then `gz obpi complete`.
  **Rationale:** The implementation is genuinely done and re-verified green;
  the blocker is a verb defect, not missing evidence. Operator ratified
  "Proceed with completion" after the full diagnosis.
  **Alternatives rejected:** Hold the OBPI repudiated-and-incomplete until the
  structural fix lands (leaves verified work dangling indefinitely);
  `--force` the precomplete (does not satisfy the register gate anyway).
- **Decision:** File the corrective-action gap as TWO defect GHIs (#610 symptom,
  #611 architectural) and route both as defect correction under ADR-0.0.71.
  **Rationale:** Operator: "this isn't new design, this is defect correction."
  The capability is what repudiation was meant to provide.
  **Alternatives rejected:** A new pool ADR / gz-design ceremony (operator
  explicitly rejected the new-design framing); labeling as enhancement.
- **Decision:** Capture the correction-vs-enhancement doctrine into the
  AGENTS.md corpus (single universal home), not multiple corpora.
  **Rationale:** CLAUDE.md redirects to AGENTS.md; one universal-contract
  corpus binds all agents. Duplication would manufacture multi-source drift.
  **Alternatives rejected:** Also writing to CLAUDE.md corpus (redundant);
  hand-editing the rendered AGENTS.md (forbidden — playback is the sole writer).

## Immediate Next Steps

1. Operator decides whether to mirror the correction-vs-enhancement doctrine
   into the `ghi-author` skill classification table / Common Rationalizations
   list (the operational surface where defect-vs-enhancement is applied at
   GHI-authoring time). This is a skill edit under `.gzkit/skills/ghi-author/`,
   followed by `gz agent sync control-surfaces`.
2. Operator decides scheduling for the GHI #610 / #611 corrective work under
   ADR-0.0.71 (completion-repudiation). #610 is the mechanical fix (reset brief
   status + reuse sealed scope evidence in the repudiate verb); #611 is the
   general append-only corrective-action transition model.
3. Optionally trigger the corpus compress/rendition setpoint so the captured
   doctrine renders into the visible AGENTS.md (currently it lives in
   `.gzkit/corpus/AGENTS.md.jsonl` as the source of truth, not yet rendered).

## Pending Work / Open Loops

- GHI #610 (defect/runtime) — OPEN: `gz obpi repudiate` does not reset brief
  status and severs sealed scope evidence; repudiated OBPIs cannot be
  re-completed without the manual workaround used this session.
- GHI #611 (defect/runtime) — OPEN: no general append-only corrective-action
  primitive to undo agent/human error; reframed to defect correction under
  ADR-0.0.71. Both GHIs cross-linked; #611 generalizes #610.
- Optional: mirror the captured doctrine into the ghi-author skill.
- Corpus rendition of the captured doctrine into rendered AGENTS.md is pending
  the next compress/playback setpoint.

## Verification Checklist

- [ ] `uv run gz obpi reconcile OBPI-0.0.70-02-session-correction-mining` shows receipt and brief agree
- [ ] `uv run gz adr status ADR-0.0.70 --json` reflects item 2 completed
- [ ] Branch matches: `git branch --show-current` is `main`
- [ ] `uv run -m unittest tests.chores.test_session_correction_mining -q` passes 14/14
- [ ] `gh issue view 610` and `gh issue view 611` are OPEN with cross-links

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/obpis/OBPI-0.0.70-02-session-correction-mining.md` — re-completed brief with genuine attestation
- `src/gzkit/insights/correction_mining.py` — the read-only miner (re-verified, unchanged)
- `tests/chores/test_session_correction_mining.py` — 14 tests, all green this session
- `.gzkit/insights/agent-insights.jsonl` — Behavior Rule 11 improvement record appended this session
- `.gzkit/corpus/AGENTS.md.jsonl` — correction-vs-enhancement doctrine captured (prime-directive-ownership, invariant tier)

## Environment State

Windows 11 / PowerShell primary; Python 3.13 via uv. Branch `main`, ahead=0
behind=0 at session start. gz CLI from the working tree.

Lock-pairing metadata (token-block discipline Sub-Invariant 2): matching
`obpi_lock_claimed` event timestamp `2026-06-13T12:08:50.829919+00:00`; HEAD
commit SHA at handoff creation `f34c771b7ff76ddf8449510e10febbf758a31246`;
branch `main`, ahead=0 behind=0.
