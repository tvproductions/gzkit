---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-15T10:36:13Z'
agent: claude-code
session_id: f6dec6b5-558f-4ce0-bac2-a6eb07ccb646
continues_from: 20260915T102720Z-rnd-skill-and-campaign-rebalance.md
---

## Current State Summary

Continues `20260915T102720Z-rnd-skill-and-campaign-rebalance.md` in the same session. The operator is clearing context to continue the R&D design DISCUSSION in a fresh session.

What changed since the predecessor:
- **The R&D design is reopened as a discussion.** The operator: "the rnd was supposed to come with an extended discussion". The agent had compressed the six open design questions into one accept-all menu and authored `gz-rnd` on the answer. That menu's preview was likely clipped in the terminal UI, so the operator may not have seen the text. `docs/governance/rnd-discipline.md` and `.gzkit/skills/gz-rnd/SKILL.md` (committed in `b7fc95e95`) are PROVISIONAL until the discussion concludes. Whatever it settles replaces them, up to deleting the skill.
- **The campaign amendment stands** (§ Amendments 2026-09-15), re-confirmed after its three ratified items were shown in full in chat.
- **AskUserQuestion previews clip long text with no way to scroll** — Claude Code issue #38674 (closed, not planned), verified with `gh issue view`. Long text goes in chat before any question; previews stay short.

At authoring: HEAD `930227588` level with origin/main; the only change is one uncommitted insight line; no OBPI locks.

## Important Context

### THREAD (own line, per amendment item 2): the R&D design discussion
- Records: `docs/governance/mpas-appropriation-analysis.md` § Questions for the design session (the open questions and their evidence), and `docs/governance/rnd-discipline.md` (the agent's provisional answers, NOT operator-ratified in substance).
- Operator framing, verbatim, 2026-09-13: "the mpas appropriation is meant to generate a design discussion, not a wholesale onboarding." Held 2026-09-12: "it is a chargé d'affaires for retaining and organizing possible outcomes from an R&D designing session. I expect outcomes, but need to understand possibilities for outcomes throughout and as a result of an R&D session. this skill should be sensing but also direct executable."
- **The discussion's first two questions, already put to the operator and unanswered.** The rest depend on them:
  1. **Sensing: who starts an R&D run?** The operator said a paste is "almost always an occasion for R&D". The provisional design makes `gz-rnd` operator-invoked only (`disable-model-invocation: true`), so the agent cannot react to a paste, which reads "sensing" out of the design. The alternative: the agent recognizes an R&D occasion and asks whether to open a run. Trade-off: agent initiative at the start of a run.
  2. **Outcomes throughout or only at the end?** The provisional design fills the Outcomes table only in the final precipitate phase. The operator's "throughout" suggests a live picture as the discussion moves. Trade-off: MPAS "hide the downstream step" protects the discussion from rushing toward conclusions, against seeing late where things are heading.
- **Discussion form.** Put questions in chat, with the operator's own quotes and the tension. Take one dependency frontier at a time, rough thinking welcome. Do not use an accept-all menu, and do not author until the operator rules on substance.

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **new R&D:** first in drawn-work order. The design discussion above is the live item.
- **chore estate:** second. Board at 36 overdue / 1 due / 3 unmeasured at the predecessor's authoring; #997, #808, #1009, #1011 open; staleness-gate inconsistency unruled.
- **ghi triage:** third, narrowed by the amendment; #1013 (heredoc bodies) blocks heredoc authoring.
- **adr/obpi campaign:** unchanged; ADR-0.35.0 TOPMOST; OBPI work only on operator initiation.

## Decisions Made

- [operator-ruled] After the three ratified amendment items were shown in full in chat: "the amendment stands, let's continue the rnd discussion after a h/o (context window filling up)".
- [agent-chose] Hold `gz-rnd` and `rnd-discipline.md` as provisional instead of reverting `b7fc95e95`. The skill is operator-invoked only, so it stays inert until the discussion rules on it.

## Immediate Next Steps

1. Resume the R&D design discussion: re-present the two open questions from Important Context (sensing / who starts a run; outcomes throughout or at the end) in chat, with the operator's quotes, and wait for their thinking before anything else.
2. Carry the discussion through the remaining questions in `docs/governance/mpas-appropriation-analysis.md` § Questions for the design session, one dependency frontier at a time. Record the operator's rulings verbatim as they land.
3. When the discussion concludes, revise `docs/governance/rnd-discipline.md` and `.gzkit/skills/gz-rnd/SKILL.md` to what was settled, or delete the skill if the shape changed. Run `uv run gz agent sync control-surfaces` and `uv run gz check`, then commit.

## Pending Work / Open Loops

- The two discussion questions above, unanswered.
- `gz-rnd` and `rnd-discipline.md` are provisional, and their manpage, index, nav and router entries go with them if the skill is revised or removed.
- Chore estate: 36 overdue; #997, #808, #1009, #1011; staleness-gate inconsistency.
- GHIs #1012, #1013 open. Carried: #810, #934, #983 and #894 ruling-gated, #969, #968.
- Untracked except in handoffs: the shared lexer reads a quoted lone metacharacter as an operator.

## Verification Checklist

```bash
git status -sb
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
grep -n "Status:" docs/governance/rnd-discipline.md
gh issue view 38674 --repo anthropics/claude-code --json state,stateReason
```
Expected: level with origin; no locks; the rnd-discipline status line present (it reads RULED, which this handoff records as provisional); #38674 CLOSED/NOT_PLANNED.

## Evidence / Artifacts

- `.gzkit/handoffs/20260915T102720Z-rnd-skill-and-campaign-rebalance.md` (predecessor).
- `docs/governance/rnd-discipline.md`, `.gzkit/skills/gz-rnd/SKILL.md`, `docs/governance/mpas-appropriation-analysis.md`.
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` (§ Amendments 2026-09-15).
- `.gzkit/insights/agent-insights.jsonl` (insight scope agent/rnd-design-needs-dialogue).
- Commits `b7fc95e95`, `930227588`.

## Settled Rulings

875 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
