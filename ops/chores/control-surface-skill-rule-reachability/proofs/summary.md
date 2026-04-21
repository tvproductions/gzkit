# Summary — Skill/Rule Reachability (Pass B)

Audit of 56 `SKILL.md` files (15 archived/forwarders, 41 active) against 19 rule files under `.gzkit/rules/`. Applicability scoped per the three-basis test (a/b/c) from CHORE.md. Judgment-only rules (`behavioral-invariants.md`, `constraints.md`, `governance-core.md`) treated as always-on agent contract and not enumerated per-skill.

## Counts

- Honored (cite): 5
- Honored (mechanical): 17
- Gap-latent: 9
- Gap-known-blocking: 21
- Archived / n/a: 13

(Derivation in `reachability-matrix.md` and `ghi-cross-reference.md`.)

## Top 5 known-blocking gaps

Ranked by (a) frequency across rows, (b) whether the anchoring GHI is recent (past 30 days stronger), (c) how load-bearing the skill is in governance flow.

1. **gz-adr-audit / tests.md § "Tests assert semantics, not strings"** (row 1, GHI #268, today)
   The canonical case. Step 2 procedure pushes agents toward backfilling cosmetic `@covers` on output-pinning tests when audit-check fails. Skill does not cite tests.md; rule does not anticipate audit-check remediation flow.

2. **gz-adr-closeout-ceremony / attestation-enrichment.md § "Canonical invocations" + arb.md § ARB usage matrix** (rows 5–6, GHI #199, #225, #229, #230)
   The ceremony that produces Heavy-lane attestation never cites the rules that govern its attestation receipts. Evidence Summary Template prescribes bare `gz lint`/`gz test --bdd`/`gz typecheck`/`mkdocs build --strict` — none of these are the canonical ARB-wrapped forms. Heavy-lane fail-closed rule is therefore bypassed procedurally.

3. **gz-obpi-pipeline / tests.md § "@covers" semantics + brief-heading-conventions.md** (rows 12–13, GHI #157, #238, #268)
   Stage 3 Phase 1b parity gate is mechanical but blind to whether the `@covers`-tagged tests assert REQ-derived semantics. Stage 5 brief authoring does not invoke `gz validate --brief-headings` before `gz obpi complete`. Both are promoted-mechanical-check families the pipeline skill has not absorbed.

4. **gz-skill-router / tool-skill-runbook-alignment.md** (row 56, GHI #141, #149, #150, #151)
   The router dispatches to skills whose `gz_command` may drift from the runbook-prescribed verb or from the skill's Output Contract — exactly the invariant family #141 and #149 were filed against. Router is the natural surface for a pre-dispatch alignment self-check; it does not perform one.

5. **gz-plan / defect-fix-routing.md + gz-design / defect-fix-routing.md** (rows 24, 58, GHI #195, #229)
   The two most common plan-authoring entry points do not cite the routing rule. An agent entering gz-plan or gz-design with an in-flight 5-line defect will scaffold a full ADR/OBPI ceremony — the exact over-application pattern GHI #195 authored the rule to prevent.

## Recommendation per top-5

### 1. gz-adr-audit / tests.md

**Recommendation: reconcile skill + reconcile rule (dual)**

- *Reconcile skill:* gz-adr-audit Step 2 body must cite `.gzkit/rules/tests.md § "Tests assert semantics, not strings"` and change remediation prose from "fix brief evidence first and rerun" to "audit-check failure signals either (a) genuinely missing coverage — add REQ-derived tests and decorate with `@covers`, OR (b) coverage-shape drift — do not backfill cosmetic decorators; re-derive assertions from the OBPI brief's REQ semantics."
- *Reconcile rule:* tests.md § "Red-Green-Refactor" add an anti-pattern bullet naming "backfilling `@covers` to make `gz adr audit-check` pass without re-deriving semantic assertions."
- Trackable under GHI #268.

### 2. gz-adr-closeout-ceremony / attestation-enrichment.md + arb.md

**Recommendation: reconcile skill + promote mechanical check**

- *Reconcile skill:* gz-adr-closeout-ceremony Evidence Summary Template replaces bare QA commands with the canonical ARB-wrapped forms from attestation-enrichment.md § "Canonical invocations". Add explicit citation "Heavy-lane ceremony fail-closed on missing receipt IDs per `.gzkit/rules/attestation-enrichment.md` § Lane behavior."
- *Promote mechanical check:* `gz closeout --ceremony --attest` CLI should refuse Heavy-lane attestation when the attestation text does not contain receipt IDs matching the canonical prefixes in `CANONICAL_STEP_COMMANDS` (src/gzkit/arb/validator.py). File new GHI for the mechanical promotion.

### 3. gz-obpi-pipeline / tests.md + brief-heading-conventions.md

**Recommendation: promote mechanical check + reconcile skill**

- *Promote mechanical check:* `gz validate --brief-headings` (already exists per GHI #238) must be invoked in Stage 5 pre-complete by the pipeline runtime, not relegated to ad-hoc operator call. Extend `gz obpi precomplete` (GHI #196) to run it.
- *Reconcile skill:* gz-obpi-pipeline Stage 3 Phase 1b must add a citation to tests.md § invariant 6f ("Tests assert semantics") alongside the `@covers` parity mechanical check. The parity gate is necessary but not sufficient.
- Trackable under a new GHI referencing #238 and #268.

### 4. gz-skill-router / tool-skill-runbook-alignment.md

**Recommendation: reconcile skill**

- gz-skill-router should cite `.gzkit/rules/tool-skill-runbook-alignment.md § Invariants` in its routing table and run a self-check (or defer to `gz validate --surfaces`) before dispatching when the caller's intent mentions a CLI-verb-name. Skill-level change, not a mechanical promotion — mechanical enforcement is the existing `gz validate --surfaces` surface. The router must be taught that surface validation is a prerequisite to dispatch.

### 5. gz-plan + gz-design / defect-fix-routing.md

**Recommendation: reconcile skill (both)**

- gz-plan Workflow Step 1 should add a pre-flight: "If this is an in-flight defect fix per `.gzkit/rules/defect-fix-routing.md` thresholds (≤10 source lines, ≤2 source files, in-flight trigger, ≥3 recent `fix(...)` precedents), route to a direct `fix(<scope>): … (GHI #N)` commit instead of scaffolding an ADR."
- gz-design analogous pre-flight at Step 1.
- Both citations are one-line additions; low-risk, high-leverage. Trackable under a new GHI referencing #195 and #229.

---

## Cross-cutting observation

Only 3 active skills cite any rule in their body (`gz-arb`, `gz-obpi-pipeline`, `gz-plan-audit`, `gz-skill-router`). The rule layer has grown 19 files strong with granular binding invariants; the skill layer has remained largely citation-free since the initial scaffolding. This asymmetry IS the reachability problem: skills were authored from procedural memory, not from the rule catalogue, and rule updates do not propagate into skills unless a rule explicitly amends a skill file.

The long-term remediation is a `gz validate --rule-reachability` scope that enforces: for every active rule with domain-specific `paths:` frontmatter, at least one skill whose procedure touches those paths cites the rule or enforces it via `gz validate --<scope>`. That matches the Invariant-3 enforcement pattern of tool-skill-runbook-alignment.md (§ Enforcement) — the next mechanical promotion in the advisory-rules-audit scorecard.
