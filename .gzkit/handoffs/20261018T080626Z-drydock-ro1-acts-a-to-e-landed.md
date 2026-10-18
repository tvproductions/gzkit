---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T08:06:26Z'
agent: claude-code
session_id: 0b7ff53e-3083-4747-9b5f-cc5a1a8b3cb2
continues_from:
- .gzkit/handoffs/20261017T114454Z-drydock-ro1-ready-for-cheaper-session.md
- .gzkit/handoffs/20261017T115019Z-session-exit-bookmark.md
---

## Current State Summary

RO-1 acts (a) to (e) are landed and pushed under docs/governance/harbor-pilotage-candidate-2026-10-15.md, one commit per act, each with its passage-log row; act (f), WP-13's budget witness over every loaded surface, is the one act of RO-1 still open. Commits since the predecessor (eae913ff8): e8528b0c9 act (a), session-start text on one channel, 9,848 B to 3,974 B; 69d8f6f86 act (b), the dead instruction-router hook retired for gzkit and adopters; 170d62a2c act (c), skill descriptions to one sentence, 13,229 to 5,938 chars over 62 skills; 6d36c8ec8 act (d), 25 rule version banners lifted to rule-version-history, rules 161,070 B to 154,985 B; 953cf8fc4 act (e), the governance read mandate scoped to the Coverage Ledger section, 237,282 B of mandated reading to 3,413 B plus the touched rule's rows. Red-witness receipts, final cut of each act: (a) arb-red-commit-e8528b0c9ae0-ff9ce52f36844532842f9796fc742f01, inconclusive, 38 killed, 0 survived, 9 declaration hunks inconclusive; the two earlier cuts were undriven (arb-red-commit-422b8a4c3350-f3e2d7fbe24f4a40988b8e0065b70ffd on 27 hunks, arb-red-commit-cd718eed2759-b43370a2c3124e22949ad495e41f3742 on 4) and were repaired before push. (b) arb-red-commit-69d8f6f869ee-47c3f665307c4d109901778a8f472639, driven. (c) arb-red-commit-170d62a2c6b7-323e03d083d14495a93cd792cb5d5378, no-production-hunks. (d) arb-red-commit-6d36c8ec811b-b7e9d54d6e57403991c77ce665c97317, inconclusive, 0 survived; the earlier cuts were undriven (arb-red-commit-38536e75516e-08fbe65d1daa46b39f79c8d97093c9fd, arb-red-commit-8ec4881fbc2f-d90b3344aad84d06839ffb993762aad0) and were repaired before push. (e) arb-red-commit-953cf8fc4b1e-f00c8748988d4060bde2cce1db41d18a, no-production-hunks. The 2026-10-17T11:50 exit bookmark recorded a six-minute session that changed nothing; this handoff supersedes it. Main is in sync with origin.

## Important Context

Safe mode is still open (.gzkit/mx.json mode safe, contract harbor-pilotage-candidate-2026-10-15.md), so every guard outside GATE5_INVARIANTS is advisory and a gz validate or gz check exit code there proves less than it seems. Act (d) found exactly that: --advisory-scorecard had carried a real mx-mode.md drift since RO-0 (rule 1.6.0 against a ledger row of 1.5.2, row 62f still saying safe mode does not demote), hidden by the demotion. Read such scopes by calling their audit functions and reading the error lists, not the exit code. The mx-session lock held by claude-code-696ca9a4 (the RO-0 session) stood at 1,409 of 1,440 TTL minutes at authoring, so the next SessionStart may reap it per token-block-discipline Sub-Invariant 4; what reaping does to the open safe-mode marker is unverified. The orientation is now the single session-start channel: its handoff section hosts the advisement (gzkit.session_start), and the advisement hook is registered only where scripts/session_orientation.py is absent, so adopters keep it on additionalContext. The act (c) routing read used the 134-goal trigger basket of 2026-10-10 with one blind sonnet pass per set; the report is .gzkit/chores/skill-trigger-testing/proofs/routing-2026-10-17-report.md. The act (e) landing went through gz content remember, retire and land with a retention map whose conditions a separate spec-reviewer extracted; the operator's words were passed verbatim with the dropped condition ids appended as evidence. Workflow fronts per the campaign: this session worked the handoff-system front only through this document; the drydock is the governing work.

## Decisions Made

- [operator-ruled] RO-1 proceeds starting at act (a) (verbatim: "proceed with RO-1, starting at act (a)"); booked with gz handoff decide against the predecessor.
- [operator-ruled] RO-1 act (a) uses the orientation as the one session-start channel (verbatim selection: "Orientation only (Recommended)"); insight scope drydock-ro1a.
- [operator-ruled] Acts (b), (c) and (d) proceed in turn (verbatim: "proceed with RO-1 act (b)", "proceed with RO-1 act (c)", "proceed with RO-1 act (d)").
- [operator-ruled] RO-1 act (e) takes wording A for the governance read mandate (verbatim selection: "A: Ledger + scoped (Rec.)"); passed as the corpus attestation; insight scope drydock-ro1e.
- [operator-ruled] The session handoff is written now, before act (f) (verbatim: "write the session handoff now, citing the five acts' receipts").
- [agent-chose] Adopters keep the advisement hook on additionalContext only, because the orientation script exists only in gzkit; the Claude generator and Codex sync omit it where the orientation exists.
- [agent-chose] The rule-version-markers validator gained banner-not-one-sentence, mechanizing skill-surface-sync rule 2's one-sentence rationale so the banners cannot regrow.
- [agent-chose] No skill was made disable-model-invocation in act (c); which skills the agent need not reach on its own is the operator's choice.
- [agent-chose] Coverage Ledger row 62f was re-scored to R6 and mx-mode.md moved to 1.6.1, repairing the drift act (d) surfaced.

## Immediate Next Steps

1. Operator: rule on the mx-session lock before or at the next session start: let the SessionStart hook reap it at TTL, or release it through gz-session-handoff; confirm what either does to the open safe-mode marker before it happens.
2. Next session: RO-1 act (f), WP-13's budget witness (GHI #1249): every loaded surface in data/instructions_files_budget.json, measured by gz validate --instructions-files-budget against the contract's exit numbers, with skill descriptions read by a YAML parse (insight scope gzkit.skill_contract.parse_frontmatter) and the session-start text budget moved from the test constant into the budget file.
3. After act (f): close GHI #1249 through ghi-close, and assess #1246 and #1252: #1246's description cut landed in act (c), but its rules narrative lift is RO-7 work; #1252's protocol has its first stage reads (readiness eval per act, the act (c) routing report) and needs the per-stage report series.
4. Session that specifies: RO-2, the identity seam, as the predecessor advised.
5. Operator: two offered follow-ups await a ruling: a repair order to let a model correct AGENTS.md inside the drydock and relock it under a retention map, attestation and re-armed witnesses; and a WP-16-style measure of the content CMS's validators, code and caught defects to size what to keep.

## Pending Work / Open Loops

- GHI #1249 (act f), #1246 and #1252 stay open; RO-7 owns the rest of the cut.
- detect_claude_settings_drift compares 4 of the 6 hook phases gzkit owns; SessionStart and SessionEnd drift is invisible (insight scope gzkit.sync_surfaces.detect_claude_settings_drift); no GHI yet.
- gzkit.skill_contract.parse_frontmatter and sync_skills._extract_skill_description read a block-scalar description as its first line (insight recorded); act (f) should measure through YAML.
- The session-start text can still pass 4 KB when the advised steps or the account's commit list are long; act (f)'s witness measures it on the real tree.
- Carried from the predecessor: RO-5's repair tagging scheme undesigned; the orientation does not print the drydock's repair orders (GHI #1245); 136 docs carry absolute local paths (insight scope docs-absolute-local-paths); briefs 17 and 20 stay PENDING by R4.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0 and HEAD is 953cf8fc4 or later.
- uv run gz obpi lock list shows the mx-session lock's state, or its reap record.
- echo '{}' | uv run python scripts/session_orientation.py | wc -c reports under 4,000 bytes on an ordinary tree.
- uv run python -m unittest tests.scripts.test_session_orientation tests.governance.test_session_start tests.test_hooks tests.test_codex_hooks tests.validators.test_rule_version_markers passes.
- uv run python -c 'from pathlib import Path; from gzkit.governance.trust_audits.release import audit_advisory_scorecard; print(audit_advisory_scorecard(Path(".")))' prints an empty list (read directly, since safe mode demotes the scope's exit code).
- uv run gz handoff rulings --search 'Ledger + scoped' returns the act (e) ruling.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` — the contract; five new passage-log rows, one per act.
- `scripts/session_orientation.py` and `src/gzkit/session_start.py` — the one session-start channel.
- `src/gzkit/hooks/claude.py` — the advisement registration and the retired instruction-router.
- `src/gzkit/validators/rule_version_markers.py` — the banner-not-one-sentence check.
- `docs/governance/rule-version-history.md` — the 25 lifted banners.
- `docs/governance/advisory-rules-audit.md` — the Coverage Ledger rows moved with each rule and row 62f re-scored.
- `.gzkit/chores/skill-trigger-testing/proofs/routing-2026-10-17-report.md` — the act (c) routing read with its inputs and picks.
- `.gzkit/chores/instructions-files-diet/proofs/retention-map-2026-10-18-ro1e.json` — the act (e) retention map.
- `.gzkit/insights/agent-insights.jsonl` — the session's rulings and defects.

## Settled Rulings

1583 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
