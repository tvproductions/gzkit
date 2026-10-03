---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-03T12:02:28Z'
agent: claude-code
session_id: a9af18d5-a740-4e43-832d-e7166bf5ce6f
continues_from: .gzkit/handoffs/20261003T114257Z-obpi-08-done-decisions-list-called-nonsense.md
---

## Current State Summary

The operator asked for a review of the 11:42Z handoff because OBPI-0.35.0-08 ran badly. Its claims verified against Layer 2: OBPI-0.35.0-08 attested completed, no lock held, main in sync, ADR-0.35.0 at 9 of 14. The run's token cost was then measured from the session transcripts and saved as a dated record with a re-runnable script. The operator ruled a trial: run OBPI-0.35.0-10 in one direct session and compare its cost with that baseline. The trial is prepared and NOT launched; the operator launches it. Nothing is in flight, no lock is held, and no pipeline is active.

## Important Context

Operator concerns this session, verbatim, recorded as concerns and not as rulings: "obpi-0-35-0-08 ran very poorly and makes me question the obpi pipeline for the first time we started using it."; "I am wondering if I'd be better off just asking the agent to `/goal` on the obpi directly."; "I also think that all of our control surface diet work is back to having little or no effect. Every turn becomes a bloated race to 1M tokens. I think the obpi-pipeline is out of control, I think gzkit is out of control. this is highly dismaying. I am willing to try whatever, but I believe I am backed into a corner with gzkit". Measured (figures in the evidence README; re-run the script rather than trusting them): the OBPI-0.35.0-08 run read about 154M cached tokens over 557 API calls; the orchestrator session alone was 260 calls and 77 percent of the reads, its context growing from 55K to 744K tokens with no compaction; the 12 reviewer sessions together were about 22M. The change it landed was 97 lines in one source file. The agent first reported 237M and 802 calls and corrected it the same session: a still-open unrelated session had been counted by file modification time. Sizes read the same day: the gz-obpi-pipeline skill is about 124K characters and no budget covers skills or briefs; root AGENTS.md is over its advisory budget in data/instructions_files_budget.json; ADR-0.35.0 briefs run up to 156K characters and OBPI-0.35.0-10's is 22K. Path-scoped rules load on edit: writing one Python file under docs loaded two rule files. Completion mechanics, read from code and help text and NOT run: gz obpi complete refuses without a recorded proof per requirement and review coverage (acceptance_store.completion_review); a single-driver declaration reduces the required review channels to the adversarial one; the human-review operation of gz obpi acceptance records the operator's verbatim ruling as a tier-3 review, and the completion is then marked degraded-human-only; gz obpi dispatch needs an active pipeline marker; gz obpi pipeline has a --no-subagents single-session mode; the lock and plan-audit checks sit in gz obpi precomplete only. The agent had told the operator the trial would complete through gz obpi complete as now, and corrected that. The trial departs from AGENTS.md (never substitute inline Stage 2); the operator's ruling is the witness for this one OBPI and the rule is unchanged. Workflow fronts (source: the campaign plan, Workflow fronts section): handoff system was worked (resume and this handoff); adr/obpi campaign: the trial was ruled and nothing was implemented; ghi triage was not run; new R&D was not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] Run the single-session trial on OBPI-0.35.0-10 (verbatim: "yes, run the trial on obpi-10").
- [operator-ruled] Write a handoff and sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] Did not launch the trial in the reviewing session: that session's context would have entered the measurement, and the goal command is the operator's to type.
- [agent-chose] Chose the CLI's own single-session route (no-subagents launch, single-driver declaration, human review) for the trial instead of bypassing completion checks.
- [agent-chose] Saved the measurement as a dated evidence record with its script, and recorded one insight, so the comparison can be run from any session.
- [agent-chose] Attributed sibling sessions by the span of their rows after file modification time counted an unrelated open session.

## Immediate Next Steps

1. The operator launches the trial: a fresh session, no handoff resume in it, and the text under Trial launch prompt in docs/governance/obpi-run-cost-2026-10-03-evidence/README.md pasted after the goal command. An agent does not launch it on its own.
2. When the trial session stops, run the script in that README with the trial session's id and time window, and report the three groups beside the size of the change, next to the OBPI-0.35.0-08 baseline.
3. If the trial reaches its condition, completion takes two operator rulings in the operator's own words: the human-review judgment and the attestation. Ask for them; never author them.
4. Leave the gz-obpi-pipeline skill unedited until the operator has seen the comparison and rules on what changes: round caps, a size budget for skills and briefs, or a context reset for the orchestrator.
5. Do not re-present the Stage 4 list the predecessor handoff records; raise one of its items only if the operator asks or it blocks work the operator has started.
6. Tautological-test debt measured 228 outstanding against a ceiling of 229 on 2026-10-03, and the ceiling keeps falling. Measure with uv run python .gzkit/chores/decommission-tautological-tests/check_debt_target.py. The chore is operator-paced.

## Pending Work / Open Loops

Unobserved in the trial route: the no-subagents launch and the single-driver declaration were read, not run; commits touching src or tests need a Task trailer, which may need gz task commands the launch prompt does not spell out; the prompt tells the trial session to stop when a gz command refuses twice for the same reason. The two OBPIs differ in scope, so the comparison is indicative and not controlled. Root AGENTS.md being over its advisory budget is noted here and not repaired. Of the lineage, only this handoff's predecessor and the 11:35Z handoff were read; the 11:38Z one and the older ancestors were not. Carried and not worked: what a session draws when no OBPI is initiated; ADR-0.36.0 naming obpi_complete_adversarial.py as the Step-4b surface; GHI #1154 and GHI #1155; re-completion of the repudiated OBPIs, OBPI-0.35.0-09 among them; trackers #611, #921, #978, #1028 and #799; 35 chores overdue; ghi-triage not run.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after the sync; uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect PENDING until the trial runs; uv run gz obpi lock list: expect no active locks unless the trial is in flight; uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing: expect 9/14; uv run python docs/governance/obpi-run-cost-2026-10-03-evidence/session_token_cost.py 553e5afb-48e8-4cae-be4a-db046a3690ba --siblings-between 2026-10-03T06:55:00+00:00 2026-10-03T11:35:00+00:00: expect the README's baseline rows on the machine that holds the transcripts; uv run gz handoff rulings --search trial: expect this handoff's ruling.

## Evidence / Artifacts

Files: `docs/governance/obpi-run-cost-2026-10-03-evidence/README.md`, `docs/governance/obpi-run-cost-2026-10-03-evidence/session_token_cost.py`, `.gzkit/insights/agent-insights.jsonl`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md`. Predecessor: `.gzkit/handoffs/20261003T114257Z-obpi-08-done-decisions-list-called-nonsense.md`, whose resume decision is booked as proceed with the operator's words. Code read for the completion mechanics: `src/gzkit/acceptance_store.py`, `src/gzkit/commands/obpi_precomplete.py`, `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/obpi_dispatch.py`, `.claude/hooks/pipeline-gate.py`.

## Settled Rulings

1292 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
