# Plan — OBPI-0.0.37-17: AGENTS.md Density Classification (#519 byte relief)

## Context

OBPI-11/12 built a correct temperature dial (`src/gzkit/content/render/pipeline.py`:
a bullet renders iff `density_min` ≤ the requested temperature; `density_min=None`
renders at every tier — the 0-Kelvin floor). OBPI-13/14 wired `sync_agents_md` to
render the root `AGENTS.md` from the `AgentContract` master model. **But the dial is
inert:** every `Bullet` parsed from `src/gzkit/templates/agents.md` carries
`density_min=None`, so lite/medium/heavy emit byte-identical output. The committed
`AGENTS.md` is **32,651 B** — only 117 B under Codex's 32,768-byte `project_doc_max_bytes`
cap (GHI #519). This OBPI classifies the corpus so the dial thins non-binding prose,
then renders the shared root at `medium` to get under cap with headroom.

### Forced blocker → operator-ratified brief amendment (Option A, 2026-06-03)

Relieving #519 requires sync to write the root at `medium` (≤30,000). But
`gz validate --invariant-coherence` (in the default `gz check` scope) renders via
`src/gzkit/governance/compose.py`, which **hardcodes `temperature="heavy"`** (line 72)
and byte-compares to the committed root. The instant committed=medium, it drifts from
compose(heavy) → `gz check` fails. The conflict is **mathematically forced**: a working
dial (REQ-03: lite<medium<heavy) + committed=medium (REQ-01) *guarantees*
committed ≠ compose(heavy) unless the dial is inert — the exact defect this OBPI kills.
Every allowed-path escape is closed (heavy can't shrink — REQ-05; committed can't stay
heavy — REQ-01/06; the validator isn't in allowed paths). The fix touches two **denied**
paths. Operator ratified the amendment.

**Key code facts established during planning:**
- `compose.py:render_agents_md` **ignores its `invariants` param** and renders the
  `AgentContract` template at hardcoded heavy (lines 61–72). It is squarely on the
  AgentContract path this OBPI owns — the brief's "OBPI-09 registry path" rationale is
  factually stale.
- `sync_agents_md` already reads the tier from `temperature_for("AgentContract","claude")`
  (`data/vendor-manifest.json` → currently `heavy`); the `claude_temp = "heavy"` literal
  at `sync_surfaces.py:375` is **only the no-manifest fallback**, never hit in this repo.
  So flipping the manifest entry flips sync automatically — no sync logic change needed.
- `render_content_surface` (the generic vendor-mirror renderer) has **zero callers**;
  `CLAUDE.md` renders from its own template and redirects via `@AGENTS.md`. So the
  `AgentContract.claude` manifest entry is consumed by exactly one writer (the shared
  root) + the coherence validator. Setting `claude→medium` thins **only** the shared
  root — no Claude mirror to over-thin, no separate "root tier" knob required.

## Step 0 — Amend the OBPI-17 brief (operator-attested)

File: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-17-agents-md-density-classification.md`

1. **Allowed Paths** — add:
   - `src/gzkit/governance/compose.py` (render at the sync/relief tier, not hardcoded heavy)
   - `data/vendor-manifest.json` (the single tier source: `AgentContract.claude` heavy→medium)
   - `features/steps/constitutional_invariants_steps.py` (only if new BDD steps are needed; reuse existing steps first)
2. **REQ-05** — reword: `heavy` render matches a captured **pre-classification baseline**
   (annotations stripped), not "the committed surface" (which becomes `medium` after this
   lands and would make the literal wording self-falsifying).
3. **Denied Paths / REQ-07** — rewrite the compose.py rationale: compose.py is the
   AgentContract path (OBPI-14 repurposed it; `invariants` param ignored), not the
   registry path. Registry surfaces (`.gzkit/invariants/*.yaml`, `gz governance render`)
   remain denied.
4. Record the amendment in the brief's Implementation Summary; operator attests at Gate 5
   (foundation + heavy + universal).

## Step 1 — Classify the corpus via mechanism (a): template annotations + parser

**Mechanism choice (a), recorded per REQ-04:** density carried as durable annotations in
`src/gzkit/templates/agents.md`, read by an extended `markdown_parser`. Chosen over (b)
because it preserves the existing template-as-source pipeline and "zero hand-authored
prose at the rendered location" (the template is source; the rendered root loses the
markers). The scorecard-derived `classification` path is too fragile to drive the dial
(4 classes vs the brief's 3, defaults to `Ambiguous`, keyed to a doc that doesn't cover
every bullet).

- **Annotation convention** (HTML comments — safe against `str.format_map`, stripped at
  parse, never rendered):
  - Section: `## Section Title <!-- density: heavy -->` → sets `Pillar.tier`
  - Bullet: `- <!-- density: medium --> text` → sets `Bullet.density_min`
- **Classification mapping** (drives the dial through `density_min` / `tier`; no new
  enum value needed — `_Classification` stays as-is, `density_min: _Temperature` is the
  driver):
  - **Binding / anti-vibe** (PRIME DIRECTIVE, DO IT RIGHT, SKILLS FIRST, Behavior Rules
    Always/Never, anti-vibing + stdlib + OEE operative claims) → `classification="Judgment"`
    → auto `density_min="lite"` via the existing floor validator (`bullet.py:34-39`) →
    renders at **every** tier (REQ-02).
  - **Mechanical enforcement** (Pattern Discovery, Defect-fix routing decision protocol,
    Skills protocol) → `density_min="medium"`.
  - **Reference** (Persona table, Gate Covenant tables, Kinds table, Canonical-invocation
    table, Execution Rules, Control Surfaces, "Why this contract is not minimal",
    rationale prose) → `density_min="heavy"` (dropped at medium/lite).
- **Parser changes** — `src/gzkit/content/parse/markdown_parser.py`:
  - `_extract_pillar_bullets` (lines 267–284): parse the bullet `<!-- density: X -->`
    marker, strip it from `text`, pass `density_min=X` to the `Bullet(...)` constructor
    (line 283 currently passes only `text`, `indent`, `classification`).
  - `_build_pillars` (lines 287–305): parse the section-heading `<!-- density: X -->`
    marker, set `Pillar.tier=X` (currently always defaults `tier="lite"`).
  - Marker grammar is net-new code with its own unit tests (REQ-04).

## Step 2 — Make sync + validator render the root at `medium` (coherently)

- `data/vendor-manifest.json`: `content_type_temperatures.AgentContract.claude`
  `"heavy"` → `"medium"`. This single edit flips `sync_agents_md` (already manifest-driven)
  to write the root at medium.
- `src/gzkit/governance/compose.py` line 72: render at
  `temperature_for("AgentContract","claude", project_root=project_root)` instead of the
  hardcoded `"heavy"`, with a `heavy` fallback on `ValueError` (mirroring
  `sync_surfaces.py:369-375` exactly). Now the coherence validator and sync agree → no
  drift. Add the lazy `temperature_for` import alongside the existing imports.
- `src/gzkit/sync_surfaces.py`: no logic change; update the docstring (lines 353-356) that
  still says `temperature="heavy"`.

## Step 3 — Budget calibration (REQ-06)

- `data/instructions_files_budget.json`: `files.AGENTS.md` `33000` → `30000` (under the
  32,768 cap with headroom; ties GHI #579). Update the `_doc` note.

## Step 4 — Tests (RED→GREEN; assertions derive from REQ semantics)

`tests/content/test_round_trip_agent_contract.py` (+ parser unit tests near the markdown
parser's existing tests):
- **REQ-04 mechanism**: parsing a template with `<!-- density: medium -->` markers sets
  the bullet's `density_min` and strips the marker from `text`; section marker sets
  `Pillar.tier`. (New parser unit tests.)
- **REQ-03 dial-not-inert**: on the live `src/gzkit/templates/agents.md`,
  `render(model,'claude',temperature='lite') < ... 'medium' < ... 'heavy'` (byte sizes,
  strict). Fails if all-tiers-identical regresses.
- **REQ-02 Judgment floor**: every `Judgment` bullet renders at `lite`; assert specific
  binding markers (PRIME DIRECTIVE / DO IT RIGHT / Behavior Rules / anti-vibing mantra)
  survive the `lite` render.
- **REQ-05 semantic preservation at heavy**: strip all `<!-- density: ... -->` markers
  from the template text in-test, render both annotated and stripped at `heavy`, assert
  byte-identical (proves annotations are metadata-only — no reword/drop). No 32 KB fixture.
- `tests/governance/` **REQ-01 #519 regression**: the live rendered root `AGENTS.md`
  ≤ 30,000 B (under the 32,768 cap). Follow the pattern in
  `tests/governance/test_audit_instructions_files_budget.py`.
- `@covers("REQ-0.0.37-17-NN")` on each, matching the existing decorator style.

## Step 5 — BDD (REQ coverage, Gate 4)

`features/constitutional_invariants.feature`: add `@REQ-0.0.37-17-01..08` scenarios
(dial-live, Judgment-floor-at-lite, root-fits-cap). **Reuse existing step definitions**
from OBPI-15 (render-at-temperature, "Judgment bullet present", "heavy-only bullet absent")
where possible; only add to `features/steps/constitutional_invariants_steps.py` if a new
phrasing is unavoidable (and only then under the Step-0 path addition).

## Step 6 — Docs (Gate 3)

- `docs/user/runbook.md`: "to edit AGENTS.md, edit `src/gzkit/templates/agents.md`
  (model/annotations) and re-render; the shared root renders at the #519-relief tier
  (`medium`)."
- Update the budget note where the 33000→30000 change is referenced.
- `uv run mkdocs build --strict`.

## Critical files

| File | Change |
|------|--------|
| `…/obpis/OBPI-0.0.37-17-*.md` | Step 0 brief amendment (operator-attested) |
| `src/gzkit/templates/agents.md` | density annotations (section + bullet) |
| `src/gzkit/content/parse/markdown_parser.py` | `_extract_pillar_bullets`, `_build_pillars` read/strip markers |
| `src/gzkit/governance/compose.py` | render at manifest tier (heavy fallback) — **amended path** |
| `data/vendor-manifest.json` | `AgentContract.claude` heavy→medium — **amended path** |
| `src/gzkit/sync_surfaces.py` | docstring only (already manifest-driven) |
| `data/instructions_files_budget.json` | AGENTS.md 33000→30000 |
| `tests/content/test_round_trip_agent_contract.py` + parser tests | REQ-02/03/04/05 |
| `tests/governance/…` | REQ-01 #519 cap regression |
| `features/constitutional_invariants.feature` (+ steps if needed) | `@REQ-0.0.37-17-*` |

`src/gzkit/content/models/bullet.py` / `agent_contract.py`: **no change expected** —
`classification`, `density_min`, `Pillar.tier`/`enabled`/`order` already exist; the
Judgment→lite floor is already coded.

## Verification (end-to-end)

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.content.test_round_trip_agent_contract -v
uv run -m unittest discover -s tests -t .          # full suite incl. new governance test
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature --tags=REQ-0.0.37-17

# REQ-01 hard requirement (live root fits Codex cap with headroom)
uv run python -c "
from pathlib import Path
b=len(Path('AGENTS.md').read_text(encoding='utf-8').encode('utf-8'))
assert b<=30000, f'AGENTS.md {b} B exceeds 30000'; print(f'REQ-01 OK — {b} B')
"

# REQ-03 dial live on the source template
uv run python -c "
from pathlib import Path
from gzkit.content.parse import parse
from gzkit.content.render import render
m=parse(Path('src/gzkit/templates/agents.md').read_text(encoding='utf-8'),'AgentContract')
s={t:len(render(m,'claude',temperature=t)) for t in ('lite','medium','heavy')}
print('tier sizes:',s); assert s['lite']<s['medium']<s['heavy'], f'inert/non-monotonic: {s}'
print('REQ-03 OK — dial live')
"

# Coherence gate must stay green (the whole reason for Step 2)
uv run gz validate --invariant-coherence
uv run gz check
```

Then re-render surfaces and re-run the plan audit:
```bash
uv run gz agent sync control-surfaces   # regenerate AGENTS.md root + mirrors via sync
# /gz-plan-audit OBPI-0.0.37-17   (expect PASS now that a plan exists and brief is amended)
```

After approval, run the pipeline: `uv run gz obpi pipeline OBPI-0.0.37-17`.

## Notes / risks

- **Coherence gate is the load-bearing risk.** Step 2 must land in the same commit as the
  manifest flip, or `gz check` fails between edits. Render compose.py and sync from the
  identical `temperature_for(...)` call so they cannot diverge.
- **Achieved `medium` size is an output, not a target.** REQ-01's hard bound is ≤30,000;
  the operator's ~16 KB medium aim is advisory. Report actual lite/medium/heavy bytes in
  the Implementation Summary; classify honestly (Judgment floor is non-negotiable).
- **Re-render before committing** so the committed root reflects the medium render and the
  coherence + budget gates see the new bytes.
