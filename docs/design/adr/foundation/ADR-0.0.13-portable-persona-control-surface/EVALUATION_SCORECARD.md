<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.13 Evaluation Scorecard

**ADR:** ADR-0.0.13 — Portable Persona Control Surface
**Evaluator:** Claude Opus 4.6 (adversarial red-team mode)
**Date:** 2026-03-30
**Mode:** Full adversarial evaluation with --red-team

---

## Part 1: ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | The problem is well-defined: persona frames exist in gzkit but are not portable across GovZero repos. Before/after states are clear (manual vs `gz init`/`gz agent sync`). However, the ADR does not quantify the pain -- how many repos, how much manual effort, how often sync breaks. The "so what?" is implicit (portfolio-level investment leverage) rather than measured. |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decisions follow the established canon-first/vendor-mirror pattern and cite the existing rules/skills precedent explicitly (the table in Rationale is strong). Alternatives are not named or dismissed -- there is no discussion of why personas could not be a subfield of an existing surface (e.g., embedded in rules), why the vendor adapter layer is needed vs direct file copying, or why drift monitoring belongs in this ADR rather than a separate one. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Six items, each independently valuable. Removing any one leaves a visible gap. Consistent granularity. One concern: "Vendor-neutral persona loading" (item 5) overlaps significantly with "gz agent sync persona mirroring" (item 4) -- sync IS the loading mechanism for file-based vendors, so these may not be as independent as presented. |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | Six OBPIs follow a logical progression (schema -> scaffolding -> manifest/sync -> loading -> monitoring -> cross-project). Boundaries are domain-driven. Size appears reasonable. One structural concern: OBPI-03 bundles manifest schema AND sync behavior, which are arguably two distinct surfaces (schema is data, sync is engine). The decomposition scorecard calculated 6 correctly from its dimensions. |
| 5 | Lane Assignment | 10% | 1 | 0.10 | **Critical defect.** The ADR table assigns OBPI-03 as Heavy, OBPI-05 as Heavy, and OBPI-06 as Heavy. But ALL SIX briefs declare themselves as **Lite**. This is a direct contradiction between parent ADR and child briefs. Furthermore, the ADR-level lane is Heavy, yet briefs 03, 05, and 06 self-describe as Lite despite the ADR table saying Heavy. The Lite justification boilerplate in the briefs ("This OBPI remains internal to the promoted ADR implementation scope") is factually wrong for OBPIs that change CLI commands (`gz personas drift`), manifest schema, and cross-project contracts. OBPI-01 (schema spec) and OBPI-04 (vendor adapters) are also arguably Heavy since they define external contracts consumed by other projects. |
| 6 | Scope Discipline | 10% | 2 | 0.20 | The Critical Constraint section provides one important non-goal (no gzkit-specific content imposed on other projects). The Anti-Pattern Warning is useful. However, there is no explicit non-goals section. Missing non-goals include: persona runtime evaluation (only storage/loading), persona versioning, persona inheritance between projects, persona composition conflict resolution, and backward compatibility policy. Scope creep is likely toward runtime persona activation and behavioral enforcement, which the drift monitoring OBPI already flirts with. |
| 7 | Evidence Requirements | 10% | 2 | 0.20 | The ADR names test files (`tests/test_persona_portability.py`) and BDD features (`features/persona_sync.feature`), which is good. But the Evidence section is generic -- it lists artifact classes without specifying what commands prove each OBPI is done. The Completion Checklist uses "Test output" and "Sync output" as evidence, which are vague. No specific `gz` commands are listed for verification beyond the CLI section's usage examples. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | Strong alignment with the existing control surface pattern. The Rationale table showing Rules/Skills/Schemas/Personas in parallel is excellent. Integration points list specific module paths (`src/gzkit/sync_surfaces.py`, `src/gzkit/commands/init.py`, `.gzkit/manifest.json`). The sync_surfaces.py module currently has no persona support (confirmed by code search), so the integration point is real. Anti-patterns are named clearly. |

**WEIGHTED TOTAL: 2.60 / 4.0**

**Threshold Assessment: CONDITIONAL GO** (2.5-3.0 range)

---

## Part 2: OBPI-Level Scores

All six briefs are scaffolded templates with no authored content. Scored as-is.

### OBPI-0.0.13-01 — Portable Persona Schema

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| A: Independence | 3 | First in chain, depends only on ADR-0.0.11 and ADR-0.0.12 (declared at ADR level). Could start independently. |
| B: Testability | 1 | Objective is "TBD". Acceptance criteria are template placeholders. No verification commands specified. |
| C: Value | 4 | Removing the schema specification collapses the entire ADR -- everything downstream depends on it. |
| D: Size | 3 | Schema specification is a reasonable 1-3 day unit. |
| E: Clarity | 1 | Objective is "TBD". Requirements are "First constraint" / "Second constraint". Allowed paths are "src/module/". Two different agents would produce wildly different implementations. |
| **Average** | **2.4** | |

### OBPI-0.0.13-02 — gz init Persona Scaffolding

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| A: Independence | 2 | Depends on OBPI-01 (schema) but this dependency is not declared anywhere in the brief. |
| B: Testability | 1 | Template placeholder. No commands. |
| C: Value | 3 | Removing init scaffolding means manual persona setup per-project, defeating portability. |
| D: Size | 3 | Adding a directory to `gz init` is a well-bounded unit. |
| E: Clarity | 1 | "TBD" objective. Template paths and requirements. |
| **Average** | **2.0** | |

### OBPI-0.0.13-03 — Manifest Schema and Persona Sync

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| A: Independence | 2 | Depends on OBPI-01 (schema) and OBPI-02 (init creates the directory to sync). Undeclared. |
| B: Testability | 1 | Template placeholder. |
| C: Value | 4 | Without manifest integration and sync, personas are not a control surface at all. Core value proposition. |
| D: Size | 2 | Bundles manifest schema update AND sync engine changes. These are two distinct concerns -- schema validation vs file mirroring. Could be too large. |
| E: Clarity | 1 | "TBD" objective. Template boilerplate only. |
| **Average** | **2.0** | |

### OBPI-0.0.13-04 — Vendor-Neutral Persona Loading

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| A: Independence | 2 | Depends on OBPI-01 (schema format) and OBPI-03 (sync mechanism). Not declared. |
| B: Testability | 1 | Template placeholder. |
| C: Value | 3 | Vendor adapters are needed for multi-vendor portability. However, value overlaps with OBPI-03 sync -- for file-based vendors (Claude, Codex), sync IS loading. The adapter layer's distinct value is translating format, which may be minimal initially. |
| D: Size | 3 | Reasonable scope for adapter pattern implementation. |
| E: Clarity | 1 | "TBD" objective. Template boilerplate. **Also note:** The brief's checklist item reference says "#4 - gz agent sync persona mirroring" but OBPI-04 in the ADR table is "Vendor-neutral persona loading adapters". The brief title says "Vendor Neutral Persona Loading" but references the wrong checklist item. |
| **Average** | **2.0** | |

### OBPI-0.0.13-05 — Persona Drift Monitoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| A: Independence | 2 | Depends on OBPI-01 (what does a persona look like) and implicitly on deployed personas to monitor. Undeclared. |
| B: Testability | 1 | Template placeholder. |
| C: Value | 3 | Closes the feedback loop (design->deploy->monitor). Important but the most speculative OBPI -- "behavioral proxies" for drift are described vaguely in the ADR Rationale. |
| D: Size | 2 | Drift monitoring is potentially unbounded. What exactly does `gz personas drift` report? The ADR describes three behavioral proxy questions but does not define data sources, thresholds, or output format. Could easily balloon. |
| E: Clarity | 1 | "TBD" objective. Template boilerplate. **Also note:** The brief references checklist item "#5 - Vendor-neutral persona loading" but this is OBPI-05 (drift monitoring). The checklist items are cross-wired -- OBPI-05's brief references OBPI-04's checklist item, and OBPI-06's brief references OBPI-05's checklist item. |
| **Average** | **1.8** | |

### OBPI-0.0.13-06 — Cross-Project Validation

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| A: Independence | 1 | Cannot start until OBPIs 01-04 are complete (need schema, init, sync, loading to validate cross-project). Depends on virtually everything. |
| B: Testability | 1 | Template placeholder. Cross-project testing is inherently harder to verify with a single command. |
| C: Value | 3 | Proves the "portable" claim. Without this, portability is theoretical. |
| D: Size | 2 | Applying to airlineops is either trivial (if everything works) or enormous (if integration reveals design flaws). Unpredictable. |
| E: Clarity | 1 | "TBD" objective. Template boilerplate. **Also note:** Brief references checklist item "#6 - Persona drift monitoring surface" but this is OBPI-06 (cross-project validation). The checklist mapping is shifted by one. |
| **Average** | **1.6** | |

### OBPI Score Summary

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 3 | 1 | 4 | 3 | 1 | 2.4 |
| 02 | 2 | 1 | 3 | 3 | 1 | 2.0 |
| 03 | 2 | 1 | 4 | 2 | 1 | 2.0 |
| 04 | 2 | 1 | 3 | 3 | 1 | 2.0 |
| 05 | 2 | 1 | 3 | 2 | 1 | 1.8 |
| 06 | 1 | 1 | 3 | 2 | 1 | 1.6 |

**OBPI Average: 1.97 / 4.0 -- ALL BELOW 3.0 THRESHOLD**

**Critical finding:** Every OBPI scores 1 on both Testability and Clarity. This is expected for scaffolded templates, but it means zero OBPIs are implementation-ready. Additionally, OBPI-05 and OBPI-06 score 1.8 and 1.6 respectively, indicating structural issues beyond just template defaults.

---

## Part 3: Red-Team Challenge Protocol

### Challenge 1: The "So What?" Test

**Result: PASS (marginal)**

Testing each checklist item:

1. **Portable persona schema** -- Without it: no standard way to define personas across projects. Every project invents its own format. Concrete loss. PASS.
2. **gz init persona scaffolding** -- Without it: manual directory creation and file copying per project. Concrete loss. PASS.
3. **Manifest schema update** -- Without it: personas are not a recognized control surface. `gz validate` cannot check them. Concrete loss. PASS.
4. **gz agent sync persona mirroring** -- Without it: manual vendor-directory maintenance. Concrete loss, follows established pattern. PASS.
5. **Vendor-neutral persona loading** -- Without it: vendors cannot consume personas in their native format. But for file-based vendors (Claude, Codex, Copilot), the sync in item 4 already places files where vendors read them. The additional "loading adapter" value is translating format, which may not be needed initially if the canonical format is already vendor-consumable markdown. MARGINAL -- the "so what" depends on how different vendor consumption actually is.
6. **Persona drift monitoring** -- Without it: no feedback loop on persona effectiveness. But "behavioral proxies" are not defined concretely in the ADR. What data feeds `gz personas drift`? Agent conversation logs? Output analysis? This is aspirational without a data source. The "so what" is real in theory but undefined in practice. MARGINAL.

### Challenge 2: The Scope Challenge

**Result: FAIL**

**Something NOT in scope that arguably SHOULD be:**

1. **Persona versioning** -- If personas are portable and synced across projects, what happens when the schema evolves? Version migration is not addressed. Projects on schema v1 receive a v2 persona file and break silently.
2. **Persona composition conflict resolution** -- The ADR mentions "composition rules" in the Decision section but no OBPI addresses how conflicting traits between composed personas are resolved.
3. **Backward compatibility contract** -- If this becomes a portable primitive consumed by other projects, breaking changes have cross-project blast radius. No compatibility policy is stated.

**Something IN scope that arguably SHOULD NOT be:**

1. **Persona drift monitoring (OBPI-05)** -- This is a fundamentally different concern from storage/sync portability. Drift monitoring requires runtime behavioral observation, data collection, and analysis. The ADR itself acknowledges gzkit "cannot directly measure activation space positions" and must use "behavioral proxies" -- but those proxies are undefined. This OBPI belongs in a separate ADR focused on persona observability, after the portability foundation is proven. Including it here risks scope creep and delivery delay for the core value (making personas portable).

**Where is scope creep likely?**

The drift monitoring OBPI will naturally expand into runtime persona evaluation, behavioral scoring, and reporting dashboards -- none of which are portable primitives. The "observability surface" framing invites unbounded work.

**Pass criteria requires:** Both inclusions and exclusions justified with specific reasoning. The ADR does not address versioning, composition conflicts, or backward compatibility at all, and the drift monitoring inclusion is not defended against the alternative of deferral to a dedicated ADR.

### Challenge 3: The Alternative Challenge

**Result: PASS (marginal)**

**Could this ADR achieve its goals with fewer OBPIs?**

Yes. OBPI-01 (schema) and OBPI-04 (vendor loading) could merge. The schema specification and vendor adapter format are tightly coupled -- you cannot design the schema without knowing how vendors will consume it, and the adapter layer is just the schema-to-vendor translation. Merging produces a 5-OBPI decomposition.

OBPI-03 could absorb the manifest schema portion into OBPI-01 (schema spec naturally includes where it lives in the manifest) and become purely "sync engine changes," making it more focused.

**Could it be done with more OBPIs? Which are too large?**

OBPI-03 bundles manifest schema update AND sync engine behavior. These are separable: one is a data/schema change (add `control_surfaces.personas` to manifest), the other is an engine change (teach `sync_surfaces.py` to mirror personas). Splitting to 7 OBPIs would improve independence.

OBPI-05 (drift monitoring) is potentially too large for its undefined scope. If kept, it should be split into "drift data model" and "drift CLI surface."

**Defense of current decomposition:** The 6-OBPI count matches the decomposition scorecard calculation. The groupings follow domain boundaries. The current granularity is defensible but not optimal.

### Challenge 4: The Dependency Challenge

**Result: FAIL**

**Dependency graph analysis:**

```
OBPI-01 (schema) <-- root, single point of failure
   |
   +-- OBPI-02 (init) -- depends on schema
   |      |
   +-- OBPI-03 (manifest/sync) -- depends on schema, benefits from init
   |      |
   +-- OBPI-04 (loading) -- depends on schema, sync
   |
   +-- OBPI-05 (drift) -- depends on schema, deployed personas
   |
   +-- OBPI-06 (cross-project) -- depends on ALL of 01-04
```

**Single point of failure:** OBPI-01 is a critical-path bottleneck. If the schema specification is wrong or delayed, every downstream OBPI is blocked. This is acknowledged implicitly but not addressed with a mitigation strategy (e.g., schema review gate before downstream work begins).

**If OBPI-03 fails:** Both OBPI-04 (loading needs synced files) and OBPI-06 (cross-project needs sync working) are blocked. OBPI-03 is a secondary bottleneck.

**If OBPI-05 fails:** Only OBPI-06 is partially affected (cross-project validation might skip drift testing). OBPI-05 failure is contained.

**The dependency graph is NOT explicitly documented anywhere** -- neither in the ADR nor in the briefs. The briefs have no "depends on" metadata. The ADR table has no dependency column. This is a structural gap: the graph is implicit, forcing implementers to infer sequencing.

### Challenge 5: The Gold Standard Challenge

**Result: FAIL**

**Comparison target:** ADR-0.0.1 (Canonical GovZero Parity with AirlineOps) -- the foundational ADR that established the governance pattern this ADR extends.

**What ADR-0.0.1 has that ADR-0.0.13 lacks:**

1. **Explicit STOP/BLOCKER criteria with specificity** -- ADR-0.0.1's blockers name discoverable conditions ("If any governance concept lacks a discoverable source artifact"). ADR-0.0.13's blockers are good but less operationally precise.
2. **Series metadata** -- ADR-0.0.1 uses `Series: adr-0.0.x` for grouping. ADR-0.0.13 omits this.
3. **Completion status context** -- ADR-0.0.1, even in Draft, has been the foundational reference for all subsequent ADRs. Its structural patterns (feature checklist sections, lane definitions) became the standard. No validated ADR exists in this repo to compare against, which means ADR-0.0.13 is being written in a pre-validation ecosystem -- there is no proven exemplar to follow perfectly.

**What ADR-0.0.13 improves over ADR-0.0.1:**

1. **Decomposition scorecard** -- ADR-0.0.13 includes the quantitative decomposition matrix. ADR-0.0.1 does not.
2. **Agent Context Frame** -- The MANDATORY context frame with Role/Purpose/Goals/Anti-Pattern is clearer and more structured than ADR-0.0.1's implicit framing.
3. **Integration points** -- ADR-0.0.13 names specific module paths. ADR-0.0.1 is more abstract.

**Gap:** No ADR in this repository has reached Validated status. The exemplar comparison is limited because the gold standard does not yet exist locally. This makes structural quality harder to benchmark.

### Challenge 6: The Timeline Challenge

**Result: PASS**

**Critical path:**

```
Stage 1: OBPI-01 (schema) .............. ~2 days
Stage 2: OBPI-02, OBPI-03 (parallel) .. ~2-3 days
Stage 3: OBPI-04 (loading) ............. ~2 days
Stage 4: OBPI-05 (drift) ............... ~3 days (speculative)
Stage 5: OBPI-06 (cross-project) ....... ~2-3 days
```

**Parallelization:** OBPI-02 and OBPI-03 can run in parallel after OBPI-01 completes. OBPI-05 can potentially start in parallel with OBPI-04 if it only needs the schema (not synced files). Maximum parallelism: 2 OBPIs simultaneously.

**Theoretical minimum wall-clock time:** ~11-13 days assuming single-agent execution, or ~8-10 days with two-agent parallelism.

**Bottleneck:** OBPI-01 blocks everything. OBPI-06 must wait for everything. These bookend constraints define the critical path.

**Assessment:** The timeline is feasible but the ADR does not state it. The dependency relationships that drive the critical path are implicit, not documented.

### Challenge 7: The Evidence Challenge

**Result: FAIL**

Attempting to write verification commands for each OBPI:

**OBPI-01 (schema):**
```bash
# What file proves the schema exists?
cat .gzkit/schemas/persona.schema.json  # Guessing -- ADR doesn't specify filename
# What validates schema correctness?
uv run gz personas validate  # This command doesn't exist yet; circular dependency
```
The schema specification OBPI has no defined output artifact path. Is it a JSON Schema file? A Pydantic model? A markdown specification? The ADR says "project-agnostic schema" but not what format it takes.

**OBPI-02 (init scaffolding):**
```bash
mkdir /tmp/test-project && cd /tmp/test-project && uv run gz init
ls .gzkit/personas/  # Should exist with default files
```
Reasonable, but the brief does not specify it.

**OBPI-03 (manifest/sync):**
```bash
uv run gz validate --surfaces  # Should include personas
uv run gz agent sync control-surfaces  # Should mirror personas
ls .claude/personas/ .agents/personas/ .github/personas/  # Should exist
```
Reasonable, but the brief does not specify it.

**OBPI-04 (vendor loading):**
```bash
# How to verify vendor adapters work?
# Need to invoke each vendor's loading path -- but gzkit doesn't run vendors
# This is inherently untestable from gzkit's perspective alone
```
**Underspecified.** Vendor-neutral loading verification requires defining what "loaded" means for each vendor.

**OBPI-05 (drift monitoring):**
```bash
uv run gz personas drift  # What does this output? Against what data?
# The ADR says "behavioral proxies" but names no data source
```
**Critically underspecified.** Cannot write a verification command because the drift data model is undefined.

**OBPI-06 (cross-project validation):**
```bash
cd ../airlineops && uv run gz init && ls .gzkit/personas/
uv run gz agent sync control-surfaces && ls .claude/personas/
```
Reasonable in concept but requires a second repository, which makes CI verification complex.

**Verdict:** OBPIs 01, 04, and 05 cannot have concrete verification commands written because the output artifacts and data sources are not defined. The briefs are templates with zero verification content. Even the ADR-level evidence section uses generic artifact classes.

### Challenge 8: The Consumer Challenge

**Result: FAIL**

A maintainer or operator reading this ADR would still ask:

1. **"What does a persona file actually look like?"** -- The ADR says "traits, anti-traits, grounding, composition rules" but never shows an example. A single example persona file (even a mock) would make the entire ADR concrete. Its absence forces readers to imagine the schema.

2. **"How do I customize the default persona set?"** -- gz init creates defaults, but the override mechanism is not described. Do I edit files in `.gzkit/personas/`? Will sync overwrite my changes? What is the merge strategy?

3. **"What does `gz personas drift` actually report?"** -- The ADR describes three behavioral proxy questions but not the output format, data source, or actionable response. A maintainer cannot evaluate whether this feature is useful without seeing example output.

4. **"If I am running Copilot, what changes for me?"** -- The vendor adapter concept is described abstractly. A concrete example (persona X becomes system prompt fragment Y for Claude and instruction block Z for Copilot) would make this concrete.

5. **"Are my existing personas in airlineops compatible?"** -- The ADR mentions airlineops has "persona-like language in AGENTS.md" (Tidy First item 3) but does not describe the migration path from unstructured text to structured persona files.

### Challenge 9: The Regression Challenge

**Result: FAIL**

**Six months post-validation, what could silently break?**

1. **Schema drift across projects** -- Project A updates to persona schema v2; project B stays on v1. `gz init` in a new project uses v2. There is no schema versioning strategy. Personas synced between projects may silently fail validation.

2. **Vendor format changes** -- When Claude Code, Codex, or Copilot change how they consume identity context (which they do regularly), the vendor adapters break. No vendor format compatibility monitoring is described.

3. **Sync surface staleness** -- If a developer adds a persona file to `.gzkit/personas/` but forgets to run `gz agent sync`, the vendor mirrors are stale. The existing rules/skills sync has this same problem, and the ADR does not address whether personas inherit the same staleness risk or mitigate it.

4. **Drift monitoring data source decay** -- Whatever behavioral proxy feeds `gz personas drift` could change or disappear (e.g., if agent log formats change). No contract ensures the drift data source remains available.

**What monitoring ensures validity?**

The ADR proposes `gz personas drift` for behavioral monitoring, but there is no contract for monitoring the portability infrastructure itself (schema compatibility, sync freshness, vendor adapter validity). The observability surface monitors persona adherence, not system health.

### Challenge 10: The Parity Challenge

**Result: FAIL**

**Weakest parity claim:** "Personas follow the same canon-first, vendor-mirror pattern" as rules and skills.

**Why this claim does NOT fully hold:**

Rules and skills are **static text files** that can be copied verbatim to vendor mirrors. The sync operation is a straightforward file copy with minimal transformation.

Personas, as described in this ADR, require **vendor-specific translation** ("system prompt fragments for Claude, instruction blocks for Codex"). This is fundamentally different from the rules/skills pattern. Rules sync is `cp source dest`. Persona sync is `transform(source, vendor_format) -> dest`. The "same pattern" claim glosses over this structural difference.

Furthermore, rules and skills have **no monitoring surface**. Adding `gz personas drift` creates an observability layer that rules and skills do not have. This makes personas a categorically heavier control surface than the ones cited as precedent.

The parity claim is partially valid (canonical directory, vendor mirrors, manifest entry) but overstated. The transformation and monitoring layers make personas more complex than the cited precedent suggests. The ADR should acknowledge this difference explicitly rather than presenting full pattern parity.

---

## Red-Team Challenge Summary

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | PASS | All items justified, though items 5-6 are marginal |
| 2 | Scope | FAIL | Missing versioning, composition, backward compat; drift monitoring arguably out of scope |
| 3 | Alternative | PASS | Current decomposition is defensible with minor merge/split opportunities |
| 4 | Dependency | FAIL | Single point of failure on OBPI-01; dependency graph is undocumented |
| 5 | Gold Standard | FAIL | No validated exemplar exists in repo; structural comparison limited |
| 6 | Timeline | PASS | Critical path is feasible, ~8-13 days, parallelism available |
| 7 | Evidence | FAIL | OBPIs 01, 04, 05 cannot have verification commands written; outputs undefined |
| 8 | Consumer | FAIL | Five unanswered operator questions identified; no example persona shown |
| 9 | Regression | FAIL | No schema versioning, no vendor compat monitoring, no staleness mitigation |
| 10 | Parity | FAIL | Vendor transformation and monitoring surface break pattern parity with rules/skills |

**Red-Team Failures: 7 of 10**

**Red-Team Threshold: NO GO (>=5 failures = NO GO)**

---

## OBPI Brief Structural Defects

Beyond the template-default low scores, three structural defects were found in the brief metadata:

1. **Lane contradiction:** The ADR OBPI table assigns Heavy to OBPIs 03, 05, 06, but all six briefs declare Lite. This must be reconciled before any implementation begins.

2. **Checklist item cross-wiring:** OBPI-05's brief references checklist item #5 ("Vendor-neutral persona loading") instead of #5 in the ADR table ("Persona drift monitoring surface"). OBPI-06's brief references #6 ("Persona drift monitoring surface") instead of #6 ("Cross-project validation"). The checklist item references are shifted by one starting at OBPI-05, suggesting a copy-paste error during scaffolding.

3. **OBPI-04 checklist mismatch:** OBPI-04's brief references "#4 - gz agent sync persona mirroring" but the ADR table item 4 is "Vendor-neutral persona loading adapters". The sync mirroring is item 3 in the ADR feature checklist (as a combined entry with manifest). The mapping between feature checklist and OBPI table is inconsistent.

---

## Overall Verdict

**[X] NO GO -- Structural revision required**

The ADR itself is well-structured with strong architectural alignment and a clear pattern precedent. However, the combination of:

- 7/10 red-team challenge failures (threshold is >=5 for NO GO)
- ADR weighted score of 2.60 (CONDITIONAL GO range, dragged down by lane assignment defect)
- All 6 OBPIs below the 3.0 threshold (expected for templates, but briefs also have metadata defects)
- Lane assignment contradiction between ADR table and briefs (score of 1)
- Checklist-to-OBPI cross-wiring errors

...produces a NO GO verdict. The ADR's architectural vision is sound, but the execution artifacts are not ready for implementation.

---

## Top 5 Action Items (Ranked by Impact)

1. **Fix lane assignments and brief metadata** -- Reconcile ADR table lanes (Heavy for 03, 05, 06) with brief frontmatter. Fix all checklist item cross-references in OBPI briefs 04, 05, 06. This is a blocking mechanical defect.

2. **Author all OBPI briefs** -- Replace every "TBD" objective, template requirement, template allowed-path, and placeholder acceptance criterion with real content. Every OBPI must have at least one concrete verification command. Testability and Clarity scores of 1 across the board mean no OBPI is implementation-ready.

3. **Add an explicit non-goals section to the ADR** -- Document that persona versioning/migration, persona composition conflict resolution, backward compatibility policy, and runtime behavioral enforcement are out of scope. State why drift monitoring IS in scope despite being categorically different from storage/sync.

4. **Add a concrete persona file example** -- Include one example persona file (even a minimal mock) in the ADR to make the schema concept tangible. This resolves the Consumer Challenge failure and grounds the schema specification OBPI.

5. **Document the OBPI dependency graph** -- Add a dependency column to the ADR OBPI table or a separate dependency diagram. Explicitly name OBPI-01 as the critical-path bottleneck and describe the mitigation strategy (e.g., schema design review gate before downstream work begins).

### Secondary Action Items

6. **Acknowledge the parity gap** -- The vendor transformation layer makes personas a heavier control surface than rules/skills. State this explicitly and explain why the additional complexity is justified.

7. **Define the drift monitoring data source** -- Before OBPI-05 can be sized or implemented, the ADR must specify what data `gz personas drift` consumes. Without a data source, the OBPI is unbounded.

8. **Consider deferring OBPI-05 (drift monitoring)** -- Moving it to a separate ADR focused on persona observability would tighten this ADR's scope to the portable storage/sync primitive and reduce scope creep risk.
