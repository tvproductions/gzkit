## Class of failure

System Card §6.2.2.2 Efficiency: 4.7 is *"prone to declaring sufficiency without acting — in the worst case stating 'I have enough context, let me write the code,' then resuming exploration until it hits the tool-call cap with nothing written."* Tutorial reinforces: 4.7 uses tools *more selectively* and needs explicit specification.

Skills that describe operations in prose (*"find the brief"*, *"search tests/"*, *"read the file"*) without naming the corresponding tool invocation invite action-skip or input hallucination (§6.3.3.4).

Scope: six instances in `.gzkit/skills/*` that mirror to `.claude/skills/` (Claude Code primary; Codex has no skills-loading equivalent).

## Evidence

| Location | Text | Issue |
|---|---|---|
| `.gzkit/skills/gz-obpi-specify/SKILL.md:149-209` | Pre-Save Ground-Truth Check is section 6 of 9 | Correct content, wrong position — purely positional promotion to step 1-2 |
| `.gzkit/skills/gz-obpi-reconcile/SKILL.md:119-151` | "Agent action: SEARCH for evidence / grep tests/ for @covers tags" | No Grep tool call; "grep" is shell prose; fails Windows-native |
| `.gzkit/skills/gz-obpi-simplify/SKILL.md:73-77` | `find docs/design/adr -name "OBPI-{id}*.md"` | Bash `find` fails Windows-native; Glob is the native cross-platform answer |
| `.gzkit/skills/gz-check/SKILL.md:50-58` | "Verify: 1. No hook errors 2. Surfaces match canonical 3. CLAUDE.md under 200 lines" | Three check items, zero commands named |
| `.gzkit/skills/gz-adr-audit/SKILL.md:87-90` | `ADR_DIR=... mkdir -p "${ADR_DIR}/audit/proofs"` | Shell var persistence; Bash tool resets between calls per tool docs |
| `.gzkit/skills/gz-adr-emit-receipt/SKILL.md:29` | `$gz-adr-emit-receipt` placeholder | Needs verification: template residue vs. real bug |

## Fix plan

Two coordinated commits under this GHI:

1. `refactor(skills): promote gz-obpi-specify pre-save ground-truth check to step 1 (GHI #<N>)` — position-only, no content change
2. `fix(skills): replace prose operations with tool-literal invocations (GHI #<N>)` — the other five:
   - `gz-obpi-simplify:75` `find X` → `Use Glob(pattern="docs/design/adr/**/obpis/OBPI-{id}*.md")`
   - `gz-obpi-reconcile:119-151` `grep X` → `Use Grep(pattern=..., path=...)`
   - `gz-check:50-58` three verify items → each names a concrete CLI (`uv run gz validate --surfaces`, `wc -l CLAUDE.md`, etc.)
   - `gz-adr-audit:87-90` inline the paths; no shell vars
   - `gz-adr-emit-receipt:29` verify whether placeholder is a rendering artifact; if not, replace with literal invocation

## Routing

Multi-file (6 files); ≤25 lines total. Direct-fix per `defect-fix-routing.md`. Two focused commits.

## Tracked under

Umbrella GHI #224 (4.7 regression — governance surface hardening).
