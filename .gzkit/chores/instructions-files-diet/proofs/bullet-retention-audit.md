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

---

# Bullet Retention Audit — Run 4 (Pass 3: narrative lift + rule compression)

**Date:** 2026-05-04
**Pass:** Pass 3 (Run 4)
**Origin GHI:** #327 follow-up
**Session baseline:** 2200 lines (AGENTS.md + CLAUDE.md + `.claude/rules/**`)

## Lift inventory

| # | Origin | Class lifted | Destination | Lines removed | Pointer left |
|---|---|---|---|---|---|
| A | `src/gzkit/templates/agents.md` § Anti-vibing — "Ownership and craftsmanship pillars…" paragraph | Judgment cross-ref narrative | `docs/governance/agent-contract-rationale.md` § Anti-vibing mantra — relationship to the rest of the contract | ~5 lines → 0 (pointer already existed) | Yes (existing) |
| B | `src/gzkit/templates/agents.md` § Stdlib-First — "LLM training corpus is biased…" opener | Judgment corpus-bias narrative | `docs/governance/agent-contract-rationale.md` § Stdlib-First doctrine — rationale (new) | ~5 lines → 0 (pointer added) | Yes |
| C | `src/gzkit/templates/agents.md` § Stdlib-First § Highly-opinionated defaults bind consuming projects | Judgment opinionated-defaults framing (2 paragraphs) | `docs/governance/agent-contract-rationale.md` § Stdlib-First doctrine — rationale (same section) | ~8 lines → 0 (pointer added) | Yes |
| D | `src/gzkit/templates/agents.md` § Stdlib-First § Relationship to the corpus | Judgment meta-commentary (1 paragraph) | `docs/governance/agent-contract-rationale.md` § Stdlib-First doctrine — rationale (same section) | ~3 lines → 0 (pointer covers) | Yes |
| E | `src/gzkit/templates/agents.md` § Operator economy — "Canonical interaction mode…" framing paragraph | Judgment framing coda | `docs/governance/agent-contract-rationale.md` § Operator economy — why this is canon (existing) | ~4 lines → 0 | Yes (existing) |
| F | `.gzkit/rules/agent-failure-modes.md` — 6× repeated citation block | Citation deduplication (identical mechanical text) | Consolidated to single `[1]` footnote in header | ~30 lines → 6 × 1 (≈−24) | N/A (source note in header) |
| G | `.gzkit/rules/agent-failure-modes.md` — 3× worked examples (GHI #290, #263, #261) | Judgment worked examples | `docs/governance/agent-contract-rationale.md` § Failure-mode worked examples (new) | ~18 lines → 3 pointers | Yes |
| H | `.gzkit/rules/agent-failure-modes.md` § Loading posture | Judgment advisory commentary + promotion roadmap | `docs/governance/agent-contract-rationale.md` § Agent failure-mode taxonomy — loading posture and worked examples (new) | ~17 lines → 5-line binding summary + pointer | Yes |

## Mechanical/Promotable bullet preservation

The advisory-scorecard validator (`uv run gz validate --advisory-scorecard`) result: **exit 0, all scopes valid (5/5 PASS).**

All lifted content was Judgment-class:

- **Lifts A–E** removed Judgment narrative paragraphs and framing codas around binding Operative Claims bullets. The Operative Claims numbered lists (1–4 in § Anti-vibing; 1–5 in § Stdlib-First; 1–6 in § Operator economy) remain per-turn intact.
- **Lift F** deduplicated identical citation text — the citation is still cited once (footnote `[1]`) per pattern, not removed. No rule content removed.
- **Lift G** replaced worked examples (Judgment, pedagogical) with pointers. The backstop bullets naming the enforcing invariants (DO IT RIGHT 6g, 6h; Behavior Rules — Never #6; ARB discipline) remain intact in each pattern's `**Backstop:**` block.
- **Lift H** compressed § Loading posture advisory commentary. The binding summary retained: "This rule is **advisory** at authoring time — the vocabulary, not a mechanical gate." No backstop description removed.

**Conclusion:** zero Mechanical or Promotable bullets removed. Zero scorecard-listed entries silenced. All lifts were strictly Judgment-class narrative, rationale exposition, worked examples, or duplicate citation text.

**Note on Pass 1 Lift 3 deferral:** Lifts C and D in this pass correspond to the previously-deferred Lift 3 ("Stdlib-First § Highly-opinionated defaults bind consuming projects" and "§ Relationship to the corpus"). Operator review confirmed these sections are Judgment-class (framing and meta-commentary, not binding invariants) — cleared for lift.

## Pointer discipline

Every lift left a `> See [...]` one-line pointer at the origin site, or relied on an existing pointer (Lifts A, E). GFM anchors verified against actual H2/H3 headings in `docs/governance/agent-contract-rationale.md`:

- `#anti-vibing-mantra--relationship-to-the-rest-of-the-contract` ✓
- `#stdlib-first-doctrine--rationale` ✓ (new section)
- `#agent-failure-mode-taxonomy--loading-posture-and-worked-examples` ✓ (new section)
- `#failure-mode-worked-examples` ✓ (H3 renamed from `### Worked examples` to `### Failure-mode worked examples` to match the pointer slug)

## Validation gates (post-trim)

| Gate | Command | Result |
|---|---|---|
| Advisory scorecard | `uv run gz validate --advisory-scorecard` | exit 0 |
| Documents + surfaces | `uv run gz validate --documents --surfaces` | exit 0 |
| Lint | `uv run gz lint` | exit 0 |
| Docs build strict | `uv run mkdocs build --strict` | exit 0 |
| Unit tests | `uv run -m unittest -q` | exit 0 (4049 tests) |

## Line-count delta

| Surface | Before | After | Δ |
|---|---|---|---|
| `AGENTS.md` | 470 | 454 | −16 |
| `.claude/rules/agent-failure-modes.md` | 228 | 200 | −28 |
| Other rule files | unchanged | unchanged | 0 |
| **Total per-turn** | **2200** | **2156** | **−44** |

---

# Bullet Retention Audit — Run 5 (Pass 4: catalog indirection + token-block compression)

**Date:** 2026-05-22
**Pass:** Pass 4
**Origin GHI:** #327 follow-up
**Session baseline:** 2110 lines (`AGENTS.md` + `CLAUDE.md` + `.gzkit/rules/**`)

## Lift inventory

| # | Origin | Class lifted | Destination | Lines removed | Pointer left |
|---|---|---|---|---|---|
| A | `AGENTS.md` § Available Skills generated catalog | Generated discovery list | `uv run gz skill list` live catalog + `.gzkit/skills/<skill-name>/SKILL.md` | 31 lines -> 1 line | Yes |
| B | `.gzkit/agents.local.md` governance-scorecard prose | Judgment explanation | Existing governance doctrine pages | 3 lines -> 1 line | Yes |
| C | `.gzkit/agents.local.md` architectural-boundary rationale | Judgment rationale around binding boundary bullets | Architecture Planning Memo Section 12 + existing doctrine links | 6 bullets compressed in place | Source pointer retained |
| D | `.gzkit/rules/token-block-discipline.md` railway-history and register-entry rationale | Judgment pedagogy | `docs/governance/token-block-doctrine.md` | 6 lines -> 2 pointers | Yes |

## Mechanical/Promotable bullet preservation

The advisory-scorecard validator result after the pass: **exit 0, all scopes valid**.

- **Lift A** changed discovery form, not skill availability. The generated per-turn file now points to `uv run gz skill list`, and the canonical skill files remain under `.gzkit/skills/<skill-name>/SKILL.md`. Tests were updated to assert the new indirection contract.
- **Lifts B and C** retained the governance-doctrine links and every `Do not ...` architectural-boundary command. Only explanatory phrases around those commands were compressed.
- **Lift D** retained every binding sub-invariant, enum, validator rule, TTL value, release precondition, vocabulary item, cross-link, and audit command. Railway-history prose now lives in the already-existing token-block doctrine page.

**Conclusion:** zero Mechanical or Promotable bullets removed. The pass trims generated catalog text and Judgment-class rationale while retaining binding rules in the per-turn contract.

## Validation gates (post-trim)

| Gate | Command | Result |
|---|---|---|
| Advisory scorecard | `uv run gz validate --advisory-scorecard` | exit 0 |
| Surfaces | `uv run gz validate --surfaces` | exit 0 |
| Instruction budget | `uv run gz validate --instructions-files-budget` | exit 0 |
| Invariant coherence | `uv run gz validate --invariant-coherence` | exit 0 |
| Lint | `uv run gz lint` | exit 0 |
| Docs build strict | `uv run mkdocs build --strict` | exit 0 |
| Unit tests | `uv run -m unittest -q` | exit 0 (5432 tests) |
| Documents + surfaces | `uv run gz validate --documents --surfaces` | exit 1 (known legacy ADR corpus failures present at baseline) |

## Line-count delta

| Surface | Before | After | Δ |
|---|---|---|---|
| `AGENTS.md` | 392 | 366 | −26 |
| `CLAUDE.md` | 27 | 27 | 0 |
| `.gzkit/rules/token-block-discipline.md` | 135 | 132 | −3 |
| Other canonical rule files | unchanged | unchanged | 0 |
| **Total measured surface** | **2110** | **2081** | **−29** |
