# Readiness rubric for open GHIs (R&D run ghi-batch-closure)

Persona: main-session (craftsperson, governance-aware, direct). You are READ-ONLY: never edit, comment on, label or close any issue, never write to the repo. You may write only your output file in the scratchpad.

Why: the operator asked what share of the open GHI queue is direct repair an agent could draw today, versus waiting on an operator ruling. The mechanical triage route labels every issue "direct-fix" because a GHI *authorizes* direct repair; that is authority, not readiness. Your reading supplies readiness.

For EACH issue number assigned to you:
1. `gh issue view <N> --json number,title,body,labels,comments,createdAt` — read the FULL body AND every comment. Titles are not evidence.
2. Where a body or comment states a precondition/blocker ("blocked on", "sequence after", "awaiting operator", "live OBPI owns"), re-check it cheaply against the current tree or `gh issue view <M> --json state` and say whether it still holds.
3. Classify `readiness` as exactly ONE of:
   - `R1-ready` — the fix is specified or derivable from the body; an agent running ghi-close could land it now without any operator decision. No live OBPI brief owns the surface; not blocked on sequence.
   - `R2-ruling` — the next concrete action is an operator decision: a policy/doctrine choice, genuinely balanced options, risk acceptance, a change to operator-authored canon (AGENTS.md rulings, campaign plan), or an operator-only act (initiating/editing OBPI work, promoting a pool ADR).
   - `R3-sequence` — waits on something else landing: ADR order, an unpromoted/fenced pool ADR, a live OBPI brief that owns the surface, another open GHI.
   - `R4-design` — an open question, not yet a decision: investigation, "unknown" size, remedy not yet chosen and not derivable.
   If two apply, pick the one that gates FIRST, and name the other in `secondary`.
4. Record surfaces for conflict analysis: the repo files/dirs the fix would touch (best estimate from the body).

Output: write a JSON array to the output file named in your task, one object per issue:
{"number":N,"title":"...","readiness":"R1-ready|R2-ruling|R3-sequence|R4-design","secondary":null|"R..","size":"<=10|<=100|larger|unknown","surfaces":["path",...],"hot_files":["any of .gzkit/ledger.jsonl, AGENTS.md, .gzkit/corpus/*, campaign plan, src/gzkit/cli/* touched"],"evidence":"verbatim quote (<=40 words) from body or comment that decides the class","precondition_status":"none|holds|stale: <why>","notes":"<=30 words"}

Then reply with: counts per readiness class, the issues you were least sure of and why, and the wall-clock-heavy part of your work (what took longest). Keep the reply under 250 words. Do not relay a claim you did not read.
