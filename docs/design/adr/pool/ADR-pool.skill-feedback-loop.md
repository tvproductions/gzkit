---
id: ADR-pool.skill-feedback-loop
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: nousresearch/hermes-agent skill_manager_tool.py
---

# ADR-pool.skill-feedback-loop: Skill Feedback Ledger Events for Human-Reviewed Improvement

## Status

Pool

## Date

2026-04-16

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add a `skill_feedback` ledger event so agents can flag when a skill's
instructions led to a suboptimal path, creating a human-reviewed improvement
queue that closes the learning loop without autonomous self-modification.

---

## Target Scope

- Define a `skill_feedback` ledger event schema: `skill_id`, `session_id`, `outcome` (success/suboptimal/failure), `observation` (concrete description of what went wrong), `suggestion` (proposed improvement).
- Add `gz skill feedback <skill-id> --outcome <outcome> --observation "..."` CLI surface for emitting feedback events.
- Add `gz skill feedback-report [--skill <id>]` to surface accumulated feedback as a human-reviewable queue.
- Define the review workflow: human reads feedback, edits the canonical skill in `.gzkit/skills/`, bumps `skill-version`, runs sync.
- Integrate feedback emission into the OBPI pipeline's post-implementation stage — if a skill was wielded and the agent encountered friction, emit feedback before completing.

---

## Non-Goals

- No autonomous skill editing — agents propose, humans approve. This is the governance boundary.
- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No skill quality scoring or ranking — feedback is qualitative, not quantitative.
- No cross-repo skill sharing — feedback is project-scoped.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.skill-behavioral-hardening (enriches skills with defense patterns; feedback loop identifies which skills need hardening), ADR-pool.session-productivity-metrics (feedback is a dimension of session productivity)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Ledger event schema for `skill_feedback` is accepted.
3. Review workflow (feedback queue → human edit → version bump → sync) is agreed upon.

---

## Inspired By

[NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) —
Hermes agents autonomously create and edit SKILL.md files via
`skill_manager_tool.py`, closing a learning loop where solved problems become
reusable procedural memory. The power of the pattern is capturing learning
signal at the moment of friction. The risk is autonomous self-modification
without review. gzkit's adaptation preserves the learning signal (ledger
event at the moment of friction) while routing the modification through human
review (Gate 5 attestation pattern applied to skill edits).

---

## Notes

- The feedback event must capture enough context to be actionable months later: which skill, which step in the skill, what the agent tried, what went wrong, and what would have been better.
- Consider: should feedback events reference the OBPI brief that was active when the friction occurred? This would enable tracing "skill X caused friction during OBPI Y" patterns.
- Hermes's self-improvement works because it operates in low-stakes environments (personal assistant tasks). gzkit operates in governance-critical environments where a bad skill edit could silently break a gate ceremony. Human review is non-negotiable.
- The feedback queue is a natural chore: `gz chores` could surface "N unreviewed skill feedback events" as a maintenance item.
