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

### Local Agent Rules (`CLAUDE.md` § Local Agent Rules)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 7 | Order versioned identifiers semantically, never lexicographically | **Mechanical** | `gz adr report`/`gz state` sort via `semver` library; tests in `tests/test_adr_status.py` lock the order |
| 8 | Add imports with usage in same Edit | **Judgment** | Meta-rule about agent tool use; the ruff hook removing unused imports IS the enforcement |
| 9 | Never prefix `uv run gz` with `PYTHONUTF8=1` | **Mechanical** | Enforced by `gz validate --utf8-prefix` (GHI #206) — regex scan across `docs/**`, `.gzkit/skills/**`, `.claude/skills/**`, `features/**` |
| 10 | Attestation enrichment (pass user words + enrichment + receipt IDs) | **Mechanical** | ARB receipt-ID requirement enforced by `gz arb validate`; heavy-lane fail-closed per `.gzkit/rules/attestation-enrichment.md` |
| 11 | Every version bump → GitHub release | **Mechanical** | Enforced by `gz validate --version-release` (GHI #205) — compares `pyproject.toml` version against local `git tag` set for a matching `vX.Y.Z` |
| 12 | Use GitHub gitignore template for `.gitignore` scaffolding | **Judgment** | Only applies to `gz init` / scaffolding skills; hard to mechanize retrospectively |

### Governance Core (`.gzkit/rules/governance-core.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 13 | Read AGENTS.md before implementation work | **Judgment** | Pre-work discipline; no compile-time signal |
| 14 | Use `uv run` for Python command execution | **Mechanical** | Ruff + tests run via `uv run`; CI enforces. Runbook + docs scanned by `gz validate --cli-alignment` for `uv run gz ...` form |
| 15 | Do not bypass Gate 5 for Heavy/Foundation | **Mechanical** | `gz closeout` pipeline enforces attestation before `Completed` lifecycle event |
| 16 | Do not edit `.gzkit/ledger.jsonl` manually | **Mechanical** | Enforced by `.githooks/pre-commit-ledger-guard` (GHI #207) — rejects staged ledger edits that are not strict appends from a registered `gz` command |
| 17 | Every defect must be trackable (GHI or agent-insights.jsonl) | **Judgment** | Enforcement is cultural; no reliable mechanical signal for "defect noticed but not tracked" |

### Pythonic Standards (`.gzkit/rules/pythonic.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 18 | No bare `except:` / `except Exception:` | **Mechanical** | ruff BLE001 enforces |
| 19 | Functions ≤50 lines | **Mechanical** | xenon complexity + pre-commit hooks |
| 20 | Modules ≤600 lines | **Mechanical** | Pre-commit check under `.pre-commit-config.yaml` |
| 21 | Classes ≤300 lines | **Mechanical** | Enforced by `gz validate --class-size` (GHI #204) — AST scan over `src/gzkit/**`, with explicit `_CLASS_SIZE_WAIVERS` for documented exceptions |
| 22 | No `Optional`/`List` (use `\| None` / `list[]`) | **Mechanical** | ruff UP007, UP006 |
| 23 | Top-level imports only (no lazy imports) | **Promotable** | Partially enforced by ruff PLC0415; inventory of exceptions documented |
| 24 | Suppress ty diagnostics via `# ty: ignore[<code>]` or bare `# type: ignore` | **Mechanical** | Enforced by `gz validate --type-ignores` (this audit's direct outcome, GHI #197) |

### Data Models (`.gzkit/rules/models.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 25 | All data models use Pydantic `BaseModel` (no stdlib `dataclass`) | **Mechanical** | Enforced by `gz validate --pydantic-models` (GHI #203) — AST scan flags `@dataclass` in `src/gzkit/**` unless explicitly waived in `_DATACLASS_WAIVERS` |
| 26 | Immutable models use `ConfigDict(frozen=True, extra="forbid")` | **Mechanical** | Same audit (`--pydantic-models`) — flags `BaseModel` subclasses missing `model_config = ConfigDict(...)` |
| 27 | Use `str \| None` not `Optional[str]` | **Mechanical** | ruff UP007 |

### Tool / Skill / Runbook Alignment (`.gzkit/rules/tool-skill-runbook-alignment.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 28 | **Invariant 1** — Every CLI tool has a wielding skill | **Mechanical** | Enforced by `gz validate --skill-alignment` (GHI #202) — scans every top-level CLI verb; requires at least one skill under `.gzkit/skills/**` unless explicitly waived in `_NO_SKILL_VERBS` |
| 29 | **Invariant 2** — Every skill's `gz_command` matches a runbook-prescribed tool | **Promotable** | Invariant 1 landed under GHI #202; Invariants 2 and 3 remain advisory until the skill→runbook cross-reference and output-form fixtures are mechanized |
| 30 | **Invariant 3** — Destination verb's default output matches routing skill's Output Contract | **Promotable** | Requires per-skill output-form fixtures; tracked for a follow-up after #202's Invariant 1 baseline |

### Skill & Surface Sync (`.gzkit/rules/skill-surface-sync.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 31 | Edit `.gzkit/` first; never edit vendor mirrors | **Mechanical** | `gz agent sync control-surfaces` detects drift; version + commit hash resolution documented |
| 32 | Bump `skill-version` on every skill edit | **Mechanical** | Skill version discipline enforced by sync command; higher version wins |
| 33 | Run sync after every skill/rule edit | **Mechanical** | Enforced by `.githooks/pre-commit-sync-guard` (GHI #210) — rejects a staged commit that touches `.gzkit/skills/**` or `.gzkit/rules/**` without the corresponding mirror under `.claude/**` or `.github/**` |

### Tests Policy (`.gzkit/rules/tests.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 34 | Red-Green-Refactor TDD discipline | **Judgment** | Cannot mechanically verify "test failed before implementation" after the fact |
| 35 | Every commit touching src/tests carries Task: or Ceremony: trailer | **Mechanical** | `gz validate --commit-trailers` — landed under GHI #201 |
| 36 | Use stdlib `unittest` (no pytest) | **Mechanical** | `forbid pytest` pre-commit hook |
| 37 | Two runners: unittest + behave (no tier under unittest) | **Mechanical** | Enforced by `gz validate --test-tiers` (GHI #209) — fails on `tests/{integration,e2e,slow,bdd}/` or forbidden `--integration`/`--e2e`/`--slow`/`--bdd-only` flags re-appearing in `parser_*.py` |
| 38 | Coverage floor ≥40% | **Mechanical** | Pre-commit hook |
| 39 | Behave scenarios covering a REQ carry `@REQ-X.Y.Z-NN-MM` tag | **Mechanical** | Enforced by `gz validate --behave-req-tags` (GHI #211) — scans Heavy/Foundation OBPIs for REQ-IDs without matching scenario-level `@REQ-*` tags |

### Chores Workflow (`.gzkit/rules/chores.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 54 | Plan-first chore discipline | **Judgment** | Procedural; enforced by `gz chores plan/advise` ordering in the skill |
| 55 | Lite lane by default (<=60s, unit tests only) | **Mechanical** | Lane config enforced by `gz chores plan` |
| 56 | CLI-only evidence (no raw SQL attestation) | **Judgment** | Anti-pattern prevention; cultural |

### ADR Audit (`.gzkit/rules/adr-audit.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 40 | Audit sequence: `gz adr audit-check` → quality checks → closeout lifecycle → emit receipt | **Judgment** | Sequence is procedural; individual steps are mechanically enforced by `gz closeout`/`gz attest`/`gz audit` but ordering is operator discipline |

### Cross-Platform (`.gzkit/rules/cross-platform.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 41 | Use `pathlib.Path` for file paths | **Mechanical** | ruff PTH rules enforce |
| 42 | Specify `encoding="utf-8"` on file I/O | **Mechanical** | ruff / unit tests |
| 43 | Use context managers for temp files | **Judgment** | Pattern — hard to mechanize reliably |
| 44 | Subprocess list form (no `shell=True`) | **Mechanical** | ruff S602/S603 |
| 45 | Runtime UTF-8 config in entrypoint (no env-var prefix) | **Mechanical** | Rule 9 audit `--utf8-prefix` covers this |

### Defect Fix Routing (`.gzkit/rules/defect-fix-routing.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 46 | Direct fix vs OBPI ceremony thresholds (≤10 source lines, ≤2 files, single surface) | **Judgment** | Routing decision requires human scope assessment |
| 47 | Default against over-applying ceremony | **Judgment** | Meta-rule about agent reasoning |

### Gate 5 Runbook-Code Covenant (`.gzkit/rules/gate5-runbook-code-covenant.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 48 | Docs update when command output changes | **Judgment** | Correlation between code change and doc change is not reliably mechanizable |
| 49 | No placeholder output examples | **Promotable** | Could regex-scan for `<…>` / `TODO` placeholders in runbook/manpages |
| 50 | Heavy/foundation lane requires explicit human attestation before completion | **Mechanical** | Enforced by `gz closeout` pipeline (rule 15 in this scorecard) |

### GitHub CLI Guardrails (`.gzkit/rules/gh-cli.md`)

| # | Rule | Score | Notes |
|---|------|-------|-------|
| 51 | Use `gh` only when explicitly requested | **Judgment** | Agent-behavior rule; no compile-time signal |
| 52 | Prohibited commands (settings mutations, secret management, force push, un-authorized merges) | **Judgment** | Permission model lives in `.claude/settings.json`; gh-level enforcement is server-side |
| 53 | Defect tracking: create GHI when fix deferred | **Judgment** | Cultural enforcement; see rule 17 |

### Constraints (`.gzkit/rules/constraints.md`)

This file is a cross-reference aggregator; every entry maps to one of the rules scored above. Its meta-rule ("these prohibitions are addressed to you — the executing agent") is itself **judgment** — the document's purpose is behavioral guidance for Claude Code sessions, not a mechanical gate.

### Behavioral Invariants (`.gzkit/rules/behavioral-invariants.md`)

Invariants #1–17 in the behavioral invariants doc are primarily **judgment** rules aimed at agent tool use and session behavior:

- "Own the work completely" / "Complete all work fully" / "Never say out of scope" — judgment
- "Fix class of failure, not instance" — judgment (but this audit itself is an instance of applying it)
- "Read AGENTS.md before starting work" — judgment
- "If <90% sure, ask the human" — judgment
- "On inconsistencies, STOP, name confusion, present tradeoff, wait" — judgment

**Invariant #10a** ("When a skill step names a tool, invoke it in the same turn") is **promotable** — could be detected via hook analysis, but the signal-to-noise ratio is probably poor.

---

## Summary

Counts updated 2026-04-18 after the GHI #202–#215 promotion wave landed.

| Score | Count | % |
|-------|-------|---|
| **Mechanical** | 33 | 59% |
| **Promotable** | 5 | 9% |
| **Judgment** | 18 | 32% |
| **Ambiguous** | 0 | 0% |

**The mechanical floor rose from 30 % to 59 %** under the #202–#215 promotion wave. Ten advisory rules were mechanized as `gz validate --<scope>` flags; two became pre-commit guards under `gzkit.hooks.guards`. The remaining Promotable band (Invariants 2/3 of the tool-skill-runbook rule, lazy imports, runbook placeholders, etc.) is tracked for follow-up waves.

---

## Recommended promotion order (highest leverage first)

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
- `.gzkit/rules/constraints.md` — the cross-reference index of these rules
- `CLAUDE.md` — architectural-boundaries memo (rules 1–6 in scorecard)
