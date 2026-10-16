# Recommendation — 2026-10-15 (harbor pilotage, WO-2)

A dated record. Nothing below has been applied. The chore reached § When to stop and ask, state 2.

## Surface — root `AGENTS.md` (24,279 B; budget 20,000 chars; over by 4,154)

| Quantity | Bytes | Source |
|---|---|---|
| Rendered and delivered | 24,279 | `wc -c AGENTS.md` == `.gzkit/renditions/AGENTS.md/root.md` |
| `tier: invariant` text live in the rendition, 101 entries | 22,599 | `root.lineage.json` entry ids joined to `.gzkit/corpus/AGENTS.md.jsonl` |
| `tier: compressible` text live in the rendition, 4 entries | 876 | same |
| Structure and unowned text (headings, separators, two unowned sections) | 804 | 24,279 − 22,599 − 876 |
| Required delta | 4,154 | `gz validate --instructions-files-budget` |
| Codex delivery cap headroom | 41,257 | surface-delivery witness |

## Candidate items (every compressible entry live in the rendition)

| Item | Action | Saving | Scorecard class | Cost |
|---|---|---|---|---|
| `corpus-pattern-discovery-*` pointer line (281 B) | lift | ≤ 281 B | Judgment | The pointer to the requirements-catalog ruling leaves the per-turn surface; the ruling itself is already in `docs/governance/agent-contract-rationale.md` |
| `corpus-gate-covenant-*` pointer line (279 B) | lift | ≤ 279 B | Judgment | Same shape: the BDD/Gate 4 rationale pointer leaves; the rationale page stays |
| `corpus-architectural-boundaries-*` pointer line (211 B) | lift | ≤ 211 B | Judgment | Same shape: the 2026-09-29 retirements pointer leaves |
| `corpus-behavior-rules-*` size-limit bullet (105 B) | keep | 0 | Judgment | It is the rule this chore runs under; removing it removes the trigger |

Cumulative saving if every pointer is lifted: 771 B against a required 4,154. **The gap is not closable here.**

## Finding (§ When to stop and ask, state 2 — gap exceeds the compressible budget)

Closing 4,154 chars means compressing `tier: invariant` entries, which the composer preserves verbatim by design and which are operator canon. The remaining lever is architectural or a ruling, not editorial. Three options for the operator:

- **A (recommended under martial law).** Record the budget at the invariant floor plus margin: set `AGENTS.md` to 25,000 in `data/instructions_files_budget.json` with a dated entry in `docs/governance/instructions-files-budget-history.md`. The witness that binds is the Codex cap (41 KB headroom); the 20,000 figure predates the 2026-10-10 restoration of binding sentences that the rule-conflict audit found over-lifted. Cost: the per-turn surface stays at 24 KB.
- **B.** Re-tier named invariant entries to compressible, by the operator's own ruling, and run § 5a to compress them toward the budget. Cost: operator time per entry; the agent may not choose which operator words to compress.
- **C.** Per-consumer delivery: a lighter root rendition for Claude (the vendor whose harness also loads `.claude/rules/**` and 15 KB of skill descriptions every turn) and the full rendition for Codex. Cost: a composition-engine change, which the campaign already queues as a feature ADR ("re-home the registry→AGENTS.md composition engine").

Per-turn load the budget does not see, measured 2026-10-15: `.claude/rules/*.md` 150 KB in 26 files (path-scoped; `tests.md` 11.6 KB is the largest), and 15,085 chars of skill descriptions across 73 skills loaded on every turn. Those are the next cuts whichever option is ruled.
