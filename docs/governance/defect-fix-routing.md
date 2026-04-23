# Defect-fix routing

> Binding content lives in [AGENTS.md § Defect-fix routing](../../AGENTS.md#defect-fix-routing). This page carries the deep-dive rationale: the anti-pattern catalog, the origin GHI #195 narrative, and the related-rules cross-references that would otherwise clutter the per-turn agent context.

When a defect surfaces, the routing decision (direct `fix(...)` commit vs. full OBPI ceremony) is made against the explicit thresholds in AGENTS.md. This page records *why* those thresholds exist, what they look like when applied wrong, and which other rules they compose with.

## Anti-patterns

- Authoring an OBPI brief for a defect surfaced mid-pipeline because "the parent ADR is the natural home." The parent ADR may be the natural home for the *fix description in the commit body*; it is not necessarily the home for ceremony.
- Adding a Surface Boundary scorecard split + WBS item + brief + audit + attest + sync for a 5-line filter change. Per the OBPI-04 → OBPI-06 → revert sequence (commits `4d14ebf9` → `d2ed160b`), this exact pattern produced 30%+ session waste with zero governance benefit a direct `fix(validator)` commit didn't produce.
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
