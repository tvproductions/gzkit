---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-09-27T16:50:44Z'
agent: claude-code
session_id: 9c70e8e2-365b-4a4e-9c05-8bcdf332f3a2
continues_from: .gzkit/handoffs/20260927T164026Z-skills-packaging-design-discussion.md
---

## Current State Summary

Checkpoint added after the main handoff (`.gzkit/handoffs/20260927T164026Z-skills-packaging-design-discussion.md`, committed at 71564d447) to carry one more discussion thread: parallel agents, and the agent's advice on how to "chunk" work for them. Discussion only. The operator, verbatim: "actually dont take action, just discuss", then "add this to a checkpoint handoff so I resume it. I need to better understand your "chunk" advice."

Nothing was built, configured or run for this thread. No files other than this handoff changed.

The operator asked whether the idea came from the insights report. Partly: the report's "On the Horizon: Parallel Agents Drain the GHI Backlog" proposes a coordinator that picks about six open GHIs touching mostly separate files and gives each to a subagent in its own git worktree and branch. That splits the issue backlog, not the repo.

## Important Context

**Discussion to resume, not rulings.** The operator has made no decision on parallel agents. Everything below is the agent's advice, which the operator has asked to understand better before discussing.

**What "chunk" means in the agent's advice.** A chunk is one unit of investigation with its own question and its own deliverable, small enough for one agent to finish and for the main session to check. The advice is to chunk by question or decision, not by repo directory.

Why not by directory: a typical gzkit change is coupled across surfaces (AGENTS.md § DO IT RIGHT 1a). One defect usually touches a validator under src/gzkit, its rule text, its skill and its generated copies. An agent that owns only one directory either collides with the others or stops at its lane's edge and fixes the instance instead of the class, which the craftsmanship rules forbid.

**The pattern: fan out to read, funnel to write.**

1. Parallel agents only investigate. Each reproduces the problem, traces the cause, drafts a proposed change, and returns evidence with file:line citations. They write nothing to the repo.
2. The main session verifies each result before relying on it. This session showed why: one of two research subagents invented a Claude Code `skillsDir` setting that does not exist.
3. One writer, the main session, applies the changes one after another on main, through the normal commit hooks and the pre-push `gz check`.

This keeps the "work on main, no branches" directive and keeps the ledger at a single writer, while running the slow part (investigation) in parallel.

**Worked example, GHI #1138.** 42 delivered skills cite 62 `docs/` paths that do not exist in an adopter tree.

- Chunks: the skills, in batches of about six, which gives about seven agents.
- Each agent's question: for each `docs/` reference in these skills, is it gzkit-only, created later by the adopter's own tooling, or something that should ship with the skill? What should the text say instead?
- Each agent returns: one row per reference (skill, line, path, class, proposed replacement text, evidence). It edits nothing.
- The main session: spot-checks the rows against the files and a scratch `gz init` tree, merges them into one table, and puts the per-reference choices to the operator.
- The single writer: applies the edits with the skill-version and last_reviewed bumps, runs `gz agent sync control-surfaces`, adds the guard test, and commits under the GHI with one pre-push `gz check`.

**The case against doing much of this.** The bottleneck is operator attention (rulings, Gate 5 on every OBPI completion), not agent speed. Parallel agents that finish together put more evidence bundles and rulings in front of the operator at once. Parallelism only helps where the operator is not needed until the end.

**Fits and misfits.**
- Good fits: research that splits into separate questions; per-item classification across a catalog (the #1138 case); adversarial review passes; reading issue bodies during triage.
- Poor fits: anything that writes shared state. `.gzkit/ledger.jsonl`, handoffs, insights, the campaign file and AGENTS.md are single hot files, and almost every `gz` verb appends to the ledger. Merges also serialize on the multi-minute pre-push `gz check`.
- Out of scope unless the operator says otherwise: OBPI work, which only the operator initiates and which runs through its own pipeline.

**Conflicts with canon in the insights version.** A worktree and branch per GHI conflicts with the standing directive to work on main without branches. The insights' copyable prompts are model-written and assume tools this repo rules out (they tell agents to run pytest, which the forbid-pytest hook blocks). Design from the repo's rules, not from those prompts.

**Existing machinery.** `gz obpi lock` and the exchange register (ADR-0.0.41) already coordinate multiple agents on OBPIs. GHIs have no claim or lock. If agents ever write in parallel, that gap comes first.

## Decisions Made

No rulings. The operator directed discussion only and asked for this checkpoint so the thread can be resumed.

- [agent-chose] Wrote a CHECKPOINT (a bookmark) chained to the session's main handoff rather than a second CREATE, as the operator asked for a checkpoint; the main handoff stays the record of the session's state.
- [agent-chose] Added the #1138 worked example to make the chunking advice concrete, since the operator said they need to understand it better. It is illustrative only and does not route #1138, which remains an open operator decision in the main handoff.

## Immediate Next Steps

These are advised steps for the operator to rule on; none is authorized by this handoff.

1. Walk the operator through the chunking advice in Important Context, starting from the #1138 worked example, and answer their questions about it before anything else on this thread.
2. Ask the three open questions: is the goal wall-clock speed or less operator time per unit of work; would short-lived local worktrees that are never pushed be acceptable for isolated verification runs, or does the no-branches directive cover them; which work classes are eligible (the agent suggested GHI direct repair and catalog audits like #1138, with OBPI work excluded).
3. Then resume the main handoff's design thread (`.gzkit/handoffs/20260927T164026Z-skills-packaging-design-discussion.md`): skills delivery model, Magna Carta implications, option A timing, #1138 routing.

## Pending Work / Open Loops

- This thread: the operator's understanding of the chunking advice and the three open questions in Immediate Next Steps. No design record exists.
- If parallel agents ever write, GHIs need a claim or lock mechanism like `gz obpi lock`; not designed.
- Everything open in the main handoff carries unchanged: the skills-packaging discussion, option A for vendor mirrors, the project-local gz-skills tracking skill, the Magna Carta amendment, GHI #1138 routing, and the predecessor's carried GHI queue and insights. See `.gzkit/handoffs/20260927T164026Z-skills-packaging-design-discussion.md` § Pending Work / Open Loops.

## Verification Checklist

- The main handoff exists and is committed: `git log --oneline -1 -- .gzkit/handoffs/20260927T164026Z-skills-packaging-design-discussion.md` shows 71564d447.
- GHI #1138 state for the worked example: `gh issue view 1138 --json state,title`.
- The existing multi-agent coordination surface: `uv run gz obpi lock --help`.
- The no-branches directive: AGENTS.md § Operator Doctrine (verbatim canon), "Work directly on main, commit, and git-sync."

## Evidence / Artifacts

- `.gzkit/handoffs/20260927T164026Z-skills-packaging-design-discussion.md` (the main handoff this checkpoint chains to)
- `AGENTS.md` (§ DO IT RIGHT 1a coupled surfaces; § Operator Doctrine no-branches directive; § OBPI Acceptance Protocol operator initiation)
- `.gzkit/skills/gz-obpi-lock/SKILL.md` (existing multi-agent claim and release surface)
- GHI #1138 (the worked example)
- The insights report section "On the Horizon: Parallel Agents Drain the GHI Backlog" (local usage report generated 2026-09-27; outside the repo)

## Settled Rulings

1122 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
