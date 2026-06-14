# Agent Control Surface Rendering Substrate — Doctrine

> **North star.** Agent = Model + Harness + Intent. Harness = vendor harness (Claude Code, Codex, Copilot) + local extension. **gzkit is the governance meta-harness layer:** it does not replace the vendor model/tool loop; it composes, validates, and audits the control surfaces and deterministic tools that wrap that loop. The **Agent Control Surface** is the per-turn corpus the harness loads on the model's behalf — `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`, skill bodies, the chore registry, persona files, handoffs. **gzkit is control surfaces and tools designed so that operator intent makes the model's intrinsic weaknesses and negative tendencies inert.**
>
> This doctrine governs the substrate gzkit composes those control surfaces from.

## Binding claim

> **Every file in the per-turn agent control surface is rendered from a canonical Pydantic content model via a Jinja2 template, deterministically, byte-stably, vendor-aware. Nothing in the per-turn surface is hand-authored at the rendered location. Vendor mirrors (`.claude/`, `.codex/`, `.github/`) are derived outputs. The fidelity validators (ADR-0.0.33) check the rendered output against the canonical models. The substrate is the harness's own integrity layer.**

This is gzkit's headless-CMS doctrine. It is the long-forecast generalization of ADR-0.0.19's `gz justify` Pydantic+Jinja2 rendering pattern, applied to the entire agent control surface. It supersedes ADR-0.16.0's aspirational naming with an authored substrate doctrine and a deliberate delivery sequence.

## Invariant Tier — 0-Kelvin Floor

`tier: invariant` corpus entries are emitted **verbatim at every setpoint** — they are
never dropped, combined, or rewritten by the compression composer. This is the
0-Kelvin floor: the dial thins only `compressible` content; invariant content is
exact operator intent, analogous to the immutable upstream system prompt the
operator cannot edit.

Enforcement: `gzkit.content.tier_policy.assert_invariant_verbatim(corpus, rendered_text)`
raises `ValueError` on any violation. The canonical named invariants — PRIME DIRECTIVE,
DO IT RIGHT, NEVER PYTEST — MUST survive verbatim at the leanest setpoint (`lite`).

## Prompt assembly and cache stability

Prompt assembly order is part of the substrate contract. gzkit does not control
vendor prompt-cache internals, but it does control the bytes it renders and the
order in which stable and volatile material appear.

The rendering pipeline must preserve this order:

1. Stable gzkit covenant and vendor-independent policy prefix.
2. Stable project control surfaces such as `AGENTS.md`, rules, personas, and
   skills.
3. Path-scoped or task-scoped dynamic context.
4. Volatile runtime state, preferably as pointers to durable artifacts rather
   than pasted transcript text.

This ordering keeps the highest-value static prefix byte-stable for vendor
prompt caching, makes drift diffable, and prevents volatile run facts from
invalidating the invariant surface. Any renderer or hook that injects mutable
session content ahead of the stable prefix creates a substrate defect.

## Why this doctrine is foundation-tier

By the invariance test (foundation = "without it, we wouldn't be doing the project"):

- gzkit's purpose is to make stochastic LLM vibing structurally inert at the agent control surface.
- The control surface is presently a mix of hand-authored static files and partially-templated mirrors. Hand-authored surfaces accrete vibe-coded drift; the failure pattern recorded in ADR-0.14.0's and ADR-0.16.0's closeout audits is the empirical evidence.
- Without a canonical content-model substrate that the surface is *rendered from*, every authoring action is a vibing surface — the operator (or agent) edits markdown directly, drift is invisible until validation runs, and the validators themselves have to grep static files instead of diffing canonical models.
- A substrate that authors against Pydantic models + Jinja2 templates + vendor-aware rendering is the structural backstop the fidelity doctrine (ADR-0.0.33) rests on. Without it, the fidelity doctrine's validators are weaker and the per-turn surface's drift is harder to catch.

This is the foundation/feature distinction applied: the substrate is the invariant; specific implementation features (TUI, LSP integration, retrieval-time disclosure, CMS-styled web admin) are feature-tier work that may or may not happen, but the substrate's invariant binds regardless.

## Derivation from upstream pillars

This doctrine derives from existing canon, not adjacent to it:

- **PRIME DIRECTIVE #5 (FLAG DEFECTS, NEVER EXCUSE THEM):** drift in the rendered control surface is a defect; the substrate makes drift detectable at compile time rather than at audit time.
- **DO IT RIGHT #1 (fix the class of failure, not the instance):** hand-edited surfaces are a class of failure; this substrate closes the class.
- **MAKE LLM STOCHASTIC VIBES INERT operative claim 2 ("lighter ceremony is not a tradeoff axis"):** the substrate is heavier than direct hand-authoring; that weight is the product, not overhead.
- **OPERATOR ECONOMY OF EFFORT operative claim 1 ("agent drafts; operator reviews"):** the substrate is the form constraint the agent drafts against; the operator reviews the rendered output and the canonical model interchangeably; both are valid review surfaces, but the rendered output is human-readable prose (the canonical model is agent-input only per OPERATOR ECONOMY anti-patterns).
- **STDLIB-FIRST DOCTRINE:** Pydantic is the explicit named departure from stdlib (validation semantics stdlib does not supply); Jinja2 is a named departure for template-engine semantics; both inherit the named-rationale-required rule.

The doctrine does not introduce a new philosophical claim. It names what the upstream pillars already imply and gives that implication mechanical teeth.

## Scope — the headless-Django mapping

The "CLI/TUI Django for these files" framing (operator's verbatim) commits the substrate to deliver the full Django-shape over time, not just templating. The mapping:

| Django concept | gzkit-substrate equivalent | Binding commitment |
|---|---|---|
| **Models** | Pydantic content models per surface (`AgentContract`, `Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, `Scenario`, `Bullet`, …) with `frozen=True, extra="forbid"` | All per-turn surface artifacts MUST have a canonical Pydantic model |
| **Migrations** | Schema versioning + content-lifecycle state machine (ADR-0.16.0 OBPI-05 is the seed; this doctrine generalizes its scope) | Models evolve under attestation; rendered output stays consistent across schema generations |
| **Templates** | Jinja2 templates per (content type × vendor) producing deterministic byte-stable markdown | One canonical model produces N vendor mirrors deterministically |
| **Views / URLs** | CLI verbs (`gz content edit / render / import / list / show / migrate`) | Operator-direct invocation surface; output is human-readable prose, not raw JSON |
| **Admin** | Agent-mediated dialogical tuning + light CLI/TUI affordances consistent with Claude Code's own surface idioms | The agent IS the authoring UI under operator direction; no heavy editor surface |
| **ORM** | Pydantic models over filesystem (today); pluggable backend later | Content is queryable as data, not just files; storage backend is not the doctrine |
| **Forms** | Pydantic models + structured Jinja2 scaffold templates the operator-and-agent fill dialogically | Form constraints are encoded in the model + the scaffold template; not a separate form layer |
| **Validation** | Pydantic + the fidelity validators from ADR-0.0.33 | Cannot save a content model that violates invariants; cannot render output that violates fidelity |
| **Signals / hooks** | Ledger event emission on content lifecycle transitions | Every authoring action is auditable in the ledger |
| **Reverse rendering** | Markdown-to-model parser per content type (ADR-0.0.19's `gz justify validate` is the precedent) | Round-trip fidelity is a binding contract |

**The eight-component delivery scope:**

1. **Content model registry generalization.** Extend ADR-0.16.0 OBPI-01 (rules-only registry) to all per-turn surface artifacts. Every artifact type has a registered Pydantic model with lifecycle, schema, and rendering rules.
2. **Rendering pipeline.** Replace the file-copy logic in `gz agent sync` with a Jinja2-templated render-from-canonical pipeline per content type × vendor. Outputs at the canonical mirror locations.
3. **Reverse-parse migration tooling.** `gz content import <file> --as <type>` reads existing hand-authored markdown back into a canonical Pydantic model so existing surfaces migrate without loss.
4. **Authoring CLI.** `gz content edit / render / list / show` — operator-direct invocation; output is human-readable prose summary, never raw JSON.
5. **Light TUI affordances.** Claude-Code-style status lines, chore-runner-style result tables, plan-mode-style panels — native CLI affordances. **No Textual form editor, no dedicated authoring app.**
6. **Validation hooks.** Every render and every save fires the ADR-0.0.33 fidelity validators. Output that fails validation does not land.
7. **Migration layer.** Pydantic schema versioning so model refactors do not break rendered-output stability across releases.
8. **Vendor manifest expansion.** ADR-0.16.0 OBPI-03 seeded the vendor manifest schema; this doctrine binds it as the canonical declaration of which content types render to which vendor mirrors.

The doctrine commits to all eight as the binding scope. OBPIs deliver them in priority order, not all at once.

## The authoring surface — agent-mediated dialogical tuning

The canonical authoring mode in gzkit is **agent-mediated dialogical tuning against a structured Pydantic+Jinja2 scaffold**, with operator-correctional authority preserved through the OPERATOR ECONOMY pillar. This is canonical because:

- ADR-0.0.19 (`gz justify`) is the precedent: an 8-section Walkthrough scaffold the operator and agent fill dialogically; operator fills `_[To be filled]_` blocks via normal interaction; agent drafts substantively; operator corrects verbatim; ceremony attests.
- The 2026-04-25 complexity-doctrine handoff records the binding decision: *"Distillation is agent-driven, human-reviewed and attested/corrected (not 'joint authoring')."*
- ADR-0.0.30 OBPI-04 records the precedent for editor integration: gzkit specifies the contract (LSP-style JSON-over-stdio); editor authors implement editor UIs. **gzkit's scope is the protocol surface, not the editor ecosystem.**
- The OPERATOR ECONOMY pillar explicitly forbids machine-readable surfaces as review surfaces. The rendered markdown is the review surface; the Pydantic model is agent-input only.

**What this means concretely:**

| Mode | Surface | Authoring action |
|---|---|---|
| **Direct CLI** | `gz content edit <type> <id>` | Opens the canonical model as a Jinja2-rendered markdown scaffold (with `_[To be filled]_` blocks where the model has empty fields); operator and agent iterate dialogically; `gz content save` validates and ledger-records the lifecycle transition |
| **Direct render** | `gz content render <type> <id> --vendor=<v>` | Renders the canonical model to the vendor-specific mirror location; deterministic byte-stable output |
| **Migration** | `gz content import <file> --as <type>` | Reverse-parses an existing rendered file into the canonical model; supports operator-supervised migration of existing hand-authored surfaces |
| **Listing/discovery** | `gz content list / show` | Human-readable prose summary tables; Rich-rendered; never raw JSON in operator review surface |
| **Editor integration (forecast)** | LSP-style JSON-over-stdio protocol specified as a contract | Editor authors consume the contract; gzkit does not implement editor plugins |

**What is explicitly NOT in scope:**

- Textual TUI form editor
- Rich form-shaped UIs for content authoring
- Web admin interface
- Dedicated content-authoring desktop app
- Replacing the agent dialogue with a non-dialogical UI

These are anti-patterns. The agent IS the authoring UI; the templates ARE the form constraints; the Pydantic model IS the validation layer; the ceremony IS the attestation. Adding a UI on top of that stack is over-tooling for a problem the dialogical mode already solves.

## Worked example — `AgentContract` content model

Concrete demonstration: the model behind `AGENTS.md` itself.

```python
# src/gzkit/content/models/agent_contract.py
from pydantic import BaseModel, ConfigDict, Field

class Bullet(BaseModel):
    """A single binding bullet on the agent control surface."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    id: str = Field(..., description="Stable bullet ID (e.g. PRIME-DIR-1)")
    text: str = Field(..., description="The binding bullet text — verbatim")
    classification: str = Field(..., description="Mechanical | Promotable | Judgment | Ambiguous")
    origin_ghi: int | None = Field(None, description="GHI that authored or last revised the bullet")

class Pillar(BaseModel):
    """A top-level H2 section of the agent contract."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(..., description="Pillar name (e.g. PRIME DIRECTIVE)")
    subtitle: str | None = Field(None, description="Parenthetical subtitle (e.g. OWNERSHIP)")
    bullets: list[Bullet] = Field(default_factory=list)
    derivation: str | None = Field(None, description="One-line derivation pointer to upstream pillar")
    pointer_targets: list[str] = Field(
        default_factory=list,
        description="Lift-pointer destinations under docs/governance/",
    )

class AgentContract(BaseModel):
    """Canonical content model for AGENTS.md."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    project_name: str
    project_purpose: str
    tech_stack: str
    north_star: str = Field(..., description="The Agent = Model + Harness + Intent framing")
    pillars: list[Pillar]
    behavior_rules_always: list[Bullet]
    behavior_rules_never: list[Bullet]
    gate_covenant_rows: list["GateRow"]
    attestation_pattern: str
    defect_fix_routing: "DefectFixRoutingTable"
    architectural_boundaries: list[Bullet]
    governance_doctrine_surfaces: list["DoctrinePointer"]
```

A change to AGENTS.md is then expressed as:

1. `gz content edit agent_contract --section pillars` — opens the rendered scaffold for the pillars section
2. Operator and agent iterate dialogically; agent drafts; operator corrects verbatim
3. `gz content save` validates against the Pydantic model and records the lifecycle transition in the ledger
4. `gz content render agent_contract --vendor=root` renders to `AGENTS.md` deterministically
5. ADR-0.0.33 fidelity validators confirm: every Mechanical/Promotable bullet from the canonical model lands in the rendered output; line-count regression is within tolerance; pointer anchors resolve

The same pattern applies to every other surface artifact (`Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, …). The Pydantic shape and the Jinja2 template are different per content type; the substrate's contract is the same.

## Round-trip fidelity contract

Every content type MUST satisfy:

```
content_model = parse(render(content_model))
```

For any canonical Pydantic model instance, render-then-parse must reconstruct an equivalent instance. ADR-0.0.19's `gz justify validate` is the reference implementation. The contract is binding: a content type that cannot round-trip is not substrate-compliant.

This is what enables existing hand-authored surfaces to migrate without loss: parse the existing markdown, get a canonical model, store it, render-from-model going forward. Any drift between the parsed-then-rendered output and the original input is itself a fidelity finding the validators surface.

## Levers and constraints (what gzkit controls vs. influences vs. cannot govern)

| Layer | Lever (gzkit owns) | Constraint (gzkit accepts) |
|---|---|---|
| Canonical content models | Pydantic schema authorship; validation; lifecycle | — |
| Rendering | Jinja2 template authorship; vendor-aware output paths; deterministic byte-stable rendering | — |
| Prompt assembly order | Stable-prefix, dynamic-context, and volatile-state ordering | Vendor prompt-cache implementation and cache-hit policy |
| Vendor mirrors | Sync to vendor-mirror locations; mirror-fidelity validation | Vendor harnesses honor the mirror format; if a vendor changes its loading semantics, gzkit's templates adapt to the new format |
| Loading per turn | — | Vendor harness decides what to load (path-scoped frontmatter for Claude Code, equivalent for Codex/Copilot) |
| Within-turn dynamics | — | Context window is append-only at runtime; no DOM-style manipulation; "forgetting" only exists between turns |
| Authoring | Agent-mediated dialogue; CLI verbs; LSP-style protocol contract | Editor implementations are the editor ecosystem's responsibility |

The doctrine works the levers gzkit owns to shape outcomes within constraints gzkit does not control. **The substrate's resilience is exactly that it does not depend on runtime control of the vendor harness.** Composition happens between turns; rendering happens before the agent loads; loading is the vendor harness's call. gzkit governs what gets composed and validates what was composed.

## Substrate-invariance across implementation eras

The doctrine governs the *output's fidelity to its declared invariants*, not the composition method. This means the doctrine survives implementation transitions:

| Era | Composition method | What changes | What does not change |
|---|---|---|---|
| **Era 1 — today** | Hand-authored static files (mostly) + partial templating (`src/gzkit/templates/agents.md` → AGENTS.md via naive substitution) | — | Validators check rendered output against canonical models (where models exist) |
| **Era 2 — substrate landed** | Pydantic + Jinja2 deterministic rendering for all content types; vendor-aware sync | Composition method becomes principled; canonical models exist for all surfaces | Validators are stronger (diff against canonical models, not grep static files); rendered output shape is unchanged |
| **Era 3 — progressive disclosure** | Scenario-aware retrieval composes per-turn surface from canonical models on demand | Loading scenarios become first-class; surface size becomes per-scenario; per-turn weight is amortized | Validators still check rendered output; the per-scenario render is what gets validated |

In every era, the agent reads a static document. What changes is *how the document is composed*. **Errors of what is printed become feedback for the CMS process (the composition pipeline) regardless of which era's pipeline is active.** The doctrine's invariants survive the transitions; the validators evolve to test the active composition method.

## Anti-patterns

- **Editing rendered output directly.** `AGENTS.md`, `.claude/rules/<rule>.md`, `.gzkit/skills/**/SKILL.md` are derived outputs; edits land in the canonical model, then propagate via render.
- **Building a heavy TUI editor.** The agent is the authoring UI; light CLI affordances suffice; LSP-style protocol contracts are the path for editor integration.
- **Asking the operator to read raw Pydantic-model JSON.** Per OPERATOR ECONOMY: rendered markdown is the review surface; the canonical model is agent-input only.
- **Bypassing round-trip fidelity.** A content type that cannot parse-then-render-then-parse to identity is not substrate-compliant.
- **Skipping the migration layer.** Existing hand-authored surfaces migrate via `gz content import`, not via "we'll re-author from scratch."
- **Injecting volatile context before the stable prefix.** It weakens prompt-cache behavior and hides drift in the bytes that should be invariant.
- **Treating ADR-0.16.0's deliverable as the substrate.** ADR-0.16.0 delivered a partial prior — Pydantic content-type registry, vendor-aware sync (file-copy), lifecycle state machine. It did NOT deliver Jinja2-templated rendering for the full surface. The substrate doctrine generalizes ADR-0.16.0's scope to deliver what its prose promised.
- **Letting "lighter ceremony" become a tradeoff axis.** The substrate adds composition steps the operator may experience as friction. That friction is the product. Per the anti-vibing mantra.

## Related canon

- **ADR-0.0.19 (Validated, foundation):** `gz justify` — the Pydantic+Jinja2 deterministic rendering precedent. The substrate doctrine generalizes this pattern.
- **ADR-0.16.0 (closed, drifted):** "CMS Architecture Formalization" — partial prior. Delivered Pydantic registry + vendor-aware sync + lifecycle state machine. Did not deliver Jinja2-templated rendering for the full surface. The substrate doctrine is the authored capture of what ADR-0.16.0 promised.
- **ADR-0.0.33 (paired foundation, this cluster):** Agent Control Surface Fidelity Doctrine. The fidelity invariants the substrate's rendered output must preserve.
- **ADR-0.0.30 (Validated, foundation):** Complexity Authoring Guidance. Precedent for "specify the protocol; do not implement the editor."
- **ADR-0.0.33 (airlineops, Pool):** Agent Context Engineering. 12-Factor Agents grounding (Factor 3 — Own Your Context Window; Factor 9 — Compact Errors). 384-session empirical evidence.
- **Pool cluster (gzkit):** `ADR-pool.progressive-context-disclosure`, `ADR-pool.brief-loaded-context-manifest`, `ADR-pool.focused-context-loader`, `ADR-pool.execution-memory-graph`, `ADR-pool.cross-session-search`, `ADR-pool.compression-governance-hooks`, `ADR-pool.rag-anything-governance-retrieval`. Future-feature work that consumes the substrate's invariants when promoted.
- **Pool stub (gzkit):** `ADR-pool.gz-interview-render` — render machine-readable artifacts as human-readable prose for operator review. Same JSON-review-anti-pattern this doctrine inherits from OPERATOR ECONOMY.

## Origin

GHI #327 — instructions-files-diet pass surfaced a long-deferred doctrine gap during a pass-1 lift. The substrate doctrine is the authored capture of a design conversation whose canonical artifact had been lost across ADR-0.0.19's Future Considerations forecast, ADR-0.16.0's aspirational naming, and the pool cluster's distributed intentions. This page consolidates them into one foundation-tier artifact.
