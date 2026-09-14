---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-14T10:06:18Z'
agent: claude-code
session_id: 735b8082-6bf0-4a83-ac46-f9af2c98b706
continues_from: .gzkit/handoffs/20260914T084920Z-exit-status-shape-session-close.md
---

## Current State Summary

Session 735b8082 resumed `20260914T084920Z-exit-status-shape-session-close.md` and worked family-A shape: presence. Pushed at `ab9ce5a4c`; origin/main level (`0 0`); no OBPI locks; 43 open GHIs (search total_count).

- Full-body read and ownership check of the four presence members. #996 and #994 have no live brief; #983 is touched by PENDING ADR-0.35.0 briefs (OBPI-0.35.0-07 declares `content/ownership.py` read-only, -10 binds on corpus-owned, -13 reads it); #894 stays blocked on OBPI-0.35.0-08 (IN PROGRESS, no lock) and the 2026-09-07 awaiting-ruling booking.
- Finding put to the operator: the drafted class fix (a present-but-false declaration on `@enforces`) reaches none of the four open instances, because their witnesses are not registered claims.
- GHI #996 fixed in `eb91f20b6` and closed with a cause-to-test table. The justify-binding qualifier now requires parse + complete + frontmatter subject + generated after the evaluation. Enrolled as claims `evaluation-justify-binding` / `evaluation-justify-binding-qualified`. Repaired the eval-feedback-cluster regression it exposed (template and hints text read as confusion). gz-adr-evaluate footer, gz-justify skill, validate.md and BDD step updated.
- Live scope unchanged: exit 3 on ADR-0.33.0-airlock-membrane, ADR-0.35.0, ADR-0.35.0-canon-entry-corpus-landing.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** no change.
- **ghi triage:** presence shape begun. #996 closed; #994 remains the one presence member free of live-brief ownership; #983 and #894 need operator routing. Evidence added to #969 (second harness-green-over-red instance). Queue 43 open.
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 TOPMOST unchanged. The three live justify-binding violations include ADR-0.35.0; answering them needs genuine reasoning on an OBPI under the ADR or its draft slug, never invented text.
- **new R&D:** not worked.

### Gotchas learned
- `src/gzkit/chores/*.py` libraries have canonical copies under `.gzkit/chores/`; `gz agent sync control-surfaces` overwrites an edit made to the src copy.
- The walkthrough parser breaks sections only at `## `, so the `### Authoring-time complexity hints` block lands inside section 8's reasoning, and every producer-written walkthrough contains "not sure" and "uncertain" from its template.
- A reconstructed walkthrough anchor has `body=None`; a mutant reading the anchor body is equivalent and survives by construction.
- A helper named `_outcome` in a unittest TestCase shadows a unittest internal.
- The background notification again said exit 0 over `GZ CHECK REAL EXIT: 1`; read the file.

## Decisions Made

- [operator-ruled] Resume ruling on `20260914T084920Z`: "Presence shape (Recommended)". Cap-not-reduction, population drain and the short direct repairs set aside.
- [operator-ruled] Presence shape route: "Fix #996 + enroll (Recommended)". Class-mechanism-first, #983 ruling and #894 ruling set aside for now.
- [operator-ruled] ADR evaluation binding: "Draft slug or OBPI (Recommended)". A low ADR evaluation is answered by a draft walkthrough whose slug is the ADR id dotted to dashed, or by a walkthrough on an OBPI under that ADR; a tracking-GHI walkthrough never discharges it; the gz-adr-evaluate footer fires on the gate's own condition.
- [agent-chose] Kept REQ-0.0.19-04-05's three assertions true at the surface (threshold cited with its data file as authority, footer requires an OBPI, justify suggestion kept) and recorded the amendment in the skill, per governance-core's attested-REQ rule, rather than editing its test.
- [agent-chose] Declined the reviewer's OBPI-existence finding: frontmatter self-identity is the evidence channel, and a hand-written draft slug can claim any ADR identically.

## Immediate Next Steps

1. Put the next presence member to the operator: #994 (no live owner; remedy arm, prompt contract vs import-time check, is open in its body) is the direct-fix candidate.
2. For #983, surface the routing facts: live PENDING briefs OBPI-0.35.0-07/-10/-13 read the ownership surface, and the disposition of the 10 uncovered sections is operator-ruled.
3. #894 stays awaiting the operator's ruling on relocating `_is_named` while OBPI-0.35.0-08 is IN PROGRESS; do not treat it as next eligible.
4. The class-wide presence declaration on `@enforces` (inventory plus grandfather) remains an option; it covers future checks, not the open instances.

## Pending Work / Open Loops

- GHI #994, #983, #894 open (presence); #969 open by ruling; #1008 open, unselected.
- Insight still open: `src/gzkit/commands/obpi_stages.py` BASELINE_VERIFICATION prescribes `uv run -m unittest -q` rather than the canonical unittest step.
- Three live justify-binding violations (ADR-0.33.0-airlock-membrane, ADR-0.35.0, ADR-0.35.0-canon-entry-corpus-landing) need genuine walkthroughs; the gate is opt-in, not in the gz check default scope.
- 83 enforcement claims still disclosed population-undeclared; 55 exemption-undeclared.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
gh issue view 996 --json state
uv run gz obpi lock list
uv run -m unittest tests.governance.test_justify_binding_gate tests.chores.test_eval_feedback_cluster tests.skills.test_skill_surface_sync_justify
uv run gz validate --evaluation-justify-binding --json
uv run gz validate --exemption-controls
```
Expected at authoring: `0 0` apart from this handoff's sync; #996 CLOSED; no locks; tests green; the justify-binding scope exits 3 on exactly three ADR ids; exemption-controls exit 0 with 88 claims. Re-run rather than trust.

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/evaluation_justify_binding.py` — qualifier, subject keys, refusal prose.
- `src/gzkit/governance/trust_audits/_qc_nc_evaluation.py` — refuse and admit fixtures; registrations in `src/gzkit/governance/trust_audits/_qc_negative_controls.py`, `src/gzkit/governance/trust_audits/_qc_claim_exemptions.py`, `src/gzkit/governance/trust_audits/_qc_claim_populations.py`.
- `.gzkit/chores/eval_feedback_cluster_lib.py` — authored-text keyword read.
- `tests/governance/test_justify_binding_gate.py`, `tests/chores/test_eval_feedback_cluster.py`, `features/steps/evaluation_feedback_loop_steps.py`.
- `.gzkit/skills/gz-adr-evaluate/SKILL.md` (6.8.0), `.gzkit/skills/gz-justify/SKILL.md` (6.2.0), `docs/user/manpages/validate.md`.
- Commits `eb91f20b6`, `ab9ce5a4c`; GHI #996 contract amendments and close comment; #969 evidence comment.

## Settled Rulings

857 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
