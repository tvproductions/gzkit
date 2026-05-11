# Rule Surface Inventory — Pass A

> Chore: `control-surface-rule-conflicts` (Lite lane, audit-only)
> Generated: 2026-05-11
> Scope per CHORE.md § Policy and Guardrails: every `.md` under `.gzkit/rules/` plus root `AGENTS.md` and `CLAUDE.md`. Vendor mirrors (`.claude/rules/`, `.github/instructions/`) are derivatives and not audited here.

## File set in scope (22 files)

| # | Path | Lines | Frontmatter `id` / Rule | Primary load surface |
|---|------|-------|-------------------------|----------------------|
| 1 | `AGENTS.md` (root) | 379 | (no frontmatter; project root contract) | All agents, every session |
| 2 | `CLAUDE.md` (root) | 27 | (no frontmatter; Claude-specific prelude) | Claude Code session prelude |
| 3 | `.gzkit/rules/AGENTS.md` | 106 | Generated subtree readme (re-exports `agent-failure-modes`, `skill-surface-sync`) | `.gzkit/rules/` subtree |
| 4 | `.gzkit/rules/adr-audit.md` | 47 | `adr-audit` | `docs/design/adr/**` |
| 5 | `.gzkit/rules/agent-failure-modes.md` | 29 | `agent-failure-modes` | `AGENTS.md`, `.gzkit/rules/**`, `docs/governance/**` |
| 6 | `.gzkit/rules/brief-heading-conventions.md` | 52 | `brief-heading-conventions` | `docs/design/adr/**/obpis/**` |
| 7 | `.gzkit/rules/chores.md` | 138 | `chores` (rule-version 0.2.0) | Repository chores workflow |
| 8 | `.gzkit/rules/cli.md` | 89 | `cli` | `src/gzkit/commands/**` |
| 9 | `.gzkit/rules/complexity-doctrine.md` | 123 | `complexity-doctrine` (rule-version 0.3.0) | Complexity calibration cluster |
| 10 | `.gzkit/rules/complexity-thresholds.md` | 99 | `complexity-thresholds` (rule-version 0.3.0) | Threshold table doctrine |
| 11 | `.gzkit/rules/cross-platform.md` | 46 | `cross-platform` (rule-version 0.3.0) | Cross-platform code policy |
| 12 | `.gzkit/rules/gate5-runbook-code-covenant.md` | 39 | (no frontmatter, mirrored) | Docs-as-deliverable covenant |
| 13 | `.gzkit/rules/gh-cli.md` | 38 | `gh-cli` (rule-version 0.2.0) | `.github/**`, ADR ceremony, `gz issue file` |
| 14 | `.gzkit/rules/governance-core.md` | 72 | `governance-core` (rule-version 0.2.0) | `**/*` (universal) |
| 15 | `.gzkit/rules/model-selection.md` | 84 | `model-selection` (rule-version 0.2.0) | Model routing surface |
| 16 | `.gzkit/rules/models.md` | 46 | (data-model policy, mirrored) | Pydantic doctrine |
| 17 | `.gzkit/rules/pythonic.md` | 62 | (idiomatic-code contract, mirrored) | All Python source |
| 18 | `.gzkit/rules/security-sensitivity.md` | 40 | `security-sensitivity` (rule-version 0.2.0) | Sensitivity attestation axis |
| 19 | `.gzkit/rules/skill-surface-sync.md` | 87 | `skill-surface-sync` (rule-version 0.2.0) | Canonical/mirror sync |
| 20 | `.gzkit/rules/tests.md` | 83 | `tests` (rule-version 0.4.0) | `tests/**` |
| 21 | `.gzkit/rules/token-block-discipline.md` | 135 | `token-block-discipline` (rule-version 0.1.0) | Lock-release / handoff coupling |
| 22 | `.gzkit/rules/tool-skill-runbook-alignment.md` | 41 | `tool-skill-runbook-alignment` (rule-version 0.2.0) | `src/gzkit/commands/**`, `.gzkit/skills/**` |

**Total in-scope lines:** 1862 (per `wc -l`)
**Possible unordered pairs:** 22 × 21 / 2 = 231

## Canonical section headings per file (key invariant anchors)

The pairwise walk in `conflict-matrix.md` cites these section names by their literal headings as printed in each rule body.

### `AGENTS.md` (root)
- `## PRIME DIRECTIVE (OWNERSHIP)` (items 1–6)
- `## DO IT RIGHT (CRAFTSMANSHIP MAXIM)` (items 1, 1a, 2–9; § Invariants 6c/6g/6h)
- `## MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)` (operative claims 1–4)
- `## STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)` (operative claims 1–5)
- `## OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)` (operative claims 1–6)
- `## Behavior Rules` § Always (#1–#12), § Never (#1–#7)
- `## Gate Covenant` (Gate 1–5; Lane Rules: lite/heavy)
- `## OBPI Acceptance Protocol` (Lane × Kind × Sensitivity matrix)
- `## Defect-fix routing` (Direct-fix thresholds, OBPI-ceremony triggers)
- `## Attestation` (Canonical invocations, lite vs heavy behavior)
- `# Local Agent Rules` (semantic ordering, UTF-8 prefix, PII, `.gitignore` source)

### `CLAUDE.md` (root)
- `### Invariant 10a — skill-tool-invoke-same-turn`
- `### Opus 4.7 tuning` (Default effort: `xhigh` for agentic work; `high`/`medium` for lookups; `max` for hard problems)
- `## Compact Instructions` (compaction-preservation list)

### `.gzkit/rules/governance-core.md`
- `## Non-negotiable rules` (read AGENTS.md, `uv run`, no Gate 5 bypass, no ledger edits, defect tracking)
- `## Required workflow order (OBPI implementation path)` (6 steps; scoped clause)
- `## Operator-doc verb resolution (binding)`
- `## ADR status index regeneration (binding)`

### `.gzkit/rules/tests.md`
- `## General Rules (binding)` (unittest, table-driven, smoke <=60s)
- `## Coverage Floor (binding)` (40.00%)
- `## Red-Green-Refactor (TDD Discipline — binding)` (incl. Invariant 6f "Tests assert semantics, not strings"; Output-form fixture carve-out)
- `## TASK-Driven Workflow (binding)`
- `## Two runners, one test surface` (`gz check` requires both unittest AND behave)
- `### Behave scenario tagging`

### `.gzkit/rules/tool-skill-runbook-alignment.md`
- `### Invariant 1 — Every CLI tool has at least one skill that wields it`
- `### Invariant 2 — Every skill's gz_command matches a runbook-prescribed tool for the same operator moment`
- `### Invariant 3 — Destination verb's default output form must honor the routing skill's Output Contract`

### `.gzkit/rules/cli.md`
- `## Core Principles` (Human-first, Consistency via `gz cli audit`)
- `## Exit Codes (Standard 4-Code Map)`
- `## Flag Conventions`
- `## Output Contracts` (Default: Human-readable; `--json`: machine; `--plain`: grep-friendly)
- `## Adding CLI Features` (New Flag = Lite; New Subcommand = Heavy)

### `.gzkit/rules/chores.md`
- `## Two-Surface Layout (ADR-0.0.21)`
- `## Core Principles` (Lite by default: `uv run -m unittest -q`; no behave; no network)
- `## Command Sequences` (discover / plan / advise / apply / execute / audit / health)

### `.gzkit/rules/pythonic.md`
- `## Core Principles` (10 numbered)
- `## Size Limits & Refactoring` (Functions <=50, Modules <=600, Classes <=300)
- `## Imports (PEP 8)` (top-level only; no lazy)
- `## Error Handling` (no bare `except`)
- `## Type-check suppression syntax (ty — binding)` (`# ty: ignore[<code>]`, not `# type: ignore[<code>]`)

### `.gzkit/rules/models.md`
- Use **Pydantic `BaseModel`** for all data models; no stdlib `dataclasses`.
- `ConfigDict(frozen=True, extra="forbid")` for immutable models.
- Anti-patterns: stdlib `dataclass` for governance data.

### `.gzkit/rules/complexity-doctrine.md`
- `## Invariant` (corpus-curated, distilled, citable)
- `## Selection Criteria (binding — all must hold)` (7 items)
- `## Corpus Anti-Patterns (binding — any disqualifies)` (7 items)
- `## Distillation Cadence (binding)` (3 triggers)
- `## Citation Contract (binding)` (canonical tuple, percentile + absolute pairing, refresh portability)

### `.gzkit/rules/complexity-thresholds.md`
- `## Data source-of-truth` (JSON sibling)
- `## Invariant` (one canonical table; downstream consumers do not own thresholds)
- `## Trigger-Semantic Vocabulary (binding)` (block / warn / advise; fourth value forbidden)
- `## Bootstrap absolutes (REQ-11 carve-out)` (radon_mi, lizard_nesting_depth, cohesion_lcom4)
- `## Operator-amendable mapping protocol` (amendments via ADR-0.0.28 ceremony; silent edits forbidden)

### `.gzkit/rules/skill-surface-sync.md`
- `## Non-negotiable rules` (edit `.gzkit/` first; bump version; run sync; never edit mirrors)
- `## Surface layout` (canonical → vendor mirror table)
- `## Procedure` (5 steps)
- `## Version discipline` (major/minor/patch table)
- `## Conflict resolution` (mirror > canonical → promote; equal + diff → recency)

### `.gzkit/rules/model-selection.md`
- `## Operative claims (binding)` (1–4: tier = decision complexity; default lowest tier; explicit `model:` frontmatter; subagent effort levels)
- `## Routing matrix` (haiku for read-only/mechanical; opus for design/refactor)
- `## Skill frontmatter (`model:` directive)`
- `## Subagent effort levels` (light=haiku, high=sonnet, xhigh=opus, max=opus+thinking)

### `.gzkit/rules/cross-platform.md`
- `## Quick Reference` (Paths, encoding, subprocess, line endings)
- `## Render relative paths via `.as_posix()` (binding)`
- `## Console / UTF-8 (binding)` (no `PYTHONUTF8=1` prefix on `uv run gz`)

### `.gzkit/rules/security-sensitivity.md`
- `## Invariant` (security work needs heightened review regardless of lane/kind; third axis is additive)
- `## Registry contract` (data/security_surfaces.json)
- `## `gz validate --sensitivity` (binding)` (auto-detect floor; escalate-not-escape)
- `## Heightened walkthrough` (scanner-unavailable is fail-closed)

### `.gzkit/rules/agent-failure-modes.md`
- Six-pattern taxonomy (Safeguard circumvention / Reckless action / Fabrication / Skipped cheap verification / Correction fails / Dishonest when caught)
- Loading posture: advisory vocabulary, not mechanical gate

### `.gzkit/rules/adr-audit.md`
- `## Audit sequence` (1: `gz adr audit-check`; 2: quality checks; 3: closeout → attest → audit; 4: emit-receipt)
- `## Rules` (don't `gz audit` before attestation; failed audit-check → derive REQ-grounded test, never cosmetic `@covers`)

### `.gzkit/rules/brief-heading-conventions.md`
- OBPI brief evidence sections MUST use H3, not H2
- Canonical evidence sections (H3): Implementation Summary, Key Proof, Closing Argument
- `## Acceptance Criteria` (H2) is top-level brief structure, not per-pass evidence

### `.gzkit/rules/gh-cli.md`
- `## Allowed commands` (defect tracking, issue close, release create)
- `## Prohibited without explicit approval` (repo/org settings, secrets, force pushes)
- `## Cross-repo filing` (consumer repos route gzkit defects to `tvproductions/gzkit`)

### `.gzkit/rules/gate5-runbook-code-covenant.md`
- `## Three-layer documentation model` (runbook / governance runbook / manpages)
- `## Required updates when behavior changes` (docs + runbook + attestation)
- `## Anti-patterns` (placeholder examples; code-without-docs; bundled Gate 5)

### `.gzkit/rules/token-block-discipline.md`
- `## Binding Sub-Invariant 1` — Auditable abandon categories (closed enum)
- `## Binding Sub-Invariant 2` — Register-entry minimum-information rule (timestamp, SHA, decision, branch)
- `## Binding Sub-Invariant 3` — Reaping register-entry rule
- `## Binding Sub-Invariant 4` — TTL canon (24h default; warn @ 12h; reap @ 24h)
- `## Binding Sub-Invariant 5` — Release fail-closed precondition

## Method

For each unordered pair `(rule_a, rule_b)` of the 22 files (231 pairs), the audit asks one question:

> Can these two files disagree on a concrete case?

A `yes` requires a worked example — a specific scenario where rule A and rule B prescribe contradictory behavior. The matrix admits a row only when the example is concrete; "could maybe conflict" rows are excluded per CHORE.md § Policy and Guardrails ("No speculation").

The pairwise walk found 11 substantive disagreement rows. See `conflict-matrix.md`. Severity classification, GHI cross-reference, and prioritized follow-up live in `summary.md`.

## Exclusions and posture

- **Generated subtree readme** (`.gzkit/rules/AGENTS.md`) re-exports `agent-failure-modes.md` and `skill-surface-sync.md` verbatim. Pairings against the subtree readme reduce to pairings against the originals — counted once.
- **Vendor mirrors** (`.claude/rules/*.md`, `.github/instructions/*.md`) are derivatives synthesized by `gz agent sync control-surfaces` and excluded per CHORE.md.
- **JSON data files** (`complexity-thresholds.json`) are out of scope for Pass A — Pass A audits prose rules; data-doctrine drift is the subject of separate validators.
