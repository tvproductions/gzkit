---
id: ADR-0.0.43-ddd-domain-cascade
status: Draft
kind: foundation
semver: 0.0.43
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-11
---

# ADR-0.0.43: DDD Domain Cascade

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
This ADR formalizes a domain-modeling cascade that has been implicit in gzkit
since its origins; the agent who advances it must respect the strict
source-of-truth separation between PRD strategic surface (Layer 1), DM tactical
surface (Layer 1), and derived navigation views (Layer 3) as identity-shaping.
Anti-vibing mantra applies throughout — `gz-glossary-<term>` markers are the
smallest-vibing-surface for glossary discipline; the AST cross-context import
enforcer is the strongest-mechanical-enforcement layer Python permits;
operator-attested ratification of LLM-classified legacy mappings is the
canonical pattern for any future agent-drafted-then-human-attested ceremony.
Domain modeling is human judgment; the validator catches drift but never
authors semantics.

## Why foundation tier?

Without this ADR, gzkit's domain boundaries cascade ungoverned — cross-domain checks (validators, gates, ceremony steps) accumulate without a unified routing or coverage discipline, and domain-overlap drift becomes silent maintenance debt.

This ADR authors a port: the DDD domain-cascade contract every cross-domain validator and ceremony step binds to.

## Intent

gzkit currently lacks an explicit pre-Gate-1 link from PRD intent through to ADR decision that captures the three core artifacts of Domain-Driven Design: shared vocabulary, bounded contexts, and documented inter-context contracts. The cascade is implicit today — PRDs describe project context, ADRs make architectural decisions, OBPIs decompose implementation — but there is no mechanical surface enforcing that ADRs land within a named bounded context, no canonical glossary that ADR / GHI / OBPI prose resolves against, and no context map declaring how bounded contexts integrate. The consequence is what Evans (2003) named *model integrity collapse*: agents and operators reach for terms like 'change', 'user', 'context', 'event' across artifacts with subtly different meanings depending on the BC being implicitly assumed, and no validator catches the drift. In agentic SDLC the problem is acute: a single ADR conversation can span minutes; a fresh agent session inherits no shared vocabulary; same-token-different-meaning collisions become silent and accumulate across the artifact graph.

The cascade this ADR codifies is *not* a foreign methodology. gzkit's foundation / feature kinds already approximate Evans's bounded-context distinction; lane (lite / heavy) approximates context-map relationship semantics; attestation receipts and ledger events already capture cross-context provenance. The decision here is to formalize what gzkit implicitly does — naming the structure that is already present and making it mechanically enforceable. The operator's 'so close to using DDD already' framing surfaced during design dialogue is the rationale anchor: this ADR moves implicit into explicit, not foreign into native.

The shakiest condition surfaced during Tier-2 WWHTBT analysis is the AST cross-context import enforcer's false-positive rate on the existing gzkit corpus. Python's import semantics (lazy imports, conditional imports, `importlib`) historically defeat static analysis; if the enforcer flags >5% of legitimate code patterns, operators will route around it via inline bypass comments and the enforcement collapses. OBPI-11 is scoped explicitly against this risk: static AST analysis with a documented exception inline-marker (`# cascade-allowed: <reason>` emitting a ledger event), not runtime enforcement. Runtime cross-context import blocking is deferred to a named future ADR (ADR-0.0.46-cross-context-import-runtime-block) so the foundation cascade can land without coupling to a higher-risk technical commitment.

## Decision

Codify a three-layer domain cascade with strict source-of-truth discipline and binding Gate-1 enforcement.

**Layer 1 (canon) — PRD strategic surface.** PRDs gain three new sections after `## 2. Overview`:

- `## 2.1 Ubiquitous Language` — project-wide and per-BC glossary. YAML-renderable entries: `term`, `scope` (cross-cutting | <bc-slug>), `definition`, `provenance` (ADR refs that codified or refined the term).
- `## 2.2 Bounded Contexts` — BC enumeration. Per BC: `slug`, `purpose`, `owner_persona`, `lifecycle_state` (active | deprecated | retired), `dm_ref`, `introduced_in` (PRD or ADR id).
- `## 2.3 Context Map` — inter-BC relationships. Per entry: `from`, `to`, `type` (Evans-7 + Vernon Partnership + Big-Ball-of-Mud anti-pattern), `description` (operator-authored prose ≥10 words grounding the label in this project's actual semantics).

**Layer 1 (canon) — DM tactical surface.** New artifact type at `docs/design/domain/DM-<bc-slug>.md` — one per BC, never per PRD. Required sections: `## Identity`, `## Glossary Specializations`, `## Aggregates` (≥1), `## Implementation Surface`, `## Inbound Contracts`, `## Outbound Contracts`. Optional: `## Entities`, `## Value Objects`, `## Domain Events`, `## Open Questions`. `## Decision History` is auto-populated from ADR `bounded_context:` frontmatter by `gz domain regenerate` (Layer-3-within-Layer-1 carve-out, validator-checked for staleness).

**Layer 3 (derived) — navigation views.** Three flat-file readable surfaces under `docs/design/domain/`: `glossary.md`, `bounded-contexts.md`, `context-map.md`. Regenerated by `gz domain regenerate` from PRD § 2.1 / 2.2 / 2.3 + all DMs. **Never source-of-truth, never hand-edited.** Freshness fail-closed by `gz validate --domain-views-fresh` (parallels `--adr-status-fresh` from GHI #322).

**ADR / GHI / OBPI frontmatter cascade keys:**

- ADR (non-pool): `bounded_context:` required (string or list); `domain_model:` optional; `crosses_contexts:` optional.
- ADR (pool): same as above but all optional.
- GHI: `bounded_context:` required; `crosses_contexts:` optional; `cascade_change: true|false` for triage prioritization.
- OBPI: inherits parent ADR; `bounded_context_override:` for rare sub-BC scoping.

**Marker convention (binding precedent for all future gzkit-namespace categories).** Glossary terms referenced in prose use backticked `gz-glossary-<term>` form. Validator rule (stateless, three-tier):

1. Backticked token `gz-glossary-<term>` AND not a registered skill name → glossary reference, must resolve, fail-closed at Gate 1.
2. Backticked token matches registered skill name (`gz-design`, `ghi-author`, etc.) → skill reference, no glossary check.
3. Anything else → code identifier, no glossary check.

Future gzkit-namespace categories follow the `gz-<category>-<entity>` pattern. No single-letter discriminators (rejected `gzd-`, `gzi-`, `gzr-` family for opacity and scaling cost). Verbosity is bounded; clarity is unbounded.

**Three-point pre-Gate-1 enforcement:**

1. *Authoring time* — `gz plan create --bounded-context X` refuses unknown BC with exit 3 (operator gets error before file exists).
2. *Document validation* — `gz validate --domain-cascade` runs cascade integrity check on every CI / local pass.
3. *Gate 1 audit* — `gz adr audit-check` reads frontmatter, verifies cascade integrity, fail-closed on unresolved.

Block-after-backfill: legacy ADRs run through hybrid migration (frontmatter for new + classification index for legacy) before fail-closed mode activates corpus-wide.

**Cascade-touchpoint contract — slow gear / fast gear.** Slow gear (populate): `gz-prd`, new `gz-domain-enumerate` skill, new `gz-domain-model` skill, mechanical `gz domain regenerate`. Fast gear (reference + enforce): `gz-design` (pre-flight BC question, block on unknown), `gz-obpi-pipeline` verify stage (AST cross-context import enforcer), `ghi-author` (required BC frontmatter + cascade-change flag), `ghi-close` (mini-Gate-5 reconciliation), `ghi-triage` (BC-grouped rendering + cascade-change priority tier), `gz-adr-evaluate` (cascade-compliance scoring dimension), `gz-adr-closeout-ceremony` (mini-Gate-5 cascade reconciliation), `gz-adr-audit` (cascade integrity audit section). **The cascade is populated lazily, referenced eagerly, enforced at gates** — the translation that lets a 20-year-old methodology fit an agentic SDD loop.

**2am operator affordances** (added during interview Tier 2.5):

- `gz validate --domain-cascade --accept-undefined-term <term> --accept-reason <REASON>` — emergency bypass for hotfix prose using yet-to-be-glossaried term; emits `cascade_debt_acknowledged` ledger event.
- `# cascade-allowed: <reason>` inline marker in Python source — AST enforcer respects; emits `cascade_import_bypass` ledger event.
- `gz validate --domain-cascade --skip-legacy` — emergency triage when legacy-mapping YAML has typo blocking everything.
- `gz obpi complete --bc-introduced <slug> --bc-introduced-reason <REASON>` — operator introduces a new BC during implementation but PRD update is blocked; emits `bounded_context_pending_ratification` ledger event, PRD update happens async.
- Every cascade validator failure carries a `Resolve:` line naming the path to fix.
- `gz domain regenerate --check` dry-run mode; atomic write-temp-then-rename; views written under `.gzkit/state/storybook-views-prev/` for one-shot rollback.

**Backfill — hybrid one-shot, agent-classified, operator-attested.** OBPI-07 implements: LLM-as-judge classification walks each of the ~49 existing canonical ADRs + ~118 pool entries + completed OBPIs, drafting a `bounded_context:` mapping. Output lands at `docs/design/domain/legacy-adr-bc-mapping.yaml.draft`. Operator reviews, corrects misclassifications, ratifies. Final file at `docs/design/domain/legacy-adr-bc-mapping.yaml`. Validator dual-mode: checks frontmatter first, falls back to legacy mapping for legacy IDs. One-way promotion allowed (index → frontmatter on next modification, never reverse). The existing corpus is primary evidence of what BCs gzkit already has — classification is *extraction from canon, not invention*. The bootstrap BC list for PRD § 2.2 surfaces from the classification, not from a blank page.

**Ledger event surface (Layer-2 truth):**

- `bounded_context_created`, `bounded_context_renamed`, `bounded_context_retired`
- `glossary_term_added`, `glossary_term_revised`
- `context_map_updated` (action: added | revised | removed)
- `domain_model_created`, `domain_model_revised`
- `legacy_mapping_ratified` (count, ratified_by)
- `cascade_reconciled` (closing_artifact, changes[]) — emitted at closeout
- `cascade_debt_acknowledged`, `cascade_import_bypass`, `bounded_context_pending_ratification` — 2am-affordance events

**Reversibility assessment.** Predominantly **one-way door**. One-way: PRD § 2.1 / 2.2 / 2.3 section schema, BC slugs once referenced by ADRs / GHIs, ledger event types, marker convention `gz-glossary-<term>`. Two-way: skill extensions, scorecard dimensions, validator severity (warning ↔ fail-closed), Evans-vocabulary enum extensions (additive). 12-month reversal cost: very high (corpus-wide migration with operator attestation). Foundation-heavy ceremony is appropriate.

**Kind: foundation.** Identity-shaping — changes what gzkit IS (cascade-governed) rather than producing a new release-carrying capability. Per ADR-0.0.18 taxonomy doctrine.

**Lane: heavy.** New CLI verbs (`gz domain *` subgroup), new validator scopes (`--domain-cascade`, `--domain-views-fresh`), new directory contract (`docs/design/domain/`), new schemas (BoundedContextDeclaration, DomainModel, ContextMapEntry, GlossaryTerm, LegacyAdrBcMapping), new artifact type (DM), required frontmatter on three artifact types (ADR / GHI / OBPI), new ledger event types. External-contract surface across the board.

**Sensitivity: absent.** No security surface.

**Implementation surface anchors.** OBPI execution lands new and extended surfaces against these existing canonical files and directories:

- *PRD canon being extended* — [docs/design/prd/PRD-GZKIT-1.0.0.md](../../../prd/PRD-GZKIT-1.0.0.md) gains `## 2.1` / `## 2.2` / `## 2.3` sections via OBPI-13 amendment; [src/gzkit/templates/prd.md](../../../../../src/gzkit/templates/prd.md) gains the same scaffold sections via OBPI-01.
- *Pydantic surface* — [src/gzkit/governance/__init__.py](../../../../../src/gzkit/governance/__init__.py) gains new `domain_models.py` module (OBPI-01 lays `UbiquitousLanguageTerm`, `BoundedContextDeclaration`, `ContextMapEntry`; OBPI-02 extends with `DomainModel`, `Aggregate`, `Entity`, `ValueObject`, `DomainEvent`, `ImplementationSurface`, `InboundContract`, `OutboundContract`).
- *Schema surface* — [src/gzkit/schemas/__init__.py](../../../../../src/gzkit/schemas/__init__.py) gains new `{glossary_term, bounded_context, context_map_entry, domain_model, legacy_mapping}.json` files; OBPI-04 extends [src/gzkit/schemas/adr.json](../../../../../src/gzkit/schemas/adr.json), `ghi.json`, `obpi.json` with cascade-key frontmatter requirements.
- *CLI surface* — [src/gzkit/cli/__init__.py](../../../../../src/gzkit/cli/__init__.py) gains new `domain.py` module via OBPI-03 (`gz domain init/list/status/show/regenerate` verbs); OBPI-06 extends `validate.py` and `check.py` with `--domain-cascade` / `--domain-views-fresh` scopes.
- *Validator surface* — [src/gzkit/governance/trust_audits](../../../../../src/gzkit/governance/trust_audits) gains a `domain_cascade.py` validator scope via OBPI-06, parallel to the existing audit scopes (advisory-scorecard, reconcile-freshness, cli-alignment, adr-status-fresh).
- *Skill canon* — two new skills land at `.gzkit/skills/gz-domain-enumerate/SKILL.md` and `.gzkit/skills/gz-domain-model/SKILL.md` via OBPI-08; OBPI-09 extends [.gzkit/skills/gz-prd/SKILL.md](../../../../../.gzkit/skills/gz-prd/SKILL.md), [.gzkit/skills/gz-design/SKILL.md](../../../../../.gzkit/skills/gz-design/SKILL.md), [.gzkit/skills/gz-adr-evaluate/SKILL.md](../../../../../.gzkit/skills/gz-adr-evaluate/SKILL.md), [.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md](../../../../../.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md), [.gzkit/skills/gz-adr-audit/SKILL.md](../../../../../.gzkit/skills/gz-adr-audit/SKILL.md); OBPI-10 extends [.gzkit/skills/ghi-author/SKILL.md](../../../../../.gzkit/skills/ghi-author/SKILL.md), [.gzkit/skills/ghi-close/SKILL.md](../../../../../.gzkit/skills/ghi-close/SKILL.md), [.gzkit/skills/ghi-triage/SKILL.md](../../../../../.gzkit/skills/ghi-triage/SKILL.md).
- *Persona* — agents working this ADR adopt [.gzkit/personas/main-session.md](../../../../../.gzkit/personas/main-session.md).
- *Doctrine references* — Layer-1/2/3 separation per [docs/governance/state-doctrine.md](../../../../governance/state-doctrine.md); kind/lane semantics per [docs/governance/GovZero/adr-status.md](../../../../governance/GovZero/adr-status.md); anti-vibing and operator-economy rationale per [docs/governance/agent-contract-rationale.md](../../../../governance/agent-contract-rationale.md); ADR taxonomy semantics per [docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md](../ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md).
- *New canonical paths this ADR creates* — `docs/design/domain/DM-<bc-slug>.md` (per-BC tactical model, OBPI-02); `docs/design/domain/glossary.md` / `bounded-contexts.md` / `context-map.md` (Layer-3 views, OBPI-06); `docs/design/domain/legacy-adr-bc-mapping.yaml` (OBPI-07); `docs/governance/domain-cascade.md` (doctrine page, OBPI-12); `docs/user/manpages/gz-domain*.md` (OBPI-12).

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: the named gz validate --domain-views-fresh validator is unlanded (ADR is Draft); the sibling Layer-3 derived-view freshness gate this ADR explicitly parallels holds green. | uv run gz validate --adr-status-fresh | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.43-ddd-domain-cascade --check | 0 |

## Consequences

### Positive

1. gzkit gains a mechanical pre-Gate-1 link from PRD intent through ADR decision that makes domain modeling enforceable rather than aspirational. Three-point Gate-1 enforcement (authoring-time, validation, audit) makes laziness mechanically impossible to slip into never-populated.
2. The cascade becomes the navigation taxonomy for governance work writ large — ADRs, GHIs, OBPIs all anchor to bounded contexts. Triage and review can slice by domain rather than chronology, which becomes more valuable as the artifact graph grows.
3. The 'so close to using DDD already' insight is operationalized — gzkit's foundation / feature kinds already approximate bounded contexts; lane semantics already approximate context-map relationships; this ADR formalizes what is present, lowering doctrine-imposition cost.
4. Slow-gear / fast-gear discipline maps directly to agentic SDLC reality: the cascade is populated lazily when conversations reveal missing structure, referenced eagerly during ADR / OBPI / GHI authoring, and enforced at gates. This is the translation that lets DDD (2003) fit agentic SDD without front-loading modeling ceremony.
5. The marker convention `gz-glossary-<term>` is a stateless, three-tier validator rule with no skill-registry tiebreaker dependency. Future gzkit-namespace categories inherit the `gz-<category>-<entity>` pattern as binding precedent. No proliferating single-letter discriminator family.
6. Layer separation is mechanically enforced: PRD § 2.1 / 2.2 / 2.3 and DM files are Layer-1 canon; flat-file views are Layer-3 derived; `gz domain regenerate` is the only path from canon to view; `gz validate --domain-views-fresh` is the freshness backstop. Source-of-truth ambiguity cannot accumulate silently.
7. The Evans-vocabulary enum (shared-kernel, customer-supplier, conformist, anticorruption-layer, separate-ways, open-host-service, published-language, plus Vernon's partnership and the big-ball-of-mud anti-pattern recognition) is canonical translatable vocabulary with required prose grounding. Labels alone are insufficient; the grounding sentence pins the label to project semantics.
8. The 2am operator affordances (`--accept-undefined-term`, `# cascade-allowed:`, `--skip-legacy`, `--bc-introduced`, `Resolve:` line in every error) match gzkit's existing fail-closed-with-escape-hatches pattern (`--accept-uncovered`, `--dry-run`, storybook `--accept-stale-storybook`). Operational continuity preserved without weakening the doctrine.
9. The hybrid backfill strategy bounds migration work to a single OBPI (OBPI-07) with agent-drafted classification + operator attestation. Completed ADRs are not reopened. The bootstrap BC list for PRD § 2.2 emerges from classification — the existing corpus is primary evidence, not a blank-page authoring task.
10. The AST cross-context import enforcer (OBPI-11) gives Python-level mechanical enforcement of context-map declarations. Cross-context imports without a context-map entry fail-closed during `gz obpi pipeline` verify stage. This is the strongest enforcement layer: compiler-style, cannot lie. Runtime enforcement deferred to a named future ADR to keep this ADR's risk envelope bounded.
11. GHIs gain a first-class place in the cascade. `ghi-author` requires `bounded_context:`; `ghi-close` runs mini-Gate-5 cascade reconciliation; `ghi-triage` groups by BC and prioritizes cascade-change-labeled issues. GHIs are the highest-frequency governance surface; cascade enforcement here keeps the cascade true between ADR-scale slow-gear turns.
12. Reversibility is honest: one-way doors are named explicitly (PRD section schema, BC slugs, ledger event types, marker convention). Foundation-heavy ceremony is justified by the corpus-wide reversal cost.

### Negative

1. **Adds significant surface area to gzkit.** Two new skills (`gz-domain-enumerate`, `gz-domain-model`), nine existing-skill extensions (`gz-prd`, `gz-design`, `gz-adr-evaluate`, `gz-adr-closeout-ceremony`, `gz-adr-audit`, `ghi-author`, `ghi-close`, `ghi-triage`, `gz-obpi-pipeline`), new CLI subcommand group (`gz domain`), two new validator scopes, new artifact type (DM), new schemas, new ledger event types, new frontmatter requirements on three artifact types. The operator explicitly accepted this growth ('I know the surface of gzkit grows, but I am so close to using DDD already that it makes sense now') — the cost is acknowledged, not denied.
2. **Pre-mortem failure mode — glossary inflation.** PRD § 2.1 grows past comprehension (>200 terms); agents cannot reliably scan it; backtick markers become technically valid but semantically noisy; cascade is 'compliant' but no longer aids comprehension. Mitigation: glossary growth boundary doctrine deferred to a future ADR (named in Forced Downstream Commitments) when corpus warrants — likely when § 2.1 crosses ~100 terms.
3. **Pre-mortem failure mode — legacy mapping ratification stalls.** LLM-as-judge classification produces ~70% accuracy; operator never finds time to ratify the remaining 30%; validator runs in warning mode indefinitely; cascade is half-true. Mitigation: OBPI-07 requires operator ratification as the completion criterion, not classification draft. Closeout is gated on full ratification. If classification accuracy <70% during OBPI-07 execution, abandon the LLM step and author the mapping directly.
4. **Pre-mortem failure mode — AST enforcer false positives.** Python's import semantics (lazy imports, conditional imports, `importlib.import_module`) defeat naive AST analysis; enforcer produces enough false positives that operators add `# cascade-allowed:` comments liberally; the enforcer becomes ignored. Mitigation: OBPI-11 scoped to static AST analysis with documented exception inline-marker; runtime enforcement deferred to ADR-0.0.46. WWHTBT shakiest condition: false-positive rate <5% on existing corpus must be measured during OBPI-11 implementation and reported in evidence.
5. **Pre-mortem failure mode — BC churn outpaces ledger events.** Bounded contexts get renamed / split as gzkit evolves; ledger event types for renames exist but downstream artifacts (legacy mapping YAML, 100+ ADR frontmatters) don't auto-track; orphan BC references accumulate. Mitigation: `gz validate --domain-cascade` catches orphan BC references on every run; rename ceremony documented as part of OBPI-04 frontmatter validators.
6. **Pre-mortem failure mode — closeout reconciliation becomes rubber-stamp.** Operator clicks through cascade check at Gate 5 without engaging; introduced terms / contracts during implementation are never propagated; cascade is 'true at closeout' by attestation but false by content. Mitigation: closeout cascade reconciliation requires named diff (terms added / contracts changed / BCs touched); empty diff with non-trivial implementation is a flag for operator review.
7. **Pre-mortem failure mode — marker convention fatigue.** Operators find `gz-glossary-<term>` too verbose; write `change` in prose instead; validator can't see them; glossary terms drift unenforced. Mitigation: marker convention is mechanically required only at gate boundaries (ADR / GHI promotion, Gate-1 audit). Day-to-day prose can be loose; gate enforcement forces the marker discipline where it matters.
8. **Assumption-surfacing risk — operators may prefer chronological browsing.** The cascade introduces BC-grouped navigation as the new primary taxonomy. If operators don't engage with BC-grouped views, the navigation value of the cascade collapses to its enforcement value alone. Mitigation: `gz domain show` and `gz domain list` are additive surfaces; chronological views (existing `gz status`, `gz adr status`) remain unchanged. Operators can ignore BC-grouped views without breaking anything.
9. **Assumption-surfacing risk — 13 OBPIs may be over-fragmented.** Some OBPIs (04 frontmatter + 05 ledger events + 06 validator wiring) are tightly coupled; closeout overhead may be disproportionate to implementation effort. Mitigation: keep 13 OBPIs for clean review boundaries; reconciliation pass after first half of OBPIs lands may merge if coupling is excessive.
10. **Assumption-surfacing risk — foundation-kind vs feature-kind ambiguity.** Domain modeling produces a user-visible capability (`gz domain show`), arguably feature-kind. Decision: foundation per ADR-0.0.18 (identity-shaping wins over capability-producing when ambiguous). Documented tension; not a blocker.
11. **Scope-minimization tension.** Minimal version (just `bounded_context:` frontmatter + Gate-1 validator) delivers ~20% of current scope at ~5x less effort. Operator overrode with 'EVERYTHING in scope for 0.0.43.' Justification: foundation cost-of-incompleteness premium — partial cascade is half a cascade is no cascade. Documented as scope override, not scope creep.
12. **Constraint-archaeology surface — Evans vocabulary kept by assumption.** Could rename to gzkit-native vocabulary; chose to keep canonical for translatability. Cost: some readers may find Evans's mid-2000s enterprise-Java terms ('Anticorruption Layer', 'Open Host Service', 'Conformist') alienating. Bet: gzkit's audience is engineering-literate; canonical vocabulary is worth preserving.
13. **Reversibility cost.** Predominantly one-way door. 12-month reversal would require corpus-wide migration with operator attestation. The ADR ceremony level (foundation, heavy, full evaluation scorecard, full OBPI decomposition, human attestation at every OBPI closeout) is calibrated to this irreversibility.
14. **PRD-GZKIT-1.0.0 amendment required.** OBPI-13 amends PRD § 2.1 / 2.2 / 2.3 with the discovered BC list from legacy classification. This is the first-cascade-authoring exercise. PRD is currently semver 0.3 (Draft); the amendment lifts it to 0.4 (Draft - DDD Domain Cascade integrated).

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
- Baseline Selected: 9
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 13

<!-- Split rationale:
  - Single-Narrative (2): PRD/DM/views are three independent canon narratives; new
    skills vs existing-skill extensions are different authoring narratives.
  - Surface Boundary (3): CLI, validator, schema, skill mesh, runbook docs each
    cross distinct surface boundaries that warrant their own brief.
  - State Anchor (2): frontmatter cascade, ledger event surface, and derived-view
    freshness are three independent state anchors with their own invariants.
  - Testability Ceiling (1): AST cross-context import enforcer has a separately
    measurable false-positive-rate test boundary distinct from the cascade
    validator's structural correctness boundary. -->

**Path-overlap management strategy.** Several OBPIs share file-path globs by
design — the Pydantic domain-model surface is naturally cross-cutting and
cannot be split along strict path-disjoint lines without losing schema
coherence. OBPI-01 and OBPI-02 both extend `src/gzkit/governance/domain_models.py`
because PRD-strategic models and DM-tactical models share the same Pydantic
module; OBPI-01, 02, 04, 07 all extend `src/gzkit/schemas/**` because the
schema surface is the contract layer for every cascade artifact. The overlap
is managed at *implementation sequencing time*, not by structural splitting:

- **OBPI-01 must land first** — it lays the foundational Pydantic surface
  (`UbiquitousLanguageTerm`, `BoundedContextDeclaration`, `ContextMapEntry`) and
  the schema directory layout. Every subsequent OBPI imports from this.
- **OBPI-02, 04, 05 can run after 01 in parallel** — once the foundational
  Pydantic surface is locked, the DM model (02), frontmatter cascade keys (04),
  and ledger event schemas (05) are independent additive extensions.
- **OBPI-06 (validator) waits for 04 + 05** — cascade-integrity checks depend
  on frontmatter + ledger surfaces being defined first.
- **OBPI-07 (legacy mapping) waits for 06** — classification driver consumes
  the validator's BC-resolution logic.
- **OBPI-08, 09, 10 (skills) can run in parallel after 06** — skill extensions
  reference the validated cascade surface but don't depend on each other.
- **OBPI-11 (AST enforcer) waits for 02** — needs the DM Implementation Surface
  schema to know which paths belong to which BC.
- **OBPI-12, 13 (docs + PRD amendment) run last** — capture the landed cascade
  in runbooks and populate PRD § 2.1 / 2.2 / 2.3 with the discovered BC list
  from OBPI-07 classification.

The execution graph (01 → {02, 04, 05} → 06 → {07, 08, 09, 10} → {11, 12, 13})
keeps coupled OBPIs sequenced and independent OBPIs parallelizable. Closeout
review boundaries remain clean because each OBPI carries a distinct narrative
(strategic schema, tactical schema, validator, classification, skill, etc.)
even when allowed-paths overlap.


## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.43-01: PRD § 2.1 / 2.2 / 2.3 schema + scaffolder + Pydantic — UbiquitousLanguageTerm, BoundedContextDeclaration, ContextMapEntry models; gz prd scaffolder appends three sections; src/gzkit/templates/prd.md updated; src/gzkit/schemas/{glossary_term,bounded_context,context_map_entry}.json. Allowed paths: src/gzkit/governance/domain_models.py, src/gzkit/schemas/**, src/gzkit/templates/prd.md, src/gzkit/cli/prd.py, tests/governance/domain/**, tests/cli/test_prd.py.
- [ ] OBPI-0.0.43-02: DM artifact + schema + template — New artifact type at docs/design/domain/DM-<bc-slug>.md; DomainModel Pydantic model with Aggregate / Entity / ValueObject / DomainEvent / ImplementationSurface / InboundContract / OutboundContract; src/gzkit/schemas/domain_model.json; template file; Aggregates + Implementation Surface required, rest optional. Allowed paths: src/gzkit/governance/domain_models.py, src/gzkit/schemas/domain_model.json, src/gzkit/templates/dm.md, docs/design/domain/.gitkeep, tests/governance/domain/test_dm_schema.py.
- [ ] OBPI-0.0.43-03: gz domain CLI subcommand group — init / list / status / show / regenerate verbs; structured table + --json output forms; idempotent regenerate with diff summary. Allowed paths: src/gzkit/cli/domain.py, src/gzkit/domain/**, docs/user/manpages/gz-domain*, tests/cli/test_domain.py.
- [ ] OBPI-0.0.43-04: ADR / GHI / OBPI frontmatter cascade keys + Pydantic + validators — bounded_context (required for non-pool ADR / GHI), domain_model (optional), crosses_contexts (optional), cascade_change (GHI only), bounded_context_override (OBPI rare case); schema updates; validator hooks. Allowed paths: src/gzkit/schemas/adr.json, src/gzkit/schemas/ghi.json, src/gzkit/schemas/obpi.json, src/gzkit/governance/frontmatter.py, tests/governance/test_frontmatter_cascade.py.
- [ ] OBPI-0.0.43-05: Ledger event schemas + emit paths — bounded_context_{created,renamed,retired}, glossary_term_{added,revised}, context_map_updated, domain_model_{created,revised}, legacy_mapping_ratified, cascade_reconciled, cascade_debt_acknowledged, cascade_import_bypass, bounded_context_pending_ratification. Allowed paths: src/gzkit/ledger/events.py, src/gzkit/ledger/schemas/**, tests/ledger/test_domain_events.py.
- [ ] OBPI-0.0.43-06: gz validate --domain-cascade + --domain-views-fresh + wire into gz check — Cascade integrity validator (BC resolution, glossary marker resolution, context-map entry presence for cross-context ADRs); freshness validator for Layer-3 derived views; both added to gz check default pipeline. Allowed paths: src/gzkit/governance/trust_audits.py (domain cascade scope), src/gzkit/cli/validate.py, src/gzkit/cli/check.py, tests/governance/test_domain_cascade_validator.py.
- [ ] OBPI-0.0.43-07: Legacy mapping schema + LLM-as-judge classification + ratification ceremony — LegacyAdrBcMapping Pydantic; classification driver walks existing ~49 ADRs + ~118 pool entries + completed OBPIs; output to legacy-adr-bc-mapping.yaml.draft; ratification ceremony (operator review, corrections, accept); final file at docs/design/domain/legacy-adr-bc-mapping.yaml; validator dual-mode. Allowed paths: src/gzkit/governance/legacy_mapping.py, src/gzkit/schemas/legacy_mapping.json, docs/design/domain/legacy-adr-bc-mapping.yaml.draft (eventual), docs/design/domain/legacy-adr-bc-mapping.yaml (eventual), tests/governance/test_legacy_mapping.py.
- [ ] OBPI-0.0.43-08: gz-domain-enumerate + gz-domain-model skills (canonical + mirrors) — Two new skills authored at .gzkit/skills/gz-domain-enumerate/ and .gzkit/skills/gz-domain-model/; both follow gz-design conversational shape; both opus-tier; sync through gz agent sync control-surfaces to .claude/skills/ and .agents/skills/. Allowed paths: .gzkit/skills/gz-domain-enumerate/**, .gzkit/skills/gz-domain-model/**, .claude/skills/gz-domain-{enumerate,model}/** (synced), .agents/skills/gz-domain-{enumerate,model}/** (synced), .gzkit/manifest.json.
- [ ] OBPI-0.0.43-09: Existing-skill extensions (gz-prd, gz-design, gz-adr-evaluate, gz-adr-closeout-ceremony, gz-adr-audit) — gz-prd scaffolds three new PRD sections; gz-design adds pre-flight BC question + new-BC / multi-BC sub-dialogues; gz-adr-evaluate adds cascade-compliance scoring dimension; gz-adr-closeout-ceremony adds mini-Gate-5 cascade reconciliation; gz-adr-audit adds cascade integrity audit section. All version bumps + sync. Allowed paths: .gzkit/skills/gz-prd/SKILL.md, .gzkit/skills/gz-design/SKILL.md, .gzkit/skills/gz-adr-evaluate/SKILL.md, .gzkit/skills/gz-adr-closeout-ceremony/SKILL.md, .gzkit/skills/gz-adr-audit/SKILL.md, mirrors (synced).
- [ ] OBPI-0.0.43-10: GHI workflow extensions (ghi-author, ghi-close, ghi-triage) — ghi-author requires bounded_context frontmatter + cascade-change flag; ghi-close runs mini-Gate-5 cascade reconciliation; ghi-triage groups by BC + cascade-change priority tier. All version bumps + sync. Allowed paths: .gzkit/skills/ghi-author/SKILL.md, .gzkit/skills/ghi-close/SKILL.md, .gzkit/skills/ghi-triage/SKILL.md, mirrors (synced), src/gzkit/governance/ghi.py (frontmatter requirements).
- [ ] OBPI-0.0.43-11: OBPI pipeline verify-stage AST cross-context import enforcer — Static AST analysis of Python source against DM Implementation Surface declarations; cross-context imports without context-map entry fail-closed during gz obpi pipeline verify stage; # cascade-allowed: <reason> inline marker honored with cascade_import_bypass ledger event; false-positive rate measured on existing corpus, reported in evidence (must be <5%). Allowed paths: src/gzkit/governance/cascade_import_check.py, src/gzkit/pipeline/verify.py, tests/governance/test_cascade_import_check.py.
- [ ] OBPI-0.0.43-12: Documentation cross-coverage — runbooks (docs/user/runbook.md, docs/governance/governance_runbook.md), manpages (gz domain *), governance docs (docs/governance/domain-cascade.md authoring the cascade doctrine), agent contract rationale appendix. Allowed paths: docs/user/runbook.md, docs/governance/governance_runbook.md, docs/user/manpages/gz-domain*, docs/governance/domain-cascade.md, docs/governance/agent-contract-rationale.md (appendix).
- [ ] OBPI-0.0.43-13: PRD-GZKIT-1.0.0 amendment with discovered BC list — First-cascade-authoring exercise; populates PRD § 2.1 / 2.2 / 2.3 from OBPI-07 classification ratification; PRD semver lifts to 0.4 (Draft - DDD Domain Cascade integrated); ledger events emitted for each BC introduced. Allowed paths: docs/design/prd/PRD-GZKIT-1.0.0.md.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-05-11T16:20:49.017817*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.43

### Q: What is the title of this ADR?

**A:** DDD Domain Cascade

### Q: What is the semantic version?

**A:** 0.0.43

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit currently lacks an explicit pre-Gate-1 link from PRD intent through to ADR decision that captures the three core artifacts of Domain-Driven Design: shared vocabulary, bounded contexts, and documented inter-context contracts. The cascade is implicit today — PRDs describe project context, ADRs make architectural decisions, OBPIs decompose implementation — but there is no mechanical surface enforcing that ADRs land within a named bounded context, no canonical glossary that ADR / GHI / OBPI prose resolves against, and no context map declaring how bounded contexts integrate. The consequence is what Evans (2003) named *model integrity collapse*: agents and operators reach for terms like 'change', 'user', 'context', 'event' across artifacts with subtly different meanings depending on the BC being implicitly assumed, and no validator catches the drift. In agentic SDLC the problem is acute: a single ADR conversation can span minutes; a fresh agent session inherits no shared vocabulary; same-token-different-meaning collisions become silent and accumulate across the artifact graph.

The cascade this ADR codifies is *not* a foreign methodology. gzkit's foundation / feature kinds already approximate Evans's bounded-context distinction; lane (lite / heavy) approximates context-map relationship semantics; attestation receipts and ledger events already capture cross-context provenance. The decision here is to formalize what gzkit implicitly does — naming the structure that is already present and making it mechanically enforceable. The operator's 'so close to using DDD already' framing surfaced during design dialogue is the rationale anchor: this ADR moves implicit into explicit, not foreign into native.

The shakiest condition surfaced during Tier-2 WWHTBT analysis is the AST cross-context import enforcer's false-positive rate on the existing gzkit corpus. Python's import semantics (lazy imports, conditional imports, `importlib`) historically defeat static analysis; if the enforcer flags >5% of legitimate code patterns, operators will route around it via inline bypass comments and the enforcement collapses. OBPI-11 is scoped explicitly against this risk: static AST analysis with a documented exception inline-marker (`# cascade-allowed: <reason>` emitting a ledger event), not runtime enforcement. Runtime cross-context import blocking is deferred to a named future ADR (ADR-0.0.46-cross-context-import-runtime-block) so the foundation cascade can land without coupling to a higher-risk technical commitment.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Codify a three-layer domain cascade with strict source-of-truth discipline and binding Gate-1 enforcement.

**Layer 1 (canon) — PRD strategic surface.** PRDs gain three new sections after `## 2. Overview`:

- `## 2.1 Ubiquitous Language` — project-wide and per-BC glossary. YAML-renderable entries: `term`, `scope` (cross-cutting | <bc-slug>), `definition`, `provenance` (ADR refs that codified or refined the term).
- `## 2.2 Bounded Contexts` — BC enumeration. Per BC: `slug`, `purpose`, `owner_persona`, `lifecycle_state` (active | deprecated | retired), `dm_ref`, `introduced_in` (PRD or ADR id).
- `## 2.3 Context Map` — inter-BC relationships. Per entry: `from`, `to`, `type` (Evans-7 + Vernon Partnership + Big-Ball-of-Mud anti-pattern), `description` (operator-authored prose ≥10 words grounding the label in this project's actual semantics).

**Layer 1 (canon) — DM tactical surface.** New artifact type at `docs/design/domain/DM-<bc-slug>.md` — one per BC, never per PRD. Required sections: `## Identity`, `## Glossary Specializations`, `## Aggregates` (≥1), `## Implementation Surface`, `## Inbound Contracts`, `## Outbound Contracts`. Optional: `## Entities`, `## Value Objects`, `## Domain Events`, `## Open Questions`. `## Decision History` is auto-populated from ADR `bounded_context:` frontmatter by `gz domain regenerate` (Layer-3-within-Layer-1 carve-out, validator-checked for staleness).

**Layer 3 (derived) — navigation views.** Three flat-file readable surfaces under `docs/design/domain/`: `glossary.md`, `bounded-contexts.md`, `context-map.md`. Regenerated by `gz domain regenerate` from PRD § 2.1 / 2.2 / 2.3 + all DMs. **Never source-of-truth, never hand-edited.** Freshness fail-closed by `gz validate --domain-views-fresh` (parallels `--adr-status-fresh` from GHI #322).

**ADR / GHI / OBPI frontmatter cascade keys:**

- ADR (non-pool): `bounded_context:` required (string or list); `domain_model:` optional; `crosses_contexts:` optional.
- ADR (pool): same as above but all optional.
- GHI: `bounded_context:` required; `crosses_contexts:` optional; `cascade_change: true|false` for triage prioritization.
- OBPI: inherits parent ADR; `bounded_context_override:` for rare sub-BC scoping.

**Marker convention (binding precedent for all future gzkit-namespace categories).** Glossary terms referenced in prose use backticked `gz-glossary-<term>` form. Validator rule (stateless, three-tier):

1. Backticked token `gz-glossary-<term>` AND not a registered skill name → glossary reference, must resolve, fail-closed at Gate 1.
2. Backticked token matches registered skill name (`gz-design`, `ghi-author`, etc.) → skill reference, no glossary check.
3. Anything else → code identifier, no glossary check.

Future gzkit-namespace categories follow the `gz-<category>-<entity>` pattern. No single-letter discriminators (rejected `gzd-`, `gzi-`, `gzr-` family for opacity and scaling cost). Verbosity is bounded; clarity is unbounded.

**Three-point pre-Gate-1 enforcement:**

1. *Authoring time* — `gz plan create --bounded-context X` refuses unknown BC with exit 3 (operator gets error before file exists).
2. *Document validation* — `gz validate --domain-cascade` runs cascade integrity check on every CI / local pass.
3. *Gate 1 audit* — `gz adr audit-check` reads frontmatter, verifies cascade integrity, fail-closed on unresolved.

Block-after-backfill: legacy ADRs run through hybrid migration (frontmatter for new + classification index for legacy) before fail-closed mode activates corpus-wide.

**Cascade-touchpoint contract — slow gear / fast gear.** Slow gear (populate): `gz-prd`, new `gz-domain-enumerate` skill, new `gz-domain-model` skill, mechanical `gz domain regenerate`. Fast gear (reference + enforce): `gz-design` (pre-flight BC question, block on unknown), `gz-obpi-pipeline` verify stage (AST cross-context import enforcer), `ghi-author` (required BC frontmatter + cascade-change flag), `ghi-close` (mini-Gate-5 reconciliation), `ghi-triage` (BC-grouped rendering + cascade-change priority tier), `gz-adr-evaluate` (cascade-compliance scoring dimension), `gz-adr-closeout-ceremony` (mini-Gate-5 cascade reconciliation), `gz-adr-audit` (cascade integrity audit section). **The cascade is populated lazily, referenced eagerly, enforced at gates** — the translation that lets a 20-year-old methodology fit an agentic SDD loop.

**2am operator affordances** (added during interview Tier 2.5):

- `gz validate --domain-cascade --accept-undefined-term <term> --accept-reason <REASON>` — emergency bypass for hotfix prose using yet-to-be-glossaried term; emits `cascade_debt_acknowledged` ledger event.
- `# cascade-allowed: <reason>` inline marker in Python source — AST enforcer respects; emits `cascade_import_bypass` ledger event.
- `gz validate --domain-cascade --skip-legacy` — emergency triage when legacy-mapping YAML has typo blocking everything.
- `gz obpi complete --bc-introduced <slug> --bc-introduced-reason <REASON>` — operator introduces a new BC during implementation but PRD update is blocked; emits `bounded_context_pending_ratification` ledger event, PRD update happens async.
- Every cascade validator failure carries a `Resolve:` line naming the path to fix.
- `gz domain regenerate --check` dry-run mode; atomic write-temp-then-rename; views written under `.gzkit/state/storybook-views-prev/` for one-shot rollback.

**Backfill — hybrid one-shot, agent-classified, operator-attested.** OBPI-07 implements: LLM-as-judge classification walks each of the ~49 existing canonical ADRs + ~118 pool entries + completed OBPIs, drafting a `bounded_context:` mapping. Output lands at `docs/design/domain/legacy-adr-bc-mapping.yaml.draft`. Operator reviews, corrects misclassifications, ratifies. Final file at `docs/design/domain/legacy-adr-bc-mapping.yaml`. Validator dual-mode: checks frontmatter first, falls back to legacy mapping for legacy IDs. One-way promotion allowed (index → frontmatter on next modification, never reverse). The existing corpus is primary evidence of what BCs gzkit already has — classification is *extraction from canon, not invention*. The bootstrap BC list for PRD § 2.2 surfaces from the classification, not from a blank page.

**Ledger event surface (Layer-2 truth):**

- `bounded_context_created`, `bounded_context_renamed`, `bounded_context_retired`
- `glossary_term_added`, `glossary_term_revised`
- `context_map_updated` (action: added | revised | removed)
- `domain_model_created`, `domain_model_revised`
- `legacy_mapping_ratified` (count, ratified_by)
- `cascade_reconciled` (closing_artifact, changes[]) — emitted at closeout
- `cascade_debt_acknowledged`, `cascade_import_bypass`, `bounded_context_pending_ratification` — 2am-affordance events

**Reversibility assessment.** Predominantly **one-way door**. One-way: PRD § 2.1 / 2.2 / 2.3 section schema, BC slugs once referenced by ADRs / GHIs, ledger event types, marker convention `gz-glossary-<term>`. Two-way: skill extensions, scorecard dimensions, validator severity (warning ↔ fail-closed), Evans-vocabulary enum extensions (additive). 12-month reversal cost: very high (corpus-wide migration with operator attestation). Foundation-heavy ceremony is appropriate.

**Kind: foundation.** Identity-shaping — changes what gzkit IS (cascade-governed) rather than producing a new release-carrying capability. Per ADR-0.0.18 taxonomy doctrine.

**Lane: heavy.** New CLI verbs (`gz domain *` subgroup), new validator scopes (`--domain-cascade`, `--domain-views-fresh`), new directory contract (`docs/design/domain/`), new schemas (BoundedContextDeclaration, DomainModel, ContextMapEntry, GlossaryTerm, LegacyAdrBcMapping), new artifact type (DM), required frontmatter on three artifact types (ADR / GHI / OBPI), new ledger event types. External-contract surface across the board.

**Sensitivity: absent.** No security surface.

### Q: What good things result from this decision? List benefits.

**A:** 1. gzkit gains a mechanical pre-Gate-1 link from PRD intent through ADR decision that makes domain modeling enforceable rather than aspirational. Three-point Gate-1 enforcement (authoring-time, validation, audit) makes laziness mechanically impossible to slip into never-populated.
2. The cascade becomes the navigation taxonomy for governance work writ large — ADRs, GHIs, OBPIs all anchor to bounded contexts. Triage and review can slice by domain rather than chronology, which becomes more valuable as the artifact graph grows.
3. The 'so close to using DDD already' insight is operationalized — gzkit's foundation / feature kinds already approximate bounded contexts; lane semantics already approximate context-map relationships; this ADR formalizes what is present, lowering doctrine-imposition cost.
4. Slow-gear / fast-gear discipline maps directly to agentic SDLC reality: the cascade is populated lazily when conversations reveal missing structure, referenced eagerly during ADR / OBPI / GHI authoring, and enforced at gates. This is the translation that lets DDD (2003) fit agentic SDD without front-loading modeling ceremony.
5. The marker convention `gz-glossary-<term>` is a stateless, three-tier validator rule with no skill-registry tiebreaker dependency. Future gzkit-namespace categories inherit the `gz-<category>-<entity>` pattern as binding precedent. No proliferating single-letter discriminator family.
6. Layer separation is mechanically enforced: PRD § 2.1 / 2.2 / 2.3 and DM files are Layer-1 canon; flat-file views are Layer-3 derived; `gz domain regenerate` is the only path from canon to view; `gz validate --domain-views-fresh` is the freshness backstop. Source-of-truth ambiguity cannot accumulate silently.
7. The Evans-vocabulary enum (shared-kernel, customer-supplier, conformist, anticorruption-layer, separate-ways, open-host-service, published-language, plus Vernon's partnership and the big-ball-of-mud anti-pattern recognition) is canonical translatable vocabulary with required prose grounding. Labels alone are insufficient; the grounding sentence pins the label to project semantics.
8. The 2am operator affordances (`--accept-undefined-term`, `# cascade-allowed:`, `--skip-legacy`, `--bc-introduced`, `Resolve:` line in every error) match gzkit's existing fail-closed-with-escape-hatches pattern (`--accept-uncovered`, `--dry-run`, storybook `--accept-stale-storybook`). Operational continuity preserved without weakening the doctrine.
9. The hybrid backfill strategy bounds migration work to a single OBPI (OBPI-07) with agent-drafted classification + operator attestation. Completed ADRs are not reopened. The bootstrap BC list for PRD § 2.2 emerges from classification — the existing corpus is primary evidence, not a blank-page authoring task.
10. The AST cross-context import enforcer (OBPI-11) gives Python-level mechanical enforcement of context-map declarations. Cross-context imports without a context-map entry fail-closed during `gz obpi pipeline` verify stage. This is the strongest enforcement layer: compiler-style, cannot lie. Runtime enforcement deferred to a named future ADR to keep this ADR's risk envelope bounded.
11. GHIs gain a first-class place in the cascade. `ghi-author` requires `bounded_context:`; `ghi-close` runs mini-Gate-5 cascade reconciliation; `ghi-triage` groups by BC and prioritizes cascade-change-labeled issues. GHIs are the highest-frequency governance surface; cascade enforcement here keeps the cascade true between ADR-scale slow-gear turns.
12. Reversibility is honest: one-way doors are named explicitly (PRD section schema, BC slugs, ledger event types, marker convention). Foundation-heavy ceremony is justified by the corpus-wide reversal cost.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **Adds significant surface area to gzkit.** Two new skills (`gz-domain-enumerate`, `gz-domain-model`), nine existing-skill extensions (`gz-prd`, `gz-design`, `gz-adr-evaluate`, `gz-adr-closeout-ceremony`, `gz-adr-audit`, `ghi-author`, `ghi-close`, `ghi-triage`, `gz-obpi-pipeline`), new CLI subcommand group (`gz domain`), two new validator scopes, new artifact type (DM), new schemas, new ledger event types, new frontmatter requirements on three artifact types. The operator explicitly accepted this growth ('I know the surface of gzkit grows, but I am so close to using DDD already that it makes sense now') — the cost is acknowledged, not denied.
2. **Pre-mortem failure mode — glossary inflation.** PRD § 2.1 grows past comprehension (>200 terms); agents cannot reliably scan it; backtick markers become technically valid but semantically noisy; cascade is 'compliant' but no longer aids comprehension. Mitigation: glossary growth boundary doctrine deferred to a future ADR (named in Forced Downstream Commitments) when corpus warrants — likely when § 2.1 crosses ~100 terms.
3. **Pre-mortem failure mode — legacy mapping ratification stalls.** LLM-as-judge classification produces ~70% accuracy; operator never finds time to ratify the remaining 30%; validator runs in warning mode indefinitely; cascade is half-true. Mitigation: OBPI-07 requires operator ratification as the completion criterion, not classification draft. Closeout is gated on full ratification. If classification accuracy <70% during OBPI-07 execution, abandon the LLM step and author the mapping directly.
4. **Pre-mortem failure mode — AST enforcer false positives.** Python's import semantics (lazy imports, conditional imports, `importlib.import_module`) defeat naive AST analysis; enforcer produces enough false positives that operators add `# cascade-allowed:` comments liberally; the enforcer becomes ignored. Mitigation: OBPI-11 scoped to static AST analysis with documented exception inline-marker; runtime enforcement deferred to ADR-0.0.46. WWHTBT shakiest condition: false-positive rate <5% on existing corpus must be measured during OBPI-11 implementation and reported in evidence.
5. **Pre-mortem failure mode — BC churn outpaces ledger events.** Bounded contexts get renamed / split as gzkit evolves; ledger event types for renames exist but downstream artifacts (legacy mapping YAML, 100+ ADR frontmatters) don't auto-track; orphan BC references accumulate. Mitigation: `gz validate --domain-cascade` catches orphan BC references on every run; rename ceremony documented as part of OBPI-04 frontmatter validators.
6. **Pre-mortem failure mode — closeout reconciliation becomes rubber-stamp.** Operator clicks through cascade check at Gate 5 without engaging; introduced terms / contracts during implementation are never propagated; cascade is 'true at closeout' by attestation but false by content. Mitigation: closeout cascade reconciliation requires named diff (terms added / contracts changed / BCs touched); empty diff with non-trivial implementation is a flag for operator review.
7. **Pre-mortem failure mode — marker convention fatigue.** Operators find `gz-glossary-<term>` too verbose; write `change` in prose instead; validator can't see them; glossary terms drift unenforced. Mitigation: marker convention is mechanically required only at gate boundaries (ADR / GHI promotion, Gate-1 audit). Day-to-day prose can be loose; gate enforcement forces the marker discipline where it matters.
8. **Assumption-surfacing risk — operators may prefer chronological browsing.** The cascade introduces BC-grouped navigation as the new primary taxonomy. If operators don't engage with BC-grouped views, the navigation value of the cascade collapses to its enforcement value alone. Mitigation: `gz domain show` and `gz domain list` are additive surfaces; chronological views (existing `gz status`, `gz adr status`) remain unchanged. Operators can ignore BC-grouped views without breaking anything.
9. **Assumption-surfacing risk — 13 OBPIs may be over-fragmented.** Some OBPIs (04 frontmatter + 05 ledger events + 06 validator wiring) are tightly coupled; closeout overhead may be disproportionate to implementation effort. Mitigation: keep 13 OBPIs for clean review boundaries; reconciliation pass after first half of OBPIs lands may merge if coupling is excessive.
10. **Assumption-surfacing risk — foundation-kind vs feature-kind ambiguity.** Domain modeling produces a user-visible capability (`gz domain show`), arguably feature-kind. Decision: foundation per ADR-0.0.18 (identity-shaping wins over capability-producing when ambiguous). Documented tension; not a blocker.
11. **Scope-minimization tension.** Minimal version (just `bounded_context:` frontmatter + Gate-1 validator) delivers ~20% of current scope at ~5x less effort. Operator overrode with 'EVERYTHING in scope for 0.0.43.' Justification: foundation cost-of-incompleteness premium — partial cascade is half a cascade is no cascade. Documented as scope override, not scope creep.
12. **Constraint-archaeology surface — Evans vocabulary kept by assumption.** Could rename to gzkit-native vocabulary; chose to keep canonical for translatability. Cost: some readers may find Evans's mid-2000s enterprise-Java terms ('Anticorruption Layer', 'Open Host Service', 'Conformist') alienating. Bet: gzkit's audience is engineering-literate; canonical vocabulary is worth preserving.
13. **Reversibility cost.** Predominantly one-way door. 12-month reversal would require corpus-wide migration with operator attestation. The ADR ceremony level (foundation, heavy, full evaluation scorecard, full OBPI decomposition, human attestation at every OBPI closeout) is calibrated to this irreversibility.
14. **PRD-GZKIT-1.0.0 amendment required.** OBPI-13 amends PRD § 2.1 / 2.2 / 2.3 with the discovered BC list from legacy classification. This is the first-cascade-authoring exercise. PRD is currently semver 0.3 (Draft); the amendment lifts it to 0.4 (Draft - DDD Domain Cascade integrated).

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. OBPI-0.0.43-01: PRD § 2.1 / 2.2 / 2.3 schema + scaffolder + Pydantic — UbiquitousLanguageTerm, BoundedContextDeclaration, ContextMapEntry models; gz prd scaffolder appends three sections; src/gzkit/templates/prd.md updated; src/gzkit/schemas/{glossary_term,bounded_context,context_map_entry}.json. Allowed paths: src/gzkit/governance/domain_models.py, src/gzkit/schemas/**, src/gzkit/templates/prd.md, src/gzkit/cli/prd.py, tests/governance/domain/**, tests/cli/test_prd.py.

2. OBPI-0.0.43-02: DM artifact + schema + template — New artifact type at docs/design/domain/DM-<bc-slug>.md; DomainModel Pydantic model with Aggregate / Entity / ValueObject / DomainEvent / ImplementationSurface / InboundContract / OutboundContract; src/gzkit/schemas/domain_model.json; template file; Aggregates + Implementation Surface required, rest optional. Allowed paths: src/gzkit/governance/domain_models.py, src/gzkit/schemas/domain_model.json, src/gzkit/templates/dm.md, docs/design/domain/.gitkeep, tests/governance/domain/test_dm_schema.py.

3. OBPI-0.0.43-03: gz domain CLI subcommand group — init / list / status / show / regenerate verbs; structured table + --json output forms; idempotent regenerate with diff summary. Allowed paths: src/gzkit/cli/domain.py, src/gzkit/domain/**, docs/user/manpages/gz-domain*, tests/cli/test_domain.py.

4. OBPI-0.0.43-04: ADR / GHI / OBPI frontmatter cascade keys + Pydantic + validators — bounded_context (required for non-pool ADR / GHI), domain_model (optional), crosses_contexts (optional), cascade_change (GHI only), bounded_context_override (OBPI rare case); schema updates; validator hooks. Allowed paths: src/gzkit/schemas/adr.json, src/gzkit/schemas/ghi.json, src/gzkit/schemas/obpi.json, src/gzkit/governance/frontmatter.py, tests/governance/test_frontmatter_cascade.py.

5. OBPI-0.0.43-05: Ledger event schemas + emit paths — bounded_context_{created,renamed,retired}, glossary_term_{added,revised}, context_map_updated, domain_model_{created,revised}, legacy_mapping_ratified, cascade_reconciled, cascade_debt_acknowledged, cascade_import_bypass, bounded_context_pending_ratification. Allowed paths: src/gzkit/ledger/events.py, src/gzkit/ledger/schemas/**, tests/ledger/test_domain_events.py.

6. OBPI-0.0.43-06: gz validate --domain-cascade + --domain-views-fresh + wire into gz check — Cascade integrity validator (BC resolution, glossary marker resolution, context-map entry presence for cross-context ADRs); freshness validator for Layer-3 derived views; both added to gz check default pipeline. Allowed paths: src/gzkit/governance/trust_audits.py (domain cascade scope), src/gzkit/cli/validate.py, src/gzkit/cli/check.py, tests/governance/test_domain_cascade_validator.py.

7. OBPI-0.0.43-07: Legacy mapping schema + LLM-as-judge classification + ratification ceremony — LegacyAdrBcMapping Pydantic; classification driver walks existing ~49 ADRs + ~118 pool entries + completed OBPIs; output to legacy-adr-bc-mapping.yaml.draft; ratification ceremony (operator review, corrections, accept); final file at docs/design/domain/legacy-adr-bc-mapping.yaml; validator dual-mode. Allowed paths: src/gzkit/governance/legacy_mapping.py, src/gzkit/schemas/legacy_mapping.json, docs/design/domain/legacy-adr-bc-mapping.yaml.draft (eventual), docs/design/domain/legacy-adr-bc-mapping.yaml (eventual), tests/governance/test_legacy_mapping.py.

8. OBPI-0.0.43-08: gz-domain-enumerate + gz-domain-model skills (canonical + mirrors) — Two new skills authored at .gzkit/skills/gz-domain-enumerate/ and .gzkit/skills/gz-domain-model/; both follow gz-design conversational shape; both opus-tier; sync through gz agent sync control-surfaces to .claude/skills/ and .agents/skills/. Allowed paths: .gzkit/skills/gz-domain-enumerate/**, .gzkit/skills/gz-domain-model/**, .claude/skills/gz-domain-{enumerate,model}/** (synced), .agents/skills/gz-domain-{enumerate,model}/** (synced), .gzkit/manifest.json.

9. OBPI-0.0.43-09: Existing-skill extensions (gz-prd, gz-design, gz-adr-evaluate, gz-adr-closeout-ceremony, gz-adr-audit) — gz-prd scaffolds three new PRD sections; gz-design adds pre-flight BC question + new-BC / multi-BC sub-dialogues; gz-adr-evaluate adds cascade-compliance scoring dimension; gz-adr-closeout-ceremony adds mini-Gate-5 cascade reconciliation; gz-adr-audit adds cascade integrity audit section. All version bumps + sync. Allowed paths: .gzkit/skills/gz-prd/SKILL.md, .gzkit/skills/gz-design/SKILL.md, .gzkit/skills/gz-adr-evaluate/SKILL.md, .gzkit/skills/gz-adr-closeout-ceremony/SKILL.md, .gzkit/skills/gz-adr-audit/SKILL.md, mirrors (synced).

10. OBPI-0.0.43-10: GHI workflow extensions (ghi-author, ghi-close, ghi-triage) — ghi-author requires bounded_context frontmatter + cascade-change flag; ghi-close runs mini-Gate-5 cascade reconciliation; ghi-triage groups by BC + cascade-change priority tier. All version bumps + sync. Allowed paths: .gzkit/skills/ghi-author/SKILL.md, .gzkit/skills/ghi-close/SKILL.md, .gzkit/skills/ghi-triage/SKILL.md, mirrors (synced), src/gzkit/governance/ghi.py (frontmatter requirements).

11. OBPI-0.0.43-11: OBPI pipeline verify-stage AST cross-context import enforcer — Static AST analysis of Python source against DM Implementation Surface declarations; cross-context imports without context-map entry fail-closed during gz obpi pipeline verify stage; # cascade-allowed: <reason> inline marker honored with cascade_import_bypass ledger event; false-positive rate measured on existing corpus, reported in evidence (must be <5%). Allowed paths: src/gzkit/governance/cascade_import_check.py, src/gzkit/pipeline/verify.py, tests/governance/test_cascade_import_check.py.

12. OBPI-0.0.43-12: Documentation cross-coverage — runbooks (docs/user/runbook.md, docs/governance/governance_runbook.md), manpages (gz domain *), governance docs (docs/governance/domain-cascade.md authoring the cascade doctrine), agent contract rationale appendix. Allowed paths: docs/user/runbook.md, docs/governance/governance_runbook.md, docs/user/manpages/gz-domain*, docs/governance/domain-cascade.md, docs/governance/agent-contract-rationale.md (appendix).

13. OBPI-0.0.43-13: PRD-GZKIT-1.0.0 amendment with discovered BC list — First-cascade-authoring exercise; populates PRD § 2.1 / 2.2 / 2.3 from OBPI-07 classification ratification; PRD semver lifts to 0.4 (Draft - DDD Domain Cascade integrated); ledger events emitted for each BC introduced. Allowed paths: docs/design/prd/PRD-GZKIT-1.0.0.md.

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Option A alone — new DM artifact type without PRD-level BC enumeration.** REJECTED during design dialogue: misses the project-wide BC enumeration that operators and agents need to navigate the artifact graph. Tactical DDD without strategic-level structure is half a cascade.

2. **Option B alone — extend PRD with three sections, no separate DM artifact.** REJECTED during design dialogue: PRDs balloon for larger projects; mixing strategic intent with tactical structure conflates concerns; multiple PRDs cannot share BC tactical models. Strategic-only-in-PRD breaks the moment a second PRD lands or a BC's tactical depth grows past prose-section size.

3. **Option C alone — three orthogonal files (glossary.md / bounded-contexts.md / context-map.md) as source-of-truth.** REJECTED during design dialogue: three independent canon homes = three drift surfaces; no single source-of-truth; matches the transcript's 'three artifacts' framing literally but loses the cascade discipline. Operator framing was 'three artifacts as one cascade,' not 'three independent files.'

4. **Single 'gz ddd' verb prefix instead of 'gz domain'.** REJECTED during design dialogue: too tied to one methodology by name. 'domain' is the gzkit-native generalization — DDD-derived but not DDD-bound. Future cascade refinements can draw on patterns beyond strict Evans canon without renaming the CLI surface.

5. **Per-PRD DM file (DM-PRD-<id>-<bc>.md) instead of per-BC DM file.** REJECTED during design dialogue: couples DM granularity to PRD granularity; cannot share one BC's tactical model across multiple PRDs. Per-BC granularity is the correct abstraction level.

6. **No 'governance' sentinel — hard-skip tooling ADRs from cascade enforcement.** REJECTED during design dialogue: leaks an exception pathway that agents will reach for. 'My ADR is about tooling, not domain' becomes a reliable cascade-bypass excuse. Sentinel-as-real-BC ('governance' is enumerated in PRD § 2.2 like any other BC) preserves the universal-rule property — smallest vibing surface principle.

7. **'gzd-<term>' single-letter prefix for glossary markers instead of 'gz-glossary-<term>'.** REJECTED during design dialogue: requires learned vocabulary (what does 'gzd' mean?); doesn't self-describe; sets precedent for proliferating single-letter discriminator family ('gzi-' for invariants, 'gzr-' for receipts, 'gze-' for events). Verbosity of full-word prefix is bounded; clarity is unbounded. Binding precedent set: future gzkit-namespace categories follow 'gz-<category>-<entity>' pattern.

8. **NLP / stemmed-match validator for glossary term resolution.** REJECTED during design dialogue: high false-positive rate; brittle; common words ('change' as 'code change') collide with domain terms ('change' as DOM-mutation-on-customer-site). The marker convention with explicit prefix opt-in is the smallest vibing surface for the validator to enforce.

9. **Per-document glossary-terms-used frontmatter list.** REJECTED during design dialogue: highest operator burden; cleanest mechanical surface but doesn't catch undeclared uses. Backtick marker convention with namespace prefix dominates this on every axis except explicit declaration.

10. **Simplified Context Map relationship vocabulary (consumes / produces / shares / isolated, four-value enum).** REJECTED during design dialogue: strips DDD nomenclature to bare semantic relationships; lossy. The Evans labels carry decades of accumulated meaning; throwing them away costs translatability for marginal authoring-burden savings. Decision: keep Evans-7 + Vernon Partnership + Big-Ball-of-Mud anti-pattern with required prose grounding (label alone is insufficient; grounding sentence pins the label to project semantics).

11. **Eager migration — walk every existing ADR, write bounded_context frontmatter retroactively.** REJECTED: reopens closeout-attested ADRs, violating closeout invariant. Existing ADRs are attested artifacts; retroactive frontmatter mutation invalidates prior attestation.

12. **Lazy migration — frontmatter required only when ADR is touched next.** REJECTED: cascade remains half-true indefinitely; half the corpus is shadow-state. Validator runs in warning mode for years; cascade compliance becomes aspirational.

13. **Defer the AST cross-context import enforcer to 0.0.44+.** Considered after Tier-2 WWHTBT surfaced the false-positive rate as the shakiest condition. Operator explicitly OVERRODE: 'EVERYTHING about this move should be in-scope for 0.0.43 - cascade and enforcer.' Documented as scope override, not scope creep. Justification: foundation cost-of-incompleteness premium; partial enforcement is no enforcement once operators learn to route around it. OBPI-11 is scoped to static analysis with documented exception inline-marker; runtime enforcement deferred to a named future ADR (ADR-0.0.46-cross-context-import-runtime-block).

14. **Pool ADR (ADR-pool.ddd-domain-cascade) instead of canonical foundation ADR.** REJECTED by operator: 'this is not pool, this is straight to foundation.' Pool was the initial recommendation; operator-overridden. Foundation reasoning: pre-1.0.0 boundary work; identity-shaping; the architecture memo explicitly calls for locking foundations before 1.0.

15. **One combined gz-domain skill instead of two (gz-domain-enumerate + gz-domain-model).** REJECTED during design dialogue: two operator moments warrant two skills per existing gzkit pattern (parallels gz-design + gz-plan + gz-adr-create as separate skills for separate moments). Skills compose in meta-workflows — gz-design can invoke gz-domain-enumerate as a sub-dialogue when a new BC surfaces.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Option A alone — new DM artifact type without PRD-level BC enumeration.** REJECTED during design dialogue: misses the project-wide BC enumeration that operators and agents need to navigate the artifact graph. Tactical DDD without strategic-level structure is half a cascade.

2. **Option B alone — extend PRD with three sections, no separate DM artifact.** REJECTED during design dialogue: PRDs balloon for larger projects; mixing strategic intent with tactical structure conflates concerns; multiple PRDs cannot share BC tactical models. Strategic-only-in-PRD breaks the moment a second PRD lands or a BC's tactical depth grows past prose-section size.

3. **Option C alone — three orthogonal files (glossary.md / bounded-contexts.md / context-map.md) as source-of-truth.** REJECTED during design dialogue: three independent canon homes = three drift surfaces; no single source-of-truth; matches the transcript's 'three artifacts' framing literally but loses the cascade discipline. Operator framing was 'three artifacts as one cascade,' not 'three independent files.'

4. **Single 'gz ddd' verb prefix instead of 'gz domain'.** REJECTED during design dialogue: too tied to one methodology by name. 'domain' is the gzkit-native generalization — DDD-derived but not DDD-bound. Future cascade refinements can draw on patterns beyond strict Evans canon without renaming the CLI surface.

5. **Per-PRD DM file (DM-PRD-<id>-<bc>.md) instead of per-BC DM file.** REJECTED during design dialogue: couples DM granularity to PRD granularity; cannot share one BC's tactical model across multiple PRDs. Per-BC granularity is the correct abstraction level.

6. **No 'governance' sentinel — hard-skip tooling ADRs from cascade enforcement.** REJECTED during design dialogue: leaks an exception pathway that agents will reach for. 'My ADR is about tooling, not domain' becomes a reliable cascade-bypass excuse. Sentinel-as-real-BC ('governance' is enumerated in PRD § 2.2 like any other BC) preserves the universal-rule property — smallest vibing surface principle.

7. **'gzd-<term>' single-letter prefix for glossary markers instead of 'gz-glossary-<term>'.** REJECTED during design dialogue: requires learned vocabulary (what does 'gzd' mean?); doesn't self-describe; sets precedent for proliferating single-letter discriminator family ('gzi-' for invariants, 'gzr-' for receipts, 'gze-' for events). Verbosity of full-word prefix is bounded; clarity is unbounded. Binding precedent set: future gzkit-namespace categories follow 'gz-<category>-<entity>' pattern.

8. **NLP / stemmed-match validator for glossary term resolution.** REJECTED during design dialogue: high false-positive rate; brittle; common words ('change' as 'code change') collide with domain terms ('change' as DOM-mutation-on-customer-site). The marker convention with explicit prefix opt-in is the smallest vibing surface for the validator to enforce.

9. **Per-document glossary-terms-used frontmatter list.** REJECTED during design dialogue: highest operator burden; cleanest mechanical surface but doesn't catch undeclared uses. Backtick marker convention with namespace prefix dominates this on every axis except explicit declaration.

10. **Simplified Context Map relationship vocabulary (consumes / produces / shares / isolated, four-value enum).** REJECTED during design dialogue: strips DDD nomenclature to bare semantic relationships; lossy. The Evans labels carry decades of accumulated meaning; throwing them away costs translatability for marginal authoring-burden savings. Decision: keep Evans-7 + Vernon Partnership + Big-Ball-of-Mud anti-pattern with required prose grounding (label alone is insufficient; grounding sentence pins the label to project semantics).

11. **Eager migration — walk every existing ADR, write bounded_context frontmatter retroactively.** REJECTED: reopens closeout-attested ADRs, violating closeout invariant. Existing ADRs are attested artifacts; retroactive frontmatter mutation invalidates prior attestation.

12. **Lazy migration — frontmatter required only when ADR is touched next.** REJECTED: cascade remains half-true indefinitely; half the corpus is shadow-state. Validator runs in warning mode for years; cascade compliance becomes aspirational.

13. **Defer the AST cross-context import enforcer to 0.0.44+.** Considered after Tier-2 WWHTBT surfaced the false-positive rate as the shakiest condition. Operator explicitly OVERRODE: 'EVERYTHING about this move should be in-scope for 0.0.43 - cascade and enforcer.' Documented as scope override, not scope creep. Justification: foundation cost-of-incompleteness premium; partial enforcement is no enforcement once operators learn to route around it. OBPI-11 is scoped to static analysis with documented exception inline-marker; runtime enforcement deferred to a named future ADR (ADR-0.0.46-cross-context-import-runtime-block).

14. **Pool ADR (ADR-pool.ddd-domain-cascade) instead of canonical foundation ADR.** REJECTED by operator: 'this is not pool, this is straight to foundation.' Pool was the initial recommendation; operator-overridden. Foundation reasoning: pre-1.0.0 boundary work; identity-shaping; the architecture memo explicitly calls for locking foundations before 1.0.

15. **One combined gz-domain skill instead of two (gz-domain-enumerate + gz-domain-model).** REJECTED during design dialogue: two operator moments warrant two skills per existing gzkit pattern (parallels gz-design + gz-plan + gz-adr-create as separate skills for separate moments). Skills compose in meta-workflows — gz-design can invoke gz-domain-enumerate as a sub-dialogue when a new BC surfaces.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.43 | Pending | | | |
