---
id: ADR-0.30.0-okf-documentation-knowledge-structure
status: Proposed
kind: feature
semver: 0.30.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-28
---

# ADR-0.30.0-okf-documentation-knowledge-structure: OKF documentation-knowledge structure

## Persona

Craftsperson with orientation-not-authority discipline: treats the OKF bundle as a
map, never a deed. Knows that the moment a generated convenience becomes citable
evidence, it stops being a map and starts forging title — so the no-enforcement fence
is a correctness property, not a nicety. Holds the tracer-bullet bar against the
reflex to "tag everything": success is ONE working progressive-disclosure path, not
corpus-wide coverage. Keeps source docs canonical and the bundle generated-and-additive,
so authorship discipline is never traded for navigability. Refuses to let a second
navigation structure compete with the existing compact-pointer model; the bundle
complements pointers or it is dead weight. Honors the content boundary as a placement
discipline — gzkit-core canon homes under `.gzkit/`, `docs/` is adopter space — and
names bundles by their knowledge DOMAIN, never by the OKF format. Treats the
docs/→`.gzkit/` migration as delicate: establishes the boundary now, moves the corpus
later, never inside a tracer bullet.

## Agent Context Frame — MANDATORY

This section establishes the mental model agents must carry through all OBPI execution.

**Role:** Knowledge-orientation architect. This is an ADDITIVE, generated orientation
layer over existing documentation — NOT a new authority surface, NOT a replacement for
authored docs, NOT a control-surface change. The CMS gains a documentation-knowledge
OKF emission path; the truth surfaces (ADRs, OBPIs, ledger, campaign, binding rules)
are untouched and remain the only evidence.

**Purpose:** Agents can find the relevant explanatory document via typed frontmatter,
descriptions, tags, links, and index files — traversing a self-describing bundle
instead of inferring structure from filename search and prose alone. The bundle is
generated over a narrow tracer slice; source docs stay canonical.

**Goals:**

- A typed OKF concept-frontmatter model (required `type`; optional
  title/description/resource/tags/timestamp) that is unknown-field- and
  unknown-type-tolerant per the OKF posture.
- A generated OKF bundle (root `index.md`, concept docs, directory `index.md`
  progressive disclosure, markdown-link edges) over the tracer slice, with source docs
  preserved canonical.
- `gz validate --okf-conformance` checks ONLY the generated bundle (parseable
  frontmatter, non-empty `type`; reserved `index.md`/`log.md` structure); it NEVER
  gates authored source docs.
- One documented progressive-disclosure path: a control surface points an agent into
  the bundle and the agent finds the right doc without a whole-corpus read.

**Critical Constraint:** OKF is an ORIENTATION layer, never an AUTHORITY layer. OKF
frontmatter and OKF links MUST NEVER be consumed as enforcement evidence by any
`gz validate` / gates / closeout surface (the STRUCTURAL-FENCE boundary invariant
below). Consumers MUST preserve the OKF posture: unknown frontmatter fields and unknown
`type` values are NOT errors. The validator scope is generated-bundle-only and MUST NOT
gate authored source documents.

**Anti-Pattern Warning:** A FAILED implementation lets the bundle become citable —
an OKF `type` or link consulted as proof somewhere in the gates/closeout surface (the
named authority-creep pre-mortem). Equally failed: scope-creep toward "all docs tagged"
instead of one working path; the validator silently widening to gate authored source
docs (turning a convenience into a second authoring gate); or a stale generated bundle
that drifts from its sources so agents trust wrong orientation.

**Integration Points:** `src/gzkit/schemas/` (new OKF concept-frontmatter JSON schema);
`src/gzkit/knowledge/` (the domain-named OKF model + bundle generator package — Pydantic,
per the named models departure; NOT an `okf`-named package); `src/gzkit/governance/trust_audits/`
(new `--okf-conformance` validator scope, recognizing bundles by reserved files + `type`,
never by folder name); `src/gzkit/commands/` + `src/gzkit/cli/` (new `gz knowledge` generate/refresh
subcommand — domain-named verb matching the `src/gzkit/knowledge/` package; no format-named
verb); `.gzkit/governance/knowledge/`
(DOMAIN-named generated bundle output for the governance tracer slice — a dedicated sub-root
under `.gzkit/governance/`, separate from the pre-existing `ontology.json`; state doctrine,
trust doctrine, agent-contract rationale, active campaign reference; NO `okf/` folder);
`.gzkit/` content-boundary doctrine doc (OBPI-06); manpages + both runbooks for the new
CLI surface and the progressive-disclosure path.

**Content boundary (carry this through every OBPI):** gzkit-core knowledge homes under
`.gzkit/` (domain-named); `docs/` is adopter space. The tracer bundle and the doctrine
doc both land under `.gzkit/`; the wholesale docs/→`.gzkit/` migration is phased and is
NOT performed in this tracer (Boundary Invariant 4).

## Tidy First Plan

Behavior-preserving tidyings before any behavior change; tests stay green throughout.

- Prep tidyings (behavior-preserving):
  1. Confirm the tracer-slice source docs (`docs/governance/state-doctrine.md`,
     `docs/governance/trust-doctrine.md`, `docs/governance/agent-contract-rationale.md`,
     the active campaign reference) exist and are stable targets before generating over
     them — the generator reads them read-only and never edits them.
  2. Survey the existing `gz validate --<scope>` audit pattern and the existing
     Pydantic schema shape under `src/gzkit/schemas/` so the OKF model and validator
     reuse the established patterns rather than inventing new ones (stdlib-first /
     named-departure discipline).

Separation of prep → change → polish: the schema/model lands first (OBPI-01,
foundation for everything downstream); the generator lands next (OBPI-02, produces the
bundle into the domain-named `.gzkit/governance/knowledge/` root); the conformance validator +
STRUCTURAL-FENCE land third (OBPI-03, the guard); the CLI surface lands fourth (OBPI-04,
the operator entry point); the docs/runbook progressive-disclosure path lands fifth
(OBPI-05, the success definition); the content-boundary doctrine doc lands last (OBPI-06,
authoring-only — establishes the boundary, performs NO migration). STOP/BLOCKERS: if any
tracer-slice source doc is missing or unstable, name it in a BLOCKERS list before
generating; do NOT begin any docs/→`.gzkit/` content move under this ADR.

## Intent

gzkit's documentation corpus (docs/governance/ doctrine, rationale, appraisal, research notes; docs/user/concepts/ explanatory docs; selected research_sources/) is large, and agents must infer its structure from filename search and prose alone — there is no typed, navigable semantic map over general app knowledge. Control surfaces are already trained to be compact pointers into deeper docs, but the pointed-to docs are not self-describing enough for an agent to traverse without reading the whole corpus. This ADR makes the CMS emit and maintain an OKF-conformant semantic map over documentation-knowledge surfaces (orientation layer only) so agents can find the relevant explanatory document via type hints, descriptions, tags, links, and indexes. OKF is NOT an authority layer in gzkit: ADRs, OBPIs, the ledger, the active campaign, and binding rules remain the truth surfaces. This is distinct from ADR-0.16.0 (CMS architecture formalization), which governs CONTROL-SURFACE rendering (the Django-parallel headless CMS turning canonical .gzkit/ content into vendor surfaces); OKF organizes DOCUMENTATION and the knowledge base to assist agents in general app knowledge. The two are orthogonal concerns with distinct consumers (operator clarification, 2026-06-28).

Authoring the OKF bundle surfaces a second, coupled concern this ADR now seats as a first-class part of the same decision (operator ruling, 2026-06-28): **where gzkit's documentation knowledge is HOMED**. gzkit currently places much of its core canon under `docs/`, but `docs/` is the surface an adopting project authors. In the operator's words: "`.gzkit/` should be things about gzkit's core function; `docs/` is about the adopting project"; "gzkit's binding canon of documentation — why it exists, what are its bounds — should live in `.gzkit/`"; "much of what we place into `/docs` really belongs in `.gzkit/`. This keeps it clean for implementing projects." This is "a delicate matter." The OKF feature cannot home a knowledge bundle correctly without resolving the content boundary, so this ADR establishes the boundary as doctrine and homes the tracer-slice bundle on the correct side of it. Two further facts from the OKF spec shape the homing: OKF requires exactly one field (`type`); and **OKF bundles are DOMAIN-named, never format-named** — there is no `okf/` namespace in the standard (the spec's own example root is `sales/`). OKF-conformance is a property of the markdown files (reserved `index.md`/`log.md` + a `type` frontmatter), not of a folder name.

## Decision

Generate a small, typed OKF-conformant markdown knowledge bundle over a documentation slice, following the Open Knowledge Format v0.1 draft: a root index.md, concept documents with YAML frontmatter carrying a required `type` and optional `title`/`description`/`resource`/`tags`/`timestamp`, directory index.md files for progressive disclosure, and markdown links as graph edges. Add a validator (gz validate --okf-conformance) that checks OKF conformance ONLY for the generated bundle: every non-reserved markdown file has parseable frontmatter and a non-empty `type`; reserved index.md and log.md follow OKF structure. Source docs are preserved as the canonical authored documents — the bundle is generated over them, never replacing them. gzkit may add producer-defined frontmatter keys where useful, but consumers MUST preserve the OKF posture: unknown fields and unknown `type` values are NOT errors. The first implementation is a tracer bullet (narrow slice: state doctrine, trust doctrine, agent-contract rationale, active campaign reference) proving one working progressive-disclosure path. A STRUCTURAL-FENCE boundary invariant is added to this ADR (operator decision, 2026-06-28): OKF frontmatter and OKF links MUST NEVER be used as enforcement evidence anywhere in the gz validate / gates / closeout surfaces — the fence audits at ADR-closeout layer and keeps the entire feature from drifting into an authority layer.

Two homing decisions are added (operator ruling, 2026-06-28). FIRST, the bundle root is **DOMAIN-named, never format-named**: there is no `okf/` folder anywhere — OKF-conformance is recognized by the validator through reserved files (`index.md`/`log.md`) and `type` frontmatter, not a namespace. The governance tracer slice (state doctrine, trust doctrine, agent-contract rationale, campaign reference) homes at `.gzkit/governance/knowledge/`; the implementation package is the domain-named `src/gzkit/knowledge/`. SECOND, this ADR establishes the **`.gzkit/` vs `docs/` content boundary** as doctrine: gzkit's core-function knowledge and the binding canon of documentation (why gzkit exists, what its bounds are) live under `.gzkit/`; `docs/` is reserved for adopter-authored project content. The consequence — that much of gzkit's current `docs/` core canon belongs under `.gzkit/` — is REAL but the migration is **phased and NOT performed in this tracer bullet**: OBPI-0.30.0-06 authors the content-boundary doctrine doc (homed under `.gzkit/`, eating its own dogfood) declaring the boundary and the phased relocation plan; the wholesale docs/→`.gzkit/` move is a forced subsequent decision, not this ADR's work. This is "a delicate matter" (operator) and is deliberately gated to doctrine-plus-tracer here.

## Interfaces

- **CLI (external contract):** `uv run gz knowledge generate` / `uv run gz knowledge refresh` — new
  subcommand that generates/refreshes the OKF bundle over the tracer slice (OBPI-04).
  Heavy lane: a new operator-facing CLI surface with manpage + `gz cli audit` coverage.
- **CLI (external contract):** `uv run gz validate --okf-conformance` — new validator
  scope (OBPI-03). Exit 0 clean; exit 3 on a generated-bundle conformance failure
  (unparseable frontmatter, empty `type`, or malformed reserved `index.md`/`log.md`).
  Generated-bundle-only — it does NOT gate authored source docs.
- **Schema surface:** new OKF concept-frontmatter JSON schema under
  `src/gzkit/schemas/` (required `type`; optional
  `title`/`description`/`resource`/`tags`/`timestamp`), unknown-field- and
  unknown-type-tolerant (OBPI-01).
- **Generated artifact surface:** the OKF bundle (root `index.md`, concept docs,
  directory `index.md` files, markdown-link edges) emitted over the tracer slice
  (OBPI-02). Generated and additive; source docs remain canonical.
- **Docs surface:** manpages for the new CLI verb + validator scope, both runbooks, and
  the documented progressive-disclosure path showing a control surface pointing an agent
  into the bundle (OBPI-05).
- **Doctrine surface:** the `.gzkit/` vs `docs/` content-boundary doctrine doc, authored
  under `.gzkit/` (OBPI-06), declaring the boundary and the phased docs/→`.gzkit/`
  relocation plan (the migration itself is NOT performed here).

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

1. **OKF frontmatter and OKF links are NEVER consumed as enforcement evidence by any
   `gz validate` / gates / closeout surface.** OKF is an orientation layer, never an
   authority layer. No `gz validate` scope, no gate, and no closeout step may read an
   OKF `type`, tag, description, or link as proof of a governance claim. Truth lives in
   canon (Layer-1) and the ledger (Layer-2); the OKF bundle is a Layer-3 derived
   navigation aid and, per state doctrine, is never source-of-truth. This is the
   load-bearing fence that keeps the entire feature from drifting into an authority
   layer (operator decision, 2026-06-28).
2. **The `--okf-conformance` validator scope is generated-bundle-only, and recognizes
   bundles by reserved files + `type` frontmatter, NEVER by folder name.** It checks
   ONLY the generated OKF bundle (identified by its reserved `index.md`/`log.md` and
   `type`-bearing concept docs); it MUST NEVER gate authored source documents and MUST
   NOT key off any `okf/`-named namespace. Widening the scope to validate authored docs
   would turn a navigation convenience into a second authoring gate — the re-coarsening
   failure this fence forbids.
3. **Consumers preserve the OKF posture: unknown fields and unknown `type` values are
   NOT errors.** The only required frontmatter field is `type`. gzkit may add
   producer-defined keys, but no consumer may reject a document for carrying an unknown
   field or an unrecognized `type` — that tolerance is what makes OKF an external
   convention rather than a revived bespoke taxonomy.
4. **The `.gzkit/` vs `docs/` content boundary holds: gzkit-core canon lives under
   `.gzkit/`; `docs/` is adopter space.** gzkit's core-function knowledge and the binding
   canon of documentation live under `.gzkit/` (domain-named, OKF-conformant); `docs/` is
   reserved for adopter-authored project content. The OKF feature NEVER writes core canon
   into `docs/` nor adopter content into `.gzkit/`, and OKF bundle roots are DOMAIN-named
   (no `okf/`-format namespace). The wholesale relocation of gzkit's existing `docs/`
   core canon into `.gzkit/` is a phased consequence declared by this ADR, NOT performed
   within it (operator ruling, 2026-06-28 — "a delicate matter").

## Rationale

The documentation corpus is large enough that agents pay a whole-corpus-read tax to
find the one explanatory doc they need; control surfaces are already compact pointers,
but the pointed-to docs are not self-describing, so the pointer model bottoms out at
"now read everything." A typed, navigable OKF bundle closes exactly that gap: type
hints, descriptions, tags, links, and index files let an agent traverse to the right
doc. The convention is deliberately EXTERNAL (OKF v0.1) rather than a revived
gzkit-specific doc-type taxonomy — Movement I already cut the 0.0.74 doc-type taxonomy
as a smuggled classification system, and OKF supplies the lighter convention without
re-opening that cut.

**Why orientation, never authority (the load-bearing rejection).** The natural drift is
to let a tidy typed map start answering "is this allowed?" — to cite an OKF `type` or
link as evidence. This is REJECTED and hardened into Boundary Invariant 1. gzkit's truth
already lives in canon and the ledger (Layer-1/Layer-2); a generated bundle is Layer-3
and, per `docs/governance/state-doctrine.md`, derived views are never source-of-truth.
OKF helps agents FIND and UNDERSTAND knowledge; it never PROVES claims. The
STRUCTURAL-FENCE is the only mechanical guard against this drift, so its closeout audit
must be real, not cosmetic.

**Why generated-and-additive, not authored-in-place.** Source docs stay canonical and
authored; the bundle is generated over them. This keeps authorship discipline unchanged
and makes the bundle disposable/regenerable — a stale bundle is re-generated, never
hand-patched. It also keeps the validator's blast radius small: it gates only generated
output (Boundary Invariant 2), so authoring a source doc never has to satisfy OKF.

**Why a tracer bullet, not corpus-wide tagging.** Success is ONE working
progressive-disclosure path (state doctrine, trust doctrine, agent-contract rationale,
active campaign reference), not "all docs tagged." A narrow slice proves the mechanism
end-to-end — generator, validator, CLI, and a control surface pointing into the bundle —
before any corpus-wide investment, which is the scope-minimization discipline the
campaign demands.

**Why stdlib-first holds the line on RAG.** The companion
`okf-rag-hybrid-design-note-2026-06-27.md` records the operator's OKF+RAG-hybrid
interest but keeps RAG OUT of this first pass: the doc corpus is `rg`-reachable in
milliseconds, so the stdlib-first reach tier (OKF index files + ripgrep) is tried first;
a vector/embedding runtime dependency is a foundation-ADR-gated departure, not a default.

**Why bundles are domain-named, never format-named.** The OKF spec models bundles by
their KNOWLEDGE DOMAIN — its own example root is `sales/` (`sales/index.md`,
`sales/tables/orders.md`), not an `okf/` namespace. OKF-conformance is a PROPERTY of the
markdown files (reserved `index.md`/`log.md` + a `type` field), not a folder name. A
format-named `okf/` folder would invert the model and re-import exactly the "smuggled
classification namespace" smell Movement I cut. So the governance tracer slice homes at
`.gzkit/governance/knowledge/` (domain), the implementation package is `src/gzkit/knowledge/`
(domain), and the validator recognizes bundles structurally (Boundary Invariant 2).

**Why the `.gzkit/` vs `docs/` content boundary is part of THIS decision, not a separate
ADR (operator ruling, 2026-06-28).** You cannot home a knowledge bundle correctly without
deciding which side of the boundary it belongs on, so the boundary is a first-class
concern of the OKF homing decision rather than a deferred one. The operator's framing
(verbatim): *"`.gzkit/` should be things about gzkit's core function; `docs/` is about
the adopting project"*; *"gzkit's binding canon of documentation — why it exists, what
are its bounds — should live in `.gzkit/`"*; *"much of what we place into `/docs` really
belongs in `.gzkit/`. This keeps it clean for implementing projects"*; *"This is a
delicate matter."* The delicacy is exactly why the migration is phased: this ADR
ESTABLISHES the boundary (Decision + Boundary Invariant 4) and homes the tracer bundle +
doctrine doc on the correct side, but it does NOT perform the wholesale docs/→`.gzkit/`
relocation — that is a forced subsequent decision (see Subsequent decisions forced). A
mass move inside a tracer bullet would be the precise scope-creep failure the
tracer-bullet discipline exists to prevent.

### Pre-Mortem (Gary Klein — "18 months out, this failed spectacularly. Why?")

1. **OKF became an authority layer.** An agent (or a validator author) started citing an
   OKF `type`/link as evidence, and over time the bundle accreted enforcement meaning. →
   Mitigated by Boundary Invariant 1 and OBPI-0.30.0-03's STRUCTURAL-FENCE REQ, audited
   at ADR closeout. This is the single mechanical guard, so its audit must be real.
2. **The bundle went stale.** Source docs moved on; the generated bundle drifted and
   agents trusted wrong orientation. → Generation must be cheap and idempotent (a
   `gz knowledge refresh` re-run), and a regeneration cadence is a forced subsequent decision.
3. **Scope crept to "tag everything."** The tracer slice ballooned into a corpus-wide
   tagging project that never shipped a working path. → The Persona's tracer-bullet bar
   and the Scope Minimization discipline hold the line at one path.
4. **The validator widened to gate authored docs**, turning a convenience into a second
   authoring gate that fought the existing authorship surface. → Boundary Invariant 2
   fences the scope to generated-bundle-only.

### What Would Have to Be True (Roger Martin)

For the OKF bundle to be the right call, agents must actually PREFER traversing the
bundle over blind `rg` — if they keep grepping, the bundle is dead weight. This is the
SHAKIEST condition (raised at interview); a usage proof is warranted and is a candidate
for a later validation REQ. For "make OKF an authority layer" (rejected alternative) to
have been better, gzkit's truth would have to NOT already live in canon+ledger — but it
does, so orientation-only is correct.

### Constraint Archaeology

The OKF posture (unknown fields / unknown `type` are not errors; required field is
`type` only) is an EXTERNAL convention (OKF v0.1 draft), not inherited gzkit convention —
adopting it instead of a bespoke taxonomy is a deliberate, currently-tested choice
(Movement I cut the bespoke taxonomy). The stdlib-first constraint that keeps RAG out is
real and load-bearing (the corpus is `rg`-reachable today), not assumed.

### Assumption Surfacing

The design assumes the generated bundle COMPLEMENTS the existing compact-pointer model
rather than competing with it. If the opposite were true — agents get conflicting
orientation from two navigation structures — the bundle would be a net negative. OBPI-05
must wire the bundle INTO the pointer model (a control surface points into the bundle),
not stand it up beside it.

### The 2am Operator Question

At 2am the operator needs `gz knowledge refresh` to be a single idempotent re-run that
re-generates the bundle from current sources (no hand-patching), and needs
`gz validate --okf-conformance` to name WHICH generated file and WHICH field failed —
not just "bundle invalid." Both are folded into the briefs.

### Reversibility Assessment

Two-way door. The bundle is generated and additive; deleting it removes nothing
authored. The CLI verb and validator scope are additive surfaces. Re-pointing or
removing the tracer slice is low-cost. Low reversal cost supports proceeding now.

### Scope Minimization

OBPI-01 (schema) + OBPI-02 (generator) + OBPI-05 (one documented path) are the minimal
end-to-end tracer. OBPI-03 (conformance validator + fence) and OBPI-04 (CLI surface) are
the durability and operator-ergonomics layer. OBPI-06 (content-boundary doctrine) is
authoring-only and establishes the boundary without performing any migration. If time
were halved, the schema, a generator, and one hand-run documented path ship first; the
validator, polished CLI, and doctrine doc follow. Critically, the docs/→`.gzkit/`
migration is OUT of the tracer entirely — declaring the boundary is in scope; moving the
corpus is not.

### Subsequent decisions forced

- Execute the **phased docs/→`.gzkit/` relocation** of gzkit's existing core canon
  declared by OBPI-06's doctrine doc — a delicate, multi-step migration that is its own
  future work (likely its own ADR phase), never folded into this tracer.
- Define a **regeneration cadence** for the OKF bundle so staleness does not accrete
  (the named staleness pre-mortem).
- Decide whether a **usage proof** (agents prefer the bundle over blind `rg`) is
  warranted as a later validation REQ — the shakiest WWHTBT condition.
- Gate any future **RAG/vector reach tier** behind a corpus-size trigger AND a foundation
  ADR (per `okf-rag-hybrid-design-note-2026-06-27.md`); the stdlib-first ripgrep reach
  tier is tried first.

## Consequences

### Positive

1. Agents navigate the large documentation corpus without whole-corpus reads — a typed semantic map replaces filename-search-plus-prose inference.
2. Progressive disclosure is strengthened: control surfaces (already compact pointers) can point an agent into a self-describing OKF bundle that the agent can traverse.
3. An EXTERNAL convention (OKF v0.1) is adopted instead of reviving a bespoke gzkit doc-type taxonomy — Movement I already cut the 0.0.74 doc-type taxonomy as a smuggled classification system; OKF supplies the lighter convention.
4. Source docs stay canonical and authored — the bundle is generated and additive, so authorship discipline is unchanged.
5. The no-enforcement-evidence STRUCTURAL-FENCE keeps truth in canon+ledger; OKF helps agents find and understand knowledge but never proves claims, mechanically preventing authority creep.
6. The `.gzkit/` vs `docs/` content boundary is established as doctrine (Boundary Invariant 4): gzkit-core canon homes under `.gzkit/` and `docs/` stays adopter space, which keeps the surface clean for implementing projects. Bundles are domain-named, so no format-named namespace re-imports the cut taxonomy smell.

### Negative

1. Staleness risk: a generated bundle can silently drift from its source docs, so agents trust stale orientation. Generation must be cheap and idempotent, and freshness bounded; a regeneration cadence is a forced subsequent decision.
2. Authority-creep risk (the named pre-mortem failure, fenced by the STRUCTURAL-FENCE REQ): OKF could be cited as evidence over time. The fence is the only mechanical guard, so its closeout audit must be real.
3. Scope-creep toward 'tag everything': success is NOT 'all docs tagged' — it is ONE working progressive-disclosure path. Holding to the tracer-bullet bar is a discipline risk.
4. A second navigation structure now coexists with existing control-surface pointers; if they diverge, agents get conflicting orientation. The bundle must complement, not compete with, the pointer model.
5. The 'agents prefer the bundle over ripgrep' condition is the shakiest WWHTBT — if agents keep grepping, the bundle is dead weight. A usage proof is warranted (raised at interview; candidate for a later validation REQ).
6. The content boundary is established but its consequence — relocating much of gzkit's existing `docs/` core canon into `.gzkit/` — is a large, delicate, phased migration deferred out of this ADR. Declaring a boundary the current corpus does not yet satisfy creates a known doctrine-vs-state gap until the phased relocation lands; the gap is tracked as a forced subsequent decision, not silently tolerated.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: this ADR's enforcement is not yet landed (no OKF concept-frontmatter schema, no bundle generator, no `gz validate --okf-conformance` scope, no `gz knowledge` CLI). The documentation corpus this ADR organizes validates clean today as the closest green proxy. | uv run gz validate --documents | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.30.0-okf-documentation-knowledge-structure --check | 0 |

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 1
- Dimension Total: 8
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 2
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.30.0-01: OKF schema + frontmatter model: Pydantic model for OKF concept frontmatter (required `type`, optional title/description/resource/tags/timestamp), unknown-field- and unknown-type-tolerant per OKF posture; JSON schema under src/gzkit/schemas/.
- [ ] OBPI-0.30.0-02: OKF bundle generator: produce a root index.md plus concept docs over the tracer slice (state doctrine, trust doctrine, agent-contract rationale, active campaign reference), with directory index.md progressive disclosure and markdown-link edges; source docs preserved canonical.
- [ ] OBPI-0.30.0-03: gz validate --okf-conformance scope (generated-bundle-only conformance: parseable frontmatter, non-empty `type`; reserved index.md/log.md structure; does NOT gate authored source docs) AND carry the STRUCTURAL-FENCE REQ that no gz validate / gates / closeout surface consumes OKF frontmatter or links as enforcement evidence — proven via this ADR's `## Boundary Invariants` entry, audited at ADR-closeout layer.
- [ ] OBPI-0.30.0-04: CLI surface to generate/refresh the bundle (Heavy lane: new subcommand) + manpage + cli-audit coverage + behave smoke.
- [ ] OBPI-0.30.0-05: Docs/runbook wiring: show how a control surface points an agent into the OKF bundle (the one working progressive-disclosure path that defines success); three-layer doc updates.
- [ ] OBPI-0.30.0-06: Content-boundary doctrine: author the `.gzkit/` vs `docs/` content-boundary doctrine doc (homed under `.gzkit/`; gzkit-core canon under `.gzkit/`, `docs/` = adopter space; OKF bundles domain-named) DECLARING the phased docs/→`.gzkit/` relocation as a forced subsequent decision — the migration is NOT performed here; three-layer doc pointers.

## OBPI Briefs

The Checklist above is decomposed 1:1 into OBPI briefs under `obpis/`. Every Feature
Checklist item maps to exactly one brief (1:1 Synchronization Mandate). All six are
Heavy lane (each adds or changes a schema, CLI, validator, or operator-facing doc/doctrine
contract).

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.30.0-01 | OKF concept-frontmatter Pydantic model + JSON schema under `src/gzkit/schemas/` (required `type`; optional title/description/resource/tags/timestamp); unknown-field- and unknown-type-tolerant per OKF posture. | Heavy | Pending |
| 2 | OBPI-0.30.0-02 | OKF bundle generator: root `index.md` + concept docs over the tracer slice into the DOMAIN-named `.gzkit/governance/knowledge/` root, directory `index.md` progressive disclosure, markdown-link edges; source docs preserved canonical; no `okf/` folder. | Heavy | Pending |
| 3 | OBPI-0.30.0-03 | `gz validate --okf-conformance` generated-bundle-only scope (recognizes bundles by reserved files + `type`, not folder name; does NOT gate authored source docs) + the STRUCTURAL-FENCE REQ enforcing Boundary Invariant 1 (no OKF data consumed as enforcement evidence). | Heavy | Pending |
| 4 | OBPI-0.30.0-04 | `gz knowledge` generate/refresh CLI subcommand (domain-named `src/gzkit/knowledge/` package) + manpage + `gz cli audit` coverage + behave smoke. | Heavy | Pending |
| 5 | OBPI-0.30.0-05 | Docs/runbook wiring of the one working progressive-disclosure path (a control surface points an agent into the bundle); three-layer doc updates. | Heavy | Pending |
| 6 | OBPI-0.30.0-06 | Content-boundary doctrine doc under `.gzkit/` (`.gzkit/` = gzkit-core canon; `docs/` = adopter space; OKF bundles domain-named) declaring the phased docs/→`.gzkit/` relocation; migration NOT performed here. | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.30.0-*.md`. Every row above has exactly one brief file.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-06-28T17:07:01.469826*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.30.0-okf-documentation-knowledge-structure

### Q: What is the title of this ADR?

**A:** OKF documentation-knowledge structure

### Q: What is the semantic version?

**A:** 0.30.0

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's documentation corpus (docs/governance/ doctrine, rationale, appraisal, research notes; docs/user/concepts/ explanatory docs; selected research_sources/) is large, and agents must infer its structure from filename search and prose alone — there is no typed, navigable semantic map over general app knowledge. Control surfaces are already trained to be compact pointers into deeper docs, but the pointed-to docs are not self-describing enough for an agent to traverse without reading the whole corpus. This ADR makes the CMS emit and maintain an OKF-conformant semantic map over documentation-knowledge surfaces (orientation layer only) so agents can find the relevant explanatory document via type hints, descriptions, tags, links, and indexes. OKF is NOT an authority layer in gzkit: ADRs, OBPIs, the ledger, the active campaign, and binding rules remain the truth surfaces. This is distinct from ADR-0.16.0 (CMS architecture formalization), which governs CONTROL-SURFACE rendering (the Django-parallel headless CMS turning canonical .gzkit/ content into vendor surfaces); OKF organizes DOCUMENTATION and the knowledge base to assist agents in general app knowledge. The two are orthogonal concerns with distinct consumers (operator clarification, 2026-06-28).

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Generate a small, typed OKF-conformant markdown knowledge bundle over a documentation slice, following the Open Knowledge Format v0.1 draft: a root index.md, concept documents with YAML frontmatter carrying a required `type` and optional `title`/`description`/`resource`/`tags`/`timestamp`, directory index.md files for progressive disclosure, and markdown links as graph edges. Add a validator (gz validate --okf-conformance) that checks OKF conformance ONLY for the generated bundle: every non-reserved markdown file has parseable frontmatter and a non-empty `type`; reserved index.md and log.md follow OKF structure. Source docs are preserved as the canonical authored documents — the bundle is generated over them, never replacing them. gzkit may add producer-defined frontmatter keys where useful, but consumers MUST preserve the OKF posture: unknown fields and unknown `type` values are NOT errors. The first implementation is a tracer bullet (narrow slice: state doctrine, trust doctrine, agent-contract rationale, active campaign reference) proving one working progressive-disclosure path. A STRUCTURAL-FENCE boundary invariant is added to this ADR (operator decision, 2026-06-28): OKF frontmatter and OKF links MUST NEVER be used as enforcement evidence anywhere in the gz validate / gates / closeout surfaces — the fence audits at ADR-closeout layer and keeps the entire feature from drifting into an authority layer.

### Q: What good things result from this decision? List benefits.

**A:** 1. Agents navigate the large documentation corpus without whole-corpus reads — a typed semantic map replaces filename-search-plus-prose inference.
2. Progressive disclosure is strengthened: control surfaces (already compact pointers) can point an agent into a self-describing OKF bundle that the agent can traverse.
3. An EXTERNAL convention (OKF v0.1) is adopted instead of reviving a bespoke gzkit doc-type taxonomy — Movement I already cut the 0.0.74 doc-type taxonomy as a smuggled classification system; OKF supplies the lighter convention.
4. Source docs stay canonical and authored — the bundle is generated and additive, so authorship discipline is unchanged.
5. The no-enforcement-evidence STRUCTURAL-FENCE keeps truth in canon+ledger; OKF helps agents find and understand knowledge but never proves claims, mechanically preventing authority creep.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Staleness risk: a generated bundle can silently drift from its source docs, so agents trust stale orientation. Generation must be cheap and idempotent, and freshness bounded; a regeneration cadence is a forced subsequent decision.
2. Authority-creep risk (the named pre-mortem failure, fenced by the STRUCTURAL-FENCE REQ): OKF could be cited as evidence over time. The fence is the only mechanical guard, so its closeout audit must be real.
3. Scope-creep toward 'tag everything': success is NOT 'all docs tagged' — it is ONE working progressive-disclosure path. Holding to the tracer-bullet bar is a discipline risk.
4. A second navigation structure now coexists with existing control-surface pointers; if they diverge, agents get conflicting orientation. The bundle must complement, not compete with, the pointer model.
5. The 'agents prefer the bundle over ripgrep' condition is the shakiest WWHTBT — if agents keep grepping, the bundle is dead weight. A usage proof is warranted (raised at interview; candidate for a later validation REQ).

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. OKF schema + frontmatter model: Pydantic model for OKF concept frontmatter (required `type`, optional title/description/resource/tags/timestamp), unknown-field- and unknown-type-tolerant per OKF posture; JSON schema under src/gzkit/schemas/.
2. OKF bundle generator: produce a root index.md plus concept docs over the tracer slice (state doctrine, trust doctrine, agent-contract rationale, active campaign reference), with directory index.md progressive disclosure and markdown-link edges; source docs preserved canonical.
3. gz validate --okf-conformance scope (generated-bundle-only conformance: parseable frontmatter, non-empty `type`; reserved index.md/log.md structure; does NOT gate authored source docs) AND carry the STRUCTURAL-FENCE REQ that no gz validate / gates / closeout surface consumes OKF frontmatter or links as enforcement evidence — proven via this ADR's `## Boundary Invariants` entry, audited at ADR-closeout layer.
4. CLI surface to generate/refresh the bundle (Heavy lane: new subcommand) + manpage + cli-audit coverage + behave smoke.
5. Docs/runbook wiring: show how a control surface points an agent into the OKF bundle (the one working progressive-disclosure path that defines success); three-layer doc updates.

### Q: What alternatives were considered and why were they rejected?

**A:** Inline the OKF reasoning into the campaign (REJECTED): the active Build-to-1.0 campaign is intentionally slim; inline accretion killed its predecessor. Invent a gzkit-specific documentation taxonomy (REJECTED): Movement I already cuts the 0.0.74 doc-type taxonomy as a smuggled classification system; OKF supplies the lighter external convention rather than reviving the cut. Make OKF an enforcement or truth layer (REJECTED): gzkit truth already lives in canon and ledger surfaces; OKF helps agents find and understand knowledge but does not prove claims — this rejection is hardened into the STRUCTURAL-FENCE boundary invariant. Convert control surfaces first (REJECTED): control surfaces are already compact operational pointers; the immediate gap is the semantic structure of the documentation they point into, so the first pass is documentation knowledge, not control surfaces. Route under ADR-0.16.0 as new OBPIs (REJECTED): ADR-0.16.0's declared intent is the Django-parallel control-surface CMS; it never named documentation-knowledge OKF conformance, so by the correction-vs-enhancement doctrine OKF is a new capability with its own ADR, not corrective work under 0.16.0 (operator clarification, 2026-06-28). Defer RAG / vector layer (REJECTED for this pass): stdlib-first / ripgrep reach tier comes first; a vector layer is a foundation-ADR-gated departure per okf-rag-hybrid-design-note-2026-06-27.md.


## Evidence

Four-Gate evidence (filled at OBPI closeout):

- **Gate 1 (ADR):** this document.
- **Gate 2 (TDD):** OKF concept-frontmatter model round-trip + posture-tolerance tests
  (unknown field / unknown `type` accepted) under `tests/`; generator output-shape tests;
  `gz validate --okf-conformance` clean-bundle / malformed-bundle exit tests; `gz knowledge`
  CLI surface tests.
- **Gate 3 (Docs):** new manpages for `gz knowledge` and the `--okf-conformance` validator
  scope; `docs/user/runbook.md` + `docs/governance/governance_runbook.md` (the
  progressive-disclosure path); generated OKF bundle output under `docs/`.
- **Gate 4 (BDD):** behave smoke for the `gz knowledge` generate/refresh surface (OBPI-04);
  the new validator scope is covered by direct CLI/validator unit tests at Gate 2.
- **Gate 5 (Human):** brief-level human attestation is universal (ADR-0.0.36); all five
  briefs are Heavy lane and require Gate-5 attestation at completion.

## Alternatives Considered

Inline the OKF reasoning into the campaign (REJECTED): the active Build-to-1.0 campaign is intentionally slim; inline accretion killed its predecessor. Invent a gzkit-specific documentation taxonomy (REJECTED): Movement I already cuts the 0.0.74 doc-type taxonomy as a smuggled classification system; OKF supplies the lighter external convention rather than reviving the cut. Make OKF an enforcement or truth layer (REJECTED): gzkit truth already lives in canon and ledger surfaces; OKF helps agents find and understand knowledge but does not prove claims — this rejection is hardened into the STRUCTURAL-FENCE boundary invariant. Convert control surfaces first (REJECTED): control surfaces are already compact operational pointers; the immediate gap is the semantic structure of the documentation they point into, so the first pass is documentation knowledge, not control surfaces. Route under ADR-0.16.0 as new OBPIs (REJECTED): ADR-0.16.0's declared intent is the Django-parallel control-surface CMS; it never named documentation-knowledge OKF conformance, so by the correction-vs-enhancement doctrine OKF is a new capability with its own ADR, not corrective work under 0.16.0 (operator clarification, 2026-06-28). Defer RAG / vector layer (REJECTED for this pass): stdlib-first / ripgrep reach tier comes first; a vector layer is a foundation-ADR-gated departure per okf-rag-hybrid-design-note-2026-06-27.md.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.30.0 | Pending | | | |
