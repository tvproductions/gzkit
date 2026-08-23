# Defect-fix routing

> Binding content lives in [AGENTS.md § Defect-fix routing](../../AGENTS.md#defect-fix-routing). This page carries the deep-dive rationale: the anti-pattern catalog, the origin GHI #195 narrative, and the related-rules cross-references that would otherwise clutter the per-turn agent context.

When a defect surfaces, the routing decision (direct `fix(...)` commit vs. full OBPI ceremony) is made against the explicit thresholds in AGENTS.md. This page records *why* those thresholds exist, what they look like when applied wrong, and which other rules they compose with.

## Precondition: does an OBPI brief already own this work?

The thresholds in AGENTS.md ask how big the fix is, how many surfaces it touches, and whether it surfaced in flight. **They never ask who owns the work**, and that question is upstream of all of them: a defect whose surface is already decomposed into an authored OBPI brief is not a routing choice the agent makes, whichever side of the thresholds it falls on.

Check before applying the matrix:

```bash
grep -rln "<surface path / entry id / symbol>" docs/design/adr/*/*/obpis/*.md
```

A hit on a **live** brief (`Draft`, `pending`, `in_progress`) makes the routing question operator-level. Two rules in AGENTS.md both apply and they select on which *description* of the work governs — "NEVER work an OBPI without running it through the gz-obpi-pipeline skill" against "GHIs are AUTHORIZED for direct repair, always … those criteria gate planned ADR work, not defect repair." Neither is wrong; they answer different questions about the same commit. Surface the brief id, its status, its parent ADR, and the requirement lines that match, then let the operator rule.

A hit on a **terminal** brief (`Completed`, `attested_completed`, `Validated`, `Superseded`, `Withdrawn`, `Abandoned`) does not block. That work shipped; a fresh defect against the same surface is an ordinary GHI.

**Surface the disposition, never just the match.** GHI #862's collision with `OBPI-0.35.0-03-retire-duplicate-invariant-entries` was first reported as `entry_id in brief` → 7/7, which established only that the ids appeared — the brief enumerated *both* sides of every pair. Read against its `retire X; RETAIN Y` structure, the operator's ruling had **inverted** the brief on all seven groups, and its `REQUIREMENT 12` said so explicitly. The coarse check would have let the operator rule a second time without seeing the conflict.

**Origin:** GHI #864. `ghi-author` Step 0's pre-flight read GitHub issues only, so a brief owning the work was invisible to the one check meant to catch it; the collision was found by an unrelated `grep`, after the fix had landed and been pushed. The skill now carries a third query and a decision-table branch; this page is where the routing side of that answer lands, because the AGENTS.md criteria table is the surface that consumes it.

## Anti-patterns

- Authoring an OBPI brief for a defect surfaced mid-pipeline because "the parent ADR is the natural home." The parent ADR may be the natural home for the *fix description in the commit body*; it is not necessarily the home for ceremony.
- Adding a Surface Boundary scorecard split + WBS item + brief + audit + attest + sync for a 5-line filter change. Per the OBPI-04 → OBPI-06 → revert sequence (commits `4d14ebf9` → `d2ed160b`), this exact pattern produced 30%+ session waste with zero governance benefit a direct `fix(validator)` commit didn't produce.
- Applying the threshold matrix without first asking whether a live OBPI brief owns the surface. The matrix answers *how much ceremony*; it cannot answer *whose work this is*, and a clean pass through it is not evidence that nobody else owns the change (GHI #864).
- Treating direct-fix and OBPI-ceremony as a stylistic preference. They are not — they have different costs and different audit shapes; the wrong choice is wasted operator time.

## Recent baseline precedent

Mechanically-verifiable recent precedent (60-day window, `git log --grep='^fix('`):

- **GHI #186** — `fix(prd): canonicalize scaffolded id to match validator schema` (`0b9a805c`)
- **GHI #187** — `fix(plan-audit): canonicalize obpi_id before writing receipt` (`ab142962`)
- **GHI #188** — `fix(hooks): plan-audit gate accepts canonical-slug receipt` (`68e45cf7`)
- **GHI #189** — `fix(validator): recovery hint uses plural 'gz chores run'` (`5deba76b`)
- **GHI #191** — `fix(hooks): plan-audit-gate self-runs gz plan audit when receipt is stale` (`40dc7864`)
- **GHI #192** — `fix(validator): skip pool ADRs in validate_frontmatter for chore-library parity` (`4e914dd0`)

Each of these is ≤~250 lines including tests, single-surface, surfaced in flight, and shipped without OBPI ceremony.

## When this rule was authored

GHI #195, 2026-04-18. The triggering session was OBPI-0.0.16-04 dogfooding, where a 5-line validator pool-skip fix (GHI #192) was first wrapped in a full OBPI-0.0.16-06 ceremony, then reverted (commit `d2ed160b`) when the operator pointed out the precedent. The rule encodes the precedent so the next agent does not need an operator pushback to make the same call.

The rule originally lived at `.gzkit/rules/defect-fix-routing.md` with a universal `paths: "**"` scope. ADR-0.0.20 (agent-rule-placement-invariant) reclassified universal rule files as a placement violation — binding content belongs in AGENTS.md, pedagogy belongs here. OBPI-0.0.20-04 performed the fold: the threshold tables and decision protocol migrated to AGENTS.md § Defect-fix routing; the anti-patterns, origin narrative, and cross-references landed on this page.

## Related

- [AGENTS.md § Defect-fix routing](../../AGENTS.md#defect-fix-routing) — the binding threshold tables and decision protocol this page is the pedagogy for.
- [AGENTS.md § Behavior Rules — Never, item 5](../../AGENTS.md#never) (brief-boundary anti-pattern).
- [AGENTS.md § DO IT RIGHT, item 7 (6c)](../../AGENTS.md#do-it-right-craftsmanship-maxim) — "choose fix scope per thresholds, not intuition." Ceremony is not always more thorough.
- [`gz-obpi-pipeline` SKILL](../../.gzkit/skills/gz-obpi-pipeline/SKILL.md) — the ceremony this rule modulates; its "When NOT to Use" section cites the direct-fix thresholds.
- [`gz-obpi-specify` SKILL](../../.gzkit/skills/gz-obpi-specify/SKILL.md) — the brief-authoring skill this rule modulates.
