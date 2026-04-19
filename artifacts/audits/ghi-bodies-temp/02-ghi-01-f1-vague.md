## Class of failure

Under 4.7, vague-inference phrases ("use judgment", "similar-shape", "match existing flags", "≤60s") produce action-downgrade and over-asking per System Card §6.2.2.2 — *"the cautious system prompt amplified rather than corrected [the action-downgrade tendency]."* Fixing these with mechanical triggers reduces session friction.

Scope: three instances in `.gzkit/rules/*` that sync to Claude Code (`.claude/rules/`) and GitHub Copilot (`.github/instructions/`). AGENTS.md-body instances (5 others) are deferred to the `ADR-pool.vendor-alignment-claude-code` tidy chore.

## Evidence

| File:line | Observed text | Issue |
|---|---|---|
| `.gzkit/rules/chores.md:19` | "Lite by default \| Fast lane (<=60s)" | Agent has no clock; threshold is unmeasurable at the agent layer |
| `.gzkit/rules/defect-fix-routing.md:22` | "Precedent \| …shows ≥1 similar-shape direct-fix commit" | "Similar-shape" is subjective; over-match or under-match risk |
| `.gzkit/rules/cli.md:20` | "Consistency \| Follow UNIX/POSIX patterns; match existing flags" | No mechanical check against `config/cli_doctrine.json` |

## Fix plan

- `chores.md:19` → *"Lite lane: `uv run -m unittest -q`; wall-time budget ≤60s **enforced via `gz arb validate` against the receipt's `step.duration_seconds`**. Agent does NOT introspect time."* (Tool-enforceable threshold, not agent-introspected.)
- `defect-fix-routing.md:22` → *"Precedent \| `git log --since='60 days ago' --oneline --grep='^fix('` returns ≥3 commits."* (Mechanical check; no subjective shape-matching.)
- `cli.md:20` → *"Before adding a flag, run `uv run gz cli audit` and confirm the flag appears in `config/cli_doctrine.json` or add it in the same patch."* (Mechanical check.)

## Routing

Single coordinated commit under this GHI: `fix(rules): replace F1 vague-inference phrases with mechanical triggers (GHI #<N>)`. ≤10 lines across 3 files. Direct-fix per `defect-fix-routing.md`.

## Tracked under

Umbrella GHI #224 (4.7 regression — governance surface hardening).
