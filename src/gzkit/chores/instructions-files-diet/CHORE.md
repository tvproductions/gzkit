# CHORE: Instructions & Memory Files Diet (Progressive Disclosure)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `instructions-files-diet`

---

## Overview

Trim per-turn agent context weight by lifting pedagogical narrative from
`AGENTS.md`, `CLAUDE.md`, and `.claude/rules/**` to corresponding pages
under `docs/governance/`. The contract retains binding bullets and one-line
pointers to the lifted rationale — pedagogy becomes reachable on demand,
not loaded per-turn.

This is a **narrative trim**, never an invariant relaxation. The doctrine
is explicit at `AGENTS.md` § Anti-vibing mantra operative claim 2:
*"lighter ceremony is not a tradeoff axis."* The same binding invariants
remain in-contract; only the in-place rationale moves.

## Source

GHI #327 — *AGENTS.md: trim per-turn contract weight, lift pedagogy to
docs/governance*. The meta-tension is already named at
`AGENTS.md:13-22` (§ Why this contract is not minimal); this chore acts on
that articulated cost.

Precedent: `AGENTS.md` § Extracted pedagogy (line 99) already lifted the
anti-pattern canon and TASK-driven workflow binding to
`docs/governance/agent-contract-rationale.md`, leaving a one-line pointer
behind. This chore generalizes that pattern across the remaining pillars.

## Baseline (2026-04-26)

| Surface | Lines |
|---|---|
| `AGENTS.md` | 632 |
| `CLAUDE.md` (imports AGENTS.md + addendum) | 60 |
| `.claude/rules/*.md` (13 path-scoped rule files) | 1085 |
| **Total contract weight** | **~1777 lines** |

## Policy and Guardrails

- **Lane:** Lite — editorial curation against existing canon
- **Foundation-kind content rigor:** the agent contract is an app/system
  invariant surface; bullet retention is gated on the advisory scorecard
  (`docs/governance/advisory-rules-audit.md`), not author judgment
- **Binding-bullet preservation:** every bullet scoring Mechanical or
  Promotable on the scorecard MUST remain in the per-turn contract
- **Judgment-bullet folding:** Judgment-class bullets that duplicate a
  Mechanical neighbor get folded; standalone Judgment bullets that carry
  unique signal stay
- **Pedagogy lift target:** `docs/governance/agent-contract-rationale.md`
  is the established home for lifted pedagogy; new pages may be authored
  under `docs/governance/` when the rationale is large enough to warrant
  a dedicated page (e.g. `docs/governance/anti-vibing-mantra.md`)
- **Pointer discipline:** every lift leaves a one-line pointer at the
  origin site naming the destination page, in the same shape as the
  existing § Extracted pedagogy entry

## Workflow

### 1. Inventory

Tabulate the current per-turn surfaces and their pillars:

```bash
wc -l AGENTS.md CLAUDE.md .claude/rules/*.md
```

Record the baseline in `proofs/baseline-YYYY-MM-DD.txt`.

### 2. Score

For each pillar (H2 section in `AGENTS.md`; whole rule files under
`.claude/rules/**`), audit each bullet against the advisory scorecard:

```bash
uv run gz validate --advisory-scorecard
```

Mark each bullet **Mechanical / Promotable / Judgment / Ambiguous**.

### 3. Lift

Move Judgment-class narrative paragraphs and "Why this is canon" /
"Relationship to the rest of the contract" codas to:

| Origin pillar | Destination |
|---|---|
| `AGENTS.md` § DO IT RIGHT — multi-paragraph rationale | `docs/governance/agent-contract-rationale.md` (existing) |
| `AGENTS.md` § Anti-vibing mantra — philosophical framing | `docs/governance/anti-vibing-mantra.md` (new, if size warrants) |
| `AGENTS.md` § Stdlib-First — "Why this is canon" coda | `docs/governance/stdlib-first-doctrine.md` (new, if size warrants) |
| `AGENTS.md` § Operator economy — "Why this is canon" coda | `docs/governance/operator-economy.md` (new, if size warrants) |
| `.claude/rules/<rule>.md` — multi-paragraph "Rationale" sections beyond the binding rule | `docs/governance/<rule>-rationale.md` (per-rule lift, only when narrative >20 lines) |

Each lifted block leaves a one-line pointer at the origin in the shape:

```markdown
> See [<destination title>](<destination path>) for the rationale, worked
> examples, and citations underlying the bullets above.
```

### 4. Compress

After lifting, walk each remaining pillar and:

- Fold Judgment bullets that duplicate a Mechanical neighbor
- Collapse multi-paragraph framings down to a one-sentence binding statement
- Preserve verbatim every Mechanical / Promotable bullet — these are the
  load-bearing per-turn payload

### 5. Sync mirrors

```bash
uv run gz agent sync control-surfaces
```

`.claude/rules/**` is generated from `.gzkit/rules/**` per
`.claude/rules/skill-surface-sync.md`. Edit the canonical surface; let sync
propagate.

### 6. Validate

```bash
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz lint
uv run mkdocs build --strict
uv run -m unittest -q
```

### 7. Measure

Re-run the inventory and record the post-trim baseline in
`proofs/post-trim-YYYY-MM-DD.txt`. Compute the delta and record it in
`proofs/CHORE-LOG.md`.

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | Advisory scorecard audit passes | `uv run gz validate --advisory-scorecard` exit 0 |
| 2 | Documents and surfaces validate | `uv run gz validate --documents --surfaces` exit 0 |
| 3 | Lint clean | `uv run gz lint` exit 0 |
| 4 | Docs build strict | `uv run mkdocs build --strict` exit 0 |
| 5 | Tests pass | `uv run -m unittest -q` exit 0 |
| 6 | Control-surface sync clean | `uv run gz agent sync control-surfaces` reports no stale or divergent mirrors |
| 7 | Per-turn contract weight reduction recorded | `proofs/baseline-*.txt` and `proofs/post-trim-*.txt` exist with a measurable line-count delta |
| 8 | Every binding bullet retained | Each Mechanical / Promotable scorecard entry resolves to a bullet still present in the per-turn contract (manual cross-check recorded in `proofs/bullet-retention-audit.md`) |
| 9 | Pedagogy reachable via in-line link | Every pillar that lifted narrative carries a one-line pointer to its destination page |

## Evidence Commands

```bash
wc -l AGENTS.md CLAUDE.md .claude/rules/*.md
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz lint
uv run mkdocs build --strict
uv run -m unittest -q
uv run gz agent sync control-surfaces
```

## Anti-patterns

- Removing a Mechanical or Promotable bullet to hit a line-count target
  ("lighter ceremony is not a tradeoff axis")
- Lifting binding bullets to `docs/governance/` and replacing them with a
  pointer — only narrative rationale lifts; bullets stay
- Treating the line-count delta as the headline metric — bullet retention
  is the floor; the delta is the by-product
- Editing `.claude/rules/**` mirrors directly — edit `.gzkit/rules/**` and
  let sync propagate
- Running this chore mid-OBPI without a quiet tree — the diff is large
  and reviewing it tangled with feature work hides binding-bullet drift

## Related

- GHI #327 — origin
- `AGENTS.md` § Why this contract is not minimal — articulated tradeoff
- `AGENTS.md` § Extracted pedagogy — lift precedent
- `docs/governance/advisory-rules-audit.md` — scorecard catalogue
- `docs/governance/agent-contract-rationale.md` — established lift home
- `.claude/rules/skill-surface-sync.md` — canonical-vs-mirror discipline
