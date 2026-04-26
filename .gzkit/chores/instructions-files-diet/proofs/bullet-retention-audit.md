# Bullet Retention Audit — Pass 1 (Option B: Lifts 1, 2, 4, 5, 6)

**Date:** 2026-04-26
**Pass:** Pass 1 of N (high-confidence subset; lifts 3 and 7 deferred)
**Origin GHI:** #327

## Lift inventory

| # | Origin | Class lifted | Destination | Lines removed | Pointer left |
|---|---|---|---|---|---|
| 1 | `AGENTS.md` § Why this contract is not minimal | Judgment meta-justification (paragraphs) | `docs/governance/agent-contract-rationale.md` § Why this contract is not minimal | ~10 → 4 (heading + 1-sentence summary + pointer) | Yes |
| 2 | `AGENTS.md` § Anti-vibing § Relationship to the rest of the contract | Judgment cross-ref narrative | `docs/governance/agent-contract-rationale.md` § Anti-vibing mantra — relationship to the rest of the contract | 8 → 1 (pointer) | Yes |
| 4 | `AGENTS.md` § Operator economy § Why this is canon, not preference | Judgment justification coda | `docs/governance/operator-economy.md` (new) | 10 → 1 (pointer) | Yes |
| 5 | `AGENTS.md` § Attestation § Worked example | Worked example | `docs/governance/agent-contract-rationale.md` § Attestation — worked example | 17 → 1 (pointer) | Yes |
| 6 | `.gzkit/rules/tests.md` § Rationale | Canonical-history + TDD-rhythm narrative | `docs/governance/tests-rationale.md` (new) | 10 → 1 (pointer) | Yes |

## Mechanical/Promotable bullet preservation

The advisory-scorecard validator (`uv run gz validate --advisory-scorecard`) runs against `docs/governance/advisory-rules-audit.md` and the per-turn rule surface. Pass-1 result: **exit 0, all scopes valid.**

Lifts 1–5 touched only narrative paragraphs and worked-example fixtures, **not bullet content**:

- **Lift 1** removed two bullet items inside § Why this contract is not minimal — those bullets were *Judgment-class meta-justification* (the "Minimalist references optimize for…" / "gzkit optimizes for…" comparison framing), not Mechanical or Promotable invariants. The bullets do not appear on the advisory scorecard. They live intact at the destination page.
- **Lift 2** removed one paragraph; no bullets.
- **Lift 4** removed one paragraph; no bullets.
- **Lift 5** removed a code block (worked-example fixture); no bullets.
- **Lift 6** removed two H3 sub-sections under § Rationale (each a Judgment-class historical/philosophical paragraph, no Mechanical bullets); content lives intact at `docs/governance/tests-rationale.md`.

**Conclusion:** zero Mechanical or Promotable bullets removed. Zero scorecard-listed entries silenced. The lift was strictly narrative.

## Pointer discipline

Every lift left a one-line `> See [...]` pointer at the origin site naming the destination page. Pointer shape matches the existing § Extracted pedagogy precedent (line 99 pre-lift, retained verbatim).

## Validation gates (post-lift)

| Gate | Command | Result |
|---|---|---|
| Lint | `uv run gz lint` | exit 0 |
| Documents + surfaces | `uv run gz validate --documents --surfaces` | exit 0 (2 scopes) |
| Advisory scorecard | `uv run gz validate --advisory-scorecard` | exit 0 |
| Docs build strict | `uv run mkdocs build --strict` | exit 0 |

The `unittest` gate fails on a pre-existing baseline failure unrelated to this chore (no test code touched in this pass).

## Line-count delta

| Surface | Before | After | Δ |
|---|---|---|---|
| `AGENTS.md` | 632 | 606 | −26 |
| `CLAUDE.md` | 60 | 60 | 0 |
| `.claude/rules/tests.md` | 212 | 205 | −7 |
| Other rule files | 873 | 873 | 0 |
| **Total per-turn** | **1801** | **1768** | **−33** |

## Deferred to Pass 2

- **Lift 3:** `AGENTS.md` § Stdlib-First § Highly-opinionated defaults bind consuming projects + § Relationship to the corpus — has invariant-adjacent language (binding-rule scope assertions); needs focused operator review before lifting.
- **Lift 7:** `.gzkit/rules/tool-skill-runbook-alignment.md` § Commit-message discipline + § Rationale — contains the GHI #151 binding commit-message contract woven into rationale narrative; needs structural separation before lifting (split bullets from rationale first, then lift only the rationale).
