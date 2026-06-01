# OBPI-0.0.37-12 — Temperature Renderer + lite/medium/heavy Templates

## Context

**Why this work, now.** The operator directed "work #519 first." Emergency GHI #519
(*codex context surface exhausts 258K window*) is the one acute L1-ROOT item in the
return-to-health recovery. Its remediation vehicle is the **Context-Load CMS** workstream
— ADR-0.0.37's density-dial composition (OBPIs 11–16). The CMS renders AGENTS.md from a
master content model at a chosen *temperature* (lite/medium/heavy) instead of a
hand-authored monolith; the Codex `lite` tier is the named #519 relief.

OBPI-0.0.37-11 (density-aware master model) is **Completed + attested** — the model layer
is built. OBPI-12 is the next brick: the **renderer** that consumes a temperature and
projects the model to deterministic bytes.

**Honest expectation (advisor-flagged):** OBPI-12 delivers **zero #519 byte relief** by
itself. The brief is explicit — *"Renderer only — wiring is OBPI-14."* AGENTS.md stays at
32,121 B / 98% of cap until **OBPI-14** retires the monolith and **OBPI-15** lands the
Codex `lite` tier. "#519 first" means a **12 → 13 → 14 → 15 chain**; this is brick 1 of 4.

**Lane:** Heavy + Foundation → Gate 5 human attestation required; no self-close.

## Current State (verified this session)

- `_Temperature = Literal["lite","medium","heavy"]` already defined in
  `src/gzkit/content/models/agent_contract.py:10` and `bullet.py:9`.
- `Bullet` (`bullet.py:13-41`) has `classification`, `witness`, `rationale_ref`,
  `density_min`; a `@model_validator` pins `Judgment` bullets to `density_min="lite"`
  (0-Kelvin floor, enforced at model time).
- `Pillar` (`agent_contract.py:13-25`) has `id`, `title`, `order`, `enabled` (default
  `True`), `tier` (default `"lite"`), `bullets`. `AgentContract.pillars: list[Pillar]`.
- `render()` (`src/gzkit/content/render/pipeline.py:77-123`) signature is
  `render(model, vendor, *, project_root=None) -> bytes`. **No temperature param.**
  Byte-stability comes from frozen Pydantic `model_dump()` (insertion order) + Jinja2
  `StrictUndefined`, `keep_trailing_newline=True`, cached `FileSystemLoader`.
- Template `src/gzkit/content/templates/agentcontract/claude.md.j2` renders only
  `name`/`purpose`/`tech_stack`/`rules` — **`pillars` is completely ignored today**; no
  density logic anywhere.
- Tests: `unittest` (not pytest); `@covers("REQ-...")` from `gzkit.traceability`;
  byte-stability stubs in `tests/content/test_byte_stability.py` (`_STUB_AGENT_CONTRACT`).

## Design Decisions (surfaced for approval — grounded, not invented)

1. **Density-aware projection in Python, not Jinja filtering.** A pure function
   `_project_for_temperature(model, temperature) -> AgentContract` filters bullets/sections
   and returns a new frozen model; the template just iterates the projected structure. This
   keeps the filtering logic directly unit-testable, preserves byte-stability (frozen dump +
   sorted pillars), and satisfies REQ-5 (one template set, temperature as a parameter — **no
   three forked template files**). The brief's "templates iterate bullets/sections with
   density logic" is honored by the template now rendering the *projected* pillars.

2. **Section withholding is the coarse axis and wins (grounded in REQ-3).** Brief REQ-3 is
   unconditional: *"a section MUST be withheld when enabled=False or tier above
   temperature."* So a withheld section drops all its bullets — including any `Judgment`
   bullet. The 0-Kelvin floor (REQ-2) applies to bullets **within rendered scopes**
   (top-level `rules` + included pillars). A well-formed master model should not place a
   Judgment bullet in a high-tier section; preventing that is an authoring-time concern, not
   this renderer's. *If you read the floor as overriding section withholding, say so at
   approval — it flips REQ-02/REQ-03 test assertions.*

3. **`density_min=None` → never thinned (grounded in the OBPI-13 hardening note).** A
   non-Judgment bullet with no explicit `density_min` renders at **every** temperature. This
   mirrors the recorded principle *"the dial can never thin an unenforced rule"* — absent
   explicit density metadata, content is conservatively retained. Explicit omission requires
   an explicit `density_min` above the requested temperature.

4. **`temperature` default = `"heavy"`.** Preserves current behavior for all existing
   `render()` callers (heavy = full fidelity = strict superset). Temperature is validated for
   every model class (fail-closed, REQ-1) but only `AgentContract` is projected; other
   content types ignore it.

## Implementation

### Renderer — `src/gzkit/content/render/pipeline.py`
- Add keyword param: `render(model, vendor, *, temperature="heavy", project_root=None)`.
- **Validate `temperature` first, before routing/template lookup** (REQ-1, fail-closed):
  reject anything outside `{lite, medium, heavy}` with a clear error.
- Add module-level `_TEMP_RANK = {"lite": 0, "medium": 1, "heavy": 2}`.
- Add pure helpers:
  - `_bullet_renders(bullet, temperature) -> bool`:
    `True` if `classification == "Judgment"` **or** `density_min is None` **or**
    `_TEMP_RANK[density_min] <= _TEMP_RANK[temperature]`.
  - `_project_for_temperature(model: AgentContract, temperature) -> AgentContract`:
    filter `rules` by `_bullet_renders`; keep pillars where
    `pillar.enabled and _TEMP_RANK[pillar.tier] <= _TEMP_RANK[temperature]`, sort kept
    pillars by `order`, filter each kept pillar's bullets by `_bullet_renders`; build a new
    `AgentContract`.
- In `render()`: after temperature validation, if `isinstance(model, AgentContract)`,
  replace `model` with the projection, then proceed through the existing `model_dump()` +
  `template.render()` path unchanged (byte-stability preserved).

### Template — `src/gzkit/content/templates/agentcontract/*.md.j2`
- Add a `pillars` rendering block after `rules` (iterate `pillars`, emit `## {{ pillar.title }}`
  then each bullet as `{{ '  ' * bullet.indent }}- {{ bullet.text }}`), matching the existing
  bullet idiom. Apply to **every** vendor template present in the `agentcontract/` dir for
  consistency (confirm the file set at implementation time; explore saw `claude.md.j2`).
- No new template files; no `temperature` variable passed into Jinja (projection already
  applied in Python).

### Tests (TDD — RED first, then GREEN)
`tests/content/test_render_pipeline.py` (build `AgentContract` fixtures inline, per existing
direct-construction style):
- `@covers("REQ-0.0.37-12-01")` — render `lite` omits a `density_min="heavy"` bullet but
  keeps a `lite`/`None` bullet and a `Judgment` bullet.
- `@covers("REQ-0.0.37-12-02")` — `render(model, "claude", temperature="ultra")` raises
  before template lookup (fail-closed).
- `@covers("REQ-0.0.37-12-03")` — a pillar with `enabled=False` or `tier` above temperature
  is absent; included pillars appear in `order`.
- `@covers("REQ-0.0.37-12-05")` — `lite` output's rendered bullet set ⊆ `heavy` output
  (monotonic density superset).

`tests/content/test_byte_stability.py`:
- `@covers("REQ-0.0.37-12-04")` — repeated `render(model, "claude", temperature=T)` is
  byte-identical for each `T` (extend the existing stub/subTest pattern).

> If `@covers` raises `ValueError: Unknown REQ` at import, the brief's REQs are not yet
> extracted — that is a STOP-and-investigate signal, **not** a cue to backfill a cosmetic
> decorator (per `.gzkit/rules/adr-audit.md`).

### BDD (Gate 4, Heavy)
OBPI-12 adds no CLI surface (wiring is OBPI-14), so there is no command to drive a Gherkin
scenario. **Expectation: behave coverage is waived here per the OBPI-11 sibling precedent**
(schema/renderer-only; BDD deferred to ADR closeout). Confirmed/recorded during the pipeline
ceremony stage — not fabricated as a CLI scenario with no backing command.

## Execution path (after this plan is approved)

1. **Claim the OBPI lock** for `OBPI-0.0.37-12` (`gz-obpi-lock`) — verify whether
   `gz obpi pipeline` claims it; if not, claim first (token-block discipline is fail-closed).
2. Run the governed pipeline: **`uv run gz obpi pipeline OBPI-0.0.37-12`** (runtime owns
   stage sequencing: implement → verify → ceremony → guarded git-sync → completion;
   `uv run gz git-sync --apply --lint --test` before final accounting).
3. **Stop before Gate 5** and present durable evidence for human attestation (Heavy +
   Foundation → universal Gate 5; never self-close). Advisor checkpoint here.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.test_render_pipeline -v
uv run -m unittest tests.content.test_byte_stability -v
# Key proof — lite vs heavy byte diff:
uv run python -c "from gzkit.content.render import render; ..."   # render same model at lite vs heavy, diff byte length
```

Acceptance: REQ-0.0.37-12-01..05 each covered by a passing `@covers` test; byte-stable at
every temperature; `gz check` green; Gate 5 human attestation recorded.
