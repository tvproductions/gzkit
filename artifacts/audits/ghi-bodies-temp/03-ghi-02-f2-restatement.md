## Class of failure

Anthropic tutorial guidance: *"write your directions once and clearly."* 4.7 treats each occurrence of a rule as an independent constraint; within-surface restatement triggers rule-competition. Scope: within-surface (within-rule-file or within-skill) repetition; cross-surface restatement between rule files and architectural questions about `agents.local.md` embed are deferred to `ADR-pool.vendor-alignment-claude-code`.

## Evidence

| Surface | Pattern | Severity |
|---|---|---|
| `.gzkit/rules/tests.md` + `.gzkit/rules/behavioral-invariants.md:64` (rule 6f "Tests assert semantics, not strings") | **TDD drift** — rule 6f exists in behavioral-invariants only, missing from canonical tests.md | **P1** |
| `.gzkit/skills/gz-obpi-pipeline/SKILL.md:29-75` | **Iron Law restated 5× within one skill** (Iron Law L29-33 + Rationalization table L43-56 + Hard Boundaries L68-74) | **P0** on skill invocation |
| `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:356-383` | **MUST/MUST NOT 20 rows** where 10 one-sided directives would do | **P1** on skill invocation |

## Fix plan

Three coordinated commits under this GHI:

1. `fix(rules): add TDD rule 6f to tests.md as canonical home; drop from behavioral-invariants (GHI #<N>)` — pick canonical home; behavioral-invariants.md replaces its TDD block with a one-line pointer.
2. `refactor(skills): collapse Iron Law repetition in gz-obpi-pipeline to one statement + 3-row rationalization table (GHI #<N>)`.
3. `refactor(skills): halve MUST/MUST NOT table in gz-adr-closeout-ceremony to one-sided directives (GHI #<N>)`.

**Preserved intent** for the skill refactors: the thoroughness expectations of the Iron Law and MUST/MUST NOT stay. Only the 4-5× repetition is collapsed.

## Verification

Use Claude Code's **`InstructionsLoaded` hook** (Claude Code docs: memory#agents-md; inventory `docs/drafts/claude-code-inventory.md` row 69) to log which instruction files load in a post-fix session. The hook is the authoritative mechanism for verifying that rule 6f drift is actually closed (and for catching future sync regressions). Operator can enable via `.claude/settings.json` hooks section; log output shows the exact rules loaded per-session.

## Routing

Multi-file (3 files); ≤40 lines total. Direct-fix per `defect-fix-routing.md`. Three focused commits under one GHI.

## Tracked under

Umbrella GHI #224 (4.7 regression — governance surface hardening).
