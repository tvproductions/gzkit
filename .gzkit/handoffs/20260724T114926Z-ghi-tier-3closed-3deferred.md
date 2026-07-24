---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-24T11:49:26Z'
agent: claude-code
---

## Current State Summary

Worked the operator-authorized 'Handoff GHI tier' (from the 2026-07-24 08:36 handoff). Closed 3 GHIs as governed direct-fixes, all pushed to main and green through pre-commit + pre-push gz check: #665 (scaffold-vs-authored brief distinction in gz adr status, commit 50a42a76), #577 (unified gz status / gz context lane-aware gate projection, 7c04dab5), #573 (single-sourced attestation-verdict classifier, ebbda474). Triaged, reproduced, and deferred 3 with full GHI annotations: #641 (verb collision to Movement IV), #594 (arb receipts unbounded to post-release design), #607 (Pydantic-forced-on-adopters, governance-coupled, execution deferred). Logged 2 course-correction insights (47c06b1a). Re-ran ghi-triage: 19 to 16 open, fresh rank cached. Tree clean, main synced at HEAD (47c06b1a). No active OBPI lock, no in-flight ADR or pipeline.

## Important Context

REPRODUCE-BEFORE-TRUSTING held again on every item. #665's concrete instance had self-healed (ADR-0.31.0 all attested); only the class survived. #577's divergence is reachable ONLY via the deprecated 'gz gates --gate 3' override on a lite ADR; no supported workflow (closeout, implement, default gates) produces it. #573's naive collapse would cycle: the import graph is one-directional (closeout imports ceremony_state), so the canonical home is ceremony_state and closeout imports through the closeout_ceremony facade. The is_terminal_brief_status predicate (brief_structure.py) is the reusable terminal-brief gate; #665 uses it to skip authored-readiness on terminal briefs. #607 IS A GOVERNANCE LANDMINE: audit_code_contract_mismatches is bound to attested REQ-0.14.0-04-04 (OBPI-0.14.0-04 is ATTESTED COMPLETED per the ledger, not just a checkbox), so bare deletion falsifies attested canon. AND the validate framework has NO advisory or warning channel (ValidationError is a frozen extra=forbid model with no severity field), so 'soften to advisory' is NOT direct-fix-sized. My earlier 'direct-fix-sized' estimate for #607 was wrong and was corrected to the operator. Operator doctrine established this session: gzkit's internal design constraints are NOT adopter constraints; a design choice lives in its ADR decision record (ADR-0.15.0 owns the Pydantic choice), not a fail-closed adopter gate; prefer advisory reflection chores over extensive mechanical checks.

## Decisions Made

#577 direction (operator-ruled): shared lane-aware helper project_lane_gates in commands/common.py consumed by BOTH surfaces, not context-only masking or defer; status.py stays behavior-preserving. #641 (operator-ruled): DEFER to Movement IV, a breaking CLI verb rename across 120 refs, not defect repair, best named in the reduction pass beside #618/#581. #594: annotate + defer to governed design; sibling #585 set precedent by routing the identical retention class to an OBPI, not a direct-fix. #607: root-caused and direction decided (de-mechanize the over-aggressive check; ADR-0.15.0 owns the decision; a general architectural-reflection chore is POST-RELEASE per operator), but EXECUTION DEFERRED because it is governance-coupled (attested REQ-0.14.0-04-04) and the validate framework lacks an advisory channel. Recommended focused-pass approach: remove the check from the fail-closed suite AND govern REQ-0.14.0-04-04's rescoping/retirement, paired with the post-release chore. #665 and #573 had no design forks; clean direct-fixes.

## Immediate Next Steps

1. Resume the degrading tier from .gzkit/cache/triage/rank.json in rank order: #696 (handoff decision-state lost across the session boundary, authored 3-5 next steps but only 1 consumed; meta-relevant to this very handoff), then #580 (composition-renderer periphery-bias: critical AGENTS.md mechanical rules rendered mid-file are under-weighted every agent turn), then #614 (correction-mining has no negative-signal telemetry, so silent lexicon decay is indistinguishable from a genuine zero-find). 2. VERIFY reproduction before fixing each item; bodies self-heal and mis-estimate. 3. #607 (ranked 4, degrading) is GOVERNANCE-PARKED: do NOT treat it as a mechanical direct-fix; it needs an operator ruling on retiring or rescoping attested REQ-0.14.0-04-04 first, and the validate framework's missing advisory channel must be solved. Surface before touching code. 4. This is a RESUME: present these steps and obtain explicit operator authorization via gz handoff authorize before executing any of them.

## Pending Work / Open Loops

Deferred-by-decision (annotated, still open): #641 (Movement IV), #594 (post-release design), #607 (governance-coupled; needs the REQ-0.14.0-04-04 ruling plus the post-release reflection chore). #581 and #615 remain open annotated-deferred from the prior session (architecture-scale remainders, not degrading-untouched). The latent tail (ranks 5-16 in rank.json) is unworked by design. No active OBPI locks. No blockers. 2 course-correction insights logged 2026-07-24 under scopes adopter-boundary and defect-fix-routing in agent-insights.jsonl.

## Verification Checklist

gh issue view 665 577 573 --json state (all CLOSED); gh issue view 641 594 607 --json state (all OPEN, annotated); git log --oneline 50a42a76~1..HEAD (session commits 50a42a76 / 7c04dab5 / ebbda474 / 47c06b1a); uv run gz adr status ADR-0.35.0 (OBPI-03 and OBPI-08 render 'draft (scaffold)' while siblings render 'draft', proving #665 live); uv run python -m unittest tests.commands.test_status tests.commands.test_context_cmd tests.test_attestation_verdict_classifier (new coverage green); uv run python -m unittest -q (expect 7336 or more OK); uv run python .claude/skills/ghi-triage/scripts/triage.py --format rank --rank-input .gzkit/cache/triage/rank.json (renders the 16-item ranking).

## Evidence / Artifacts

Session fix commits: #665 50a42a76, #577 7c04dab5, #573 ebbda474, insights 47c06b1a (HEAD, main, synced ahead=0 behind=0). Changed surfaces: `src/gzkit/commands/status_obpi_inspect.py`, `src/gzkit/commands/status_obpi.py`, `src/gzkit/commands/status_render.py` (#665); `src/gzkit/commands/common.py`, `src/gzkit/commands/status.py`, `src/gzkit/commands/context_cmd.py` (#577); `src/gzkit/commands/closeout.py`, `src/gzkit/commands/ceremony_state.py` (#573). New test: `tests/test_attestation_verdict_classifier.py`. Fresh triage ranking: `.gzkit/cache/triage/rank.json`. Session insights: `.gzkit/insights/agent-insights.jsonl`. #607 diagnosis surfaces: `src/gzkit/instruction_audit.py`, `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`.
