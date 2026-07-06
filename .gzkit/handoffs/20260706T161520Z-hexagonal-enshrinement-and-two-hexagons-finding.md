---
mode: CREATE
adr_id: ADR-0.32.0
obpi_id: OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants
branch: main
timestamp: '2026-07-06T16:15:20Z'
agent: claude-code-d0e6fa92
last_commit_sha: ffd8ac75
---

<!-- Session handoff: hexagonal enshrinement + the two-hexagons conformance finding. -->

## Current State Summary

Long design session, all work committed + pushed (`origin/main` level at `ffd8ac75`). Three things landed:

1. **Hexagonal Architecture enshrined as gzkit's primary code-architecture directive.** New binding per-turn rule `.gzkit/rules/hexagonal-architecture.md` (deps behind adapters, stdlib+Pydantic core, parameterize-everything per Cockburn §1.1, Protocol>ABC, strong-form) + full Cockburn §1–§5.7 reference in `docs/governance/hexagonal-architecture.md` (five elements + configurator, provided/required, driving/driven, conformance checklist, weak-vs-strong, DDD/bounded-contexts/ACLs). Operator fed the whole reference image-by-image (~30 images). Scorecard entry #64 (Promotable), distribution baseline regenerated.
2. **Instructions-files budgets bumped** (operator ruling "bump all limits, that hard-coded value is noise"): AGENTS.md 31800→50000, CLAUDE.md 4000→15000, `.claude/rules/*.md` 15000→30000. The `_CODEX_PROJECT_DOC_CAP_BYTES` guard was **renamed** `_PROJECT_DOC_BUDGET_CEILING_BYTES` and raised 32768→65536 — decoupling gzkit's budget from the Codex vendor cap (hexagonal: an adapter limit must not gate the core). **NOTE: Codex still truncates at 32768 B at runtime; the number change removed gzkit's guard, not Codex's behavior — durable fix remains corpus-split (GHI #533).**
3. **`provenance: INTENT | OBSERVED` landed on `OntologyEdge`** (required field + `Provenance` StrEnum), backfilled in the corpus projection (child/supersedes→INTENT, validates/attests→OBSERVED). RGR-verified. This is the keystone for the airlock seam-diff ("what ought to be touched" vs "what is touched").

Also this session: **OBPI-0.32.0-04** (ownership/plane doctrine + Boundary-Invariants STRUCTURAL-FENCE) completed + attested (g0) + synced — the ADR-0.32.0 MVP spine (01–04) is now complete.

## THE ISSUE — two hexagons (facade vs working), a real conformance gap

An independent code assessment found gzkit realizes the hexagonal testing benefits **through parameter injection, not through its declared ports layer**:

- **Working hexagon (real):** `project_root: Path` at **738** call-sites; path-injectable `Ledger(path)`; tests act as configurator + driving actor over temp-dir worlds (`tests/test_ontology_corpus.py`). The `ontology/` package is the strong-conformance exemplar (pure core, single injectable seam). `tests/policy/test_import_boundaries.py` is a real AST **test wall** (leakage protection, mechanized). By the DDD criterion (*"tests make the boundary real"*), gzkit's boundaries ARE real where tests inject over temp worlds.
- **Facade hexagon (dormant):** `src/gzkit/ports/` (FileStore/ProcessRunner/LedgerStore/ConfigStore) + `tests/fakes/` + `src/gzkit/adapters/` are built and conformance-tested but wired into **zero** production code and injected into **zero** domain tests (ADR-0.0.3 closed at Gate 5, yet 0% adoption). Only 1 of 4 ports has any adapter (`FileConfigStore`). By Cockburn's own test it's "a nice drawing but not much more."

**Decision owed (the "issue"):** either (a) **wire the dormant ports** into production + domain tests, or (b) **bless parameter-injection as gzkit's canonical hexagon and retire/reframe the facade.** The newly-enshrined rule favors (b) — *"encapsulate first; formalize the port only when a second adapter is real"* — so the dormant 4-port ABC layer over single/zero impls is exactly the speculative-generality the rule now names. Recommend routing as a GHI (`/ghi-author`) for a design decision, or an OBPI if wiring is chosen.

## Important Context

- The provenance model (`INTENT | OBSERVED`) deliberately does NOT store binding-vs-advisory — that is derived from the intent-endpoint node type (REQ/ADR ⇒ binding; Doc ⇒ advisory), auto-honoring OKF BI#1 (ADR-0.30.0). See `src/gzkit/ontology/model.py` `Provenance` docstring.
- The `Snapshot` diff-baseline stores edges as `"source|target|link_type"` strings (no provenance) — so the provenance field did NOT break `resense`. If the seam-diff needs provenance in edge identity later, extend `snapshot_of`.
- Commit cascade lesson: adding a canonical rule file coupled through **three** surfaces — advisory scorecard (`docs/governance/advisory-rules-audit.md`), `bullet_retention` (scorecard bullet must render verbatim in a per-turn surface; `_ENFORCED_CLASSES={mechanical,promotable}`), and the distribution baseline (`gz validate --distribution --regenerate`). All Invariant-1a couplings; budget for them when adding rules.

## Decisions Made

- **Hexagonal (Ports & Adapters) is gzkit's primary code-architecture directive** (operator ruling 2026-07-06) — deps behind adapters, stdlib+Pydantic core, parameterize-everything, Protocol>ABC, encapsulate-first. Enshrined as a binding per-turn rule.
- **Bump all instructions-files limits and decouple from the Codex 32768 cap** (operator: "bump all limits, that hard-coded value is noise") — the vendor cap must not gate the core contract (hexagonal).
- **Edge provenance is `INTENT | OBSERVED`, required (non-erasable), backfilled** — binding-vs-advisory derived from the intent-endpoint node type, not stored (auto-honors OKF BI#1).
- **Provenance landed as a direct-fix correction under ADR-0.32.0** (operator directed "land the provenance field") — the airlock/seam thesis the ADR names cannot compute without it; corrective, not new-design.
- **networkx kept, tree-sitter deferred to exercised-polyglot** (operator re-affirmed on review) — `ast` for gzkit's own Python first; adopt tree-sitter when a non-Python adopter codebase needs imaging.

## Immediate Next Steps

1. **Decide the two-hexagons issue** (wire ports vs bless injection + retire facade). This is the operator's call; the rule leans toward (b).
2. **Wire the seam-diff** on the new provenance field — needs the push-domain (OBSERVED) edges: source domain `covers`/`surface` (OBPI-0.32.0-07) and work domain `blocks`/`blocked_by`/`discovered_from` (OBPI-0.32.0-06). Both are ADR-0.32.0 deferred-breadth, gated behind BI#1 fidelity (proven) and operator work-start authorization (not yet given).
3. **Code↔docs interop** (spine-pivot join key) — discussed, designed, not built: OKF docs declare `explains`/`governs` a REQ/ADR; code anchors via `@covers`; a trace crosses the membrane *through* the governance spine. Reserve direct code↔doc edges for the no-REQ case.
4. **networkx/tree-sitter re-check** at OBPI-06/07: networkx kept (multigraph + near-term community-detection for bounded-context seams); tree-sitter deferred to exercised-polyglot (stdlib `ast` for gzkit's own Python first).

## Pending Work / Open Loops

- ADR-0.32.0 deferred-breadth OBPIs 05 (OKF absorption), 06 (work-domain L2 schema), 07 (source tree-sitter) — pending, operator-gated work-start.
- The `_PROJECT_DOC_BUDGET_CEILING_BYTES` constant name is now honest, but AGENTS.md content past 32768 B will still truncate under Codex until corpus-split (GHI #533).

## Verification Checklist

- [ ] `git rev-parse HEAD` resolves to `ffd8ac75` (or operator explains drift); branch `main`, `origin/main` level.
- [ ] `uv run python -m unittest tests.test_ontology_model tests.test_ontology_graph tests.commands.test_ontology tests.test_ontology_corpus` → all pass (50 in the model/graph/command trio).
- [ ] `uv run gz validate --advisory-scorecard --distribution` → pass (scorecard #64 + regenerated baseline).
- [ ] Key proof of provenance: `OntologyEdge(source_id="a", target_id="b", link_type=LinkType.CHILD)` raises `ValidationError` (provenance required); with `provenance=Provenance.INTENT` it carries the vein.

## Evidence / Artifacts

- Commits (all on `main`, pushed): `219d23fd` (hexagonal rule + budget bump + test-constant rename), `dfb5a953` (scorecard #64 + distribution baseline regen), `ffd8ac75` (DDD/ACL doctrine section + provenance field). This handoff rides the next commit.
- Rule: `.gzkit/rules/hexagonal-architecture.md` (+ mirrors `.claude/rules/`, `.agents/`, `.github/instructions/`, `src/gzkit/rules/`).
- Doctrine: `docs/governance/hexagonal-architecture.md` (Cockburn §1–§5.7 reference + gzkit conformance section).
- Scorecard: `docs/governance/advisory-rules-audit.md` row #64 (Promotable).
- Model: `src/gzkit/ontology/model.py` (`Provenance` enum + `provenance` field on OntologyEdge); backfill in `src/gzkit/ontology/corpus.py`.
- Budget: `data/instructions_files_budget.json` (50000/15000/30000); guard renamed in `tests/governance/test_agents_md_map_doctrine.py` + `tests/governance/test_agents_md_map_doctrine_application.py`.
- Prior OBPI-0.32.0-04 completion handoff: `.gzkit/handoffs/20260706T130549Z-OBPI-0.32.0-04-ownership-plane-doctrine-and-boundary-invariants-complete.md`.
- The two-hexagons finding was produced by an independent read-only code assessment (Explore subagent) cross-checked against `src/gzkit/ports/`, `tests/fakes/`, `src/gzkit/adapters/`, and the 738 `project_root: Path` injection sites.
