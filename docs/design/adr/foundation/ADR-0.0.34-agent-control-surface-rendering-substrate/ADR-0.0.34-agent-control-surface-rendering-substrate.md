---
id: ADR-0.0.34-agent-control-surface-rendering-substrate
status: Validated
kind: foundation
semver: 0.0.34
lane: heavy
parent:
date: 2026-04-26
---

# ADR-0.0.34-agent-control-surface-rendering-substrate: Agent Control Surface Rendering Substrate

## Persona

`main-session` (craftsperson, governance-aware, whole-file-reasoning, direct).
This ADR codifies gzkit's headless-CMS doctrine — the substrate from which
every per-turn agent control surface is rendered. Authoring posture is
doctrine-author + substrate-architect: the eight-component delivery scope
must remain coherent across the OBPI sequence; light-CLI/light-TUI
discipline must hold against the temptation to build a heavy editor; the
agent-mediated dialogical authoring mode is the binding interaction model.

## Why foundation tier?

Without this ADR, the agent control surface is a hand-authored vibing surface — fidelity validators have nothing canonical to diff against, and per-turn agent context drifts from authored doctrine with no structural defense.

This ADR authors a port: the canonical rendering-substrate contract that fidelity validators bind to (the rendered surface is the spec; future renderers are plugs behind it).

## Intent

**Current state.** The per-turn agent control surface (`AGENTS.md`,
`CLAUDE.md`, `.claude/rules/**`, skill bodies, the chore registry, persona
files, handoffs) is hand-authored markdown with no canonical content model.
Vendor mirrors are produced by `shutil.copy`-style propagation in
`sync_surfaces.py`; mirror-drift defects recur (e.g. `.claude/skills/` vs
`.gzkit/skills/` divergence); validators check the output after the fact
with substring grep, not against a canonical schema. Authoring is itself a
vibing surface.

**Target state.** Every per-turn surface file is rendered byte-stably from a
canonical Pydantic content model via a Jinja2 template, vendor-aware.
Round-trip fidelity (`model = parse(render(model))`) is the binding
substrate contract. The fidelity validators (ADR-0.0.33) check rendered
output against the canonical model rather than against substring patterns.
The authoring action is a model edit, not a markdown edit.

> **Agent = Model + Harness + Intent.** The Agent Control Surface is the
> per-turn corpus the harness loads on the model's behalf — `AGENTS.md`,
> `CLAUDE.md`, `.claude/rules/**`, skill bodies, the chore registry, persona
> files, handoffs. **gzkit is control surfaces and tools designed so that
> operator intent makes the model's intrinsic weaknesses and negative
> tendencies inert.**

This ADR canonizes the substrate gzkit composes those control surfaces
from. The full doctrine lives at
[`docs/governance/agent-control-surface-rendering-substrate.md`](../../../../governance/agent-control-surface-rendering-substrate.md);
this ADR is the lifecycle anchor that lands its eight-component delivery.

The originating signals are: (a) ADR-0.0.19's Future Considerations forecast
of a generalization ADR for the `gz justify` Pydantic+Jinja2 deterministic
rendering pattern; (b) ADR-0.16.0's "CMS Architecture Formalization"
shipping a partial prior (Pydantic registry + vendor-aware sync via file
copy + lifecycle state machine) without the Jinja2-templated rendering its
prose promised; (c) GHI #327's diet pass surfacing the empirical question
of how gzkit knows the per-turn surface preserves its rules across
authoring actions. ADR-0.0.34 is the authored capture of what those three
signals point at.

ADR-0.0.34 is the substrate ADR-0.0.33's fidelity validators evolve to
test against in Era 2. The two ADRs are paired foundation: fidelity is the
structural backstop; substrate is the canonical authoring surface that
backstop rests on.

## Decision

**Every file in the per-turn agent control surface is rendered from a
canonical Pydantic content model via a Jinja2 template, deterministically,
byte-stably, vendor-aware. Nothing in the per-turn surface is hand-authored
at the rendered location. Vendor mirrors (`.claude/`, `.codex/`, `.github/`)
are derived outputs. The fidelity validators (ADR-0.0.33) check the
rendered output against the canonical models. The substrate is the
harness's own integrity layer.**

This is gzkit's headless-CMS doctrine — *"CLI/TUI Django for these files"*
(operator's verbatim). It is the long-forecast generalization of
ADR-0.0.19's `gz justify` rendering pattern, applied to the entire agent
control surface. It supersedes ADR-0.16.0's aspirational naming with an
authored substrate doctrine and a deliberate eight-component delivery
sequence:

1. **Content model registry generalization.** Extend ADR-0.16.0 OBPI-01
   (rules-only registry) to all per-turn surface artifacts.
2. **Rendering pipeline.** Replace file-copy logic in `gz agent sync` with
   a Jinja2-templated render-from-canonical pipeline per content type ×
   vendor.
3. **Reverse-parse migration tooling.** `gz content import <file> --as <type>`
   reads existing hand-authored markdown back into a canonical Pydantic
   model so existing surfaces migrate without loss.
4. **Authoring CLI.** `gz content edit / render / list / show` —
   operator-direct invocation; output is human-readable prose summary,
   never raw JSON.
5. **Light TUI affordances.** Claude-Code-style status lines, chore-runner
   result tables, plan-mode panels — native CLI affordances. **No Textual
   form editor, no dedicated authoring app.**
6. **Validation hooks.** Every render and every save fires the ADR-0.0.33
   fidelity validators.
7. **Migration layer.** Pydantic schema versioning so model refactors do
   not break rendered-output stability across releases.
8. **Vendor manifest expansion.** ADR-0.16.0 OBPI-03 seeded the vendor
   manifest schema; this ADR binds it as the canonical declaration of
   which content types render to which vendor mirrors.

The authoring mode is **agent-mediated dialogical tuning against a
structured Pydantic+Jinja2 scaffold**, with operator-correctional authority
preserved through the OPERATOR ECONOMY pillar. The agent IS the authoring
UI under operator direction; the templates ARE the form constraints; the
Pydantic model IS the validation layer; the ceremony IS the attestation.
A heavy TUI editor or web admin is explicitly anti-pattern. Editor
integration is via LSP-style JSON-over-stdio protocol contract specification
only (gzkit specifies; editor authors implement) — precedent: ADR-0.0.30
OBPI-04.

**Round-trip fidelity contract:** every content type satisfies
`content_model = parse(render(content_model))`. ADR-0.0.19's
`gz justify validate` is the reference implementation; the contract is
binding for substrate compliance.

The doctrine is **substrate-invariant across implementation eras**: it
governs the rendered output's fidelity to its declared invariants, not the
composition method. Era 1 (today's hand-authored + partial-templated) →
Era 2 (substrate landed) → Era 3 (progressive disclosure) — *errors of
what is printed become feedback for the CMS process (the composition
pipeline) regardless of which era's pipeline is active*.

## Comparator Uplift (2026-05-07)

Kiro, Spec Kit, BMAD, Superpowers, and Compound Engineering all improve the
human-facing entry point. gzkit should absorb the UX lesson through this
substrate: better rendered panels, tighter generated prompts, and package-aware
skill surfaces. The rendering substrate remains headless and governed; polish is
acceptable only when the rendered output remains byte-stable, parseable, and
validator-bound.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Rendered agent control surfaces stay byte-faithful to their canonical source; the rendering-substrate fidelity invariant holds. | uv run gz validate --surface-fidelity | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.34-agent-control-surface-rendering-substrate --check | 0 |

## Consequences

### Positive

- The per-turn agent control surface stops being a hand-authored vibing
  surface. Every rendered file traces to a canonical Pydantic model;
  drift becomes a fidelity finding the validators surface at compile
  time.
- The fidelity doctrine (ADR-0.0.33) gains its Era-2 validators: substring
  grep upgrades to canonical-model diff without invalidating Era-1
  evidence.
- ADR-0.0.16.0's aspirational scope ships in this ADR's eight-component
  delivery rather than drifting further.
- Vendor mirrors become deterministic outputs of one canonical model,
  closing the class of mirror-drift defects (`.claude/skills/` vs
  `.gzkit/skills/` divergence, etc.) at the substrate layer.
- The pool cluster (`progressive-context-disclosure`,
  `brief-loaded-context-manifest`, `focused-context-loader`,
  `execution-memory-graph`, `cross-session-search`,
  `compression-governance-hooks`,
  `rag-anything-governance-retrieval`) gains a coherent substrate to
  consume when promoted; Era 3 (progressive disclosure) becomes a
  composition-method change against the same substrate, not a re-author.

### Negative

- The substrate is materially heavier than direct hand-authoring. Per the
  anti-vibing mantra ("lighter ceremony is not a tradeoff axis"), this is
  the product, not overhead — but it is a real cost the operator
  experiences during authoring.
- Eight OBPIs is a long delivery sequence. Sequencing matters: components
  1, 2, 8 must land before 3 (migration cannot run without a registry
  and a render pipeline); 4, 5 depend on 2; 6 depends on 1, 2, and the
  ADR-0.0.33 validators; 7 lands last as the schema-evolution backstop.
- Pydantic and Jinja2 are named departures from stdlib (per Stdlib-First
  doctrine). The rationales are explicit (validation semantics; template
  engine semantics) and inherited from ADR-0.0.19's precedent, but the
  substrate concentrates dependence on those two libraries across the
  authoring surface.
- The migration layer (component 7) defers Pydantic schema evolution
  cost; if it slips, every model refactor creates a re-render burden
  across the surface.
- Editor integration is forecast-only via LSP-style protocol contract.
  Operators who prefer in-editor authoring of the canonical models will
  experience a gap until the editor ecosystem implements the contract;
  gzkit's scope is the protocol, not the editors.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 3
- Final Target OBPI Count: 8

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.34-01: Content model registry generalization — extend ADR-0.16.0 OBPI-01 to all per-turn surface artifacts (`AgentContract`, `Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, `Scenario`, `Bullet`, …) with `frozen=True, extra="forbid"`
- [ ] OBPI-0.0.34-02: Rendering pipeline — Jinja2 templates per (content type × vendor) producing deterministic byte-stable markdown; replace file-copy logic in `gz agent sync` with render-from-canonical
- [ ] OBPI-0.0.34-03: Reverse-parse migration tooling — `gz content import <file> --as <type>` reads existing hand-authored markdown back into canonical Pydantic models; round-trip fidelity contract enforced
- [ ] OBPI-0.0.34-04: Authoring CLI — `gz content edit / render / list / show` with human-readable prose output (never raw JSON in operator review surface)
- [ ] OBPI-0.0.34-05: Light TUI affordances — Claude-Code-style status lines, Rich tables, plan-mode-style panels; explicitly NOT a Textual form editor
- [ ] OBPI-0.0.34-06: Validation hooks — every render and every save fires the ADR-0.0.33 fidelity validators; output that fails validation does not land
- [ ] OBPI-0.0.34-07: Migration layer — Pydantic schema versioning so model refactors do not break rendered-output stability across releases
- [ ] OBPI-0.0.34-08: Vendor manifest expansion — extend ADR-0.16.0 OBPI-03 vendor manifest schema as the canonical declaration of which content types render to which vendor mirrors

## Q&A Transcript

<!-- Interview transcript preserved for context -->

The doctrine page is the canonical Q&A capture. See
[`docs/governance/agent-control-surface-rendering-substrate.md`](../../../../governance/agent-control-surface-rendering-substrate.md)
for the headless-Django mapping, the agent-mediated dialogical authoring
mode, the substrate-invariance argument across Eras 1/2/3, and the
worked example of the `AgentContract` content model behind `AGENTS.md`.

The 2026-04-25 complexity-doctrine handoff records the binding decision:
*"Distillation is agent-driven, human-reviewed and attested/corrected
(not 'joint authoring')."* That decision binds the authoring mode for
this ADR's OBPIs.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/content/test_agent_contract_round_trip.py`, `tests/content/test_render_pipeline.py`, per-content-type round-trip fidelity tests under `tests/content/`
- [ ] Docs: `docs/governance/agent-control-surface-rendering-substrate.md`, `docs/user/manpages/gz-content.md` (forthcoming)
- [ ] Models: `src/gzkit/content/models/**`
- [ ] Templates: `src/gzkit/content/templates/**`
- [ ] CLI: `src/gzkit/commands/content/**`
- [ ] Vendor manifest: `data/vendor-manifest.json`
- [x] Partial-prior audit (ADR-0.16.0 historical-drift acknowledgement): `artifacts/audits/adr-0.16.0-closeout-drift-2026-04-26.md` (GHI #332 — Jinja2-templating substrate gap, heavy-parent lite-self-closed OBPIs, terminal-dirty receipts; scope generalized into this ADR's eight-component delivery rather than re-attesting the partial prior).

## Alternatives Considered

- **A — Stay hand-authored; rely on ADR-0.0.33 validators alone.**
  Rejected: validators on a hand-authored surface are weaker (substring
  grep, not canonical-model diff); the authoring action itself remains
  a vibing surface; ADR-0.16.0's drift class stays open.
- **B — Build a heavy TUI editor (Textual app) for content authoring.**
  Rejected: per OPERATOR ECONOMY OF EFFORT, the agent IS the authoring
  UI; a heavy editor surface is over-tooling for a problem the
  dialogical mode already solves; the precedent is ADR-0.0.30 OBPI-04
  (specify the protocol; do not implement the editor).
- **C — Build a web admin (Django-style) for the canonical models.**
  Rejected: same anti-pattern as B at greater scope; introduces a web
  framework dependency for a problem that does not require it; rendered
  markdown is the operator review surface per OPERATOR ECONOMY.
- **D — Defer the substrate; ship Era-3 progressive disclosure first.**
  Rejected: Era 3 composes a per-turn surface from canonical content
  models on demand; without the substrate, there are no canonical
  models to compose from. Era 2 is a prerequisite for Era 3.
- **E — Re-author existing surfaces from scratch rather than build the
  reverse-parse migration tool.** Rejected: re-authoring loses operator
  intent embedded in existing markdown; round-trip fidelity is the
  binding contract; component 3 (`gz content import`) is the migration
  path.
- **F — Bundle the eight components into fewer OBPIs (e.g. five).**
  Rejected per the OBPI Decomposition Mandate's right-sizing protocol;
  each priority-ordered component is independently attestable and
  carries its own Gate-2 evidence; bundling collapses the firing point
  for governance gates per `gz-obpi-specify` rationale.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.34 | Completed | Jeffry | 2026-05-17 | Completed — ADR-0.0.34 agent-control-surface-rendering-substrate: 8/8 OBPIs attested_completed, 39/39 REQs covered 100%; canonical content substrate (Pydantic models + Jinja2 templates + vendor manifest) replaces shutil-copy mirror propagation per ADR Intent; gz content list/show/render/edit/import authoring CLI live (OBPI-04); gz validate --vendor-manifest scope live (OBPI-08); fidelity hooks wired at render and save (OBPI-06); migration registry stamped at schema_version=1 (OBPI-07); ARB receipts arb-ruff-88a38972158342088b2005974ff923b0, arb-step-unittest-a13ce5a677d149c494038df90901f2ca (5198/5198), arb-step-typecheck-2bb2b53f283244f59f5bc7ba558f139d, arb-step-mkdocs-f80e6d03c5644c198a852a2a18cec4a3 all clean; gz adr audit-check PASS; spec-reviewer + quality-reviewer independent passes both clean; no open GHIs reference ADR-0.0.34; operator attestation phrase "Completed" received via AskUserQuestion at Step 6 ATTESTATION 2026-05-17. |
