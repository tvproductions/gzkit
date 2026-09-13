---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-13T12:40:03Z'
agent: claude-code
session_id: 3a6e7568-21a3-4990-a17d-ece63e598e8b
continues_from: .gzkit/handoffs/20260913T100146Z-chores-revamp-status-and-ghi-classes.md
---

## Current State Summary

Session 3a6e7568 resumed `20260913T100146Z-chores-revamp-status-and-ghi-classes.md` (Fresh). Resume ruling booked with `gz handoff decide`: proceed on option A (chores-revamp step 5 with GHI #1006 alongside); step 2 (`gz chores status`, GHI #936) and pausing the revamp were set aside.

Landed and pushed to main (HEAD `980691150`, level with origin, clean tree, no locks):
- `96b447bf5`, GHI #1006 CLOSED: `gz validate --cli-alignment` now also scans `.gzkit/chores/**/*.md` (excluding `proofs/`), `.gzkit/rules/**/*.md` and root `AGENTS.md`, and the manpage-filename check reads the same enumeration. The 8 unresolved chains in 4 chores were fixed: the complexity verbs renamed, and `gz obpi park`, `gz pool *` and `gz superbook` marked. governance-core.md is at 0.15.0 and scorecard row 17e was re-scored.
- `980691150`, GHI #999 step 5 (the issue stays OPEN for step 6): all 40 chores are declared (class, rung, idempotent, staleness, remediation, nonAuthority, governingRule) and every Workflow step carries a stage. The control-surface five were calibrated with the operator one at a time. The stop-at-data and self-contradictory chores were remedied, and the later Pass D was retitled Pass E. `gz chores run` now REFUSES an undeclared chore (exit 1), and `audit_chore_rung_conformance` fails on one. `scripts/check_proof_freshness.py` now reads a chore's declared elapsed-time `periodDays` (`_SCAN_INTERVALS` deleted) and counts only PASS run blocks.

## Chores revamp — status at a glance

Plan: `docs/governance/chore-class-system.md` § Implementation order. Work orders: GHI #999 (steps 1, 3–6) and GHI #936 (step 2).

| Step | Status |
|---|---|
| 1. Registry schema | DONE `f1c9b0e59` |
| 2. `gz chores status` indicator + orientation announcement | NOT STARTED — GHI #936, set aside at three resume rulings |
| 3. Rung-conformance validator | DONE `6615d0a18`; fence blindness fixed in `980691150` |
| 4. README: classes, rungs, admission | DONE `16caf8392` |
| 5. Declare all 40; remedies; calibrate the control-surface five; flip absence to refusal | DONE `980691150` |
| 6. Suppression prohibition as rule text with its witness | NOT STARTED — the last step under GHI #999 |

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** no change this session. GHI #1003 and GHI #870 untouched.
- **ghi triage:** closed GHI #1006 (a family-A instance: a check covering less than its claim). No GHIs filed. The family-A class recommendation from the predecessor is still unruled.
- **adr/obpi campaign:** no OBPI work (IRON LAW) and no locks. ADR-0.35.0 remains TOPMOST and untouched.
- **new R&D:** not worked.

### What step 5 decided, so it is not re-derived
- Remediation categories: `vendor_fix` when the chore, or its declared paired repair chore, applies the repair; `no_fix_planned` when the chore stops at propose and the repair is an operator ruling or edit outside the chore system.
- Staleness by class: conformance and coherence use content-delta with graceDays 7; curation uses accumulated-work (memory-hygiene uses content-delta); mining and currency use elapsed-time, periodDays 30, graceDays 7. Two exceptions carry recorded reasons: `decommission-tautological-tests` is accumulated-work (a reduction chore, GHI #808), and `control-surface-permission-consent-drift` is elapsed-time (`settings.local.json` is gitignored).
- A repair that touches operator-authored canon (skills, rules, corpus, model-sourced doctrine, a permission grant) is `operator-only-repair`, per README § The Four Rungs.
- Step stage = what the step does. Writing a proofs artifact is observe; recommending is propose. A chore's rung equals its highest stage.

### Live readings after the change (announcements, not gz check failures)
- `control-surface-permission-consent-drift` is overdue: last PASS run 2026-08-09 against a 30-day period.
- `control-surface-rule-conflicts` proofs are stale: `.gzkit/rules` moved this session.
- The predecessor's stale `control-surface-skill-rule-reachability` proofs presumably remain.

### Gotchas learned
- The `spec-reviewer` agent's definition (`.claude/agents/spec-reviewer.md`) caps it at 15 turns. A 45-file review exhausted the cap before any report was written. Split large reviews, or scope each to a few files.
- `gz agent sync control-surfaces` regenerates `src/gzkit/chores/**` from `.gzkit/chores/**`: edit the `.gzkit` copy, never the wheel copy, or sync reverts it.
- `gz validate --tautological-test-audit` refuses a test that `read_text`s a live file and asserts. Inject the state in a temp root, or call an audit function.
- The verifier-pipe gate refuses `ruff` followed by any other statement; run it on its own.
- `audit_chore_metadata_authority` requires the newest change note in a CHORE.md to match the registry version. Bump a chore that has a history note together with a new note.

## Decisions Made

- [operator-ruled] Resume ruling on `20260913T100146Z`: "A" (chores-revamp step 5, with GHI #1006 alongside). Step 2 (`gz chores status`, GHI #936) and pausing the revamp were set aside.
- [operator-ruled] Step 5 calibration 1, control-surface-rule-conflicts: "As drafted (Recommended)" — coherence at propose. This confirms "stay diagnostic" lands at the propose rung, which still owes a recommendation.
- [operator-ruled] Step 5 calibration 2, control-surface-skill-rule-reachability: "Propose, every gap row (Recommended)".
- [operator-ruled] Step 5 calibration 3, control-surface-rule-vs-check-drift: "Propose, per-verdict recs (Recommended)".
- [operator-ruled] Step 5 calibration 4, control-surface-permission-consent-drift: "Operator-only repair (Recommended)", with the class corrected to "conformance (Recommended)".
- [operator-ruled] Step 5 calibration 5, control-surface-validator-reachability: "As drafted (Recommended)".
- [operator-ruled] Pass-label collision: "Later one becomes Pass E (Recommended)".
- [agent-chose] Widened GHI #1006's scan to `.gzkit/rules/**` and root `AGENTS.md` as well as chore docs. The measurement showed both unscanned (0 unresolved), in the same failure class; the contract amendment is recorded in the close comment.
- [agent-chose] Declared the 35 remaining chores without a per-chore ruling, applying the operator's standing directives (class seams; "please fix/make consistent"; stopping at data "needs rememdy") and README canon. Every judgment call is listed on GHI #999 for review.
- [agent-chose] Made the freshness gate read declared staleness rather than keeping `_SCAN_INTERVALS` beside the declarations. Two authorities already disagreed for permission-consent-drift. The step-2 status verb (GHI #936) will build on the declaration.
- [agent-chose] Fixed the spec reviewer's blocking finding (FAIL run blocks reset the clock) before committing. Its non-blocking notes were also applied: the settings patch became a required artifact, the stale criterion description was fixed, and the staleness exceptions now carry reasons.

## Immediate Next Steps

1. Put the step-5 follow-ups to the operator: (a) the `test-isolation-compliance` profiler fails the parallel suite over 60s, while `.gzkit/rules/tests.md` § General Rules retired a full-unit-tier ceiling (the suite ran 90.9s on 2026-09-13) — drop the ceiling, or re-scope it to the smoke tier; (b) `frontmatter-ledger-coherence` rewrites OBPI frontmatter at plain `repair` while briefs are otherwise operator-only — the design record approves it, so decide whether it stands.
2. Put the next chores-revamp move to the operator: step 6 (the suppression prohibition as rule text with its witness, GHI #999) or step 2 (`gz chores status`, GHI #936).
3. If step 6: read `docs/governance/chore-class-system.md` § Suppression and the Movement C box constraint (the rule and its witness land together, so no new Promotable scorecard row), then draft the rule clause and witness for operator review.
4. Put the family-A recommendation (carried from the predecessor, still unruled) to the operator: work "a witness covers less than its claim" as one class under the Movement C box. GHI #1006 [settled] and the fence-blind rung audit were two more instances this session.

## Pending Work / Open Loops

- GHI #999 step 6: the suppression prohibition in a rule file, with its witness.
- GHI #936 (step 2, status verb) — set aside at three resume rulings. It should read the declared `staleness` fields; `scripts/check_proof_freshness.py` now reads `periodDays` from the registry and can be generalized.
- GHI #997 (`eval-feedback-cluster` runs fixtures, not live clustering) and GHI #808 (`decommission-tautological-tests` criteria gate the ratchet, not the debt) — open, not declaration defects.
- `test-isolation-compliance` 60s suite ceiling vs `tests.md` — recorded as a defect insight in `.gzkit/insights/agent-insights.jsonl`; the fix direction needs an operator ruling.
- Overdue or stale chores: permission-consent-drift (overdue), rule-conflicts (stale proofs), skill-rule-reachability (stale per the predecessor).
- `complexity-reduction-xenon`'s post-cluster mode still waits on the `.gzkit/rules/pythonic.md` threshold ruling.
- `config-paths-remediation` and `hardcoded-root-eradication` overlap heavily (both config-first) — noticed, not raised as a finding.
- The GHI #1006 [settled] widening does not scan vendor mirrors or wheel copies; those are held byte-equal by `gz validate --distribution` (a stated limit).
- GHI #1003 (Movement D ruling identity), GHI #870, GHI #810 untouched.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
gh issue view 999 --json state,title
gh issue view 1006 --json state,title
gh issue view 936 --json state,title
uv run gz chores list
uv run gz validate --cli-alignment
uv run -m unittest tests.governance.test_chore_rung_conformance tests.governance.test_chore_metadata_authority tests.governance.test_scan_interval_gate tests.commands.test_chores_declaration tests.governance.test_cli_alignment_scope
uv run python scripts/check_proof_freshness.py frontier-model-card-currency
uv run gz handoff rulings --search "Later one becomes Pass E"
```

Expected at authoring: `0 0`; no active locks; #999 OPEN; #1006 CLOSED; #936 OPEN; `gz chores list` prints no undeclared-chore notice; cli-alignment exit 0; tests green; the frontier gate exits 0 (last PASS run 2026-09-12); the ruling is found. Re-run these rather than trust them.

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/cli.py` — widened `_cli_alignment_sources`; `_manpage_alignment_sources` reads it (GHI #1006).
- `tests/governance/test_cli_alignment_scope.py`, `tests/governance/test_manpage_alignment.py` — scope witnesses.
- `.gzkit/rules/governance-core.md` 0.15.0, `docs/governance/rule-version-history.md`, `docs/governance/advisory-rules-audit.md` row 17e, `docs/user/manpages/validate.md`.
- `.gzkit/chores/registry.json` — 40 declarations; `.gzkit/chores/*/CHORE.md` — stages and remedies.
- `src/gzkit/commands/chores.py` — refusal of undeclared chores; `src/gzkit/governance/trust_audits/chores.py` — `_mask_fences`, undeclared-chore finding.
- `scripts/check_proof_freshness.py` — declared-period arm; PASS-only run stamps.
- `tests/commands/test_chores_declaration.py`, `tests/commands/test_chores.py`, `tests/governance/test_chore_rung_conformance.py`, `tests/governance/test_chore_metadata_authority.py`, `tests/governance/test_scan_interval_gate.py`.
- `src/gzkit/chores/README.md`, `docs/user/manpages/chores-run.md`, `docs/user/manpages/chores-list.md`, `docs/governance/chore-class-system.md`, `docs/governance/rules-tools-audits-refactors-alignment.md`, `.gzkit/skills/gz-intent-trace/SKILL.md`.
- Commits `96b447bf5`, `980691150`; GHI #1006 close comment; GHI #999 comments for the control-surface rulings and the step-5 landing.

## Settled Rulings

838 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
