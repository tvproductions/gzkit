---
id: ADR-0.0.55-package-import-direction-invariant
status: Draft
kind: foundation
semver: 0.0.55
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-19
---

# ADR-0.0.55-package-import-direction-invariant: Package Import Direction Invariant

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats the gzkit package's `src/gzkit/` import graph as architecture, not as a residue of authorship convenience. Refuses to enforce a layer doctrine that fires red against current code without a deliberate grandfather window; refuses to ship doctrine debt where doctrine is supposed to be the witness. Composes — does not replace — the two existing architectural ADRs (0.0.3 hexagonal, 0.0.43 DDD cascade) and codifies the missing structural rung between them: the canonical *order* of `src/gzkit/` subpackages and the mechanical fail-closed validator that binds it.

## Why foundation tier?

**Invariance test:** Without this ADR, gzkit's architecture remains a verbal commitment (ADR-0.0.3 hexagonal at the conceptual ring; ADR-0.0.43 DDD cascade within domains) with no mechanical defense against import-direction drift across the flat `src/gzkit/` package. The empirical audit at authoring time found 12+ back-edges from `governance` into surfaces it conceptually sits above (cli, commands, arb, hooks, skills, templates, chores, doc_coverage, insights, personas, rules, schemas), a bidirectional `cli ↔ commands` flow (9 + 6 edges), and multiple back-edges from leaf-analysis surfaces (`doc_coverage → commands`, `chores → commands`, `arb → commands`, `hooks → cli`, `justify → cli`). The project still ships, but the *"architecture as constraint"* property — *"agents are most effective in environments with strict boundaries and predictable structure"* (OpenAI Harness Engineering, 2026-02-11) — silently degrades each time a new validator pulls a CLI helper "just this once." **Yes — the project would still be the project, but it would lose the property that the layer doctrine is mechanically witnessed.** This ADR names the canonical layer order as invariant and ships the validator that binds it.

**Port-vs-adapter framing:** This ADR authors a **port**. It declares the canonical layer order for `src/gzkit/` subpackages (the *contract* every import must honor) and the `gz validate --import-direction` validator that enforces it. The specific allow/deny semantics for any single subpackage are derived from the port; the validator's logic, the baseline-allowlist mechanism, and the phased-rollout policy are adapters behind the port. ADR-0.0.3 (hexagonal tune-up) and ADR-0.0.43 (DDD domain cascade) supply the conceptual scaffolding the port composes; this ADR is the structural rung between them.

## Intent

The OpenAI Harness Engineering thesis (2026-02-11) names the lever directly: *"Agents are most effective in environments with strict boundaries and predictable structure, so we built the application around a rigid architectural model. Each business domain is divided into a fixed set of layers, with strictly validated dependency directions and a limited set of permissible edges. These constraints are enforced mechanically via custom linters and structural tests. This is the kind of architecture you usually postpone until you have hundreds of engineers. With coding agents, it's an early prerequisite: the constraints are what allow speed without decay or architectural drift."*

gzkit has already authored the *intent* of layered architecture twice:

- **ADR-0.0.3-hexagonal-architecture-tune-up** declares the hexagonal ring: `core` is dependency-free; `ports` exposes abstract interfaces; `adapters` implements ports against external systems; the rest of the package depends inward, not outward. The package has the three subdirectories (`core/`, `ports/`, `adapters/`) — the doctrine is partially realized.
- **ADR-0.0.43-ddd-domain-cascade** declares the DDD cascade within a domain: the domain's layers (typically Types → Config → Repo → Service → Runtime → UI in the canonical DDD shape, mapped to gzkit's per-domain vocabulary) cascade in a single direction.

Neither ADR binds **the order of `src/gzkit/` subpackages as a whole.** The package is structurally flat (40+ siblings at the top level); the layer order between them is implicit, encoded only in author convention. The empirical audit found this implicit-order regime produces real drift: `governance` imports back into `cli`, `commands`, `arb`, `hooks`, and ten other surfaces; `cli` and `commands` are bidirectionally coupled; multiple "leaf analysis" surfaces (`doc_coverage`, `chores`, `arb`) import upward into `commands`. None of these is a bug today — each was written by a careful author — but they accumulate. The Anti-vibing mantra's *"every option is framed by smallest-vibing-surface"* lens reads this state cleanly: an unbound import direction is a vibing surface, because the next change has no mechanical hand on the wheel.

This ADR composes the two existing architectural ADRs into a third, mechanically-enforced layer:

- **Package level (extending ADR-0.0.3):** A canonical order for the subpackages of `src/gzkit/`. Imports flow upward only (a subpackage at layer *i* may import from any subpackage at layer *j ≤ i*; the reverse direction is denied). The order is declared once, in a single canonical manifest (`data/package_layer_order.json`), and consumed by the validator.
- **Domain level (anchoring ADR-0.0.43):** Within any subpackage that becomes an explicit domain with internal layers (today: none; future-proofed for the OBPI pipeline runtime, the ARB receipt subsystem, and the governance audit chain as they grow internal structure), the DDD cascade from ADR-0.0.43 governs the per-domain order; the validator extends to per-domain when a subpackage adds a `_layer_order.json` manifest.

The two-tier design is the operator's "1+2" composition: hexagonal at the package level (the existing `core / ports / adapters` ring), DDD cascade per-domain (the existing ADR-0.0.43 doctrine extended where domains gain internal structure), with this ADR as the structural binding between them.

**Empirical reality at authoring time (pre-ADR audit):** the import graph carries 12+ back-edges that the canonical order would deny. Shipping a fail-closed validator on day one would fire red across the codebase — **doctrine debt, not doctrine** (the explicit advisor framing the operator received before this ADR was authored). The decision: phased rollout. The validator ships in **warn-only mode** at OBPI-02; a baseline allowlist (`data/package_import_direction_baseline.json`) enumerates every existing back-edge as exempt; subsequent OBPIs migrate the highest-volume back-edges off the allowlist; the validator promotes to **fail-closed** at the final OBPI when the allowlist is empty. This is the same bootstrap-vs-drift discipline `gz validate --reconcile-freshness` uses; the same monotonic-shrinkage discipline ADR-0.0.53's baseline uses.

## Decision

Author the canonical `src/gzkit/` subpackage layer order, declare it as invariant, ship `gz validate --import-direction` with a phased rollout from warn-only to fail-closed, and compose the result with the existing ADR-0.0.3 hexagonal ring and ADR-0.0.43 DDD cascade. Decomposed into four OBPIs.

**The invariant (canonical statement):** Every import in `src/gzkit/` whose source and destination are both subpackages of `gzkit.*` MUST be classified by one of three roles declared in `data/package_layer_order.json` — **Vertical Layer**, **Provider**, or **Utility** — and respect the role's import-direction predicate. The canonical structure (low → high vertical layers; cross-cutting Providers; depend-on-nothing Utilities):

**Vertical cascade (8 layers):**

| Layer | Members | Role |
|---|---|---|
| L0 — Data | `schemas`, `templates` | static data / template content (no Python logic dependencies on other gzkit subpackages) |
| L1 — Models | `models`, `core` | typed primitives + core exceptions / lifecycle (imports L0, Providers, Utility) |
| L2 — Adapters | `adapters` | port implementations against external systems (imports L0–L1, Providers, Utility) |
| L3 — Canon surfaces | `rules`, `personas`, `skills`, `chores`, `content` | canonical authored content surfaces (imports L0–L2, Providers, Utility) |
| L4 — Analysis libraries | `complexity`, `scan`, `eval`, `justify`, `reporter`, `flags`, `insights`, `doc_coverage`, `validate_pkg`, `validators` | analytical / validation libraries (imports L0–L3, Providers, Utility) |
| L5 — Governance | `governance` | audit / status / reconciliation surfaces (imports L0–L4, Providers, Utility) |
| L6 — Commands | `commands` | orchestration / business-logic (imports L0–L5, Providers, Utility) |
| L7 — CLI | `cli` | parser / entrypoint (imports L0–L6, Providers, Utility) |

**Providers (cross-cutting; importable by any vertical layer at or above the Provider's own floor; depend only on lower vertical layers + Utility; mirror OpenAI Harness Engineering's *"cross-cutting concerns enter through a single explicit interface: Providers; anything else is disallowed and enforced mechanically"*):**

| Provider | Floor | Role | Empirical justification (pre-ADR audit) |
|---|---|---|---|
| `ports` | L1 | abstract interfaces — the hexagonal-port surface from ADR-0.0.3 | Any layer that consumes an abstract contract pulls `ports` directly rather than re-deriving it; ADR-0.0.3 already declares this shape conceptually |
| `arb` | L2 | attestation receipt channel — telemetry analogue (every fail-closed gate produces a receipt; every validator-scope failure emits one) | `governance/trust_audits/attestation_receipts.py` already imports `gzkit.arb` despite governance being at L5; the import is structurally legitimate cross-cutting, not a back-edge |
| `hooks` | L2 | event-time interceptors — feature-flag / connector analogue (SessionStart, PreToolUse, PreCommit; consumed wherever a runtime moment needs interception) | `governance/trust_audits/kind_invariance.py` already imports `gzkit.hooks` from L5; multiple top-level modules (`sync_surfaces.py`, `adr_eval_scoring.py`, `pipeline_markers.py`) also pull `hooks` directly; the import is structurally legitimate cross-cutting |

**Utility (outside the cascade entirely; depend on nothing in `gzkit.*` beyond stdlib + named departures; importable from anywhere without manifest declaration):**

| Module | Role | Constraint |
|---|---|---|
| `gzkit.utils` (the `utils.py` top-level module) | shared depend-on-nothing helpers (date formatting, string ops, path normalization) | MUST NOT import any `gzkit.*` submodule. Stdlib + named-departure (Pydantic per ADR-0.0.0-models) imports only. Enforced mechanically by the same validator's Utility-floor check |

**Predicates the validator enforces:**

- **Vertical-to-vertical:** `layer(src) > layer(dst)` allowed; `==` allowed (sibling-within-layer); `<` denied (upward — must be baseline-allowlisted or relocated/inverted)
- **Vertical-to-Provider:** allowed iff `layer(src) ≥ Provider.floor`; below-floor calls denied
- **Provider-to-vertical:** allowed iff `layer(dst) < Provider.floor`; at-or-above-floor calls denied (Providers must not depend on layers above their declared floor — that's the cross-cutting discipline)
- **Provider-to-Provider:** denied unless explicitly declared in the manifest's `provider_edges` allowlist (Providers should not chain; if `arb` needs `hooks`, that's a manifest declaration with rationale, not silent coupling)
- **Anything-to-Utility:** always allowed
- **Utility-to-anything-in-`gzkit.*`:** always denied (Utility is depend-on-nothing)

**Decision items (1:1 with Checklist below):**

1. **Author the canonical layer-order + Providers + Utility manifest, plus the helper port.** Add `data/package_layer_order.json` declaring the structure above as the single source of truth — three top-level keys: `vertical_layers` (the 8-layer cascade with `members` per layer), `providers` (Provider name → `floor`, `role`, `empirical_justification`), `utility` (depend-on-nothing module list), and `provider_edges` (the explicit Provider-to-Provider allowlist, empty at OBPI-01 landing). Add `src/gzkit/governance/import_direction.py` (governance-layer module: imports lower vertical layers, Providers, and Utility only) providing `compute_import_edges(root: Path) -> dict[tuple[str, str], list[ImportSite]]` (returns edges with source-line provenance for each violation), `classify(subpackage: str) -> Literal["vertical", "provider", "utility", "unknown"]`, `layer_of(subpackage: str) -> int | None` (returns layer for vertical, floor for provider, None for utility), `violates_predicate(src: str, dst: str) -> bool` (the unified predicate covering all five rules: vertical-to-vertical, vertical-to-Provider, Provider-to-vertical, Provider-to-Provider, anything-to-Utility, Utility-to-anything). Add Pydantic model `PackageImportManifest` validating the manifest's shape (vertical-layer indices contiguous; no subpackage appearing in multiple roles; every `src/gzkit/` subdirectory and top-level utility-tier module accounted for or explicitly marked `excluded`; Provider floors reference valid vertical layers; `provider_edges` only references declared Providers). Author `.gzkit/rules/package-import-direction.md` (rule version `0.1.0`, paths `src/gzkit/**/*.py`) declaring the invariant and citing this ADR plus the OpenAI Harness Engineering Figure 4 (Layered domain architecture with explicit cross-cutting boundaries) as visual exemplar. Add scorecard entry to `docs/governance/advisory-rules-audit.md` classifying the rule **Mechanical**. Author `data/package_import_direction_baseline.json` capturing every predicate-violation present at OBPI-01 landing as exempt, with each entry tagged `phase: bootstrap` and a target-OBPI hint for cleanup. **Critical OBPI-01 step:** re-run the empirical import-graph audit *under the new tri-role classifier* — many edges previously flagged as back-edges (notably `governance → arb`, `governance → hooks`, top-level-modules → `hooks`) are reclassified as legitimate vertical-to-Provider imports and disappear from the baseline allowlist entirely; the baseline only carries genuine vertical-to-vertical violations and any Provider-to-Provider or above-floor Provider-to-vertical leaks.

2. **Ship `gz validate --import-direction` in warn-only mode.** New validator scope under `src/gzkit/governance/trust_audits/import_direction.py` consuming the helper from OBPI-01. Exit code `0` regardless of violations during warn-only phase (warnings print to stderr in the `RemediationPayload` shape from ADR-0.0.53 once that lands; if ADR-0.0.53 has not yet attested, the warnings use a forward-compatible shape that becomes payload-conformant under ADR-0.0.53's migration). Add `--import-direction` to the `gz check` default pipeline as a warning-only step. Add tests asserting (a) warn-only mode never raises non-zero; (b) the baseline allowlist suppresses warnings for exempted edges; (c) every new back-edge introduced after this OBPI lands surfaces as a warning. Update `docs/user/manpages/validate.md` § Scopes naming the new scope and its phase.

3. **Migrate the genuine vertical-to-vertical back-edges off the baseline allowlist.** Under the tri-role classifier from OBPI-01, the original 12+ back-edge list shrinks substantially — `governance → arb`, `governance → hooks`, and top-level-modules → `hooks` reclassify as legitimate vertical-to-Provider imports. The remaining genuine vertical-to-vertical back-edges requiring cleanup: (a) `cli ↔ commands` bidirectional (9 + 6 edges) — extract the shared utilities into `commands/` and have `cli` import them in the canonical direction; (b) `governance → cli` and `governance → commands` (3 edges) — relocate the back-imports either by moving the consumed symbols into lower vertical layers, by inverting through a `ports` Provider, or by promoting the consumed concern to a new Provider declaration with rationale; (c) `doc_coverage → commands` (4 edges), `chores → commands` (1), `justify → cli` (1) — same relocate-or-invert treatment; (d) `arb → commands` (1) — this is a Provider-to-above-floor leak (Provider importing a layer above its declared floor of L2) and MUST be cleaned, not exempted, because it breaks the Provider's depend-only-on-lower-layers discipline. Each migrated edge is removed from `package_import_direction_baseline.json` with a commit trailer naming the migration receipt. Tests: re-run the empirical audit script (which becomes a permanent fixture under `tests/governance/test_package_layer_order.py`) and assert the violation inventory has shrunk by the target count. Quality bar: zero new violations may be introduced during this OBPI; the validator surfaces them as warnings the OBPI completion gate rejects.

4. **Promote `gz validate --import-direction` to fail-closed.** The baseline allowlist's `phase: bootstrap` entries MUST all be migrated by OBPI-03; any remaining entries either get explicit `phase: permanent-exemption` reclassification with an attached foundation ADR justifying why the exemption is structural (not transitional), or get cleaned up here. Flip the validator's exit-code policy: violations exit non-zero. Add `--import-direction` to the `gz check` default pipeline as a fail-closed step. Update `.gzkit/rules/package-import-direction.md` rule version `0.1.0 → 1.0.0` reflecting promotion. Update `docs/governance/governance_runbook.md` § Layer doctrine naming the canonical order and the recovery procedure when a new feature requires a cross-layer import (extract through a port; relocate; or — last resort — author a foundation ADR justifying a permanent exemption). Update `docs/user/runbook.md` § Common errors with the new validator's failure surface.

**Sequencing:** OBPI-01 is the precondition for all others (manifest + helper + rule + baseline). OBPI-02 (warn-only validator + tests) lands second; it requires OBPI-01's helper but no migration work. OBPI-03 (high-volume back-edge migration) is the longest OBPI and depends on OBPI-02's tooling. OBPI-04 (fail-closed promotion) requires OBPI-03's allowlist drain to be complete; its attestation includes the receipt asserting the baseline allowlist contains zero `phase: bootstrap` entries.

**Lane: Heavy.** New CLI scope (`--import-direction`) + new rule file + new Pydantic manifest model + behavior change across `src/gzkit/` import graph + new `gz check` pipeline step. Per `.claude/rules/cli.md` (new validator scope), `.gzkit/rules/skill-surface-sync.md` (new canonical rule surface), and AGENTS.md § Architectural Boundaries (this ADR is an architectural-boundary intervention itself). Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.36-universal-obpi-attestation.

**Relationship to existing architectural ADRs:**

- **Extends ADR-0.0.3-hexagonal-architecture-tune-up.** ADR-0.0.3 declares `core / ports / adapters` as the hexagonal ring. This ADR places `core` at L1 (Models tier; the foundational primitive layer), `adapters` at L2 (port implementations), and **promotes `ports` to Provider status with floor L1** — `ports` is exactly the *"explicit interface through which cross-cutting concerns enter"* that the OpenAI Providers pattern names, which is also precisely the hexagonal-port concept ADR-0.0.3 declares. The two doctrines compose cleanly: `ports` is *both* a hexagonal-port surface (ADR-0.0.3) *and* a Provider (this ADR), and the validator's Provider semantics enforce the hexagonal direction (any vertical layer can import `ports`; `ports` depends only on lower vertical layers).
- **Anchors on ADR-0.0.43-ddd-domain-cascade.** ADR-0.0.43 declares the per-domain DDD cascade; this ADR makes that cascade *applicable* by giving each domain a canonical position in the package-level order. Where a domain grows internal layers (future state — the OBPI pipeline runtime is the likely first), the ADR-0.0.43 cascade governs the internal direction; this ADR's validator extends to per-domain when `<subpackage>/_layer_order.json` is present, with the same tri-role classifier (vertical / Provider / Utility) applied at the per-domain scope.
- **References OpenAI Harness Engineering (2026-02-11) Figure 4 — *"Layered domain architecture with explicit cross-cutting boundaries."*** The diagram's three-region structure (vertical Types → Config → Repo → Service → Runtime → UI cascade; explicit **Providers** cross-cutting gateway; **Utils** outside the business-logic domain entirely) is the visual exemplar this ADR's tri-role classifier (vertical / Provider / Utility) mirrors. The diagram drove the late-stage refinement from an initial pure-vertical 11-layer model to the 8-vertical-layers + Providers + Utility model — see § Q&A Transcript and § Alternatives Considered Alt 6.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT modify the existing `core/ports/adapters` semantics from ADR-0.0.3 — those remain authoritative for what each ring layer contains.
- Does NOT author per-domain layer manifests for any current subpackage. Per-domain cascade enforcement (ADR-0.0.43 mechanical extension) is a future GHI when the first subpackage gains internal layers warranting it.
- Does NOT relocate or rename any source files except those required by the OBPI-03 back-edge migration; existing module names are preserved.
- Does NOT introduce new abstraction layers (e.g., a new `commands/cli_helpers/` subpackage to absorb the `cli ↔ commands` back-edges) without an OBPI-03 receipt naming the relocation explicitly. The migration is structural, not aesthetic.
- Does NOT extend to test code or to `tests/**` import direction; test fixtures may import freely. The invariant binds production code only.
- Does NOT mechanically enforce same-layer imports as either allowed or denied — equal-layer imports are allowed under the canonical order; if a future ADR wants to forbid them, it authors that constraint additively.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The src/gzkit package import-boundary policy holds — the import-direction invariant this ADR enforces across the subpackage graph. | uv run -m unittest tests.policy.test_import_boundaries | 0 |

## Consequences

### Positive

1. **The OpenAI Harness Engineering "rigid architectural model" pattern lands as a foundation invariant for gzkit's own package, not a verbal commitment.** New code landing under future ADRs inherits the layer order mechanically; back-edges are rejected at CI time once OBPI-04 promotes the validator to fail-closed. The Anti-vibing operative claim *"every option is framed by smallest-vibing-surface"* gains a structural defense at the import-direction surface.

2. **ADR-0.0.3 and ADR-0.0.43 get the missing structural rung that binds them.** Both pre-existing architectural ADRs declare *intent* (hexagonal ring; per-domain cascade). Neither carried mechanical enforcement of the *order between subpackages*. This ADR is the canonical "where do they compose" answer the package has been missing since the hexagonal tune-up landed.

3. **The 12+ back-edges the empirical audit surfaced get explicit, time-bound treatment.** Today: implicit, accumulating, uninspectable. After this ADR: enumerated in `data/package_import_direction_baseline.json`, each with a target-OBPI hint; migrated under OBPI-03 with per-edge receipts; the allowlist drains monotonically; the final state has zero bootstrap exemptions. The OpenAI thesis's *"corrections are cheap, waiting is expensive"* applies to the back-edges themselves — the cost of carrying them indefinitely exceeds the cost of paying them down in one bounded migration.

4. **The phased rollout (warn-only → migration → fail-closed) prevents doctrine debt.** The advisor framing pre-authoring identified this as the highest-risk failure mode: shipping a fail-closed validator on day one against a codebase that doesn't pass it. The phased pattern (warn-only first; baseline allowlist; monotonic drain; fail-closed at the end) is the same discipline `gz validate --reconcile-freshness` uses and the same baseline-allowlist pattern ADR-0.0.53 OBPI-04 uses — proven shape, low surprise.

5. **The validator surfaces every new back-edge at PR time, not at audit time.** Today, a new validator pulling a CLI helper "just this once" lands silently; over months, dozens accumulate. After OBPI-02, every PR introducing a new back-edge produces a warning during `gz check`; after OBPI-04, it fails the check. The pre-merge surfacing is the same mechanism that has compounded for `gz validate --advisory-scorecard` (every new rule landing without a scorecard entry fails the audit).

6. **The layer manifest becomes a tour of the package.** Today, a new agent landing in `src/gzkit/` confronts 40+ flat siblings with no obvious ordering. After this ADR, `data/package_layer_order.json` is the single-page map: 8 vertical layers, 3 declared Providers with floors and empirical justification, 1 Utility tier, and any future Provider-to-Provider edges in an explicit allowlist with rationale. This is the OpenAI thesis's *"agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front"* applied to the package itself — the manifest is the entry point, the tri-role classifier is the small stable surface.

7. **The validator composes naturally with `gz validate --remediation-payload-binding` from ADR-0.0.53.** Any layer-direction violation emits a `RemediationPayload` whose `recovery` field names the canonical resolution path (relocate the import; extract through a port; promote the concern to a new Provider declaration; or — last resort — add a baseline allowlist entry with a justifying GHI). Two foundation ADRs landing in the same session produce composable harness behavior — the OpenAI thesis's *"constraints become multipliers"* compounding case study.

8. **The Providers gateway absorbs the cross-cutting reality the pure-vertical model would have forced into permanent exemptions.** The empirical audit found `governance → arb` and `governance → hooks` imports already in production code; these are *not* layering violations — they are the cross-cutting concerns OpenAI's Providers pattern names. The pure-vertical 11-layer model would have either (a) baseline-allowlisted these indefinitely as `phase: permanent-exemption` entries (the failure mode Negative #5 names), or (b) forced a relocation that broke working code to satisfy a doctrinally-wrong model. The tri-role classifier surfaces these as legitimate vertical-to-Provider imports — no exemption needed, no relocation needed, the doctrine matches the code. This is the direct dividend of incorporating OpenAI Figure 4's structural insight before OBPI-01 lands.

9. **The Utility tier closes the depend-on-nothing gap.** `gzkit.utils` and similar truly-stateless helpers can be pulled from any layer without participating in the cascade. The discipline runs the other direction: Utility modules MUST NOT import any `gzkit.*` submodule (stdlib + named-departures only). This is enforceable mechanically (single check at validator runtime) and prevents the slow drift where a "utility" accretes domain knowledge and becomes a hidden middle-tier with no declared layer.

### Negative

1. **OBPI-03 migration is the longest OBPI in this ADR's decomposition.** The empirical audit identified at minimum 30+ back-edges across ~10 subpackage pairs requiring relocation or inversion. **Pre-mortem scenario:** 6 weeks into OBPI-03, the migration stalls because one back-edge (e.g. `commands → cli`) turns out to be load-bearing for a feature the operator depended on, and the relocation breaks a runbook command silently. **Mitigation:** every back-edge migration is paired with a regression-invariant test under `tests/governance/test_package_layer_order.py` capturing the function's behavior *before* the migration moves the symbol; the test fails if the post-migration code behaves differently. The same regression-invariant overlay pattern from `.claude/rules/adr-audit.md` § Legitimate-authoring exemptions applies — exception marker `# audit-exempt: regression-invariant-overlay <reason>` is allowed where the test enforces the prior invariant.

2. **The layer manifest may be wrong for some subpackages.** The 8-layer cascade + 3 Providers + 1 Utility tier above is the author's best inference from the empirical audit; some subpackages (`reporter`, `flags`, `insights`) have weak inbound/outbound signal and their layer assignment is partly judgment. **Pre-mortem scenario:** OBPI-03 surfaces that `insights` actually wants to import from `commands` for a legitimate reason (event-write helper), and the L4 placement is wrong — or that `insights` is actually Provider-shaped (cross-cutting event-emission). **Mitigation:** the manifest is updatable under amendment OBPIs without re-authoring this ADR; the tri-role classifier allows reclassifying any subpackage from vertical to Provider (or vice versa) with a single manifest edit + empirical-justification line. The validator's behavior is to enforce *whatever the manifest says*, so a role correction is mechanical. The cost of getting one subpackage's role wrong is one amendment OBPI; the cost of getting the manifest's *shape* wrong (which this ADR pins — three roles, contiguous layers, depend-on-nothing Utility, declared Provider edges) would be a re-ADR ceremony — the shape is the high-stakes piece.

3. **The validator's CLI scope adds another flag to `gz validate`.** `gz validate` already carries ~20+ scopes; one more is incremental but not free. Mitigated by: the scope follows the existing naming convention; it is added to the `gz check` default pipeline (so operators never need to invoke it manually); it produces no output when clean.

4. **Reversibility: this is a one-way door at the layer-order level.** Once OBPI-04 promotes the validator to fail-closed, downstream code (every future ADR's implementation) inherits the order. Reversal in 18 months would either require an amendment ADR loosening specific edges or an architectural rewrite of the package. Justified by: the alternative is the indefinite continuation of the implicit-order regime that produced the 12+ back-edges the audit found. The asymmetry is intentional; the cost of leaving the order implicit is what the OpenAI thesis names *"speed without decay or architectural drift"* losing the second half of the conjunction.

5. **The baseline allowlist may be abused as a permanent escape hatch.** **Pre-mortem scenario:** 12 months in, a difficult migration produces a new `phase: permanent-exemption` entry "just this once"; six months later, three more entries land; six months after that, the allowlist contains a dozen permanent exemptions and the invariant is back to advisory-only. **Mitigation:** every `phase: permanent-exemption` entry requires a foundation ADR justifying it (per OBPI-04's promotion criteria); the ADR ceremony is the structural friction. The `gz validate --import-direction` failure utterance includes the canonical-resolution-path recovery from ADR-0.0.53 — relocate, invert, or open a foundation ADR; the path-of-least-resistance is migration, not exemption.

6. **The `cli ↔ commands` migration may require introducing a third subpackage.** The current bidirectional flow (9 + 6 edges) suggests a missing utility layer between them. **Pre-mortem scenario:** OBPI-03 attempts to extract a `commands/cli_support.py` module to absorb the back-edges, but the helper organically grows into a 5th-layer subpackage with its own ambiguous placement. **Mitigation:** the manifest's L9 (commands) and L10 (cli) levels have one layer of headroom built in; the relocation target is a sibling within `commands/` (not a new sibling subpackage), keeping the manifest stable. If a new subpackage genuinely emerges, OBPI-03's migration receipt names it explicitly and the manifest gets a single-entry amendment — bounded scope.

7. **The 2am operator scenario:** an operator on-call at 2am needs to ship a hotfix that requires a cross-layer import; the fail-closed validator refuses to merge. **Mitigation:** during the warn-only phase (OBPI-02 through OBPI-03), the validator never blocks. After OBPI-04 fail-closed promotion, the operator has three options surfaced by the validator's `RemediationPayload`: (a) relocate the import (mechanical), (b) add a `phase: bootstrap` baseline allowlist entry with the operator's GHI commitment to clean it up in the next sprint (one-line JSON edit), or (c) merge with the validator override flag (`--allow-layer-violation` with a required GHI argument, surfaced explicitly in the rule file). The escape hatch exists, is structurally bounded (requires a GHI), and produces a ledger event that the next audit catches.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 2
- Dimension Total: 8
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.55-01: Author tri-role manifest (vertical layers + Providers + Utility) + helper + rule + scorecard + baseline allowlist (post-reclassification bootstrap snapshot)
- [ ] OBPI-0.0.55-02: Ship `gz validate --import-direction` in warn-only mode + `gz check` integration + manpage
- [ ] OBPI-0.0.55-03: Migrate high-volume back-edges (cli↔commands, governance→cli/commands, doc_coverage→commands, etc.) + drain baseline allowlist of bootstrap entries
- [ ] OBPI-0.0.55-04: Promote validator to fail-closed + runbook updates + rule version `0.1.0 → 1.0.0`

## Q&A Transcript

<!-- Interview transcript preserved for context -->

**Operator framing:** Discussion of OpenAI's "Harness Engineering" thesis surfaced *"rigid architectural model with strictly validated dependency directions and a limited set of permissible edges"* as the structural lever gzkit had not mechanically realized despite ADR-0.0.3 (hexagonal) and ADR-0.0.43 (DDD cascade) declaring the intent.

**Bounded decision (layer doctrine basis):** Three options surfaced — (1) extend ADR-0.0.3 hexagonal at package level, (2) anchor on ADR-0.0.43 DDD cascade, (3) define a new explicit layer list. Operator selected **(1)+(2) composed**: hexagonal at the package level (extending ADR-0.0.3) AND DDD cascade per-domain (anchoring on ADR-0.0.43), with this ADR as the structural rung between them.

**Pre-authoring empirical audit** (advisor-prescribed before authoring): the import-graph script enumerated current cross-subpackage edges. Top findings: `commands → governance` (33), `commands → content` (17), `commands → complexity` (13), `governance → core` (12), `commands → hooks` (10), `commands → cli` (9, REVERSE), `commands → doc_coverage` (8), `cli → commands` (6), `governance → cli` (1, REVERSE), `governance → commands` (2, REVERSE), `doc_coverage → commands` (4, REVERSE), `arb → commands` (1, REVERSE), `chores → commands` (1, REVERSE), `hooks → cli` (1, REVERSE), `justify → cli` (1, REVERSE). At least 12 distinct back-edges across ~10 subpackage pairs. **Implication:** day-one fail-closed validator produces doctrine debt; phased rollout required.

**Composition relationship to existing ADRs:** ADR-0.0.3 (hexagonal ring, `core/ports/adapters`) is preserved verbatim and assigned canonical layers L1/L2/L3. ADR-0.0.43 (DDD cascade) is referenced as the per-domain governance for any subpackage that grows internal layers; the validator extends per-domain when `<subpackage>/_layer_order.json` appears.

**OBPI brief authoring deferral (explicit annotation):** The 4 OBPIs declared in this ADR's Checklist (OBPI-0.0.55-01 through -04) are listed as canonical decomposition items, but their per-brief authoring under `gz-obpi-specify` is **deferred to a follow-up session** and tracked under **GHI #499** (sibling-class to GHI #495). The 1:1 Synchronization Mandate is satisfied at the Checklist level; the `obpis/` subdirectory populates under GHI #499's follow-up authoring passes before this ADR's promotion from Draft to Proposed.

**Late-stage decomposition refinement (Figure 4 driven):** This ADR's first draft pinned a pure-vertical 11-layer model with `arb` at L7 and `hooks` at L8. The operator surfaced OpenAI Harness Engineering's Figure 4 (*"Layered domain architecture with explicit cross-cutting boundaries"*) before promotion; the diagram's explicit **Providers gateway** + **Utils-outside-the-domain** pattern reframed the question from *"where do `arb` and `hooks` sit in the cascade?"* to *"are `arb` and `hooks` actually vertical-cascade members, or cross-cutting concerns?"* The pre-amendment empirical audit confirmed the cross-cutting reality: `governance/trust_audits/attestation_receipts.py` imports `gzkit.arb` from L5; `governance/trust_audits/kind_invariance.py` imports `gzkit.hooks` from L5; multiple top-level modules pull `hooks` directly. These imports are not back-edges to be migrated — they are the legitimate cross-cutting consumption the Providers pattern names. The 8-vertical-layer + Providers + Utility model that landed in § Decision is the result; the original 11-layer model is preserved as Alternatives Considered Alt 6.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/governance/test_package_layer_order.py` (import-graph empirical fixture + per-edge regression-invariants), `tests/governance/test_import_direction_validator.py` (validator scope), `tests/governance/test_layer_order_manifest.py` (manifest Pydantic shape)
- [ ] Rule file: `.gzkit/rules/package-import-direction.md` (version `0.1.0 → 1.0.0` on OBPI-04 promotion)
- [ ] Manifest: `data/package_layer_order.json`
- [ ] Baseline allowlist: `data/package_import_direction_baseline.json` (drains monotonically; empty `phase: bootstrap` entries by OBPI-04)
- [ ] Scorecard: `docs/governance/advisory-rules-audit.md` entry (Mechanical)
- [ ] Docs: `docs/user/manpages/validate.md` (new `--import-direction` scope), `docs/governance/governance_runbook.md` § Layer doctrine, `docs/user/runbook.md` § Common errors

## Alternatives Considered

**Alt 1: Day-one fail-closed validator with no baseline allowlist.** Maximally rigorous. Rejected because the empirical audit identified 12+ existing back-edges; day-one fail-closed would either block every CI run until the migration completed, or force the migration to land in a single mega-PR (anti-pattern). The phased rollout is the proven shape (`gz validate --reconcile-freshness` bootstrap; ADR-0.0.53 baseline drain).

**Alt 2: Advisory rule only (no validator).** Author the rule file; classify it Promotable; defer the validator. Rejected because the OpenAI thesis's empirical claim — that mechanical enforcement is the lever — applies precisely when the rule is hard to police visually. The 12+ existing back-edges are evidence that human review alone is insufficient; the validator is the structural defense.

**Alt 3: Per-subpackage manifest files (no central manifest).** Each subpackage carries its own `_layer.json` declaring its layer. Rejected because (a) the layer-order constraint is *between* subpackages, not within them — the global picture is what the validator needs; (b) per-subpackage manifests rot independently with no cross-coupling check; (c) the OpenAI thesis explicitly named the *single map* property — *"agents start with a small, stable entry point and are taught where to look next."*

**Alt 4: Use `import-linter` or another third-party tool.** A mature package exists for exactly this purpose. Rejected per gzkit's stdlib-first doctrine — the layer-direction check is well within stdlib reach (`ast` for parsing, dict lookup for layer comparison), the manifest is small (single JSON), and the validator's logic is ~50 lines. Adding a third-party dependency for ~50 lines of well-bounded logic violates the named-departure rule. (This is precisely the *"reimplement a subset rather than pull a generic package"* discipline the OpenAI piece independently endorses with its p-limit example.)

**Alt 5: Defer per-domain DDD cascade enforcement to a future ADR.** Author this ADR as package-level only. Considered, rejected because the operator's "1+2" composition explicitly named both as in-scope; the per-domain extension is a single-paragraph addition to the validator (look for `<subpackage>/_layer_order.json` and apply the cascade) rather than a separate ADR.

**Alt 6: Pure-vertical 11-layer model with no Providers gateway and no Utility tier (the original first-draft model).** Place every subpackage including `arb`, `hooks`, `ports` on the single vertical cascade (L0–L10), no cross-cutting role, no depend-on-nothing exemption. Rejected after the operator surfaced OpenAI Harness Engineering Figure 4 and the pre-amendment empirical audit confirmed that `governance → arb` and `governance → hooks` are *real, legitimate, in-production* cross-cutting imports — not back-edges to migrate. The pure-vertical model would have forced two unacceptable outcomes: (a) baseline-allowlisting these forever as `phase: permanent-exemption` (silently doctrinally-wrong; the failure mode Negative #5 names); or (b) inverting the dependency through ports-only-indirection that doesn't match the actual cross-cutting nature of receipt-emission and event-interception. The tri-role classifier landed in § Decision is the result of incorporating Figure 4's empirical evidence ("Cross-cutting concerns enter through a single explicit interface: Providers; anything else is disallowed and enforced mechanically") plus gzkit's own import-graph audit confirming that `arb` and `hooks` already behave this way in production. **Material consequence:** under Alt 6 the baseline allowlist would have started with ~12 vertical-to-vertical back-edges *plus* ~5 cross-cutting "back-edges" that aren't really back-edges; under the landed model the baseline starts with only the genuine ~12, and the Providers reframing is a *zero-cost win* (no code moves, the doctrine matches existing reality).

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.55 | Pending | | | |
