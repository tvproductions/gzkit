---
id: ADR-0.0.37-constitutional-invariant-composition
status: Validated
kind: foundation
semver: 0.0.37
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-06
---

# ADR-0.0.37-constitutional-invariant-composition: Constitutional Invariant Composition

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats AGENTS.md as a Layer-3 derived view to be composed from a constitutional invariant registry, never as Layer-1 canon. Treats brief↔reality coherence as a structural invariant whose witness is mechanical (schema + validator + ledger event + gate), never narrative. Refuses to assert foundational claims in prose without a corresponding registry entry; refuses to advance a brief past Stage 2 or close it past Stage 5 without a fresh reconciliation receipt. The same skepticism the existing § Attestation receipt-ID rule applies at code-execution time, this ADR's persona applies at the canon and brief layers — every claim must be observable, dated, signed, replayable.

This is the largest single foundation ADR in the cluster (ten OBPIs) because it codifies two co-load-bearing invariants (composition + brief↔reality coherence) plus the migration that proves the framework. Decomposition discipline applies — each OBPI is a separable invariant, not a fragmentation move. The ten-OBPI count is locked from the design dialogue's MAX DO IT RIGHT pass.

## Why foundation tier?

Without this ADR, constitutional invariants don't compose mechanically — each invariant has its own validator and recovery doctrine, but invariant composition (e.g., "every artifact satisfies both T1 read-path and T2 write-path") is ad-hoc judgment.

This ADR authors a port: the constitutional-invariant composition contract every multi-invariant validator binds to (composition is structural, not narrated).

## Intent

gzkit's foundation surface is currently inverted. AGENTS.md — the prose contract every agent reads at session start — is treated as Layer 1 canon, with foundation ADRs documenting "defenses of" its claims. This makes every foundational invariant only as trustworthy as the prose it's encoded in: an editable, drift-prone, narrative surface that the project's own MAKE LLM STOCHASTIC VIBES INERT mantra explicitly identifies as the named failure class. Two pool stubs (`ADR-pool.brief-authoring-evidence-checks`, `ADR-pool.obpi-pipeline-dispatch-attestation`) recently rejected foundation-kind framing for their own work on the explicit grounds that "the invariant already exists in AGENTS.md operative-claim-4" — the inversion in plain sight, twice within a week.

The operator's loaded statement (preserved verbatim per OEE doctrine § 3): *"A statement in what is ultimately flimsy and ephemeral - AGENTS.MD - can NOT be considered foundation. Foundation adrs must place structures and processes that guarantee gzkits behavior. I have the LOWEST amount of faith in AGENTS.md."* The doctrinal correction the operator named: *"Foundation = invariant intent of the project's purpose, established with structural witness (schema + validator + ledger event), not asserted in prose. Feature = capability that users invoke (CLI flags, surfaces, mechanical defenses of a foundation invariant). Pool = backlog for feature work. AGENTS.md = composed/generated view of the foundation set, not source-of-truth."*

This ADR fixes the inversion. It establishes a constitutional-invariant registry as Layer 1 canon, renders AGENTS.md from the registry as a derived view, and codifies brief↔reality coherence as the first concrete invariant flowing through the new mechanism. The two halves are co-load-bearing: brief-reconciliation cannot be trusted without the composition framework that gives the invariant its structural witness; the composition framework cannot be tested without an instance.

The recurring failure-mode evidence motivating this ADR: OBPI-0.0.29-02's mid-Stage-4 surface where `data/behave_coverage_waivers.json` had to be edited outside the brief allowlist as coupled-surface coherence work, with the same edit having been applied silently in OBPI-0.0.29-01 (precedent without ceremony). The same shape recurs across the cluster. The pool stubs naming GHI #380 / #406 / #407 / #381 are evidence that the inversion is producing repeated drift at every authoring-time and execution-time boundary the gate covenant assumes is closed.

## Decision

Codify two co-load-bearing foundation invariants in one ADR:

**Invariant CIC-1 (composition).** Every claim that AGENTS.md asserts as foundational MUST originate from an addressable, schema-validated, ledger-witnessed entry in the constitutional invariant registry at `.gzkit/invariants/`. AGENTS.md is *rendered* from the registry; drift between rendered view and committed AGENTS.md is fail-closed at `gz validate --invariant-coherence` (and `gz check`). Hand-authoring foundational claims directly into AGENTS.md is the same class of failure as hand-writing ledger entries (AGENTS.md § Behavior Rules — Never #2 applied at the canon layer).

**Invariant CIC-2 (brief↔reality coherence).** Every OBPI brief is a structural artifact whose Allowed Paths, Discovery Checklist, Verification commands, REQ-IDs, and citation tuples MUST reconcile against current project shape before Stage 2 implementation begins. Drift is fail-closed at `gz obpi pipeline` Stage 1 (refuses Stage 2 entry without a fresh reconciliation receipt) and at `gz obpi complete` Stage 5 (refuses completion without a reconciliation receipt newer than the most recent mutation in the brief's allowlist domain).

**Rationale (numbered, binding):**

1. **Foundation requires structural witness, not prose.** A foundational claim asserted only in AGENTS.md is indistinguishable from doctrine drift at the next agent session — it can be edited, reinterpreted, partially-loaded, or outright forgotten. The mantra (MAKE LLM STOCHASTIC VIBES INERT) names this failure class explicitly; this ADR mechanizes the structural defense the mantra calls for at the canon layer itself.

2. **Two invariants in one ADR because they are co-load-bearing.** CIC-2 (brief↔reality coherence) cannot be trusted without CIC-1's witness mechanism — a brief-reconciliation invariant codified in prose without a structural-witness framework underneath it would re-instance the inversion. CIC-1 (composition) cannot be tested without an instance. Sequencing them across two ADR ceremonies doubles the gate ceremony with no separability gain.

3. **The composition framework's first composition target is AGENTS.md** because AGENTS.md is the most-read, most-edited, highest-blast-radius prose surface in the project. Other composition targets (skill READMEs, persona files, rule mirrors) are forward-references; the registry abstraction supports them but this ADR scopes the AGENTS.md instance only.

4. **The brief-reconciliation invariant covers five drift dimensions** (allowlist, Discovery Checklist, Verification verbs, REQ counts, citation tuples) because each is a separately-observed drift class with a distinct mechanical signature. The cluster's recurring evidence (OBPI-0.0.29-01 / 02 allowlist drift, GHI #380 manpage-anchor + scope-collision, GHI #406 cluster-coherence dimensions, GHI #407 evaluation-time dimensions) names all five.

5. **Reconciliation receipts must be fresher than the most recent mutation in the brief's allowlist domain** because a stale receipt that predates a coupled-surface change carries the same misinformation as no receipt. Freshness is the structural test for receipt validity (parallel to the receipt-freshness rule already governing `.plan-audit-receipt-*.json` per `.claude/rules/governance-core.md`).

6. **Fail-closed at both Stage 1 and Stage 5** because Stage 1 catches authoring drift (brief ≠ project shape at implementation start) and Stage 5 catches in-flight drift (brief shape mutated during implementation, e.g. when a sibling OBPI lands and shifts the allowlist domain). One-gate-only would leave half the failure surface open.

7. **Pool stubs for `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` remain in pool** because they're feature-shaped defenses of CIC-2 once this foundation lands. Promoting them now (as the agent's flawed pre-correction recommendation proposed) would entrench the inversion.

8. **Ten OBPIs is the right size** because each codifies one separable invariant or surface: schema + registry primitive, composition renderer, composition drift validator, brief structural schema, reconciliation engine, CLI verb, Stage 1 gate, Stage 5 gate, AGENTS.md migration, doctrine refresh. Bundling produces one Gate 5 witness for ten separable concerns; over-fragmenting produces ceremony without invariant addition.

**The invariant (canonical statement):** gzkit's foundation surface is composed from a schema-validated, ledger-witnessed constitutional invariant registry, not authored as primary canon in prose. Every OBPI brief reconciles against current project shape before implementation begins and before completion is recorded; drift between brief-declared shape and observed project shape is fail-closed at Stage 1 and Stage 5 of the OBPI pipeline.

**Mechanical surfaces (what changes in code):**

- `src/gzkit/governance/invariants.py` (new): frozen Pydantic `ConstitutionalInvariant` (id, claim, structural_witness, composition_targets fields).
- `src/gzkit/schemas/constitutional_invariant.json` (new): JSON Schema mirror; `additionalProperties: false`; structural-witness array `minItems: 1`.
- `.gzkit/invariants/*.yaml` (new directory): one YAML per invariant; CIC-1, CIC-2, plus the self-referential "every foundation ADR registers ≥1 invariant" check are the seed entries.
- `src/gzkit/governance/compose.py` (new): composition renderer; consumes registry, projects into AGENTS.md template, emits deterministic byte sequence.
- `src/gzkit/commands/governance_render.py` (new): `gz governance render --target agents-md` CLI verb.
- `src/gzkit/governance/trust_audits/` (package): add `invariant_coherence.py` (re-renders, byte-compares to committed AGENTS.md) and `brief_reconcile.py` (drift detection across the five reconciliation dimensions); register both in the package `__init__.py` validator registry. Note: `trust_audits` is a package with per-scope modules (one module per validator scope), not a monolithic file.
- `src/gzkit/schemas/obpi_brief_structure.json` (new): structural schema for OBPI briefs beyond markdown frontmatter.
- `src/gzkit/governance/brief_reconcile.py` (new): reconciliation engine; per-dimension delta computation.
- `src/gzkit/commands/brief_reconcile.py` (new): `gz brief reconcile <OBPI-ID> [--apply]` CLI verb.
- `src/gzkit/cli/parser_artifacts.py`: register the new verbs (`governance render`, `brief reconcile`).
- `src/gzkit/pipeline_runtime.py`: extend Stage 1 to require fresh reconciliation receipt before Stage 2 entry.
- `src/gzkit/commands/obpi_complete.py`: extend to require fresh reconciliation receipt before completion event emission.
- `.gzkit/schemas/ledger_events.json`: extend ledger event family with `invariant_registered`, `invariant_amended`, `composition_rendered`, `composition_drift_detected`, `brief_reconciled`, `brief_reconcile_drift_detected`.
- `tests/governance/test_invariants.py`, `tests/governance/test_compose.py`, `tests/governance/test_brief_reconcile.py`, `tests/commands/test_governance_render.py`, `tests/commands/test_brief_reconcile.py`: REQ-derived assertions across the ten OBPIs.
- `features/constitutional_invariants.feature` + `features/brief_reconcile.feature` (new): BDD scenarios tagged `@REQ-0.0.37-NN-MM`.
- `docs/user/manpages/gz-governance.md` + `docs/user/manpages/gz-brief.md` (new): manpages per gate5-runbook-code-covenant.
- `docs/user/runbook.md`: runbook entries for the new ceremony surfaces.
- `docs/governance/advisory-rules-audit.md`: scorecard entries classifying the new validator scopes.
- AGENTS.md: hand-authored content migrated to `.gzkit/invariants/` registry entries; the file becomes a rendered output.

**Ten OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.37-01 — Constitutional invariant schema + registry primitive:** Frozen Pydantic `ConstitutionalInvariant` (id, claim, structural_witness array, composition_targets array); JSON Schema mirror; first three seed invariants registered: CIC-1, CIC-2, and the self-referential "every foundation ADR registers ≥1 invariant" check.

**OBPI-0.0.37-02 — Composition renderer:** `gz governance render --target agents-md` consumes the registry and projects into AGENTS.md's existing structural shape; deterministic byte output (template-rendered, not LLM-rewritten); supports `--check` mode that exits non-zero on drift without writing.

**OBPI-0.0.37-03 — Composition drift validator:** `gz validate --invariant-coherence` re-renders the registry and byte-compares to committed AGENTS.md; fail-closes on drift; emits `composition_drift_detected` ledger event.

**OBPI-0.0.37-04 — OBPI brief structural schema:** Pydantic `BriefStructure` model; JSON Schema mirror; extends current frontmatter to include machine-readable allowlist domain definitions, REQ-IDs as structured fields, verification commands as structured array, citation tuples; backward-compat permissive mode with deprecation window.

**OBPI-0.0.37-05 — Brief reconciliation engine:** `brief_reconcile.py`: given an OBPI brief, walks the project tree, computes observed vs. declared deltas across all five reconciliation dimensions (allowlist coherence with coupled-surface registries, Discovery Checklist file existence, Verification verb resolution against parser_artifacts, REQ-count parity against acceptance criteria, citation-tuple freshness against current corpus revision).

**OBPI-0.0.37-06 — `gz brief reconcile` CLI verb:** Operator-runnable surface; emits `brief_reconciled` ledger event with delta summary; supports `--apply` to write operator-attested amendments back into the brief frontmatter.

**OBPI-0.0.37-07 — Pipeline Stage 1 fail-close gate:** Extends `gz obpi pipeline` Stage 1 to require a fresh reconciliation receipt before Stage 2 entry; receipt freshness defined as "newer than the most recent mutation timestamp in the brief's allowlist domain."

**OBPI-0.0.37-08 — `gz obpi complete` fail-close gate:** Refuses Stage 5 completion without a fresh reconciliation receipt; receipt staleness blocks the completion event from emitting. The 2am-operator escape hatch (`--accept-stale-reconciliation --reason '<text>'`) records the override to the ledger as a `brief_reconcile_drift_overridden` event.

**OBPI-0.0.37-09 — AGENTS.md migration:** The seed pass — every existing § in AGENTS.md gets analyzed, decomposed into discrete constitutional invariants, registered in `.gzkit/invariants/`. AGENTS.md is then rendered from the registry; drift validator runs in CI to lock the inversion. Operator-attested per § (foundation-kind brief-level Gate 5 across the migration).

**OBPI-0.0.37-10 — Doctrine refresh:** Update ADR-0.0.18 references to clarify the kind axis carries the structural-witness vs. prose distinction (via the `gz adr amend` flow if it exists; otherwise via amendment-pool stub). Update pool stubs `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` with re-routing notes that name CIC-2 as their foundation surface. Update contributing docs.

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-03 (composition framework lands first; ledger events online). Then OBPI-04 → OBPI-05 → OBPI-06 (brief reconciliation engine). Then OBPI-07 → OBPI-08 (gates wired). Then OBPI-09 (migration; depends on OBPI-03 to validate the result). OBPI-10 in parallel with OBPI-09.

**Lane: Heavy.** New Pydantic models + new schema mirrors + new CLI verbs (`gz governance render`, `gz brief reconcile`) + new ledger event family + new validator scopes (`--invariant-coherence`, `--brief-reconcile`) + breaking change to AGENTS.md authoring surface. All trigger heavy-lane rigor per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.18.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT specify the full constitution-amendment ceremony — the registry primitive (OBPI-01) supports `gz adr amend`-style amendments via emerging amendment pool stubs, but the formal amendment-tracking ceremony is `ADR-pool.adr-amendment-tracking`'s scope.
- Does NOT cover composition targets beyond AGENTS.md — skill READMEs, persona files, rule mirrors are forward-references; the registry abstraction supports them but each composition target is its own (likely future) feature ADR.
- Does NOT cover frontmatter↔body↔ledger metadata coherence — that is `ADR-pool.adr-layer-coherence`'s scope (parallel concern at the metadata layer; this ADR addresses the canon-prose layer).
- Does NOT promote `ADR-pool.brief-authoring-evidence-checks` or `ADR-pool.obpi-pipeline-dispatch-attestation` — those remain in pool until CIC-2 lands; they then become feature-kind ADRs that consume CIC-2.
- Does NOT modify the ledger event schema beyond the new event family added here — broader ledger schema changes are out of scope.
- Does NOT introduce a new attestation type — the existing `human` / `agent-relayed-operator-attestation` / `self-close-exception` taxonomy carries through.

## Decision Extension (2026-05-30): CIC-1 Density-Dial Composition

The original Decision scoped CIC-1's renderer as a *byte-preserving* migration of the
existing AGENTS.md prose into a flat claim registry (OBPI-02/09). Post-landing review
under the return-to-health emergency (#519) established that this under-delivers the
mechanism's purpose and strands it short of the always-intended CMS vision. This
extension re-aims CIC-1's **composition** half; the brief↔reality half (CIC-2,
OBPIs 04–08) is untouched.

**Operator vision (verbatim, preserved per OEE doctrine § 3):** *"We keep a master JSON
file that has MAX richness, MAX depth, MAX specification, and then use different
'temperatures' to dial up or down within. OR, even add/withhold sections. All of that can
be templated: lite template, medium template, heavy template. These could become truly
dynamic in the future → vendor-specific templates. We could even stop the 'dumb' mirroring
and do some agent/harness/model detection and REALLY fine tune. This was always the vision
for this system."*

**The mechanism.** The constitutional-invariant registry is reconciled into ADR-0.0.34's
`AgentContract`/`Pillar`/`Bullet` content-model substrate — one spine, not two parallel
ones. Each bullet carries its full-fidelity prose plus a `classification`
(Mechanical | Promotable | Judgment | Ambiguous), a `witness` (the gate that mechanically
enforces it), a `rationale_ref` (a pointer, never rendered inline), and a `density_min`
(the lowest temperature at which it still renders). Sections carry `order`, `enabled`, and
`tier`. The renderer takes a **temperature** (lite / medium / heavy) and a
**section-inclusion set** and projects the master model to a surface deterministically: low
temperature renders terse claims + witness pointers; high temperature renders full prose.

**The dial has an absolute floor — it does not go to 0 Kelvin.** `Judgment`-class bullets
render at *every* temperature, because they are the anti-vibe invariants no gate can
enforce and the model must hold in-context. The dial thins only Mechanical/Reference prose,
because a gate or a fetch already carries that safety property.

**Consequence for context economy.** AGENTS.md ceases to be a hand-authored monolith;
`sync_agents_md` renders it from the master model at a chosen temperature; vendor mirrors
render at per-vendor temperatures (Codex lite for the 258K-window relief named in #519,
Claude standard). `agents.local.md` and the hardcoded `get_project_context` literals
dissolve into model rows — **zero hand-authored prose at the rendered location**, which is
the binding claim of [`docs/governance/agent-control-surface-rendering-substrate.md`](../../../../governance/agent-control-surface-rendering-substrate.md),
finally load-bearing. Harness/model *detection* that auto-selects the template is a named
forward-reference, not in this extension's scope.

This extension adds six OBPIs (11–16) to the Checklist below; the Decomposition Scorecard
Final Target is updated 10 → 16 accordingly. The base ten-OBPI scoring stands for the
original decision; the six-item extension is the density-dial composition increment.

**Extension OBPIs (1:1 with the new Checklist items):**

- **OBPI-0.0.37-11 — Density-aware master content model.** Reconcile `ConstitutionalInvariant` into `AgentContract`/`Pillar`/`Bullet`; add `classification`, `witness`, `rationale_ref`, `density_min` to `Bullet`; add `order`/`enabled`/`tier` to sections. The master JSON at MAX fidelity.
- **OBPI-0.0.37-12 — Temperature renderer + lite/medium/heavy templates.** Renderer consumes temperature + section-set, renders each bullet at/above its `density_min`; `Judgment` always renders; deterministic byte-stable output; the three named templates are defined here.
- **OBPI-0.0.37-13 — Reverse-parse migration to the master model (zero hand-authored prose).** `gz content import` the live AGENTS.md/template into the model; dissolve `agents.local.md` and the `get_project_context` literals into model rows; round-trip fidelity asserted. Supersedes OBPI-09's byte-preserving framing.
- **OBPI-0.0.37-14 — Wire sync through the renderer; retire the monolith.** Repoint `sync_agents_md` off `render_template("agents")`; `gz validate --invariant-coherence` now diffs the model render against the committed surface.
- **OBPI-0.0.37-15 — Per-vendor template selection.** Codex mirror renders lite; Claude standard; ends identical 4× mirroring. Harness/model detection remains a forward-reference.
- **OBPI-0.0.37-16 — Docs-for-agents orientation index.** A routable surface → authoritative-model+doctrine map rendered from the same substrate, so the rendering architecture stops being re-derived from source each session.

## Decision Re-Alignment (2026-06-03): Corpus → Setpoint-Compression → Invariant Tier

> **Supersession scope.** This re-alignment supersedes the *mechanism* of the 2026-05-30 Density-Dial extension (the per-`Bullet` `density_min` include/exclude switch + three static lite/medium/heavy templates). It does **not** change CIC-1's invariant or CIC-2 (brief↔reality). The 2026-05-30 text is retained above as authored history; the binding composition mechanism is the one defined here. Authored under live operator design dialogue 2026-06-03 (decision record: `.gzkit/insights/agent-insights.jsonl` improvement entry `ts=2026-06-03T11:32:52Z`). ADR remains `Draft` (Attestation Block: `0.0.37 | Pending` — no ratified ADR-level decision exists). Ledger truth: OBPIs 11–15 ARE Gate-5 attested-complete (`obpi_receipt_emitted` / `obpi_completion: attested_completed`, attestor g0); 16–17 were never completed (16 created-only; 17 launched, 8 tasks blocked, never completed). What is superseded is the **density-dial mechanism** those OBPIs delivered, not a ratified ADR decision — CIC-1's invariant is unchanged. The attested 11–15 receipts remain valid; their reusable substrate (11/13/14) is re-homed into the re-aligned items 18–27.

**Why re-aim.** Empirical review proved the 2026-05-30 mechanism inert: the render template `agentcontract/claude.md.j2` emits `pillar.lines | join` verbatim and every parsed `Bullet.density_min=None`, so `render(lite) == render(medium) == render(heavy)` byte-for-byte. The corrective attempt (OBPI-17-as-scoped: thin by dropping whole sections) collides with ADR-0.0.33 `bullet-retention` (in the default `gz check` scope) and floors the committed root at ~29,885 B with no headroom; `# Local Agent Rules` is an H1 the parser glues into the Control-Surfaces pillar. Both mechanisms are the wrong shape. The operator's correction (verbatim): *"temperature levels are to condense and shorten language within sections. Dropping whole sections is not preferred"*; *"we don't write-rewrite AGENTS.md … we write to the growing corpus … like how you, as a harness, store user memories"*; *"the user might want invariants - things that are omnipresent and never condense … PRIME DIRECTIVE, DO IT RIGHT, and NEVER PYTEST"*; *"I set the thermostat and the system works to hit that target."*

**The re-aimed mechanism — four parts + one pipeline:**

1. **Append-only corpus (source of truth).** A schema-bound, append-only store of contract content (paras/bullets). Operator "remember X" moments and agent course-corrections **append** entries; nothing is hand-edited at the rendered location (the substrate doctrine's binding claim, made load-bearing). Each entry is **addressed and provenanced**: `id, surface, section, anchor?, tier (invariant|compressible), classification, witness?, text, origin, ts`. **Sections are defined by the surface's Jinja2 template, not a separate registry; the `AgentContract`/`Pillar` Pydantic models enforce conformance** — an entry's `section` MUST resolve to a real template section, invariant-tier sections MUST be present, setpoint/section coherence validates. Append fires a `corpus_entry_appended` ledger event; the committed rendition carries a provenance map (rendered section → contributing entry ids) for bidirectional audit (rendered surface → rendition → corpus entry → origin GHI/session).

2. **Temperature = compression setpoint (thermostat).** A declared parsimony target per *(surface × consumer)*, stored in the existing `data/vendor-manifest.json` `content_type_temperatures` map. The setpoint is a *target the composer drives toward*, never a stored-rendition selector. Achieved byte size is an **output** (a function of how much content is invariant-tier), reported as evidence — not a hand-tuned input.

3. **Authoring-time compression composer (LLM, advisor-QC'd, operator-attested).** At authoring time the composer scans the corpus and compresses `compressible`-tier content toward the setpoint using judgment (drop/combine/rewrite), maximizing information retained per byte reduced. Output is graded by an advisor panel (LLM-as-judge — **advisory, never gating**, per ADR-0.0.39), then **operator-attested** (universal Gate 5; no auto-accept), then committed as a durable **rendition artifact**.

4. **Deterministic playback (no LLM in the render path).** `sync_agents_md` renders the committed rendition deterministically to AGENTS.md and vendor mirrors. The non-deterministic step (compression) happens between turns at authoring time; the render path is pure playback. **This is the load-bearing anti-vibing seam** — it is the canon-layer instance of Alternative #11's rejection of LLM-as-rendering.

5. **Invariant tier (0-Kelvin floor).** `tier: invariant` entries (PRIME DIRECTIVE, DO IT RIGHT, NEVER PYTEST, …) emit **verbatim at every setpoint**, never compressed — exact operator intent, analogous to the immutable upstream system prompt the operator cannot edit. The dial thins only `compressible` content.

**The binding pipeline:** `corpus (append-only source) → compress toward setpoint (LLM + advisor-QC + operator attest) → committed rendition (durable artifact) → deterministic playback → rendered surface`.

**Recompose contract (build + on-demand + chore).** Every build (`gz agent sync` / `gz check`) runs only **deterministic playback + a freshness gate**: if the corpus changed since the committed rendition for a surface, the build **fails closed** ("corpus drifted; run `gz content compose <surface>` and attest"), the same shape as `--invariant-coherence` / `register-adrs` freshness. Recompose itself is available **both** on-demand (`gz content compose <surface>`) **and** as a scheduled **chore** that detects drift, runs the compression + advisor-QC legwork, and stages a candidate rendition for operator attestation — never auto-committing (Gate 5 stays human). Cadence is material-change-triggered (setpoint and invariant-tier changes always recompose).

**#519 re-anchors** as "declare a lean `AgentContract.codex` (and tighter root) setpoint and compress to it." Interim relief = an operator-attested hand-compressed rendition landed early as the first committed-rendition artifact; the composer regenerates it once the engine lands. Fixes the `data/instructions_files_budget.json` miscalibration.

**ADR-0.0.33 reconciliation (coupled attested amendment).** `bullet-retention` becomes **tier-scoped**: verbatim presence required at the invariant tier; compressed tiers satisfy retention via the advisor-QC info-retention receipt + operator attestation, not verbatim-bullet substrings. This is a real attested amendment to ADR-0.0.33's Invariant 1 (Validated, heavy), landed in the same commit-window as the tier-aware validator (re-decomposed OBPI below), never a silent validator edit (which would be the doctrine-drift ADR-0.0.33 itself prohibits).

**Refined canonical statement (CIC-1 composition half):** gzkit's agent control surface is composed from an append-only, schema-validated, ledger-witnessed corpus. A declared compression setpoint per *(surface × consumer)* drives an authoring-time, advisor-QC'd, operator-attested compression of compressible-tier content into a committed rendition artifact, played back to the rendered surface deterministically — no LLM in the render path. Invariant-tier content is emitted verbatim at every setpoint. Drift between deterministic playback and the committed surface is fail-closed at `gz validate --invariant-coherence`.

**Re-decomposed extension OBPIs** (items 18–27) replace the live density-dial decomposition (see the Checklist). The decomposition scorecard's mechanical target is 27 because the checklist retains minted historical identities 11–17; the active non-withdrawn target is 19 after 09 and 11–17 are withdrawn from active status. **09 is withdrawn** (operator-directed 2026-06-04, `obpi_withdrawn`): never built, its invariant-registry migration superseded by the corpus-rendition track — items 18/22/27 own AGENTS.md authoring and the `--invariant-coherence` lock moves to OBPI-22 rendition-store playback; no substrate to re-home. Disposition of prior work (ledger-grounded): **11–15 are attested-complete** (`obpi_receipt_emitted` / `attested_completed`, attestor g0 — their density-dial *mechanism* is superseded; the receipts remain valid); **11/13/14 built reusable substrate** (`AgentContract`/`Pillar` model, markdown↔model parser, sync/playback plumbing) → re-homed into 18–27; the dead surface is narrow (the inert `density_min` filter + three-static-template framing); **15's per-vendor selection retires** (per-vendor emission ruled out by the Codex-loader finding); **16 (created-only, never built) folds its orientation-index intent into item 27**; **17 (launched, 8 tasks blocked, never completed) retires**.

## Comparator Uplift (2026-05-07)

Comparator lessons must not enter gzkit as prose pasted into AGENTS.md. This ADR
is the intake gate: any borrowed doctrine that claims to shape gzkit identity
must become a constitutional invariant with schema, validator, ledger event, and
rendered projection. Workflow conveniences remain feature or pool work until
they have a foundation invariant to defend.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

> **Re-scoped 2026-07-18 (Terminal Disposition — Completed-Partial).** The prior Row 1
> asserted "re-rendering the constitutional invariant *registry* byte-matches the composed
> AGENTS.md." That claim was false against delivered code — `render_agents_md` ignores its
> registry argument and `--invariant-coherence` compares deterministic *rendition* playback
> to the committed surface, never the registry (the registry spine, OBPI-02/03, is the
> superseded half severed to GHI #623). The rows below assert only the witnesses that are
> genuinely delivered and load-bearing; each was observed exit 0 on 2026-07-18.

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Committed AGENTS.md byte-matches deterministic playback of the committed rendition; hand-edits to the rendered surface fail closed. | uv run gz validate --invariant-coherence | 0 |
| CIC-2 brief↔reality reconciliation is live and fail-closed. | uv run gz validate --brief-reconcile | 0 |
| Corpus↔rendition freshness (content-fingerprint) and rendition-byte integrity are enforced. | uv run gz validate --rendition-freshness | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.37-constitutional-invariant-composition --check | 0 |

## Consequences

### Positive

1. **AGENTS.md becomes a Layer-3 derived view (per `docs/governance/state-doctrine.md`).** Every foundational claim has a structural witness; drift between rendered and committed AGENTS.md fails CI; hand-authoring becomes mechanically blocked the way ledger-editing already is. Closes the inversion the operator named explicitly.

2. **The foundation/feature kind axis acquires a structural test.** "Is the invariant intent of the project's purpose, established with structural witness?" is now mechanical (does the invariant have a registry entry with a non-empty `structural_witness` array?), not a narrative judgment call. Future foundation ADRs gain a checklist and a fail-closed gate at promotion.

3. **The recurring brief↔reality drift class closes mechanically.** OBPI-0.0.29-02's `behave_coverage_waivers.json` shape, OBPI-0.0.29-01's silent precedent, the GHI #380/#406/#407 superseding chain, the GHI #381 dispatch-attestation gap all route through a single `gz brief reconcile` surface with operator-attested amendments. The pool stubs become feature-kind defenses *of* CIC-2 once this lands.

4. **Operator-bandwidth-protection at brief authoring and at Stage 1 entry.** Operators receive the reconciliation delta upfront with operator-attested amendment shapes, instead of discovering coupled-surface edits mid-Stage-4. The OEE doctrine's "agent drafts substantively, operator reviews" pattern applied at brief reconciliation time.

5. **The composition framework supports future composition targets** (skill READMEs, persona files, rule mirrors) without re-architecture. Each new composition target adds a `composition_targets` entry in the relevant invariant; the renderer pattern is reused.

6. **Ledger-of-truth doctrine extends to canon coherence.** The new event family (`composition_*` + `invariant_*` + `brief_reconcile_*`) makes drift events first-class ledger entries replayable across sessions. Audit trails for governance-surface mutations gain receipts at parity with code-execution receipts.

7. **Pool stubs gain a foundational anchor.** `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` can be authored as feature-kind ADRs that consume CIC-2 — their Alternative-C reasoning gets retroactively justified (foundation invariant exists with structural witness; these stubs are mechanical defenses of that foundation).

8. **The CMS-composition direction the operator named is mechanically begun.** Future foundation ADRs codify invariants in `.gzkit/invariants/` first; AGENTS.md re-renders. The inversion is fixed at the project's foundation layer.

9. **`gz check` becomes the single gate for canon coherence.** Operators have one command that fails closed on every canon-drift class (composition drift, brief↔reality drift) at the same surface as code-quality checks. No special invocation required.

10. **The two co-load-bearing invariants ship together with one Gate 5 ceremony per OBPI.** Foundation-kind brief-level attestation discipline applies; each OBPI gets independent witness; the ten-OBPI count is the right decomposition for ten separable invariants.

### Negative

1. **Largest-foundation ceremony in the cluster (~10 OBPIs).** Composition framework, registry, renderer, drift validator, brief schema, reconcile engine, CLI verb, pipeline gate, completion gate, plus a migration OBPI to seed AGENTS.md content into the registry, plus a doctrine refresh OBPI. Bandwidth cost is real; bounded by foundation-kind decomposition discipline (each OBPI is a separable invariant, not a fragmentation move).

2. **AGENTS.md migration (OBPI-09) is a one-shot risk.** Moving from hand-authored to rendered-from-registry means every existing claim must be analyzed, decomposed, and registered. Risk: claims that look foundational but have no structural witness (today's reality) need either a structural witness authored or downgraded to a non-foundation surface (skill, rule, runbook). Either path is significant work. **Pre-mortem scenario:** 18 months from now, this decision failed because the migration produced a registry of "placeholder structural witnesses" (validator scopes that don't actually validate, ledger events that don't actually emit) — i.e. theater of structure rather than structure. **Mitigation:** each migrated invariant requires at least one assertion-bearing test in `tests/governance/` to count as witnessed.

3. **Brief-structure schema extension is breaking.** Existing OBPI briefs use ad-hoc frontmatter shapes that won't validate against the new `obpi_brief_structure.json`. Either the schema is permissive at first (with a deprecation window) or every existing brief gets a migration pass. Foundation-kind decomposition lets this be one OBPI (OBPI-04 ships permissive mode; a future feature ADR tightens).

4. **Pool stubs need re-routing.** `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` need their Alternative-C reasoning updated (their pool-stage rejection of foundation-kind was based on the inverted assumption this ADR fixes). Both should remain in pool until CIC-2 lands, then promote as feature-kind ADRs *that consume CIC-2*. Risk: if those stubs are promoted before CIC-2 lands (operator forgets the dependency), the inversion re-instances. **Mitigation:** OBPI-10 (doctrine refresh) explicitly documents the dependency in the pool stubs.

5. **Citation-graph density.** Every future foundation ADR references CIC-1; every brief references CIC-2 implicitly through pipeline gates. This is the same "load-bearing foundation cited everywhere" shape as ADR-0.0.18; bounded by being foundation-kind work it has earned.

6. **Reconciliation receipt-freshness adds Stage 1 + Stage 5 latency.** Every OBPI pipeline run pays the reconciliation cost twice. Real cost in seconds; bounded by the engine's decomposition-by-dimension (only re-walk dimensions whose source surface has mutated since last receipt). Acceptable per the mantra (5:1 governance-to-output ratio is the product).

7. **The composition renderer is itself code with potential for drift between specification and behavior.** **Pre-mortem:** 18 months from now the renderer silently emits invariants in a slightly different order than the registry declares, AGENTS.md drifts byte-by-byte but not semantically, drift validator alarms continuously, operators learn to ignore it. **Mitigation:** byte-deterministic rendering is REQ-01 of OBPI-02; the test suite asserts byte-identical output for every fixture registry input.

8. **OBPI brief structural schema (OBPI-04) introduces fan-out of brief-authoring complexity.** Operators authoring new briefs must now think about the structured forms of allowlist, Discovery Checklist, Verification, REQs, citations. This adds authoring overhead. **Mitigation:** `gz obpi specify` (existing skill) is extended to scaffold the structured form; operators don't hand-author the YAML.

9. **The 2am operator scenario for this ADR's failure path:** an operator on-call at 2am needs to ship an emergency fix and `gz obpi complete` refuses because the reconciliation receipt is stale. **Mitigation:** a `--accept-stale-reconciliation --reason '<text>'` escape hatch (parallel to `--accept-uncovered` for REQ coverage gate per ADR-0.0.25) records the override to the ledger as a `brief_reconcile_drift_overridden` event for later operator review. Never silent.

10. **Reversibility assessment: this is a one-way door.** Once AGENTS.md is rendered-from-registry and CI fails on drift, hand-editing AGENTS.md becomes mechanically blocked. Reversal in 12 months would require disabling the validator and re-authoring AGENTS.md by hand — significant work. Justified by the recurring failure-mode evidence: the door we're closing is one that was producing repeated drift. The asymmetry is intentional; the cost of leaving it open exceeds the cost of closing it.

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
- Baseline Selected: 15
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 15
<!-- Baseline Selected 12→16 (2026-06-03 Re-Alignment): split flags are 0/1 booleans (Split Total max 4), so the re-decomposition's added separable units (append-only corpus store, capture tool+skill, setpoint config, compression composer, committed-rendition store + deterministic playback, invariant tier, advisor-QC loop, tier-scoped retention validator, #519 setpoint, migration) raise the baseline from 12 to 16. Baseline 16 + Split 4 = 20. (2026-06-04: 16→15 after OBPI-09 withdrawn — a never-built base migration unit, superseded by the corpus track; Baseline 15 + Split 4 = 19.) -->
<!-- 16→17 (operator-directed, 2026-06-03): OBPI-17 added after the Codex-loader finding ruled out per-vendor emission as the #519 relief and the dial was found inert (every Bullet.density_min=None → identical bytes at every temperature). The "locked 16" was a design-dialogue calibration ("calibrated over time from project evidence"); the emergency-relief increment is the evidence. OBPI-17 is the AgentContract-path density classification; distinct from OBPI-09's superseded invariant-registry migration. -->
<!-- 17→20 active / 27 mechanical (operator-directed 2026-06-03; renumbered to 18–27 on 2026-06-04): the § Decision Re-Alignment supersedes the 2026-05-30 density-dial mechanism (inert per-bullet density_min filter + three static templates) with the corpus → setpoint-compression → committed-rendition → deterministic-playback + invariant-tier model. The 10 re-aligned items are numbered 18–27 (clean of every minted ID; ledger-verified — old 11–15 are attested-complete, 16/17 created-only). The scorecard target is 27 so `gz validate --documents` and `gz specify --item 18..27` operate on the actual checklist identities; the active non-withdrawn target is 19 = 9 base (01–08, 10) + 10 re-aligned (18–27) after 09 and 11–17 are withdrawn from active status. (2026-07-18 audit reconciliation: 19→15 after the Foundation-Sunset split-and-supersede withdrew 02/03/21/22 in `d03ce98f` — active target is now 7 base (01, 04–08, 10) + 8 re-aligned (18–20, 23–27), matching `gz adr status` 15/15.) 09 withdrawn 2026-06-04 (operator-directed; never built; invariant-registry migration superseded by the corpus track — items 18/22/27 own AGENTS.md authoring; coherence lock preserved via OBPI-22 rendition playback). 11/13/14 substrate re-homed, 15 retires, 16 folds into item 27, 17 retires. Per SKILLS-FIRST, each new capability is delivered as tool(s) + the skill that wields them. -->


## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.37-01 — Constitutional invariant schema + registry primitive (frozen Pydantic ConstitutionalInvariant + JSON Schema mirror + first three seed invariants: CIC-1, CIC-2, foundation-ADR-registers-invariant)
- [ ] OBPI-0.0.37-02 — Composition renderer (`gz governance render --target agents-md`; deterministic byte output; `--check` mode) [withdrawn; repudiated 2026-06-16, permanently withdrawn `obpi_withdrawn` 2026-07-17 (`d03ce98f`); registry spine obsoleted by the 2026-06-03 corpus Re-Alignment — `render_agents_md` ignores its registry argument; severed to GHI #623, post-1.0]
- [ ] OBPI-0.0.37-03 — Composition drift validator (`gz validate --invariant-coherence`; fail-closed on drift; `composition_drift_detected` ledger event) [withdrawn; repudiated 2026-06-16, permanently withdrawn `obpi_withdrawn` 2026-07-17 (`d03ce98f`); `--invariant-coherence` ships but diffs rendition playback vs committed surface, never the registry — re-pointed by item 22; severed to GHI #623, post-1.0]
- [ ] OBPI-0.0.37-04 — OBPI brief structural schema (`BriefStructure` Pydantic + JSON Schema mirror; structured allowlist + REQs + Verification + citations; permissive mode with deprecation window)
- [ ] OBPI-0.0.37-05 — Brief reconciliation engine (project-tree walker; per-dimension delta computation across the five drift classes)
- [ ] OBPI-0.0.37-06 — `gz brief reconcile <OBPI-ID> [--apply]` CLI verb (operator-runnable; `brief_reconciled` ledger event; `--apply` writes operator-attested amendments)
- [ ] OBPI-0.0.37-07 — Pipeline Stage 1 fail-close gate (refuses Stage 2 entry without fresh reconciliation receipt)
- [ ] OBPI-0.0.37-08 — `gz obpi complete` fail-close gate (refuses Stage 5 completion without fresh reconciliation receipt; `--accept-stale-reconciliation --reason` escape hatch records override)
- [ ] OBPI-0.0.37-09 — AGENTS.md migration [withdrawn; never built; invariant-registry migration superseded (ADR line: OBPI-13 "Supersedes OBPI-09's byte-preserving framing") — corpus-rendition track (items 18/22/27) owns AGENTS.md authoring; no substrate to re-home; invariant-coherence lock preserved via OBPI-22 rendition-store playback. `obpi_withdrawn` 2026-06-04, operator-directed]
- [ ] OBPI-0.0.37-10 — Doctrine refresh (update ADR-0.0.18 kind-axis distinction; re-route pool stubs `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation`; update contributing docs)
<!-- Items 11–17: the 2026-05-30 Density-Dial extension (authored history in § Decision Extension). Mechanism superseded by the 2026-06-03 Re-Alignment (items 18–27); retained here in 1:1 with the existing brief files. Ledger-verified status (obpi_receipt_emitted): 11–15 ATTESTED-COMPLETE (mechanism superseded, substrate re-homed); 16 created-only (never built); 17 launched then retired (8 tasks blocked, no receipt). The explicit `[withdrawn; ...]` marker keeps these identity rows visible while excluding them from the live scorecard target and `gz specify` active-item count. Checkbox stays [ ] per this checklist's ADR-closeout convention — cf. the attested-complete 01–05, also [ ]. -->
- [ ] OBPI-0.0.37-11 — Density-aware master content model [withdrawn; attested-complete; AgentContract/Pillar substrate re-homed into item 18; density_min filter dead]
- [ ] OBPI-0.0.37-12 — Temperature renderer + lite/medium/heavy templates [withdrawn; attested-complete; mechanism proven inert (render(lite)==render(heavy)) — superseded]
- [ ] OBPI-0.0.37-13 — Reverse-parse migration to the master model [withdrawn; attested-complete; markdown↔model parser substrate re-homed]
- [ ] OBPI-0.0.37-14 — Wire sync through the renderer; retire the monolith [withdrawn; attested-complete; sync/playback plumbing re-homed into item 22]
- [ ] OBPI-0.0.37-15 — Per-vendor template selection [withdrawn; attested-complete; per-vendor emission later ruled out by the Codex-loader finding — selection superseded]
- [ ] OBPI-0.0.37-16 — Docs-for-agents orientation index [withdrawn; created-only, never built; intent folds into item 27]
- [ ] OBPI-0.0.37-17 — AGENTS.md density classification [withdrawn; retired; launched, 8 tasks blocked, never completed — collided with ADR-0.0.33 bullet-retention]
<!-- Items 18–27: the 2026-06-03 Re-Alignment (corpus → setpoint-compression → committed-rendition → deterministic-playback + invariant-tier). Renumbered from 11–20 on 2026-06-04, off the attested/minted 11–17 (ledger-verified: 18–27 have no identity events). Brief files authored via gz-obpi-specify. Per SKILLS-FIRST each capability ships as tool(s) + the skill that wields them. -->
- [ ] OBPI-0.0.37-18 — Append-only corpus model + addressed-entry schema (reuse AgentContract/Pillar substrate from prior 11/13; entry = id/surface/section/anchor/tier{invariant|compressible}/classification/witness/text/origin/ts; sections are TEMPLATE-defined, Pydantic enforces conformance; append-only contract)
- [ ] OBPI-0.0.37-19 — Corpus capture tool + skill (`gz content remember <surface> --section <id> [--tier]` tool appends an entry + `corpus_entry_appended` ledger event, never edits a rendered surface; wielding capture skill; replaces prior OBPI-12 renderer)
- [ ] OBPI-0.0.37-20 — Setpoint declaration + coherence validator (compression target per surface×consumer in `data/vendor-manifest.json` `content_type_temperatures`; `gz validate` scope asserts every (surface×consumer) has a declared setpoint; re-homes prior 13/15 substrate)
- [ ] OBPI-0.0.37-21 — Authoring-time compression composer tool + skill (LLM compresses compressible-tier corpus toward the setpoint — drop/combine/rewrite; emits candidate rendition + per-tier byte evidence; wielded by a compose skill; NO LLM in the render path) [withdrawn; repudiated 2026-06-16, permanently withdrawn `obpi_withdrawn` 2026-07-17 (`d03ce98f`); the composer *validates* an agent-supplied candidate rather than *materializing* from the corpus — the attributable generator is severed to GHI #623 (+#654), post-1.0. NOTE: `src/gzkit/content/composer.py` and `tier_policy.py` ship from this brief's work and are load-bearing for the delivered floor — see § Terminal Disposition]
- [ ] OBPI-0.0.37-22 — Committed-rendition store + deterministic playback + freshness gate (durable rendition artifact per surface×consumer; `sync_agents_md` plays it back deterministically; build fail-closes on corpus↔rendition drift; `--invariant-coherence` diffs playback vs committed surface; re-homes prior OBPI-14 sync/compose plumbing) [withdrawn; repudiated 2026-06-16, permanently withdrawn `obpi_withdrawn` 2026-07-17 (`d03ce98f`); the `rendition ⊆ corpus` superset gate binding candidate lineage is severed to GHI #623 (+#654), post-1.0. NOTE: `src/gzkit/content/rendition_store.py` and `governance/trust_audits/rendition_freshness.py` ship from this brief's work and ARE the delivered playback floor — see § Terminal Disposition]
- [ ] OBPI-0.0.37-23 — Invariant tier (verbatim, never condense) (`tier: invariant` entries emit verbatim at every setpoint; test asserts PRIME DIRECTIVE / DO IT RIGHT / NEVER PYTEST survive at the leanest setpoint; the 0-Kelvin floor made first-class)
- [ ] OBPI-0.0.37-24 — Advisor-panel info-retention QC loop (per ADR-0.0.39 llm-as-judge: advisory never gating, receipt-emitting; scores information-retained-per-byte of a candidate rendition; verdict cited in operator attestation; tool(s) wielded by an advisor-QC skill)
- [ ] OBPI-0.0.37-25 — ADR-0.0.33 bullet-retention tier-scoped validator (flip `--bullet-retention` from whole-surface verbatim grep to tier-aware: verbatim on invariant tier; advisor-QC receipt + attestation on compressed tiers; lands in the same commit-window as the coupled ADR-0.0.33 Invariant-1 amendment)
- [ ] OBPI-0.0.37-26 — #519 Codex-root setpoint application + interim attested relief (declare lean `AgentContract.codex`/tighter-root setpoint; land an operator-attested interim hand-compressed rendition as the first committed-rendition artifact — sequenced FIRST so the emergency is not stranded; fix `data/instructions_files_budget.json` miscalibration; composer regenerates the rendition once 21/22 land)
- [ ] OBPI-0.0.37-27 — Migration/disposition + doctrine refresh + orientation index (retire the inert density_min filter + three-static-template framing; repoint sync onto the rendition store; fold in the OBPI-16 orientation-index surface→model map; refresh the substrate doc + return-to-health plan)

## Q&A Transcript

*Interview conducted: 2026-05-06 via `uv run gz interview adr --from /tmp/adr-0.0.37-interview.json` after a multi-turn design dialogue with the operator. Full conversation history preserved in session transcript and `.gzkit/insights/agent-insights.jsonl` (2026-05-06T10:45:00 entry — kind-axis doctrinal correction). The dialogue's two operator turns that re-shaped the design:*

*1. **Operator correction to agent's flawed routing recommendation** (verbatim):* *"A statement in what is ultimately flimsy and ephemeral - AGENTS.MD - can NOT be considered foundation. Foundation adrs must place structures and processes that guarantee gzkits behavior. I have the LOWEST amount of faith in AGENTS.md. ... If I go with A, and accepting our distinction of what constitutes a feature ('Foundation kind is reserved for app/system invariants per ADR-0.0.18; these are mechanical defenses of an invariant ... not the invariant itself'), we can't trust AGENTS.MD until a structured set of structured foundational/constitutional invariants are established that AGENTS is composed from. Leading elements of our CMS approach are in place, but not fully to my original intent. Pool is for feature, foundational is for invariant intent of the project's purpose. unfortunately, the emergent nature of this project is revealing and shaping the project as we go."*

*2. **Operator scope decision** (verbatim):* *"Wide == DO IT RIGHT"* — locking the two-invariant scope (CIC-1 composition + CIC-2 brief↔reality coherence in one ADR) over the alternatives of narrow scope or two sequenced ADRs.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/governance/test_invariants.py`, `tests/governance/test_compose.py`, `tests/governance/test_brief_reconcile.py`, `tests/commands/test_governance_render.py`, `tests/commands/test_brief_reconcile.py`, `features/constitutional_invariants.feature`, `features/brief_reconcile.feature`
- [ ] Docs: `docs/user/manpages/gz-governance.md`, `docs/user/manpages/gz-brief.md`, `docs/user/runbook.md` (new entries), `docs/governance/advisory-rules-audit.md` (new scorecard entries), `.gzkit/invariants/*.yaml` (registry seed)

## Alternatives Considered

1. **Promote ADR-pool.brief-authoring-evidence-checks as feature-kind (the agent's flawed pre-correction recommendation).** REJECTED at operator-cited reasoning: the pool stub's Alternative-C self-rejection ("foundation kind is reserved for app/system invariants per ADR-0.0.18; these are mechanical defenses of an invariant, not the invariant itself") was structurally flawed because it rested on AGENTS.md § operative-claim-4 being a trustworthy invariant. Operator's verbatim correction: *"A statement in what is ultimately flimsy and ephemeral - AGENTS.MD - can NOT be considered foundation. Foundation adrs must place structures and processes that guarantee gzkits behavior."* Promoting as feature-kind would entrench the inversion.

2. **Author CIC-1 (composition) and CIC-2 (brief↔reality) as separate sequenced foundation ADRs.** REJECTED — they're co-load-bearing: CIC-2 cannot be trusted without CIC-1's witness mechanism, and CIC-1 cannot be tested without an instance. Sequencing them across two ADR ceremonies doubles the gate ceremony with no separability gain. Foundation-kind decomposition discipline applies within one ADR via OBPI splitting.

3. **Narrow scope to brief-reconciliation only; defer composition framework to later.** REJECTED at operator's *"Wide == DO IT RIGHT"* direction — narrow scope would re-instance the inversion (brief-reconciliation invariant codified in prose without the structural-witness framework underneath it). The composition framework is the structural witness CIC-2 requires.

4. **Continue with pool stubs' "defense of existing invariant" framing.** REJECTED — the existing invariant (AGENTS.md § operative-claim-4) is itself prose without structural witness; defenses of an unwitnessed invariant inherit the unwitness. The cluster's recurring drift evidence shows the framing has produced the very failure class it claimed to defend.

5. **Hand-roll a structural witness for AGENTS.md without a registry abstraction.** REJECTED — AGENTS.md is one composition target; future composition targets (skill READMEs, persona files, rule mirrors) will follow. Registry abstraction is YAGNI-rejected only if we believe AGENTS.md is the only surface; observable evidence says otherwise (multiple vendor mirrors, multiple skill renderings, multiple persona files all asserting partial overlapping foundational content).

6. **Treat composition framework as a chore, not an ADR.** REJECTED — chores are scheduled-maintenance work against existing invariants. Establishing a new invariant (CIC-1) requires foundation-kind ceremony per ADR-0.0.18; chore-tier work cannot establish foundational invariants.

7. **Implement brief reconciliation as a `gz` validator scope only (no CLI verb, no pipeline gate).** REJECTED — a validator without operator-runnable invocation is the same failure shape as an advisor that requires manual invocation (per ADR-0.0.29 § Decision rationale #3). The CLI verb (OBPI-06) is the operator-bandwidth-protection move; the pipeline gates (OBPI-07/08) are the load-bearing mechanical defense.

8. **Allow `--accept-stale-reconciliation` only on lite-lane briefs; heavy lane is fail-closed-without-escape.** REJECTED — the 2am operator scenario applies regardless of lane. Heavy-lane bias is appropriate at attestation rigor (already enforced via foundation/heavy/security axes), not at the operational-recovery escape hatch. The escape hatch records override to ledger; the audit trail is the structural defense, not lane-based access control.

9. **AGENTS.md migration (OBPI-09) deferred to a separate ADR; this ADR ships only the framework + brief reconciliation.** REJECTED — the migration is the test of the framework. Without a real composition target seeded into the registry and rendered to AGENTS.md, CIC-1 ships as theater (registry exists but no composition runs through it). The migration validates that the framework actually works at production scale.

10. **Constitutional invariant registry as a single JSON file rather than per-invariant YAML files.** REJECTED — per-invariant files give git history its natural granularity (one commit per invariant amendment, not one commit that touches every invariant). YAML preferred over JSON for human-authored governance content; existing precedent in `.gzkit/personas/` and `.gzkit/skills/`.

11. **Composition rendering driven by an LLM rather than deterministic templating.** REJECTED — non-determinism at the canon layer is the failure mode this ADR exists to close. Byte-deterministic rendering is the structural witness; LLM rendering would introduce vibing-as-rendering, the canon-layer instance of the cluster's mantra-named failure class.

12. **Reconciliation receipt-freshness defined by wall-clock TTL (e.g. 1 hour) rather than mutation-timestamp comparison.** REJECTED — wall-clock TTL produces false-positive staleness on briefs whose allowlist domain has not mutated, and false-negative freshness on briefs whose allowlist domain mutated 30 seconds after a receipt was emitted. Mutation-timestamp comparison is the semantically-correct freshness test; TTL is the easier-but-wrong proxy.

### Rejected alternatives for the 2026-06-03 Decision Re-Alignment

13. **Keep the built per-bullet `density_min` include/exclude dial (2026-05-30 mechanism).** REJECTED — empirically inert: the render template emits `pillar.lines | join` verbatim and every parsed `Bullet.density_min=None`, so `render(lite)==render(medium)==render(heavy)` byte-for-byte. An include/exclude switch cannot *condense language within a section* — the operator's stated requirement.

14. **Three static authored lite/medium/heavy templates.** REJECTED — recreates the operator-named anti-pattern ("we don't write-rewrite AGENTS.md"); hand-authored renditions drift and triple the hand-authoring surface the substrate doctrine forbids. Replaced by one append-only corpus + setpoint-driven compose.

15. **Section-drop to hit the Codex cap (OBPI-17-as-scoped).** REJECTED — collides with ADR-0.0.33 bullet-retention (in the default `gz check` scope), floors the committed root at ~29,885 B with no headroom, and the `# Local Agent Rules` H1 is glued into the Control-Surfaces pillar so dropping it loses Mechanical bullets. The operator explicitly deprioritized whole-section drops ("each section serves a vital function").

16. **Runtime LLM compression in the render path.** REJECTED — non-determinism at the canon layer is the exact failure Alternative #11 already rejected. The committed-rendition artifact (OBPI-15) is the determinism seam: compression is authoring-time; the render path is pure deterministic playback.

17. **Author a NEW superseding foundation ADR for the re-alignment.** REJECTED — ADR-0.0.37 is `Draft` (Attestation Block: `0.0.37 | Pending`), so there is no ratified ADR-level decision to supersede, and CIC-1's invariant is unchanged (only its composition *mechanism* is refined). OBPIs 11–15 ARE individually attested-complete in the ledger — but a completed OBPI's receipt is not an ADR-level ratification; those receipts stay valid, their *mechanism* is superseded and their substrate re-homed, which an in-place re-aligned decomposition (items 18–27) handles without a new ADR. A new ADR is ceremony with no separability gain (original Rationale #2), and the recovery posture forbids new foundation ADRs during recovery.

18. **Silently flip the Era-1 bullet-retention validator to tolerate compression.** REJECTED — editing a Validated invariant's enforcement without an attested amendment is the doctrine-drift failure ADR-0.0.33 exists to prevent. The tier-scoping is a real attested ADR-0.0.33 Invariant-1 amendment coupled to OBPI-0.0.37-18, never a silent validator edit.

## Boundary Invariants

Cross-OBPI / scope-boundary state properties audited at ADR closeout (ADR-0.0.59
STRUCTURAL-FENCE proof anchor):

- **BI-1 (OBPI-10 doctrine-refresh scope fence — REQ-0.0.37-10-05):** The doctrine-refresh
  OBPI modified only documentation surfaces — no `src/` files, and AGENTS.md content
  untouched. Verified by `git diff --name-only` at completion; OBPI-10's ledger footprint
  carries only documentation `artifact_edited` events.

## Terminal Disposition (2026-07-18): Split-and-Supersede

Operator ruling (2026-07-17/18): *"split-and-supersede to conclude 0.0.37"* … *"post 1.0."*
Ratified after two independent macro assessments (a fresh-context Claude analyst and a
cross-vendor Codex analyst) converged, and four independent verifiers re-derived the
2026-06-16 repudiation findings against current code and found them **still standing**.

This ADR concludes as **Completed — Partial (superseded)**, not thesis-fulfilled. The
foundation *invariant* — "AGENTS.md must be a derived view, not primary canon" — is kept and
load-bearing. The full composition *engine* that would materialize AGENTS.md from canon was
never built; it is feature-shaped (ADR-0.0.18: a mechanical defense of an invariant is a
feature, not the invariant) and is **severed to a post-1.0 successor feature** tracked at
GHI #623 (absorbing GHI #654). The Build-to-1.0 campaign already ratified this engine as
severable enrichment behind a shipped floor — the airlock ships and gates on the floor.

> **Tracker reconciliation (2026-07-19, pointer-only — the ruling above is unchanged).**
> GHI #623 is **closed**; the surviving tracker for the severed engine is **GHI #654**.
> The absorption direction recorded above is backwards relative to what survived: #623
> was the audit finding and its findings are discharged (claims 3/4 fixed by later work;
> corrective scope A landed as `--rendition-floor-coherence`; the discarded registry
> parameters removed at `4f9c7d2b`; a witness-resolution gate added at `e409bb08`).
> #654 states the same unbuilt capability from the operator side, with a reproduction —
> *"there is no generator that renders the corpus delta into a candidate."* Recorded here
> because this section is the canon a future reader consults, and it would otherwise
> point them at a closed issue for work that is still open.

**Delivered and load-bearing (the honest floor 1.0 ships on):**

- **CIC-2 brief↔reality coherence** — `gz validate --brief-reconcile`, the Stage-1 and
  Stage-5 fail-close gates, and `gz brief reconcile` ship and function (OBPIs 04–08).
- **Corpus rendition floor** — append-only corpus (18), capture tool + skill (19),
  setpoint-coherence (20), invariant-tier verbatim floor (23), advisor-QC receipt (24),
  tier-scoped bullet-retention (25), Codex-root setpoint relief (26), disposition/doctrine
  refresh (27). Deterministic playback, corpus-fingerprint freshness
  (`--rendition-freshness`), rendition-byte integrity (GHI #694), and the `invariant ⊆
  rendition` floor gate (GHI #623) are real and tamper-tested. Hand-authoring foundational
  prose is fenced; invariant-tier doctrine (PRIME DIRECTIVE, DO IT RIGHT, NEVER PYTEST) is
  verbatim-protected.

  **Attribution (2026-07-18 audit reconciliation).** The playback half of this floor was
  *built under the withdrawn briefs 21/22*, not by 18–20/23–27. `rendition_store.py`,
  `rendition_freshness.py`, `composer.py`, and `tier_policy.py` originate in that work and
  remain load-bearing and gated. Withdrawal severed the **unbuilt** half — the attributable
  corpus→candidate generator and the `rendition ⊆ corpus` lineage gate — not the shipped
  code. Recording this explicitly because an ADR whose thesis is *"canon must not diverge
  from delivered reality"* cannot itself credit shipped deliverables to briefs that did not
  produce them. Re-completion of 21/22 stays refused (the severed half genuinely does not
  exist); the surviving code's provenance is now stated rather than silently reassigned.

**Not delivered — severed to GHI #623 (absorbing #654), post-1.0:**

- **Registry→AGENTS.md renderer (OBPI-02) + drift validator (OBPI-03)** — the registry spine,
  obsoleted by the 2026-06-03 corpus Re-Alignment. `render_agents_md` ignores its registry
  argument; `--invariant-coherence` does not consult the registry. **Permanently withdrawn**
  (`obpi_withdrawn`, 2026-07-17).
- **Full corpus-derivation composition (OBPI-21/22)** — the composer *validates* an
  agent-supplied candidate rather than *materializing* from the corpus, and no `rendition ⊆
  corpus` superset gate binds the candidate's lineage, so prose absent from the corpus can
  pass. **Withdrawn** here; the attributable corpus→candidate generator + invented-prose
  rejection + guarded atomic multi-consumer landing are the successor feature's scope
  (GHI #623 + #654), executed post-1.0.

**Re-completion is refused.** The four OBPIs were repudiated on 2026-06-16 as a
fraud/nonexistence finding; the code still shows the engine does not exist, so re-attesting
any of them as Completed would repeat that fabrication. The framing that ends the multi-session
loop: *historical work, present semantic validity, and future capability ownership are three
separate axes.* Withdrawing the four engine OBPIs erases no decision — it records honestly that
the engine is unbuilt and re-homes it as a post-1.0 feature. The invariant is kept; the engine
is severed.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.37 | Completed - Partial: Completed - Partial: attest completed (g0) — split-and-supersede ruling: delivered floor (CIC-2 brief-coherence + corpus rendition floor: playback/freshness/integrity/invariant-floor) gated and green (7153 unittests arb-step-unittest-cafb4c5556b14d588644246fe06528e2, fidelity 4/4, ruff/typecheck/mkdocs clean); composition engine (OBPI-02/03 registry spine superseded; OBPI-21/22 corpus-derivation) severed to GHI #623 (+#654) as post-1.0 successor feature. | g0 | 2026-07-18 | Completed - Partial: attest completed (g0) — split-and-supersede ruling: delivered floor (CIC-2 brief-coherence + corpus rendition floor: playback/freshness/integrity/invariant-floor) gated and green (7153 unittests arb-step-unittest-cafb4c5556b14d588644246fe06528e2, fidelity 4/4, ruff/typecheck/mkdocs clean); composition engine (OBPI-02/03 registry spine superseded; OBPI-21/22 corpus-derivation) severed to GHI #623 (+#654) as post-1.0 successor feature. |
