---
mode: CREATE
adr_id: ADR-0.0.27
branch: main
timestamp: "2026-04-25T19:42:51Z"
agent: claude-code
obpi_id:
session_id: complexity-doctrine-cluster
continues_from:
---

<!-- Handoff for the four-foundation-ADR complexity-doctrine cluster.
     Originating session: 2026-04-25, design dialogue + canon landings + ADR-0.0.27 skeleton booking. -->

## Current State Summary

This session designed and partially booked a **four-ADR foundation cluster** for complexity doctrine in gzkit. Three new top-level pillars landed in AGENTS.md. ADR-0.0.27 skeleton landed in canonical structure with seven OBPI scaffolds; substantive OBPI authoring + the remaining three ADRs are the next tranche of work.

**Canon landed (this session):**
- `MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)` — gzkit's reason for existing
- `STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)` — default to stdlib; departures named-rationale only; opinionated defaults bind consuming projects
- `OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)` — agent drafts substantively; operator reviews; multiple-choice when bounded; verbatim phrasing preserved; **JSON/YAML/raw machine-readable formats are agent-input surfaces, not review surfaces**
- All five top-level pillars normalized to ALL CAPS with parenthetical subtitles for visual consistency

**ADR-0.0.27 skeleton complete:**
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/` directory created
- ADR markdown with kind=foundation, lane=heavy, persona authored, scorecard set to Final Target OBPI Count = 7 (Single-Narrative=1, Surface-Boundary=1)
- `adr-interview.json` preserved alongside ADR markdown
- `ADR-CLOSEOUT-FORM.md` authored with 7-OBPI table + pool-stub list
- 7 OBPI briefs scaffolded under `obpis/` (template state — semantic content TBD)
- `gz validate --documents` clean
- `gz adr status ADR-0.0.27` shows Pending/HEAVY 7/7 OBPI scaffolds; closeout BLOCKED on ledger proofs (expected)

**Architectural shape (locked across the four ADRs):**

| ADR | Title | OBPIs | Notes |
|---|---|---|---|
| ADR-0.0.27 | Exemplar-Corpus Doctrine | 7 | Skeleton landed; 7 OBPI briefs scaffolded |
| ADR-0.0.28 | Complexity Threshold Doctrine | ~3 | Cites 0.0.27's distilled characteristics |
| ADR-0.0.29 | Complexity Advisor (trigger-time) | 9 | "QC pre-commit" bookend |
| ADR-0.0.30 | Complexity Authoring Guidance | 5 | "QC upfront" bookend |

Total: ~24 OBPIs; foundation-kind + heavy-lane across all four; brief-level Gate 5 attestation per increment.

## Important Context

**The mantra binds every option.** *"MAKE LLM STOCHASTIC VIBES INERT"* is the load-bearing criterion. Every option is framed by *"which choice leaves the smallest surface for vibing to leak through,"* never by maintenance burden or velocity. *"Lighter ceremony"* is not a tradeoff axis. The 5:1 governance-to-output ratio is the product, not overhead.

**Operator Economy of Effort governs interaction.** The agent drafts substantively (forcing-function answers, alternative analyses, per-cell project nominations); operator reviews and decides via multiple-choice or verbatim corrections. Operator's typing budget is the scarce resource. **Never ask the operator to read raw JSON, YAML, or other machine-readable artifacts** — review surface is always human-readable prose summary in chat.

**Three-pillar authority + corpus structure:** complexity-doctrine cluster grounds itself in (a) authority citation (Fowler *Refactoring* 2e, Martin SOLID, Page-Jones connascence taxonomy, Constantine coupling/cohesion modes — the diagnostic vocabulary) AND (b) exemplar-corpus measurement (the empirical boundaries). Both are required.

**Per-cell exemplar corpus locked in design dialogue:**

| Cell | Domain | Project (locked) |
|---|---|---|
| 1 | Sync web framework | Django (with path filtering) |
| 2 | Async web framework | Starlette |
| 3 | HTTP library | httpx |
| 4 | CLI tooling | click (corpus inclusion ≠ dependency adoption) |
| 5 | Type-strict data modeling | attrs (Pydantic excluded for Rust-core) |
| 6 | Stdlib-style | CPython selected modules — pathlib, dataclasses, functools, contextlib |
| 7 | Testing / property-based | hypothesis (pytest excluded per Stdlib-First) |
| 8 | Console / TUI | rich |
| 9 | Static analysis / type checker | mypy |
| 10 | Build / packaging | flit |

Target corpus size: 12-15 projects.

**Pytest demerit lesson:** I mentioned pytest in early Cell 7 drafting despite gzkit's `forbid-pytest` hook. The operator demerited it. Lesson canonized as the **project-doctrine-fitness criterion** in ADR-0.0.27's selection methodology — projects whose foundational design choices contradict gzkit canon are excluded regardless of other strengths.

**OBPI-31 reconciliation:** OBPI-0.31.0-02-complexity-check (literal port of opsdev's wrapper) is to be **withdrawn** with ADR-0.31.0's checklist annotated `→ subsumed by ADR-0.0.29`. Not yet executed; on the next-steps list.

**The 2am operator scenarios identified three ameliorations** which became OBPIs:
1. ADR-0.0.27-07: `gz validate --complexity-doctrine-links` (link-integrity validator) — closes Scenario 2 (broken cross-references in advisor diagnoses)
2. ADR-0.0.29 OBPI-09: pre-commit timeout/fallback/failure-logging — closes Scenario 1 (advisor itself hangs)
3. ADR-0.0.29 OBPI-07: two-path intrinsic-complexity attestation (pre-attested decorator + in-flight commit-time attestation with Gate 5 follow-up) — closes Scenario 3 (CC=24 ship-now reality)

**Pool stubs to book at OBPI-0.0.27-02 land time** (forward-references in citation graph):
1. `ADR-pool.attestation-quality-measurement`
2. `ADR-pool.doctrine-amendment-protocol`
3. `ADR-pool.complexity-doctrine-validate-suite`
4. `ADR-pool.canon-pillar-codification`
5. `ADR-pool.complexity-doctrine-meets-chore-system`
6. `ADR-pool.complexity-guide-obpi-authoring-integration`

Plus one independent of the cluster (operator-tooling concern):
7. `ADR-pool.gz-interview-render` — render machine-readable interview artifacts as human-readable prose for operator review (closes the JSON-review failure pattern at the tooling layer)

## Decisions Made

- **Decision:** ADR-0.0.27 = Exemplar-Corpus Doctrine (foundation, heavy)
  **Rationale:** Most-cited foundation in the cluster; renumbered from initially-proposed ADR-0.0.27 = Complexity Advisor when the corpus dimension entered scope
  **Alternatives rejected:** Feature-kind (would relegate doctrine to rationale section, exposing it to silent drift); single ADR with all four concerns (bundles distinct invariants under one Gate 5 witness)

- **Decision:** Four foundation ADRs in dependency order (0.0.27 corpus, 0.0.28 threshold, 0.0.29 advisor, 0.0.30 authoring guidance)
  **Rationale:** Each codifies one distinct invariant; brief-level Gate 5 attestation per OBPI; mantra says ceremony is the deliverable
  **Alternatives rejected:** Two ADRs (corpus+threshold folded together, advisor separate); one ADR with everything; pool stub first

- **Decision:** Required hard pinned dependencies (radon, lizard, cohesion) — no graceful-degradation
  **Rationale:** Closes the "advisor verdict varies by environment" failure class. Pinned major versions make upstream drift visible at dep-bump time.
  **Alternatives rejected:** Optional with graceful degradation (situational doctrine = doctrine drift); vendored/reimplemented (DEFERRED to potential separate ADR)

- **Decision:** xenon-as-gate, advisor-on-failure (auto-chained from pre-commit)
  **Rationale:** Operator's exact framing — *"triggered design responses when xenon threshold is triggered"*. Preserves SKIP-bypass guard wiring.
  **Alternatives rejected:** Advisor-on-demand (loses trigger-time response); advisor-as-gate (replaces xenon — wider blast radius, breaks SKIP-guard wiring)

- **Decision:** Ten archetypal cells as initial corpus diversity frame; 12-15 project corpus size
  **Rationale:** Statistical adequacy for inter-project variance estimation; manageable operator audit
  **Alternatives rejected:** 3-5 (insufficient variance estimation); 25+ (diminishing returns + audit fatigue); agent-supplied list (training-corpus bias)

- **Decision:** Distillation is agent-driven, human-reviewed and attested/corrected (not "joint authoring")
  **Rationale:** Operator correction
  **Alternatives rejected:** Joint authoring (understates operator's correctional authority); operator-driven (mis-prices the agent's pattern-extraction capability)

- **Decision:** Annual distillation cadence + signal-trigger drift detection > 25% + judgment trigger
  **Rationale:** Python ecosystem evolves on roughly annual cycles; signal trigger is the load-bearing trigger
  **Alternatives rejected:** Quarterly/semi-annual (over-eager); biennial (doctrine staleness); continuous (churn without signal)

- **Decision:** Distillation runs as `gz-complexity-distill` skill (operator-runnable ad-hoc)
  **Rationale:** Operator wanted ad-hoc invocation; skill carries corpus list + path filters + methodology rationale
  **Alternatives rejected:** CLI verb only (loses ad-hoc; loses the "skill includes targets and rationale" property)

- **Decision:** No cuts under scope minimization
  **Rationale:** Each OBPI codifies one distinct invariant; all 24 are essential under MAX DO IT RIGHT-maxxing
  **Alternatives rejected:** Cut OBPI-30-04 (editor/IDE integration); cut OBPI-29-08 (verdict↔proof binding)

- **Decision:** All seven pool stubs at OBPI-02 land time (six cluster + one operator-tooling)
  **Rationale:** Forward-references make citation graph honest; pool stubs are cheap; operator picked B (most thorough citation-graph hygiene)
  **Alternatives rejected:** Three pool stubs (forwards only the highest-confidence); zero pool stubs (loses forward-reference discipline)

## Immediate Next Steps

1. **Author 7 OBPI briefs for ADR-0.0.27 semantically** from the Decision section. Each brief gets:
   - Objective grounded in the OBPI's invariant
   - Allowed paths derived from the mechanical surfaces in the ADR's Decision
   - Acceptance criteria as REQ-ID-decorated bullets
   - Implementation summary placeholder for OBPI-pipeline use
   - Closing argument placeholder
   - Files: `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-{01..07}-*.md`

2. **Update three registries** for ADR-0.0.27:
   - `docs/design/adr/adr_index.md`
   - `docs/design/adr/adr_status.md`
   - `docs/governance/GovZero/adr-status.md`
   (Run `uv run gz adr sync` first to see if it auto-updates; otherwise manual.)

3. **Run `gz-adr-evaluate ADR-0.0.27`** (mandatory per gz-adr-create skill). Score the ADR on 8 dimensions and each OBPI on 5 dimensions. Any 1-score must be revised before proceeding. Output to `EVALUATION_SCORECARD.md`.

4. **Book ADR-0.0.28** (Complexity Threshold Doctrine) via the same flow:
   - Draft `artifacts/drafts/ADR-0.0.28-complexity-threshold-doctrine-interview.json` (refer to design dialogue's threshold content)
   - Present prose summary in chat for operator approval (NOT JSON content)
   - Run `gz interview adr --from <file>.json`
   - Move flat ADR to canonical foundation directory
   - Fill kind/persona placeholders
   - Adjust scorecard for ~3 OBPIs
   - Author CLOSEOUT-FORM
   - Run `gz specify` per OBPI
   - Author OBPI briefs
   - Update registries
   - `gz-adr-evaluate ADR-0.0.28`

5. **Book ADR-0.0.29** (Complexity Advisor) via the same flow — 9 OBPIs.

6. **Book ADR-0.0.30** (Complexity Authoring Guidance) via the same flow — 5 OBPIs.

7. **Withdraw OBPI-0.31.0-02-complexity-check** and annotate ADR-0.31.0's checklist with `→ subsumed by ADR-0.0.29`. File the withdrawal ledger event via `gz adr emit-receipt` (or equivalent).

8. **Strengthen `complexity-reduction-xenon` chore** at `src/gzkit/chores/complexity-reduction-xenon/CHORE.md` to consume `gz complexity-advise --json` output and `proofs/` to record operator-witnessed diagnosis acceptance (closes pre-mortem #6 — advisor recommendation unbinding).

## Pending Work / Open Loops

- The seven pool stubs are forward-referenced in ADR-0.0.27 but not yet booked as files. They book at OBPI-0.0.27-02 implementation time.
- ADR-0.0.30 OBPI-04 (editor/IDE integration contract) is forward-looking specification — out of scope for any CLI implementation; it specifies a contract editor authors can consume.
- Per ADR-0.0.27 OBPI-04 (distillation pass), the first distilled-characteristics document is authored at OBPI implementation time, not at ADR booking. The doctrine ships when implementation lands.
- Vendored/reimplemented metric layer (rejected alternative #5 in ADR-0.0.27) is a deferred separate ADR if upstream `radon`/`lizard`/`cohesion` divergence ever justifies it. Not currently scoped.

## Verification Checklist

- [ ] `uv run gz validate --documents` returns `✓ All validations passed`
- [ ] `uv run gz adr status ADR-0.0.27` shows lane=heavy, kind=foundation, OBPI count 7/7
- [ ] `git status` shows clean working tree (no uncommitted changes — should commit current state before resuming)
- [ ] AGENTS.md contains all five top-level pillars with ALL CAPS headers
- [ ] `grep -c "MAKE LLM STOCHASTIC VIBES INERT" AGENTS.md` returns ≥ 2
- [ ] `grep -c "Stdlib-First\|STDLIB-FIRST" AGENTS.md` returns ≥ 2
- [ ] `grep -c "Operator Economy of Effort\|OPERATOR ECONOMY" AGENTS.md` returns ≥ 2
- [ ] `ls docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/` shows 7 files

## Evidence / Artifacts

| Artifact | Path |
|---|---|
| Canonical ADR | `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md` |
| Interview JSON | `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/adr-interview.json` |
| Closeout form | `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-CLOSEOUT-FORM.md` |
| 7 OBPI scaffolds | `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-{01..07}-*.md` |
| Draft JSON (preserved) | `artifacts/drafts/ADR-0.0.27-exemplar-corpus-doctrine-interview.json` |
| AGENTS.md template (canon source) | `src/gzkit/templates/agents.md` |
| AGENTS.md (rendered) | `AGENTS.md` |
| Session handoff (this file) | `.gzkit/handoffs/2026-04-25-complexity-doctrine-cluster.md` |
