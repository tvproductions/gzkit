<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Advisory Rules Audit — Mechanical Enforcement Scorecard

**Session date:** 2026-04-18
**Companion doctrine:** [trust-doctrine.md](./trust-doctrine.md)
**Purpose:** Catalog every rule currently stated as agent-facing doctrine in `CLAUDE.md` and `.gzkit/rules/`, score its mechanical-enforceability, and name the highest-leverage candidates for promotion from advisory to fail-closed.

---

## Why this audit exists

The ADR-0.0.16 closeout cascade (trust-doctrine.md § *The 2026-04-18 outage taxonomy*) proved that **advisory rules without mechanical enforcement accumulate invisible drift until one operation stresses all the cracks at once**. Nine concurrent silent failures had been sitting in production for weeks, each individually an honest doctrine violation, collectively a full-session outage.

The lesson: rules that depend on agent discipline are unreliable over long runs, especially under agent rotation and multi-session work. Every rule that *could* be a test *should* be a test.

This audit scores every rule by:

| Score | Meaning |
|---|---|
| **Mechanical** | Already has a fail-closed check (unit test, validator scope, pre-commit hook). No agent discipline required. |
| **Promotable** | Could become mechanical; naming the specific check is tractable. |
| **Judgment** | Requires human or agent judgment by its nature. Mechanical enforcement would overconstrain. |
| **Ambiguous** | Scope is unclear enough that the first step is rule clarification, not mechanization. |

---

## Scorecard

### Architectural Boundaries (`CLAUDE.md` § Architectural Boundaries)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | Do not promote post-1.0 pool ADRs into active work | **Mechanical** | Enforced by `gz validate --pool-adr-isolation` (GHI #208) — scans ledger for pool ADR IDs receiving Gate 1+ events |
| 2 | Do not add more pool ADRs to the runtime track | **Mechanical** | Same audit as #1 — a pool ADR receiving `gate_checked`/`lifecycle_transition`/`attestation`/`obpi_completed`/`adr_audit`/`adr_closeout` is a violation |
| 3 | Do not build the graph engine without locking state doctrine first | **Judgment** | "Locking" is a human decision; can't mechanize ordering of conceptual work |
| 4 | Do not let reconciliation remain a maintenance chore | **Mechanical** | Enforced by `gz validate --reconcile-freshness` (GHI #213) — flags when the latest reconcile ledger event is older than HEAD by more than 24h |
| 5 | Do not let AirlineOps parity become perpetual catch-up | **Judgment** | Requires a metric ("perpetual") that depends on external repo state |
| 6 | Do not let derived views silently become source-of-truth | **Mechanical** | Enforced by `gz validate --frontmatter`, `--event-handlers`, `--validator-fields`. Trust doctrine operationalizes this rule |
| 6a | `gz validate --taxonomy` enforces | **Mechanical** | Enforced by `gz validate --taxonomy` (GHI #218 / ADR-0.0.17) — non-pool ADRs carry `kind: foundation` (semver `0.0.x`) or `kind: feature` (any other semver); pool ADRs (id prefix `ADR-pool.`) derive kind from the id and carry no `kind:` frontmatter |

### Local Agent Rules (`CLAUDE.md` § Local Agent Rules)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 7 | Order versioned identifiers semantically, never lexicographically | **Mechanical** | `gz adr report`/`gz state` sort via `semver` library; tests in `tests/test_adr_status.py` lock the order |
| 8 | Add imports with usage in same Edit | **Judgment** | Meta-rule about agent tool use; the ruff hook removing unused imports IS the enforcement |
| 9 | Never prefix `uv run gz` or `uv run -m gzkit` | **Mechanical** | Enforced by `gz validate --utf8-prefix` (GHI #206) — regex scan across `docs/**`, `.gzkit/skills/**`, `.claude/skills/**`, `features/**` |
| 10 | pass user words verbatim | **Mechanical** | ARB receipt-ID requirement enforced by `gz arb validate`; heavy-lane fail-closed per `.gzkit/rules/attestation-enrichment.md` |
| 11 | Every version bump is a release | **Mechanical** | Enforced by `gz validate --version-release` (GHI #205) — compares `pyproject.toml` version against local `git tag` set for a matching `vX.Y.Z` |
| 12 | Use GitHub gitignore template for `.gitignore` scaffolding | **Judgment** | Only applies to `gz init` / scaffolding skills; hard to mechanize retrospectively |

### Governance Core (`.gzkit/rules/governance-core.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 13 | Read AGENTS.md before implementation work | **Judgment** | Pre-work discipline; no compile-time signal |
| 14 | Use `uv run` for Python command execution | **Mechanical** | Ruff + tests run via `uv run`; CI enforces. Runbook + docs scanned by `gz validate --cli-alignment` for `uv run gz ...` form |
| 15 | Bypass Gate 5 (human attestation) | **Mechanical** | `gz closeout` pipeline enforces attestation before `Completed` lifecycle event |
| 16 | Do not edit `.gzkit/ledger.jsonl` manually | **Mechanical** | Enforced by `.githooks/pre-commit-ledger-guard` (GHI #207) — rejects staged ledger edits that are not strict appends from a registered `gz` command |
| 17 | Every defect must be trackable (GHI or agent-insights.jsonl) | **Judgment** | Enforcement is cultural; no reliable mechanical signal for "defect noticed but not tracked" |
| 17a | `improvement` record to `.gzkit/insights/agent-insights.jsonl` | **Mechanical** | Enforced by `gz validate --insights-shape` (GHI #358) — every record validates against `gzkit.insights.InsightRecord` (`extra="forbid"`, ISO8601 `ts`, `type` enum, `evidence: list[str]`). Pre-lock entries waived by content hash in `_INSIGHTS_SHAPE_WAIVERS`; new writes must conform. Wired into `gz check`. |
| 17b | Per-file char budget for AGENTS.md / CLAUDE.md | **Mechanical** | Enforced by `gz validate --instructions-files-budget` (GHI #373) — each tracked file checked against budget in `data/instructions_files_budget.json` (defaults: 40k chars AGENTS.md/CLAUDE.md, 16k per rule file). Fail-closed (exit 3) on overrun with remediation pointer to `/gz-context-diet`. Wired into `gz check`. |

### Pythonic Standards (`.gzkit/rules/pythonic.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 18 | No bare `except:` / `except Exception:` | **Mechanical** | ruff BLE001 enforces |
| 19 | Functions <=50 lines | **Mechanical** | xenon complexity + pre-commit hooks |
| 20 | Modules <=600 lines | **Mechanical** | Pre-commit check under `.pre-commit-config.yaml` |
| 21 | Classes <=300 lines | **Mechanical** | Enforced by `gz validate --class-size` (GHI #204) — AST scan over `src/gzkit/**`, with explicit `_CLASS_SIZE_WAIVERS` for documented exceptions |
| 22 | No `Optional`/`List` (use `\| None` / `list[]`) | **Mechanical** | ruff UP007, UP006 |
| 23 | no lazy imports | **Promotable** | Partially enforced by ruff PLC0415; inventory of exceptions documented |
| 24 | `# type: ignore` (bare) | **Mechanical** | Enforced by `gz validate --type-ignores` (this audit's direct outcome, GHI #197) |

### Data Models (`.gzkit/rules/models.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 25 | Use **Pydantic `BaseModel`** for all data models; no stdlib `dataclasses` | **Mechanical** | Enforced by `gz validate --pydantic-models` (GHI #203) — AST scan flags `@dataclass` in `src/gzkit/**` unless explicitly waived in `_DATACLASS_WAIVERS` |
| 26 | Use `ConfigDict(frozen=True, extra="forbid")` for immutable models | **Mechanical** | Same audit (`--pydantic-models`) — flags `BaseModel` subclasses missing `model_config = ConfigDict(...)` |
| 27 | Use `str \| None` not `Optional[str]` | **Mechanical** | ruff UP007 |

### Tool / Skill / Runbook Alignment (`.gzkit/rules/tool-skill-runbook-alignment.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 28 | Invariant 1 — Every CLI tool has at least one skill that wields it | **Mechanical** | Enforced by `gz validate --skill-alignment` (GHI #202) — scans every top-level CLI verb; requires at least one skill under `.gzkit/skills/**` unless explicitly waived in `_NO_SKILL_VERBS` |
| 29 | Invariant 2 — Every skill's `gz_command` matches a runbook-prescribed tool | **Promotable** | Invariant 1 landed under GHI #202; Invariants 2 and 3 remain advisory until the skill→runbook cross-reference and output-form fixtures are mechanized |
| 30 | Invariant 3 — Destination verb's default output form | **Promotable** | Requires per-skill output-form fixtures; tracked for a follow-up after #202's Invariant 1 baseline |

### Skill & Surface Sync (`.gzkit/rules/skill-surface-sync.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 31 | Edit `.gzkit/` first | **Mechanical** | `gz agent sync control-surfaces` detects drift; version + commit hash resolution documented |
| 32 | bumping its `skill-version` frontmatter | **Mechanical** | Skill version discipline enforced by sync command; higher version wins |
| 33 | `gz agent sync control-surfaces` | **Mechanical** | Enforced by `.githooks/pre-commit-sync-guard` (GHI #210) — rejects a staged commit that touches `.gzkit/skills/**` or `.gzkit/rules/**` without the corresponding mirror under `.claude/**` or `.github/**` |

### Tests Policy (`.gzkit/rules/tests.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 34 | Red-Green-Refactor TDD discipline | **Judgment** | Cannot mechanically verify "test failed before implementation" after the fact |
| 35 | Eval-feedback-source: | **Mechanical** | `gz validate --commit-trailers` — landed under GHI #201 |
| 36 | Use **stdlib `unittest`**; no pytest | **Mechanical** | `forbid pytest` pre-commit hook |
| 37 | Two runners, one test surface | **Mechanical** | Enforced by `gz validate --test-tiers` (GHI #209) — fails on `tests/{integration,e2e,slow,bdd}/` or forbidden `--integration`/`--e2e`/`--slow`/`--bdd-only` flags re-appearing in `parser_*.py` |
| 38 | Coverage >=40.00% | **Mechanical** | Pre-commit hook |
| 39 | Behave scenarios covering a REQ carry `@REQ-X.Y.Z-NN-MM` | **Mechanical** | Enforced by `gz validate --behave-req-tags` (GHI #211, reversed direction GHI #276) — enumerates heavy-lane OBPI briefs (pool ADRs excluded), extracts REQ-IDs from each brief's Acceptance Criteria, and asserts every REQ has a matching scenario-level `@REQ-*` tag under `features/**`. Heavy OBPIs that defer BDD (schema-only, template-only) register in `data/behave_coverage_waivers.json`. |

### Chores Workflow (`.gzkit/rules/chores.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 54 | Plan-first chore discipline | **Judgment** | Procedural; enforced by `gz chores plan/advise` ordering in the skill |
| 55 | **Lite by default** | **Mechanical** | Lane config enforced by `gz chores plan` |
| 56 | CLI-only evidence (no raw SQL attestation) | **Judgment** | Anti-pattern prevention; cultural |

### ADR Audit (`.gzkit/rules/adr-audit.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 40 | Audit sequence: `gz adr audit-check` → quality checks → closeout lifecycle → emit receipt | **Judgment** | Sequence is procedural; individual steps are mechanically enforced by `gz closeout`/`gz attest`/`gz audit` but ordering is operator discipline |

### Cross-Platform (`.gzkit/rules/cross-platform.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 41 | All file operations use `pathlib.Path` | **Mechanical** | ruff PTH rules enforce |
| 42 | All file I/O specifies `encoding="utf-8"` | **Mechanical** | ruff / unit tests |
| 43 | Use context managers for temp files | **Judgment** | Pattern — hard to mechanize reliably |
| 44 | No `shell=True` in subprocess | **Mechanical** | ruff S602/S603 |
| 45 | The CLI entrypoint handles UTF-8 at startup | **Mechanical** | Rule 9 audit `--utf8-prefix` covers this |
| 45a | fresh `python -c` or helper scripts | **Mechanical** | Enforced by `gz validate --utf8-prefix` (GHI #275 — scope extended from rule-9 prefix scan to gz-pipe patterns in docs/skills/features + `tools/**/*.py` entry-point AST walk) |

### Defect Fix Routing (`.gzkit/rules/defect-fix-routing.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 46 | Direct fix vs OBPI ceremony thresholds (≤10 source lines, ≤2 files, single surface) | **Judgment** | Routing decision requires human scope assessment |
| 47 | Default against over-applying ceremony | **Judgment** | Meta-rule about agent reasoning |

### Gate 5 Runbook-Code Covenant (`.gzkit/rules/gate5-runbook-code-covenant.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 48 | Docs update when command output changes | **Judgment** | Correlation between code change and doc change is not reliably mechanizable |
| 49 | Do not leave placeholder output examples | **Promotable** | Could regex-scan for `<…>` / `TODO` placeholders in runbook/manpages |
| 50 | Heavy/foundation lane requires explicit human attestation before completion | **Mechanical** | Enforced by `gz closeout` pipeline (rule 15 in this scorecard) |

### GitHub CLI Guardrails (`.gzkit/rules/gh-cli.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 51 | Use `gh` only when explicitly requested | **Judgment** | Agent-behavior rule; no compile-time signal |
| 52 | Prohibited commands (settings mutations, secret management, force push, un-authorized merges) | **Judgment** | Permission model lives in `.claude/settings.json`; gh-level enforcement is server-side |
| 53 | Defect tracking: create GHI when fix deferred | **Judgment** | Cultural enforcement; see rule 17 |

### Agent Contract (folded into `AGENTS.md` / `CLAUDE.md` / `docs/governance/agent-contract-rationale.md`)

*File consolidated 2026-04-21 — merged from the former `behavioral-invariants.md` (positive invariants — Do) and `constraints.md` (negative constraints — Do not) to close the dual-framing co-load drift that Pass A of the control-surface audit surfaced.*

*Folded 2026-04-22 under ADR-0.0.20 OBPI-02 — the unique invariants (6c, 6g, 6h, judgment 12–14, Pipeline lifecycle and State doctrine "Never" items) moved into `AGENTS.md`; the Claude-specific invariant 10a moved into `CLAUDE.md` § Claude Code addendum; the pedagogy (anti-pattern canon, TASK-driven workflow, Lindsey 2025 rationale for 6g/6h) moved into `docs/governance/agent-contract-rationale.md`. The canonical `.gzkit/rules/agent-contract.md` rule file was deleted.*

The `Do not` section is a cross-reference aggregator; every entry maps to one of the rules scored above. Its meta-rule ("these prohibitions are addressed to you — the executing agent") is **judgment** — the document's purpose is behavioral guidance for Claude Code sessions, not a mechanical gate.

The `Do` section (Invariants #1–17) is primarily **judgment** rules aimed at agent tool use and session behavior:

- "Own the work completely" / "Complete all work fully" / "Never say out of scope" — judgment
- "Fix class of failure, not instance" — judgment (but this audit itself is an instance of applying it)
- "Read AGENTS.md before starting work" — judgment
- "If <90% sure, ask the human" — judgment
- "On inconsistencies, STOP, name confusion, present tradeoff, wait" — judgment
- "When the operator course-corrects in flight, append an `improvement` record to `.gzkit/insights/agent-insights.jsonl` before completing the corrected work" (Behavior Rules — Always #11, GHI #357) — **judgment** at authoring time (recognizing a correction); the schema-lock side is now mechanical via `gz validate --insights-shape` (GHI #358; see scorecard row 17a)

**Invariant #10a** ("When a skill step names a tool, invoke it in the same turn") is **promotable** — could be detected via hook analysis, but the signal-to-noise ratio is probably poor.

### Agent Rule Placement Invariant (`ADR-0.0.20`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 47 | `.gzkit/rules/*.md` with `paths: "**"` or missing `paths:` may not live under any vendor-surface rules directory | **Mechanical** | `gz validate --unscoped-rules` — enumerates canonical rule files, parses YAML frontmatter, and fails closed on any file carrying `paths: "**"` or missing `paths:` without an allow-listed exception under `rules.unscoped_allowlist` in `.gzkit/manifest.json`. Runs as part of the `--audits` aggregate and `gz check`. Exit codes per `cli.md` 4-code map: 0 clean, 2 I/O error, 3 policy breach. Allow-list schema enforced via Pydantic (`UnscopedAllowlistEntry`) and `src/gzkit/schemas/manifest.json`. |

### ARB middleware (now hosted in `.gzkit/rules/attestation-enrichment.md`)

*File merged 2026-04-21 — the former `.gzkit/rules/arb.md` carried a duplicate lane matrix that drifted from the canonical table in `attestation-enrichment.md`. The unique ARB material (core concept, available commands, receipt schema, exit codes) moved into `attestation-enrichment.md`; the duplicate lane matrix was dropped. The canonical invocations table lives at one home (scorecard rows above still apply; the file path changed but the mechanical enforcement did not).*

### Security Sensitivity (`.gzkit/rules/security-sensitivity.md`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 48 | Security work needs heightened review regardless of lane or kind. | **Mechanical** | Enforced by `gz validate --sensitivity` (ADR-0.0.22) — `audit_sensitivity_binding` in `src/gzkit/governance/trust_audits.py` runs floor + escalate-not-escape against the registry; audit OR-branch `_requires_security_review_attestation` at `src/gzkit/commands/adr_audit.py` forces brief-level human attestation on every `sensitivity: security` brief regardless of lane or kind; canonical security-scan ARB step is reserved in `CANONICAL_STEP_COMMANDS` so receipt absence fails Gate 5 walkthrough. Mirror discipline by `gz agent sync control-surfaces`. |

### Agent Failure-Mode Taxonomy (`.gzkit/rules/agent-failure-modes.md`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 49 | Six-pattern agent failure-mode vocabulary (`Safeguard circumvention` / `Reckless action` / `Fabrication` / `Skipped cheap verification` / `Correction fails` / `Dishonest when caught`) — drawn from Opus 4.7 § 2.3.6 (Anthropic, 2026-04-16) and corroborated by GPT-5.5 § 9.2 (OpenAI, 2026-04-23). Cited by name when reviewing PRs, filing defects, and extending the scorecard; routes the conversation directly to the engineered backstop instead of re-deriving the failure motivation each time. | **Judgment** | Vocabulary, not mechanical check. The mechanical defenses already exist as separate rules and gates — TTY + `ATTEST` authenticity gate at `_enforce_human_attestation_authenticity` (`src/gzkit/commands/adr_audit.py`), ARB receipt requirements (`AGENTS.md` § Attestation), hook fail-closed behavior, `gz validate --commit-trailers`, layered-trust T1/T2/T3 invariants — and this rule is the **shared name** they point at. Promotion candidate `gz validate --failure-mode-coverage` (a self-test confirming every scorecard row names the failure shape it backstops) tracked under follow-up GHIs #308–#312 per ADR-0.0.23 § Decision. |

### Model Selection (`.gzkit/rules/model-selection.md`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 52 | Every skill SKILL.md declares `model: haiku\|sonnet\|opus` frontmatter; `SkillFrontmatter.skill_model` is `Literal["haiku", "sonnet", "opus"]` (required). Routing matrix maps decision complexity to model tier. Subagents use effort levels, not hardcoded model IDs. | **Mechanical** | Enforced by `gz validate --surfaces` via `SkillFrontmatter` Pydantic validation — missing or invalid `model:` fails closed. All 67 skills declare tier (GHI #409). |

### Verdict <-> Proof Binding (validator-only; binding declared by `src/gzkit/schemas/advisor_diagnosis.json` + `src/gzkit/complexity/advisor/diagnosis.py`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 54 | `Field(min_length=1)` on `AdvisorDiagnosis.proof` | **Mechanical** | Enforced by `gz validate --advisor-proof-binding` (OBPI-0.0.29-08, `src/gzkit/governance/trust_audits/advisor_proof_binding.py`) — fails closed (exit 1) on (a) any fixture under `tests/fixtures/advisor/*.json` whose top-level `proof` array is empty, (b) any `intrinsic-complexity-attestation` ledger event whose payload references a diagnosis id whose fixture has empty proof, or (c) `src/gzkit/schemas/advisor_diagnosis.json` whose `properties.proof.minItems` is missing or `< 1`. Speculative-marker escape: a fixture's top-level `"_negative_case": true` skips it (the OBPI-01 model test that asserts `ValidationError` on empty proof is the test of the defense, not a defect). Wired into `--all` aggregation and `gz check` (`_run_scope_checks` opt-in scope). Behave scenarios at `features/advisor_proof_binding.feature` cover the two canonical failure paths (REQ-0.0.29-08-02: empty fixture; REQ-0.0.29-08-03: ledger event citing empty-proof diagnosis). Validator validated by `tests/governance/test_advisor_proof_binding_validator.py` (16 tests across fixture, ledger, schema, error-message-quality, and CLI-integration test classes). Scorecard citation: ADR-0.0.29 (parent), OBPI-0.0.29-01 (model layer), OBPI-0.0.29-02 (engine layer), OBPI-0.0.29-08 (validator layer). |

### Constitutional Invariant Composition (ADR-0.0.37 / OBPI-0.0.37-03)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 58 | `gz validate --invariant-coherence` — composition drift fail-close | **Mechanical** | Enforced by `gz validate --invariant-coherence` (OBPI-0.0.37-03, `src/gzkit/governance/trust_audits/invariant_coherence.py`) — fails closed (exit 3) on byte-drift between the rendered constitutional invariant registry output and the committed AGENTS.md. Emits `composition_rendered` event on every invocation; additionally emits `composition_drift_detected` event with diff payload on drift. Included in `gz check` default scope list (REQ-0.0.37-03-05). Validator validated by `tests/governance/test_invariant_coherence.py` (17 tests across match-no-drift, mismatch-drift, event-emission, schema-registration, gz-check-default test classes). Scorecard citation: ADR-0.0.37 (parent), OBPI-0.0.37-01 (registry primitive), OBPI-0.0.37-02 (composition renderer), OBPI-0.0.37-03 (validator). |

### Brief Reconciliation Invariant (CIC-2) (`ADR-0.0.37` / OBPI-0.0.37-05)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 59 | OBPI brief reconciles against current project shape before Stage 2 and before completion | **Mechanical** | Enforced by `gz validate --brief-reconcile` (OBPI-0.0.37-05, `src/gzkit/governance/trust_audits/brief_reconcile.py`) — walks all OBPI briefs under `docs/design/adr/**/{obpis,briefs}/`, computes per-dimension delta across five drift classes (allowlist coherence, Discovery Checklist path existence, Verification verb resolution against parser registry, REQ-count parity against Acceptance Criteria, citation-tuple file existence); reports ERROR severity per dimension with drift; routed to exit 3 via `_POLICY_BREACH_ERROR_TYPES`. Enforcement scope: drift is escalated only for briefs that parse as a structured `BriefStructure` — legacy briefs are walked and reconciled but not escalated, honoring OBPI-0.0.37-04's permissive-mode deprecation window; the validator scope widens automatically as briefs migrate to structured frontmatter. Scorecard citation: ADR-0.0.37 (parent), OBPI-0.0.37-05 (engine), OBPI-0.0.37-06 (CLI verb, pending). |

### Token Block Discipline (`.gzkit/rules/token-block-discipline.md`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 53 | abandon categories are closed | **Promotable** | Doctrine exists in the rule file and parent ADR-0.0.41, but OBPI-0.0.41-02/03/04 are still pending for runtime warning/fail-closed enforcement and `gz validate --lock-handoff-coupling`. Until those land, this is a promotable rule with a clear mechanical path rather than already-mechanical enforcement. |

### Exemplar Corpus Doctrine (`.gzkit/rules/complexity-doctrine.md`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 50 | empirically-measured exemplar corpus | **Mechanical** | Enforced by `gz validate --complexity-doctrine-links` (OBPI-0.0.27-07, `src/gzkit/governance/trust_audits/complexity_doctrine_links.py`) — fails closed (exit 3) when cluster ADRs (0.0.27/0.0.28/0.0.29/0.0.30) or `.gzkit/rules/complexity-doctrine.md` cite distilled-characteristics documents that do not exist, anchors that do not resolve, or `corpus_revision` values outside the supported portability window. Two-signal heuristic (`§` + `(corpus revision`) gates the citation candidate set; HTML-comment speculative-skip marker (`<!-- gz-validate-skip: complexity-doctrine-links -->`) supported. Wired into `gz check` via the "Complexity-doctrine links" runner so pre-merge gates fire automatically. Selection methodology criteria are pinned in `.gzkit/rules/complexity-doctrine.md` and validated by `tests/governance/test_complexity_doctrine_rule.py`. Scorecard citation: ADR-0.0.27 (parent), OBPI-0.0.27-07 (link-integrity enforcement). |

### Complexity Thresholds (`.gzkit/rules/complexity-thresholds.{md,json}`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 51 | `(metric, percentile-band, absolute-number, trigger-semantic)` tuple | **Mechanical** | Enforced by `gz validate --complexity-thresholds` (OBPI-0.0.28-03, `src/gzkit/governance/trust_audits/complexity_thresholds.py`) — fails closed (exit 3) on missing `block` band per metric, missing percentile + absolute pairing, trigger-semantic outside the three-value enum, unparseable citation tuple, or canonical-metric coverage gap. Bootstrap-mode carve-out emits an informational stdout notice (non-policy-breach). The `ThresholdTable` Pydantic loader at `src/gzkit/complexity/thresholds.py` (OBPI-0.0.28-02) is the runtime contract that ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance bind against; the loader's Pydantic field validators close the loader-layer half of the invariant. Selection-methodology and citation-tuple form inherited from `.gzkit/rules/complexity-doctrine.md` (rule 50) — the threshold table cites that doctrine's distilled-characteristics document at corpus revision 1. Wired into `gz check` via the "Complexity-thresholds" runner; behave scenarios under `features/complexity_thresholds.feature` cover the four canonical failure paths (missing block band, off-enum percentile, malformed citation, bootstrap-mode notice). Rule body validated by `tests/governance/test_complexity_thresholds_rule.py`; validator validated by `tests/governance/test_complexity_thresholds_validator.py`. Scorecard citation: ADR-0.0.28 (parent), OBPI-0.0.28-02 (loader), OBPI-0.0.28-03 (validator-as-enforcement). |

### Editor/IDE Protocol Surface (`.gzkit/schemas/authoring_guide_protocol.json`)

| # | Rule | Score | Why |
|---|------|-------|-----|
| 55 | src/gzkit/schemas/authoring_guide_protocol.json | **Mechanical** | Enforced by `src/gzkit/schemas/authoring_guide_protocol.json` validation in the protocol server (`gz complexity guide --server`); message payload validation happens at parse time (before handler dispatch), so schema evolution (adding required fields, renaming envelopes, changing encoding) is fail-closed at request/response boundaries. Scorecard citation: ADR-0.0.30 (parent), OBPI-0.0.30-04 (protocol server implementation). |

### Distribution Invariant Doctrine (T0) (`docs/governance/trust-doctrine.md` T0 layer + `ADR-0.0.31`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 57 | byte-equivalent to the wheel's authored canonical content | **Mechanical** | Enforced by `gz validate --distribution` (OBPI-0.0.32-07, `src/gzkit/governance/trust_audits/distribution.py`) — static check against `pyproject.toml` include globs + `data/distribution_baseline_manifest.json` + on-disk canonical surface trees; detects three drift classes (ON\_DISK\_NOT\_INCLUDED / BASELINE\_NOT\_ON\_DISK / ON\_DISK\_NOT\_BASELINE); exit 3 on any drift; exit 2 on system error. Receipt-id prefix: `arb-distribution-`. |

### Map-Not-Encyclopedia Doctrine (`.gzkit/rules/agents-md-map-doctrine.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 58 | AGENTS.md MUST contain only binding bullets, structured tables, and canonical-link references; MUST NOT contain multi-paragraph rationale prose, worked examples, anti-pattern catalogs, "Why this is canon" blockquotes, narrative pedagogical sections, or operative-claims expansions already stated in binding-bullet form | **Mechanical** (shape invariant); per-section size targets remain **Judgment** | Shape check forthcoming as `gz validate --agents-md-map-conformance` (OBPI-0.0.54-03). Budget tightening (AGENTS.md 40000→15000, CLAUDE.md 40000→4000) enforced by `gz validate --instructions-files-budget` (OBPI-0.0.54-01 / ADR-0.0.54). Per-section size targets live in ADR-0.0.54 § Intent TOC table and require human judgment. Canonical expansion: `docs/governance/agents-md-doctrine.md`. |

### REQ Scope Discipline (`.gzkit/rules/tests.md` § REQ Scope Discipline)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 59 | Every REQ in an OBPI brief's Acceptance Criteria MUST declare exactly one of three kinds — BEHAVIOR, SUPPORT, or STRUCTURAL-FENCE — via an inline tag `[kind]`; each kind has exactly one proof channel (BEHAVIOR → `@covers` test; SUPPORT → ledger event + structural validator; STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` entry) | **Mechanical** | `gz validate --req-kind-discipline` (OBPI-0.0.59-02 scope) fail-closes brief-time on missing `[kind]` tags and per-kind proof-citation gaps. Three-kind taxonomy is a closed StrEnum; brief-authoring scaffold prompts for kind (OBPI-0.0.59-02); parity gate consumes per-kind proof channels (OBPI-0.0.59-03). Added by OBPI-0.0.59-01 (2026-05-26). ADR-0.0.59. Canonical expansion: `docs/governance/req-scope-discipline.md`. |

### TASK Discovery (`.gzkit/rules/task-discovery.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 60 | Every unit of labor traceable to a TASK MUST surface that attribution through at least one of four discovery channels | **Promotable** | Python `@advances` decorator landed in OBPI-0.0.64-02 with decoration-time fail-close on invalid TASK IDs and unknown parent REQs (mirrors `@covers` machinery). Commit-trailer channel already enforced by `gz validate --commit-trailers`. Ledger `task_id` channel added in OBPI-0.0.64-01. Frontmatter `tasks:` schema enforcement and four-channel coherence validator (`gz validate --task-envelope-coherence`) deferred to OBPI-0.0.64-04. Parent ADR-0.0.64. |

### Guardrail Feedback Prose (`.gzkit/rules/guardrail-feedback-prose.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 61 | Every fail-closed hook and validator emits agent-actionable three-part recovery prose: what failed, why it is forbidden (cited rule/invariant), the governed next step (runnable command or named ceremony) | **Promotable** | Authored under ADR-0.0.70 (Buetow adoption: "the feedback encodes the prompt you would write as a human"). First enforcement consumer is `stop-turn-feedback.py`, whose block prose is asserted against the bar by `tests/hooks/test_stop_turn_feedback.py` (REQ-0.0.70-03-02). Promotion path named in the rule: a `gz validate` scope asserting the three-part shape on hook/validator output fixtures once catch evidence accumulates — deliberately deferred (an inferential prose-grader is weaker than a real enforcement consumer; ADR-0.0.70 § Decision). |

### MX Mode (`.gzkit/rules/mx-mode.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 62 | Honor the marker: when `.gzkit/mx-active` exists, most guards drop to advisory | **Promotable** | The marker-check is structural (file exists/not); the awareness hook (`src/gzkit/mx/awareness.py`) fires per-turn but liveness is advisory. Could promote to fail-closed via a `gz validate --mx-marker-coherence` scope that confirms guard fatality state is consistent with marker presence. Parent ADR-0.0.74. |
| 63 | PRIME DIRECTIVE binds the entire hangar session — ownership never relaxes; operate the skill, not the shell | **Judgment** | "Fix what you know AND what you find; 'not my work' stays forbidden in the bay" requires agent judgment to apply. Mechanizing ownership is the broader gzkit mission, not a single validator scope. |

---

## Summary

Counts updated 2026-05-26 after REQ Scope Discipline taxonomy added as Mechanical (OBPI-0.0.59-01 / ADR-0.0.59). Per-section size targets remain Judgment.

| Score | Count | % |
|-------|-------|---|
| **Mechanical** | 43 | 64% |
| **Promotable** | 6 | 9% |
| **Judgment** | 19 | 28% |
| **Ambiguous** | 0 | 0% |

**The mechanical floor rose from 30 % to 62 %** under the #202–#215 promotion wave plus ADR-0.0.20's rule-placement invariant. Eleven advisory rules were mechanized as `gz validate --<scope>` flags and two became pre-commit guards under `gzkit.hooks.guards`. ADR-0.0.22 added the security-sensitivity third axis as `gz validate --sensitivity`, lifting the floor by a further point. ADR-0.0.23 OBPI-02 added the **Judgment**-classed agent failure-mode taxonomy as shared reviewer vocabulary (mechanical promotion `gz validate --failure-mode-coverage` tracked under follow-up GHIs #308–#312). ADR-0.0.27 OBPI-01 added the **Mechanical**-classed exemplar-corpus doctrine rule. ADR-0.0.28 OBPI-01 added the **Mechanical**-classed complexity-thresholds rule (forthcoming `gz validate --complexity-thresholds` validator under OBPI-0.0.28-03). ADR-0.0.30 OBPI-04 added the **Mechanical**-classed editor/IDE protocol surface rule, with envelope validation enforced by JSON Schema. ADR-0.0.31 OBPI-02 added the T0 distribution invariant rule, promoted to **Mechanical** in OBPI-0.0.32-07 via `gz validate --distribution` (static check: pyproject.toml include + baseline manifest + on-disk canonical trees, exit 3 on any drift class). ADR-0.0.37 OBPI-05 added the **Mechanical**-classed brief-reconciliation invariant (CIC-2) rule, enforced by `gz validate --brief-reconcile`. ADR-0.0.54 OBPI-01 added the **Mechanical** (shape) / **Judgment** (per-section size) Map-Not-Encyclopedia doctrine rule, with shape enforcement forthcoming as `gz validate --agents-md-map-conformance` (OBPI-0.0.54-03) and budget tightening (AGENTS.md 40k→15k, CLAUDE.md 40k→4k) enforced now by `gz validate --instructions-files-budget`. ADR-0.0.59 OBPI-01 added the **Mechanical**-classed REQ Scope Discipline taxonomy rule (three-kind BEHAVIOR/SUPPORT/STRUCTURAL-FENCE with per-kind proof channels), with `gz validate --req-kind-discipline` forthcoming under OBPI-0.0.59-02. The remaining Promotable band (Invariants 2/3 of the tool-skill-runbook rule, lazy imports, runbook placeholders, etc.) is tracked for follow-up waves.

---

## Recommended promotion order (highest leverage first)

> **FROZEN — 2026-06-08 (governance-subtraction, track 2 / reading A).** This
> backlog is no longer a burn-down list. The mechanical floor (64%) is judged
> sufficient; the imbalance to correct now is *too much* mechanism, not too
> little. Promotion is opt-in-with-justification: a new mechanical check is added
> only when a *specific, observed* drift instance justifies it. The discipline
> below still governs *how* to promote — it no longer implies that every
> Promotable row *should* be promoted. The remaining Promotable rows stay
> advisory by default.
>
> **Subtraction now has equal standing.** A mechanism that misfires, over-fires,
> gives false assurance, or only guards other mechanism is removed with *named
> steering-failure evidence* (the same evidence-bearing bar this scorecard set
> for promotion — write the case, show the failure, then cut). This operates
> under the existing anti-vibing operative claim *"volume follows steering
> need"*; it does **not** amend *"never maintenance burden or velocity"* — burden
> alone is still not a removal rationale; degraded steering is. First subtraction
> increment landed this date (3 wrapper chores; see CHANGELOG / agent-insights).

Each promotion candidate has a tracking GHI. Close the GHI when the promotion lands per the discipline in § Promotion discipline below.

| # | Rule(s) | GHI | Summary | Landed as |
|---|---------|-----|---------|-----------|
| 1 | 28 (Inv 1) | [#202](https://github.com/tvproductions/gzkit/issues/202) | Every CLI verb has a wielding skill | `gz validate --skill-alignment` |
| 2 | 25 / 26 | [#203](https://github.com/tvproductions/gzkit/issues/203) | Pydantic `BaseModel` + `ConfigDict` discipline | `gz validate --pydantic-models` |
| 3 | 21 | [#204](https://github.com/tvproductions/gzkit/issues/204) | Class size limit (300 lines) | `gz validate --class-size` |
| 4 | 11 | [#205](https://github.com/tvproductions/gzkit/issues/205) | Version bump → git tag alignment | `gz validate --version-release` |
| 5 | 9 | [#206](https://github.com/tvproductions/gzkit/issues/206) | No `PYTHONUTF8=1` prefix on `uv run gz` | `gz validate --utf8-prefix` |
| 6 | 16 | [#207](https://github.com/tvproductions/gzkit/issues/207) | No manual ledger edits (pre-commit guard) | `gzkit.hooks.guards.forbid_manual_ledger_edits` |
| 7 | 1 / 2 | [#208](https://github.com/tvproductions/gzkit/issues/208) | Pool ADRs never receive runtime-track events | `gz validate --pool-adr-isolation` |
| 8 | 37 | [#209](https://github.com/tvproductions/gzkit/issues/209) | No third test tier under `unittest` | `gz validate --test-tiers` |
| 9 | 33 | [#210](https://github.com/tvproductions/gzkit/issues/210) | Sync after every skill/rule edit | `gzkit.hooks.guards.forbid_skill_sync_drift` |
| 10 | 39 | [#211](https://github.com/tvproductions/gzkit/issues/211) | Behave scenarios tagged `@REQ-X.Y.Z-NN-MM` | `gz validate --behave-req-tags` |
| 11 | meta | [#212](https://github.com/tvproductions/gzkit/issues/212) | Scorecard self-test | `gz validate --advisory-scorecard` |
| 12 | 4 | [#213](https://github.com/tvproductions/gzkit/issues/213) | Reconcile freshness audit | `gz validate --reconcile-freshness` |
| 13 | 6 (extension) | [#214](https://github.com/tvproductions/gzkit/issues/214) | L3 derived-view inventory | `docs/governance/layer-three-derived-views.md` |
| 14 | discoverability | [#215](https://github.com/tvproductions/gzkit/issues/215) | Wire trust-doctrine + scorecard into agent surfaces | `agents.local.md` + mirror sync |
| 15 | brief-heading-conventions | [#238](https://github.com/tvproductions/gzkit/issues/238) | Brief evidence sections must use H3 (not H2) | `gz validate --brief-headings` |
| 16 | 45a (scope-boundary subsection) | [#275](https://github.com/tvproductions/gzkit/issues/275) | Fresh-interpreter helpers + non-Python pipes + `tools/**/*.py` reconfigure | `gz validate --utf8-prefix` (extends row 5) |
| 17 | 47 (ADR-0.0.20) | ADR-0.0.20 | Agent rule placement invariant: no `paths: "**"` under vendor rule dirs | `gz validate --unscoped-rules` |
| 18 | 48 (ADR-0.0.22) | ADR-0.0.22 | Security-sensitivity third axis: floor + escalate-not-escape + heightened walkthrough | `gz validate --sensitivity` (+ `_requires_security_review_attestation` audit OR-branch + reserved `arb-step-security-scan-*` ARB slot) |
| 19 | brief-cross-references | [#436](https://github.com/tvproductions/gzkit/issues/436) | Bare `OBPI-X.Y.Z-NN` / `ADR-X.Y.Z` identifiers in briefs must resolve to on-disk artifacts; speculative-skip marker `<!-- gz-validate-skip: brief-cross-references -->` for forward-reference cases | `gz validate --brief-cross-references` |
| 20 | brief-demo-section | [#431](https://github.com/tvproductions/gzkit/issues/431) | Heavy-lane CLI-shipping briefs (Allowed Paths intersect `src/gzkit/cli/parser_artifacts.py` or `src/gzkit/commands/*.py`) must carry a `## Demo` H2 section before completion so the closeout walkthrough does not fall back to `--help`; terminal-status briefs grandfathered; speculative-skip marker `<!-- gz-validate-skip: brief-demo-section -->` for genuine exemptions | `gz validate --brief-demo-section` |

Invariants 2 and 3 of the tool-skill-runbook rule (rows 29/30 above) remain Promotable — Invariant 1 landed first to establish the waiver shape for the harder body/output-form scans.

---

## Promotion discipline

When promoting an advisory rule to mechanical:

1. **Write the audit first.** It fails. You observe real current violations (or none). Don't write the audit against a clean state you assumed — you'll miss drift that's already in.
2. **Fix or waive the current violations.** Waivers are explicit dict entries with rationale; silent pass-lists are anti-pattern (trust doctrine T2).
3. **Promote the audit into `gz validate` as a named scope.** Discoverable via `--help`, runnable at pre-commit.
4. **Delete or narrow the advisory rule text.** The rule is now mechanical; the doctrine file can drop the admonition and point at the audit. Doctrine that's mechanical is doctrine that survives agent rotation.

This audit is itself a candidate for promotion: the catalog above could be a test that fails when a new rule is added without a score. That would make the audit self-sustaining. Left as a follow-up — the scorecard shape is still stabilizing.

---

## Related

- `docs/governance/trust-doctrine.md` — the pattern this scorecard supports
- `docs/governance/state-doctrine.md` — storage-layer doctrine; complement to trust doctrine
- `docs/governance/layer-three-derived-views.md` — L3 view inventory and remaining audit gaps (GHI #214)
- `AGENTS.md` § Prime Directive / § DO IT RIGHT / § Behavior Rules — the cross-reference index of these rules (Do / Do not framings), folded in from the former `.gzkit/rules/agent-contract.md` under ADR-0.0.20 OBPI-02
- `docs/governance/agent-contract-rationale.md` — pedagogy extracted from the rule file: anti-pattern canon, TASK-driven workflow, 6g/6h rationale
- `CLAUDE.md` — architectural-boundaries memo (rules 1–6 in scorecard)
