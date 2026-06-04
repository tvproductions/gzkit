---
id: OBPI-0.0.37-17-agents-md-density-classification
parent: ADR-0.0.37-constitutional-invariant-composition
item: 17
lane: Heavy
status: Abandoned
---

# OBPI-0.0.37-17-agents-md-density-classification: AGENTS.md Density Classification (#519 byte relief)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #17 — "OBPI-0.0.37-17 — AGENTS.md density classification (classify the AgentContract corpus so the temperature dial is no longer inert; render the shared root AGENTS.md at a tier that fits Codex's 32,768-byte cap with headroom — the concrete #519 byte relief)"

**Status:** Draft

## Objective

Make the temperature dial real on the live AGENTS.md surface, then use it to relieve emergency GHI #519.

OBPI-11/12 built a correct density renderer (`src/gzkit/content/render/pipeline.py`: a bullet renders iff `_TEMP_RANK[density_min] <= _TEMP_RANK[temperature]`; `density_min=None` renders at every temperature — the 0-Kelvin floor). OBPI-13/14 wired `sync_agents_md` to render the root `AGENTS.md` from the `AgentContract` master model. **But the dial is inert:** every `Bullet` parsed from the source carries `density_min=None`, so `render(model, "lite")`, `render(model, "medium")`, and `render(model, "heavy")` all emit byte-identical output (verified 2026-06-03: template renders 23,403 B at every temperature; committed `AGENTS.md` renders 32,651 B at every temperature). The machine is connected to nothing.

This OBPI supplies the classifications the machine acts on, and the parse/authoring mechanism to carry them durably:

1. **Classify the corpus.** Assign each `Bullet` a `classification` (`Judgment` / `Mechanical` / `Reference`) and the derived `density_min` tier across the whole AGENTS.md content, so the dial thins non-Judgment prose while the 0-Kelvin floor preserves every binding/anti-vibe rule.
2. **Carry the classification durably.** The parser (`src/gzkit/content/parse/markdown_parser.py`) currently sets no density — the annotation mechanism is **net-new**. Choose and implement exactly one: (a) density annotations in `src/gzkit/templates/agents.md` read by an extended `markdown_parser`, or (b) an authored classified `AgentContract` model store rendered directly. The choice is an in-scope design decision recorded in the Implementation Summary.
3. **Relieve #519.** Render the shared root `AGENTS.md` at the lowest tier that stays Judgment-complete and fits Codex's 32,768-byte `project_doc_max_bytes` cap with real headroom (target tier: `medium`). Codex reads only repo-root `AGENTS.md` (no vendor sink, no path redirect, silent truncation past the cap — see ADR-0.0.37 § Codex-loader finding via the return-to-health plan), so the shared-surface shrink is the only mechanism that relieves the emergency.

**Calibration targets (operator-directed, advisory):** heavy ≈ full corpus (~32 KB), medium ≈ half (~16 KB), lite ≈ the Judgment floor (~8 KB). These are calibration aims, not fail-closed bounds — the achieved `lite` size is an *output* of how much of AGENTS.md is genuinely binding (Judgment bullets force `density_min=lite`), reported in evidence. The fail-closed requirement is #519-fits-cap (REQ-01), which `medium` satisfies comfortably.

## Why a new OBPI (not OBPI-09 repurposed)

OBPI-09 (`agents-md-migration`) targets the **invariant-registry** render path: `.gzkit/invariants/*.yaml` → `gz governance render --target agents-md` → `compose.py` (OBPI-02). This OBPI works on the **AgentContract/Bullet** path: `gzkit.content.parse` → `gzkit.content.render` driven by `sync_agents_md` (the OBPI-13/14 lineage; `sync_surfaces.py:365/376`). Different store, different renderer, different files — repurposing OBPI-09 would collide with its registry REQs and cross-references (ADR line 264 supersession note; GHI #495/#485), not complete it. OBPI-09's superseded-but-pending disposition is pre-existing drift surfaced by the 2026-06-03 plan-audit and is routed separately (OBPI-10 doctrine-refresh / ADR-0.0.37 closeout), not bundled here.

## Lane

**Heavy** — changes how the universal `AGENTS.md` contract renders (content visibly thinned for every agent that reads the root surface). Heavy + foundation + universal Gate 5 per ADR-0.0.36. Operator attests the classification because "which rules are droppable below heavy" is a governance judgment, not a mechanical one.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` (parent reference; read-only)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-17-agents-md-density-classification.md` (this brief)
- `src/gzkit/content/parse/markdown_parser.py` (add density-annotation parsing — mechanism (a))
- `src/gzkit/templates/agents.md` (annotate bullets with density tiers — mechanism (a)) **OR** the authored classified model store (mechanism (b)); exactly one mechanism is implemented
- `src/gzkit/content/models/bullet.py` (only if the classification enum or `density_min` validation needs extension — minimal; the 0-Kelvin floor is already coded)
- `src/gzkit/sync_surfaces.py` (render the shared root at the chosen tier — `sync_agents_md` is already manifest-driven via `temperature_for("AgentContract","claude")`; the call-site `heavy` literal is only the no-manifest fallback, so the docstring is updated and the tier flips via `data/vendor-manifest.json`)
- `data/vendor-manifest.json` (**amended-in 2026-06-03, operator-ratified**) — the single tier source: set `content_type_temperatures.AgentContract.claude` `heavy`→`medium` so the shared root renders at the #519-relief tier
- `src/gzkit/governance/compose.py` (**amended-in 2026-06-03, operator-ratified**) — render the AgentContract template at `temperature_for("AgentContract","claude")` (heavy fallback) instead of hardcoded `heavy`, so `gz validate --invariant-coherence` and `gz governance render` stay byte-coherent with the medium-rendered committed root. OBPI-14 repurposed compose.py onto the AgentContract path (its `invariants` param is ignored); it is NOT the registry path.
- `data/instructions_files_budget.json` (correct the AGENTS.md budget to fit Codex's 32,768-byte cap with headroom — closes the gate-miscalibration defect)
- `tests/content/test_round_trip_agent_contract.py` (add classification + per-tier byte-budget + Judgment-floor tests)
- `tests/governance/` (add #519-fits-cap regression test)
- `features/constitutional_invariants.feature` (migration/relief round-trip scenarios tagged `@REQ-0.0.37-17-*`)
- `features/steps/constitutional_invariants_steps.py` (**amended-in 2026-06-03**) — only if a new step phrasing is unavoidable; reuse OBPI-15 steps first

## Denied Paths

- Paths not listed in Allowed Paths
- `.gzkit/invariants/*.yaml` and the registry→bullet reconciliation (`gzkit.governance.invariants`) — the OBPI-09 registry data path remains out of scope. (Note, amended 2026-06-03: `src/gzkit/governance/compose.py` was moved to Allowed Paths. OBPI-14 already repurposed compose.py to render the **AgentContract template** at hardcoded `heavy` — its `invariants` param is ignored — so it is on the AgentContract render path this OBPI owns, not the registry path. The amendment changes only its temperature *source*, not its content source.)
- `CLAUDE.md` (operator-facing redirect; not a render target here)
- `.claude/rules/*.md`, `.gzkit/rules/*.md` (separate canon surface; rule-file budgets are out of scope)
- The *content semantics* of any rule — classification adds metadata and may thin prose at lower tiers, but the **heavy** render must remain semantically equivalent to today's AGENTS.md (REQ-07). Rewording rules is a separate ADR amendment.
- CI workflow files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT (#519 hard requirement): The shared root `AGENTS.md`, as rendered by `sync_agents_md` at its chosen temperature, is **≤ 30,000 bytes** — under Codex's 32,768-byte `project_doc_max_bytes` cap with real headroom. A regression test asserts the byte ceiling against the live render.
2. REQUIREMENT (0-Kelvin floor): Every `Judgment`-classification bullet renders at **every** temperature. A test asserts the binding core — PRIME DIRECTIVE, DO IT RIGHT, Behavior Rules (Always/Never), the anti-vibing mantra — survives intact at `lite`. No binding/anti-vibe rule is thinned at any tier.
3. REQUIREMENT (dial no longer inert): On the live AGENTS.md corpus, `render(model, "lite")` and `render(model, "medium")` are each **strictly smaller** than `render(model, "heavy")`. The inertness defect (all-tiers-identical) is closed and a test fails if it regresses.
4. REQUIREMENT (durable mechanism): Density classifications are carried by exactly one named, durable mechanism — (a) template annotations read by an extended `markdown_parser`, or (b) an authored classified model store — chosen and documented in the Implementation Summary. The parse/authoring path is net-new code with its own tests; classifications are not injected ad hoc at render time.
5. REQUIREMENT (semantic preservation at heavy): The `heavy` render remains semantically equivalent to the **pre-classification** corpus — a test strips the density annotations from the template and asserts the `heavy`-tier render is byte-identical to the render of the stripped template (classification adds metadata; it does not rewrite or drop rule text). *(Amended 2026-06-03: the baseline is the captured pre-classification render, not "the committed surface" — the committed surface becomes the `medium` render once this OBPI lands, which would make the original wording self-falsifying.)*
6. REQUIREMENT (budget calibration): `data/instructions_files_budget.json` sets the `AGENTS.md` budget to a value that fits Codex's 32,768-byte cap with headroom (≤ 30,000), closing the defect where the gate (33,000) exceeded the cap it guards. Ties GHI #579.
7. REQUIREMENT (no scope creep into registry data path): This OBPI does not modify the `.gzkit/invariants/` registry contents or the registry→bullet reconciliation; it operates on the AgentContract render path. The compose.py change aligns its temperature *source* with sync so that `gz governance render` and `gz validate --invariant-coherence` stay byte-coherent with the medium-rendered committed root — it does not change compose.py's content source. Coupling into the registry data path would be a brief-boundary violation.
8. REQUIREMENT (Gate 5 governance attestation): Operator attests the classification decision set — specifically that no rule classified below `Judgment` is in fact binding — recorded in the brief's Human Attestation with the per-tier byte evidence. Universal Gate 5.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision Extension (2026-05-30) "CIC-1 Density-Dial Composition" — the dial vision OBPI-11..16 implement
- [ ] ADR § Codex-loader finding (recorded in the return-to-health plan) — why per-vendor emission is ruled out and the shared-surface shrink is the only #519 lever
- [ ] ADR Decomposition Scorecard — the 16→17 increment rationale

**Governance:**

- [ ] `AGENTS.md` (every section — the classification source-of-truth; what is Judgment vs Mechanical vs Reference)
- [ ] `.gzkit/rules/tests.md` — Two-runners doctrine; assertions derive from REQ semantics
- [ ] `docs/governance/return-to-health-plan-2026-05-30.md` § Context-Load CMS — the #519 relief route and the dial-inert finding

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/render/pipeline.py` — the density filter the classification feeds (`_bullet_renders` line 31: `density_min=None` → renders at every temperature; `_project_for_temperature`)
- [ ] `src/gzkit/content/models/bullet.py` — `classification` / `density_min` fields (lines 18/27) and the coded Judgment→lite 0-Kelvin floor (lines 34-39)
- [ ] `src/gzkit/content/parse/markdown_parser.py` — current parse sets no density (the net-new annotation mechanism lands here)
- [ ] `src/gzkit/sync_surfaces.py:353-377` — `sync_agents_md` render path; the OBPI-15 `heavy` call-site default (line 369-376) to change to the #519-relief tier

**Prerequisites:**

- [ ] OBPIs 11, 12, 13, 14 landed (master model + renderer + reverse-parse + sync wiring) — all attested-complete
- [ ] `AGENTS.md` present and readable

## Quality Gates

- [ ] Gate 1: Classification recorded; per-tier byte evidence captured; mechanism choice (a/b) documented
- [ ] Gate 2: Per-tier byte-budget test + Judgment-floor test + dial-not-inert test + heavy semantic-stability test; RGR followed
- [ ] Code Quality: lint + typecheck; parser changes covered
- [ ] Gate 3: Runbook update ("if AGENTS.md needs an edit: go via the model/annotations and re-render; the root renders at the #519-relief tier"); budget note updated; mkdocs strict
- [ ] Gate 4: `features/constitutional_invariants.feature` includes `@REQ-0.0.37-17-*` scenarios; behave passes
- [ ] Gate 5: Operator attestation that no sub-Judgment classification is actually binding (foundation-kind + heavy + universal Gate 5)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.content.test_round_trip_agent_contract -v
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature --tags=REQ-0.0.37-17

# REQ-01 (#519 hard requirement): shared root render fits Codex cap with headroom
uv run python -c "
from pathlib import Path
b = len(Path('AGENTS.md').read_text(encoding='utf-8').encode('utf-8'))
assert b <= 30000, f'AGENTS.md {b} B exceeds 30000 headroom ceiling (Codex cap 32768)'
print(f'REQ-01 OK — AGENTS.md {b} B <= 30000 (Codex cap 32768)')
"

# REQ-03 (dial no longer inert): lite < medium < heavy on the live corpus
uv run python -c "
from pathlib import Path
from gzkit.content.parse import parse as parse_content
from gzkit.content.render import render as render_content_model
model = parse_content(Path('src/gzkit/templates/agents.md').read_text(encoding='utf-8'), 'AgentContract')
sizes = {t: len(render_content_model(model, 'claude', temperature=t).encode('utf-8')) for t in ('lite','medium','heavy')}
print('tier sizes:', sizes)
assert sizes['lite'] < sizes['medium'] < sizes['heavy'], f'dial still inert / non-monotonic: {sizes}'
print('REQ-03 OK — dial is live (lite < medium < heavy)')
"

# REQ-06 (budget calibration): AGENTS.md budget fits Codex cap
uv run python -c "
import json
b = json.load(open('data/instructions_files_budget.json'))['files']['AGENTS.md']
assert b <= 30000, f'AGENTS.md budget {b} exceeds 30000 (Codex cap 32768)'
print(f'REQ-06 OK — AGENTS.md budget {b} <= 30000')
"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-17-01: Live `AGENTS.md` render at the chosen tier is ≤ 30,000 bytes (under Codex's 32,768 cap with headroom); regression test asserts the ceiling
- [ ] REQ-0.0.37-17-02: Every `Judgment` bullet renders at every temperature; the binding core survives at `lite` (test-asserted)
- [ ] REQ-0.0.37-17-03: `render(lite) < render(medium) < render(heavy)` on the live corpus (inertness defect closed)
- [ ] REQ-0.0.37-17-04: Density carried by exactly one durable mechanism (template-annotation+parser OR authored classified model), net-new parse/authoring code with tests, documented in Implementation Summary
- [ ] REQ-0.0.37-17-05: `heavy` render byte-identical to the annotation-stripped template render (pre-classification baseline; classification is metadata-only — no reword/drop)
- [ ] REQ-0.0.37-17-06: `data/instructions_files_budget.json` AGENTS.md budget ≤ 30,000 (fits Codex cap; ties #579)
- [ ] REQ-0.0.37-17-07: No modification to `.gzkit/invariants/` registry contents or the registry→bullet reconciliation; compose.py temperature-source aligned with sync (registry data path untouched)
- [ ] REQ-0.0.37-17-08: Operator attestation that no sub-`Judgment` classification is actually binding, with per-tier byte evidence

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz obpi reconcile OBPI-0.0.37-17-agents-md-density-classification` reports zero drift
- [ ] Per-tier byte evidence recorded in Implementation Summary; #519 relief measured against the 32,768 cap

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: the CMS shipped a temperature dial (OBPI-11/12) wired to a model (OBPI-13/14) whose every bullet is unclassified, so heavy/medium/lite render identical bytes — an elaborate machine connected to nothing, and emergency #519 unrelieved. After: the corpus is density-classified, the dial is live, and the shared root AGENTS.md renders under Codex's 32,768-byte cap with headroom — #519 relieved on the one surface Codex actually reads, with every binding rule preserved by the 0-Kelvin floor. -->

### Key Proof

<!-- REQ-01 byte ceiling test (AGENTS.md <= 30000) + REQ-03 lite<medium<heavy on the live corpus + REQ-02 Judgment-floor test (binding core survives at lite) + per-tier byte evidence in the table. -->

### Implementation Summary

- **Brief amendment (operator-ratified, 2026-06-03):** A plan-audit established that REQ-01 (committed root ≤30,000) cannot be satisfied without breaking `gz validate --invariant-coherence`: that validator renders via `compose.py` at hardcoded `temperature="heavy"` (32,651 B) and byte-compares to the committed root, so the moment sync writes `medium` it drifts. The conflict is mathematically forced (a working dial + committed=medium guarantees committed ≠ compose(heavy) unless the dial is inert). Resolution: add `src/gzkit/governance/compose.py` and `data/vendor-manifest.json` to Allowed Paths; reword REQ-05 to a pre-classification baseline; rewrite REQ-07 / denied-path rationale (compose.py is the AgentContract path post-OBPI-14). Operator ratified via plan-mode AskUserQuestion ("Amend brief, one OBPI").
- Mechanism chosen (a template-annotation+parser / b authored model): **(a)** — durable density annotations in `src/gzkit/templates/agents.md`, read+stripped by an extended `markdown_parser`. Chosen over (b): preserves the template-as-source pipeline and "zero hand-authored prose at the rendered location"; the scorecard `classification` path is too fragile to drive the dial (defaults Ambiguous; 4 classes vs 3).
- Files created/modified:
- Tests added:
- Per-tier byte sizes (lite / medium / heavy) and chosen root tier:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #519 (the emergency this relieves), GHI #579 (budget calibration), GHI #580 (composition-renderer periphery ordering — adjacent; not in scope)

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive text grounded in the per-tier byte evidence and the classification decision set (no sub-Judgment rule is binding)
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
