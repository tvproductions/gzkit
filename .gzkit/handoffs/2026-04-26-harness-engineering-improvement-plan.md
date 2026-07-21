---
mode: CREATE
adr_id:
branch: main
timestamp: "2026-04-26T00:00:00Z"
agent: claude-code
obpi_id:
session_id: harness-engineering-improvement-plan
continues_from: 2026-04-25-complexity-doctrine-cluster.md
---

<!-- Frontmatter `mode:` was authored as DESIGN, a work-type label reaching for
     a field that did not exist; the vocabulary is exactly CREATE|RESUME (the
     authoring operation), and this document is a creation. Normalized to CREATE
     under GHI #709 so it parses against its own schema. `adr_id` is empty and
     now legitimately so — a design session has no parent ADR, which is the
     defect GHI #709 fixed and which this document was the evidence for. -->

<!-- Handoff for the harness-engineering improvement plan.
     Originating session: 2026-04-26, evaluation of gzkit against
     Birgitta Böckeler's "Harness Engineering" article + Chris Ford
     transcript on Martin Fowler's site. Operator confirmed all three
     waves; this artifact captures the design output for further
     action across multiple subsequent sessions. -->

## Current State Summary

Operator pivoted from execution to evaluate/design mode mid-session and asked for a structured improvement plan against the harness-engineering frame: **fortify** strengths, **strengthen/implement** weaknesses, **illuminate** blindspots. The plan was produced and **all three waves were confirmed**. No implementation occurred. One incidental ledger artifact exists from a TASK-store probe (`TASK-0.31.0-07-01-01` started + completed, used to confirm tasks are implicit and don't require pre-allocation); the OBPI lock for `OBPI-0.31.0-07-mutate` was claimed and released within the same session; pipeline marker was cleared.

This handoff is the durable design artifact. Subsequent sessions consume it to author pool ADRs, chores, validator scopes, and doctrine folds in the sequenced order below.

## Source Material

- Article: <https://martinfowler.com/articles/harness-engineering.html> (Birgitta Böckeler)
- Companion video transcript: Böckeler + Chris Ford deep-dive on the "sensors" axis of harness engineering (full transcript captured in originating session)
- Mapping framework (binding for the plan structure): the 2×2 of **feed-forward (guides) vs feedback (sensors)** crossed with **inferential (LLM-judged) vs computational (deterministic)**

## Mapping gzkit Against the 2×2 (Reference)

|  | Inferential (LLM-judged) | Computational (deterministic) |
|---|---|---|
| **Feed-forward (guides)** | `AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`, `.gzkit/skills/**`, ADRs, OBPI briefs, personas | `gz` CLI surface, `ruff --fix`, `ty`, pre-commit hooks, ARB-canonical step commands, OBPI pipeline runtime |
| **Feedback (sensors)** | `quality-reviewer` / `spec-reviewer` subagents (manual invocation) | `gz validate --<scope>` (≥12 scopes), `gz check`, `gz cli audit`, `gz adr audit-check`, ARB receipts, ledger reconciliation, coverage floor (40%) |

## Confirmed Waves (operator-approved)

Three waves, gated by operator absorption between waves. Sized so a normal session can absorb each wave without saturating context.

### Wave 1 — already in flight or trivially queued

No new pool ADRs needed; small-surface work that can land standalone.

| Item | Type | Status / Route |
|---|---|---|
| **F-5 / S-2** Drive `OBPI-0.31.0-07-mutate` to completion (port airlineops mutation testing → `gz mutate`) | Existing OBPI (heavy lane, status Pending) | Brief at `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/obpis/OBPI-0.31.0-07-mutate.md`. Source: `../airlineops/src/opsdev/commands/mutation_tools.py` (451 lines). Adaptation notes captured in the originating session's implementer dispatch (size caps, Pydantic models, ASCII-only console, exit codes 0/1/2/3, `--min-kill-rate FLOAT` for new policy-breach gate, mocked unit tests). |
| **S-6** Author `dependency-freshness-sweep` chore | New chore | Layout: `src/gzkit/chores/dependency-freshness-sweep/` (canonical) + `.gzkit/chores/dependency-freshness-sweep/` (project overlay) per ADR-0.0.21. Computational tier: parse `pyproject.toml` + `uv.lock`, fetch PyPI versions, emit age-in-days. Optional inferential tier: subagent flags deprecation/abandonment via web research. Cadence: monthly via `/schedule`. |
| **B-6** Doctrine fold for `hypothesis` as named-future-departure | Small AGENTS.md edit | Extend `AGENTS.md § STDLIB-FIRST DOCTRINE § Existing canonical applications` to name `hypothesis` as a future named departure contingent on Wave 2's S-3 landing. Documents the property-testing tradeoff explicitly. |

### Wave 2 — pool ADRs to draft and absorb

Operator absorption is the pacing constraint, not implementation. Each pool ADR is drafted via `/gz-design` or `gz plan create --kind pool --slug <slug>` and stored under `docs/design/adr/pool/`.

| Slug | Title | Source-of-need |
|---|---|---|
| `ADR-pool.harness-sidecar` | In-session sensor sidecar (`gz harness watch`) | S-1 — Böckeler's central demonstration: live process observing edits, running cheapest validators on changed paths, emitting delta to `.gzkit/sidecar.jsonl` for an agent-readable view |
| `ADR-pool.property-testing-doctrine` | Property-based testing under stdlib `unittest` (with `hypothesis` as named departure) | S-3 — closes logic-gap detection on parsers (semver/lifecycle/REQ-ID/ledger event/ARB receipt). Departs from STDLIB-FIRST with explicit rationale. |
| `ADR-pool.code-mod-corpus` | Repeatable mechanical-rewrite registry (`gz codemod list/show/apply`) | S-5 — concrete rewrites: `# type: ignore[code]` → `# ty: ignore[<ty-code>]` (GHI #197), `PYTHONUTF8=1 uv run gz` purge (GHI #275), `dataclass` → Pydantic. Each codemod ships with behave scenario pinning before/after. |
| `ADR-pool.behavior-truth-doctrine` | Doctrine that gates verify *artifact consistency*, not *behavior correctness* | B-4 — names that behavior correctness lives in `features/**` + operator review; bounds what gates do and don't claim. Foundation-kind candidate. |
| `ADR-pool.downstream-runtime-doctrine` | Production-runtime feedback obligations for downstream gzkit-governed projects | B-7 — gzkit binds dependency/testing/CLI doctrine on adopters but is silent on production telemetry → harness loop. Doctrine names structured logging, fitness functions, error budgets as `kind:foundation` adopter obligations. Foundation-kind candidate. |

### Wave 3 — invariants and validator-scope additions

Smaller surface; ride on existing rule files where possible. Add `ADR-pool.review-agent-pipeline-stage`, `ADR-pool.validator-telemetry`, and the new `gz health` aggregator as the only new top-level surfaces in this wave.

| Item | Type | Anchor |
|---|---|---|
| **F-1** `gz validate --receipt-citations` — every claim of "tests pass / lint clean / coverage X%" in commits, OBPI evidence sections, ADR closeout text must cite a resolvable ARB receipt ID | New validator scope | `AGENTS.md § Attestation` (extend) |
| **F-2** Tighten `gz validate --advisory-scorecard` to fail-closed when a rule-file diff doesn't pair with a scorecard-entry diff in the same commit | Existing validator hardening | `docs/governance/advisory-rules-audit.md` |
| **F-3 + B-5 (combined)** New rule `.gzkit/rules/validator-discipline.md`: every new validator scope ships with a self-test fixture (`gz validate --validator-self-tests`) AND cites the failure-class anchor it closes (`gz validate --scope-anchors`) | New rule + 2 validator scopes | New `.gzkit/rules/validator-discipline.md` |
| **F-4** `gz validate --rule-provenance` — every rule file body carries `<!-- ghi: #N -->` marker citing the GHI under which it landed | New validator scope | Extend `.claude/rules/skill-surface-sync.md` rule-version marker convention |
| **F-6** Validator message style guide ("what failed, why it matters, recovery command, doctrine anchor") + `gz validate --validator-message-shape` linting validator output strings | New rule section + validator scope | Extend `.gzkit/rules/cli.md` |
| **F-7** `gz validate --review-surface-shape` — scans agent transcripts for raw JSON/YAML in agent→operator messages (advisory only initially) | New validator scope | `AGENTS.md § OPERATOR ECONOMY` (anti-pattern named, currently unenforced) |
| **S-4** `ADR-pool.review-agent-pipeline-stage` — promote `quality-reviewer` and `spec-reviewer` subagents from on-demand to optional Stage 2.5 in `gz obpi pipeline` for any heavy-lane OBPI; output is advisory (never blocks gates), produces `review-receipt-*.json` attached to OBPI evidence | New pool ADR | Existing personas in `.gzkit/personas/` |
| **S-7** `gz health` — new CLI verb, distinct from `gz check`. Aggregates every `gz validate --<scope>` in cheapest-first order; renders single table; `--since=<commit>` mode shows delta from baseline; `--watch` mode polls every N seconds (sidecar-lite) | New CLI verb (heavy-lane ADR per `cli.md`) | New ADR |
| **B-1** `ADR-pool.validator-telemetry` — every `gz validate --<scope>` invocation emits structured event to `.gzkit/telemetry.jsonl` (scope, duration, exit code, hits, repo size). Quarterly chore `validator-cost-value-review` summarizes hit rate; zero-hit scopes surface as retirement candidates | New pool ADR | Telemetry stream is ledger-adjacent, NOT the ledger (different storage layer per state-doctrine) |
| **B-2** One-time chore `guide-coverage-experiment` — for each top-level rule in `.claude/rules/**`, run controlled subagent task with rule present vs absent, all sensors active. Score: did sensors catch what the guide describes? Outcome: coverage matrix at `docs/governance/guide-coverage-matrix.md`. Drives the "delete redundant guides" question Böckeler asked | New one-time chore | Companion to `gz-context-diet` |
| **B-3** Foundation-kind OBPI Gate 5 attestation requires walkthrough prompt — `gz obpi precomplete` interactively presents 3 randomly-selected acceptance criteria and asks operator to name observed evidence (not check a box). Closes glance-and-attest failure mode | Invariant + validator scope `gz validate --attestation-walkthrough-shape` | Extend `AGENTS.md § OBPI Acceptance Protocol` |

## Cross-Cutting Findings (Reference, Not Action Items)

These framed the plan but don't decompose into individual artifacts. They live here for the next session's orientation.

- **gzkit IS a harness-engineering project by design.** The `MAKE LLM STOCHASTIC VIBES INERT` mantra is the harness-engineering thesis stated as canon. The 5:1 governance-to-output ratio is the product, not overhead.
- **gzkit's strongest contribution beyond the article frame:** the Promotable→Mechanical lifecycle (advisory-rules-audit.md scorecard) makes the LLM-to-deterministic ladder Chris Ford described into an institutionalized practice with GHI-tracked promotions. This is what fortification F-2 and the new invariant F-3 are protecting.
- **gzkit's most consequential blindspot:** the guides-vs-sensors balance has never been empirically tested. The contract argues *a priori* why it must be heavy ("Why this contract is not minimal" in AGENTS.md) but no experiment shows which markdown content is load-bearing vs redundant given the validator surface. B-2 is the proposed remedy.
- **Sensor sprawl pressure is asymmetric:** every observed failure produces pressure to add a check; nothing produces pressure to retire one. F-3+B-5 (validator-discipline.md) and B-1 (validator-telemetry) are the paired remedies.

## Doctrine Anchors Already In Place (Reference)

The plan layers on top of these. No conflict expected; if conflict surfaces during authoring, code is source of truth (per AGENTS.md § Lane & Kind Attestation Matrix), the plan is the defect.

- `AGENTS.md` § Behavior Rules — Always (judgment invariants 7–10)
- `AGENTS.md` § DO IT RIGHT (#6a–6h)
- `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT
- `AGENTS.md` § STDLIB-FIRST DOCTRINE
- `AGENTS.md` § OPERATOR ECONOMY OF EFFORT
- `AGENTS.md` § Attestation
- `AGENTS.md` § Defect-fix routing
- `.claude/rules/tests.md` § TDD Red-Green-Refactor + Invariant 6f
- `.claude/rules/cli.md` § CLI Contract Doctrine
- `.claude/rules/skill-surface-sync.md` § Rule version markers
- `docs/governance/advisory-rules-audit.md`
- `docs/governance/state-doctrine.md` (Layer 1 / 2 / 3 distinction)
- `docs/governance/trust-doctrine.md` (T1/T2/T3 layer-boundary invariants)

## Resume Action

The next session resumes work on this plan via one of the following entry points (operator-routed):

1. **Wave 1 — pick a starting item:**
   - `OBPI-0.31.0-07-mutate` — re-claim lock, restart pipeline, dispatch implementer (full brief preserved in originating session transcript)
   - `dependency-freshness-sweep` chore — author via `gz-chore-runner` skill
   - `hypothesis` doctrine fold — small AGENTS.md edit
2. **Wave 2 — pick one pool ADR to draft first.** Recommendation: `ADR-pool.harness-sidecar` (highest-leverage gap from the article; unlocks several downstream invariants). Route: `/gz-design ADR-pool.harness-sidecar`.
3. **Wave 3 — only after Wave 2 absorption.** Many Wave 3 items depend on Wave 2 doctrine landing.

**Do not start Wave 3 work before Wave 2 absorption.** The validator-discipline rule (F-3+B-5) explicitly governs how Wave 3 validator scopes are introduced; landing Wave 3 scopes without that rule in place would be the exact sensor-sprawl failure mode the plan exists to prevent.

## Outstanding Session Artifacts

- Probe TASK in ledger: `TASK-0.31.0-07-01-01` (started + completed, harmless, used only to confirm TASK lifecycle is implicit)
- OBPI lock for `OBPI-0.31.0-07-mutate`: released
- Pipeline markers for `OBPI-0.31.0-07-mutate`: cleared via `gz obpi pipeline --clear-stale`
- No source files modified
- No commits authored
