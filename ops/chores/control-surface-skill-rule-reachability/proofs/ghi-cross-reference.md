# GHI Cross-Reference — Reachability Gaps vs. Recent Defect Trail

For each "no" row in `reachability-matrix.md`, searched recent GHIs (#59, #121, #130, #139, #141–#268) via `git log --since='2026-01-01' --grep='GHI #'` (99 commits scanned).

**Convention:** "known-blocking" = reachability gap with a historical GHI that explicitly names the violation pattern. "latent" = reachability gap without a matching GHI hit.

| Row # | Skill / Rule | GHI hit? | GHI(s) | Notes |
|---|---|---|---|---|
| 1 | gz-adr-audit / tests.md § "Tests assert semantics" | yes | GHI #268 | Filed today during ADR-0.0.17 audit; the canonical example of the class. |
| 2 | gz-adr-audit / adr-audit.md § "Audit sequence" | no | — | Latent — procedural ordering drift between skill and rule has not yet produced a visible defect but the asymmetry exists. |
| 3 | gz-adr-audit / attestation-enrichment.md § "Canonical invocations" | yes | GHI #199, #225, #229 | GHI #199 traces Heavy-lane attestation failure where a non-canonical form (`ty check .`) passed while canonical (`ty check src`) failed. GHI #225 aligned arb.md examples with canon. GHI #229 resolved cross-surface contradictions in usage matrix. Pattern is the same class: skill bypassing canonical receipt forms. |
| 4 | gz-adr-audit / gate5-runbook-code-covenant.md § three-layer model | no | — | Latent — no GHI names a post-audit runbook-drift incident originating from gz-adr-audit. |
| 5 | gz-adr-closeout-ceremony / attestation-enrichment.md § "Canonical invocations" | yes | GHI #199, #225, #229, #230 | Same canonical-invocation family as row 3. GHI #230 hoisted binding content to anchor output-form claims to locking tests; rule integration pattern established, ceremony skill has not absorbed it. |
| 6 | gz-adr-closeout-ceremony / arb.md § "When to Use ARB" | yes | GHI #199, #229 | The "gz check never implemented ARB receipt emission" note in gz-arb/SKILL.md (revival_note) documents the same class of failure: gate-aggregating skills that route around the ARB contract. |
| 9 | gz-obpi-pipeline / attestation-enrichment.md | yes | GHI #199, #225 | Partial-honor only — skill cites rule at line 493 but Stage 3 QA invocations bypass canonical ARB forms. |
| 10 | gz-obpi-pipeline / arb.md | yes | GHI #199, #229 | Same class. Pipeline Stage 3 is the upstream of Heavy-lane attestation at Stage 5; bypassing ARB here forces Stage 5 to invent receipt citations. |
| 12 | gz-obpi-pipeline / tests.md § "Red-Green-Refactor" / "@covers" semantics | yes | GHI #157, #268 | GHI #157 codified per-increment TDD rhythm against test-dump batching. GHI #268 is the `@covers`-as-cosmetic-backfill pattern. Stage 3 Phase 1b parity gate is mechanical but blind to assertion quality. |
| 13 | gz-obpi-pipeline / brief-heading-conventions.md | yes | GHI #238 | GHI #238 promoted the H3 convention to a `gz validate --brief-headings` scope. Pipeline has not absorbed the pre-Stage-5 check. |
| 15 | gz-obpi-pipeline / gate5-runbook-code-covenant.md | yes | GHI #249, #265 | GHI #249 eliminated residual Heavy/Foundation bucketing in docs. GHI #265 added concepts_page proof type + relaxed runbook slug match — both indicate runbook-parity drift originating mid-OBPI that the pipeline did not prevent. |
| 16 | gz-obpi-specify / brief-heading-conventions.md | yes | GHI #238 | The very GHI that promoted the mechanical check was motivated by authoring-time drift; gz-obpi-specify is the authoring skill that should have cited it. |
| 17 | gz-obpi-specify / attestation-enrichment.md | no | — | Latent — no GHI names a brief-authoring acceptance criterion that forced downstream attestation-text drift. |
| 19 | gz-adr-create / gh-cli.md § "Defect tracking requirement" | no | — | Latent. |
| 23 | gz-adr-emit-receipt / attestation-enrichment.md | yes | GHI #199, #229 | Same canonical-invocation class. emit-receipt is the raw surface; skills wielding it without enrichment produce narrative-only receipts. |
| 24 | gz-plan / defect-fix-routing.md | yes | GHI #195, #229 | GHI #195 authored the routing rule after the OBPI-0.0.16-06 over-ceremony incident. GHI #229 added the defect-fix scope gate to pipeline and router. gz-plan is the plan-mode entry point and still does not cite the routing rule. |
| 27 | gz-chore-runner / tests.md § coverage floor + BVT ceiling | no | — | Latent. |
| 29 | gz-check / arb.md § ARB usage matrix | yes | GHI #199 (revival_note in gz-arb/SKILL.md documents this explicitly) | The revival_note names the exact drift: "gz check never implemented ARB receipt emission, so the rule contract in .gzkit/rules/arb.md was referencing a nonexistent surface." Known-blocking but only partially remediated — gz-arb was revived as a separate skill rather than merged into gz-check. |
| 32 | gz-patch-release / attestation-enrichment.md | yes | GHI #233 | GHI #233 anchored GHI discovery to commit range; did not address attestation-text shape in release notes. Latent adjacent to remediated surface. |
| 33 | gz-patch-release / arb.md § "When to Use ARB" (Mandatory: release) | yes | GHI #229 | GHI #229 keyed ARB usage on attestation context; release ceremony is mandatory in that matrix but the skill has not absorbed the change. |
| 35 | gz-agent-sync / skill-surface-sync.md § "Version discipline" | yes | GHI #247 | GHI #247 fixed sync regeneration of copilot-instructions.md when canonical rules exist — skill-version discipline gap that the sync skill could pre-flight but does not. |
| 36 | gz-adr-autolink / tests.md § "@covers"/"Tests assert semantics" | yes | GHI #268 | Same class as row 1. Autolink consumes `@covers` tags as ground truth regardless of semantic assertion quality. |
| 38 | gz-obpi-reconcile / tests.md § "Coverage Floor" + "@covers" semantics | yes | GHI #160 (Phase 3/4 backfill), GHI #268 | GHI #160 Phase 4 "retroactive @covers for orphan ceremony tests" and Phase 3 "backfill REQ IDs across 260 briefs" — large-scale `@covers` backfill work that did not surface the semantic-assertion gap tests.md § invariant 6f names. |
| 41 | gz-obpi-simplify / cross-platform.md | no | — | Latent. |
| 42 | gz-obpi-simplify / models.md | no | — | Latent. |
| 43 | gz-obpi-simplify / tests.md § RGR | no | — | Latent. |
| 56 | gz-skill-router / tool-skill-runbook-alignment.md | yes | GHI #141, #149, #150, #151 | The entire invariant family was motivated by the router/skill-routing drift class. Router skill is the dispatcher but does not self-apply the invariants. |
| 57 | gz-adr-evaluate / tests.md § "Tests assert semantics" | yes | GHI #157, #268 | Evaluation scoring dimension gap — a known-blocking latency because adr-evaluate is the authoring-time scorecard that should catch exactly this class. |
| 58 | gz-design / defect-fix-routing.md | yes | GHI #195 | gz-design is a frequent entry point for "small design" requests that routing-rule explicitly governs. |
| 61 | gz-session-handoff / attestation-enrichment.md | no | — | Latent. |

---

## Roll-up

- **Known-blocking rows** (gap + GHI hit): rows 1, 3, 5, 6, 9, 10, 12, 13, 15, 16, 23, 24, 29, 32, 33, 35, 36, 38, 56, 57, 58 → **21**
- **Latent rows** (gap + no GHI hit): rows 2, 4, 17, 19, 27, 41, 42, 43, 61 → **9**
- **Honored rows** (cite or mechanical): rows 7, 8, 11, 14, 18, 20, 21, 22, 25, 26, 28, 30, 31, 34, 37, 39, 40, 55, 59, 62, 63, 64 → **22**
- **n/a (archived/forwarder)**: rows 44–54, 60, 65 → **13**

Totals align with `summary.md` counts.
