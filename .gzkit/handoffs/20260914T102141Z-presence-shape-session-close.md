---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-14T10:21:41Z'
agent: claude-code
session_id: 735b8082-6bf0-4a83-ac46-f9af2c98b706
continues_from: .gzkit/handoffs/20260914T100618Z-presence-shape-996-justify-binding.md
---

## Current State Summary

Fresh handoff at operator request ("update h/o, git sync"), re-authored at `c6b735985` after predecessor `20260914T100618Z-presence-shape-996-justify-binding.md` synced. No code changed since that handoff.

Session 735b8082 resumed `20260914T084920Z-exit-status-shape-session-close.md` and worked family-A shape: presence.
- GHI #996 fixed in `eb91f20b6` and closed. A walkthrough under `artifacts/justify/` discharges a triggered evaluation only when it parses, every section is filled, its own frontmatter names the subject, and it was generated after the evaluation. Enrolled as enforcement claims `evaluation-justify-binding` (refuse) and `evaluation-justify-binding-qualified` (admit).
- The eval-feedback-cluster regression the fix exposed (template and complexity-hint text read as confusion) is repaired in the same commit.
- Evidence of a second harness-green-over-red instance added to GHI #969.

At authoring: working tree clean, origin/main level (`0 0`), no OBPI locks, 43 open GHIs (search total_count).

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** no change.
- **ghi triage:** presence shape in progress. #996 closed; #994 open with no live-brief owner; #983 open, touched by PENDING ADR-0.35.0 briefs OBPI-0.35.0-07/-10/-13; #894 open, awaiting the operator's 2026-09-07 ruling while OBPI-0.35.0-08 is IN PROGRESS (no lock). Queue 43 open.
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 TOPMOST unchanged. `gz validate --evaluation-justify-binding` still exits 3 on ADR-0.33.0-airlock-membrane, ADR-0.35.0 and ADR-0.35.0-canon-entry-corpus-landing; answering them needs genuine reasoning on an OBPI under the ADR or its draft slug.
- **new R&D:** not worked.

### Gotchas carried
- `src/gzkit/chores/*.py` libraries are synced from `.gzkit/chores/`; edit the canonical copy or sync overwrites the change.
- The walkthrough parser splits only at `## `, so the complexity-hints block sits inside section 8's reasoning.
- The drafted presence class fix (a declaration on `@enforces`) reaches none of the open presence instances: their witnesses are not registered claims.
- Background notifications can report exit 0 over a failing `gz check`; read the captured REAL EXIT line.

## Decisions Made

- [agent-chose] Re-authored as a fresh CREATE chained to `20260914T100618Z`, with state re-verified at `c6b735985`. This session's three operator rulings (resume "Presence shape (Recommended)", "Fix #996 + enroll (Recommended)", "Draft slug or OBPI (Recommended)") are carried by the rulings store through that link and deliberately not restated (GHI #1003).

## Immediate Next Steps

1. Put the next presence member to the operator: #994 is the direct-fix candidate (no live owner; its body leaves the remedy arm, prompt contract vs import-time check, open).
2. For #983, surface the routing facts: PENDING briefs OBPI-0.35.0-07/-10/-13 read the ownership surface, and the disposition of the 10 uncovered sections is operator-ruled.
3. Keep #894 as awaiting a ruling; do not treat it as next eligible.
4. Offer the class-wide presence declaration on `@enforces` only as an option for future checks.

## Pending Work / Open Loops

- GHI #994, #983, #894 open (presence); #969 open by ruling; #1008 open, unselected.
- Insight still open: `src/gzkit/commands/obpi_stages.py` BASELINE_VERIFICATION prescribes `uv run -m unittest -q` rather than the canonical unittest step.
- Three live justify-binding violations await genuine walkthroughs; the scope is opt-in, outside the gz check default.
- 83 enforcement claims disclosed population-undeclared; 55 exemption-undeclared.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
gh issue view 996 --json state
uv run gz obpi lock list
uv run -m unittest tests.governance.test_justify_binding_gate tests.chores.test_eval_feedback_cluster tests.skills.test_skill_surface_sync_justify
uv run gz validate --evaluation-justify-binding --json
```
Expected at authoring: `0 0` apart from this handoff's sync; #996 CLOSED; no active locks; tests green; the scope exits 3 on exactly three ADR ids. Re-run rather than trust.

## Evidence / Artifacts

- `.gzkit/handoffs/20260914T100618Z-presence-shape-996-justify-binding.md` (predecessor).
- `src/gzkit/governance/trust_audits/evaluation_justify_binding.py`, `src/gzkit/governance/trust_audits/_qc_nc_evaluation.py`, `.gzkit/chores/eval_feedback_cluster_lib.py`.
- `tests/governance/test_justify_binding_gate.py`, `tests/chores/test_eval_feedback_cluster.py`.
- `.gzkit/skills/gz-adr-evaluate/SKILL.md`, `.gzkit/skills/gz-justify/SKILL.md`, `docs/user/manpages/validate.md`.
- Commits `eb91f20b6`, `ab9ce5a4c`, `c6b735985`; GHI #996 close comment; GHI #969 evidence comment.

## Settled Rulings

860 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
