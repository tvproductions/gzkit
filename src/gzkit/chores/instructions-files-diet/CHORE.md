# CHORE: Instructions & Memory Files Diet (Progressive Disclosure)

**Version:** 2.0.0
**Lane:** Lite
**Slug:** `instructions-files-diet`

> **2.0.0 (GHI #817) — the surfaces this chore trims are DERIVED, and `1.0.0`
> edited them directly.** `AGENTS.md` is played back from a committed rendition
> composed out of `.gzkit/corpus/AGENTS.md.jsonl`; hand-editing it is drift that
> `gz validate --invariant-coherence` fails closed, and that a later
> `gz agent sync control-surfaces` silently overwrites. `1.0.0` named `AGENTS.md`
> as a direct edit target, carried **zero** mentions of the corpus, and omitted
> `--invariant-coherence` from its acceptance set — so it could edit a rendered
> surface, go green on its own gate, and hand the drift to an unrelated
> `gz check`. It also contradicted itself on mirrors: § 3 named
> `.claude/rules/<rule>.md` as an origin while § 5 and § Anti-patterns both said
> never to edit mirrors. Both arms are now routed to their canonical source, and
> the corpus arm stops at the Gate 5 boundary rather than landing canon
> unattested. `1.0.0` predated the composition architecture (baseline 2026-04-26)
> and aged into incorrectness silently — nothing couples a chore's procedure to a
> change in the layer model of the surfaces it names.

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

**Never edit the origin surface named below — edit its SOURCE.** Both origins are
derived artifacts; the middle column is where the change is actually authored.

| Origin pillar (derived — do NOT edit) | Edit this source instead | Destination for the lifted narrative |
|---|---|---|
| `AGENTS.md` § DO IT RIGHT — multi-paragraph rationale | `.gzkit/corpus/AGENTS.md.jsonl` (see § 3a) | `docs/governance/agent-contract-rationale.md` (existing) |
| `AGENTS.md` § Anti-vibing mantra — philosophical framing | `.gzkit/corpus/AGENTS.md.jsonl` (see § 3a) | `docs/governance/anti-vibing-mantra.md` (new, if size warrants) |
| `AGENTS.md` § Stdlib-First — "Why this is canon" coda | `.gzkit/corpus/AGENTS.md.jsonl` (see § 3a) | `docs/governance/stdlib-first-doctrine.md` (new, if size warrants) |
| `AGENTS.md` § Operator economy — "Why this is canon" coda | `.gzkit/corpus/AGENTS.md.jsonl` (see § 3a) | `docs/governance/operator-economy.md` (new, if size warrants) |
| `.claude/rules/<rule>.md` — multi-paragraph "Rationale" beyond the binding rule | `.gzkit/rules/<rule>.md`, then `gz agent sync control-surfaces` | `docs/governance/<rule>-rationale.md` (per-rule lift, only when narrative >20 lines) |

The rules row restates `.gzkit/rules/skill-surface-sync.md` § Non-negotiable rules
#4 (*"Never edit vendor mirrors directly"*), which § 5 and § Anti-patterns below
have always said. Through `1.0.0` this table contradicted both by naming the
mirror as the origin to edit.

### 3a. The `AGENTS.md` arm goes through the corpus, and stops at Gate 5

`AGENTS.md` is **not** a hand-authored file. It is played back from a committed
rendition under `.gzkit/renditions/AGENTS.md/<consumer>.md`, composed from the
append-only corpus at `.gzkit/corpus/AGENTS.md.jsonl`. Editing the rendered file
is drift on two counts: `gz validate --invariant-coherence` fails closed on it
(`src/gzkit/quality.py` — *"AGENTS.md vs committed rendition playback"*), and
`gz agent sync control-surfaces` re-renders over it.

Compression is therefore authored against corpus entries, not prose:

```bash
# 1. Retire a superseded entry (append-only retraction — never delete a line)
uv run gz content retire AGENTS.md --entry <entry-id> --reason "<why>"

# 2. Capture a replacement when combining or rewriting
uv run gz content remember AGENTS.md --address <section> --text "<compressed text>"

# 3. Compose a candidate per consumer. ALWAYS pass --candidate explicitly:
#    omitted, it reads from STDIN and silently validates empty input.
uv run gz content compose AGENTS.md --consumer claude --candidate /tmp/claude.md
uv run gz content compose AGENTS.md --consumer codex  --candidate /tmp/codex.md
```

**STOP THERE.** `gz content compose` writes a *candidate* and emits byte
evidence; it never writes a rendered surface. Promotion is
`uv run gz content commit`, which requires human attestation — landing a
recomposed `AGENTS.md` is a Layer-1 canon change and Gate 5 is universal
(ADR-0.0.36). **This chore does the compression labor and hands the operator a
candidate to attest. It never lands canon itself.**

`tier: invariant` corpus entries are verbatim-preserved by the composer and are
not compressible by any amount of editorial judgment. The compressible budget is
the non-invariant remainder; measure it rather than assuming it.

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
uv run gz validate --invariant-coherence
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz lint
uv run mkdocs build --strict
uv run -m unittest -q
```

`--invariant-coherence` leads because it is the only one of these that can see
whether a rendered surface drifted from the rendition it is played back from.
Through `1.0.0` it was absent from every acceptance list in this chore, so the
chore's own gate was blind to the exact failure its § 3 procedure invited.

### 7. Measure

Re-run the inventory and record the post-trim baseline in
`proofs/post-trim-YYYY-MM-DD.txt`. Compute the delta and record it in
`proofs/CHORE-LOG.md`.

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 0 | No rendered surface drifted from its rendition | `uv run gz validate --invariant-coherence` exit 0 |
| 1 | Advisory scorecard audit passes | `uv run gz validate --advisory-scorecard` exit 0 |
| 2 | Documents and surfaces validate | `uv run gz validate --documents --surfaces` exit 0 |
| 3 | Lint clean | `uv run gz lint` exit 0 |
| 4 | Docs build strict | `uv run mkdocs build --strict` exit 0 |
| 5 | Tests pass | `uv run -m unittest -q` exit 0 |
| 6 | Control-surface sync clean | `uv run gz agent sync control-surfaces` reports no stale or divergent mirrors |
| 7 | Per-turn contract weight reduction recorded | `proofs/baseline-*.txt` and `proofs/post-trim-*.txt` exist with a measurable line-count delta |
| 8 | Every binding bullet retained | Each Mechanical / Promotable scorecard entry resolves to a bullet still present in the per-turn contract (manual cross-check recorded in `proofs/bullet-retention-audit.md`) |
| 9 | Pedagogy reachable via in-line link | Every pillar that lifted narrative carries a one-line pointer to its destination page |
| 10 | `AGENTS.md` compression authored in the corpus, not the rendered file | `git diff` shows changes under `.gzkit/corpus/` and `.gzkit/renditions/`; a diff touching `AGENTS.md` with no corresponding corpus change is drift, not a trim |
| 11 | Canon left at the attestation boundary | A composed candidate exists at `.gzkit/renditions/AGENTS.md/<consumer>.candidate.md` and `gz content commit` has NOT been run by the chore — promotion is the operator's Gate 5 act |

## Evidence Commands

```bash
wc -l AGENTS.md CLAUDE.md .claude/rules/*.md
uv run gz validate --invariant-coherence
uv run gz validate --instructions-files-budget
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz lint
uv run mkdocs build --strict
uv run -m unittest -q
uv run gz agent sync control-surfaces
```

`--instructions-files-budget` is the outcome measure: it reports each surface's
byte distance to its budget AND to each consuming vendor's delivery cap. Budget
overruns are advisory until 1.0 by operator ruling; a vendor-cap exceedance is a
physical truncation no gzkit ruling can stay, so that line is the one this chore
exists to move.

## Anti-patterns

- Removing a Mechanical or Promotable bullet to hit a line-count target
  ("lighter ceremony is not a tradeoff axis")
- Lifting binding bullets to `docs/governance/` and replacing them with a
  pointer — only narrative rationale lifts; bullets stay
- Treating the line-count delta as the headline metric — bullet retention
  is the floor; the delta is the by-product
- Editing `.claude/rules/**` mirrors directly — edit `.gzkit/rules/**` and
  let sync propagate
- **Editing `AGENTS.md` directly** — it is played back from a committed
  rendition composed out of `.gzkit/corpus/AGENTS.md.jsonl`. A hand-edit is
  drift that `gz validate --invariant-coherence` fails closed and that
  `gz agent sync control-surfaces` overwrites. Author against the corpus (§ 3a)
- **Running `gz content commit` from this chore** — promotion of a candidate to
  the committed rendition is a Layer-1 canon change requiring human attestation
  (Gate 5 is universal, ADR-0.0.36). The chore composes and stops
- **Compressing a `tier: invariant` corpus entry** — the composer preserves them
  verbatim and the invariant floor is not an editorial judgment. Compress the
  non-invariant remainder, and measure it rather than assuming it
- **Reading a byte figure out of a markdown doc** — thresholds and measurements
  live in JSON and in validator output. Re-derive from
  `uv run gz validate --instructions-files-budget`; a number in prose is a dated
  record, never the authority
- Running this chore mid-OBPI without a quiet tree — the diff is large
  and reviewing it tangled with feature work hides binding-bullet drift

## Related

- GHI #327 — origin
- GHI #817 — the `2.0.0` correction: `1.0.0` edited rendered and mirror surfaces
- GHI #815 — the Codex delivery-cap breach this chore's shrink pass would relieve
- GHI #533 — the `<15k` shrink destination
- `AGENTS.md` § Why this contract is not minimal — articulated tradeoff
- `AGENTS.md` § Extracted pedagogy — lift precedent
- `docs/governance/advisory-rules-audit.md` — scorecard catalogue
- `.gzkit/rules/skill-surface-sync.md` § Non-negotiable rules #4 — mirror prohibition
- `ADR-0.0.37` / `ADR-0.35.0` — the composition architecture § 3a routes through
- `docs/governance/agent-contract-rationale.md` — established lift home
- `.claude/rules/skill-surface-sync.md` — canonical-vs-mirror discipline
